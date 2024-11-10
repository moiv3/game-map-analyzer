from celery import Celery
import boto3
import json
import traceback
import video_analysis.mario_parser_0809 as mario_parser_0809
import utils.send_email as send_email
from utils.config import db_host, db_user, db_pw, db_database, region_name, aws_access_key_id, aws_secret_access_key, BUCKET_NAME, CLOUDFRONT_URL
import mysql.connector


# S3 client initialization
s3_client = boto3.client('s3', region_name=region_name, 
                         aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key)


celery_app = Celery(
    'worker',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)


# For video uploaded via S3
@celery_app.task(bind=True)
def process_uploaded_video(self, video_id: str, user_id: int, game: str, task_num_id: int):
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
    cmd = "UPDATE task SET task_id = %s, status = %s WHERE (video_id = %s AND id = %s)"
    website_db_cursor.execute(cmd, (task_id, "PROCESSING", video_id, task_num_id))
    website_db.commit()

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

            # UPLOAD A PICTURE TO S3 SEQUENCE
            map_filepath = parse_result["file"]
            map_filename = f"map_{task_id}.jpg"
            print("Uploading map...")
            s3_client.upload_file(map_filepath, BUCKET_NAME, map_filename, ExtraArgs={'ContentType': 'image/jpeg'})
            print("Uploading complete.")
            picture_url = f"https://{CLOUDFRONT_URL}/{map_filename}"

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
            video_url = f"https://{CLOUDFRONT_URL}/{video_filename}"

            # UPDATE database with video url
            cmd = "UPDATE task SET result_video = %s WHERE task_id = %s"
            website_db_cursor.execute(cmd, (video_url, task_id))
            website_db.commit()

            if game == "mario":
                print("mario v1 engine does not output a movement.")
                movement_url = None

            elif game == "sonic" or game == "mario_new":
                movement_filepath = parse_result["movement"]
                movement_filename = f"movement_{task_id}.jpg"
                movement_url = f"https://{CLOUDFRONT_URL}/{movement_filename}"

                print("Uploading movement...")
                s3_client.upload_file(movement_filepath, BUCKET_NAME, movement_filename, ExtraArgs={'ContentType': 'image/jpeg'})
                print("Uploading complete.")

            # UPDATE database with json url
            cmd = "UPDATE task set result_movement = %s WHERE task_id = %s"
            website_db_cursor.execute(cmd, (movement_url, task_id))
            website_db.commit()

            # UPDATE task status
            cmd = "UPDATE task SET status = %s, message = %s WHERE task_id = %s"
            website_db_cursor.execute(cmd, ("COMPLETED", "分析完成", task_id))
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

    return {"status": "completed", "video_id": video_id}