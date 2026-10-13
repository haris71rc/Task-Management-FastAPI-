import uuid
from datetime import datetime
from sqlalchemy import(
    DateTime,
    String,
    Text,
    Index,
    func
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class OutboxEvent(Base):
    __tablename__ = "outbox_events"
    __table_args__ = (
        Index(
            "ix_outbox_events_pending",
            "published_at",
            "created_at",
        ),
    )
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key= True,
        default=uuid.uuid4
    )
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    