from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import LoginRequest
from app.services.auth import AuthService
from app.dependencies import get_db


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
    
    return {
        "message": "Login Successful",
        "user_id": user.id,
        "email": user.email
    }
    