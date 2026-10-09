from datetime import datetime
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger
from enum import Enum
from sqlalchemy import Enum as SQLEnum
from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.project import Project
    from app.db.models.task import Task

class UserRole(str,Enum):
    ADMIN="ADMIN"
    USER="USER"

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger,primary_key= True)
    
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable= False,
        server_default=func.now()
    )
    
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )
    
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        nullable=False,
        default=UserRole.USER
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    
    projects: Mapped[list["Project"]] = relationship(back_populates="owner")
    
    created_tasks: Mapped[list["Task"]] = relationship(back_populates="creator")
    