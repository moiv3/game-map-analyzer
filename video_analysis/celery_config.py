from celery import Celery
import time
import boto3
import uuid
import json
import traceback
import video_analysis.mario_parser_0809 as mario_parser_0809
import utils.send_email as send_email

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
def process_video(self, video_id: str, api_key: str):
    task_id = self.request.id
    print(f"Processing video {video_id} with task ID {task_id} by key {api_key}")

    # 20240807 add database support
    website_db = mysql.connector.connect(
        host=db_host, user=db_user, password=db_pw, database=db_database)
    website_db_cursor = website_db.cursor()
    cmd = "INSERT INTO task_status (task_id, api_key, youtube_id, status, video_source) VALUES (%s, %s, %s, %s, %s)"
    website_db_cursor.execute(cmd, (task_id, api_key, video_id, "PROCESSING", "Youtube"))
    website_db.commit()

    # THE FAKE FUNCTION
    try:
        # DUMMY SEQUENCE
        parse_result = mario_parser_0809.mario_parser_function(task_id, video_id=video_id)

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

        if parse_result["ok"]:
            # REAL JSON
            data_dict = parse_result["text"]
        else:
            # DUMMY JSON
            data_dict = {"start_frame":0,"end_frame":0, "jumps":[{"jump":20, "fall":30},{"jump":40, "fall":50},{"jump":60, "fall":70},]}
        
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
        return {"status": "error", "video_id": video_id}

    # END OF THE FAKE FUNCTION

    return {"status": "completed", "video_id": video_id}


# For video uploaded via S3
@celery_app.task(bind=True)
def process_uploaded_video(self, video_id: str, user_id: int, game: str):
    if game not in ["mario", "sonic", "mario_new"]:
        return{"error": True, "message": "Not a currently supported game"}
        
    task_id = self.request.id
    print(f"Processing uploaded video {video_id} with task ID {task_id} by user_id {user_id}, game: {game}")

    # 20240807 add database support
    website_db = mysql.connector.connect(
        host=db_host, user=db_user, password=db_pw, database=db_database)
    website_db_cursor = website_db.cursor()

    # get user email and name
    cmd = "SELECT id, name, email, send_mail FROM member WHERE id = %s"
    website_db_cursor.execute(cmd, (user_id,))
    user_info = website_db_cursor.fetchone()
    user_name = user_info[1]
    user_email = user_info[2]
    user_send_mail = user_info[3]

    # update task status
    cmd = "UPDATE task SET task_id = %s, status = %s WHERE video_id = %s"
    # cmd = "INSERT into task (task_id, user_id, video_id, status) VALUES (%s, %s, %s, %s)"
    website_db_cursor.execute(cmd, (task_id, "PROCESSING", video_id))
    website_db.commit()

    # THE REAL FUNCTION
    try:
        # parse sequence
        parse_result = mario_parser_0809.mario_parser_function(task_id, source="S3", video_id=video_id, game_type=game)
        if "error" in parse_result and parse_result["error"]:
            # log error to database
            message = parse_result["message"]
            cmd = "UPDATE task SET status = %s, message = %s WHERE task_id = %s"
            website_db_cursor.execute(cmd, ("ERROR", message, task_id))
            website_db.commit()

            # send mail to user
            if user_send_mail:
                send_email.send_email_to_address(user_email, user_name, "分析未成功")

            return parse_result
        
        elif "ok" in parse_result and parse_result["ok"]:
            # filepath
            # file_path = f"{task_id}.jpg"

            # UPLOAD A PICTURE TO S3 SEQUENCE
            map_filepath = parse_result["file"]
            map_filename = f"map_{task_id}.jpg"
            print("Uploading map...")
            s3_client.upload_file(map_filepath, BUCKET_NAME, map_filename, ExtraArgs={'ContentType': 'image/jpeg'})
            print("Uploading complete.")
            picture_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{map_filename}"
            # file_url = f"https://{CLOUDFRONT_URL}/{unique_filename}"

            # UPDATE database with picture url
            cmd = "UPDATE task SET result_map = %s WHERE task_id = %s"
            website_db_cursor.execute(cmd, (picture_url, task_id))
            website_db.commit()

            # upload video to s3
            video_filepath = parse_result["video"]
            video_filename = f"video_{task_id}.mp4"
            print("Uploading video...")
            s3_client.upload_file(video_filepath, BUCKET_NAME, video_filename)
            print("Uploading complete.")
            video_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{video_filename}"
            # file_url = f"https://{CLOUDFRONT_URL}/{unique_filename}"

            # UPDATE database with video url
            cmd = "UPDATE task SET result_video = %s WHERE task_id = %s"
            website_db_cursor.execute(cmd, (video_url, task_id))
            website_db.commit()

            if game == "mario":
                # Upload json data, convert dictionary to JSON string
                data_dict = parse_result["text"]
                json_data = json.dumps(data_dict)
                json_file_name = f"movement_{task_id}.json"
                movement_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{json_file_name}"
                print("Uploading JSON...")
                s3_client.put_object(Bucket=BUCKET_NAME, Key=json_file_name, Body=json_data)
                print("Uploading complete.")
            elif game == "sonic" or game == "mario_new":
                movement_filepath = parse_result["movement"]
                movement_filename = f"movement_{task_id}.jpg"
                movement_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{movement_filename}"
                print("Uploading movement...")
                s3_client.upload_file(movement_filepath, BUCKET_NAME, movement_filename, ExtraArgs={'ContentType': 'image/jpeg'})
                print("Uploading complete.")

            # UPDATE database with json url
            cmd = "UPDATE task set result_movement = %s WHERE task_id = %s"
            website_db_cursor.execute(cmd, (movement_url, task_id))
            website_db.commit()

            # UPDATE task status
            cmd = "UPDATE task SET status = %s WHERE task_id = %s"
            website_db_cursor.execute(cmd, ("COMPLETED", task_id))
            website_db.commit()

            # send mail to user
            if user_send_mail:
                send_email.send_email_to_address(user_email, user_name, "分析成功")

        else:
            print("Something weird happened! Please check logs.")
            # send mail to user
            send_email.send_email_to_address(user_email, user_name, "分析未成功")
            return{"error": True, "message": "An unknown exception happened"}

    except Exception:
        traceback.print_exc()
        cmd = "UPDATE task SET status = %s, message = %s WHERE task_id = %s"
        website_db_cursor.execute(cmd, ("ERROR", "內部系統異常", task_id))
        website_db.commit()

        if user_send_mail:
            send_email.send_email_to_address(user_email, user_name, "分析未成功")

    # END OF THE REAL FUNCTION

    return {"status": "completed", "video_id": video_id}