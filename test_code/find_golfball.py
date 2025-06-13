import cv2
import numpy as np

def find_golfball(image_path):
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found at {image_path}")
    
    # Get image dimensions
    height, width, _ = image.shape
    
    # Split the image horizontally into two halves (top and bottom)
    top_half = image[:height // 2, :]
    bottom_half = image[height // 2:, :]
    
    # Function to detect golf ball in a given region
    def detect_golfball(region, is_top_half):
        # Convert to grayscale
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (15, 15), 0)
        
        # Apply Canny edge detection
        edges = cv2.Canny(blurred, 40, 110, apertureSize=3)
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        edges = cv2.erode(edges, kernel, iterations=1)
        
        # Detect circles using HoughCircles
        circles = cv2.HoughCircles(
            edges, 
            cv2.HOUGH_GRADIENT, 
            dp=1.0, 
            minDist=30, 
            param1=100, 
            param2=10, 
            minRadius=5, 
            maxRadius=10
        )
        
        if circles is None:
            return None, None
        
        # Find the circle with the highest white pixel ratio
        circles = np.uint16(np.around(circles))
        max_white_ratio = 0
        best_circle = None
        
        for circle in circles[0, :]:
            center = (circle[0], circle[1])
            radius = circle[2]
            
            # Create a mask for the circle
            mask = np.zeros_like(gray)
            cv2.circle(mask, center, radius, 255, -1)
            
            # Calculate white pixel ratio
            circle_region = cv2.bitwise_and(gray, gray, mask=mask)

            # Apply threshold to isolate white pixels
            _, thresholded = cv2.threshold(circle_region, 200, 255, cv2.THRESH_BINARY)  # Threshold for white pixels

            # Count white pixels in the thresholded region
            white_pixels = cv2.countNonZero(thresholded)

            # Count total pixels in the actual circle region
            total_pixels = cv2.countNonZero(mask)  # Use mask to count actual circle pixels

            # Calculate white ratio
            white_ratio = white_pixels / total_pixels if total_pixels > 0 else 0
            
            if white_ratio > max_white_ratio:
                max_white_ratio = white_ratio
                best_circle = circle
        
        return circles, best_circle
    
    # Detect golf balls in both halves
    top_circles, top_best_circle = detect_golfball(top_half, True)
    bottom_circles, bottom_best_circle = detect_golfball(bottom_half, False)
    
    # Adjust coordinates for bottom half
    if bottom_best_circle is not None:
        bottom_best_circle[1] += height // 2
    
    # Draw all circles on the original image
    if top_circles is not None:
        for circle in top_circles[0, :]:
            center = (circle[0], circle[1])
            radius = circle[2]
            cv2.circle(image, center, radius, (255, 0, 0), 2)  # Blue circle for all detected circles
    
    if bottom_circles is not None:
        for circle in bottom_circles[0, :]:
            center = (circle[0], circle[1] + height // 2)  # Adjust y-coordinate for bottom half
            radius = circle[2]
            cv2.circle(image, center, radius, (255, 0, 0), 2)  # Blue circle for all detected circles
    
    # Highlight the circle with the highest white ratio
    if top_best_circle is not None:
        center = (top_best_circle[0], top_best_circle[1])
        radius = top_best_circle[2]
        cv2.circle(image, center, radius, (0, 255, 255), 3)  # Yellow circle for the best circle in top
    
    if bottom_best_circle is not None:
        center = (bottom_best_circle[0], bottom_best_circle[1])
        radius = bottom_best_circle[2]
        cv2.circle(image, center, radius, (0, 255, 255), 3)  # Yellow circle for the best circle in bottom
    
    # Display the result
    cv2.imshow("Detected Golf Balls", image)
    cv2.waitKey(0)  # Wait for a key press
    cv2.destroyAllWindows()  # Close the window

# Example usage
find_golfball("test1.png")