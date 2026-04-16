from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ChatRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="Текст запроса пользователя к LLM",
        examples=["Расскажи о языке Python"],
    )

    system: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Системная инструкция для модели (опционально)",
        examples=["Ты - опытный программист на Python"],
    )

    max_history: int = Field(
        default=10,
        ge=0,
        le=50,
        description="Количество предыдущих сообщений для контекста",
        examples=[10],
    )

    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Температура модели: 0 = детерминированный, 2 = очень креативный",
        examples=[0.7],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": "Что такое FastAPI?",
                    "system": "Ты - эксперт по веб-разработке",
                    "max_history": 5,
                    "temperature": 0.7,
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    answer: str = Field(
        ...,
        description="Ответ языковой модели",
        examples=["FastAPI - это современный веб-фреймворк для Python..."],
    )

    suggested_questions: list[str] = Field(
        default_factory=list,
        max_length=2,
        description="Предложенные варианты следующих вопросов",
        examples=[
            [
                "Расскажи подробнее о маршрутизации в FastAPI",
                "Как работает зависимость Depends в FastAPI",
            ]
        ],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "answer": "FastAPI - это современный, быстрый веб-фреймворк для создания API на Python 3.7+.",
                    "suggested_questions": [
                        "Расскажи подробнее о валидации данных в FastAPI",
                        "Как настроить асинхронные эндпоинты в FastAPI",
                    ],
                }
            ]
        }
    }


class ChatMessagePublic(BaseModel):
    id: int = Field(..., description="ID сообщения", examples=[1])
    role: str = Field(..., description="Роль: user или assistant", examples=["user"])
    content: str = Field(
        ..., description="Текст сообщения", examples=["Что такое FastAPI?"]
    )
    created_at: datetime = Field(..., description="Время создания сообщения")

    model_config = ConfigDict(from_attributes=True)


class ClearHistoryResponse(BaseModel):
    deleted_count: int = Field(
        ..., description="Количество удалённых сообщений", examples=[15]
    )
    message: str = Field(
        ...,
        description="Сообщение об успешной операции",
        examples=["История чата очищена"],
    )
