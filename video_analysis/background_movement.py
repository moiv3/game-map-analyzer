import cv2
import numpy as np
import os
import video_analysis.shift_image as shift_image
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

def align_images(images):
    # Convert the first image to grayscale and use it as the reference
    ref_img = cv2.imread(images[0])
    ref_img_gray = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)

    aligned_images = [ref_img]  # Start with the reference image

    for i in range(1, len(images)):
        # Load the next image and convert it to grayscale
        img_path = images[i]
        img = cv2.imread(img_path)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Calculate optical flow between the reference image and the current image
        flow = cv2.calcOpticalFlowFarneback(ref_img_gray, img_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)

        # Calculate the median flow along x and y axes
        median_flow_x = np.median(flow[..., 0])
        median_flow_y = np.median(flow[..., 1])

        # Shift the current image to align it with the reference image
        rows, cols = img.shape[:2]
        transformation_matrix = np.float32([[1, 0, -median_flow_x], [0, 1, -median_flow_y]])

        # Warp the current image based on the flow
        aligned_img = cv2.warpAffine(img, transformation_matrix, (cols, rows))

        # Append the aligned image to the list
        aligned_images.append(aligned_img)

    return aligned_images

def stack_images_old(aligned_images):
    # Initialize the result with the first image
    stacked_image = aligned_images[0].astype(np.float32)

    # Add and blend subsequent images
    for i in range(1, len(aligned_images)):
        stacked_image = cv2.addWeighted(stacked_image, (i / (i + 1)), aligned_images[i].astype(np.float32), (1 / (i + 1)), 0)

    # Convert the stacked image back to uint8 format
    stacked_image = stacked_image.astype(np.uint8)

    return stacked_image

def stack_images_without_blending(aligned_images):
    # Start with the first image
    stacked_image = aligned_images[0].copy()

    # Place each subsequent image on top of the previous image
    for i in range(1, len(aligned_images)):
        # Mask to determine where to paste the new image
        mask = np.any(aligned_images[i] > 0, axis=-1)  # Assuming non-black pixels indicate content
        
        # Place the new image on top of the stacked image, preserving the underlying image
        stacked_image[mask] = aligned_images[i][mask]

    return stacked_image

import cv2
import numpy as np

def calculate_shift_and_align(reference_img, image):
    # Convert images to grayscale for optical flow
    ref_img_gray = cv2.cvtColor(reference_img, cv2.COLOR_BGR2GRAY)
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate optical flow to determine the background movement
    flow = cv2.calcOpticalFlowFarneback(ref_img_gray, img_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)

    # Calculate the median flow along x and y axes (background movement)
    median_flow_x = np.median(flow[..., 0])
    median_flow_y = np.median(flow[..., 1])

    # Calculate the reverse of the background movement
    shift_x = -median_flow_x
    shift_y = -median_flow_y

    # Shift the image based on the reverse movement
    rows, cols = image.shape[:2]
    transformation_matrix = np.float32([[1, 0, shift_x], [0, 1, shift_y]])

    # Apply the transformation to align the image with the reference image's background
    aligned_image = cv2.warpAffine(image, transformation_matrix, (cols, rows))

    return aligned_image

def stack_images(images):
    # Use the first image as the reference image
    reference_img = cv2.imread(images[0])
    stacked_image = reference_img.copy()

    # Align and stack each subsequent image on top of the reference image
    for i in range(1, len(images)):
        # Load the current image
        image = cv2.imread(images[i])

        # Align the image with the reference image
        aligned_image = calculate_shift_and_align(reference_img, image)

        # Stack the aligned image on top of the current stacked image
        mask = np.any(aligned_image > 0, axis=-1)  # Assuming non-black pixels indicate content
        stacked_image[mask] = aligned_image[mask]

    return stacked_image

def get_all_background_movement_from_folder(folder):
    frames = []
    movement_x = []
    movement_y = []
    files = os.listdir(folder)
    sorted_files=sorted(files, key=lambda x: int(x.split('frame_')[1].split('.')[0]))
    for frame_num in range(len(sorted_files)-1):
        curr_frame_path = f"{folder}/{sorted_files[frame_num]}"
        next_frame_path = f"{folder}/{sorted_files[frame_num+1]}"
        bg_movement_x, bg_movement_y = check_background_movement(curr_frame_path, next_frame_path)
        frames.append(sorted_files[frame_num])
        movement_x.append(round(bg_movement_x))
        movement_y.append(round(bg_movement_y))
        print(f"{frame_num} / {len(sorted_files)-1} frames analyzed.")
    print("Finished analysis.")
    return folder, frames, movement_x, movement_y

if __name__ == "__main__":
    task_id, frames, movement_x, movement_y = get_all_background_movement_from_folder("7529efda-1910-47e7-8e29-ec10d055d20e")
    final_img = shift_image.combine_images(task_id, frames, movement_x, movement_y, game="sonic")
#     print(image_paths)
#     # Example usage:
#     # List of image paths
#     # image_paths = ['frame1.jpg', 'frame2.jpg', 'frame3.jpg', ..., 'frameN.jpg']

#     # Align the images
#     aligned_images = align_images(image_paths)

#     # Stack the aligned images
#     stacked_result = stack_images_without_blending(aligned_images)

#     # Display the final stacked image
#     cv2.imshow('Stacked Image', stacked_result)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

#     # Optionally, save the result

