import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.api.routes_auth import router as auth_router
from app.api.routes_chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Действие при старте: создание таблиц
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Действие при остановке: закрытие соединений
    await engine.dispose()


def create_app() -> FastAPI:
    # 1. Создание FastAPI с заголовком из конфига
    app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

    # 2. Добавление CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # 3. Подключение роутеров
    app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
    app.include_router(chat_router, prefix="/chat", tags=["Chat"])

    # 4. Технический endpoint GET /health
    @app.get("/health", tags=["Health"])
    async def health():
        return {"status": "ok", "app": settings.APP_NAME, "environment": settings.ENV}

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=(settings.ENV == "local")
    )
