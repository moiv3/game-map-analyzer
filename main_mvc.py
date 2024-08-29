from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
import traceback

from utils.classes import *

# import app routers
from controllers import user_controllers
from controllers import website_controllers
from controllers import video_controllers

app = FastAPI(
    title="Game Map Analyzer",
    # description=description,
    summary="An analyzer website to analyzing mario and sonic gameplay videos.",
    version="0.0.1")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Static Pages
@app.get("/", include_in_schema=False)
async def index_page():
    return FileResponse("static/index.html", media_type="text/html")
@app.get("/use_api", include_in_schema=False)
async def use_api_page():
    return FileResponse("static/use_api.html", media_type="text/html")
@app.get("/member", include_in_schema=False)
async def member_page():
    return FileResponse("static/member.html", media_type="text/html")
@app.get("/task_queue", include_in_schema=False)
async def task_queue_page():
    return FileResponse("static/task_queue.html", media_type="text/html")
@app.get("/upload_video", include_in_schema=False)
async def upload_video_page():
    return FileResponse("static/upload_video.html", media_type="text/html")
@app.get("/statistics", include_in_schema=False)
async def statistics_page():
    return FileResponse("static/statistics.html", media_type="text/html")
@app.get("/settings", include_in_schema=False)
async def settings_page():
    return FileResponse("static/settings.html", media_type="text/html")  

# Routers
app.include_router(video_controllers.router)
app.include_router(website_controllers.router)
app.include_router(user_controllers.router)

# Exception Hamdling
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: Exception):    
    traceback.print_exc()
    return JSONResponse(status_code=400, content=(Error(error="true", message="格式不正確，請確認輸入資訊").dict()))

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(status_code=500, content=(Error(error="true", message="伺服器內部異常，請聯繫管理員確認").dict()))
