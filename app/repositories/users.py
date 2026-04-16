from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):

        self._db = db

    async def get_by_email(self, email: str) -> Optional[User]:

        stmt = select(User).where(User.email == email)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> Optional[User]:

        stmt = select(User).where(User.id == user_id)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, email: str, password_hash: str, role: str = "user") -> User:

        user = User(email=email, password_hash=password_hash, role=role)

        self._db.add(user)
        await self._db.commit()
        await self._db.refresh(user)

        return user
