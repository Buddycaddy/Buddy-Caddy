import numpy as np
import time
import json
from datetime import datetime
from picamera2 import Picamera2

# Ball detection using OpenCV
# This function detects a ball in the given frame based on color and position.  
# 하단 카메라에서 공을 감지  , User에게 시작 신호 전달

def detect_ball(frame, prev_position=None, position_stable_tol=5):
    import cv2

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])
    lower_white = np.array([0, 0, 100])
    upper_white = np.array([180, 80, 255])

    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_non_green = cv2.bitwise_not(mask_green)
    mask_white = cv2.inRange(hsv, lower_white, upper_white)
    mask = cv2.bitwise_and(mask_white, mask_non_green)
    mask = cv2.dilate(mask, None, iterations=2)
    mask = cv2.erode(mask, None, iterations=2)
    edge = cv2.Canny(mask, 100, 200)

    circles = cv2.HoughCircles(
        edge,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=30,
        param1=30,
        param2=15,
        minRadius=10,
        maxRadius=30
    )

    is_stable = False
    if circles is not None:
        circles = np.int16(np.around(circles))
        x, y, r = circles[0][0]
        if prev_position is not None:
            move_dist = np.linalg.norm(np.array([x, y]) - np.array(prev_position))
            if move_dist <= position_stable_tol:
                is_stable = True
        return {
            "source": "ball_detector",
            "detected": True,
            "position": (int(x), int(y)),
            "radius": int(r),
            "stable": is_stable,
            "prev_position": (int(x), int(y))
        }

    return {
        "source": "ball_detector",
        "detected": False,
        "position": None,
        "radius": None,
        "stable": False,
        "prev_position": prev_position
    }

if __name__ == "__main__":
    import cv2
    cam = Picamera2(1)
    cam.start()
    prev_position = None
    while True:
        frame = cam.capture_array()
        frame = frame[0:200, 50:400, :]
        # 프레임 타입, shape, dtype 출력
        print("frame type:", type(frame), "shape:", getattr(frame, "shape", None), "dtype:", getattr(frame, "dtype", None))
        if frame is None:
            break
        result = detect_ball(frame, prev_position)
        prev_position = result.get("prev_position")
        if result["detected"]:
            x, y = map(int, result["position"])
            r = result["radius"]
            cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
            cv2.putText(frame, "Ball Detected", (x + 15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            print(json.dumps(result))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        cv2.imshow("Ball Detection", frame)
    cam.stop()




