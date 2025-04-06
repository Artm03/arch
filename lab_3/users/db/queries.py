import typing as tp

from sqlalchemy import future
from sqlalchemy.ext import asyncio

from models import user as user_models


async def get_user_by_username(username: str, conn: asyncio.AsyncSession) -> tp.Optional[user_models.UserDB]:
    query = future.select(user_models.UserDB).filter(user_models.UserDB.username == username)
    result = (await conn.execute(query)).scalars().first()
    return result


async def get_user_by_email(email: str, conn: asyncio.AsyncSession) -> tp.Optional[user_models.UserDB]:
    query = future.select(user_models.UserDB).filter(user_models.UserDB.email == email)
    result = (await conn.execute(query)).scalars().first()
    return result


async def get_user_by_id(id: int, conn: asyncio.AsyncSession) -> tp.Optional[user_models.UserDB]:
    query = future.select(user_models.UserDB).filter(user_models.UserDB.id == id)
    result = (await conn.execute(query)).scalars().first()
    return result
