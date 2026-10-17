from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.project import Project
from app.db.models.task import Task
from app.schemas.attachment import AttachmentRead
from app.services.attachment_service import create_attachment

# Adapt this import to your existing authentication module.
from app.dependencies import get_current_user, get_db

router = APIRouter(
    prefix="/tasks",
    tags=["Attachments"],
)


@router.post(
    "/{task_id}/attachments",
    response_model=AttachmentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_task_attachments(
    task_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Load the task and its project owner in one query.
    result = await db.execute(
        select(Task, Project.owner_id)
        .join(Project, Task.project_id == Project.id)
        .where(Task.id == task_id)
    )

    row = result.one_or_none()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    task, project_owner_id = row

    # Adjust this rule if your app supports project membership.
    role = getattr(current_user.role, "value", current_user.role)
    is_admin = role == "ADMIN"
    is_owner = project_owner_id == current_user.id

    if not (is_admin or is_owner):
        raise HTTPException(
            status_code=403,
            detail="You cannot upload attachments to this task",
        )

    return await create_attachment(
        db=db,
        file=file,
        task_id=task.id,
        user_id=current_user.id,
    )
