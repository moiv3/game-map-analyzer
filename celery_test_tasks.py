from celery_config import celery_app
import mario_parser
import time

# In Celery, the delay method is a convenient shortcut for applying a task asynchronously.
# When you call process_video.delay(video_id),
# it is equivalent to calling process_video.apply_async((video_id,)).
# This schedules the task to be executed in the background by the Celery worker,
# rather than running it immediately in the current thread of execution.
@celery_app.task(bind=True)
def process_video(self, video_id: str):
    print("Hello world!")
    # self.update_state(state='PROGRESS', meta={'progress': 0})
    # Do video processing
    # mario_parser.mario_parser_function("dummy")
    print("Processing!!!!!!")
    # self.update_state(state='PROGRESS', meta={'progress': 0})
    return {"status": "completed", "video_id": video_id}