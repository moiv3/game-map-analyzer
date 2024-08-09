from celery import Celery
import time

# db config
from dotenv import load_dotenv
import os
import mysql.connector
load_dotenv()
db_host = os.getenv("db_host")
db_user = os.getenv("db_user")
db_pw = os.getenv("db_pw")
db_database = os.getenv("db_database")

celery_app = Celery(
    'worker',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

# celery_app.conf.task_routes = {'tasks.*': {'queue': 'video'}}

@celery_app.task(bind=True)
def process_video(self, video_id: str, api_key: str):
    task_id = self.request.id
    print(f"Processing video {video_id} with task ID {task_id} by key {api_key}")

    # 20240807 add database support
    website_db = mysql.connector.connect(
        host=db_host, user=db_user, password=db_pw, database=db_database)
    website_db_cursor = website_db.cursor()
    cmd = "INSERT INTO task_status (task_id, api_key, youtube_id, status) VALUES (%s, %s, %s, %s)"
    website_db_cursor.execute(cmd, (task_id, api_key, video_id, "PROCESSING"))
    website_db.commit()

    # THE FAKE FUNCTION
    try:
        for i in range(6):
            time.sleep(15)
            self.update_state(state='PROGRESS', meta={'progress': (i + 1) * 10})
            print(f"{task_id} progress updated to {(i + 1) * 10}")

        cmd = "UPDATE task_status SET status = %s WHERE task_id = %s"
        website_db_cursor.execute(cmd, ("COMPLETED", task_id))
        website_db.commit()

    except Exception:
        cmd = "UPDATE task_status SET status = %s WHERE task_id = %s"
        website_db_cursor.execute(cmd, ("ERROR", task_id))
        website_db.commit()
        {"status": "error", "video_id": video_id}

    # END OF THE FAKE FUNCTION

    return {"status": "completed", "video_id": video_id}