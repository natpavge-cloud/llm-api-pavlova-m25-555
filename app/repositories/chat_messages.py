from typing import List
from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChatMessage


class ChatMessageRepository:
    def __init__(self, db: AsyncSession):

        self._db = db

    async def add_message(self, user_id: int, role: str, content: str) -> ChatMessage:

        message = ChatMessage(user_id=user_id, role=role, content=content)

        self._db.add(message)
        await self._db.commit()
        await self._db.refresh(message)

        return message

    async def get_recent_messages(self, user_id: int, limit: int) -> List[ChatMessage]:

        # Получаем последние N сообщений в обратном порядке
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(desc(ChatMessage.created_at))
            .limit(limit)
        )

        result = await self._db.execute(stmt)
        messages = list(result.scalars().all())

        # Разворачиваем, чтобы получить хронологический порядок (от старых к новым)
        messages.reverse()

        return messages

    async def delete_user_history(self, user_id: int) -> int:

        stmt = delete(ChatMessage).where(ChatMessage.user_id == user_id)
        result = await self._db.execute(stmt)
        await self._db.commit()

        return result.rowcount
