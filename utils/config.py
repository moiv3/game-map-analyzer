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

# other config
token_valid_time = timedelta(days=7)
MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_QUEUED_VIDEOS = 3