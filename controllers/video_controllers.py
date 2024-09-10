from fastapi import APIRouter, Depends, File, Form, UploadFile

# internal dependencies
from utils.classes import *
from models.video_models import get_all_task_status_db, process_uploaded_video_by_id, upload_file_and_process
from utils.auth import get_token_header

router = APIRouter(
    prefix="/api/video",
    tags=["Video"]
)

@router.get("/task_status_db/", response_model=TaskQueueOut, summary="取得使用者目前的待分析任務清單")
async def get_user_task_status_db(token_data: TokenOut = Depends(get_token_header)):
    return get_all_task_status_db(token_data)

@router.post("/process_uploaded_video/", response_model=Success, responses={400: {"model": Error}, 401: {"model": Error}, 500: {"model": Error}},summary="解析從S3上傳的影片")
async def process_video_by_id(process_info: VideoParseInfoUploaded, token_data: TokenOut = Depends(get_token_header)):
    return process_uploaded_video_by_id(process_info, token_data)

@router.post("/upload_video", response_model=Success, responses={400: {"model": Error}, 403: {"model": Error}, 500: {"model": Error}}, summary="上傳一個影片並開始解析")
async def upload_file(file: UploadFile = File(...), token_data: TokenOut = Depends(get_token_header), gameType: str = Form(...), messageInput: str | None = Form(None)):
    return upload_file_and_process(file, token_data, gameType=gameType, messageInput=messageInput)