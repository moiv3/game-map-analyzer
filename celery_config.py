from celery import Celery
import time
import boto3
import uuid
import json
import traceback
import mario_parser_0809

# db config
from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()
db_host = os.getenv("db_host")
db_user = os.getenv("db_user")
db_pw = os.getenv("db_pw")
db_database = os.getenv("db_database")

# S3 client initialization
s3_client = boto3.client('s3', region_name=os.getenv("region_name"), 
                         aws_access_key_id=os.getenv("aws_access_key_id"),
                         aws_secret_access_key=os.getenv("aws_secret_access_key"))

BUCKET_NAME = os.getenv("s3_bucket_name")
CLOUDFRONT_URL = os.getenv("cloudfront_distribution_domain_name")

celery_app = Celery(
    'worker',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

# celery_app.conf.task_routes = {'tasks.*': {'queue': 'video'}}

@celery_app.task(bind=True)
def process_fake_video(self, video_id: str, api_key: str):
    task_id = self.request.id
    print(f"Processing video {video_id} with task ID {task_id} by key {api_key}")

    # 20240807 add database support
    website_db = mysql.connector.connect(
        host=db_host, user=db_user, password=db_pw, database=db_database)
    website_db_cursor = website_db.cursor()
    cmd = "INSERT INTO task_status (task_id, api_key, youtube_id, status) VALUES (%s, %s, %s, %s)"
    website_db_cursor.execute(cmd, (task_id, api_key, video_id, "PROCESSING"))
    website_db.commit()

    # THE FAKE FUNCTION
    try:
        # DUMMY SEQUENCE
        for i in range(6):
            time.sleep(2)
            self.update_state(state='PROGRESS', meta={'progress': (i + 1) * 10})
            print(f"{task_id} progress updated to {(i + 1) * 10}")

        # dummy filepath
        file_path = 'output0809.jpg'

        # UPLOAD A PICTURE TO S3 SEQUENCE
        unique_id = str(uuid.uuid4())
        unique_filename = f"{unique_id}_{file_path}"
        s3_client.upload_file(file_path, BUCKET_NAME, unique_filename)
        picture_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{unique_filename}"
        # file_url = f"https://{CLOUDFRONT_URL}/{unique_filename}"

        # UPDATE database with picture url
        cmd = "UPDATE task_status SET result_picture_url = %s WHERE task_id = %s"
        website_db_cursor.execute(cmd, (picture_url, task_id))
        website_db.commit()

        # Upload dummy json dataConvert dictionary to JSON string
        data_dict = {"start_frame":0,"end_frame":0, "clear_stage":True, "jumps":[{"jump":20, "fall":30},{"jump":40, "fall":50},{"jump":60, "fall":70},]}
        json_data = json.dumps(data_dict)
        json_file_name = f"{unique_id}_{file_path}.json"
        json_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{json_file_name}"

        s3_client.put_object(Bucket=BUCKET_NAME, Key=json_file_name, Body=json_data)

        # UPDATE database with json url
        cmd = "UPDATE task_status set result_text = %s WHERE task_id = %s"
        website_db_cursor.execute(cmd, (json_url, task_id))
        website_db.commit()

        # UPDATE task status
        cmd = "UPDATE task_status SET status = %s WHERE task_id = %s"
        website_db_cursor.execute(cmd, ("COMPLETED", task_id))
        website_db.commit()


    except Exception:
        traceback.print_exc()
        cmd = "UPDATE task_status SET status = %s WHERE task_id = %s"
        website_db_cursor.execute(cmd, ("ERROR", task_id))
        website_db.commit()
        {"status": "error", "video_id": video_id}

    # END OF THE FAKE FUNCTION

    return {"status": "completed", "video_id": video_id}


@celery_app.task(bind=True)
def process_video(self, video_id: str, api_key: str):
    task_id = self.request.id
    print(f"Processing video {video_id} with task ID {task_id} by key {api_key}")

    # 20240807 add database support
    website_db = mysql.connector.connect(
        host=db_host, user=db_user, password=db_pw, database=db_database)
    website_db_cursor = website_db.cursor()
    cmd = "INSERT INTO task_status (task_id, api_key, youtube_id, status) VALUES (%s, %s, %s, %s)"
    website_db_cursor.execute(cmd, (task_id, api_key, video_id, "PROCESSING"))
    website_db.commit()

    # THE FAKE FUNCTION
    try:
        # DUMMY SEQUENCE
        mario_parser_0809.mario_parser_function(task_id, youtube_id=video_id)

        # dummy filepath
        file_path = f"{task_id}.jpg"

        # UPLOAD A PICTURE TO S3 SEQUENCE
        map_filename = f"map_{file_path}"
        s3_client.upload_file(file_path, BUCKET_NAME, map_filename)
        picture_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{map_filename}"
        # file_url = f"https://{CLOUDFRONT_URL}/{unique_filename}"

        # UPDATE database with picture url
        cmd = "UPDATE task_status SET result_picture_url = %s WHERE task_id = %s"
        website_db_cursor.execute(cmd, (picture_url, task_id))
        website_db.commit()

        # upload video to s3
        video_file_path = f"video_{task_id}.mp4"
        video_filename = f"video_{task_id}.mp4"
        s3_client.upload_file(video_file_path, BUCKET_NAME, video_filename)
        video_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{video_filename}"
        # file_url = f"https://{CLOUDFRONT_URL}/{unique_filename}"

        # UPDATE database with video url
        cmd = "UPDATE task_status SET result_video_url = %s WHERE task_id = %s"
        website_db_cursor.execute(cmd, (video_url, task_id))
        website_db.commit()

        #TEST SEQUENCE TOmmorow MORNING, THEN DEAL WITH JSON


        # DUMMY JSON
        data_dict = {"start_frame":0,"end_frame":0, "clear_stage":True, "jumps":[{"jump":20, "fall":30},{"jump":40, "fall":50},{"jump":60, "fall":70},]}
        
        # Upload dummy json dataConvert dictionary to JSON string
        json_data = json.dumps(data_dict)
        json_file_name = f"movement_{task_id}.json"
        json_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{json_file_name}"

        s3_client.put_object(Bucket=BUCKET_NAME, Key=json_file_name, Body=json_data)

        # UPDATE database with json url
        cmd = "UPDATE task_status set result_text = %s WHERE task_id = %s"
        website_db_cursor.execute(cmd, (json_url, task_id))
        website_db.commit()

        # UPDATE task status
        cmd = "UPDATE task_status SET status = %s WHERE task_id = %s"
        website_db_cursor.execute(cmd, ("COMPLETED", task_id))
        website_db.commit()


    except Exception:
        traceback.print_exc()
        cmd = "UPDATE task_status SET status = %s WHERE task_id = %s"
        website_db_cursor.execute(cmd, ("ERROR", task_id))
        website_db.commit()
        {"status": "error", "video_id": video_id}

    # END OF THE FAKE FUNCTION

    return {"status": "completed", "video_id": video_id}