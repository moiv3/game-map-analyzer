from fastapi import FastAPI
# from tasks import process_video
from celery.result import AsyncResult
from celery_config import celery_app
import celery_config


app = FastAPI()

@app.post("/process-video/")
def enqueue_video(video_id: str):
    task = celery_config.process_video.delay(video_id)
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