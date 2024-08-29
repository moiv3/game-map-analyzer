from fastapi import APIRouter

router = APIRouter(
    prefix="/api/testing",
    tags=["Testing"]
)

@router.get("/cicd_test", summary="測試CI/CD使用之路徑，亦做為網站health check使用")
async def get_cicd_test():
    return {"ok": True}