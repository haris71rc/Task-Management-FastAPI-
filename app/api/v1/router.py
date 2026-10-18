from fastapi import APIRouter
from app.api.v1 import health,tasks
from app.api.v1.users import router as users_router
from app.api.v1.projects import router as project_router
from app.api.v1.auth import router as auth_router
from app.api.v1.attachments import router as attachments_router
from app.api.v1.attachment_downloads import router as downloads_router
from app.api.v1.websocket import router as websocket_router
from app.api.v1.streaming_response import router as streaming_router


router = APIRouter()

router.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"]
)

router.include_router(
    tasks.router,
    prefix="/api/v1/tasks",
    tags=["Tasks"]
)

router.include_router(
    attachments_router,
    prefix="/api/v1",
)

router.include_router(
    users_router,
)

router.include_router(
    project_router
)

router.include_router(
    auth_router
)

router.include_router(
    downloads_router
)

router.include_router(
    websocket_router
)

router.include_router(
    streaming_router
)