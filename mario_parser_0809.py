import convert_mario_to_jpg
import get_video_info_cv2
import black_threshold_test
import pprint
import csv
import json
import filter_frames
import test_one_frame_detect_0801
import traceback

def mario_parser_function(task_id: str, source: str, video_id: str):
    try:
        # main config
        start_time_sec = 0
        capture_per_n_frames = 1
        output_folder = task_id

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
            output_filename = convert_mario_to_jpg.download_s3(video_id, task_id)
            print("[Main program] Download complete, filename:", output_filename)

        # 2. Get the video data
        #TODO: 包成一個function
        video_data = get_video_info_cv2.get_video_info(output_filename)
        end_time_sec = video_data["duration"]
        # end_time_sec = 11
        # capture_per_n_frames = round(video_data["fps"] * capture_per_n_secs)
        
        
        total_frames = int(video_data["fps"] * video_data["duration"])
        print("Video data:", video_data)
        print(f"Capturing per {capture_per_n_frames} frames")

        # 3. save to jpgs, get list of captured frames
        captured_frames, frame_list = convert_mario_to_jpg.extract_frames(output_filename, start_time=start_time_sec, end_time=end_time_sec, interval_frames=capture_per_n_frames, output_folder = output_folder)
        # print("[Check black screen] Extract complete, captured frame list:", captured_frames)
        print("[Check black screen] Extract complete")

        # 4. Try to get the starting frame
        dict_to_infer = black_threshold_test.get_image_title_black_game_attr(output_folder)

        # Check if is valid video, if not, raise an exception
        count_game_image = sum(1 for v in dict_to_infer.values() if v in ["game", "title"])
        total_images = len(dict_to_infer)
        game_image_ratio = count_game_image / total_images
        game_image_ratio_threshold = 0.5
        if game_image_ratio < game_image_ratio_threshold:
            return {"error": True, "message": "Not a valid gameplay video"}
        
        # For debugging
        with open("color_infer_result.json","w") as fp:
            json.dump(dict_to_infer, fp)

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
        infer_filename, infer_result = test_one_frame_detect_0801.infer_and_combine_to_jpg(images=filtered_captured_frames, task_id=task_id, fps=video_data["fps"], output_filename = f"{task_id}.jpg")
        print("[Main program] Infer complete, jpg:", infer_filename)
        # print("[Main program] Infer complete, text:", infer_result)

        motion_result_with_jump_inference = test_one_frame_detect_0801.generate_jump_inference_from_infer_result(infer_result)
        print("[Main program] Jumping motion infer complete, text:", motion_result_with_jump_inference)

        return {"ok": True, "file": infer_filename, "text": motion_result_with_jump_inference}
    
    except Exception:
        traceback.print_exc()
        return {"error": True, "message": "An exception happened, check traceback logs"}

if __name__ == '__main__':
    mario_parser_function("DGQGvAwqpbE")