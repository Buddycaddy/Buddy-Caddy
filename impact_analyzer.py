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
