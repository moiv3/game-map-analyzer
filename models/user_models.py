# external dependencies
import mysql.connector
from fastapi import Depends
from fastapi.responses import JSONResponse
import jwt
from datetime import *
import traceback

# internal dependencies
from classes import TokenOut, UserPreferences, Error
from utils.config import db_host, db_user, db_pw, db_database, SECRET_KEY, token_valid_time
from utils.auth import get_password_hash, verify_password, get_token_header, check_user_signin_status_return_bool

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
        return JSONResponse(status_code=401, content=(Error(error="true", message="使用者帳號/密碼不匹配，請再試一次").dict()))
    elif not verify_password(password, hashed_password=result[2]):
        print("found user but password mismatch")
        return JSONResponse(status_code=401, content=(Error(error="true", message="使用者帳號/密碼不匹配，請再試一次").dict()))
    else:
        user_information = {}
        user_information["id"] = result[0]
        user_information["email"] = result[1]
        user_information["name"] = result[3]
        time_now = datetime.now(tz=timezone.utc)
        user_information["iat"] = time_now.timestamp()
        user_information["exp"] = (time_now + token_valid_time).timestamp()
        print(user_information)
        user_token = jwt.encode(user_information, SECRET_KEY, algorithm="HS256")
        print(user_token)
        return {"token": user_token}

def get_user_preferences(token_data: TokenOut = Depends(get_token_header)):
    # 檢查登入狀態
    signin_status = check_user_signin_status_return_bool(token_data)
    if not signin_status:
        return JSONResponse(status_code=401, content=(Error(error="true", message="登入資訊異常，請重新登入").dict()))
    
    # 檢查video_id & API key狀態
    else:
        website_db = mysql.connector.connect(
            host=db_host, user=db_user, password=db_pw, database=db_database)
        website_db_cursor = website_db.cursor()
        user_id = signin_status["id"]
        cmd = "SELECT id, name, email, validity, send_mail FROM member WHERE id = %s"
        print(user_id)
        website_db_cursor.execute(cmd, (user_id,))
        member_result = website_db_cursor.fetchone()
        member_id = member_result[0]
        member_validity = member_result[3]
        member_send_mail = member_result[4]
        if not member_id:
            return {"error": True, "message": "No member"}
        elif not member_validity:
            return {"error": True, "message": "Invalid member"}
        else:
            return {"ok": True, "member_preferences": {"send_mail": member_send_mail}}

def patch_user_preferences(user_preferences: UserPreferences, token_data: TokenOut = Depends(get_token_header)):
    # 檢查登入狀態
    signin_status = check_user_signin_status_return_bool(token_data)
    if not signin_status:
        return JSONResponse(status_code=401, content=(Error(error="true", message="登入資訊異常，請重新登入").dict()))
    
    # 檢查video_id & API key狀態
    else:
        try:
            # patch send_mail
            website_db = mysql.connector.connect(
                host=db_host, user=db_user, password=db_pw, database=db_database)
            website_db_cursor = website_db.cursor()
            print(user_preferences)
            send_mail_preference = user_preferences.send_mail
            user_id = signin_status["id"]
            cmd = "UPDATE member SET send_mail = %s WHERE id = %s"
            website_db_cursor.execute(cmd, (send_mail_preference, user_id))
            website_db.commit()
            return {"ok": True, "message": "Successfully updated user preference"}
        except Exception:
            traceback.print_exc()
            return {"error": True, "message": "伺服器內部錯誤"}
