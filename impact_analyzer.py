# import numpy as np
# import json
# from collections import deque

# def find_closest_frame(frames, target_timestamp):
#     """
#     진동 센서 타임스탬프와 가장 가까운 프레임을 검색
#     """
#     closest_frame = None
#     min_diff = float('inf')

#     for timestamp, frame in frames:
#         diff = abs(timestamp - target_timestamp)
#         if diff < min_diff:
#             min_diff = diff
#             closest_frame = frame

#     return closest_frame

# def analyze_impact(frames, fps=30):
#     import cv2
#     print("Impact analysis started")

#     # 가장 최신 프레임(진동 감지 시점)에서 공 탐지
#     frame = frames[-1] if frames else None
#     print("frame shape:", frame.shape if frame is not None else "None")
#     cv2.imshow("Impact Frame", frame)  # 디버깅용 프레임 표시
#     cv2.waitKey()  # 프레임을 표시하기 위해 잠시 대기
#     if frame is None:
#         return {"impact_position": None}
    
#     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#     lower_white = np.array([0, 0, 200])
#     upper_white = np.array([180, 30, 255])
#     mask = cv2.inRange(hsv, lower_white, upper_white)
#     circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
#                                param1=50, param2=30, minRadius=5, maxRadius=20)
#     if circles is not None:
#         x, y, r = np.uint16(np.around(circles[0][0]))
#         return {"source": "impact_analyzer", "impact_position": (int(x), int(y))}
#     return {"source": "impact_analyzer", "impact_position": None}

# if __name__ == "__main__":
#     import cv2
#     cap = cv2.VideoCapture(0)
#     frames = deque(maxlen=5)
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
#         frames.append(frame)
#         if len(frames) == 5:
#             result = analyze_impact(frames)
#             print(json.dumps(result))
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#     cap.release()
#     cv2.destroyAllWindows()



import numpy as np
import json
from collections import deque

def find_closest_frame(frames, target_timestamp):
    """
    진동 센서 타임스탬프와 가장 가까운 프레임을 검색
    """
    closest_frame = None
    min_diff = float('inf')

    for timestamp, frame in frames:
        diff = abs(timestamp - target_timestamp)
        if diff < min_diff:
            min_diff = diff
            closest_frame = frame

    return closest_frame

def analyze_impact(frames, fps=30):
    import cv2
    print("Impact analysis started")

    # 가장 최신 프레임(진동 감지 시점)에서 공 탐지
    frame = frames[-1] if frames else None
    print("frame shape:", frame.shape if frame is not None else "None")
    if frame is None:
        return {"impact_position": None, "frame": None}
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)
    circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                               param1=50, param2=30, minRadius=5, maxRadius=20)
    if circles is not None:
        x, y, r = np.uint16(np.around(circles[0][0]))
        return {"source": "impact_analyzer", "impact_position": (int(x), int(y)), "frame": frame}
    return {"source": "impact_analyzer", "impact_position": None, "frame": frame}

if __name__ == "__main__":
    import cv2
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