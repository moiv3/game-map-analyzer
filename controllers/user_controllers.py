from fastapi import APIRouter, Request, Response, Depends
from classes import *
from utils.auth import get_token_header
from models.user_models import create_user, authenticate_user, get_user_preferences, patch_user_preferences
from utils.auth import check_user_signin_status

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
