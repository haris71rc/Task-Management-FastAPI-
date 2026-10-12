from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from app.db.models.project import Project

SORT_COLUMNS = {
    "id": Project.id,
    "name": Project.name,
    "created_at": Project.created_at,
}


class ProjectRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, project_id: int) -> Project | None:
        stmt = select(Project).where(Project.id == project_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_detail(self, project_id: int) -> Project | None:
        stmt = (
            select(Project)
            .options(
                joinedload(Project.owner),
                selectinload(Project.tasks),
            )
            .where(Project.id == project_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        user_id: int,
        page: int,
        limit: int,
        sort: str,
        order: str,
    ) -> list[Project]:
        column = SORT_COLUMNS.get(sort, Project.created_at)
        direction = asc if order == "asc" else desc
        offset = (page - 1) * limit

        stmt = (
            select(Project)
            .where(Project.owner_id == user_id)
            .order_by(direction(column), direction(Project.id))
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_for_user(self, user_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(Project)
            .where(Project.owner_id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def create(self, project: Project) -> Project:
        self.db.add(project)
        await self.db.flush()
        return project
