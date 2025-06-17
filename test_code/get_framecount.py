import cv2
import logging

logging.basicConfig(level=logging.DEBUG, filename="debug.log", filemode="a")

def get_frame_count(video_path):
    """
    Calculate the total number of frames in a video file.
    
    Args:
        video_path (str): Path to the video file.
    
    Returns:
        int: Total number of frames in the video, or None if the video cannot be opened.
    """
    try:
        # Open the video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logging.error(f"Failed to open video file: {video_path}")
            return None
        
        # Get the frame count
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Release the video capture object
        cap.release()
        
        logging.info(f"Total frames in {video_path}: {frame_count}")
        return frame_count
    
    except Exception as e:
        logging.error(f"Error getting frame count for {video_path}: {str(e)}")
        return None

if __name__ == "__main__":
    # Example usage
    video_path = "./resource/test2.mp4"  # Same video path as used in impact_analyzer.py
    frame_count = get_frame_count(video_path)
    if frame_count is not None:
        print(f"Total number of frames: {frame_count}")
    else:
        print("Failed to retrieve frame count")