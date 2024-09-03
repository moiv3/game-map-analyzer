# external dependencies
from fastapi import APIRouter, Request, Response, Depends, Form
from google.oauth2 import id_token
from google.auth.transport import requests
import traceback

# internal dependencies
from utils.classes import *
from utils.auth import get_token_header
from models.user_models import create_user, authenticate_user, get_user_preferences, patch_user_preferences, signin_by_google
from utils.auth import check_user_signin_status
from utils.config import GOOGLE_OAUTH_CLIENT_ID

router = APIRouter(
    prefix="/api/user",
    tags=["User"]
)

@router.post("/", summary="註冊一個新的會員")
async def signup(sign_up_credentials: SignupFormData, request: Request, response: Response):
    return create_user(email=sign_up_credentials.email, password=sign_up_credentials.password, name=sign_up_credentials.name) 

@router.put("/auth", response_model=TokenOut, summary="登入會員帳戶")
async def signin(sign_in_credentials: SigninFormData, request: Request, response: Response):
    return authenticate_user(email=sign_in_credentials.email, password=sign_in_credentials.password)

@router.get("/auth", response_model=UserSigninDataOut, summary="取得當前登入的會員資訊")
async def check_signin_status(request: Request, response: Response, token_data: TokenOut = Depends(get_token_header)):
    return check_user_signin_status(token_data)

@router.get("/preferences", summary="取得使用者偏好設定")
async def fetch_preferences(token_data: TokenOut = Depends(get_token_header)):
    return get_user_preferences(token_data)

@router.patch("/preferences", summary="修改使用者偏好設定")
async def modify_preferences(user_preferences: UserPreferences, token_data: TokenOut = Depends(get_token_header)):
    return patch_user_preferences(user_preferences, token_data)

@router.post("/signin_by_google", summary="使用Google登入")
async def signin_by_google_oauth2(credential: CredentialIn):
    try:
        # Specify the CLIENT_ID of the app that accesses the backend. If valid, get user info
        idinfo = id_token.verify_oauth2_token(credential.credential, requests.Request(), GOOGLE_OAUTH_CLIENT_ID, clock_skew_in_seconds=10)
        user_google_id = idinfo['sub']
        user_email = idinfo["email"]
        user_name = idinfo["name"]
        
        # Check user info with the database (user_models)
        result = signin_by_google(user_email, user_name, user_google_id)
        return result

    except ValueError:
        traceback.print_exc()
        return {"error": True, "message": "Signin by google failed, please check logs"}