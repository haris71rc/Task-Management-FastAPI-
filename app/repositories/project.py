from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.project import Project

class ProjectRepository:
    
    def __init__(self, db: AsyncSession):
        self.db = db
     
     
    async def get_by_id(self, project_id: int) -> Project | None:
        stmt = select(Project).where(Project.id == project_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
     
    
    async def create(self, project: Project) -> Project:
        self.db.add(project)
        self.db.flush()
        return project
        