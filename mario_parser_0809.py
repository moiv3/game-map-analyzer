import convert_mario_to_jpg
import get_video_info_cv2
import black_threshold_test
import filter_frames
import test_one_frame_detect_0801
import background_movement
import shift_image
import traceback
import os

def mario_parser_function(task_id: str, source: str, video_id: str, game_type: str = "mario"):
    try:
        # main config
        start_time_sec = 0
        capture_per_n_frames = 1
        output_folder = f"output_data/{task_id}"

        if not (source == "S3" or source == "Youtube"):
            return {"error": True, "message": "Not a valid source, source must be 'Youtube' or 'S3'"}
        elif source == "Youtube":
            # Youtube config
            # Super Mario Bros (NES) Level 1-1
            # youtube_id = "-avspZlbOWU"
            # Super Mario Bros (NES) Level 2-1
            # youtube_id = "PI2o0fNKD8g"

            # Starting text
            print("[Main program] Starting...")

            # 1. load video, save as "test_video%Y%m%d%H%M%S.mp4"
            # This works, stop downloading a new video everytime, fix when infer logic ready
            # output_filename = convert_mario_to_jpg.download_youtube(video_id)
            # output_filename = convert_mario_to_jpg.download_youtube_new(video_id, task_id)
            # Short video test: 15 minutes 30s: 5 min
            output_filename = 'test_video20240808153123.mp4'
            # Long video test: 30 fps 60s: 23 min
            # output_filename = 'test_video20240808164421.mp4'

            print("[Main program] Download complete, filename:", output_filename)
            
        # source == "S3"
        else:
            print("[Main program] Starting...")
            print("[Main program] Creating task directories...")
            os.makedirs(f"output_data/{task_id}/map")
            os.makedirs(f"output_data/{task_id}/movement")
            os.makedirs(f"output_data/{task_id}/output_video")
            os.makedirs(f"output_data/{task_id}/source_video")
            os.makedirs(f"output_data/{task_id}/extracted_frames")
            
            output_filename = convert_mario_to_jpg.download_s3(video_id, task_id)
            print("[Main program] Download complete, filename:", output_filename)

        # 2. Get the video data
        video_data = get_video_info_cv2.get_video_info(output_filename)
        end_time_sec = video_data["duration"]        
        total_frames = int(video_data["fps"] * video_data["duration"])
        print("Video data:", video_data)
        print(f"Capturing per {capture_per_n_frames} frames")

        # 3. save to jpgs, get list of captured frames
        extracted_frames_folder = f"output_data/{task_id}/extracted_frames"
        captured_frames, frame_list = convert_mario_to_jpg.extract_frames(output_filename, start_time=start_time_sec, end_time=end_time_sec, interval_frames=capture_per_n_frames, output_folder=extracted_frames_folder)
        # print("[Check black screen] Extract complete, captured frame list:", captured_frames)
        print("[Check black screen] Extract complete")

        # 分歧: mario
        if game_type == "mario":
            # 4. Try to get the starting frame
            dict_to_infer = black_threshold_test.get_image_title_black_game_attr(extracted_frames_folder)

            # Check if is valid video, if not, raise an exception
            count_game_image = sum(1 for v in dict_to_infer.values() if v in ["game", "title", "game_blackbg"])
            total_images = len(dict_to_infer)
            game_image_ratio = count_game_image / total_images
            game_image_ratio_threshold = 0.5
            if game_image_ratio < game_image_ratio_threshold:
                return {"error": True, "message": "Not a valid gameplay video"}
            
            # For debugging
            # with open("color_infer_result.json","w") as fp:
            #     json.dump(dict_to_infer, fp)

            if frame_list:
                first_frame = frame_list[0]
            else:
                first_frame = 0
            starting_frame = black_threshold_test.infer_starting_frame(dict_to_infer, start_frame=first_frame, end_frame=total_frames, capture_per_n_frames=capture_per_n_frames, fps=video_data["fps"])
            print("Starting frame:", starting_frame)
            if starting_frame is False:
                return {"error": True, "message": "No starting frame was found"}

            # 5. Having the starting frame, Drop the frames before starting frame from captured_frames list
            filtered_captured_frames = filter_frames.filter_frames(filenames=captured_frames, threshold=starting_frame)
            print("Actual captured frames to infer:",filtered_captured_frames)
            
            # 6. use the new captured_frames list to do inference
            infer_filepath, infer_result, video_file_path = test_one_frame_detect_0801.infer_and_combine_to_jpg(images=filtered_captured_frames, task_id=task_id, fps=video_data["fps"], output_folder=output_folder)
            print("[Main program] Infer complete, jpg:", infer_filepath)
            # print("[Main program] Infer complete, text:", infer_result)

            motion_result_with_jump_inference = test_one_frame_detect_0801.generate_jump_inference_from_infer_result(infer_result)
            print("[Main program] Jumping motion infer complete, text:", motion_result_with_jump_inference)

            return {"ok": True, "file": infer_filepath, "text": motion_result_with_jump_inference, "video": video_file_path}
        
        elif game_type == "mario_new":
            try:
                infer_filepath, infer_result, video_file_path = test_one_frame_detect_0801.infer_and_combine_to_jpg_sonic(images=captured_frames, task_id=task_id, fps=video_data["fps"], output_folder=output_folder, game="mario")
                frames_folder, frames, movement_x, movement_y = background_movement.get_all_background_movement_from_folder(extracted_frames_folder)
                
                # mario hack: the background movement is always 0. Not working currently!!!!
                # movement_y[:] = [0 for _ in movement_y]
                
                final_map_filepath, final_movement_filepath = shift_image.combine_images(task_id, frames_folder, frames, movement_x, movement_y, infer_result, game=game_type)
                result_text = {}
                result_text["infer"] = infer_result
                result_text["task_id"] = task_id
                result_text["frames"] = frames
                result_text["movement_x"] = movement_x
                result_text["movement_y"] = movement_y

                return {"ok": True, "file": final_map_filepath, "text": result_text, "video": video_file_path, "movement": final_movement_filepath}
            except Exception:
                traceback.print_exc()
                return {"error": True, "message": "Exception occured at mario_parser_function"}
            
        elif game_type == "sonic":
            # 4. Try to get the starting frame

            # Check if is valid video, if not, raise an exception

            # 5. Having the starting frame, Drop the frames before starting frame from captured_frames list
            
            # 6. use the new captured_frames list to do inference
            infer_filename, infer_result, video_file_path = test_one_frame_detect_0801.infer_and_combine_to_jpg_sonic(images=captured_frames, task_id=task_id, fps=video_data["fps"], output_folder=output_folder, game="sonic")
            
            # 7. Background inference New 20240822 version
            extracted_frames_folder = f"output_data/{task_id}/extracted_frames"
            frames_folder, frames, movement_x, movement_y = background_movement.get_all_background_movement_from_folder(extracted_frames_folder)
            final_map_filepath, final_movement_filepath = shift_image.combine_images(task_id, frames_folder, frames, movement_x, movement_y, infer_result, game=game_type)
            result_text = {}
            result_text["infer"] = infer_result
            result_text["task_id"] = task_id
            result_text["frames"] = frames
            result_text["movement_x"] = movement_x
            result_text["movement_y"] = movement_y

            return {"ok": True, "file": final_map_filepath, "text": result_text, "video": video_file_path, "movement": final_movement_filepath}
        
        else:
            return {"error": True, "message": "Not a valid game type!"}
        
    except Exception:
        traceback.print_exc()
        return {"error": True, "message": "An exception happened, check traceback logs"}