import cv2
import numpy as np
import supervision as sv
from ultralytics import YOLO
from math import sqrt
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
def infer_and_combine_to_jpg(images, output_filename = "output.jpg"):
    # init processed_frames
    processed_frames = []
    # init this_pos, last_pos
    last_pos={}
    this_pos={}
    # init clear detection
    clear_detection = 0

    # unpack image width, define border detection. min border = 5px for small pics
    first_image = cv2.imread(images[0])
    ud_height, lr_width, _ = first_image.shape
    # min border = 5px for small pics
    lr_margin = max(int(lr_width * lr_margin_ratio), 5)
    print("Image width:", lr_width, ", border judge:", lr_margin, "px")
    print("image.shape", first_image.shape)

    for single_image in images:
        print("Reading image:", single_image)
        image = cv2.imread(single_image)
        results = model(image, conf=0.7)[0]
        detections = sv.Detections.from_ultralytics(results)

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
                processed_frames.append(cropped_frame)
            elif crop_pixels_max > 1:
                cropped_frame = crop_image(image, 0, 0, crop_pixels_max, ud_height)
                processed_frames.append(cropped_frame)

        else:
            print("No marker_classes gave a crop_pixel count. This frame is not cropped.")

        # check flagpole and castle
        if "cl" in detections.data["class_name"] and "castle" in detections.data["class_name"]:
            clear_detection += 1

        if clear_detection >= 20:
            print("Clear detection triggered, appending this frame")
            cropped_frame = crop_image(image, 0, 0, lr_width, ud_height)
            processed_frames.append(cropped_frame)
            break

        # TODO: check underground
        # 1st: check if consecutive black for 5 frames. use black_threshold_test.check_black_image_with_threshold
        # 2nd: Toggle underground mode.
        # 3rd: Assume only one screen in underground (Fix this later)
        # 4th:尋找新的定位點
        # 5th:先試著用影像辨識，然後如果不行，
        # 6th: 畫三條線(最上面三個block)分析亮度，猜出移動了多少

    if processed_frames:
        combined_image = np.hstack(processed_frames)
        cv2.imwrite(output_filename, combined_image)

        print("Inference complete. Combined image saved to:", output_filename)
        return output_filename
    else:
        print("No frames were captured from the video.")
        return False




    




