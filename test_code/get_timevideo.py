import cv2
import logging

logging.basicConfig(level=logging.DEBUG, filename="debug.log", filemode="a")

def get_video_duration(video_path):
    """
    Calculate the duration of a video file in seconds.
    
    Args:
        video_path (str): Path to the video file.
    
    Returns:
        float: Duration of the video in seconds, or None if the video cannot be opened.
    """
    try:
        # Open the video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logging.error(f"Failed to open video file: {video_path}")
            return None
        
        # Get the frame count and FPS
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Release the video capture object
        cap.release()
        
        if fps > 0:
            duration = frame_count / fps  # Calculate duration in seconds
            logging.info(f"Video duration for {video_path}: {duration:.2f} seconds")
            return duration
        else:
            logging.error(f"Failed to retrieve FPS for {video_path}")
            return None
    
    except Exception as e:
        logging.error(f"Error getting video duration for {video_path}: {str(e)}")
        return None

if __name__ == "__main__":
    # Example usage
    video_path = "./resource/segment_2.mp4"  # Path to the video file
    duration = get_video_duration(video_path)
    if duration is not None:
        print(f"Video duration: {duration:.2f} seconds")
    else:
        print("Failed to retrieve video duration")