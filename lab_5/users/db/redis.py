import json
import typing as tp
import os

import redis.asyncio as redis
import fastapi

from models import user

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_client = None

USER_DETAILS_TTL = 60 * 10  # 10 минут
USERS_LIST_TTL = 60 * 5  # 5 минут


async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    return redis_client

async def close_redis_connection():
    global redis_client
    if redis_client is not None:
        await redis_client.aclose()
        redis_client = None



def user_details_key(user_id: int) -> str:
    return f"user:details:{user_id}"

def users_list_key(login: tp.Optional[str] = None, name: tp.Optional[str] = None, 
                 surname: tp.Optional[str] = None, limit: int = 50, offset: int = 0) -> str:
    params = f"login:{login or 'None'}:name:{name or 'None'}:surname:{surname or 'None'}:limit:{limit}:offset:{offset}"
    return f"users:list:{params}"


def serialize_user(user: user.UserResponse) -> str:
    return json.dumps(user.model_dump())


def deserialize_user(user_data: str) -> user.UserResponse:
    data = json.loads(user_data)
    return user.UserResponse(**data)


def serialize_user_list(users: user.UserListResponse) -> str:\
    return json.dumps(users.model_dump())


def deserialize_user_list(users_data: str) -> user.UserListResponse:
    data = json.loads(users_data)
    return user.UserListResponse(**data)


async def get_cached_user(user_id: int, redis=fastapi.Depends(get_redis)) -> tp.Optional[user.UserResponse]:
    key = user_details_key(user_id)
    data = await redis.get(key)
    if data:
        return deserialize_user(data)
    return None


async def cache_user(user: user.UserResponse, redis=fastapi.Depends(get_redis)) -> None:
    key = user_details_key(user.id)
    await redis.set(key, serialize_user(user), ex=USER_DETAILS_TTL)


async def get_cached_users(login: tp.Optional[str] = None, name: tp.Optional[str] = None,
                          surname: tp.Optional[str] = None, limit: int = 50, offset: int = 0,
                          redis=fastapi.Depends(get_redis)) -> tp.Optional[user.UserListResponse]:
    key = users_list_key(login, name, surname, limit, offset)
    data = await redis.get(key)
    if data:
        return deserialize_user_list(data)
    return None


async def cache_users(users: user.UserListResponse, login: tp.Optional[str] = None, 
                     name: tp.Optional[str] = None, surname: tp.Optional[str] = None, 
                     limit: int = 50, offset: int = 0, redis=fastapi.Depends(get_redis)) -> None:
    key = users_list_key(login, name, surname, limit, offset)
    await redis.set(key, serialize_user_list(users), ex=USERS_LIST_TTL)


async def invalidate_user_cache(user_id: int, redis=fastapi.Depends(get_redis)) -> None:
    key = user_details_key(user_id)
    await redis.delete(key)

    await invalidate_users_list_cache(redis)


async def invalidate_users_list_cache(redis=fastapi.Depends(get_redis)) -> None:
    pattern = "users:list:*"
    cursor = 0
    while True:
        cursor, keys = await redis.scan(cursor, pattern, 100)
        if keys:
            await redis.delete(*keys)
        if cursor == 0:
            break
