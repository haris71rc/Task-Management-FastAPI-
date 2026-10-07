from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.project import Project
from app.repositories.project import ProjectRepository
from app.repositories.user import UserRepository
from fastapi import HTTPException,status


class ProjectService:
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repository = ProjectRepository(db)
        self.user_repository = UserRepository(db)
    
    async def create_project(
        self,
        name: str,
        description: str | None,
        owner_id: int
    ) -> Project:
        
        user = await self.user_repository.get_by_id(owner_id)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Onwer not found"
            )
        
        project = Project(
            name=name,
            description=description,
            owner_id=owner_id
        )
        
        try:
            await self.project_repository.create(project)
            await self.db.commit()
            await self.db.refresh(project)
        
        except Exception:
            await self.db.rollback()
            raise
        
        return project
        
        