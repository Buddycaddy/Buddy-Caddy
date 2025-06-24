from picamera2 import Picamera2
import cv2
import time

# Initialize two Picamera2 instances for two cameras
picam1 = Picamera2(0)  # First camera

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
    main={"format": "RGB888", "size": (640, 480)},  # Keep full sensor resolution
    controls={"FrameRate": 120},
    sensor={
        "output_size": desired_mode['size'],
        "bit_depth": desired_mode['bit_depth']
    }
)


# Configure and start both cameras
picam1.configure(config1)
picam1.start()

frame_count1 = 0
start_time = time.time()
while True:
    
    frame1 = picam1.capture_array()
    print("프레임 캡쳐 시작")
    frame_count1 += 1


    # Display cropped frames in separate windows
    cv2.imshow("Camera 1", frame1)


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
