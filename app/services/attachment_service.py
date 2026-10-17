import logging
import uuid

from pathlib import Path
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool
from app.core.config import settings
from app.core.s3 import s3_client
from app.db.models.attachment import Attachment
from sqlalchemy import select
from app.db.models.task import Task
from app.db.models.project import Project

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MiB

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "text/plain",
}


async def validate_file(file: UploadFile) -> tuple[str, int, str]:
    if not file.filename:
        raise HTTPException(400, "FIlename is required")

    # Normalize both Unix and Windows path separators.
    filename = Path(file.filename.replace("\\", "/")).name

    if not filename or filename in {".", ".."}:
        raise HTTPException(400, "Invalid filename")

    content_type = file.content_type or ("application/octet-stream")

    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(415, "File type is not allowed")

    # Check the size without reading the entire file into memory.
    size = 0

    while True:
        chunk = await file.read(1024 * 1024)

        if not chunk:
            break

        size += len(chunk)

        if size > MAX_FILE_SIZE:
            await file.seek(0)
            raise HTTPException(413, "File size exceeded the 10 MiB limit")

        await file.seek(0)

        return filename, size, content_type


async def create_attachment(
    db: AsyncSession,
    file: UploadFile,
    task_id: int,
    user_id: int,
) -> Attachment:

    filename, size, content_type = await validate_file(file=file)

    s3_key = f"attachments/{task_id}/{uuid.uuid4().hex}"

    # First, upload the object to S3.

    try:
        await run_in_threadpool(
            s3_client.upload_fileobj,
            file.file,
            settings.s3_bucket_name,
            s3_key,
            ExtraArgs={"ContentType": content_type},
        )

    except (BotoCoreError, ClientError) as exc:
        logger.exception("S3 upload failed")
        raise HTTPException(
            status_code=502, detail="Could not upload file to storage"
        ) from exc

    # Persist the metadata in PostgreSQL.

    attachment = Attachment(
        filename=filename,
        content_type=content_type,
        size=size,
        s3_key=s3_key,
        task_id=task_id,
        uploaded_by=user_id,
    )

    try:
        db.add(attachment)
        await db.commit()
        await db.refresh(attachment)
        return attachment

    except Exception as exc:
        await db.rollback()

        try:
            # Try deleting the uploaded file to s3
            await run_in_threadpool(
                s3_client.delete_object,
                Bucket=settings.s3_bucket_name,
                Key=s3_key,
            )

        except Exception:
            logger.exception(
                "Failed to clean up S3 object after DB failure: %s",
                s3_key,
            )

        raise HTTPException(
            status_code=500,
            detail="Could not save attachment metadata",
        ) from exc


async def get_authorized_attachment(
  db: AsyncSession,
  attachment_id: int,
  current_user,  
) -> Attachment:
    result = await db.execute(
        select(Attachment, Project.owner_id)
        .join(Task, Task.id == Attachment.task_id)
        .join(Project, Task.project_id == Project.id)
        .where(Attachment.id == attachment_id)
    )
    
    row = result.one_or_none()
    
    if row is None:
        raise HTTPException(404, "Attachment not found")
    
    attachment, owner_id = row
    role = getattr(current_user.role, "value", current_user.role)
    
    if role != "ADMIN" and owner_id != current_user.id:
        raise HTTPException(403, "You cannot access this attachment")
    
    return attachment
    