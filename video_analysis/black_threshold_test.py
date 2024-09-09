import cv2
import numpy as np
import os
import video_analysis.mario_check_white_ratio as mario_check_white_ratio
import json

# threshold: This value (ranging from 0 to 255) determines what pixel values are considered "non-black."
# For example, if threshold is set to 10, any pixel with a value greater than 10 will be counted as a "non-black" pixel.
def check_black_image_with_threshold(image_path, threshold=10, ratio_threshold=0.01):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    lighter_pixels = np.sum(image > threshold)
    total_pixels = image.size
    ratio = round(lighter_pixels / total_pixels, 3)
    print(image_path, ratio)
    return ratio

    if ratio < ratio_threshold:
        return True
    else:
        return False

def get_image_black_values(folder_path):
    image_black_values = {}
    
    # Iterate over all files in the directory
    for filename in os.listdir(folder_path):
        if filename.endswith('.jpg'):
            # Construct full file path
            file_path = os.path.join(folder_path, filename)
            
            black_ratio = check_black_image_with_threshold(file_path)
            image_black_values[filename] = black_ratio

    return image_black_values

def get_image_title_black_game_attr(folder_path, game):
    image_black_values = {}
    
    # Iterate over all files in the directory
    for filename in os.listdir(folder_path):
        if filename.endswith('.jpg'):
            # Construct full file path
            file_path = os.path.join(folder_path, filename)
            
            #TODO: 這些function開開關關，應該要整併為一個
            title_screen_have_words = mario_check_white_ratio.check_if_stage_title(file_path)
            title_screen_black_enough = mario_check_white_ratio.check_if_black_screen(file_path, threshold_ratio=0.05)
            is_black_screen = mario_check_white_ratio.check_if_black_screen(file_path)
            is_blue_game_background = bool(mario_check_white_ratio.check_color_ratio(file_path,((240, 255), (120, 155), (60, 120))) > 0.5)
            is_black_game_background = bool(mario_check_white_ratio.check_color_ratio(file_path,((0, 16), (0, 16), (0, 16))) > 0.75)
            is_sonic_start_end_screen = bool(mario_check_white_ratio.check_color_ratio(file_path,((245, 255), (17, 32), (0, 10))) > 0.6)

            if title_screen_have_words and title_screen_black_enough:
                image_black_values[filename] = "title"
            elif is_black_screen:
                image_black_values[filename] = "black"
            elif is_blue_game_background:
                image_black_values[filename] = "game"
            elif is_black_game_background:
                image_black_values[filename] = "game_blackbg"
            elif is_sonic_start_end_screen and game == "sonic":
                image_black_values[filename] = "sonic_startend"
            else:
                image_black_values[filename] = "other"


    print("[black_threshold_test.get_image_title_black_game_attr] image_black_values:")
    print(image_black_values)

    return image_black_values

def get_image_title_black_game_attr_filelist_input(files):
    image_black_values = {}
    
    for filename in files:
        title_screen_have_words = mario_check_white_ratio.check_if_stage_title(filename)
        title_screen_black_enough = mario_check_white_ratio.check_if_black_screen(filename, threshold_ratio=0.05)
        is_black_screen = mario_check_white_ratio.check_if_black_screen(filename)

        filename_without_path = filename[-14:]

        if title_screen_have_words and title_screen_black_enough:
            image_black_values[filename_without_path] = "title"
        elif is_black_screen:
            image_black_values[filename_without_path] = "black"
        else:
            image_black_values[filename_without_path] = "game"

    print(image_black_values)

    return image_black_values

def infer_starting_frame(dict_to_infer, start_frame: int, end_frame: int, capture_per_n_frames: int, fps: float):

    threshold_frames = round(fps * 8 / 30)

    if start_frame < 0 or start_frame >= 10000 or end_frame < 0 or end_frame >= 10000:
        print("[infer_starting_frame] frame number not supported yet")
        return False
    else:
        for frame_number in range(int((end_frame - start_frame) / capture_per_n_frames) - threshold_frames * 3):

            real_frame_number = start_frame + frame_number * capture_per_n_frames + threshold_frames * 3
            title_count = 0
            black_count = 0
            game_count = 0

            number_of_pics_to_check = round(threshold_frames / capture_per_n_frames)

            for i in range(number_of_pics_to_check):
                # check first third
                if dict_to_infer[f"frame_{(start_frame + (frame_number + i) * capture_per_n_frames):04d}.jpg"] == "title":
                    title_count += 1
                # check second third
                if dict_to_infer[f"frame_{(start_frame + (threshold_frames * 1 + frame_number + i) * capture_per_n_frames):04d}.jpg"] == "black":
                    black_count += 1
                # check last third
                if dict_to_infer[f"frame_{(start_frame + (threshold_frames * 2 + frame_number + i) * capture_per_n_frames):04d}.jpg"] == "game" or dict_to_infer[f"frame_{(start_frame + (threshold_frames * 2 + frame_number + i) * capture_per_n_frames):04d}.jpg"] == "gameblack":
                    game_count += 1
            
            if title_count >= max((threshold_frames * 0.7, 2)) and black_count >= max((threshold_frames * 0.4, 2)) and game_count >= max((threshold_frames * 0.7, 2)):
                starting_frame = start_frame + frame_number + threshold_frames * 2 + 1
                print("GOT STARTING FRAME! Frame", starting_frame)
                return starting_frame
            print(f"{frame_number} {title_count} {black_count} {game_count}")
    
    print("[infer_starting_frame] Did not find a starting frame, will return 0")
    return 0

# dict_to_infer = get_image_title_black_game_attr("output_test_0808")
# starting_frame = infer_starting_frame(dict_to_infer, start_frame=0, end_frame=1566)

# for i in range(26):
#     print (check_black_image_with_threshold("frame_54.jpg", threshold=10*i, ratio_threshold=0.00005))
#     print (check_black_image_with_threshold("frame_56.jpg", threshold=10*i, ratio_threshold=0.00005))
#     print (check_black_image_with_threshold("frame_164.jpg", threshold=10*i, ratio_threshold=0.00005))

# Test results - Conclusion: threshold=10 + ratio_threshold=0.01 seems good.
# frame_54.jpg: Stage screen
# frame_56.jpg: pure black
# frame_164.jpg: pure blue

# threshold=0
# frame_54.jpg 0.053287037037037036
# False
# frame_56.jpg 0.00028356481481481483
# False
# frame_164.jpg 1.0
# False

# threshold=10
# frame_54.jpg 0.029988425925925925
# False
# frame_56.jpg 0.0
# True
# frame_164.jpg 1.0
# False

# threshold=20
# frame_54.jpg 0.028182870370370372
# False
# frame_56.jpg 0.0
# True
# frame_164.jpg 1.0
# False