# import cv2
# import numpy as np

# def find_golfball(image_path):
#     # Load the image
#     image = cv2.imread(image_path)
#     if image is None:
#         raise FileNotFoundError(f"Image not found at {image_path}")
    
#     # Get image dimensions
#     height, width, _ = image.shape
    
#     # Split the image horizontally into two halves (top and bottom)
#     top_half = image[:height // 2, :]
#     bottom_half = image[height // 2:, :]
    
#     # Function to detect golf ball in a given region
#     def detect_golfball(region, is_top_half):
#         # Convert to grayscale
#         gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        
#         # Apply Gaussian blur
#         blurred = cv2.GaussianBlur(gray, (15, 15), 0)
        
#         # Apply Canny edge detection
#         edges = cv2.Canny(blurred, 40, 110, apertureSize=3)
#         kernel = np.ones((3, 3), np.uint8)
#         edges = cv2.dilate(edges, kernel, iterations=1)
#         edges = cv2.erode(edges, kernel, iterations=1)
        
#         # Detect circles using HoughCircles
#         circles = cv2.HoughCircles(
#             edges, 
#             cv2.HOUGH_GRADIENT, 
#             dp=1.0, 
#             minDist=30, 
#             param1=100, 
#             param2=10, 
#             minRadius=5, 
#             maxRadius=10
#         )
        
#         if circles is None:
#             return None, None
        
#         # Find the circle with the highest white pixel ratio
#         circles = np.uint16(np.around(circles))
#         max_white_ratio = 0
#         best_circle = None
        
#         for circle in circles[0, :]:
#             center = (circle[0], circle[1])
#             radius = circle[2]
            
#             # Create a mask for the circle
#             mask = np.zeros_like(gray)
#             cv2.circle(mask, center, radius, 255, -1)
            
#             # Calculate white pixel ratio
#             circle_region = cv2.bitwise_and(gray, gray, mask=mask)

#             # Apply threshold to isolate white pixels
#             _, thresholded = cv2.threshold(circle_region, 200, 255, cv2.THRESH_BINARY)  # Threshold for white pixels

#             # Count white pixels in the thresholded region
#             white_pixels = cv2.countNonZero(thresholded)

#             # Count total pixels in the actual circle region
#             total_pixels = cv2.countNonZero(mask)  # Use mask to count actual circle pixels

#             # Calculate white ratio
#             white_ratio = white_pixels / total_pixels if total_pixels > 0 else 0
            
#             if white_ratio > max_white_ratio:
#                 max_white_ratio = white_ratio
#                 best_circle = circle
        
#         return circles, best_circle
    
#     # Detect golf balls in both halves
#     top_circles, top_best_circle = detect_golfball(top_half, True)
#     bottom_circles, bottom_best_circle = detect_golfball(bottom_half, False)
    
#     # Adjust coordinates for bottom half
#     if bottom_best_circle is not None:
#         bottom_best_circle[1] += height // 2
    
#     # Draw all circles on the original image
#     if top_circles is not None:
#         for circle in top_circles[0, :]:
#             center = (circle[0], circle[1])
#             radius = circle[2]
#             cv2.circle(image, center, radius, (255, 0, 0), 2)  # Blue circle for all detected circles
    
#     if bottom_circles is not None:
#         for circle in bottom_circles[0, :]:
#             center = (circle[0], circle[1] + height // 2)  # Adjust y-coordinate for bottom half
#             radius = circle[2]
#             cv2.circle(image, center, radius, (255, 0, 0), 2)  # Blue circle for all detected circles
    
#     # Highlight the circle with the highest white ratio
#     if top_best_circle is not None:
#         center = (top_best_circle[0], top_best_circle[1])
#         radius = top_best_circle[2]
#         cv2.circle(image, center, radius, (0, 255, 255), 3)  # Yellow circle for the best circle in top
    
#     if bottom_best_circle is not None:
#         center = (bottom_best_circle[0], bottom_best_circle[1])
#         radius = bottom_best_circle[2]
#         cv2.circle(image, center, radius, (0, 255, 255), 3)  # Yellow circle for the best circle in bottom
    
#     # Display the result
#     cv2.imshow("Detected Golf Balls", image)
#     cv2.waitKey(0)  # Wait for a key press
#     cv2.destroyAllWindows()  # Close the window

# # Example usage
# find_golfball("test1.png")



import numpy as np
import json
from collections import deque
import os
import cv2

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

def analyze_impact(frames, motion_threshold=20, save_folder="impact_analyze"):
    """
    Analyze frames to detect ball impact using optical flow and color filtering.
    Args:
        frames (list): List of tuples (timestamp, frame) to analyze.
        motion_threshold (float): Threshold for motion detection using optical flow.
        save_folder (str): Folder to save frames for analysis.

    Returns:
        dict: Impact analysis result containing the ball position and frame.
    """
    print("Impact analysis started")
    print(len(frames), "frames received for analysis")
    # Ensure the save folder exists
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    prev_gray = None
    motion_detected = False
    impact_frame = None
    impact_position = None

    # 초록색 영역과 흰색 공의 HSV 범위 정의
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])

    # Iterate through frames to detect motion
    for i, (frame,timestamp) in enumerate(frames):
        # Save the frame to the impact_analyze folder
        frame_filename = os.path.join(save_folder, f"frame_{i:03d}.jpg")
        print("shape", frame.shape)
        rgba_frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGBA)
        cv2.imwrite(frame_filename, frame)
        # cv2.imshow("frame", frame)

        # Convert frame to grayscale for optical flow
        gray = cv2.cvtColor(rgba_frame, cv2.COLOR_BGR2GRAY)

        if prev_gray is not None:
            # Calculate dense optical flow using Farneback method
            flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])

            # Calculate the average motion in the frame
            avg_motion = np.mean(magnitude)
            print(f"Frame {i}: Average motion = {avg_motion}")

            if avg_motion > motion_threshold:
                print(f"Motion detected in frame {i} with average motion = {avg_motion}")
                motion_detected = True
                impact_frame = frame
                break

        prev_gray = gray

    # Analyze all saved frames for ball detection
    for i, (timestamp, frame) in enumerate(frames):
        # Convert the frame to HSV
        hsv = cv2.cvtColor(rgba_frame, cv2.COLOR_BGR2HSV)

        # Create masks for green and white regions
        mask_green = cv2.inRange(hsv, lower_green, upper_green)
        mask_white = cv2.inRange(hsv, lower_white, upper_white)

        # Combine masks to find white regions within the green area
        mask_non_green = cv2.bitwise_not(mask_green)
        mask_ball = cv2.bitwise_and(mask_white, mask_non_green)

        # Find contours of the ball
        contours, _ = cv2.findContours(mask_ball, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            # Find the largest contour (assumed to be the ball)
            largest_contour = max(contours, key=cv2.contourArea)
            (x, y), radius = cv2.minEnclosingCircle(largest_contour)
            impact_position = (int(x), int(y))
            print(f"Ball detected in frame {i} at position {impact_position} with radius {int(radius)}")
        


    if impact_position is not None:
        return {"source": "impact_analyzer", "impact_position": impact_position, "frame": impact_frame}
    else:
        print("공이 감지되지 않았습니다.")
        return {"source": "impact_analyzer", "impact_position": None, "frame": None}
    

def analyze_optical_flow_in_folder(folder_path, motion_threshold=20):
    # 폴더 내 이미지 파일 리스트 정렬
    image_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.png'))])
    if not image_files:
        print("이미지가 없습니다.")
        return

    prev_gray = None
    for i, fname in enumerate(image_files):
        img_path = os.path.join(folder_path, fname)
        frame = cv2.imread(img_path)
        if frame is None:
            print(f"이미지 읽기 실패: {img_path}")
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_gray is not None:
            # 옵티컬 플로우 계산
            flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            avg_motion = np.mean(magnitude)
            print(f"{fname}: 평균 옵티컬 플로우 = {avg_motion:.2f}")

            # 움직임이 감지되는 시점 출력
            if avg_motion > motion_threshold:
                print(f"==> 움직임 감지! ({fname}) 평균 옵티컬 플로우: {avg_motion:.2f}")

        prev_gray = gray

if __name__ == "__main__":
    folder = "/home/pi/Buddy-Caddy-main/impact_analyze"  # 분석할 이미지 폴더명
    analyze_optical_flow_in_folder(folder, motion_threshold=20)
