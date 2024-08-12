from pytube import YouTube
from datetime import datetime
import cv2
import numpy as np
import os

# pytube temp fix
from pytube.innertube import _default_clients

_default_clients[ "ANDROID"][ "context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients[ "ANDROID_EMBED"][ "context"][ "client"]["clientVersion"] = "19.08.35"
_default_clients[ "IOS_EMBED"][ "context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_MUSIC"][ "context"]["client"]["clientVersion"] = "6.41"
_default_clients[ "ANDROID_MUSIC"] = _default_clients[ "ANDROID_CREATOR" ]

# Helper functions

# Function to invert colors
def invert_colors(frame):
    return cv2.bitwise_not(frame)

# Function to crop the image
def crop_image(image, x, y, width, height):
    return image[y:y+height, x:x+width]

# Main functions

# Download desired YouTube video URL
def download_youtube(youtube_id: str):
    video_url = 'https://www.youtube.com/watch?v=' + youtube_id

    yt = YouTube(video_url)
    stream = yt.streams.filter(file_extension='mp4').first()
    now = datetime.now()
    # Format the datetime as a string in the desired format
    output_filename = now.strftime("test_video%Y%m%d%H%M%S.mp4")
    stream.download(filename=output_filename)

    return output_filename

# Extract frames from the video using OpenCV, saves to own folder with filename "frame_xxx.jpg"
def extract_frames(filename: str, start_time, end_time, interval_frames, output_folder):
    # Video capture setup
    input_video_path = filename
    cap = cv2.VideoCapture(input_video_path)

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = interval_frames  # Interval to capture frames (every 0.5 seconds)

    # Initialize variables
    result = []
    frame_count = 0
    frame_list = []

    # Create folder if not exist
    output_folder_path = output_folder
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Capture frame at specified interval then save image
        # TODO: fix problem where err if no such folder!
        if frame_count % frame_interval == 0 and frame_count >= fps * start_time and frame_count <= fps * end_time:
            output_filename_full = f"{output_folder}/frame_{frame_count:04d}.jpg"
            cv2.imwrite(output_filename_full, frame)
            output_filename_short = f"frame_{frame_count:04d}.jpg"
            result.append(output_filename_full)
            frame_list.append(frame_count)

        frame_count += 1

    cap.release()

    if not result:
        print("No frames were captured. returning an empty list")
    else:
        print(f"{frame_count} frames captured! Returning captured frames as list")
    
    print(result)
    return result, frame_list

# extract_frames('mario1-1.mp4',20,25,6)

# Note: cipher.py Line 264
# was:
#     function_patterns = [
#         # https://github.com/ytdl-org/youtube-dl/issues/29326#issuecomment-865985377
#         # https://github.com/yt-dlp/yt-dlp/commit/48416bc4a8f1d5ff07d5977659cb8ece7640dcd8
#         # var Bpa = [iha];
#         # ...
#         # a.C && (b = a.get("n")) && (b = Bpa[0](b), a.set("n", b),
#         # Bpa.length || iha("")) }};
#         # In the above case, `iha` is the relevant function name
#         r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
#         r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
#     ]
# is:
# function_patterns = [
#     # https://github.com/ytdl-org/youtube-dl/issues/29326#issuecomment-865985377
#     # https://github.com/yt-dlp/yt-dlp/commit/48416bc4a8f1d5ff07d5977659cb8ece7640dcd8
#     # var Bpa = [iha];
#     # ...
#     # a.C && (b = a.get("n")) && (b = Bpa[0](b), a.set("n", b),
#     # Bpa.length || iha("")) }};
#     # In the above case, `iha` is the relevant function name
#     r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&.*?\|\|\s*([a-z]+)',
#     r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
#     r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
# ]