from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Базовий декларативний клас для всіх SQLAlchemy 2.0 ORM моделей."""


engine: AsyncEngine = create_async_engine(
    settings.async_database_url,
    pool_pre_ping=True,
)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Генератор асинхронної сесії бази даних для залежностей FastAPI."""
    async with AsyncSessionLocal() as session:
        yield session
