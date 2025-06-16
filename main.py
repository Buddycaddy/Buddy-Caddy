# from multiprocessing import Process, Queue, Value
# from ball_detector import detect_ball
# from ir_sensor import setup_ir_sensor
# from vibration_sensor import setup_vibration_sensor, detect_vibration
# from speed_calculator import calculate_speed
# from impact_analyzer import analyze_impact
# from UI_display import BallDetectionUI
# from PyQt5.QtWidgets import QApplication
# from PyQt5.QtCore import QTimer, QEvent
# import sys
# import cv2
# from collections import deque
# import time
# import logging

# cv2.setNumThreads(2)
# logging.basicConfig(level=logging.DEBUG, filename="debug.log", filemode="w")

# class QCustomEvent(QEvent):
#     def __init__(self, callback):
#         super().__init__(QEvent.User)
#         self.callback = callback

# def ball_detection_process(queue, is_ready):
#     logging.info("Starting ball_detection_process")
#     image_path = "resource/lower_test1.jpg"  # 테스트할 이미지 경로
#     frame = cv2.imread(image_path)
#     # cap = cv2.VideoCapture(0)
#     # if not cap.isOpened():
#     #     logging.error("Failed to open camera 0")
#     #     exit()
#     # width, height = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
#     width, height = frame.shape[1], frame.shape[0]
#     shot_position = (width//2, height//2)
#     while True:
#         # ret, frame = cap.read()
#         ret = True  # Mocking the frame read for testing
#         if ret:
#             result = detect_ball(frame, shot_position)
#             queue.put(result)
#             logging.debug(f"Ball detection result: {result}")
#         else:
#             logging.error("Failed to read frame from camera 0")
#         time.sleep(0.033)

# def ir_sensor_process(queue, is_ready):
#     logging.info("Starting ir_sensor_process")
#     setup_ir_sensor(queue, is_ready)
#     while True:
#         time.sleep(0.1)

# def vibration_sensor_process(queue, is_ready):
#     logging.info("Starting vibration_sensor_process")
#     chan = setup_vibration_sensor()
#     if chan is None:
#         logging.error("Vibration sensor setup failed")
#         exit()
#     while True:
#         result = detect_vibration(chan, is_ready=is_ready)
#         if result:
#             queue.put(result)
#             logging.debug(f"Vibration detection result: {result}")
#         time.sleep(0.004)

# def impact_analysis_process(queue, is_ready):
#     logging.info("Starting impact_analysis_process")
#     frames = deque(maxlen=30)
#     while True:
#         with is_ready.get_lock():
#             if is_ready.value:
#                 cap = cv2.VideoCapture(1)
#                 if not cap.isOpened():
#                     logging.error("Failed to open camera 1")
#                     queue.put({"source": "impact_analyzer", "impact_position": None})
#                     break
#                 ret, frame = cap.read()
#                 if ret:
#                     frames.append(frame)
#                 else:
#                     logging.error("Failed to read frame from camera 1")
#         if not queue.empty():
#             data = queue.get()
#             if data.get("source") == "vibration_sensor" and data.get("event") == "vibration_trigger":
#                 result = analyze_impact(frames)
#                 queue.put(result)
#                 logging.debug(f"Impact analysis result: {result}")
#                 if cap.isOpened():
#                     cap.release()
#                 break
#         time.sleep(0.033)

# class MainApp:
#     def __init__(self):
#         self.queue = Queue()
#         self.ir_timestamp = None
#         self.vib_timestamp = None
#         self.impact_position = None
#         self.speed = None

#         self.app = QApplication(sys.argv)
#         screens = self.app.screens()
#         target_screen = screens[1] if len(screens) > 1 else screens[0]
#         self.geometry = target_screen.geometry()
#         self.width, self.height = self.geometry.width(), self.geometry.height()
#         self.ui = BallDetectionUI(self.width(), self.height())
#         self.ui.move(self.geometry.x(), self.geometry.y())
#         self.ui.showFullScreen()

#         self.is_ready = Value('b', False)
#         # self.start_processes()

#         self.timer = QTimer()
#         self.timer.timeout.connect(self.check_queue)
#         self.timer.start(50)
#         logging.info("MainApp initialized, processes started")

#     # def start_processes(self):
#         # self.p1 = Process(target=ball_detection_process, args=(self.queue, self.is_ready))
#         # self.p2 = Process(target=ir_sensor_process, args=(self.queue, self.is_ready))
#         # self.p3 = Process(target=vibration_sensor_process, args=(self.queue, self.is_ready))
#         # self.p1.start()
#         # self.p2.start()
#         # self.p3.start()

#     # def check_queue(self):
#     #     while not self.queue.empty():
#     #         try:
#     #             data = self.queue.get()
#     #             logging.debug(f"Queue data: {data}")
#     #             if data.get("source") == "ball_detector":
#     #                 if data.get("enable_ir"):
#     #                     with self.is_ready.get_lock():
#     #                         self.is_ready.value = True
#     #                     QApplication.postEvent(self.ui, QCustomEvent(self.ui.handle_ir_detected))
#     #             elif data.get("source") == "ir_sensor" and data.get("event") == "ir_trigger":
#     #                 self.ir_timestamp = data["timestamp"]
#     #                 Process(target=impact_analysis_process, args=(self.queue, self.is_ready)).start()
#     #             elif data.get("source") == "vibration_sensor" and data.get("event") == "vibration_trigger":
#     #                 self.vib_timestamp = data["timestamp"]
#     #             elif data.get("source") == "speed_calculator" and "speed" in data:
#     #                 self.speed = data["speed"]
#     #             elif data.get("source") == "impact_analyzer" and "impact_position" in data:
#     #                 self.impact_position = data["impact_position"]
#     #                 QApplication.postEvent(self.ui, QCustomEvent(lambda: self.ui.handle_camera_detected(self.speed, self.impact_position)))
#     #             if self.ir_timestamp and self.vib_timestamp:
#     #                 speed_result = calculate_speed(self.ir_timestamp, self.vib_timestamp)
#     #                 self.queue.put(speed_result)
#     #                 self.ir_timestamp = None
#     #                 self.vib_timestamp = None
#     #         except Exception as e:
#     #             logging.error(f"Queue error: {e}")

#     def run(self):
#         sys.exit(self.app.exec_())

# if __name__ == "__main__":
#     MainApp().run()

import sys
from queue import Queue
from ball_detector import detect_ball
from UI_display import BallDetectionUI
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, pyqtSignal, QObject
import cv2
import threading
import time
import logging

cv2.setNumThreads(0)  # OpenCV 스레드 비활성화
logging.basicConfig(level=logging.DEBUG, filename="debug.log", filemode="w", format="%(asctime)s - %(levelname)s - %(message)s")

class MainApp(QObject):
    ir_detected_signal = pyqtSignal()  # GUI 업데이트용 시그널

    def __init__(self):
        super().__init__()
        logging.info("Initializing MainApp")
        try:
            self.queue = Queue()
            logging.info("Queue initialized")
        except Exception as e:
            logging.error(f"Queue initialization error: {e}")
            raise

        try:
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
                logging.info("QApplication initialized")
        except Exception as e:
            logging.error(f"QApplication initialization error: {e}")
            raise

        # 디스플레이 설정: 다중 모니터 대신 기본 화면 사용
        try:
            screen = self.app.primaryScreen()
            geometry = screen.geometry()
            width, height = geometry.width(), geometry.height()
            logging.info(f"Screen geometry: {width}x{height}")
        except Exception as e:
            logging.error(f"Screen initialization error: {e}")
            raise

        # UI 초기화
        try:
            self.ui = BallDetectionUI(width, height)
            self.ui.move(geometry.x(), geometry.y())
            self.ui.showFullScreen()
            logging.info("BallDetectionUI initialized")
        except Exception as e:
            logging.error(f"UI initialization error: {e}")
            raise

        # 시그널 연결
        self.ir_detected_signal.connect(self.ui.handle_ir_detected)

        # 스레드 시작
        self.start_threads()

        # 타이머 설정
        try:
            self.timer = QTimer()
            self.timer.timeout.connect(self.check_queue)
            self.timer.start(50)
            logging.info("QTimer started")
        except Exception as e:
            logging.error(f"QTimer initialization error: {e}")
            raise

    def start_threads(self):
        try:
            self.t1 = threading.Thread(target=self.ball_detection_process, args=(self.queue,))
            self.t1.daemon = True
            self.t1.start()
            logging.info("Ball detection thread started")
        except Exception as e:
            logging.error(f"Thread initialization error: {e}")
            raise

    def ball_detection_process(self, queue):
        logging.info("Starting ball_detection_process")
        try:
            image_path = "resource/lower_test1.jpg"
            frame = cv2.imread(image_path)
            if frame is None:
                logging.error("Failed to load image")
                return
            width, height = frame.shape[1], frame.shape[0]
            shot_position = (width//2, height//2)
            logging.info(f"Image loaded: {width}x{height}")
        except Exception as e:
            logging.error(f"Image load error: {e}")
            return

        while True:
            try:
                result = detect_ball(frame, shot_position)
                queue.put(result)
                logging.debug(f"Ball detection result: {result}")
            except Exception as e:
                logging.error(f"Ball detection error: {e}")
            time.sleep(0.033)

    def check_queue(self):
        while not self.queue.empty():

#             if isinstance(data, dict) and "detected" in data:
#                 print("호출 전")
#                 self.ui.show_ball_detected(data["detected"], "Result/res_img.png" if data["detected"] else None)
#                 print("호출 후")
            try:
                data = self.queue.get()
                logging.debug(f"Queue data: {data}")
                if data.get("source") == "ball_detector" and data.get("enable_ir"):
                    self.ir_detected_signal.emit()
            except Exception as e:
                logging.error(f"Queue error: {e}")

    def run(self):
        logging.info("Starting QApplication event loop")
        sys.exit(self.app.exec_())

if __name__ == "__main__":
<<<<<<< jincheol
    try:
        app = MainApp()
        app.run()
    except Exception as e:
        logging.error(f"MainApp error: {e}")
=======
    MainApp().run()

>>>>>>> main
