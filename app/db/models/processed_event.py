import uuid
from datetime import datetime
from sqlalchemy import DateTime,String,func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column, Mapped
from app.db.base import Base

class ProcessedEvent(Base):
    __tablename__ = "processed_events"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )
    
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )