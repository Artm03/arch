import os

from sqlalchemy.ext import asyncio
from sqlalchemy.ext import declarative
from sqlalchemy import orm


DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://stud:stud@db-users:5432/users_db")


engine = asyncio.create_async_engine(DATABASE_URL, echo=True)

async_session_local = orm.sessionmaker(
    bind=engine, class_=asyncio.AsyncSession, expire_on_commit=False
)

Base = declarative.declarative_base()

async def get_db() -> asyncio.AsyncSession:
    async with async_session_local() as session:
        yield session
