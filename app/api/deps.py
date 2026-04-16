from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.repositories.users import UserRepository
from app.repositories.chat_messages import ChatMessageRepository
from app.services.openrouter_client import OpenRouterClient
from app.usecases.auth import AuthUseCase
from app.usecases.chat import ChatUseCase
from app.core.security import decode_access_token
from app.core.errors import UnauthorizedError, NotFoundError


# OAuth2 схема для Swagger UI (кнопка "Authorize")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:

    async with AsyncSessionLocal() as session:
        yield session


async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:

    return UserRepository(db)


async def get_message_repository(
    db: AsyncSession = Depends(get_db),
) -> ChatMessageRepository:

    return ChatMessageRepository(db)


async def get_auth_usecase(
    user_repo: UserRepository = Depends(get_user_repository),
) -> AuthUseCase:

    return AuthUseCase(user_repo)


async def get_chat_usecase(
    message_repo: ChatMessageRepository = Depends(get_message_repository),
) -> ChatUseCase:

    llm_client = OpenRouterClient()
    return ChatUseCase(message_repo, llm_client)


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:

    try:
        payload = decode_access_token(token)
        user_id: int = int(payload.get("sub"))

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невалидный токен: отсутствует user_id",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id

    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось валидировать токен",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    auth_usecase: AuthUseCase = Depends(get_auth_usecase),
):

    try:
        user = await auth_usecase.get_user_profile(user_id)
        return user
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
