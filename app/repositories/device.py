from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.device import Device

class DeviceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_fcm_token(self,fcm_token:str) -> Device|None:
        stmt = select(Device).where(Device.fcm_token == fcm_token)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_id_for_user(self, device_id: int ,user_id: int) -> Device|None:
        stmt = select(Device).where(Device.user_id == user_id, Device.id == device_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all_for_user(self,user_id:int) -> list[Device]:
        stmt = select(Device).where(Device.user_id == user_id).order_by(Device.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def create(self, device: Device)-> Device:
        self.db.add(device)
        await self.db.flush()
        return device
    
    async def delete(self,device:Device)->None:
        await self.db.delete(device)
        
        
        
        