import cv2
import numpy as np

# Load the two images
# char_img = cv2.imread('sonic.png', cv2.IMREAD_UNCHANGED)

def put_character_on_bg(background_img, char_img, x_center, y_center):
    char_y = char_img.shape[0]
    char_x = char_img.shape[1]
    x_offset = x_center - round(char_x / 2)
    y_offset = y_center - round(char_y / 2)
    # Check if char_img has an alpha channel
    if char_img.shape[2] == 4:
        # Split the channels
        b, g, r, a = cv2.split(char_img)

        # Create a mask from the alpha channel
        mask = a.astype(bool)

        # Calculate the region where char_img will be placed
        y1, y2 = y_offset, y_offset + char_img.shape[0]
        x1, x2 = x_offset, x_offset + char_img.shape[1]

        # Ensure the coordinates don't go out of bounds of background_img
        if y2 > background_img.shape[0]:
            y2 = background_img.shape[0]
            char_img = char_img[:y2 - y_offset, :, :]
            mask = mask[:y2 - y_offset, :]

        if x2 > background_img.shape[1]:
            x2 = background_img.shape[1]
            char_img = char_img[:, :x2 - x_offset, :]
            mask = mask[:, :x2 - x_offset]

        # Overlay char_img onto background_img using the mask
        for c in range(0, 3):
            background_img[y1:y2, x1:x2, c][mask] = char_img[:, :, c][mask]

        return background_img
    
    else:
        print("char_img does not have an alpha channel.")
        return None