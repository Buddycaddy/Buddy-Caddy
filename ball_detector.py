import cv2
import numpy as np
import time
import json

def detect_ball(frame, shot_position, radius_threshold=10):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    
    circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                               param1=50, param2=30, minRadius=10, maxRadius=50)
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        x, y, r = circles[0][0]
        distance = np.sqrt((x - shot_position[0])**2 + (y - shot_position[1])**2)
        if distance < radius_threshold:
            return {"detected": True, "position": (x, y), "timestamp": time.time()}
    
    return {"detected": False, "position": None, "timestamp": time.time()}

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    shot_position = (320, 240)  # 예: 프레임 중앙
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        result = detect_ball(frame, shot_position)
        print(json.dumps(result))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()