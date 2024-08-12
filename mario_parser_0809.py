import convert_mario_to_jpg
import get_video_info_cv2
import black_threshold_test
import pprint
import csv
import filter_frames
import test_one_frame_detect_0801
import traceback

def mario_parser_function(task_id, youtube_id = "PI2o0fNKD8g"):
    try:
        # config
        # Super Mario Bros (NES) Level 1-1
        # youtube_id = "-avspZlbOWU"
        # Super Mario Bros (NES) Level 2-1
        # youtube_id = "PI2o0fNKD8g"

        start_time_sec = 0
        # end_time_sec = 5
        capture_per_n_secs = 0.05
        folder_path = "output_test_0808"
        output_csv = "output_test_0808_1-4.csv"
        output_folder = task_id

        # Starting text
        print("[Main program] Starting...")

        # 1. load video, save as "test_video%Y%m%d%H%M%S.mp4"
        # This works, stop downloading a new video everytime, fix when infer logic ready
        # output_filename = convert_mario_to_jpg.download_youtube(youtube_id)
        output_filename = 'test_video20240808153123.mp4'
        print("[Main program] Download complete, filename:", output_filename)

        # 2. Get the video data
        #TODO: 包成一個function
        video_data = get_video_info_cv2.get_video_info(output_filename)
        end_time_sec = video_data["duration"]
        # end_time_sec = 11
        # capture_per_n_frames = round(video_data["fps"] * capture_per_n_secs)
        
        capture_per_n_frames = 1
        total_frames = int(video_data["fps"] * video_data["duration"])
        print("Video data:", video_data)
        print(f"Capturing per {capture_per_n_frames} frames")

        # 3. save to jpgs, get list of captured frames
        captured_frames, frame_list = convert_mario_to_jpg.extract_frames(output_filename, start_time=start_time_sec, end_time=end_time_sec, interval_frames=capture_per_n_frames, output_folder = output_folder)
        # print("[Check black screen] Extract complete, captured frame list:", captured_frames)
        print("[Check black screen] Extract complete")

        # 4. Try to get the starting frame
        dict_to_infer = black_threshold_test.get_image_title_black_game_attr(output_folder)
        if frame_list:
            first_frame = frame_list[0]
        else:
            first_frame = 0
        starting_frame = black_threshold_test.infer_starting_frame(dict_to_infer, start_frame=first_frame, end_frame=total_frames, capture_per_n_frames=capture_per_n_frames, fps=video_data["fps"])
        print("Starting frame:", starting_frame)

        # 5. Having the starting frame, Drop the frames before starting frame from captured_frames list
        filtered_captured_frames = filter_frames.filter_frames(filenames=captured_frames, threshold=starting_frame)
        print("Actual captured frames to infer:",filtered_captured_frames)
        
        # 6. use the new captured_frames list to do inference
        infer_filename = test_one_frame_detect_0801.infer_and_combine_to_jpg(images=filtered_captured_frames, task_id=task_id, fps=video_data["fps"], output_filename = f"{task_id}.jpg")
        print("[Main program] Infer complete, result:", infer_filename)
        return {"ok": True, "file": infer_filename}
    
    except Exception:
        traceback.print_exc()
        return {"error": True}

if __name__ == '__main__':
    mario_parser_function("DGQGvAwqpbE")