import cv2
import numpy as np
import json
from collections import deque

def analyze_impact(frames, fps=30):
    for frame in frames:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])
        mask = cv2.inRange(hsv, lower_white, upper_white)
        circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                                   param1=50, param2=30, minRadius=5, maxRadius=20)
        if circles is not None:
            x, y, r = np.uint16(np.around(circles[0][0]))
            return {"impact_position": (x, y)}
    return {"impact_position": None}

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    frames = deque(maxlen=5)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
        if len(frames) == 5:
            result = analyze_impact(frames)
            print(json.dumps(result))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()