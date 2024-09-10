from fastapi import APIRouter

from utils.classes import *
from models.website_models import get_api_statistics

router = APIRouter(
    prefix="/api/website",
    tags=["Website"]
)

@router.get("/statistics", response_model=WebsiteStatistics, summary="取得API統計資料")
async def get_statistics():
    return get_api_statistics()


