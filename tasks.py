from celery_config import celery_app
import time

@celery_app.task(bind=True)
def process_video(self, video_id: str):
    task_id = self.request.id
    print(f"Processing video {video_id} with task ID {task_id}")
    
    for i in range(6):
        time.sleep(2)
        self.update_state(state='PROGRESS', meta={'progress': (i + 1) * 10})
    
    return {"status": "completed", "video_id": video_id}
