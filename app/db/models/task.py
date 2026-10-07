from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy import BigInteger
from sqlalchemy import DateTime , Enum as SQLEnum
from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column , relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.project import Project
    from app.db.models.user import User
    
class TaskStatus(str, Enum):
    TODO= "TODO"
    IN_PROGRESS= "IN_PROGRESS"
    DONE= "DONE"
    
class TaskPriority(str, Enum):
    LOW= "LOW"
    MEDIUM= "MEDIUM"
    HIGH= "HIGH"

class Task(Base):
    
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(BigInteger,primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus),
        nullable=False,
        default=TaskStatus.TODO
    )
    priority: Mapped[TaskPriority] = mapped_column(
        SQLEnum(TaskPriority),
        nullable=False,
        default=TaskPriority.MEDIUM
    )
    project_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("projects.id"),
        nullable=False
    )
    created_by: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    project: Mapped["Project"] = relationship(
        back_populates="tasks"
    )
    creator: Mapped["User"] = relationship(
        back_populates="created_tasks",
    )
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    
    
    
     
