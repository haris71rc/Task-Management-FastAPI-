from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import LoginRequest, LoginResponse
from app.services.auth import AuthService
from app.dependencies import get_db
from app.core.security import create_access_token


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

@router.post("/login",status_code=status.HTTP_200_OK)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    
    user = await service.authenticate_user(
        email=payload.email,
        password=payload.password
    )
    
    access_token = create_access_token(
        user_id=user.id,
        role= "USER"
    )
    
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer"
    )
    