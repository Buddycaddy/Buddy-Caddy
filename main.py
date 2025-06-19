# from ir_sensor import setup_ir_sensor
# from vibration_sensor import setup_vibration_sensor, detect_vibration
# from speed_calculator import calculate_speed
# from impact_analyzer import analyze_impact, find_closest_frame
# import sys
# from queue import Queue
# from ball_detector import detect_ball
# from UI_display import BallDetectionUI
# from PyQt5.QtWidgets import QApplication
# from PyQt5.QtCore import QTimer, QEvent
# from multiprocessing import Process, Queue, Value, Manager
# from collections import deque
# import time
# import logging


# logging.basicConfig(level=logging.DEBUG, filename="debug.log", filemode="w")

# # 전역 변수 선언
# Manager = Manager()
# ball_queue = Manager.Queue()
# ir_queue = Manager.Queue()
# vib_queue = Manager.Queue()
# impact_queue = Manager.Queue()
# is_ready = Value('b', False)

# class QCustomEvent(QEvent):
#     def __init__(self, callback):
#         super().__init__(QEvent.User)
#         self.callback = callback

# def ball_detection_process():
#     time.sleep(5)  # Wait for other processes to initialize
#     import cv2
#     image_path = "resource/lower_test1.jpg"  # 테스트할 이미지 경로
#     frame = cv2.imread(image_path)
#     frame = cv2.resize(frame, (960, 1280))  # Mocking a frame for testing
#     # cap = cv2.VideoCapture(0)
#     # if not cap.isOpened():
#     #     logging.error("Failed to open camera 0)
#     #     exit()
#     # width, height = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
#     width, height = frame.shape[1], frame.shape[0]
#     shot_position = (width//2, height//2)
#     while True:
#         # ret, frame = cap.read()
#         ret = True  # Mocking the frame read for testing
#         if ret:
#             result = detect_ball(frame, shot_position)
#             ball_queue.put(result)
#             logging.debug(f"Ball detection result: {result}")
#         else:
#             logging.error("Failed to read frame from camera 0")
#         time.sleep(0.033)

# def ir_sensor_process():
#     time.sleep(6)  # 공 탐지 후 1초 뒤 IR 센서 신호
#     setup_ir_sensor(ir_queue, is_ready)
#     while True:
#         time.sleep(0.1)

# def vibration_sensor_process():
#     time.sleep(7.7)  # test speed_calculator
#     chan = setup_vibration_sensor()
#     chan.set_voltage(1.5)  # 초기 전압 설정
#     if chan is None:
#         logging.error("Vibration sensor setup failed")
#         exit()
#         #for debugging
#     detect_vibration(vib_queue,impact_queue,is_ready,chan)
#     while True:
#         #실제 라즈베리 파이 작동 코드
#         # detect_vibration(chan)
#         # logging.debug(f"Vibration detection")
#         time.sleep(0.004)

# def impact_analysis_process(shared_data):
#     import cv2
#     logging.info("Starting impact_analysis_process")
#     frames = deque(maxlen=30)  # 최대 30개의 프레임 저장

#     video_path = "./resource/test2.mp4"  # Video file for testing
#     cap = cv2.VideoCapture(video_path)
#     if not cap.isOpened():
#         logging.error("Failed to open video file")
#         impact_queue.put({"source": "impact_analyzer", "impact_position": None})
#         return

#     total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#     video_duration = 4.0  # seconds, as specified
#     frame_rate = total_frames / video_duration
#     logging.info(f"Video frame rate: {frame_rate} fps, total frames: {total_frames}")

#     start_time = time.time()

#     while True:
#         with is_ready.get_lock():
#             if is_ready.value:
#                 elapsed_time = time.time() - start_time
#                 target_frame = int(elapsed_time * frame_rate) % total_frames
#                 logging.debug(f"Elapsed time: {elapsed_time:.2f}s, Target frame: {target_frame}")

#                 cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
#                 ret, frame = cap.read()
#                 if ret:
#                     timestamp = time.time()
#                     frames.append((timestamp, frame))
#                     logging.debug(f"Frame {target_frame} captured at {timestamp}")
#                 else:
#                     logging.error(f"Failed to read frame {target_frame}")
#                     break

#         if shared_data["vib_timestamp"] is not None:
#             logging.debug(f" vib_timestamp {shared_data['vib_timestamp']}")
#             closest_frame = find_closest_frame(frames, shared_data["vib_timestamp"])
#             if closest_frame is not None:
#                 logging.info("Closest frame found")
#                 result = analyze_impact([closest_frame])
#                 impact_queue.put(result)
#                 logging.debug(f"Impact analysis result: {result}")
#                 print("Impact analysis finished ")
#                 break
#             else:
#                 logging.warning("No matching frame found for vibration timestamp")

#         time.sleep(0.033)

#     cap.release()
#     logging.info("Impact analysis process completed")



# class MainApp:
#     def __init__(self):
#         self.shared_data = Manager.dict()  # 공유 데이터 생성
#         self.shared_data["vib_timestamp"] = None  # 초기값 설정
#         self.shared_data["ir_timestamp"] = None
#         self.shared_data["impact_position"] = None
#         self.shared_data["speed"] = None

#         self.app = QApplication(sys.argv)
#         screens = self.app.screens()
#         target_screen = screens[1] if len(screens) > 1 else screens[0]
#         self.geometry = target_screen.geometry()
#         self.width, self.height = self.geometry.width(), self.geometry.height()
#         self.ui = BallDetectionUI(self.width, self.height)
#         self.ui.move(self.geometry.x(), self.geometry.y())
#         self.ui.showFullScreen()

#         self.start_processes()

#         self.timer = QTimer()
#         self.timer.timeout.connect(self.check_queues)
#         self.timer.start(50)
#         logging.info("MainApp initialized, processes started")

#     def start_processes(self):
#         logging.info("Starting ball_detection_process")
#         self.p1 = Process(target=ball_detection_process)
#         self.p1.start()
#         time.sleep(1)  # 프로세스 시작 후 1초 대기

#         logging.info("Starting ir_sensor_process")
#         self.p2 = Process(target=ir_sensor_process)
#         self.p2.start()
#         time.sleep(1)  # 프로세스 시작 후 1초 대기

#         logging.info("Starting vibration_sensor_process")
#         self.p3 = Process(target=vibration_sensor_process)
#         self.p3.start()

#         logging.info("Start impact analysis process")
#         self.p4 = Process(target=impact_analysis_process, args=(self.shared_data,))

#     def reset_queues(self):
#         # Clear existing queues and create new ones
#         while not ball_queue.empty():
#             ball_queue.get()
#         while not ir_queue.empty():
#             ir_queue.get()
#         while not vib_queue.empty():
#             vib_queue.get()
#         while not impact_queue.empty():
#             impact_queue.get()

#         ball_queue = Queue(maxsize=1000000)
#         ir_queue = Queue(maxsize=1000000)
#         vib_queue = Queue(maxsize=1000000)
#         impact_queue = Queue(maxsize=1000000)
#         logging.info("All queues reset")

#     def check_queues(self):
#         # Check ball detection queue
#         while not ball_queue.empty():
#             try:
#                 data = ball_queue.get()
#                 logging.debug(f"Ball queue data: {data}")
#                 if data.get("source") == "ball_detector" and data.get("enable_ir"):
#                     with is_ready.get_lock():
#                         is_ready.value = True
#                     QApplication.postEvent(self.ui, QCustomEvent(self.ui.handle_ir_detected))
#             except Exception as e:
#                 logging.error(f"Ball queue error: {e}")

#         # Check IR sensor queue
#         while not ir_queue.empty():
#             try:
#                 data = ir_queue.get()
#                 logging.debug(f"IR queue data: {data}")
#                 if data.get("source") == "ir_sensor" and data.get("event") == "ir_trigger":
#                     self.ir_timestamp = data["timestamp"]
#                     # Start impact analysis process
#                     self.p4.start()
#             except Exception as e:
#                 logging.error(f"IR queue error: {e}")

#         # Check vibration sensor queue
#         while not vib_queue.empty():
#             try:
#                 data = vib_queue.get()
#                 logging.debug(f"Vibration queue data: {data}")
#                 if data.get("source") == "vibration_sensor" and data.get("action") == "speed":
#                     self.vib_timestamp = data["timestamp"]
#                     if self.ir_timestamp:
#                         speed_result = calculate_speed(self.ir_timestamp, self.vib_timestamp)
#                         print(f"Calculated speed: {speed_result}")
#                         vib_queue.put(speed_result)  # Put back to vib_queue for consistency
#                         self.ir_timestamp = None
#                         self.vib_timestamp = None
#                 elif data.get("source") == "speed_calculator" and "speed" in data:
#                     self.speed = data["speed"]
#                 elif data.get("source") == "vibration_sensor" and data.get("action") == "impact":
#                     impact_queue.put(data)  # Forward vibration data to impact queue
#             except Exception as e:
#                 logging.error(f"Vibration queue error: {e}")

#         # Check impact analysis queue
#         while not impact_queue.empty():
#             try:
#                 data = impact_queue.get()
#                 logging.debug(f"Impact queue data: {data}")
#                 if data.get("source") == "impact_analyzer" and "impact_position" in data:
#                     self.impact_position = data["impact_position"]
#                     QApplication.postEvent(self.ui, QCustomEvent(lambda: self.ui.handle_camera_detected(self.speed, self.impact_position)))
#                 elif data.get("source") == "impact_analyzer" and data.get("action") == "reset_queues":
#                     self.reset_queues()
#                 elif data.get("source") == "vibration_sensor" and data.get("action") == "impact":
#                     self.shared_data["vib_timestamp"] = data["timestamp"]
#                     logging.info(f"Vibration sensor triggered at {self.shared_data['vib_timestamp']}")
#             except Exception as e:
#                 logging.error(f"Impact queue error: {e}")

#     def run(self):
#         sys.exit(self.app.exec_())

# if __name__ == "__main__":
#     MainApp().run()

from ir_sensor import setup_ir_sensor
from vibration_sensor import setup_vibration_sensor, detect_vibration
from speed_calculator import calculate_speed
from impact_analyzer import analyze_impact, find_closest_frame
from send_event import QCustomEvent
import sys
from queue import Queue
from ball_detector import detect_ball
from UI_display import BallDetectionUI
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QEvent
from multiprocessing import Process, Queue, Value, Manager
from collections import deque
import time
import logging
from PyQt5.QtGui import QKeyEvent

logging.basicConfig(level=logging.DEBUG, filename="debug.log", filemode="w")

# 전역 변수 선언
Manager = Manager()
ball_queue = Manager.Queue()
ir_queue = Manager.Queue()
vib_queue = Manager.Queue()
impact_queue = Manager.Queue()
is_ready = Value('b', False)


def ball_detection_process():
    time.sleep(5)  # Wait for other processes to initialize
    import cv2
    image_path = "resource/lower_test1.jpg"  # 테스트할 이미지 경로
    frame = cv2.imread(image_path)
    frame = cv2.resize(frame, (960, 1280))  # Mocking a frame for testing
    # cap = cv2.VideoCapture(0)
    # if not cap.isOpened():
    #     logging.error("Failed to open camera 0)
    #     exit()
    # keypad_arrow_left_alt_key
    # width, height = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width, height = frame.shape[1], frame.shape[0]
    shot_position = (width//2, height//2)
    while True:
        # ret, frame = cap.read()
        ret = True  # Mocking the frame read for testing
        if ret:
            result = detect_ball(frame, shot_position)
            ball_queue.put(result)

            logging.debug(f"Ball detection result: {result}")
            break
        else:
            logging.error("Failed to read frame from camera 0")
        time.sleep(0.033)

def ir_sensor_process():
    time.sleep(6)  # 공 탐지 후 1초 뒤 IR 센서 신호
    setup_ir_sensor(ir_queue, is_ready)
    while True:
        time.sleep(0.1)

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

    video_path = "./resource/test2.mp4"  # Video file for testing
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logging.error("Failed to open video file")
        impact_queue.put({"source": "impact_analyzer", "impact_position": None, "frame": None})
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_duration = 4   # seconds, as specified
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

class MainApp:
    def __init__(self):
        self.shared_data = Manager.dict()  # 공유 데이터 생성
        self.shared_data["vib_timestamp"] = None  # 초기값 설정
        self.shared_data["ir_timestamp"] = None
        self.shared_data["impact_position"] = None
        self.shared_data["speed"] = None

        self.app = QApplication(sys.argv)
        screens = self.app.screens()
        target_screen = screens[1] if len(screens) > 1 else screens[0]
        self.geometry = target_screen.geometry()
        self.width, self.height = self.geometry.width(), self.geometry.height()
        self.ui = BallDetectionUI(self.width, self.height)
        self.ui.move(self.geometry.x(), self.geometry.y())
        self.ui.showFullScreen()

        self.start_processes()

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_queues)
        self.timer.start(50)
        logging.info("MainApp initialized, processes started")

    def start_processes(self):
        logging.info("Starting ball_detection_process")
        self.p1 = Process(target=ball_detection_process)
        self.p1.start()
        time.sleep(1)  # 프로세스 시작 후 1초 대기

        logging.info("Starting ir_sensor_process")
        self.p2 = Process(target=ir_sensor_process)
        self.p2.start()
        time.sleep(1)  # 프로세스 시작 후 1초 대기

        logging.info("Starting vibration_sensor_process")
        self.p3 = Process(target=vibration_sensor_process)
        self.p3.start()

        logging.info("Start impact analysis process")
        self.p4 = Process(target=impact_analysis_process, args=(self.shared_data,))

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
                        is_ready.value = True
                        print("공 탐지")
                    QApplication.postEvent(self.ui, QCustomEvent(self.ui.handle_ir_detected))
            except Exception as e:
                logging.error(f"Ball queue error: {e}")

        # Check IR sensor queue
        while not ir_queue.empty():
            try:
                data = ir_queue.get()
                logging.debug(f"IR queue data: {data}")
                if data.get("source") == "ir_sensor" and data.get("event") == "ir_trigger":
                    self.shared_data["ir_timestamp"] = data["timestamp"]
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

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    MainApp().run()