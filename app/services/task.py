from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.task import Task
from app.repositories.project import ProjectRepository
from app.repositories.task import TaskRepository
from app.schemas.tasks import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.tasks = TaskRepository(db)
        self.projects = ProjectRepository(db)

    async def get_task(self, task_id: int, user_id: int) -> Task:
        task = await self.tasks.get_by_id(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        project = await self.projects.get_by_id(task.project_id)
        if project is None or project.owner_id != user_id:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    async def create_task(self, payload: TaskCreate, user_id: int) -> Task:
        project = await self.projects.get_by_id(payload.project_id)
        if project is None or project.owner_id != user_id:
            raise HTTPException(status_code=404, detail="Project not found")
        task = Task(**payload.model_dump(), owner_id=user_id)
        try:
            await self.tasks.create(task)
            await self.db.commit()
            await self.db.refresh(task)
        except Exception:
            await self.db.rollback()
            raise
        return task

    async def update_task(self, task_id: int, payload: TaskUpdate, user_id: int) -> Task:
        task = await self.get_task(task_id, user_id)
        updates = payload.model_dump(exclude_unset=True)
        for field in ("title", "status", "priority"):
            if field in updates and updates[field] is None:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{field} cannot be null")
        for field, value in updates.items():
            setattr(task, field, value)
        try:
            await self.db.commit()
            await self.db.refresh(task)
        except Exception:
            await self.db.rollback()
            raise
        return task

    async def delete_task(self, task_id: int, user_id: int) -> None:
        task = await self.get_task(task_id, user_id)
        try:
            await self.tasks.delete(task)
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise
