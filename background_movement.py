import cv2
import numpy as np
from matplotlib import pyplot as plt

# checks background movement between 2 frames
# takes inputs of curr_frame_path, next_frame_path, returns bg_movement_x, bg_movement_y
def check_background_movement(curr_frame_path, next_frame_path):
    # Config
    # Define the grid size (e.g., 8x8 blocks)
    grid_size = (16, 16)
    # A cell is counted if the predicted bg movement > pixel_count_threshold
    pixel_count_threshold = 2
    # Of all cells, use the nth percentile to predict final br movement values
    n = 90

    # Read the images in grayscale
    img1 = cv2.imread(curr_frame_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(next_frame_path, cv2.IMREAD_GRAYSCALE)

    # Apply Farneback's Optical Flow
    flow = cv2.calcOpticalFlowFarneback(img1, img2, None, 0.5, 3, 15, 3, 5, 1.2, 0)

    # Extract the horizontal (x-axis) and vertical (y-axis) flow
    flow_x = flow[..., 0]  # x-axis movement (horizontal)
    flow_y = flow[..., 1]  # y-axis movement (vertical)


    # Get the height and width of the image
    height, width = flow_x.shape

    # Compute the size of each block
    block_height = height // grid_size[0]
    block_width = width // grid_size[1]

    # Initialize arrays to store the dominant displacement for each block
    grid_displacement_x = np.zeros(grid_size)
    grid_displacement_y = np.zeros(grid_size)

    # Loop through each block and calculate the dominant displacement for x and y separately
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            # Define the block region
            y_start = i * block_height
            y_end = (i + 1) * block_height
            x_start = j * block_width
            x_end = (j + 1) * block_width
            
            # Get the block's optical flow for x and y axes
            block_flow_x = flow_x[y_start:y_end, x_start:x_end]
            block_flow_y = flow_y[y_start:y_end, x_start:x_end]
            
            # Calculate the dominant displacement (median) in this block for x and y axes
            grid_displacement_x[i, j] = np.median(block_flow_x)
            grid_displacement_y[i, j] = np.median(block_flow_y)

    # # Plot the grid-based displacement for the x-axis
    # plt.figure(figsize=(10, 6))
    # plt.imshow(grid_displacement_x, cmap='coolwarm', interpolation='nearest')
    # plt.title('Dominant Displacement (X-Axis) per Grid Block')
    # plt.colorbar(label='X Displacement (pixels)')
    # plt.show()

    # # Plot the grid-based displacement for the y-axis
    # plt.figure(figsize=(10, 6))
    # plt.imshow(grid_displacement_y, cmap='coolwarm', interpolation='nearest')
    # plt.title('Dominant Displacement (Y-Axis) per Grid Block')
    # plt.colorbar(label='Y Displacement (pixels)')
    # plt.show()
    
    if np.count_nonzero(grid_displacement_x > pixel_count_threshold) > np.count_nonzero(grid_displacement_x < -pixel_count_threshold):
        # 正x比較多，應該用第90th percentile
        percentile_x = n
    elif np.count_nonzero(grid_displacement_x > pixel_count_threshold) < np.count_nonzero(grid_displacement_x < -pixel_count_threshold):
        # 負x比較多，應該用第10th percentile
        percentile_x = 100 - n
    else:
        # 一樣多，應該用第50th percentile
        percentile_x = 50

    if np.count_nonzero(grid_displacement_y > pixel_count_threshold) > np.count_nonzero(grid_displacement_y < -pixel_count_threshold):
        percentile_y = n
    elif np.count_nonzero(grid_displacement_y > pixel_count_threshold) < np.count_nonzero(grid_displacement_y < -pixel_count_threshold):
        percentile_y = 100 - n
    else:
        percentile_y = 50

    bg_movement_x = np.percentile(grid_displacement_x, percentile_x)
    bg_movement_y = np.percentile(grid_displacement_y, percentile_y)
    # print(f"{n}th percentile: x:{bg_movement_x:.1f}, y:{bg_movement_y:.1f}")

    return bg_movement_x, bg_movement_y


if __name__ == "__main__":
    for i in range(1, 12):
        curr_frame = f"sonic_test_0820/frame_{i:02}.jpg"
        next_frame = f"sonic_test_0820/frame_{i+1:02}.jpg"
        print(curr_frame)
        check_background_movement(curr_frame, next_frame)