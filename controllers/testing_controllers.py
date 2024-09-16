from fastapi import APIRouter
from datetime import datetime
from utils.classes import *

router = APIRouter(
    prefix="/api/testing",
    tags=["Testing"]
)

@router.get("/cicd_test", response_model=Success, summary="測試CI/CD使用之路徑，亦做為網站health check使用")
async def get_cicd_test():
    return {"ok": True, "message":f"This message was auto-generated on: {datetime.now()}"}