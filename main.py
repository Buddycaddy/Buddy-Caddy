
from ir_sensor import setup_ir_sensor
from vibration_sensor import setup_vibration_sensor, detect_vibration
from speed_calculator import calculate_speed
from impact_analyzer import analyze_impact, find_closest_frame
import sys
from queue import Queue
from ball_detector import detect_ball
from UI_display import BallDetectionUI
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QEvent
from multiprocessing import Process, Queue, Value
from collections import deque
import time
import logging
logging.basicConfig(level=logging.DEBUG, filename="debug.log", filemode="w")

class QCustomEvent(QEvent):
    def __init__(self, callback):
        super().__init__(QEvent.User)
        self.callback = callback

def ball_detection_process(queue, is_ready):
    time.sleep(5)  # Wait for other processes to initialize
    import cv2
    image_path = "resource/lower_test1.jpg"  # 테스트할 이미지 경로
    frame = cv2.imread(image_path)
    frame = cv2.resize(frame, (960, 1280))  # Mocking a frame for testing
    # cap = cv2.VideoCapture(0)
    # if not cap.isOpened():
    #     logging.error("Failed to open camera 0")
    #     exit()
    # width, height = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width, height = frame.shape[1], frame.shape[0]
    shot_position = (width//2, height//2)
    while True:
        # ret, frame = cap.read()
        ret = True  # Mocking the frame read for testing
        if ret:
            result = detect_ball(frame, shot_position)
            queue.put(result)
            logging.debug(f"Ball detection result: {result}")
        else:
            logging.error("Failed to read frame from camera 0")
        time.sleep(0.033)
    

def ir_sensor_process(queue, is_ready):
    time.sleep(6)  # 공 탐지 후 1초 뒤 IR 센서 신호
    setup_ir_sensor(queue, is_ready)
    while True:
        time.sleep(0.1)

def vibration_sensor_process(queue, is_ready):
    time.sleep(8)  # test speed_calculator
    chan = setup_vibration_sensor()
    chan.set_voltage(1.5)  # 초기 전압 설정
    if chan is None:
        logging.error("Vibration sensor setup failed")
        exit()
        #for debugging 
    detect_vibration(queue,chan, is_ready=is_ready)
    while True:
        #실제 라즈베리 파이 작동 코드
        # detect_vibration(queue,chan, is_ready=is_ready)
        # logging.debug(f"Vibration detection")
        time.sleep(0.004)

def impact_analysis_process(queue, is_ready):
    import cv2
    logging.info("Starting impact_analysis_process")
    frames = deque(maxlen=30)  # 최대 30개의 프레임 저장

    # cap = cv2.VideoCapture(1)
    cap = cv2.VideoCapture("./resource/test2.mp4")  # Mocking a video file for testing
    if not cap.isOpened():
        logging.error("Failed to open camera 1")
        queue.put({"source": "impact_analyzer", "impact_position": None})
        return

    while True:
        with is_ready.get_lock():
            if is_ready.value:
                ret, frame = cap.read()
                if ret:
                    # 현재 시간과 프레임을 저장
                    timestamp = time.time()
                    frames.append((timestamp, frame))
                else:
                    logging.error("Failed to append to frames, no more frames to read")

        if not queue.empty():
            data = queue.get()
            if data.get("source") == "vibration_sensor" and data.get("event") == "vibration_trigger":
                vib_timestamp = data["timestamp"]
                logging.info(f"Vibration sensor triggered at {vib_timestamp}")

                # 진동 센서 타임스탬프와 가장 가까운 프레임 검색
                closest_frame = find_closest_frame(frames, vib_timestamp)
                if closest_frame is not None:
                    logging.info("Closest frame found")
                    result = analyze_impact([closest_frame])  # 분석 함수 호출
                    queue.put(result)
                    logging.debug(f"Impact analysis result: {result}")
                else:
                    logging.warning("No matching frame found for vibration timestamp")

        time.sleep(0.033)


class MainApp:
    def __init__(self):
        self.queue = Queue()
        self.ir_timestamp = None
        self.vib_timestamp = None
        self.impact_position = None
        self.speed = None

        self.app = QApplication(sys.argv)
        screens = self.app.screens()
        target_screen = screens[1] if len(screens) > 1 else screens[0]
        self.geometry = target_screen.geometry()
        self.width, self.height = self.geometry.width(), self.geometry.height()
        self.ui = BallDetectionUI(self.width, self.height)
        self.ui.move(self.geometry.x(), self.geometry.y())
        self.ui.showFullScreen()

        self.is_ready = Value('b', False)
        self.start_processes()

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_queue)
        self.timer.start(50)
        logging.info("MainApp initialized, processes started")

    def start_processes(self):
        logging.info("Starting ball_detection_process")
        self.p1 = Process(target=ball_detection_process, args=(self.queue, self.is_ready))
        self.p1.start()
        time.sleep(1)  # 프로세스 시작 후 1초 대기

        logging.info("Starting ir_sensor_process")
        self.p2 = Process(target=ir_sensor_process, args=(self.queue, self.is_ready))
        self.p2.start()
        time.sleep(1)  # 프로세스 시작 후 1초 대기

        logging.info("Starting vibration_sensor_process")
        self.p3 = Process(target=vibration_sensor_process, args=(self.queue, self.is_ready))
        self.p3.start()
    

    def check_queue(self):
        while not self.queue.empty():
            try:
                data = self.queue.get()
                logging.debug(f"Queue data: {data}")
                if data.get("source") == "ball_detector":
                    # if data.get("detected"):
                    #    print("공을 치세요")
                    if data.get("enable_ir"):
                        with self.is_ready.get_lock():
                            self.is_ready.value = True
                        QApplication.postEvent(self.ui, QCustomEvent(self.ui.handle_ir_detected))
                elif data.get("source") == "ir_sensor" and data.get("event") == "ir_trigger":
                    self.ir_timestamp = data["timestamp"]
                    Process(target=impact_analysis_process, args=(self.queue, self.is_ready)).start()
                elif data.get("source") == "vibration_sensor" and data.get("event") == "vibration_trigger":
                    self.vib_timestamp = data["timestamp"]
                elif data.get("source") == "speed_calculator" and "speed" in data:
                    self.speed = data["speed"]
                elif data.get("source") == "impact_analyzer" and "impact_position" in data:
                    self.impact_position = data["impact_position"]
                    QApplication.postEvent(self.ui, QCustomEvent(lambda: self.ui.handle_camera_detected(self.speed, self.impact_position)))
                if self.ir_timestamp and self.vib_timestamp:
                    speed_result = calculate_speed(self.ir_timestamp, self.vib_timestamp)
                    print(f"Calculated speed: {speed_result}")
                    self.queue.put(speed_result)
                    self.ir_timestamp = None
                    self.vib_timestamp = None
            except Exception as e:
                logging.error(f"Queue error: {e}")

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    MainApp().run()
