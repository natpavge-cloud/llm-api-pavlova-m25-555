from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings


# Формирование строки подключения к SQLite с асинхронным драйвером
DATABASE_URL = f"sqlite+aiosqlite:///{settings.SQLITE_PATH}"

# Создание асинхронного engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True
    if settings.ENV == "local"
    else False,  # Логирование SQL запросов в dev режиме
    future=True,
)

# Фабрика для создания асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Объекты остаются доступными после commit
    autocommit=False,
    autoflush=False,
)
