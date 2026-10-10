from fastapi import HTTPException, status
from sqlalchemy import select, update, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import UserRepository
from app.db.models.user import User
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from app.core.security import (
    generate_refresh_token,
    hash_refresh_token,
    create_access_token,
    verify_password,
)
from app.db.models.refresh_token import RefreshToken
from app.repositories.refresh_token import RefreshTokenRepository
from app.schemas.auth import TokenResponse
import uuid


class AuthService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)
        self.refresh_token_repository = RefreshTokenRepository(db)

    async def authenticate_user(self, email: str, password: str) -> User | None:
        user = await self.user_repository.get_by_email(email)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if user.password_hash is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        valid_password = verify_password(password, user.password_hash)

        if not valid_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return user

    async def issue_tokens(self, user) -> TokenResponse:
        raw_refresh_token = generate_refresh_token()
        token_hash = hash_refresh_token(raw_refresh_token)
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )

        try:
            access_token = create_access_token(user_id=user.id, role=user.role.value)
            family_id = uuid.uuid4()

            await self.refresh_token_repository.create(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=expires_at,
                family_id=family_id,
            )

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh_token,
            token_type="bearer",
        )

    async def refresh_tokens(self, raw_token: str) -> dict:
        token_hash = hash_refresh_token(raw_token)

        try:
            # First lookup: discover which family owns this token.
            initial_token = await self.refresh_token_repository.get_by_hash(token_hash)

            if initial_token is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                )

            # Serialize all operations for this family.
            await self._lock_refresh_family(initial_token.family_id)

            stored_token = await self.refresh_token_repository.get_by_hash_for_update(
                token_hash
            )

            now = datetime.now(timezone.utc)

            if stored_token is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                )

            # A previously consumed or revoked token must not be reused.
            if stored_token.revoked_at is not None:
                # A previously revoked token has been presented again.
                # Revoke every still-active token in this login session.
                await self.db.execute(
                    update(RefreshToken)
                    .where(
                        RefreshToken.family_id == stored_token.family_id,
                        RefreshToken.revoked_at.is_(None),
                    )
                    .values(revoked_at=now)
                )
                await self.db.commit()

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                )

            if stored_token.expires_at <= now:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                )

            # Lock the user row as well, so concurrent refreshes for
            # different sessions can consistently check user status.

            user_result = await self.db.execute(
                select(User).where(User.id == stored_token.user_id).with_for_update()
            )

            user = user_result.scalar_one_or_none()

            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                )

            new_raw_token = generate_refresh_token()
            new_hash = hash_refresh_token(new_raw_token)

            replacement = RefreshToken(
                user_id=user.id,
                token_hash=new_hash,
                expires_at=now + timedelta(days=settings.refresh_token_expire_days),
                family_id=stored_token.family_id,
            )

            self.db.add(replacement)

            # Get the replacement's database ID without committing yet.
            await self.db.flush()

            stored_token.revoked_at = now
            stored_token.replaced_by_id = replacement.id

            access_token = create_access_token(user_id=user.id, role=user.role.value)

            await self.db.commit()

            return {
                "access_token": access_token,
                "refresh_token": new_raw_token,
                "token_type": "bearer",
            }

        except Exception:
            await self.db.rollback()
            raise

    async def logout(self, raw_token: str) -> None:
        token_hash = hash_refresh_token(raw_token)

        try:
            stored_token = await self.refresh_token_repository.get_by_hash_for_update(
                token_hash=token_hash
            )

            if stored_token is not None:
                now = datetime.now(timezone.utc)

                await self.db.execute(
                    update(RefreshToken)
                    .where(
                        RefreshToken.family_id == stored_token.family_id,
                        RefreshToken.revoked_at.is_(None),
                    )
                    .values(revoked_at=now)
                )

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

    async def _lock_refresh_family(self, family_id: uuid.UUID) -> None:
        await self.db.execute(
            text("""
            SELECT pg_advisory_xact_lock(
                hashtextextended(:family_id, 0)
            )
            """),
            {"family_id": str(family_id)},
        )
