import logging
from firebase_admin import messaging
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.device import Device
from app.repositories.device import DeviceRepository
from app.schemas.notification import NotificationTestRequest

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.devices = DeviceRepository(db)
    
    async def send_to_user(
        self,
        user_id: int,
        payload: NotificationTestRequest
    ) -> dict:
        devices = await self.devices.get_all_for_user(user_id)
        active_devices = [
            device for device in devices if device.is_active
        ]
        
        if not active_devices:
            return {
                "total_devices": 0,
                "success_count": 0,
                "failure_count": 0,
                "message": "No active devices registered",
            }
        
        success_count = 0
        failure_count = 0
        
        for device in active_devices:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=payload.title,
                    body=payload.body
                ),
                data=payload.data or {},
                token=device.fcm_token
            )
            try:
                messaging.send(message)
                success_count+=1
            except messaging.UnregisteredError:
                failure_count+=1
                device.is_active =False
                
                logger.warning(
                    "Deactivated unregistered FCM token",
                    extra={
                        "device_id":device.id
                    }
                )
            except Exception:
                failure_count+=1
                logger.exception(
                    "Failed to send FCM notification",
                    extra={"device_id": device.id},
                )
        
        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise
        
        return {
            "total_devices": len(active_devices),
            "success_count": success_count,
            "failure_count": failure_count,
            "message": "Notification delivery attempt completed",
        }
        