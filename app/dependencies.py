from fastapi import Header, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal
from app.core.security import decode_access_token
from app.repositories.user import UserRepository
from app.db.models.user import User,UserRole

security = HTTPBearer()

async def get_request_id(x_request_id: str | None = Header(default=None)):
    return x_request_id

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
        
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_access_token(token)
    subject = payload.get("sub")
    
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    try:
        user_id = int(subject)
    except (TypeError,ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    repository = UserRepository(db)
    
    user = await repository.get_by_id(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists"
        )
    
    return user
 
async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dont have sufficient permission"
        )
    
    return current_user
    