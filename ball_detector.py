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




# 처음부터 다시 수정하기 전 코드들

# import time
# import random
# import datetime

# IS_SIMULATE = True  # True: 시뮬레이션, False: 실제 프레임 분석

# def detect_ball(frame=None, shot_position=(320, 240)):
#     if IS_SIMULATE:
#         # 시뮬레이션 모드: 3~5초 간격으로 감지된 것처럼 반환
#         time.sleep(3 + random.random() * 2)
#         return {
#             "detected": True,
#             "timestamp": datetime.datetime.now().timestamp()
#         }

#     # 실제 프레임 분석이 필요한 경우 아래 코드 사용
#     import cv2
#     import numpy as np

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     blurred = cv2.GaussianBlur(gray, (5, 5), 0)
#     _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)
#     contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     for contour in contours:
#         area = cv2.contourArea(contour)
#         if 50 < area < 500:
#             x, y, w, h = cv2.boundingRect(contour)
#             cx = x + w // 2
#             cy = y + h // 2
#             dist = ((cx - shot_position[0])**2 + (cy - shot_position[1])**2)**0.5
#             if dist < 100:
#                 return {
#                     "detected": True,
#                     "timestamp": datetime.datetime.now().timestamp()
#                 }

#     return {"detected": False}




# # import cv2
# # import numpy as np
# # import time
# # import json

# # def detect_ball(frame, shot_position, radius_threshold=10):
# #     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
# #     lower_white = np.array([0, 0, 200])
# #     upper_white = np.array([180, 30, 255])
# #     mask = cv2.inRange(hsv, lower_white, upper_white)
# #     mask = cv2.erode(mask, None, iterations=2)
# #     mask = cv2.dilate(mask, None, iterations=2)
    
# #     circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
# #                                param1=50, param2=30, minRadius=10, maxRadius=50)
    
# #     if circles is not None:
# #         circles = np.uint16(np.around(circles))
# #         x, y, r = circles[0][0]
# #         distance = np.sqrt((x - shot_position[0])**2 + (y - shot_position[1])**2)
# #         if distance < radius_threshold:
# #             return {"detected": True, "position": (x, y), "timestamp": time.time()}
    
# #     return {"detected": False, "position": None, "timestamp": time.time()}

# # if __name__ == "__main__":
# #     cap = cv2.VideoCapture(0)
# #     shot_position = (320, 240)  # 예: 프레임 중앙
# #     while True:
# #         ret, frame = cap.read()
# #         if not ret:
# #             break
# #         result = detect_ball(frame, shot_position)
# #         print(json.dumps(result))
# #         if cv2.waitKey(1) & 0xFF == ord('q'):
# #             break
# #     cap.release()
# #     cv2.destroyAllWindows()