from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, LogoutRequest
from app.services.auth import AuthService
from app.dependencies import get_db


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

@router.post("/login",status_code=status.HTTP_200_OK, response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    
    user = await service.authenticate_user(
        email=payload.email,
        password=payload.password
    )
    
    return await service.issue_tokens(user)

@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    return await service.refresh_tokens(
        raw_token= payload.refresh_token
    )

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: LogoutRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db) 
    
    await service.logout(payload.refresh_token)  
    return None