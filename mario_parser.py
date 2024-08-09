import convert_mario_to_jpg
import test_one_frame_detect_0801
import traceback

def mario_parser_function(youtube_id):
    try:
        # config
        # Super Mario Bros. - Speedrun level 1 - 1 [370] World Record
        youtube_id = "DGQGvAwqpbE"

        start_time_sec = 4
        end_time_sec = 5
        capture_per_n_frames = 1

        # Starting text
        print("[Main program] Starting...")

        # 1. load video, save as "test_video%Y%m%d%H%M%S.mp4"
        # This works, stop downloading a new video everytime, fix when infer logic ready
        output_filename = convert_mario_to_jpg.download_youtube(youtube_id)
        # output_filename = 'test_video20240801161607.mp4'
        print("[Main program] Download complete, filename:", output_filename)

        # 2. save to jpgs, get list of captured frames
        captured_frames = convert_mario_to_jpg.extract_frames(output_filename, start_time=start_time_sec, end_time=end_time_sec, interval_frames=capture_per_n_frames)
        print("[Main program] Extract complete, captured frame list:", captured_frames)

        # 3. use the list of captured frames to do inference
        infer_filename = test_one_frame_detect_0801.infer_and_combine_to_jpg(captured_frames)
        print("[Main program] Infer complete, result:", infer_filename)
        return {"ok":True, "file":infer_filename}
    except Exception:
        traceback.print_exc()
        return {"error": True}

if __name__ == '__main__':
    mario_parser_function("DGQGvAwqpbE")