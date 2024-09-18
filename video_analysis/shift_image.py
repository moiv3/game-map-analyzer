import cv2
import numpy as np
import traceback
import video_analysis.stack_transparent_image as stack_transparent_image
from matplotlib import pyplot as plt

def read_image(image_file, gray_scale=False):
    image_src = cv2.imread(image_file)
    if gray_scale is True:
        image_src = cv2.cvtColor(image_src, cv2.COLOR_BGR2GRAY)
    else:
        pass
        # image_src = cv2.cvtColor(image_src, cv2.COLOR_BGR2RGB)
    return image_src

def pad_vector(vector, how, depth, constant_value=255):
    vect_shape = vector.shape[:2]
    if (how == 'upper') or (how == 'top'):
        pp = np.full(shape=(depth, vect_shape[1]), fill_value=constant_value)
        pv = np.vstack(tup=(pp, vector))
    elif (how == 'lower') or (how == 'bottom'):
        pp = np.full(shape=(depth, vect_shape[1]), fill_value=constant_value)
        pv = np.vstack(tup=(vector, pp))
    elif (how == 'left'):
        pp = np.full(shape=(vect_shape[0], depth), fill_value=constant_value)
        pv = np.hstack(tup=(pp, vector))
    elif (how == 'right'):
        pp = np.full(shape=(vect_shape[0], depth), fill_value=constant_value)
        pv = np.hstack(tup=(vector, pp))
    else:
        return vector
    return pv

def shifter(vect, y, y_):
    if (y > 0):
        image_trans = pad_vector(vector=vect, how='lower', depth=y_)
    elif (y < 0):
        image_trans = pad_vector(vector=vect, how='upper', depth=y_)
    else:
        image_trans = vect
    return image_trans

def shift_image(image_src, at):
    x, y = at
    x_, y_ = abs(x), abs(y)

    if (x > 0):
        left_pad = pad_vector(vector=image_src, how='left', depth=x_)
        image_trans = shifter(vect=left_pad, y=y, y_=y_)
    elif (x < 0):
        right_pad = pad_vector(vector=image_src, how='right', depth=x_)
        image_trans = shifter(vect=right_pad, y=y, y_=y_)
    else:
        image_trans = shifter(vect=image_src, y=y, y_=y_)

    return image_trans

def translate_image(image_file, at, with_plot=False, gray_scale=False):
    if len(at) != 2:
        return False

    image_src = read_image(image_file=image_file, gray_scale=gray_scale)


    if not gray_scale:
        r_image, g_image, b_image = image_src[:, :, 0], image_src[:, :, 1], image_src[:, :, 2]
        r_trans = shift_image(image_src=r_image, at=at)
        g_trans = shift_image(image_src=g_image, at=at)
        b_trans = shift_image(image_src=b_image, at=at)
        # 原本的code, 不太正確
        image_trans = np.dstack(tup=(r_trans, g_trans, b_trans))
        # image_trans = np.dstack(tup=(b_trans, g_trans, r_trans))
    else:
        image_trans = shift_image(image_src=image_src, at=at)

    # Ensure the translated image is also uint8
    image_trans = image_trans.astype(np.uint8)

    # cv2.imshow("A",image_src)
    # cv2.waitKey()
    # cv2.imshow("B",image_trans)
    # cv2.waitKey()
    print (image_trans.shape)

    if with_plot:
        cmap_val = None if not gray_scale else 'gray'
        fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(10, 20))

        ax1.axis("off")
        ax1.title.set_text('Original')

        ax2.axis("off")
        ax2.title.set_text("Translated")

        ax1.imshow(image_src, cmap=cmap_val)
        ax2.imshow(image_trans, cmap=cmap_val)        

        return True
    return image_trans

def combine_translated_images(image1, image2, at):

    image2_raw = read_image(image2)
    height, width, _ = image2_raw.shape
    at_x = at[0]
    at_y = at[1]
    image1_trans = translate_image(image_file=image1, at=(at_x, -at_y))

    cv2.imshow("A",image1_trans)
    cv2.waitKey()
    if at_x >= 0:
        trans_x = 0
    else:
        trans_x = -at_x

    if at_y >= 0:
        trans_y = 0
    else:
        trans_y = -at_y

    
    image1_trans[trans_y:trans_y+height, trans_x:trans_x+width] = image2_raw
    cv2.imshow("B", image1_trans)
    cv2.waitKey()
    return image1_trans

def translate_image_for_img_objects(image_src, at, with_plot=False, gray_scale=False):
    if len(at) != 2:
        return False

    if not gray_scale:
        r_image, g_image, b_image = image_src[:, :, 0], image_src[:, :, 1], image_src[:, :, 2]
        r_trans = shift_image(image_src=r_image, at=at)
        g_trans = shift_image(image_src=g_image, at=at)
        b_trans = shift_image(image_src=b_image, at=at)
        # 原本的code, 不太正確
        image_trans = np.dstack(tup=(r_trans, g_trans, b_trans))
        # image_trans = np.dstack(tup=(b_trans, g_trans, r_trans))
    else:
        image_trans = shift_image(image_src=image_src, at=at)

    # Ensure the translated image is also uint8
    image_trans = image_trans.astype(np.uint8)

    # cv2.imshow("A",image_src)
    # cv2.waitKey()
    # cv2.imshow("B",image_trans)
    # cv2.waitKey()
    print (image_trans.shape)

    if with_plot:
        cmap_val = None if not gray_scale else 'gray'
        fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(10, 20))

        ax1.axis("off")
        ax1.title.set_text('Original')

        ax2.axis("off")
        ax2.title.set_text("Translated")

        ax1.imshow(image_src, cmap=cmap_val)
        ax2.imshow(image_trans, cmap=cmap_val)        

        return True
    return image_trans

def combine_translated_images_for_img_objects(image1_obj, image2_obj, at):

    height, width, _ = image2_obj.shape
    at_x = at[0]
    at_y = at[1]
    image1_trans = translate_image_for_img_objects(image_src=image1_obj, at=(at_x, -at_y))

    cv2.imshow("A",image1_trans)
    cv2.waitKey()
    if at_x >= 0:
        trans_x = 0
    else:
        trans_x = -at_x

    if at_y >= 0:
        trans_y = 0
    else:
        trans_y = -at_y

    
    image1_trans[trans_y:trans_y+height, trans_x:trans_x+width] = image2_obj
    cv2.imshow("B", image1_trans)
    cv2.waitKey()
    return image1_trans

def combine_images(task_id, frames_folder, images, movement_x, movement_y, all_image_result, game=None):
    try:
        print(movement_x)
        print(movement_y)

        # test movement_y for mario
        if game == "mario_new":
            movement_y[:] = [0 for _ in movement_y]
        else:
            pass

        image0 = cv2.imread(f"{frames_folder}/{images[0]}")
        height, width, _ = image0.shape

        curr_x_left = 0
        curr_x_right = width
        curr_y_top = 0
        curr_y_bottom = height

        min_x_left = 0
        max_x_right = width
        min_y_top = 0
        max_y_bottom = height

        curr_position_list = []
        for i in range(len(images)):
            curr_x_left -= movement_x[i]
            curr_x_right -= movement_x[i]
            curr_y_top -= movement_y[i]
            curr_y_bottom -= movement_y[i]
            curr_position_list.append((curr_x_left, curr_x_right, curr_y_top, curr_y_bottom))
            
            min_x_left = min(curr_x_left, min_x_left)
            max_x_right = max(curr_x_right, max_x_right)
            min_y_top = min(curr_y_top, min_y_top)
            max_y_bottom = max(curr_y_bottom, max_y_bottom)

        print(min_x_left, max_x_right, min_y_top, max_y_bottom)
        print(curr_position_list)

        final_size_x = max_x_right - min_x_left
        final_size_y = max_y_bottom - min_y_top
        print(final_size_x, final_size_y)
        # black background
        # final_img = np.zeros([final_size_y,final_size_x, 3], dtype=np.uint8)
        # white background
        final_img = np.full([final_size_y,final_size_x, 3],255, dtype=np.uint8)

        for i in range(len(images)):
            image = cv2.imread(f"{frames_folder}/{images[i]}")
            # print(f"appending image # {i}/{len(images)}")

            if game == "sonic":
                # the left 18% of the screen has text on it, so crop it
                left_crop = round(width * 0.18)
                image = image[:,left_crop:]
                # this line below fails, fix
                # final_img = final_img[:,:-left_crop]
                final_img[curr_position_list[i][2]-min_y_top:curr_position_list[i][3]-min_y_top, curr_position_list[i][0]-min_x_left:curr_position_list[i][1]-min_x_left-left_crop] = image
            elif game == "mario_new":
                left_crop = 0
                final_img[curr_position_list[i][2]-min_y_top:curr_position_list[i][3]-min_y_top, curr_position_list[i][0]-min_x_left:curr_position_list[i][1]-min_x_left] = image
            else:
                left_crop = 0
                final_img[curr_position_list[i][2]-min_y_top:curr_position_list[i][3]-min_y_top, curr_position_list[i][0]-min_x_left:curr_position_list[i][1]-min_x_left] = image
        
        final_map_filepath = f"output_data/{task_id}/map/map_{task_id}.jpg"
        cv2.imwrite(final_map_filepath, final_img)
        print(f"Combine success! Written result to file: {final_map_filepath}")

        # paste sonic/mario to the map
        print(f"Pasting {game} to the map...")

        # read and resize
        if game == "sonic":
            char_img = cv2.imread('video_analysis/sonic.png', cv2.IMREAD_UNCHANGED)
            # constants for sonic character
            char_height_on_map = round(77 / 480 * height)
            char_width_on_map = round(57 / 480 * height)
            char_img = cv2.resize(char_img, (char_width_on_map, char_height_on_map))
        elif game == "mario_new":
            char_img = cv2.imread('video_analysis/mario.png', cv2.IMREAD_UNCHANGED)
            # constants for mario character
            char_height_on_map = round(36 / 540 * height)
            char_width_on_map = round(27 / 540 * height)
            char_img = cv2.resize(char_img, (char_width_on_map, char_height_on_map))
        else:
            pass

        if game == "sonic" or game == "mario_new":
            print(game)
            for i in range(len(all_image_result)):
                if "sonic_position_x" in all_image_result[i] and "sonic_position_y" in all_image_result[i]:
                    x_center = round(all_image_result[i]["sonic_position_x"]) - 1
                    y_center = round(all_image_result[i]["sonic_position_y"]) - 1
                    final_img = stack_transparent_image.put_character_on_bg(background_img=final_img,
                                                                            char_img=char_img,
                                                                            x_center=x_center+curr_position_list[i][0]-min_x_left-left_crop,
                                                                            y_center=y_center+curr_position_list[i][2]-min_y_top)
                else:
                    pass
        
        final_movement_filepath = f"output_data/{task_id}/movement/movement_{task_id}.jpg"
        cv2.imwrite(final_movement_filepath, final_img)
        print(f"Combine success! Written result to file: {final_movement_filepath}")
        return final_map_filepath, final_movement_filepath
    
    except Exception as e:
        traceback.print_exc()
        print(f"Failed to combine images: {e}")
        return None, None