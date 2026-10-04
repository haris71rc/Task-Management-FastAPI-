import asyncio
from sqlalchemy import select

from app.db.database import AsyncSessionLocal
from app.db.models.user import User


async def main():
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.id == 7)
        result = await session.execute(stmt)
        user = result.scalar_one()
        
        try:
            await session.delete(user)
            await session.commit()
        except Exception:
            session.rollback()


if __name__ == "__main__":
    asyncio.run(main())
