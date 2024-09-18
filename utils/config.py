from datetime import timedelta
import os
from dotenv import load_dotenv
load_dotenv()

# db config
db_host = os.getenv("db_host")
db_user = os.getenv("db_user")
db_pw = os.getenv("db_pw")
db_database = os.getenv("db_database")
SECRET_KEY = os.getenv("jwt_secret_key")

# s3 config
region_name=os.getenv("region_name")
aws_access_key_id=os.getenv("aws_access_key_id")
aws_secret_access_key=os.getenv("aws_secret_access_key")
BUCKET_NAME = os.getenv("s3_bucket_name")
CLOUDFRONT_URL = os.getenv("cloudfront_distribution_domain_name")

# google oauth config
GOOGLE_OAUTH_CLIENT_ID = os.getenv("google_oauth_client_id")

# gmail config
GM_EMAIL = os.getenv("gm_sender_email")
GM_PW = os.getenv("gm_sender_pw")

# other config
token_valid_time = timedelta(days=7) # Signin token validity
MAX_FILE_SIZE = 5 * 1024 * 1024 # Maximum accepted file size in bytes FOR BACKEND
MAX_QUEUED_VIDEOS = 3 # Max video queue length. If there are more than N videos queued, the next video will not be auto processed.
MAX_REMARK_SIZE = 30 # Max remark text length FOR BACKEND.
SUPPORTED_GAME_TYPES = ["mario", "mario_new", "sonic"] # Supported game types
VIDEO_PROCESS_CACHE_DAYS = 1 # If the most recent analysis for a video is under N days old, the program returns a cached result