from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.middleware.request_logging import request_logging_middleware
from app.core.logging import configure_logging
from app.core.config import settings

from contextlib import asynccontextmanager
from app.core.redis import redis_client

configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_client.ping()
    app.state.redis = redis_client
    
    try:
        yield
    finally:
        await redis_client.aclose()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

app.middleware("http")(request_logging_middleware)
app.include_router(v1_router)
