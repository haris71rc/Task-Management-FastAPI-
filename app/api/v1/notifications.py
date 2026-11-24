from fastapi import APIRouter,Depends,status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_user,get_db
from app.db.models.user import User
from app.schemas.device import (
    DeviceDeleteResponse,
    DeviceRegisterRequest,
    DeviceResponse,
)
from app.services.device import DeviceService

from app.schemas.notification import NotificationTestRequest
from app.services.notification import NotificationService

router = APIRouter(
    prefix="/notifications",
    tags= ["Notifications"]
)

@router.post("/devices",response_model=DeviceResponse,status_code=status.HTTP_201_CREATED)
async def register_devices(
    payload: DeviceRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = DeviceService(db)
    return await service.register_device(
        payload=payload,
        user_id=current_user.id
    )
    
@router.get("/devices",response_model=list[DeviceResponse])
async def get_devices(current_user: User=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    service = DeviceService(db)
    return await service.get_user_devices(user_id=current_user.id)

@router.delete("/devices/{device_id}",response_model=DeviceDeleteResponse)
async def delete_device(
    device_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = DeviceService(db)
    
    await service.delete_device(device_id=device_id,user_id=current_user.id)
    
    return DeviceDeleteResponse(
        message="Device deleted successfully",
    )

@router.post("/test")
async def send_test_notification(
    payload: NotificationTestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = NotificationService(db)
    
    return await service.send_to_user(
        user_id=current_user.id,
        payload=payload
    )