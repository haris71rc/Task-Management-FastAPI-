from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.processed_event import ProcessedEvent
from sqlalchemy.dialects.postgresql import insert


async def claim_event(db: AsyncSession, idempotency_key: str) -> bool:
    stmt = (
        insert(ProcessedEvent)
        .values(idempotency_key=idempotency_key)
        .on_conflict_do_nothing(
            index_elements=["idempotency_key"]
        )
        .returning(ProcessedEvent.id)
    )
    
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None