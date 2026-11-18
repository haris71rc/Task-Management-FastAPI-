from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.user import User

class DevicePlatform(str, Enum):
    IOS = "IOS"
    ANDROID = "ANDROID"

class Device(Base):
    __tablename__ = "devices"
    __table_args__ = (
        UniqueConstraint(
            "fcm_token",
            name="uq_devices_fcm_token",
        ),
    )
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id",ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    fcm_token: Mapped[int] = mapped_column(
        String(512),
        nullable=False
    )
    platform: Mapped[DevicePlatform] = mapped_column(
        SQLEnum(DevicePlatform),
        nullable=False
    )
    device_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    user: Mapped["User"] = relationship(
        back_populates="devices",
    )