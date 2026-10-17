from datetime import datetime
import uuid
from sqlalchemy import(
    BigInteger,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func
)
from sqlalchemy.orm import mapped_column, Mapped
from app.db.base import Base

class Attachment(Base):
    __tablename__ = "attachments"
    __table_args__ = (
        UniqueConstraint("s3_key", name="uq_attachments_s3_key"),
    )
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    content_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )
    s3_key: Mapped[str] = mapped_column(
        String(512),
        nullable= False
    )
    task_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tasks.id",ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    uploaded_by: Mapped[int]= mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )