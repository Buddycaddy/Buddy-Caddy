
from ir_sensor import setup_ir_sensor
from vibration_sensor import setup_vibration_sensor, detect_vibration
from speed_calculator import calculate_speed
from impact_analyzer import analyze_impact
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
    logging.info("Starting ball_detection_process")
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
    logging.info("Starting ir_sensor_process")
    setup_ir_sensor(queue, is_ready)
    while True:
        time.sleep(0.1)

def vibration_sensor_process(queue, is_ready):
    logging.info("Starting vibration_sensor_process")
    chan = setup_vibration_sensor()
    if chan is None:
        logging.error("Vibration sensor setup failed")
        exit()
    while True:
        result = detect_vibration(chan, is_ready=is_ready)
        if result:
            queue.put(result)
            logging.debug(f"Vibration detection result: {result}")
        time.sleep(0.004)

def impact_analysis_process(queue, is_ready):
    import cv2
    logging.info("Starting impact_analysis_process")
    frames = deque(maxlen=30)
    while True:
        with is_ready.get_lock():
            if is_ready.value:
                cap = cv2.VideoCapture(1)
                if not cap.isOpened():
                    logging.error("Failed to open camera 1")
                    queue.put({"source": "impact_analyzer", "impact_position": None})
                    break
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)
                else:
                    logging.error("Failed to read frame from camera 1")
        if not queue.empty():
            data = queue.get()
            if data.get("source") == "vibration_sensor" and data.get("event") == "vibration_trigger":
                result = analyze_impact(frames)
                queue.put(result)
                logging.debug(f"Impact analysis result: {result}")
                if cap.isOpened():
                    cap.release()
                break
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
        self.p1 = Process(target=ball_detection_process, args=(self.queue, self.is_ready))
        self.p2 = Process(target=ir_sensor_process, args=(self.queue, self.is_ready))
        self.p3 = Process(target=vibration_sensor_process, args=(self.queue, self.is_ready))
        self.p1.start()
        self.p2.start()
        self.p3.start()

    def check_queue(self):
        while not self.queue.empty():
            try:
                data = self.queue.get()
                logging.debug(f"Queue data: {data}")
                if data.get("source") == "ball_detector":
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
                    self.queue.put(speed_result)
                    self.ir_timestamp = None
                    self.vib_timestamp = None
            except Exception as e:
                logging.error(f"Queue error: {e}")

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    MainApp().run()
