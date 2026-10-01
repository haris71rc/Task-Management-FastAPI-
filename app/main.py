from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.middleware.request_logging import request_logging_middleware
from app.core.logging import configure_logging
from app.core.config import settings

configure_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

app.middleware("http")(request_logging_middleware)
app.include_router(v1_router)
