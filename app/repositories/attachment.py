from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.attachment import Attachment


class AttachmentRepository:
    
    def __init__(self, db: AsyncSession):
        self.db= db
        
    async def get_attachment(
        self,
        attachment_id: int
    ) -> Attachment| None:
        stmt = select(Attachment).where(Attachment.id == attachment_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()