from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_chat_usecase, get_current_user_id, get_message_repository
from app.usecases.chat import ChatUseCase
from app.repositories.chat_messages import ChatMessageRepository
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatMessagePublic,
    ClearHistoryResponse,
)
from app.core.errors import ExternalServiceError


router = APIRouter(tags=["Чат"])


@router.post("", response_model=ChatResponse)
async def ask_llm(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    chat_usecase: ChatUseCase = Depends(get_chat_usecase),
):

    try:
        result = await chat_usecase.ask_llm(
            user_id=user_id,
            prompt=request.prompt,
            system=request.system,
            max_history=request.max_history,
            temperature=request.temperature,
        )
        return result
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ошибка внешнего сервиса: {e.message}",
        )


@router.get("/history", response_model=List[ChatMessagePublic])
async def get_history(
    user_id: int = Depends(get_current_user_id),
    message_repo: ChatMessageRepository = Depends(get_message_repository),
):

    messages = await message_repo.get_recent_messages(user_id, limit=100)
    return messages


@router.delete("/history", response_model=ClearHistoryResponse)
async def clear_history(
    user_id: int = Depends(get_current_user_id),
    chat_usecase: ChatUseCase = Depends(get_chat_usecase),
):

    deleted_count = await chat_usecase.clear_history(user_id)
    return {"deleted_count": deleted_count, "message": "История чата очищена"}
