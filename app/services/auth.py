from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_password
from app.repositories.user import UserRepository
from app.db.models.user import User

class AuthService:
    
    def __init__(self, db: AsyncSession):
        self.user_repository = UserRepository(db)
        
    async def authenticate_user(self, email:str , password: str) -> User | None:
        user = await self.user_repository.get_by_email(email)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        if user.password_hash is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        valid_password = verify_password(password, user.password_hash)
        
        if not valid_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        return user
        