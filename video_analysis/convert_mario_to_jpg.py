from pytube import YouTube
from datetime import datetime
import cv2
import numpy as np
import os
import boto3
import traceback
from dotenv import load_dotenv
load_dotenv()

# boto config
s3_client = boto3.client('s3', region_name=os.getenv("region_name"), 
                         aws_access_key_id=os.getenv("aws_access_key_id"),
                         aws_secret_access_key=os.getenv("aws_secret_access_key"))

BUCKET_NAME = os.getenv("s3_bucket_name")
CLOUDFRONT_URL = os.getenv("cloudfront_distribution_domain_name")

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

# Download desired s3 URL
def download_s3(video_id: str, task_id: str):
    try:
        s3_filename = f"{video_id}.mp4"
        downloaded_filename = f"output_data/{task_id}/source_video/s3_{video_id}.mp4"
        s3_client.download_file(Bucket=BUCKET_NAME, Key=s3_filename, Filename=downloaded_filename)
        return downloaded_filename
    except Exception:
        traceback.print_exc()
        return None


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