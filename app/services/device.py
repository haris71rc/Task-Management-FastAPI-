from fastapi import HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.device import Device,DevicePlatform as MobileDevicePlatform
from app.repositories.device import DeviceRepository
from app.schemas.device import DeviceRegisterRequest

class DeviceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.device = DeviceRepository(db)
    
    async def register_device(
      self,
      payload: DeviceRegisterRequest,
      user_id: int
    ) -> Device:
        device = await self.device.get_by_fcm_token(payload.fcm_token)
        
        if device is None:
            device = Device(
                user_id=user_id,
                fcm_token=payload.fcm_token,
                platform=MobileDevicePlatform(payload.platform.value),
                device_name=payload.device_name,
                is_active=True,
            )
            
            try:
                await self.device.create(device)
                await self.db.commit()
                await self.db.refresh(device)
            except Exception:
                await self.db.rollback()
                raise
            
            return device
        
        # The token already exists. Update its registration.
        # This also handles a device switching user accounts.
        
        device.user_id = user_id
        device.platform = MobileDevicePlatform(payload.platform.value)
        device.device_name = payload.device_name
        device.is_active = True
        
        try:
            await self.db.commit()
            await self.db.refresh(device)
        except Exception:
            await self.db.rollback()
            raise
        
        return device
    
    async def get_user_devices(self, user_id: int)->list[Device]:
        return await self.device.get_all_for_user(user_id)
    
    async def delete_device(self,device_id: int, user_id: int) -> None:
        device = await self.device.get_by_id_for_user(
            device_id=device_id,
            user_id=user_id
        )
        
        if device is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        try:
            await self.device.delete(device)
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise
            
            
        
        
        