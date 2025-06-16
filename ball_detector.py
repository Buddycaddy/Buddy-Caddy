import cv2
import numpy as np
import time
import json
from datetime import datetime

# Ball detection using OpenCV
# This function detects a ball in the given frame based on color and position.  
# 하단 카메라에서 공을 감지  , User에게 시작 신호 전달

def detect_ball(frame, shot_position, radius_threshold=600):
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
    # cv2.imshow("Green Mask", mask_green)  # 초록색 마스크 표시
    # 전체 마스크에서 초록색 영역 제외
    mask_non_green = cv2.bitwise_not(mask_green)
    
    # 흰색 마스크 생성
    mask_white = cv2.inRange(hsv, lower_white, upper_white)
    # cv2.imshow("White Mask", mask_white)  # 흰색 마스크 표시
    
    # 초록색이 아닌 영역에서 흰색만 추출
    mask = cv2.bitwise_and(mask_white, mask_non_green)
    cv2.imshow("Combined Mask", mask)  # 최종 마스크 표시
    
    # 노이즈 제거를 위한 침식과 팽창

    mask = cv2.dilate(mask, None, iterations=2)
    mask = cv2.erode(mask, None, iterations=2)

    # HoughCircles로 원 감지

    circles = cv2.HoughCircles(
        mask,
        cv2.HOUGH_GRADIENT,
        dp=1,           # 정밀도 유지
        minDist=30,     # 노이즈로 인한 중복 감지 방지
        param1=30,      # Canny 에지 임계값 낮춤 (경계 감지 강화)
        param2=15,      # 축적 배열 임계값 낮춤 (약한 원도 감지)
        minRadius=10,    # 최소 반지름
        maxRadius=30    # 최대 반지름 (원 크기 확장)
    )

    #debugging용 원 그리기

    # 원을 마스크 위에 표시
    # if circles is not None:
    #     circles = np.uint16(np.around(circles))
    #     for circle in circles[0, :]:
    #         x, y, r = circle
    #         cv2.circle(frame, (x, y), r, (255, 0, 255), 2)  # 원 테두리 표시
    # else:
    #     print("No circles detected")
    
    # 마스크와 감지된 원 표시
    # cv2.imshow("Mask with circles", frame)

    if circles is not None:
        circles = np.int16(np.around(circles))
        x, y, r = circles[0][0]
        distance = np.sqrt((x - shot_position[0])**2 + (y - shot_position[1])**2)
        if distance < radius_threshold:

            timestamp = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            return {
                "source": "ball_detector",
                "detected": True,
                "position": (int(x), int(y)),
                "radius": int(r),
                "timestamp": timestamp,
                "enable_ir": True  # IR 센서 활성화 플래그 추가
            }
    
    timestamp = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    return {
        "source": "ball_detector",
        "detected": False,
        "position": None,
        "radius": None,
        "timestamp": timestamp,
        "enable_ir": False
    }
if __name__ == "__main__":
    # 비디오 캡처 부분 주석 처리
    cap = cv2.VideoCapture(0)
    shot_position = (960, 1280)  # 예: 프레임 중앙
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
    cv2.imwrite("res_img.png", frame)
    # 추가

#  # 결과 시각화
#     if result["detected"]:
#         x, y = map(int, result["position"])  # 좌표를 int로 변환
#         r = result["radius"]
#         cv2.circle(frame, (x, y), r, (0, 255, 0), 2)  # 감지된 공 위치 표시
#         cv2.putText(frame, "Ball Detected", (x + 15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    # print(json.dumps(result))  # JSON 직렬화 가능

    
    # cv2.imshow("Ball Detection", frame)
    # cv2.waitKey(0)
    cv2.destroyAllWindows()

