# external dependencies
import mysql.connector
import traceback

# internal dependencies
from utils.config import db_host, db_user, db_pw, db_database


def get_api_statistics():
    try:
        website_db = mysql.connector.connect(
            host=db_host, user=db_user, password=db_pw, database=db_database)
        website_db_cursor = website_db.cursor()
        cmd = """SELECT COUNT(*) AS total,
        SUM(CASE WHEN status='COMPLETED' THEN 1 ELSE 0 END) as completed,
        SUM(CASE WHEN status='PROCESSING' THEN 1 ELSE 0 END) as processing,
        SUM(CASE WHEN status='QUEUED' THEN 1 ELSE 0 END) as queued,
        SUM(CASE WHEN status='UPLOADED' THEN 1 ELSE 0 END) as uploaded,
        SUM(CASE WHEN status='ERROR' THEN 1 ELSE 0 END) as error
        FROM task"""
        website_db_cursor.execute(cmd)
        db_fetch_result = website_db_cursor.fetchone()
        
        statistics_result = {}

        tasks_result = {}
        tasks_result["total"] = db_fetch_result[0]
        tasks_result["completed"] = db_fetch_result[1]
        tasks_result["processing"] = db_fetch_result[2]
        tasks_result["queued"] = db_fetch_result[3]
        tasks_result["uploaded"] = db_fetch_result[4]
        tasks_result["error"] = db_fetch_result[5]
        statistics_result["tasks"] = tasks_result

        cmd = """SELECT COUNT(*) AS total,
        SUM(CASE WHEN game_type='mario' THEN 1 ELSE 0 END) as mario,
        SUM(CASE WHEN game_type='mario_new' THEN 1 ELSE 0 END) as mario_new,
        SUM(CASE WHEN game_type='sonic' THEN 1 ELSE 0 END) as sonic
        FROM video"""
        website_db_cursor.execute(cmd)
        db_fetch_result = website_db_cursor.fetchone()
        
        videos_result = {}
        videos_result["total"] = db_fetch_result[0]
        videos_result["mario"] = db_fetch_result[1]
        videos_result["mario_new"] = db_fetch_result[2]
        videos_result["sonic"] = db_fetch_result[3]
        statistics_result["videos"] = videos_result

        return statistics_result 
    
    except Exception as e:
        traceback.print_exc()
        return {"error": True, "message": e}
