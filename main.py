from fastapi import FastAPI, Request, Response, Depends, Header, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime, date
from pydantic import BaseModel, EmailStr
from typing import Annotated, Literal
from annotated_types import Len, MinLen
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
from dotenv import load_dotenv
import os
import mysql.connector
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, InvalidSignatureError, DecodeError
from datetime import *
import traceback
from celery.result import AsyncResult
from celery_config import celery_app
import celery_config
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

load_dotenv()

# db config

db_host = os.getenv("db_host")
db_user = os.getenv("db_user")
db_pw = os.getenv("db_pw")
db_database = os.getenv("db_database")

secret_key = os.getenv("jwt_secret_key")

# AWS S3 config
s3_client = boto3.client('s3', region_name=os.getenv("region_name"), 
                         aws_access_key_id=os.getenv("aws_access_key_id"),
                         aws_secret_access_key=os.getenv("aws_secret_access_key"))

BUCKET_NAME = os.getenv("s3_bucket_name")
CLOUDFRONT_URL = os.getenv("cloudfront_distribution_domain_name")



# token config
from datetime import timedelta
token_valid_time = timedelta(days=7)


# from tasks import process_video
from celery.result import AsyncResult
from celery_config import celery_app, process_video
import mario_parser

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def index_page():
    return FileResponse("static/index.html")

@app.get("/use_api")
def use_api_page():
    return FileResponse("static/use_api.html")

@app.get("/member")
def member_page():
    return FileResponse("static/member.html")

@app.get("/api_keys")
def api_keys_page():
    return FileResponse("static/api_keys.html")

@app.get("/task_queue")
def task_queue_page():
    return FileResponse("static/task_queue.html")

@app.get("/upload_video")
def upload_video_page():
    return FileResponse("static/upload_video.html")

@app.get("/api/process-video/")
def process_video(video_id: str = "DGQGvAwqpbE"):
    task = mario_parser.mario_parser_function(video_id)
    # task = process_video.delay(video_id)
    return task

@app.post("/api/process-video/")
def enqueue_video(video_id: str = "AAA"):
    task = process_video.delay(video_id)
    return {"task_id": task.id, "message": f"Video {video_id} has been queued for processing."}

@app.get("/task-status/{task_id}")
def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.state == 'PENDING':
        return {"status": task_result.state}
    elif task_result.state != 'FAILURE':
        return {"status": task_result.state, "info": task_result.info}
    else:
        return {"status": task_result.state, "info": str(task_result.info)}

@app.get("/api/test")
def test_api():
    return {"ok": True}





# user signin/signout, taken from stage2

class Error(BaseModel):
    error: bool
    message: str

class SignupFormData(BaseModel):
    name: Annotated[str, MinLen(1)]
    email: EmailStr
    password: Annotated[str, MinLen(1)]

class SigninFormData(BaseModel):
    email: EmailStr
    password: Annotated[str, MinLen(1)]

class TokenOut(BaseModel):
    token: str

class UserSigninData(BaseModel):
    id: int
    name: Annotated[str, MinLen(1)]
    email: EmailStr

class UserSigninDataOut(BaseModel):
    data: UserSigninData

class VideoParseInfo(BaseModel):
    youtube_id: str
    api_key: str

class VideoParseInfoUploaded(BaseModel):
    video_id: str
    api_key: str

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 這個感覺不太好分類，可以問一下
def get_token_header(authorization: str = Header(...)) -> TokenOut:
    stripped_token = authorization[len("Bearer "):]
    if not stripped_token:
        return False
    return TokenOut(token=stripped_token)


def create_user(email: str, password: str, name: str):
    website_db = mysql.connector.connect(
        host=db_host, user=db_user, password=db_pw, database=db_database)
    website_db_cursor = website_db.cursor()
    cmd = "SELECT email FROM member WHERE email = %s"
    website_db_cursor.execute(cmd, (email,))
    result = website_db_cursor.fetchone()
    if result:
        print("user already exists")
        return JSONResponse(status_code=422, content=(Error(error="true", message="此信箱已被使用").dict()))
    else:
        hashed_password = get_password_hash(password)
        print(password, hashed_password)
        cmd = "INSERT INTO member (name, email, hashed_password) VALUES (%s, %s, %s)"
        website_db_cursor.execute(cmd, (name, email, hashed_password))
        website_db.commit()
        print("added new user")
        return {"ok": True}
    
def authenticate_user(email: str, password: str):
    website_db = mysql.connector.connect(
        host=db_host, user=db_user, password=db_pw, database=db_database)
    website_db_cursor = website_db.cursor()
    cmd = "SELECT id, email, hashed_password, name FROM member WHERE email = %s"
    website_db_cursor.execute(cmd, (email,))
    result = website_db_cursor.fetchone()
    if not result:
        print("no user")
        return JSONResponse(status_code=401, content=(Error(error="true", message="帳號不存在，請確認相關資訊").dict()))
    elif not verify_password(password, hashed_password=result[2]):
        print("found user but password mismatch")
        return JSONResponse(status_code=401, content=(Error(error="true", message="密碼不正確，請確認相關資訊").dict()))
    else:
        user_information = {}
        user_information["id"] = result[0]
        user_information["email"] = result[1]
        user_information["name"] = result[3]
        time_now = datetime.now(tz=timezone.utc)
        user_information["iat"] = time_now.timestamp()
        user_information["exp"] = (time_now + token_valid_time).timestamp()
        print(user_information)
        user_token = jwt.encode(user_information, secret_key, algorithm="HS256")
        print(user_token)
        return {"token": user_token}
    
# Put in models first. maybe should be utils?
def check_user_signin_status(token_data):
    print(token_data)
    try:
        result = {}
        result["data"] = jwt.decode(token_data.token, secret_key, algorithms="HS256")
        print("Data:", result)
        # return result #Testing 20240621
        return JSONResponse(status_code=200, content=result)
    except ExpiredSignatureError:
        print("ExpiredSignatureError")
        return JSONResponse(status_code=401, content={"data": None})
    except InvalidSignatureError:
        print("InvalidSignatureError")
        return JSONResponse(status_code=401, content={"data": None})
    except DecodeError:
        print("DecodeError")
        return JSONResponse(status_code=401, content={"data": None})
    except Exception:
        print("Other exceptions")
        return JSONResponse(status_code=401, content={"data": None})
    
def check_user_signin_status_return_bool(token_data):
    try:
        decode_result = jwt.decode(token_data.token, secret_key, algorithms="HS256")
        # decode success and there is an id in the result (indicating a real user)
        if decode_result["id"]:
            return decode_result
        else:
            return False
    except Exception:
        return False
    
@app.post("/api/user", summary="註冊一個新的會員")
async def signup(sign_up_credentials: SignupFormData, request: Request, response: Response):
    return create_user(email=sign_up_credentials.email, password=sign_up_credentials.password, name=sign_up_credentials.name) 

@app.put("/api/user/auth", response_model=TokenOut, summary="登入會員帳戶")
async def signin(sign_in_credentials: SigninFormData, request: Request, response: Response):
    return authenticate_user(email=sign_in_credentials.email, password=sign_in_credentials.password)

# check sign in status(predicted usage: on every page). response model integration was helped by ChatGPT
@app.get("/api/user/auth", response_model=UserSigninDataOut, summary="取得當前登入的會員資訊", tags=["User"])
async def check_signin_status(request: Request, response: Response, token_data: TokenOut = Depends(get_token_header)):
    return check_user_signin_status(token_data)

import uuid

def get_new_api_key(token_data):
    signin_status = check_user_signin_status_return_bool(token_data)
    if not check_user_signin_status_return_bool(token_data):
        return JSONResponse(status_code=403, content={"error":True, "message": "使用者驗證失敗，請先登入"})
    else:
        try:
            website_db = mysql.connector.connect(
                host=db_host, user=db_user, password=db_pw, database=db_database)
            website_db_cursor = website_db.cursor()
            user_id = signin_status["id"]

            # Deactivate all user's API old keys
            cmd = "UPDATE api_key SET validity = 0 WHERE user_id = %s"
            website_db_cursor.execute(cmd,(user_id,))
            website_db.commit()
            print("Old keys revoked")

            # Generate a new key (uuid4)
            new_api_key = str(uuid.uuid4())
            validity = 1
            cmd = "INSERT INTO api_key (user_id, api_key, validity) VALUES (%s, %s, %s)"
            website_db_cursor.execute(cmd,(user_id, new_api_key, validity))
            website_db.commit()
            print("New keys added and activated")

            return {"ok": True, "id": user_id, "api_key": new_api_key}

        except Exception:
            traceback.print_exc()
            return {"error": True}


@app.get("/api/generate_new_key")
async def get_api_key(request: Request, response: Response, token_data: TokenOut = Depends(get_token_header)):
    return get_new_api_key(token_data)

def get_current_api_key(token_data):
    signin_status = check_user_signin_status_return_bool(token_data)
    if not check_user_signin_status_return_bool(token_data):
        return JSONResponse(status_code=403, content={"error":True, "message": "使用者驗證失敗，請先登入"})
    else:
        try:
            website_db = mysql.connector.connect(
                host=db_host, user=db_user, password=db_pw, database=db_database)
            website_db_cursor = website_db.cursor()
            user_id = signin_status["id"]

            # Select user's valid API keys
            cmd = "SELECT api_key FROM api_key WHERE (user_id = %s AND validity = 1)"
            website_db_cursor.execute(cmd,(user_id,))
            valid_api_key_result = website_db_cursor.fetchall()
            valid_api_key_output = {"user_id": user_id}
            if valid_api_key_result:
                valid_api_keys = []
                for item in valid_api_key_result:
                    valid_api_keys.append(item[0])
                valid_api_key_output["api_keys"] = valid_api_keys
                valid_api_key_output["ok"] = True
            else:
                return {"error": True}
            
            print(valid_api_key_output)
            return valid_api_key_output
        
        except Exception:
            traceback.print_exc()
            return {"error": True}


@app.get("/api/get_current_key")
async def get_api_key(request: Request, response: Response, token_data: TokenOut = Depends(get_token_header)):
    return get_current_api_key(token_data)

@app.post("/api/process_fake_video")
async def process_fake_video(request: Request, response: Response, video_info: VideoParseInfo):
    # class VideoParseInfo(BaseModel):
    # youtube_id: str
    # api_key: str
    print(video_info)
    website_db = mysql.connector.connect(
        host=db_host, user=db_user, password=db_pw, database=db_database)
    website_db_cursor = website_db.cursor()

    # Select user's valid API keys
    cmd = "SELECT api_key FROM api_key WHERE (api_key = %s AND validity = 1)"
    website_db_cursor.execute(cmd,(video_info.api_key,))
    api_key_result = website_db_cursor.fetchone()
    if api_key_result:
        # function to parse video and add to task queue
        task = celery_config.process_video.delay(video_info.youtube_id, video_info.api_key)
        return {"ok":True, "task_id": task.id, "message": f"Video {video_info.youtube_id} has been queued for processing."}

        # task = process_video.delay(video_info.youtube_id)
        # return {"task_id": task.id, "message": f"Video {video_info.youtube_id} has been queued for processing."}

    else:
        return JSONResponse(status_code=401, content=(Error(error="true", message="API key不正確，請確認輸入資訊").dict()))

@app.get("/task-status-db/")
def get_all_task_status_db(token_data: TokenOut = Depends(get_token_header)):
    signin_status = check_user_signin_status_return_bool(token_data)
    if not check_user_signin_status_return_bool(token_data):
        return JSONResponse(status_code=403, content={"error":True, "message": "使用者驗證失敗，請先登入"})
    else:
        user_id = signin_status["id"]
        website_db = mysql.connector.connect(
            host=db_host, user=db_user, password=db_pw, database=db_database)
        website_db_cursor = website_db.cursor()
        
        final_output = {}

        # Select user's valid API keys
        # cmd = "SELECT task_id, api_key, youtube_id, status, date_updated FROM task_status WHERE status = 'PROCESSING' OR status = 'ERROR' ORDER BY date_updated DESC LIMIT 10;"
        cmd = "SELECT task_id, task_status.api_key, youtube_id, status, date_updated FROM task_status JOIN api_key ON task_status.api_key = api_key.api_key WHERE (api_key.user_id = %s AND (status = 'PROCESSING' OR status = 'ERROR')) ORDER BY date_updated DESC LIMIT 5"
        website_db_cursor.execute(cmd,(user_id,))
        tasks_wip_result = website_db_cursor.fetchall()
        if tasks_wip_result:
            output_task_part_all=[]
            for task in tasks_wip_result:
                output_task_part_single={}
                output_task_part_single["task_id"] = task[0]
                output_task_part_single["api_key"] = task[1]
                output_task_part_single["youtube_id"] = task[2]
                output_task_part_single["status"] = task[3]
                output_task_part_single["date_updated"] = task[4]
                output_task_part_all.append(output_task_part_single)
        else:
            output_task_part_all = []
        final_output["tasks_wip"] = output_task_part_all

        cmd = "SELECT task_id, task_status.api_key, youtube_id, status, date_updated FROM task_status JOIN api_key ON task_status.api_key = api_key.api_key WHERE (api_key.user_id = %s AND (status = 'COMPLETED')) ORDER BY date_updated DESC LIMIT 5"
        website_db_cursor.execute(cmd, (user_id,))
        tasks_completed_result = website_db_cursor.fetchall()
        if tasks_completed_result:
            output_task_part_all=[]
            for task in tasks_completed_result:
                output_task_part_single={}
                output_task_part_single["task_id"] = task[0]
                output_task_part_single["api_key"] = task[1]
                output_task_part_single["youtube_id"] = task[2]
                output_task_part_single["status"] = task[3]
                output_task_part_single["date_updated"] = task[4]
                output_task_part_all.append(output_task_part_single)
        else:
            output_task_part_all = []
        final_output["tasks_completed"] = output_task_part_all

        print(final_output)
        return final_output

    

    i = celery_app.control.inspect()
    active_tasks = i.active()
    reserved_tasks = i.reserved()
    scheduled_tasks = i.scheduled()
    tasks = {}

    if active_tasks:
        tasks['active'] = active_tasks
    if reserved_tasks:
        tasks['reserved'] = reserved_tasks
    if scheduled_tasks:
        tasks['scheduled'] = scheduled_tasks
    
    print(tasks)
    return tasks

@app.get("/task-status/")
def get_all_task_status_db():
    i = celery_app.control.inspect()
    active_tasks = i.active()
    reserved_tasks = i.reserved()
    scheduled_tasks = i.scheduled()
    tasks = {}

    if active_tasks:
        tasks['active'] = active_tasks
    if reserved_tasks:
        tasks['reserved'] = reserved_tasks
    if scheduled_tasks:
        tasks['scheduled'] = scheduled_tasks
    
    print(tasks)
    return tasks

@app.post("/api/upload", summary="上傳一個影片")
async def upload_file(file: UploadFile = File(...), token_data: TokenOut = Depends(get_token_header)):
    try:
        signin_status = check_user_signin_status_return_bool(token_data)
        # TODO: Exception for signin status?
        if not signin_status:
            raise HTTPException(status_code=401, detail="登入資訊異常，請重新登入")
        else:
            user_id = signin_status["id"]
            unique_id = str(uuid.uuid4())
            unique_filename = f"{unique_id}.mp4"
            s3_client.upload_fileobj(file.file, BUCKET_NAME, unique_filename)
            file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{unique_filename}"
            # file_url = f"https://{CLOUDFRONT_URL}/{unique_filename}"
            """
            create table uploaded_video(
            id int auto_increment,
            user_id int not null,
            video_id varchar(255) not null,
            video_url varchar(255) not null,
            create_time datetime not null default current_timestamp,
            primary key(id)
            );
            """        

            # save to database
            website_db = mysql.connector.connect(host=db_host, user=db_user, password=db_pw, database=db_database)
            website_db_cursor = website_db.cursor()
            
            cmd = "INSERT INTO uploaded_video (user_id, video_id, video_url, status) VALUES (%s, %s, %s, %s)"
            website_db_cursor.execute(cmd, (user_id, unique_id, file_url, "NOT PROCESSED"))
            website_db.commit()

            return {"ok": True, "filename": unique_filename}
    except (NoCredentialsError, PartialCredentialsError):
        raise HTTPException(status_code=403, detail="Could not authenticate to S3")
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/get_uploaded_videos", summary="取得影片")
async def get_uploaded_videos(token_data: TokenOut = Depends(get_token_header)):
    # try / except
    signin_status = check_user_signin_status_return_bool(token_data)
    if not signin_status:
        return JSONResponse(status_code=401, content=(Error(error="true", message="登入資訊異常，請重新登入").dict()))
    else:
        user_id = signin_status["id"]
        website_db = mysql.connector.connect(
            host=db_host, user=db_user, password=db_pw, database=db_database)
        website_db_cursor = website_db.cursor()
        
        final_output = {}

        # Select user's valid API keys
        cmd = "SELECT user_id, video_id, status, error_message, create_time FROM uploaded_video WHERE user_id = %s ORDER BY create_time DESC LIMIT 10"
        website_db_cursor.execute(cmd, (user_id,))
        uploaded_video_result = website_db_cursor.fetchall()
        if uploaded_video_result:
            output_video_all = []
            for video in uploaded_video_result:
                output_video_single = {}
                output_video_single["user_id"] = video[0]
                output_video_single["video_id"] = video[1]
                output_video_single["status"] = video[2]
                output_video_single["error_message"] = video[3]
                output_video_single["create_time"] = video[4]
                output_video_all.append(output_video_single)
        else:
            output_video_all = []
        final_output["uploaded_videos"] = output_video_all

        return final_output
    
@app.post("/api/process_uploaded_video_test_route", summary="解析從S3上傳的影片")
async def process_video_by_id(process_info: VideoParseInfoUploaded, token_data: TokenOut = Depends(get_token_header)):
    print(process_info)
    return{"ok": True}

@app.post("/api/process_uploaded_video", summary="解析從S3上傳的影片")
async def process_video_by_id(process_info: VideoParseInfoUploaded, token_data: TokenOut = Depends(get_token_header)):
    # 檢查登入狀態
    signin_status = check_user_signin_status_return_bool(token_data)
    if not signin_status:
        return JSONResponse(status_code=401, content=(Error(error="true", message="登入資訊異常，請重新登入").dict()))
    
    # 檢查video_id & API key狀態
    else:
        user_id = signin_status["id"]
        api_key = process_info.api_key
        uploaded_video_id = process_info.video_id

        website_db = mysql.connector.connect(
            host=db_host, user=db_user, password=db_pw, database=db_database)
        website_db_cursor = website_db.cursor()
        
        # Check if everything is there
        cmd = "SELECT member.id, uploaded_video.video_id, uploaded_video.video_url, uploaded_video.status FROM member JOIN uploaded_video JOIN api_key WHERE member.id = %s AND api_key.api_key = %s AND api_key.validity = 1 AND uploaded_video.video_id = %s"
        # cmd = "SELECT member.id, uploaded_video.video_id, uploaded_video.video_url FROM member JOIN uploaded_video JOIN api_key WHERE member.id = 2 AND api_key.api_key = 'accb8d65-9183-4f72-8f4a-629d8c89e9e0' AND api_key.validity = 1 AND uploaded_video.video_id = '13446a32-800d-460e-8b31-f4b7814a524b'"
        website_db_cursor.execute(cmd, (user_id, api_key, uploaded_video_id))
        db_fetch_result = website_db_cursor.fetchone()
        print(db_fetch_result)

        if not db_fetch_result:
            return JSONResponse(status_code=401, content=(Error(error="true", message="影片資訊或API key不正確，請重新確認").dict()))
        elif not db_fetch_result[3] == "NOT PROCESSED":
            return JSONResponse(status_code=400, content=(Error(error="true", message="影片正在處理中，請至會員中心確認結果").dict()))
        else:
            cmd = "UPDATE uploaded_video SET status = %s WHERE video_id = %s"
            website_db_cursor.execute(cmd, ("PROCESSING", uploaded_video_id))
            website_db.commit()

            task = celery_config.process_uploaded_video.delay(uploaded_video_id, api_key)
            return {"ok": True, "task_id": task.id, "video_id": uploaded_video_id, "message": f"已經排入處理佇列，請至會員中心確認結果"}
    #從S3下載影片
    #開始解析
    #回傳結果
    return{"ok": True}




#Exception Block
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: Exception):    
    traceback.print_exc()
    return JSONResponse(status_code=400, content=(Error(error="true", message="格式不正確，請確認輸入資訊").dict()))

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(status_code=500, content=(Error(error="true", message="伺服器內部異常，請聯繫管理員確認").dict()))

