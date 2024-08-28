import cv2

def get_video_info(video_path):
    # Load the video file
    video = cv2.VideoCapture(video_path)
    
    # Get width and height
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Get frame rate (frames per second)
    fps = video.get(cv2.CAP_PROP_FPS)
    
    # Get the total number of frames
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Calculate duration in seconds
    duration = frame_count / fps
    
    # Release the video file
    video.release()
    
    return {
        "width": width,
        "height": height,
        "fps": fps,
        "duration": duration
    }

# Example usage
if __name__ == "__main__":
    video_info = get_video_info("mario1-1.mp4")
    print(video_info)
