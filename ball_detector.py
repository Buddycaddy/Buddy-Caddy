import numpy as np
import time
import json
from datetime import datetime
from picamera2 import Picamera2

# Ball detection using OpenCV
# This function detects a ball in the given frame based on color and position.  
# 하단 카메라에서 공을 감지  , User에게 시작 신호 전달

def detect_ball(frame, shot_position, radius_threshold=600, stable_threshold=1.0):
    import cv2
    import time

    # 공의 이전 위치와 시간을 저장하기 위한 변수
    static_ball_position = None
    last_detected_time = None

    # 프레임을 HSV 색상 공간으로 변환
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 초록색 잔디 영역 정의 (HSV 범위)
    lower_green = np.array([35, 50, 50])   # 초록색 하한
    upper_green = np.array([85, 255, 255]) # 초록색 상한

    # 흰색 공 영역 정의 (HSV 범위)
    lower_white = np.array([0, 0, 200])    # 흰색 하한
    upper_white = np.array([180, 30, 255]) # 흰색 상한

    # 초록색 마스크 생성
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_non_green = cv2.bitwise_not(mask_green)

    # 흰색 마스크 생성
    mask_white = cv2.inRange(hsv, lower_white, upper_white)

    # 초록색이 아닌 영역에서 흰색만 추출
    mask = cv2.bitwise_and(mask_white, mask_non_green)

    # 노이즈 제거를 위한 침식과 팽창
    mask = cv2.dilate(mask, None, iterations=2)
    mask = cv2.erode(mask, None, iterations=2)

    # HoughCircles로 원 감지
    circles = cv2.HoughCircles(
        mask,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=30,
        param1=30,
        param2=15,
        minRadius=10,
        maxRadius=30
    )

    if circles is not None:
        circles = np.int16(np.around(circles))
        x, y, r = circles[0][0]
        distance = np.sqrt((x - shot_position[0])**2 + (y - shot_position[1])**2)

        if distance < radius_threshold:
            timestamp = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

            # 공의 위치가 이전 위치와 동일한지 확인
            if static_ball_position is not None and last_detected_time is not None:
                if (x, y) == static_ball_position:
                    elapsed_time = time.time() - last_detected_time
                    if elapsed_time >= stable_threshold:
                        return {
                            "source": "ball_detector",
                            "detected": True,
                            "position": (int(x), int(y)),
                            "radius": int(r),
                            "timestamp": timestamp,
                            "enable_ir": True,
                            "stable": True  # 공이 안정적임을 나타내는 신호
                        }
                else:
                    # 공의 위치가 변경되었으면 시간 초기화
                    static_ball_position = (x, y)
                    last_detected_time = time.time()
            else:
                # 처음 감지된 경우 위치와 시간 저장
                static_ball_position = (x, y)
                last_detected_time = time.time()

            return {
                "source": "ball_detector",
                "detected": True,
                "position": (int(x), int(y)),
                "radius": int(r),
                "timestamp": timestamp,
                "enable_ir": True,
                "stable": False  # 공이 안정적이지 않음
            }

    timestamp = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    return {
        "source": "ball_detector",
        "detected": False,
        "position": None,
        "radius": None,
        "timestamp": timestamp,
        "enable_ir": False,
        "stable": False
    }
if __name__ == "__main__":
    import cv2
    # 비디오 캡처 부분 주석 처리
    cam = Picamera2(1) 
    cam.start()
    cap = cam.video_capture  # Picamera2의 비디오 캡처 객체 사용
    width, height = cap.shape[1], cap[0].shape[0]
    shot_position = (width//2, height//2)  # 예: 프레임 중앙
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        result = detect_ball(frame, shot_position)

 # 결과 시각화 
        if result["detected"]:
            x, y = map(int, result["position"])  # 좌표를 int로 변환
            r = result["radius"]
            cv2.circle(frame, (x, y), r, (0, 255, 0), 2)  # 감지된 공 위치 표시
            cv2.putText(frame, "Ball Detected", (x + 15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            print(json.dumps(result))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()

    # # 이미지 파일로 테스트
    # image_path = "resource/lower_test1.jpg"  # 테스트할 이미지 경로
    # frame = cv2.imread(image_path)
    # if frame is None:
    #     print("이미지를 열 수 없습니다.")
    #     exit()
    # # 이미지 크기 조정 (리사이즈된 이미지를 반환값으로 저장)
    # frame = cv2.resize(frame, (960, 1280))  # 이미지 크기 조정
    # width, height = frame.shape[1], frame.shape[0]
    # print(f"이미지 크기: {width}x{height}")
    # shot_position = (960, 540)  # 예: 프레임 중앙
    # result = detect_ball(frame, shot_position)

    print(json.dumps(result))  # JSON 직렬화 가능

    # 추가
    # cv2.imwrite("res_img.png", frame)
    # 추가

#  # 결과 시각화
#     if result["detected"]:
#         x, y = map(int, result["position"])  # 좌표를 int로 변환
#         r = result["radius"]
#         cv2.circle(frame, (x, y), r, (0, 255, 0), 2)  # 감지된 공 위치 표시
#         cv2.putText(frame, "Ball Detected", (x + 15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    # print(json.dumps(result))  # JSON 직렬화 가능



