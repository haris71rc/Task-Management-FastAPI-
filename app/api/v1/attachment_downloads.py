from urllib.parse import quote
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool
from app.core.config import settings
from app.core.s3 import s3_client
from app.dependencies import get_current_user, get_db
from app.services.attachment_service import get_authorized_attachment

router = APIRouter(prefix="/api/v1", tags=["Attachments"])

DOWNLOAD_URL_TTL_SECOND = 300


@router.get("/attachments/{attachment_id}/download-url")
async def create_download_url(
    attachment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    attachment = await get_authorized_attachment(
        db=db,
        attachment_id=attachment_id,
        current_user=current_user,
    )

    safe_filename = attachment.filename.replace('"', "")
    disposition = f"attachment; filename*=UTF-8''{quote(safe_filename)}"

    url = await run_in_threadpool(
        s3_client.generate_presigned_url,
        "get_object",
        Params={
            "Bucket": settings.s3_bucket_name,
            "Key": attachment.s3_key,
            "ResponseContentDisposition": disposition,
            "ResponseContentType": attachment.content_type,
        },
        ExpiresIn =DOWNLOAD_URL_TTL_SECOND
    )
    
    return {
        "download_url": url,
        "expires_at":DOWNLOAD_URL_TTL_SECOND
    }
