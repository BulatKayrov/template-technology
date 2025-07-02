from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.conf import settings

async_engine = create_async_engine(url=settings.sqlite_url)
Session = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
    class_=AsyncSession,
)


async def get_session():
    async with Session() as session:
        yield session
