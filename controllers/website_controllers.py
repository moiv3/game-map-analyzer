from fastapi import APIRouter

from classes import *
from models.website_models import get_api_statistics

router = APIRouter(
    prefix="/api/website",
    tags=["Website"]
)

@router.get("/statistics", summary="取得API統計資料")
async def get_statistics():
    return get_api_statistics()


