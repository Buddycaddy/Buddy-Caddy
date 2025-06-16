from multiprocessing import Process, Queue
from ball_detector import detect_ball
from ir_sensor import setup_ir_sensor
from vibration_sensor import setup_vibration_sensor, detect_vibration
from speed_calculator import calculate_speed
from impact_analyzer import analyze_impact
from UI_display import BallDetectionUI

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import sys
import cv2
from collections import deque
import time

def ball_detection_process(queue):
    cap = cv2.VideoCapture(0)
    shot_position = (320, 240)
    while True:
        ret, frame = cap.read()
        if ret:
            result = detect_ball(frame, shot_position)
            queue.put(result)

def ir_sensor_process(queue):
    setup_ir_sensor()
    while True:
        time.sleep(1)  # IR callback internally sends to queue

def vibration_sensor_process(queue):
    chan = setup_vibration_sensor()
    while True:
        result = detect_vibration(chan)
        if result:
            queue.put(result)
        time.sleep(0.004)

def impact_analysis_process(queue, vib_timestamp):
    cap = cv2.VideoCapture(1)
    frames = deque(maxlen=5)
    while True:
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
            if vib_timestamp:
                result = analyze_impact(frames)
                queue.put(result)
                break

class MainApp:
    def __init__(self):
        self.queue = Queue()
        self.ir_timestamp = None
        self.vib_timestamp = None

        self.app = QApplication(sys.argv)
        screen = self.app.primaryScreen().geometry()
        self.ui = BallDetectionUI(screen.width(), screen.height())
        self.ui.showFullScreen()

        self.start_processes()

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_queue)
        self.timer.start(50)

    def start_processes(self):
        self.p1 = Process(target=ball_detection_process, args=(self.queue,))
        self.p2 = Process(target=ir_sensor_process, args=(self.queue,))
        self.p3 = Process(target=vibration_sensor_process, args=(self.queue,))
        self.p1.start()
        self.p2.start()
        self.p3.start()

    def check_queue(self):
        while not self.queue.empty():
            data = self.queue.get()
            if "detected" in data:
                self.ui.handle_ir_detected()
            if data.get("event") == "ir_trigger":
                self.ir_timestamp = data["timestamp"]
            if data.get("event") == "vibration_trigger":
                self.vib_timestamp = data["timestamp"]
                Process(target=impact_analysis_process, args=(self.queue, self.vib_timestamp)).start()
            if self.ir_timestamp and self.vib_timestamp:
                speed = calculate_speed(self.ir_timestamp, self.vib_timestamp)
                self.ui.speed_value = speed
                self.ir_timestamp = None
                self.vib_timestamp = None
            if "impact_position" in data:
                self.ui.handle_camera_detected()

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    MainApp().run()






# 처음부터 다시 수정하기 전 코드들

# from multiprocessing import Process, Queue
# from collections import deque
# import json
# import time
# import sys
# from ir_sensor import setup_ir_sensor
# from vibration_sensor import vibration_sensor_process
# from speed_calculator import calculate_speed
# from impact_analyzer import analyze_impact
# from ball_detector import detect_ball
# from PyQt5.QtWidgets import QApplication
# import cv2
# import threading
# import numpy as np

# # 시뮬레이션용 모드 설정
# IS_SIMULATE = True

# # UI 없는 시뮬레이션용 업데이트 함수
# def print_update(data):
#     print("[UPDATE]", data)

# def dummy_detect_ball(frame, shot_position):
#     # 시뮬레이션용 더미 결과
#     return {"detected": True, "position": shot_position}

# def ball_detection_process(queue):
#     if IS_SIMULATE:
#         while True:
#             dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
#             result = dummy_detect_ball(dummy_frame, (320, 240))
#             queue.put(result)
#             time.sleep(1)
#     else:
#         cap = cv2.VideoCapture(0)
#         shot_position = (320, 240)
#         while True:
#             ret, frame = cap.read()
#             if ret:
#                 result = detect_ball(frame, shot_position)
#                 queue.put(result)


# def ir_sensor_process(queue):
#     setup_ir_sensor(queue, simulate=IS_SIMULATE)
#     while True:
#         time.sleep(1)


# def vibration_sensor_process_wrapper(queue):
#     vibration_sensor_process(queue, simulate=IS_SIMULATE)


# def impact_analysis_process(queue, vib_timestamp):
#     if IS_SIMULATE:
#         time.sleep(1)
#         result = {"impact_position": (320, 240)}
#         queue.put(result)
#     else:
#         cap = cv2.VideoCapture(1)
#         frames = deque(maxlen=5)
#         while True:
#             ret, frame = cap.read()
#             if ret:
#                 frames.append(frame)
#                 if vib_timestamp:
#                     result = analyze_impact(frames)
#                     queue.put(result)
#                     break

# def update_loop(queue):
#     ir_timestamp = None
#     vib_timestamp = None
#     while True:
#         if not queue.empty():
#             data = queue.get()
#             if isinstance(data, dict) and data.get("event") == "ir_trigger":
#                 ir_timestamp = data["timestamp"]
#             elif isinstance(data, dict) and data.get("event") == "vibration_trigger":
#                 vib_timestamp = data["timestamp"]
#             elif "impact_position" in data:
#                 print_update(data)
#             elif isinstance(data, (float, int)):
#                 print_update(data)
#             elif isinstance(data, dict) and "detected" in data:
#                 print_update(data)

#             if ir_timestamp and vib_timestamp:
#                 speed = calculate_speed(ir_timestamp, vib_timestamp)
#                 print_update(speed)
#                 ir_timestamp = None
#                 vib_timestamp = None

# def main():
#     queue = Queue()

#     p1 = Process(target=ball_detection_process, args=(queue,))
#     p2 = Process(target=ir_sensor_process, args=(queue,))
#     p3 = Process(target=vibration_sensor_process_wrapper, args=(queue,))

#     p1.start()
#     p2.start()
#     p3.start()

#     # update_loop(queue)

#     start_pyqt_ui(queue)  # 여기는 Process가 아니라 그냥 함수 호출!

#     p1.join()
#     p2.join()
#     p3.join()

# if __name__ == "__main__":
#     main()





# # from multiprocessing import Process, Queue
# # import json
# # import time
# # from ball_detector import detect_ball
# # from ir_sensor import setup_ir_sensor
# # from vibration_sensor import setup_vibration_sensor, detect_vibration
# # from speed_calculator import calculate_speed
# # from impact_analyzer import analyze_impact
# # from UI_display import GolfUI
# # import tkinter as tk
# # import cv2

# # def ball_detection_process(queue):
# #     cap = cv2.VideoCapture(0)
# #     shot_position = (320, 240)
# #     while True:
# #         ret, frame = cap.read()
# #         if ret:
# #             result = detect_ball(frame, shot_position)
# #             queue.put(result)

# # def ir_sensor_process(queue):
# #     setup_ir_sensor()
# #     # IR 콜백이 queue에 직접 넣음
# #     while True:
# #         time.sleep(1)

# # def vibration_sensor_process(queue):
# #     chan = setup_vibration_sensor()
# #     while True:
# #         result = detect_vibration(chan)
# #         if result:
# #             queue.put(result)
# #         time.sleep(0.004)

# # def impact_analysis_process(queue, vib_timestamp):
# #     cap = cv2.VideoCapture(1)  # 천막 카메라
# #     frames = deque(maxlen=5)
# #     while True:
# #         ret, frame = cap.read()
# #         if ret:
# #             frames.append(frame)
# #             if vib_timestamp:
# #                 result = analyze_impact(frames)
# #                 queue.put(result)
# #                 vib_timestamp = None

# # def main():
# #     queue = Queue()
# #     root = tk.Tk()
# #     ui = GolfUI(root)
    
# #     p1 = Process(target=ball_detection_process, args=(queue,))
# #     p2 = Process(target=ir_sensor_process, args=(queue,))
# #     p3 = Process(target=vibration_sensor_process, args=(queue,))
# #     p1.start()
# #     p2.start()
# #     p3.start()
    
# #     ir_timestamp = None
# #     vib_timestamp = None
    
# #     while True:
# #         if not queue.empty():
# #             data = queue.get()
# #             if "detected" in data:
# #                 ui.update(data)
# #             if data.get("event") == "ir_trigger":
# #                 ir_timestamp = data["timestamp"]
# #             if data.get("event") == "vibration_trigger":
# #                 vib_timestamp = data["timestamp"]
# #                 p4 = Process(target=impact_analysis_process, args=(queue, vib_timestamp))
# #                 p4.start()
# #             if ir_timestamp and vib_timestamp:
# #                 speed = calculate_speed(ir_timestamp, vib_timestamp)
# #                 ui.update(speed)
# #                 ir_timestamp = None
# #                 vib_timestamp = None
# #             if "impact_position" in data:
# #                 ui.update(data)
# #         root.update()

# # if __name__ == "__main__":
# #     main()