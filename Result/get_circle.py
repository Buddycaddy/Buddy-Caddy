import cv2
import numpy as np

# 예시용 빈 이미지 생성 (300x300, 흰색)
img = cv2.imread("impact_analyze-example/frame_003.jpg")


# 원의 정보
center = (59, 246)
radius = 25

# 원 그리기 (파란색, 두께 2)
cv2.circle(img, center, radius, (255, 0, 0), 2)

# 중심점 표시 (빨간색, 반지름 3)
cv2.circle(img, center, 3, (0, 0, 255), -1)

# 이미지 출력
cv2.imshow("Circle Example", img)
cv2.waitKey(0)
cv2.destroyAllWindows()