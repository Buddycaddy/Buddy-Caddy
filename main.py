from ir_sensor import setup_ir_sensors
from vibration_sensor import setup_vibration_sensor, detect_vibration
from speed_calculator import calculate_speed
from impact_analyzer import analyze_impact, find_closest_frame
from send_event import QCustomEvent
import sys
from queue import Queue
from ball_detector import detect_ball
from UI_display import BallDetectionUI
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QEvent, QObject, Qt
from multiprocessing import Process, Queue, Value, Manager, Event
from collections import deque
import time
import logging
from PyQt5.QtGui import QKeyEvent
from picamera2 import Picamera2
import RPi.GPIO as GPIO
import threading

logging.basicConfig(level=logging.DEBUG, filename="debug.log", filemode="w")

# 전역 변수 선언
Manager = Manager()
ball_queue = Manager.Queue()
ir_queue = Manager.Queue()
vib_queue = Manager.Queue()
impact_queue = Manager.Queue()
is_ready = Value('b', False)


def ball_detection_process(pause_event):
    time.sleep(2)  
    # image_path = "resource/lower_test1.jpg"  # 테스트할 이미지 경로
    # frame = cv2.imread(image_path)
    # frame = cv2.resize(frame, (960, 1280))  # Mocking a frame for testing
    low_camera = Picamera2(1)  # Second camera
    low_camera.start()
    
    prev_position = None  # Initialize previous position
    while True:
        frame = low_camera.capture_array()  # Capture a frame from the camera

        if frame is None:
            logging.error("Failed to open low camera")
            exit()
        frame = frame[0:200, 100:500, :]
        # ret, frame = cap.read()
        pause_event.wait()  # Wait for the pause event to be cleared
        ret = True  # Mocking the frame read for testing
        if ret:
            result = detect_ball(frame, prev_position)
            if result["detected"]:
                prev_position = result.get("prev_position")
                if result["stable"]:
                    result["enable_ir"] = True
                    result["frame"] = frame  # 프레임 데이터를 결과에 추가
                prev_position = result.get("prev_position")
            else:
                result["enable_ir"]= False            
            ball_queue.put(result)  # 결과와 프레임을 큐에 넣음
            logging.debug(f"Ball detection result: {result}")
        else:
            logging.error("Failed to read frame from camera 0")
        time.sleep(0.033)

def ir_sensor_process(ir_queue, is_ready):
    IR_PINS = [18, 23, 24]
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    def ir_disconnected_callback(pin):
        print(f"IR sensor {pin} triggered at {time.time()}")
        with is_ready.get_lock():
            if is_ready.value:
                ir_queue.put({"source": "ir_sensor", "event": "ir_trigger", "pin": pin, "timestamp": time.time()})
                logging.debug(f"IR data sent to queue: pin {pin}")

    for pin in IR_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            pin,
            GPIO.FALLING,
            callback=ir_disconnected_callback,
            bouncetime=200  # 디바운싱 시간 증가
        )
        print(f"IR sensor on pin {pin} initialized")
    try:
        while True:
            time.sleep(0.1)
    finally:
        GPIO.cleanup()

def vibration_sensor_process():
    time.sleep(7.7)  # test speed_calculator
    chan = setup_vibration_sensor()
    chan.set_voltage(1.5)  # 초기 전압 설정
    if chan is None:
        logging.error("Vibration sensor setup failed")
        exit()
        #for debugging
    detect_vibration(vib_queue,impact_queue,is_ready,chan)
    while True:
        #실제 라즈베리 파이 작동 코드
        # detect_vibration(chan)
        # logging.debug(f"Vibration detection")
        time.sleep(0.004)

def impact_analysis_process(shared_data):
    import cv2
    logging.info("Starting impact_analysis_process")
    frames = deque(maxlen=30)  # 최대 30개의 프레임 저장

    video_path = "./resource/segment_2.mp4"  # Video file for testing
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logging.error("Failed to open video file")
        impact_queue.put({"source": "impact_analyzer", "impact_position": None, "frame": None})
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_duration = 4.87   # seconds, as specified
    frame_rate = total_frames / video_duration
    logging.info(f"Video frame rate: {frame_rate} fps, total frames: {total_frames}")

    start_time = time.time()

    while True:
        with is_ready.get_lock():
            if is_ready.value:
                elapsed_time = time.time() - start_time
                target_frame = int(elapsed_time * frame_rate) % total_frames
                logging.debug(f"Elapsed time: {elapsed_time:.2f}s, Target frame: {target_frame}")

                cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
                ret, frame = cap.read()
                if ret:
                    timestamp = time.time()
                    frames.append((timestamp, frame))
                    logging.debug(f"Frame {target_frame} captured at {timestamp}")
                else:
                    logging.error(f"Failed to read frame {target_frame}")
                    break

        if shared_data["vib_timestamp"] is not None:
            logging.debug(f" vib_timestamp {shared_data['vib_timestamp']}")
            closest_frame = find_closest_frame(frames, shared_data["vib_timestamp"])
            if closest_frame is not None:
                logging.info("Closest frame found")
                result = analyze_impact([closest_frame])
                impact_queue.put(result)
                logging.debug(f"Impact analysis result: {result}")
                print("Impact analysis finished ")
                break
            else:
                logging.warning("No matching frame found for vibration timestamp")

        time.sleep(0.033)

    cap.release()
    logging.info("Impact analysis process completed")

class MainApp(QObject):
    def __init__(self):
        super().__init__()
        self.shared_data = Manager.dict()  # 공유 데이터 생성
        self.shared_data["vib_timestamp"] = None  # 초기값 설정
        self.shared_data["ir_18_timestamp"] = None
        self.shared_data["ir_23_timestamp"] = None
        self.shared_data["ir_24_timestamp"] = None
        self.shared_data["impact_position"] = None
        self.shared_data["speed"] = None

        self.pause_event = Event()           # ← 이 줄을 BallDetectionUI 생성보다 먼저!
        self.pause_event.set()  # 초기 상태는 실행 상태

        self.app = QApplication(sys.argv)
        screens = self.app.screens()
        target_screen = screens[1] if len(screens) > 1 else screens[0]
        self.geometry = target_screen.geometry()

        # 화면의 절반 크기 계산
        self.width = self.geometry.width() // 2
        self.height = self.geometry.height() // 2

        # 중앙 위치 계산
        center_x = self.geometry.x() + (self.geometry.width() - self.width) // 2
        center_y = self.geometry.y() + (self.geometry.height() - self.height) // 2

        self.ui = BallDetectionUI(self.width, self.height, self)
        self.ui.move(center_x, center_y)
        self.ui.show()

        self.start_processes()

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_queues)
        self.timer.start(50)
        logging.info("MainApp initialized, processes started")

        self.app.installEventFilter(self)  # 이벤트 필터 등록

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Q:
            self.close_all()
            return True
        return False

    def start_processes(self):
        logging.info("Starting ball_detection_process")
        self.p1 = Process(target=ball_detection_process, args=(self.pause_event,))
        self.p1.start()
        time.sleep(1)  # 프로세스 시작 후 1초 대기

        
        self.p2 = threading.Thread(target=ir_sensor_process, args=(ir_queue, is_ready))
        self.p2.daemon = True  # 메인 스레드 종료 시 함께 종료
        # self.p2.start()
        time.sleep(1)  # 프로세스 시작 후 1초 대기

        logging.info("Starting vibration_sensor_process")
        self.p3 = Process(target=vibration_sensor_process)
        # self.p3.start()

        logging.info("Start impact analysis process")
        self.p4 = Process(target=impact_analysis_process, args=(self.shared_data,))

    def pause_process(self):
        logging.info("Pausing ball_detection_process")
        self.pause_event.clear()  # 프로세스를 일시 중지
        
    def resume_process(self):
        logging.info("Resuming ball_detection_process")
        self.pause_event.set()  # 프로세스를 다시 시작

    def reset_queues(self):
        # Clear existing queues and create new ones
        while not ball_queue.empty():
            ball_queue.get()
        while not ir_queue.empty():
            ir_queue.get()
        while not vib_queue.empty():
            vib_queue.get()
        while not impact_queue.empty():
            impact_queue.get()

        ball_queue = Queue(maxsize=1000000)
        ir_queue = Queue(maxsize=1000000)
        vib_queue = Queue(maxsize=1000000)
        impact_queue = Queue(maxsize=1000000)
        logging.info("All queues reset")

    def check_queues(self):
        # Check ball detection queue
        while not ball_queue.empty():
            try:
                data = ball_queue.get()
                logging.debug(f"Ball queue data: {data}")
                if data.get("source") == "ball_detector" and data.get("enable_ir"):
                    with is_ready.get_lock():
                        if not is_ready.value:
                            is_ready.value = True
                            logging.info("Starting ir_sensor_process")
                            self.p2.start()  # Start IR sensor 
                        # print("공 탐지")
                    low_cam_frame = data.get("frame")
                    # print(f"Low camera frame shape: {low_cam_frame.shape if low_cam_frame is not None else 'None'}")
                    QApplication.postEvent(self.ui, QCustomEvent(self.ui.handle_ir_detected,low_cam_frame))
                elif data.get("source") == "ball_detector" and data.get("stable"):
                    self.p1.pause()  # Pause ball detection process
            except Exception as e:
                logging.error(f"Ball queue error: {e}")

        # Check IR sensor queue
        while not ir_queue.empty():
            try:
                data = ir_queue.get()
                logging.debug(f"IR queue data: {data}")
                if data.get("source") == "ir_sensor" and data.get("event") == "ir_trigger":
                    pin_num = data.get("pin")
                    if pin_num == 18 and self.shared_data["ir_23_timestamp"] is not None:
                        self.shared_data["ir_18_timestamp"] = data["timestamp"]
                        calculate_speed(
                            self.shared_data["ir_23_timestamp"],
                            self.shared_data["ir_18_timestamp"]
                        )
                    elif pin_num == 23 :
                        self.shared_data["ir_23_timestamp"] = data["timestamp"]
                        # 첫번쨰
                    elif pin_num == 24 and self.shared_data["ir_23_timestamp"] is not None:
                        self.shared_data["ir_24_timestamp"] = data["timestamp"]
                        calculate_speed(
                            self.shared_data["ir_23_timestamp"],
                            self.shared_data["ir_24_timestamp"]
                        )
                    # Start impact analysis process
                    self.p4.start()
            except Exception as e:
                logging.error(f"IR queue error: {e}")

        # Check vibration sensor queue
        while not vib_queue.empty():
            try:
                data = vib_queue.get()
                logging.debug(f"Vibration queue data: {data}")
                if data.get("source") == "vibration_sensor" and data.get("action") == "speed":
                    self.shared_data["vib_timestamp"] = data["timestamp"]
                    if self.shared_data["ir_timestamp"]:
                        speed_result = calculate_speed(self.shared_data["ir_timestamp"], self.shared_data["vib_timestamp"])
                        print(f"Calculated speed: {speed_result}")
                        vib_queue.put(speed_result)  # Put back to vib_queue for consistency
                        self.shared_data["ir_timestamp"] = None
                        self.shared_data["vib_timestamp"] = None
                elif data.get("source") == "speed_calculator" and "speed" in data:
                    self.shared_data["speed"] = data["speed"]
                elif data.get("source") == "vibration_sensor" and data.get("action") == "impact":
                    impact_queue.put(data)  # Forward vibration data to impact queue
            except Exception as e:
                logging.error(f"Vibration queue error: {e}")

        # Check impact analysis queue
        while not impact_queue.empty():
            try:
                data = impact_queue.get()
                logging.debug(f"Impact queue data: {data}")
                if data.get("source") == "impact_analyzer" and "impact_position" in data:
                    self.shared_data["impact_position"] = data["impact_position"]
                    QApplication.postEvent(self.ui, QCustomEvent(lambda: self.ui.handle_camera_detected(
                        self.shared_data["speed"],
                        self.shared_data["impact_position"],
                        data.get("frame")
                    )))
                elif data.get("source") == "impact_analyzer" and data.get("action") == "reset_queues":
                    self.reset_queues()
                elif data.get("source") == "vibration_sensor" and data.get("action") == "impact":
                    self.shared_data["vib_timestamp"] = data["timestamp"]
                    logging.info(f"Vibration sensor triggered at {self.shared_data['vib_timestamp']}")
            except Exception as e:
                logging.error(f"Impact queue error: {e}")

    def close_all(self):
        # 프로세스 종료
        for attr in ['p1', 'p3', 'p4']:  # p2(Thread)는 제외
            proc = getattr(self, attr, None)
            if proc and hasattr(proc, 'is_alive') and proc.is_alive():
                proc.terminate()
                proc.join()
        # 스레드는 종료 신호만 보내고 강제 종료하지 않음
        # 카메라 리소스 해제
        try:
            if hasattr(self, 'ui') and hasattr(self.ui, 'cam') and self.ui.cam:
                self.ui.cam.stop()
        except Exception as e:
            logging.error(f"Error stopping camera: {e}")
        # 윈도우 종료
        self.app.quit()

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    MainApp().run()
