import asyncio
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models.project import Project
from sqlalchemy.orm import selectinload

async def main():
    async with AsyncSessionLocal() as session:
        stmt = select(Project).options(selectinload(Project.owner)).where(Project.id == 1)
        result = await session.execute(stmt)
        project = result.scalar_one()
        print(project.name,  project.owner.name)
        
if __name__ == "__main__":
    asyncio.run(main())