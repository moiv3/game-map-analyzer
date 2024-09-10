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
from utils.hash import compute_file_hash
from utils.classes import TokenOut, VideoParseInfoUploaded, Error
from utils.auth import get_token_header, check_user_signin_status_return_bool
from utils.config import db_host, db_user, db_pw, db_database
from utils.config import region_name, aws_access_key_id, aws_secret_access_key, BUCKET_NAME, CLOUDFRONT_URL
from utils.config import MAX_FILE_SIZE, MAX_QUEUED_VIDEOS, MAX_REMARK_SIZE, SUPPORTED_GAME_TYPES
from utils.config import HASHING_CHECK, VIDEO_PROCESS_CACHE_DAYS

# AWS S3 config
s3_client = boto3.client('s3', region_name=region_name, 
                         aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key)

# Check if [x] days passed since last task's update_time
def check_if_cached_response(website_db_cursor, video_id, gameType):
    print("Checking for cached result...")
    cmd = "SELECT update_time, result_map, result_movement, result_video, status, message, game_type FROM task WHERE (video_id = %s AND cached_result = '0' AND (status = %s OR status = %s) AND game_type = %s) ORDER BY update_time DESC LIMIT 1"
    website_db_cursor.execute(cmd, (video_id, "COMPLETED", "ERROR", gameType))
    cached_result_to_output = website_db_cursor.fetchone()
    if cached_result_to_output:
        print(cached_result_to_output)
        time_diff_days = (datetime.now()-cached_result_to_output[0]).total_seconds() / 86400
        # In this special case, return cached result with days mark, don't enter analysis
        if time_diff_days < VIDEO_PROCESS_CACHE_DAYS:
            print("Cached result and satisfies cache conditions, returning cached result")
            result = {}
            result["task_id"] = str(uuid.uuid4())
            result["cached_result_map"] = cached_result_to_output[1]
            result["cached_result_movement"] = cached_result_to_output[2]
            result["cached_result_video"] = cached_result_to_output[3]
            result["cached_status"] = cached_result_to_output[4]
            result["cached_message"] = cached_result_to_output[5] + "(cached)"
            return result
        else:
            print("Cached result too old, returning None")
            return None
    else:
        print("No cached result, returning None")
        return None

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
            cmd = "SELECT task.id, task.game_type, task.user_remark, task.status, task.create_time, task.update_time FROM task JOIN video ON task.video_id = video.video_id JOIN member ON task.user_id = member.id WHERE (task.user_id = %s AND (status = 'PROCESSING' OR status = 'QUEUED' OR status = 'UPLOADED')) ORDER BY task.update_time DESC LIMIT 5"
            website_db_cursor.execute(cmd,(user_id,))
            tasks_wip_result = website_db_cursor.fetchall()
            print(tasks_wip_result)

            if tasks_wip_result:
                output_task_part_all=[]
                for task in tasks_wip_result:
                    output_task_part_single={}
                    output_task_part_single["任務編號"] = task[0]
                    output_task_part_single["遊戲類型"] = task[1]
                    output_task_part_single["影片備註"] = task[2]
                    output_task_part_single["狀態"] = task[3]
                    output_task_part_single["上傳時間"] = task[4]
                    output_task_part_single["最後更新時間"] = task[5]
                    output_task_part_all.append(output_task_part_single)

            else:
                output_task_part_all = []

            final_output["tasks_wip"] = output_task_part_all

            # Select user's current COMPLETED or ERROR tasks
            cmd = "SELECT task.id, task.game_type, task.user_remark, task.status, task.update_time, task.result_map, task.result_video, task.result_movement, task.message FROM task JOIN video ON task.video_id = video.video_id JOIN member ON task.user_id = member.id WHERE (task.user_id = %s AND (status = 'COMPLETED' OR status = 'ERROR')) ORDER BY task.update_time DESC LIMIT 5"
            website_db_cursor.execute(cmd, (user_id,))
            tasks_completed_result = website_db_cursor.fetchall()
            print(tasks_completed_result)

            if tasks_completed_result:
                output_task_part_all=[]
                for task in tasks_completed_result:
                    output_task_part_single={}
                    output_task_part_single["任務編號"] = task[0]
                    output_task_part_single["遊戲類型"] = task[1]
                    output_task_part_single["影片備註"] = task[2]
                    output_task_part_single["狀態"] = task[3]
                    output_task_part_single["最後更新時間"] = task[4]
                    output_task_part_single["地圖"] = task[5]
                    output_task_part_single["影片"] = task[6]
                    output_task_part_single["路徑分析"] = task[7]
                    output_task_part_single["系統訊息"] = task[8]
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
    
    # 檢查task_id狀態
    else:
        user_id = signin_status["id"]
        task_num_id = process_info.task_id

        website_db = mysql.connector.connect(
            host=db_host, user=db_user, password=db_pw, database=db_database)
        website_db_cursor = website_db.cursor()
        # 讀取task_id的內容
        cmd = "SELECT task_id, video_id, game_type FROM task WHERE id = %s"
        website_db_cursor.execute(cmd, (task_num_id,))
        task_info = website_db_cursor.fetchone()
        if not task_info:
            return JSONResponse(status_code=401, content=(Error(error="true", message="影片資訊不正確，請重新確認").dict()))
        else:
            video_id = task_info[1]
            gameType = task_info[2]
        
        # 檢查是否可以對應cached response
        cached_result_to_output = check_if_cached_response(website_db_cursor, video_id, gameType)
        if cached_result_to_output:
            cached_result_map = cached_result_to_output["cached_result_map"]
            cached_result_movement = cached_result_to_output["cached_result_movement"]
            cached_result_video = cached_result_to_output["cached_result_video"]
            cached_status = cached_result_to_output["cached_status"]
            cached_message = cached_result_to_output["cached_message"]
            cmd = "UPDATE task SET status = %s, result_map = %s, result_movement = %s, result_video = %s, message = %s, cached_result = %s WHERE id = %s"
            website_db_cursor.execute(cmd, (cached_status, cached_result_map, cached_result_movement, cached_result_video, cached_message, 1, task_num_id))
            website_db.commit()
            #TODO: 補上信件
            return {"ok": True, "message": f"此影片已有近{VIDEO_PROCESS_CACHE_DAYS}天的分析結果，將直接更新結果"}
        else: 
            print("No cached result available, entering normal analyze route")
        
        # 先確認目前有多少 PROCESSING
        cmd = "SELECT COUNT(*) FROM task WHERE (status = %s OR status = %s)"
        website_db_cursor.execute(cmd, ("PROCESSING", "QUEUED"))
        processing_items_result = website_db_cursor.fetchone()[0]
        print("Processing items:", processing_items_result)
        if processing_items_result >= MAX_QUEUED_VIDEOS:
            return JSONResponse(status_code=500, content=(Error(error="true", message="目前有太多請求，請稍後再試").dict()))

        # 確認這個task的狀態
        cmd = "SELECT user_id, video_id, status, game_type, id FROM task WHERE user_id = %s AND id = %s"
        website_db_cursor.execute(cmd, (user_id, task_num_id))
        db_fetch_result = website_db_cursor.fetchone()
        print(db_fetch_result)
        video_unique_id = db_fetch_result[1]
        video_status = db_fetch_result[2]
        game_type = db_fetch_result[3]
        task_num_id = db_fetch_result[4]

        if not db_fetch_result:
            return JSONResponse(status_code=401, content=(Error(error="true", message="影片資訊不正確，請重新確認").dict()))
        elif video_status in ["QUEUED", "PROCESSING"]:
            return JSONResponse(status_code=400, content=(Error(error="true", message="影片正在處理中").dict()))
        elif video_status in ["COMPLETED", "ERROR"]:
            return JSONResponse(status_code=400, content=(Error(error="true", message="影片已處理完畢，請重新整理以確認結果").dict()))
        # status = "UPLOADED", 可以處理影片的狀態
        else:
            cmd = "UPDATE task SET status = %s WHERE id = %s"
            website_db_cursor.execute(cmd, ("QUEUED", task_num_id))
            website_db.commit()

            task = celery_config.process_uploaded_video.delay(video_unique_id, user_id, game_type, task_num_id)
            return JSONResponse(status_code=200, content={"ok": True, "filename": video_unique_id, "message": f"已經排入處理隊列"})

def upload_file_and_process(file: UploadFile = File(...), token_data: TokenOut = Depends(get_token_header), gameType: str = Form(...), messageInput: str | None = Form(None)):
    try:
        signin_status = check_user_signin_status_return_bool(token_data)
        if not signin_status:
            return JSONResponse(status_code=401, content={"error": True, "message": "登入資訊異常，請重新登入"})
        else:
            website_db = mysql.connector.connect(host=db_host, user=db_user, password=db_pw, database=db_database)
            website_db_cursor = website_db.cursor()

            # by GPT: Check file size
            file.file.seek(0, 2)  # Move to the end of the file
            file_size = file.file.tell()  # Get the size in bytes
            file.file.seek(0)  # Reset to the beginning of the file
            print(f"File size: {file_size} bytes")
            if file_size > MAX_FILE_SIZE:
                return JSONResponse(status_code=413, content=(Error(error="true", message="檔案大小超出上限").dict()))
            print(gameType)
            print(messageInput)

            # Check message size
            if messageInput and len(messageInput) > MAX_REMARK_SIZE:
                return JSONResponse(status_code=400, content=(Error(error="true", message="備註長度超出上限").dict()))
            
            # Check game_type
            if gameType not in SUPPORTED_GAME_TYPES:
                return JSONResponse(status_code=400, content=(Error(error="true", message="目前尚不支援此遊戲，請檢查輸入，再試一次").dict()))
            
            # get file hash
            video_hash = compute_file_hash(file.file)

            user_id = signin_status["id"]
            upload_video_id = str(uuid.uuid4())
            unique_filename = f"{upload_video_id}.mp4"

            # TODO: hash is implemented, next do logic for checking if video has same hash
            cmd = "SELECT video_id, video_url FROM video WHERE video_hash = %s ORDER BY create_time DESC LIMIT 1"
            website_db_cursor.execute(cmd, (video_hash,))
            video_duplicate_result = website_db_cursor.fetchone()
            # dupe video: 1. no upload, don't insert video id at all. Insert task only
            if video_duplicate_result:
                print("Same video detected! Overriding video_id and not uploading to S3...")
                upload_video_id = video_duplicate_result[0] # override video_id
            else:
                file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{unique_filename}"
                s3_client.upload_fileobj(file.file, BUCKET_NAME, unique_filename)

                # Save video info to database
                cmd = "INSERT INTO video (user_id, video_id, video_url, video_source, video_hash) VALUES (%s, %s, %s, %s, %s)"
                website_db_cursor.execute(cmd, (user_id, upload_video_id, file_url, "s3", video_hash))
                website_db.commit()

            # Check if [x] days passed since last task's update_time
            cmd = "SELECT update_time, result_map, result_movement, result_video, status, message, game_type FROM task WHERE (video_id = %s AND cached_result = '0' AND game_type = %s AND (status = %s OR status = %s)) ORDER BY update_time DESC LIMIT 1"
            website_db_cursor.execute(cmd, (upload_video_id, gameType, "COMPLETED", "ERROR"))
            cached_result_to_output = website_db_cursor.fetchone()
            if cached_result_to_output:
                time_diff_days = (datetime.now()-cached_result_to_output[0]).total_seconds() / 86400
                # In this special case, return cached result with days mark, don't enter analysis
                if time_diff_days < VIDEO_PROCESS_CACHE_DAYS:
                    print("Cached result and satisfies cache conditions, returning cached result")
                    task_id = str(uuid.uuid4())
                    cached_result_map = cached_result_to_output[1]
                    cached_result_movement = cached_result_to_output[2]
                    cached_result_video = cached_result_to_output[3]
                    cached_status = cached_result_to_output[4]
                    cached_message = cached_result_to_output[5] + "(cached)"
                    cmd = "INSERT INTO task (task_id, user_id, video_id, status, result_map, result_movement, result_video, message, cached_result, user_remark, game_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    website_db_cursor.execute(cmd, (task_id, user_id, upload_video_id, cached_status, cached_result_map, cached_result_movement, cached_result_video, cached_message, 1, messageInput, gameType))
                    website_db.commit()
                    #TODO: 補上信件
                    return {"ok": True, "message": f"此影片已有近{VIDEO_PROCESS_CACHE_DAYS}天的分析結果，將直接更新結果"}
                else: 
                    print("Cached result but cache too old, entering normal analyze route")
            else:
                print("No cached result available, entering normal analyze route")

            # Check if task is currently processing 確認user送出的task是否有完全一樣的task正在處理中?
            # cmd = "SELECT member.id, video.video_id, task.status FROM member JOIN video ON member.id = video.user_id JOIN task ON task.video_id = video.id WHERE video.video_id = %s"
            cmd = "SELECT user_id, video_id, game_type from task WHERE user_id = %s AND video_id = %s AND game_type = %s AND (status = %s OR status = %s OR status = %s)"
            website_db_cursor.execute(cmd, (user_id, upload_video_id, gameType, "UPLOADED", "QUEUED", "PROCESSING"))
            db_fetch_result = website_db_cursor.fetchone()
            print("Same user&video&task check:", db_fetch_result)

            if db_fetch_result:
                return JSONResponse(status_code=400, content=(Error(error="true", message="有相同的影片已在處理中").dict()))

            # Create an "uploaded" info in table "tasks"
            cmd = "INSERT into task (user_id, video_id, status, user_remark, game_type) VALUES (%s, %s, %s, %s, %s)"
            website_db_cursor.execute(cmd, (user_id, upload_video_id, "UPLOADED", messageInput, gameType))
            task_num_id = website_db_cursor.lastrowid
            website_db.commit()

            # Check how many status="PROCESSING" is there
            cmd = "SELECT COUNT(*) FROM task WHERE (status = %s OR status = %s)"
            website_db_cursor.execute(cmd, ("PROCESSING", "QUEUED"))
            processing_items_result = website_db_cursor.fetchone()[0]
            print("Processing items:", processing_items_result)

            # If too many items processing, don't process, return ok
            if processing_items_result >= MAX_QUEUED_VIDEOS:
                return {"ok": True, "message": "目前請求數量超出伺服器上限，已上傳此影片，但未開始分析，請稍待再送出分析需求"}
            # If not too many items, process video (update task first, then pass task to celery)
            else:
                cmd = "UPDATE task SET status = %s WHERE (video_id = %s AND id = %s)"
                website_db_cursor.execute(cmd, ("QUEUED", upload_video_id, task_num_id))
                website_db.commit()

                task = celery_config.process_uploaded_video.delay(upload_video_id, user_id, gameType, task_num_id)
                return {"ok": True, "message": f"已經排入處理隊列"}
                    
    except (NoCredentialsError, PartialCredentialsError):
        return JSONResponse(status_code=403, content={"error": True, "message": f"AWS S3連線異常，請稍後再試"})
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": True, "message": f"伺服器內部錯誤：{e}"})