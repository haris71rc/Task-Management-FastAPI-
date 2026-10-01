from fastapi import APIRouter
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    logger.info("Health Api Called")
    return{
        "status": "ok",
        "service": "task-management-api",
    }