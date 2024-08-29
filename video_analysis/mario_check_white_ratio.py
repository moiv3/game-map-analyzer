import cv2
import numpy as np

def check_if_stage_title(image_path, threshold_ratio=0.03, threshold=192, top_percentage=0.3, bottom_percentage=0.4, left_percentage=0.33, right_percentage=0.65):
    # Load the image in grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Determine the height of the top 10% of the image
    height, width = image.shape
    top_height = int(height * top_percentage)
    bottom_height = int(height * bottom_percentage)
    left_width = int(width * left_percentage)
    right_width = int(width * right_percentage)

    # Extract the a specified portion of the image
    top_part = image[top_height:bottom_height, left_width:right_width]

    # Show the image
    # cv2.imshow('image', top_part)
    # cv2.waitKey(0)

    # Count the number of white pixels (above the threshold)
    white_pixels = np.sum(top_part >= threshold)
    
    # Calculate the total number of pixels in the top 10% portion
    total_pixels = top_part.size
    
    # Calculate the ratio of white pixels
    white_ratio = white_pixels / total_pixels
    
    if white_ratio >= threshold_ratio:
        return True
    else:
        return False

def check_if_black_screen(image_path, threshold_ratio=0.02, threshold=10, top_percentage=0.3, bottom_percentage=0.4, left_percentage=0.33, right_percentage=0.65):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    lighter_pixels = np.sum(image > threshold)
    total_pixels = image.size
    ratio = round(lighter_pixels / total_pixels, 3) # 3 decimal places
    # print(ratio)
    if ratio < threshold_ratio:
        return True
    else:
        return False
    

# color_range = ((240, 255), (120, 155), (70, 100))  # Blue, Green, Red ranges for Mario blue background
def check_color_ratio(image_path, color_range, top_percentage=1.0, bottom_percentage=0.4, left_percentage=0.33, right_percentage=0.65):
    image = cv2.imread(image_path)
    height, width, _ = image.shape
    top_height = int(height * top_percentage)

    region = image[:top_height, :]
    
    # Define the lower and upper bounds for the color range
    lower_bound = np.array([color_range[0][0], color_range[1][0], color_range[2][0]], dtype=np.uint8)
    upper_bound = np.array([color_range[0][1], color_range[1][1], color_range[2][1]], dtype=np.uint8)
    
    # Create a mask that identifies the pixels within the color range
    mask = cv2.inRange(region, lower_bound, upper_bound)
    
    # Count the number of pixels that fall within the color range
    color_pixels = np.sum(mask > 0)
    
    # Calculate the total number of pixels in the region
    total_pixels = region.size // 3  # Divide by 3 since it's a color image
    
    # Calculate the ratio of pixels within the color range
    color_ratio = color_pixels / total_pixels
    
    return color_ratio
