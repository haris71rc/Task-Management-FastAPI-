from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.refresh_token import RefreshToken
from sqlalchemy import select

class RefreshTokenRepository:
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create(
        self,
        user_id: int,
        token_hash: str,
        expires_at: datetime
    ) -> RefreshToken:
        
        token = RefreshToken(
            user_id= user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        
        self.db.add(token)
        self.db.flush()
        
        return token
     
    async def get_by_hash_for_update(self,token_hash:str)->RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash).with_for_update()
        
        result = await self.db.execute(stmt)
        
        return result.scalar_one_or_none()
           
        