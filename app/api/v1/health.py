import logging
from fastapi import APIRouter, HTTPException
from app.core.redis import redis_client
from sqlalchemy import Engine, text

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    logger.info("Health Api Called")
    return{
        "status": "ok",
        "service": "task-management-api",
    }
    
@router.get("/health/ready")
async def readiness():
    try:
        async with Engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

        await redis_client.ping()

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Required dependency unavailable",
        ) from exc

    return {"status": "ready"}