import cv2
import numpy as np
import supervision as sv
from ultralytics import YOLO
import black_threshold_test
from math import sqrt
import traceback

# Config 
# Training Model
model = YOLO("./training_data/20240801mariov2/best.pt")
# ratio of image to 視為邊界
lr_margin_ratio = 0.005

# 今天的目標是讓這個program可以處理一整個影帶


# Function to crop the image
def crop_image(image, x, y, width, height):
    return image[y:y+height, x:x+width]

# main function, "images" is a list of image filenames
def infer_and_combine_to_jpg(images, task_id, fps, output_filename = "output.jpg"):
    # init total infer result
    all_image_result = []
    # init processed_frames
    processed_frames = []
    # init this_pos, last_pos
    last_pos={}
    this_pos={}
    # init clear detection
    clear_detection = 0
    # clear detection starts counting only if 15 seconds has passed (first_frame + fps * 15 seconds)
    first_frame = int(images[0].split('frame_')[1].split('.')[0])
    clear_detection_starting_frame = int(first_frame + fps * 15)

    # unpack image width, define border detection. min border = 5px for small pics
    first_image = cv2.imread(images[0])
    ud_height, lr_width, _ = first_image.shape
    # min border = 5px for small pics
    lr_margin = max(int(lr_width * lr_margin_ratio), 5)
    print("Image width:", lr_width, ", border judge:", lr_margin, "px")
    print("image.shape", first_image.shape)

    # Define the codec and create VideoWriter object for output video
    output_video_path = f"video_{task_id}.mp4"
    output_video = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (lr_width, ud_height))

    for single_image in images:
        print("Reading image:", single_image)
        image = cv2.imread(single_image)
        results = model(image, conf=0.7)[0]
        detections = sv.Detections.from_ultralytics(results)

        # append infer result as dict
        single_image_dict={}
        single_image_dict["filename"] = single_image
        num_part = int(single_image.split('frame_')[1].split('.')[0])
        single_image_dict["frame_number"] = num_part
        single_image_dict["detections"] = detections
        all_image_result.append(single_image_dict)


        print("Detection Data:")
        print(detections.data)

        # next: get the delta of clouds and mario and crop the image for that many pixels
        marker_classes = ['cl','ghill']
        last_pos = this_pos
        this_pos = {}

        for i in range(len(detections.data["class_name"])):
            class_of_object = detections.data["class_name"][i]
            if class_of_object in marker_classes:
                if class_of_object not in this_pos:
                    this_pos[class_of_object]=[]
                    this_pos[class_of_object].append(detections.xyxy[i])
                else:
                    this_pos[class_of_object].append(detections.xyxy[i])

        print("last_pos", last_pos)
        print("this_pos", this_pos)

        crop_pixels = {}
        for marker_class in marker_classes:             
            print("Dealing with marker class:", marker_class)

            if marker_class not in last_pos or marker_class not in this_pos:
                print("Marker class not detected in last or this pos")
            elif marker_class in last_pos and marker_class in this_pos:
                print("last pos for this marker class:", last_pos[marker_class])
                print("this pos for this marker class:", this_pos[marker_class])

                # change cloud to marker
                distance_cloud_AB_to_CD = []
                for cloud in this_pos[marker_class]:
                    distance_cloud_A_to_CD = []
                    for last_cloud in last_pos[marker_class]:
                        distance_cloud_A_to_C = []

                        # lr_margin and lr_width are calculated above
                        if cloud[0] < lr_margin or cloud[0] > lr_width - lr_margin or \
                            last_cloud[0] < lr_margin or last_cloud[0] > lr_width - lr_margin:
                            print("margin detected, not appending")
                        else:
                            distance_ul = sqrt((cloud[0]-last_cloud[0]) ** 2 + (cloud[1]-last_cloud[1]) ** 2)
                            distance_cloud_A_to_C.append(distance_ul)

                        if cloud[2] < lr_margin or cloud[2] > lr_width - lr_margin or \
                            last_cloud[2] < lr_margin or last_cloud[2] > lr_width - lr_margin:
                            print("margin detected, not appending")
                        else:
                            distance_dr = sqrt((cloud[2]-last_cloud[2]) ** 2 + (cloud[3]-last_cloud[3]) ** 2)
                            distance_cloud_A_to_C.append(distance_dr)
                        
                        print("distance_cloud_A_to_C is:")
                        print(distance_cloud_A_to_C)

                        if not distance_cloud_A_to_C:
                            print("no distance were appended")
                        elif len(distance_cloud_A_to_C) == 1:
                            print("only one distance")
                            distance_cloud_A_to_CD.append(distance_cloud_A_to_C[0])

                        elif len(distance_cloud_A_to_C) == 2 and abs(distance_cloud_A_to_C[0] - distance_cloud_A_to_C[1]) <= 3:
                            print("two distance and match, getting average")
                            distance_cloud_A_to_CD.append((distance_cloud_A_to_C[0] + distance_cloud_A_to_C[1]) / 2)
                        else:
                            print("two distance and mismatch, getting minimum")
                            distance_cloud_A_to_CD.append(min(distance_cloud_A_to_C[0], distance_cloud_A_to_C[1]))
                        # 可能要處理關於雲消失(從由邊或左邊)的部分
                        # 如果端點太左或太右，則不append
                    if distance_cloud_A_to_CD:
                        print("min distance of cloud & last_cloud:", min(distance_cloud_A_to_CD))
                        distance_cloud_AB_to_CD.append(min(distance_cloud_A_to_CD))
                print(distance_cloud_AB_to_CD)
                if distance_cloud_AB_to_CD:
                    print("min distance of all, should crop this many pixels", int(min(distance_cloud_AB_to_CD)))
                    crop_pixels[marker_class] = round(min(distance_cloud_AB_to_CD))
                else:
                    print("no marker classes detected, using value 0 for this class")
                    crop_pixels[marker_class] = 0

        print("All marker_classes analyzed. Crop pixel check:", crop_pixels)

        if crop_pixels:
            # # Average way
            # crop_pixels_total = 0
            # for item in crop_pixels:
            #     crop_pixels_total += crop_pixels[item]
            # crop_pixels_avg = round(crop_pixels_total / len(crop_pixels))

            # print("Average crop pixel check:", crop_pixels_avg)
            # # crop the pixels and save to np array
            # if crop_pixels_avg >= 1:
            #     cropped_frame = crop_image(image, 0, 0, crop_pixels_avg, ud_height)
            #     processed_frames.append(cropped_frame)

            # Max way
            crop_pixels_max = sorted(crop_pixels.values(), reverse=True)[0]
            print("Max crop pixel check:", crop_pixels_max)
            # crop the pixels and save to np array
            if crop_pixels_max > 50:
                print("Anomaly detected, getting second largest value if exists")
                if len(crop_pixels.values()) >= 2:
                    crop_pixels_max = sorted(crop_pixels.values(), reverse=True)[1]
                print("New value:",crop_pixels_max)
                cropped_frame = crop_image(image, 0, 0, crop_pixels_max, ud_height)
                cropped_frame_deep_copy = np.copy(cropped_frame)
                processed_frames.append(cropped_frame_deep_copy)
                # processed_frames.append(cropped_frame)
            elif crop_pixels_max > 1:
                cropped_frame = crop_image(image, 0, 0, crop_pixels_max, ud_height)
                cropped_frame_deep_copy = np.copy(cropped_frame)
                processed_frames.append(cropped_frame_deep_copy)
                # processed_frames.append(cropped_frame)
                

        else:
            print("No marker_classes gave a crop_pixel count. This frame is not cropped.")

        # check flagpole and castle
        if "cl" in detections.data["class_name"] and "castle" in detections.data["class_name"] and num_part >= clear_detection_starting_frame:
            clear_detection += 1

        if clear_detection >= 20:
            print("Clear detection triggered, appending this frame")
            cropped_frame = crop_image(image, 0, 0, lr_width, ud_height)
            cropped_frame_deep_copy = np.copy(cropped_frame)
            processed_frames.append(cropped_frame_deep_copy)
            # processed_frames.append(cropped_frame)
            break

        # draw a bounding box, then save to somewhere
        for result in results:
            for bbox in result.boxes:
                x1, y1, x2, y2 = bbox.xyxy[0].int().tolist()
                confidence = bbox.conf[0]
                label = model.names[int(bbox.cls[0])]
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(image, f"{label} {confidence:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Write the frame with the boxes to the output video
        output_video.write(image)

        # TODO: check underground
        # 1st: check if consecutive black for 5 frames. use black_threshold_test.check_black_image_with_threshold
        # 2nd: Toggle underground mode.
        # 3rd: Assume only one screen in underground (Fix this later)
        # 4th: 尋找新的定位點
        # 5th: 先試著用影像辨識，然後如果不行，
        # 6th: 畫三條線(最上面三個block)分析亮度，猜出移動了多少
    output_video.release()

    if processed_frames:
        combined_image = np.hstack(processed_frames)
        cv2.imwrite(output_filename, combined_image)

        print("Inference complete. Combined image saved to:", output_filename)
        return output_filename, all_image_result
    else:
        print("No frames were captured from the video.")
        return None, None
        



# main function, "images" is a list of image filenames
# Detection Data:
# {'class_name': array(['cl', 'cl', 'gpatch', 'ghill'], dtype='<U6')}
# last_pos {'cl': [array([     121.66,      69.864,      185.24,      109.06], dtype=float32), array([     452.55,      47.609,         480,      84.418], dtype=float32)], 'ghill': [array([     348.31,      280.23,      438.99,      313.07], dtype=float32)]}
# this_pos {'cl': [array([     121.66,      69.882,      185.26,      109.06], dtype=float32), array([     452.56,      48.038,         480,        84.6], dtype=float32)], 'ghill': [array([     348.37,      280.23,      438.99,      313.08], dtype=float32)]}
# def calculate_movement_of_class(marker_class_list, detection_data_last_frame, detection_data_this_frame):
def calculate_movement_of_class(marker_class, detection_data_last_frame, detection_data_this_frame, margin_detection=True, lr_width=720, lr_margin=5):

    # init processed_frames
    processed_frames = []
    # init this_pos, last_pos
    last_pos={}
    this_pos={}
    # init clear detection
    clear_detection = 0

    #=====================0810==================
    # 只看mario
    # next: get the delta of clouds and mario and crop the image for that many pixels
    last_pos = {}
    this_pos = {}

    for i in range(len(detection_data_last_frame.data["class_name"])):
        class_of_object = detection_data_last_frame.data["class_name"][i]
        if class_of_object == marker_class:
            if class_of_object not in last_pos:
                last_pos[class_of_object]=[]
                last_pos[class_of_object].append(detection_data_last_frame.xyxy[i])
            else:
                last_pos[class_of_object].append(detection_data_last_frame.xyxy[i])

    for i in range(len(detection_data_this_frame.data["class_name"])):
        class_of_object = detection_data_this_frame.data["class_name"][i]
        if class_of_object == marker_class:
            if class_of_object not in this_pos:
                this_pos[class_of_object]=[]
                this_pos[class_of_object].append(detection_data_this_frame.xyxy[i])
            else:
                this_pos[class_of_object].append(detection_data_this_frame.xyxy[i])

    print("last_pos", last_pos)
    print("this_pos", this_pos)



    print("Dealing with marker class:", marker_class)

    if marker_class not in last_pos or marker_class not in this_pos:
        print("Marker class not detected in last or this pos")
        return None
    elif marker_class in last_pos and marker_class in this_pos:
        print("last pos for this marker class:", last_pos[marker_class])
        print("this pos for this marker class:", this_pos[marker_class])
        
        # change cloud to marker
        distance_cloud_AB_to_CD = []
        for cloud in this_pos[marker_class]:
            distance_cloud_A_to_CD = []
            for last_cloud in last_pos[marker_class]:
                distance_cloud_A_to_C = []

                if margin_detection == True:
                    # lr_margin and lr_width are calculated above
                    if cloud[0] < lr_margin or cloud[0] > lr_width - lr_margin or \
                        last_cloud[0] < lr_margin or last_cloud[0] > lr_width - lr_margin:
                        print("margin detected, not appending")
                    else:
                        distance_ul = sqrt((cloud[0]-last_cloud[0]) ** 2 + (cloud[1]-last_cloud[1]) ** 2)
                        distance_cloud_A_to_C.append(distance_ul)

                    if cloud[2] < lr_margin or cloud[2] > lr_width - lr_margin or \
                        last_cloud[2] < lr_margin or last_cloud[2] > lr_width - lr_margin:
                        print("margin detected, not appending")
                    else:
                        distance_dr = sqrt((cloud[2]-last_cloud[2]) ** 2 + (cloud[3]-last_cloud[3]) ** 2)
                        distance_cloud_A_to_C.append(distance_dr)

                else:
                    distance_ul = sqrt((cloud[0]-last_cloud[0]) ** 2 + (cloud[1]-last_cloud[1]) ** 2)
                    distance_cloud_A_to_C.append(distance_ul)

                    distance_dr = sqrt((cloud[2]-last_cloud[2]) ** 2 + (cloud[3]-last_cloud[3]) ** 2)
                    distance_cloud_A_to_C.append(distance_dr)
                    
                    print("The dist of cloud is:", distance_cloud_A_to_C)

                    if not distance_cloud_A_to_C:
                        print("no distance were appended")
                    elif len(distance_cloud_A_to_C) == 1:
                        print("only one distance")
                        distance_cloud_A_to_CD.append(distance_cloud_A_to_C[0])

                    elif len(distance_cloud_A_to_C) == 2 and abs(distance_cloud_A_to_C[0] - distance_cloud_A_to_C[1]) <= 3:
                        print("two distance and match, getting average")
                        distance_cloud_A_to_CD.append((distance_cloud_A_to_C[0] + distance_cloud_A_to_C[1]) / 2)
                    else:
                        print("two distance and mismatch, getting minimum")
                        distance_cloud_A_to_CD.append(min(distance_cloud_A_to_C[0], distance_cloud_A_to_C[1]))
                    # 可能要處理關於雲消失(從由邊或左邊)的部分
                    # 如果端點太左或太右，則不append
                if distance_cloud_A_to_CD:
                    print("min distance of cloud & last_cloud:", min(distance_cloud_A_to_CD))
                    distance_cloud_AB_to_CD.append(min(distance_cloud_A_to_CD))
            print(distance_cloud_AB_to_CD)
            if distance_cloud_AB_to_CD:
                print("min distance of all, should crop this many pixels", int(min(distance_cloud_AB_to_CD)))
                marker_movement = round(min(distance_cloud_AB_to_CD))
            else:
                print("no marker classes detected, using value 0 for this class")
                marker_movement = 0

        print("All marker_classes analyzed. marker_movement check:", marker_movement)
        return marker_movement
    
def calculate_movement_of_mario(detection_data_last_frame, detection_data_this_frame, marker_class='sm', margin_detection=True, lr_width=720, lr_margin=5):

    #=====================0810==================
    # 只看mario
    # next: get the delta of clouds and mario and crop the image for that many pixels
    print("\n", "Comparing last frame:",detection_data_last_frame["frame_number"], "this frame:", detection_data_this_frame["frame_number"])
    last_pos = {}
    this_pos = {}

    for i in range(len(detection_data_last_frame["detections"].data["class_name"])):
        class_of_object = detection_data_last_frame["detections"].data["class_name"][i]
        if class_of_object == marker_class:
            if class_of_object not in last_pos:
                last_pos[class_of_object]=[]
                last_pos[class_of_object].append(detection_data_last_frame["detections"].xyxy[i])
            else:
                last_pos[class_of_object].append(detection_data_last_frame["detections"].xyxy[i])

    for i in range(len(detection_data_this_frame["detections"].data["class_name"])):
        class_of_object = detection_data_this_frame["detections"].data["class_name"][i]
        if class_of_object == marker_class:
            if class_of_object not in this_pos:
                this_pos[class_of_object]=[]
                this_pos[class_of_object].append(detection_data_this_frame["detections"].xyxy[i])
            else:
                this_pos[class_of_object].append(detection_data_this_frame["detections"].xyxy[i])

    print("last_pos", last_pos)
    print("this_pos", this_pos)



    print("Dealing with marker class:", marker_class)

    if marker_class not in last_pos or marker_class not in this_pos:
        print("Marker class not detected in last or this pos")
        return None
        # main program will return with another frame
    elif marker_class in last_pos and marker_class in this_pos:
        print("last pos for this marker class:", last_pos[marker_class])
        print("this pos for this marker class:", this_pos[marker_class])
        
        # change cloud to marker
        distance_cloud_AB_to_CD = []
        for cloud in this_pos[marker_class]:
            distance_cloud_A_to_CD = []
            for last_cloud in last_pos[marker_class]:
                distance_cloud_A_to_C = []

                # Mario case, margin detection is always false
                # But need to handle x and y axes
                # Let's just assume there is only one mario
                distance_dict = {}
                distance_dict["x"] = cloud[0]-last_cloud[0]
                distance_dict["y"] = cloud[1]-last_cloud[1]
                distance_ul = sqrt((cloud[0]-last_cloud[0]) ** 2 + (cloud[1]-last_cloud[1]) ** 2)
                distance_dict["rms"] = distance_ul
                distance_cloud_A_to_C.append(distance_dict)
            
                distance_dict = {}
                distance_dict["x"] = cloud[2]-last_cloud[2]
                distance_dict["y"] = cloud[3]-last_cloud[3]
                distance_dr = sqrt((cloud[2]-last_cloud[2]) ** 2 + (cloud[3]-last_cloud[3]) ** 2)
                distance_dict["rms"] = distance_dr
                distance_cloud_A_to_C.append(distance_dict)
                
                print("The dist of mario is:", distance_cloud_A_to_C)

                if not distance_cloud_A_to_C:
                    print("no distance were appended")
                elif len(distance_cloud_A_to_C) == 1:
                    print("only one distance")
                    distance_cloud_A_to_CD.append(distance_cloud_A_to_C[0])
                else:
                    print("two distance and mismatch, getting minimum")
                    min_rms_dict_A_to_C = min(distance_cloud_A_to_C, key=lambda d: d["rms"])
                    distance_cloud_A_to_CD.append(min_rms_dict_A_to_C)
                # 可能要處理關於雲消失(從由邊或左邊)的部分
                # 如果端點太左或太右，則不append
            if distance_cloud_A_to_CD:
                min_rms_dict_A_to_CD = min(distance_cloud_A_to_CD, key=lambda d: d["rms"])
                print("min distance of cloud & last_cloud:", min_rms_dict_A_to_CD)                    
                distance_cloud_AB_to_CD.append(min_rms_dict_A_to_CD)
        print(distance_cloud_AB_to_CD)
        if distance_cloud_AB_to_CD:
            min_rms_dict_AB_to_CD = min(distance_cloud_AB_to_CD, key=lambda d: d["rms"])
            print("min distance of all:", min_rms_dict_AB_to_CD)
            marker_movement = min_rms_dict_AB_to_CD
        else:
            print("no marker classes detected, using value 0 for this class")
            marker_movement = None

    print("All marker_classes analyzed. marker_movement check:", marker_movement)
    return marker_movement

    
def infer_start(images = None, folder_path = None):
    if images and folder_path:
        print("Only one of (images or folder_name) should be specified. Returning None")
        return None
    elif not (images or folder_path):
        print("No images or folder_name specified!!! Returning None")
        return None
    elif folder_path:
        images = []
        import os
        for filename in os.listdir(folder_path):
            if filename.endswith('.jpg'):
                # Construct full file path
                file_path = os.path.join(folder_path, filename)
                images.append(file_path)

    dict_to_infer = black_threshold_test.get_image_title_black_game_attr_filelist_input(images)
    print(dict_to_infer)
    starting_frame = black_threshold_test.infer_starting_frame(dict_to_infer, start_frame=0, end_frame=200) # fix start_frame and end_frame
    print("Starting frame:", starting_frame)
    return starting_frame


def infer_images(images, output_filename = "inference_result.csv", save_to_csvfile=False):   
    all_image_result = []

    try:
        for single_image in images:
            print("Reading image:", single_image)
            single_image_dict={}
            single_image_dict["filename"] = single_image

            num_part = int(single_image.split('frame_')[1].split('.')[0])
            single_image_dict["frame_number"] = num_part

            image = cv2.imread(single_image)
            results = model(image, conf=0.7)[0]
            detections = sv.Detections.from_ultralytics(results)
            single_image_dict["detections"] = detections
            all_image_result.append(single_image_dict)

        if save_to_csvfile:
            np.save("npy_test", all_image_result)
            np.savetxt(output_filename, all_image_result, delimiter=',', newline='\n', fmt='%s')
            print("Result saved to csv file", output_filename)

        return all_image_result
    
    except Exception:
        print("An exception occured:")
        traceback.print_exc()
        return None

def get_first_and_last_frame(infer_result):
    sorted_frames = sorted(infer_result, key=lambda x: x['frame_number'])
    first_frame = sorted_frames[0]['frame_number']
    last_frame = sorted_frames[-1]['frame_number']
    return first_frame, last_frame

def calculate_motion(infer_result):
    sorted_frames = sorted(infer_result, key=lambda x: x['frame_number'])
    frames_to_compare = len(sorted_frames) - 1

    total_motion_result = []
    for i in range(frames_to_compare):
        frame_motion_result = {}
        frame_motion_result["frame_number"] = sorted_frames[i]["frame_number"]
        mario_movement_of_frame = calculate_movement_of_mario(detection_data_last_frame=sorted_frames[i],
                                                              detection_data_this_frame=sorted_frames[i+1],
                                                              marker_class='sm', margin_detection=False, lr_width=720, lr_margin=5)
        frame_motion_result["movement"] = mario_movement_of_frame
        total_motion_result.append(frame_motion_result)

    return total_motion_result

# pretty primitive algo, think how to do better
def infer_jumping(motion_result):
    sorted_frames = sorted(motion_result, key=lambda x: x['frame_number'])
    for i in range(len(sorted_frames)):
        if not sorted_frames[i]["movement"]:
            pass
        elif sorted_frames[i]["movement"]["y"] < -5: # 10 is arbitary selected
            sorted_frames[i]["movement"]["jump"] = "jump"
        elif sorted_frames[i]["movement"]["y"] > 10: # -30 is arbitary selected
            sorted_frames[i]["movement"]["jump"] = "fall"
        else:
            sorted_frames[i]["movement"]["jump"] = None

    return sorted_frames

def infer_jumping_and_landing(motion_result_with_jumping):
    jumping_and_landing_result = []
    sorted_frames = sorted(motion_result_with_jumping, key=lambda x: x['frame_number'])
    for i in range(len(sorted_frames)-1):
        # print("Analyzing frame:", i)
        if not(sorted_frames[i]["movement"] and sorted_frames[i+1]["movement"]):
            pass
        elif sorted_frames[i]["movement"]["jump"] == None and sorted_frames[i+1]["movement"]["jump"] == "jump":            
            print("movement None => jump detected at frame:", i)
            # start tracking for 15 frames
            for j in range(15):
                print(i+j, sorted_frames[i+j]["movement"], sorted_frames[i+j+1]["movement"])
                if (i+j+1) <= len(sorted_frames) and sorted_frames[i+j]["movement"] and sorted_frames[i+j+1]["movement"] and sorted_frames[i+j]["movement"]["jump"] == "fall" and sorted_frames[i+j+1]["movement"]["jump"] == None:
                    print("Found a jump ending at:", i+j+1)
                    jump_info = {"jump":i, "land":i+j+1}
                    jumping_and_landing_result.append(jump_info)
                    break

    if jumping_and_landing_result:
        return jumping_and_landing_result
    else:
        return None
    
def generate_jump_inference_from_infer_result(infer_result):
    motion_result = calculate_motion(infer_result)
    print(motion_result)
    motion_result_with_jump = infer_jumping(motion_result)
    print(motion_result_with_jump)
    motion_result_with_jump_inference = infer_jumping_and_landing(motion_result_with_jump)
    print(motion_result_with_jump_inference)
    first_frame,last_frame = get_first_and_last_frame(infer_result)
    print("first_frame, last_frame:", first_frame, last_frame)
    
    output = {}
    output["first_frame"] = first_frame
    output["last_frame"] = last_frame
    output["jump"] = motion_result_with_jump_inference

    return output

if __name__ == "__main__":
    images=[]
    for i in range(522):
        images.append(f"output_test_0809/frame_{i:04d}.jpg")

    infer_start(images)
    import sys
    sys.exit()
    # images=["output_test_0809/frame_0121.jpg",
    #         "output_test_0809/frame_0122.jpg",
    #         "output_test_0809/frame_0123.jpg",
    #         "output_test_0809/frame_0124.jpg",
    #         "output_test_0809/frame_0125.jpg",
    #         ]
    print(images)
    # infer_result = infer_images(images, save_to_csvfile=True)
    infer_result = np.load("npy_test.npy", allow_pickle=True)
    motion_result = calculate_motion(infer_result)
    print(motion_result)
    motion_result_with_jump = infer_jumping(motion_result)
    print(motion_result_with_jump)
    motion_result_with_jump_inference = infer_jumping_and_landing(motion_result_with_jump)
    print(motion_result_with_jump_inference)
    # np.savetxt(fname="infer_result_0811.csv", X=motion_result_with_jump, delimiter=',', newline='\n', fmt='%s')
    # # Sort the list by 'frame_number', in case it is not
    # sorted_frames = sorted(infer_result, key=lambda x: x['frame_number'])
    # frames_to_compare = len(sorted_frames) - 1
    # for i in range(frames_to_compare):
    #     print(calculate_movement_of_mario(detection_data_last_frame=sorted_frames[i],
    #                                       detection_data_this_frame=sorted_frames[i+1],
    #                                       marker_class='sm', margin_detection=False, lr_width=720, lr_margin=5))
        