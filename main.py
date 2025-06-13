from multiprocessing import Process, Queue
import json
import time
from ball_detector import detect_ball
from ir_sensor import setup_ir_sensor
from vibration_sensor import setup_vibration_sensor, detect_vibration
from speed_calculator import calculate_speed
from impact_analyzer import analyze_impact
from UI_display import GolfUI
import tkinter as tk
import cv2

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
    # IR 콜백이 queue에 직접 넣음
    while True:
        time.sleep(1)

def vibration_sensor_process(queue):
    chan = setup_vibration_sensor()
    while True:
        result = detect_vibration(chan)
        if result:
            queue.put(result)
        time.sleep(0.004)

def impact_analysis_process(queue, vib_timestamp):
    cap = cv2.VideoCapture(1)  # 천막 카메라
    frames = deque(maxlen=5)
    while True:
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
            if vib_timestamp:
                result = analyze_impact(frames)
                queue.put(result)
                vib_timestamp = None

def main():
    queue = Queue()
    root = tk.Tk()
    ui = GolfUI(root)
    
    p1 = Process(target=ball_detection_process, args=(queue,))
    p2 = Process(target=ir_sensor_process, args=(queue,))
    p3 = Process(target=vibration_sensor_process, args=(queue,))
    p1.start()
    p2.start()
    p3.start()
    
    ir_timestamp = None
    vib_timestamp = None
    
    while True:
        if not queue.empty():
            data = queue.get()
            if "detected" in data:
                ui.update(data)
            if data.get("event") == "ir_trigger":
                ir_timestamp = data["timestamp"]
            if data.get("event") == "vibration_trigger":
                vib_timestamp = data["timestamp"]
                p4 = Process(target=impact_analysis_process, args=(queue, vib_timestamp))
                p4.start()
            if ir_timestamp and vib_timestamp:
                speed = calculate_speed(ir_timestamp, vib_timestamp)
                ui.update(speed)
                ir_timestamp = None
                vib_timestamp = None
            if "impact_position" in data:
                ui.update(data)
        root.update()

if __name__ == "__main__":
    main()