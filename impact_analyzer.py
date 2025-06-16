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





# 처음부터 다시 수정하기 전 코드들

# import cv2
# import numpy as np
# import random

# IS_SIMULATE = True  # 시뮬레이션 여부 (True면 랜덤 위치 반환)

# def analyze_impact(frames):
#     if IS_SIMULATE:
#         # 시뮬레이션 모드: 랜덤 좌표 생성
#         cx = random.randint(100, 540)
#         cy = random.randint(100, 380)
#         return {"impact_position": (cx, cy)}

#     if len(frames) < 2:
#         return {}

#     prev_frame = cv2.cvtColor(frames[-2], cv2.COLOR_BGR2GRAY)
#     curr_frame = cv2.cvtColor(frames[-1], cv2.COLOR_BGR2GRAY)

#     diff = cv2.absdiff(prev_frame, curr_frame)
#     blurred = cv2.GaussianBlur(diff, (5, 5), 0)
#     _, thresh = cv2.threshold(blurred, 25, 255, cv2.THRESH_BINARY)

#     contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     if contours:
#         largest = max(contours, key=cv2.contourArea)
#         if cv2.contourArea(largest) > 100:
#             x, y, w, h = cv2.boundingRect(largest)
#             cx = x + w // 2
#             cy = y + h // 2
#             return {"impact_position": (cx, cy)}

#     return {}







# # import cv2
# # import numpy as np
# # import json
# # from collections import deque

# # def analyze_impact(frames, fps=30):
# #     for frame in frames:
# #         hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
# #         lower_white = np.array([0, 0, 200])
# #         upper_white = np.array([180, 30, 255])
# #         mask = cv2.inRange(hsv, lower_white, upper_white)
# #         circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
# #                                    param1=50, param2=30, minRadius=5, maxRadius=20)
# #         if circles is not None:
# #             x, y, r = np.uint16(np.around(circles[0][0]))
# #             return {"impact_position": (x, y)}
# #     return {"impact_position": None}

# # if __name__ == "__main__":
# #     cap = cv2.VideoCapture(0)
# #     frames = deque(maxlen=5)
# #     while True:
# #         ret, frame = cap.read()
# #         if not ret:
# #             break
# #         frames.append(frame)
# #         if len(frames) == 5:
# #             result = analyze_impact(frames)
# #             print(json.dumps(result))
# #         if cv2.waitKey(1) & 0xFF == ord('q'):
# #             break
# #     cap.release()
# #     cv2.destroyAllWindows()