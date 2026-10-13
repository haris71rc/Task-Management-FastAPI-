from datetime import datetime, timezone
from fastapi import Depends
from sqlalchemy import select
from app.db.database import AsyncSessionLocal,AsyncSession 
from app.db.models.outbox_event import OutboxEvent
from app.tasks.notifications import send_task_created_notification
from app.dependencies import get_db

async def dispatch_outbox_batch(db: AsyncSession= Depends(get_db)) ->int:
    published_count= 0
    try:
        result = await db.execute(
            select(OutboxEvent).where(OutboxEvent.published_at.is_(None)).order_by(OutboxEvent.created_at).limit(50).with_for_update(skip_locked=True)
        )
        
        events = result.scalars().all()
        
        for event in events:
            if event.event_type != "project.created":
                event.last_error = "Unsupported event type"
                continue
            
            try:
                send_task_created_notification.apply_async(
                    kwargs={
                        "project_id": event.payload["project_id"],
                        "recipient_email": (
                                event.payload["recipient_email"]
                            ),
                    },
                    task_id=str(event.id)
                )
                event.published_at=datetime.now(timezone.utc)
                event.last_error=None
                published_count+=1
            
            except Exception as exp:
                event.last_error = str(exp)[:2000]
        await db.commit()
    
    except Exception:
        await db.rollback()
        raise
    
    return published_count
    
    