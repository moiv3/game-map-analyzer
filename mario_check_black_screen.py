import convert_mario_to_jpg
import get_video_info_cv2
import black_threshold_test
import pprint
import csv
import test_one_frame_detect_0801
import traceback

def mario_check_black_screen_function(youtube_id = "PI2o0fNKD8g"):
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


        # Starting text
        print("[Check black screen] Starting...")

        # 1. load video, save as "test_video%Y%m%d%H%M%S.mp4"
        # This works, stop downloading a new video everytime, fix when infer logic ready
        output_filename = convert_mario_to_jpg.download_youtube(youtube_id)
        # output_filename = 'test_video20240801161607.mp4'
        print("[Check black screen] Download complete, filename:", output_filename)

        # 2. Get the video data
        video_data = get_video_info_cv2.get_video_info(output_filename)
        end_time_sec = video_data["duration"]
        capture_per_n_frames = round(video_data["fps"] * capture_per_n_secs)
        print("Video data:", video_data)
        print(f"Capturing per {capture_per_n_frames} frames")

        # 3. save to jpgs, get list of captured frames
        captured_frames = convert_mario_to_jpg.extract_frames(output_filename, start_time=start_time_sec, end_time=end_time_sec, interval_frames=capture_per_n_frames)
        # print("[Check black screen] Extract complete, captured frame list:", captured_frames)
        print("[Check black screen] Extract complete")
        
        # 4. get black values of every captured frame
        black_values = black_threshold_test.get_image_black_values(folder_path)
        print("[Check black screen] Black values check complete")
        # pprint.pprint(black_values)

        # 5. Save to a CSV file
        with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:  
            writer = csv.writer(csv_file)
            for key, value in black_values.items():
                writer.writerow([key, value])
        print("[Check black screen] Write to csv complete")

        # # 3. use the list of captured frames to do inference
        # infer_filename = test_one_frame_detect_0801.infer_and_combine_to_jpg(captured_frames)
        # print("[Check black screen] Infer complete, result:", infer_filename)
        return {"ok":True, "file": output_csv}
    except Exception:
        traceback.print_exc()
        return {"error": True}

if __name__ == '__main__':
    mario_check_black_screen_function("rQEVS5DIgN8")