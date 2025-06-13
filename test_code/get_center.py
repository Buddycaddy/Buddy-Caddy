import cv2
import numpy as np

# 비디오 캡처 (영상 파일 경로로 변경, 예: 'test3.mp4')
cap = cv2.VideoCapture('resource/test1.mp4')  # 영상 파일 경로를 실제 파일로 변경
if not cap.isOpened():
    print("영상을 열 수 없습니다.")
    exit()

# 초기 프레임 로드
ret, prev_frame = cap.read()
if not ret:
    print("초기 프레임 로드 실패")
    exit()

# 세로 절반 분할
height, width = prev_frame.shape[:2]
half_height = height // 2
roi_prev = prev_frame[0:half_height, 0:width]
prev_gray = cv2.cvtColor(roi_prev, cv2.COLOR_BGR2GRAY)

# 충돌 감지 플래그와 임계값, 최대 강도 추적 변수
threshold = 10.0  # 움직임 크기 임계값 (조정 필요)
collision_detected = False
collision_point = None
max_magnitude_global = 0.0  # 영상 전체에서 최대 강도
max_point_global = (0, 0)  # 영상 전체에서 최대 강도 지점

# 처음 강도가 25를 넘은 지점 추적 변수
first_high_magnitude_detected = False
first_high_magnitude_point = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 세로 절반 영역
    roi = frame[0:half_height, 0:width]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # Farneback Optical Flow 계산
    flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])

    # 움직임 크기 정규화 (히트맵용)s
    flow_magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
    flow_magnitude = flow_magnitude.astype(np.uint8)

    # 처음 강도가 25를 넘은 지점 감지
    if not first_high_magnitude_detected and np.max(magnitude) > 20:
        first_high_magnitude_detected = True
        max_idx = np.unravel_index(np.argmax(magnitude), magnitude.shape)
        first_high_magnitude_point = (max_idx[1], max_idx[0])  # (x, y) 좌표
        print(f"First magnitude > 20 detected at: {first_high_magnitude_point}")
        cv2.circle(roi, first_high_magnitude_point, 10, (0, 255, 255), -1)  # 노란색 원

    # 충돌 감지
    mean_magnitude = np.mean(magnitude)
    max_magnitude = np.max(magnitude)
    # print(f"Mean Magnitude: {mean_magnitude}")
    print(f"Max Magnitude: {max_magnitude}")

    if mean_magnitude < threshold and not collision_detected:
        collision_detected = True
        collision_point = (width // 2, half_height // 2)  # 대략적인 충돌 지점
        cv2.circle(roi, collision_point, 10, (0, 0, 255), -1)  # 충돌 지점 표시
        print(f"Collision detected at: {collision_point}")

    # 가장 강도가 강한 부분 찾기
    max_magnitude = np.max(magnitude)
    max_idx = np.unravel_index(np.argmax(magnitude), magnitude.shape)
    max_point = (max_idx[1], max_idx[0])  # (x, y) 좌표

    # 영상 전체에서 최대 강도 업데이트
    if max_magnitude > max_magnitude_global:
        max_magnitude_global = max_magnitude
        max_point_global = max_point

    # 최대 강도 지점에 원 그리기
    cv2.circle(roi, max_point, 10, (255, 0, 0), -1)  # 파란색 원
    # 최대 강도 텍스트 표시 (원 옆에)
    cv2.putText(roi, f'{max_magnitude:.1f}', (max_point[0] + 15, max_point[1]), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # Optical Flow 변화 시각화 (히트맵)
    flow_heatmap = cv2.applyColorMap(flow_magnitude, cv2.COLORMAP_JET)

    # 이미지와 히트맵을 수평으로 결합
    combined = np.hstack((roi, flow_heatmap))

    # 결과 표시
    cv2.imshow('Frame with Flow Heatmap', combined)

    # 이전 프레임 업데이트
    prev_gray = gray.copy()

    # 천천히 보기 (60ms 대기, 약 16fps)
    if cv2.waitKey(50) & 0xFF == 27:
        break

# 영상 끝난 후 최대 강도 지점 표시
if max_magnitude_global > 0:
    final_frame = prev_frame.copy()  # 마지막 프레임 사용
    final_roi = final_frame[0:half_height, 0:width]
    print(f"Global Max Magnitude: {max_magnitude_global} at {max_point_global}")
    
    # 노란색 원 (처음 강도가 25를 넘은 지점)
    cv2.circle(final_roi, first_high_magnitude_point, 10, (0, 255, 255), -1)
    
    # 초록색 원 (최대 강도 지점)
    cv2.circle(final_roi, max_point_global, 10, (0, 255, 0), -1)
    
    # 두 원의 중간 지점 계산
    midpoint = ((first_high_magnitude_point[0] + max_point_global[0]) // 2,
                (first_high_magnitude_point[1] + max_point_global[1]) // 2)
    
    # 중간 지점에 원 그리기 (파란색 원)
    cv2.circle(final_roi, midpoint, 10, (255, 0, 0), -1)
    print(f"Midpoint between the two points: {midpoint}")
    
    # 결과 표시
    cv2.putText(final_roi, f'Max: {max_magnitude_global:.1f}', (max_point_global[0] + 15, max_point_global[1]), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.imshow('Max Magnitude Point', final_roi)
    cv2.waitKey(0)  # 키 입력 대기 후 닫기
    cv2.destroyWindow('Max Magnitude Point')

cap.release()
cv2.destroyAllWindows()