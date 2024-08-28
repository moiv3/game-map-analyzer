# external dependencies
import mysql.connector
from fastapi import Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from datetime import *
import traceback
import video_analysis.celery_config as celery_config
import uuid
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# internal dependencies
from utils.classes import TokenOut, VideoParseInfoUploaded, Error
from utils.auth import get_token_header, check_user_signin_status_return_bool
from utils.config import db_host, db_user, db_pw, db_database
from utils.config import region_name, aws_access_key_id, aws_secret_access_key, BUCKET_NAME
from utils.config import MAX_FILE_SIZE, MAX_QUEUED_VIDEOS

# AWS S3 config
s3_client = boto3.client('s3', region_name=region_name, 
                         aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key)

def get_all_task_status_db(token_data: TokenOut = Depends(get_token_header)):
    signin_status = check_user_signin_status_return_bool(token_data)
    if not check_user_signin_status_return_bool(token_data):
        return JSONResponse(status_code=403, content={"error":True, "message": "使用者驗證失敗，請先登入"})
    
    else:
        try:
            user_id = signin_status["id"]
            website_db = mysql.connector.connect(
                host=db_host, user=db_user, password=db_pw, database=db_database)
            website_db_cursor = website_db.cursor()
            
            final_output = {}

            # Select user's current PROCESSING, QUEUED or UPLOADED tasks
            cmd = "SELECT task.id, video.id, video.video_source, task.status, task.update_time FROM task JOIN video ON task.video_id = video.video_id JOIN member ON task.user_id = member.id WHERE (task.user_id = %s AND (status = 'PROCESSING' OR status = 'QUEUED' OR status = 'UPLOADED')) ORDER BY task.update_time DESC LIMIT 5"
            website_db_cursor.execute(cmd,(user_id,))
            tasks_wip_result = website_db_cursor.fetchall()
            print(tasks_wip_result)

            if tasks_wip_result:
                output_task_part_all=[]
                for task in tasks_wip_result:
                    output_task_part_single={}
                    output_task_part_single["task_id"] = task[0]
                    output_task_part_single["source"] = task[2]
                    output_task_part_single["video_id"] = task[1]
                    output_task_part_single["status"] = task[3]
                    output_task_part_single["date_updated"] = task[4]
                    output_task_part_all.append(output_task_part_single)

            else:
                output_task_part_all = []

            final_output["tasks_wip"] = output_task_part_all

            # Select user's current COMPLETED or ERROR tasks
            cmd = "SELECT task.id, video.id, video.video_source, task.status, task.update_time, task.result_map, task.result_video, task.result_movement, task.message FROM task JOIN video ON task.video_id = video.video_id JOIN member ON task.user_id = member.id WHERE (task.user_id = %s AND (status = 'COMPLETED' OR status = 'ERROR')) ORDER BY task.update_time DESC LIMIT 5"
            website_db_cursor.execute(cmd, (user_id,))
            tasks_completed_result = website_db_cursor.fetchall()
            print(tasks_completed_result)

            if tasks_completed_result:
                output_task_part_all=[]
                for task in tasks_completed_result:
                    output_task_part_single={}
                    output_task_part_single["task_id"] = task[0]
                    output_task_part_single["source"] = task[2]
                    output_task_part_single["video_id"] = task[1]
                    output_task_part_single["status"] = task[3]
                    output_task_part_single["date_updated"] = task[4]
                    output_task_part_single["map"] = task[5]
                    output_task_part_single["video"] = task[6]
                    output_task_part_single["movement"] = task[7]
                    output_task_part_single["message"] = task[8]
                    output_task_part_all.append(output_task_part_single)

            else:
                output_task_part_all = []

            final_output["tasks_completed"] = output_task_part_all

            return final_output
        except Exception as e:
            traceback.print_exc()
            return JSONResponse(status_code=500, content={"error": True, "message": f"伺服器內部錯誤：{e}"})
        
def process_uploaded_video_by_id(process_info: VideoParseInfoUploaded, token_data: TokenOut = Depends(get_token_header)):
    signin_status = check_user_signin_status_return_bool(token_data)
    if not signin_status:
        return JSONResponse(status_code=401, content=(Error(error="true", message="登入資訊異常，請重新登入").dict()))
    
    # 檢查video_id & API key狀態
    else:
        user_id = signin_status["id"]
        video_id = process_info.video_id

        website_db = mysql.connector.connect(
            host=db_host, user=db_user, password=db_pw, database=db_database)
        website_db_cursor = website_db.cursor()
        
        # 先確認目前有多少 PROCESSING
        cmd = "SELECT COUNT(*) FROM task WHERE (status = %s OR status = %s)"
        website_db_cursor.execute(cmd, ("PROCESSING", "QUEUED"))
        processing_items_result = website_db_cursor.fetchone()[0]
        print("Processing items:", processing_items_result)
        if processing_items_result >= MAX_QUEUED_VIDEOS:
            return JSONResponse(status_code=500, content=(Error(error="true", message="目前有太多請求，請稍後再試").dict()))

        # 確認這個影片的狀態
        cmd = "SELECT task.user_id, task.video_id, task.status, video.game_type FROM task JOIN video ON video.video_id = task.video_id WHERE task.user_id = %s AND video.id = %s"
        website_db_cursor.execute(cmd, (user_id, video_id))
        db_fetch_result = website_db_cursor.fetchone()
        print(db_fetch_result)
        video_unique_id = db_fetch_result[1]
        video_status = db_fetch_result[2]
        game_type = db_fetch_result[3]

        if not db_fetch_result:
            return JSONResponse(status_code=401, content=(Error(error="true", message="影片資訊不正確，請重新確認").dict()))
        elif video_status in ["QUEUED", "PROCESSING"]:
            return JSONResponse(status_code=400, content=(Error(error="true", message="影片正在處理中，請至會員中心確認結果").dict()))
        elif video_status in ["COMPLETED", "ERROR"]:
            return JSONResponse(status_code=400, content=(Error(error="true", message="影片已處理完畢，請至會員中心確認結果").dict()))
        # status = "UPLOADED", 可以處理影片的狀態
        else:
            cmd = "UPDATE task SET status = %s WHERE video_id = %s"
            website_db_cursor.execute(cmd, ("QUEUED", video_unique_id))
            website_db.commit()

            task = celery_config.process_uploaded_video.delay(video_unique_id, user_id, game_type)
            return JSONResponse(status_code=200, content={"ok": True, "filename": video_unique_id, "message": f"已經排入處理佇列！`"})

def upload_file_and_process(file: UploadFile = File(...), token_data: TokenOut = Depends(get_token_header), gameType: str = Form(...)):
    try:
        signin_status = check_user_signin_status_return_bool(token_data)
        if not signin_status:
            return JSONResponse(status_code=401, content={"error": True, "message": "登入資訊異常，請重新登入"})
        else:
            website_db = mysql.connector.connect(host=db_host, user=db_user, password=db_pw, database=db_database)
            website_db_cursor = website_db.cursor()

            # Check file size
            file.file.seek(0, 2)  # Move to the end of the file
            file_size = file.file.tell()  # Get the size in bytes
            file.file.seek(0)  # Reset to the beginning of the file
            print(f"File size: {file_size} bytes")
            if file_size > MAX_FILE_SIZE:
                return JSONResponse(status_code=413, content=(Error(error="true", message="檔案大小超出上限").dict()))

            user_id = signin_status["id"]
            upload_video_id = str(uuid.uuid4())
            unique_filename = f"{upload_video_id}.mp4"
            s3_client.upload_fileobj(file.file, BUCKET_NAME, unique_filename)
            file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{unique_filename}"
            # file_url = f"https://{CLOUDFRONT_URL}/{unique_filename}"

            # Save video info to database
            cmd = "INSERT INTO video (user_id, video_id, video_url, video_source, game_type) VALUES (%s, %s, %s, %s, %s)"
            website_db_cursor.execute(cmd, (user_id, upload_video_id, file_url, "s3", gameType))
            website_db.commit()

            # Create an "uploaded" info in table "tasks"
            cmd = "INSERT into task (user_id, video_id, status) VALUES (%s, %s, %s)"
            website_db_cursor.execute(cmd, (user_id, upload_video_id, "UPLOADED"))
            website_db.commit()
            
            # Check how many status="PROCESSING" is there
            cmd = "SELECT COUNT(*) FROM task WHERE (status = %s OR status = %s)"
            website_db_cursor.execute(cmd, ("PROCESSING", "QUEUED"))
            processing_items_result = website_db_cursor.fetchone()[0]
            print("Processing items:", processing_items_result)
            # If too many items processing, not process, return ok
            if processing_items_result >= MAX_QUEUED_VIDEOS:
                return {"ok": True, "filename": unique_filename, "message": "目前請求數量超出伺服器上限，已上傳此影片，但未開始分析，請稍待再送出分析需求。"}
            # If not too many items, start the process
            else:
            # Check if everything is there
                cmd = "SELECT member.id, video.video_id, task.status FROM member JOIN video ON member.id = video.user_id JOIN task ON task.video_id = video.id WHERE video.video_id = %s"
                website_db_cursor.execute(cmd, (upload_video_id,))
                db_fetch_result = website_db_cursor.fetchone()
                print(db_fetch_result)

                if db_fetch_result:
                    return JSONResponse(status_code=400, content=(Error(error="true", message="影片已在處理中，請至會員中心確認結果").dict()))
                else:
                    # not found, process video (insert task first, then pass task to celery)
                    cmd = "UPDATE task SET status = %s WHERE video_id = %s"
                    website_db_cursor.execute(cmd, ("QUEUED", upload_video_id))
                    website_db.commit()

                    task = celery_config.process_uploaded_video.delay(upload_video_id, user_id, gameType)
                    return {"ok": True, "filename": upload_video_id, "message": f"已經排入處理佇列，請至會員中心確認結果"}
                    
    except (NoCredentialsError, PartialCredentialsError):
        return JSONResponse(status_code=403, content={"error": True, "message": f"AWS S3連線異常，請稍後再試"})
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": True, "message": f"伺服器內部錯誤：{e}"})