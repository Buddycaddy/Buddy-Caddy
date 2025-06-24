
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



#5 맨앞
#6,13 중간 상단,하단  
#18,23,24 맨뒤  위/ 중간 /아래

logging.basicConfig(level=logging.DEBUG, filename="debug.log", filemode="w")
# 전역 변수 선언
Manager = Manager()
ball_queue = Manager.Queue()
ir_queue = Manager.Queue()
vib_queue = Manager.Queue()
impact_queue = Manager.Queue()

is_ready = Value('b', False)

#카메라 설정
low_camera = Picamera2(1)  # Second camera
front_camera = Picamera2(0)  # First camera


# Select desired sensor mode (1332x990 at 120 fps) for first camera
sensor_modes = front_camera.sensor_modes
desired_mode = None
for mode in sensor_modes:
    if mode['size'] == (1332, 990) and mode['fps'] >= 120:
        desired_mode = mode
        break
# Create video configuration for first camera with specific sensor mode
config1 = front_camera.create_video_configuration(
    main={"format": "RGB888", "size": (640, 480)},  # Keep full sensor resolution
    controls={"FrameRate": 120},
    sensor={
        "output_size": desired_mode['size'],
        "bit_depth": desired_mode['bit_depth']
    }
)
#5 맨앞
#6,13 중간 상단,하단  
#18,23,24 맨뒤  위/ 중간 /아래
IR_PINS = [5, 6, 13,18,23,24]

# 변수 설정
#####################################################################################################################


def ball_detection_process():
    time.sleep(2)  
    # image_path = "resource/lower_test1.jpg"  # 테스트할 이미지 경로
    # frame = cv2.imread(image_path)
    # frame = cv2.resize(frame, (960, 1280))  # Mocking a frame for testing
    # low_camera = Picamera2(1)  # Second camera
    low_camera.start()
    
    prev_position = None  # Initialize previous position
    count = 0  # Initialize count for debugging
    while True:
        frame = low_camera.capture_array()  # Capture a frame from the camera

        if frame is None:
            logging.error("Failed to open low camera")
            exit()
        frame = frame[0:200, 50:400, :]
        # ret, frame = cap.read()
        ret = True  # Mocking the frame read for testing
        if ret:
            result = detect_ball(frame, prev_position)
            if result["detected"]:
                prev_position = result.get("prev_position")
                result["enable_ir"] = True
                result["frame"] = frame  # 프레임 데이터를 결과에 추가
                if result["stable"]:
                    count += 1
            else:
                result["enable_ir"]= False            
            ball_queue.put(result)  # 결과와 프레임을 큐에 넣음
            logging.debug(f"Ball detection result: {result}")
        else:
            logging.error("Failed to read frame from camera 0")

        if count >= 5:  #
            logging.info("Ball detection is stable, breaking the loop")
            result["enable_front_camera"] = True  # Enable front camera
            ball_queue.put(result)  # Put the final result in the queue
            break
        time.sleep(0.33)
    low_camera.stop()  # 카메라 정지

def ir_sensor_process(ir_queue, is_ready):

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
    print(f"ir(23) 센서 입력 시간 : {shared_data['ir_23_timestamp']}")
    start_time = time.time()
    print(f"프레임 append 시작 시간 : {start_time}")
    logging.info("Starting impact_analysis_process")
    frames1 = deque(maxlen=120)  # 최대 60개의 프레임 저장
    # front_camera.start()
    
    while True:
        frame1 = front_camera.capture_array()  # Capture a frame from the camera
    
        if frame1 is None:
            logging.error("Failed to open front camera")
            exit()

        # frame1 = frame1[0:480, 0:640]  # Crop the frame
        frames1.append((frame1,time.time()))  # Add frame to the deque
        logging.debug(f"Frame added to deque, current size: {len(frames1)}")

        # Check if the deque is full
        if len(frames1) == frames1.maxlen:
            logging.info("Deque is full, analyzing frames")
            print(f"프레임 append 끝 시간 : {time.time()}")
            print(f"fps : {len(frames1) / (time.time() - start_time):.2f}")
            analyze_impact(list(frames1))  # Pass frames to analyze_frame
            #queue에다 넣고 exit
            
            frames1.clear()  # Clear the deque after analysis
            logging.info("Deque cleared after analysis")
            exit()  # Exit after processing the frames
        elif len(frames1) == 0:
            logging.warning("프레임 큐(frames1)에 프레임이 하나도 들어오지 않았습니다!")
        else:
            logging.debug(f"현재 프레임 큐(frames1) 크기: {len(frames1)}")

class MainApp(QObject):
    def __init__(self):
        super().__init__()
        self.shared_data = Manager.dict()  # 공유 데이터 생성
        self.shared_data["vib_timestamp"] = None  # 초기값 설정
        # ir 센서 타임스탬프 초기화
        self.shared_data["ir_1st_timestamp"] = None
        self.shared_data["ir_2nd_timestamp"] = None

        self.shared_data["impact_position"] = None
        self.shared_data["speed"] = None

        self.pause_event = Event()         
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
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Q:  # Q 키를 누르면 종료
                self.close_all()
                return True
            elif event.key() == Qt.Key_Space:  # 스페이스 바를 누르면 self.p4 실행
                if not self.p4.is_alive():  # self.p4가 실행 중이 아니면 실행
                    logging.info("Space bar pressed, starting impact_analysis_process")
                    self.shared_data["ir_23_timestamp"] = time.time()  # 현재 시간을 ir_23_timestamp에 저장
                    self.p4.start()
                else:
                    logging.info("Space bar pressed, but impact_analysis_process is already running")
                return True
        return False

    def start_processes(self):
        logging.info("Starting ball_detection_process")
        front_camera.configure(config1) 
        front_camera.start()

        self.p1 = threading.Thread(target=ball_detection_process, args=())
        self.p1.start()
        time.sleep(1)  # 프로세스 시작 후 1초 대기

        
        self.p2 = threading.Thread(target=ir_sensor_process, args=(ir_queue, is_ready))
        self.p2.daemon = True  # 메인 스레드 종료 시 함께 종료
        # self.p2.start()
        time.sleep(1)  # 프로세스 시작 후 1초 대기

        # logging.info("Starting vibration_sensor_process")                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
        # self.p3 = Process(target=vibration_sensor_process)
        # # self.p3.start()

        logging.info("Start impact analysis process")
        self.p4 = threading.Thread(target=impact_analysis_process, args=(self.shared_data,))

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
                elif data.get("source") == "ball_detector" and data.get("enable_front_camera"):
                    front_camera.start(config1)  # Start front camera with the specified configuration
        
            except Exception as e:
                logging.error(f"Ball queue error: {e}")

        # Check IR sensor queue
        while not ir_queue.empty():
            #5 공 뒤
            #6,13 중간 상단,하단  
            #18,23,24 맨뒤  위/ 중간 /아래
            try:
                data = ir_queue.get()
                logging.debug(f"IR queue data: {data}")
                if data.get("source") == "ir_sensor" and data.get("event") == "ir_trigger":
                    pin_num = data.get("pin")

                    #############################################################
                    if  pin_num == 5: 
                        # Start impact analysis process
                        self.p4.start()
                    #####################################################
                    elif pin_num == 6 or pin_num == 13:
                        if self.shared_data["ir_1st_timestamp"] is None:
                            self.shared_data["ir_1st_timestamp"] = data["timestamp"]
                            logging.info(f"IR sensor 6 or 13 triggered at {self.shared_data['ir_1st_timestamp']}")
                        else:
                            logging.warning("IR sensor 6 or 13 triggered but already has ir_1st_timestamp set")
                    ##############################################################
                    elif pin_num == 18 or pin_num == 23 or pin_num == 24:
                        if self.shared_data["ir_2nd_timestamp"] is not None:
                            self.shared_data["ir_2nd_timestamp"] = data["timestamp"]
                            logging.info(f"IR sensor 18 or 23 or 24 triggered at {self.shared_data['ir_2nd_timestamp']}")
                        else:
                            logging.warning("IR sensor 18 or 23 or 24 triggered but already has ir_2nd_timestamp set")


                if self.shared_data['ir_1st_timestamp'] is not None and self.shared_data['ir_2nd_timestamp'] is not None:
                    speed_result = calculate_speed(self.shared_data['ir_1st_timestamp'],self.shared_data['ir_2nd_timestamp'])
                    self.shared_data["speed"] = speed_result["speed"]


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
