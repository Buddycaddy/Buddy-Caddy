from picamera2 import Picamera2
import cv2
import time

# Initialize two Picamera2 instances for two cameras
picam1 = Picamera2(0)  # First camera
picam2 = Picamera2(1)  # Second camera

# List available sensor modes for first camera
print("Available sensor modes for Camera 1:")
sensor_modes = picam1.sensor_modes
for mode in sensor_modes:
    print(mode)

# Select desired sensor mode (1332x990 at 120 fps) for first camera
desired_mode = None
for mode in sensor_modes:
    if mode['size'] == (1332, 990) and mode['fps'] >= 120:
        desired_mode = mode
        break

if desired_mode is None:
    raise Exception("Desired sensor mode (1332x990 at 120 fps) not found for Camera 1")

# Shared main configuration for both cameras (640x480 output for picam2)
main_config = {
    "format": "RGB888",
    "size": (640, 480),
    "stride": 0,
    "preserve_ar": False
}

# Create video configuration for first camera with specific sensor mode
config1 = picam1.create_video_configuration(
    main={"format": "RGB888", "size": (1332, 990)},  # Keep full sensor resolution
    controls={"FrameRate": 120},
    sensor={
        "output_size": desired_mode['size'],
        "bit_depth": desired_mode['bit_depth']
    }
)

# Create video configuration for second camera with auto-selected mode
config2 = picam2.create_video_configuration(
    main=main_config,
    controls={"FrameRate": 120}  # Attempt 120 fps, defaults to max if unsupported
)

# Configure and start both cameras
picam1.configure(config1)
picam2.configure(config2)
picam1.start()
picam2.start()

frame_count1 = 0
start_time = time.time()
while True:
    
    frame1 = picam1.capture_array()
    frame_count1 += 1
    frame2 = picam2.capture_array()

    # Crop Camera 1
    frame1_cropped = frame1[0:480, 0:640]

    # Crop Camera 2
    height, width = 480, 640  
    crop_height, crop_width = 240, 320
    start_y = (height - crop_height) // 2  # Center vertically (120)
    start_x = (width - crop_width) // 2  # Center horizontally (160)
    frame2_cropped = frame2[start_y:start_y + crop_height, start_x:start_x + crop_width]

    # Display cropped frames in separate windows
    cv2.imshow("Camera 1", frame1_cropped)
    cv2.imshow("Camera 2", frame2_cropped)

    # Print FPS for Camera 1 every second
    if time.time() - start_time >= 1.0:
        print(f"Camera 1 FPS: {frame_count1}")
        frame_count1 = 0
        start_time = time.time()

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cv2.destroyAllWindows()
picam1.stop()
picam2.stop()