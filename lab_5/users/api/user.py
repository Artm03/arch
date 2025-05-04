import typing as tp

import fastapi
from sqlalchemy import exc
from sqlalchemy import future
from sqlalchemy.ext import asyncio

from db import queries
from db import db as database
from db import redis as redis_cache
from models import user as user_model
from utils import auth as auth_utils


router = fastapi.APIRouter(
    prefix='/users',
    tags=['users'],
    dependencies=[fastapi.Depends(auth_utils.get_current_user)],
)


# GET /users/validate-token - Проверить токен на корректность
@router.get('/validate-token')
async def validate_token(
    current_user: user_model.UserDB = fastapi.Depends(auth_utils.get_current_user)
):
    return {'message': 'OK'}


# GET /users - Получить всех пользователей
@router.get('/list', response_model=user_model.UserListResponse)
async def get_users(
    login: tp.Optional[str] = None,
    name: tp.Optional[str] = None,
    surname: tp.Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: user_model.UserDB = fastapi.Depends(auth_utils.get_current_user),
    conn: asyncio.AsyncSession = fastapi.Depends(database.get_db),
):
    query = future.select(user_model.UserDB)

    if login is not None:
        query = query.filter(user_model.UserDB.username == login)

    if name is not None:
        query = query.filter(user_model.UserDB.name == name)

    if surname is not None:
        query = query.filter(user_model.UserDB.surname == surname)

    query = query.order_by(user_model.UserDB.id).limit(limit).offset(offset)
    result = await conn.execute(query)
    users = result.scalars().all()

    users_result = [
        user_model.UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            age=user.age,
            name=user.name,
            surname=user.surname,
        )
        for user in users
    ]

    return user_model.UserListResponse(
        items=users_result,
        limit=limit,
        offset=offset+limit,
    )


# GET /users/details - Получить пользователя по ID
@router.get('/details', response_model=user_model.UserResponse)
async def get_user(
    user_id: int,
    current_user: user_model.UserDB = fastapi.Depends(auth_utils.get_current_user),
    conn: asyncio.AsyncSession = fastapi.Depends(database.get_db),
):
    user = await queries.get_user_by_id(id=user_id, conn=conn)
    if not user:
        raise fastapi.HTTPException(status_code=404, detail='User not found')

    result = user_model.UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        age=user.age,
        name=user.name,
        surname=user.surname,
    )

    return result


# POST /users/create - Создать нового пользователя (с инвалидацией кеша)
@router.post('/create', response_model=user_model.UserResponse, status_code=201)
async def create_user(
    user: user_model.User,
    current_user: user_model.UserDB = fastapi.Depends(auth_utils.get_current_user),
    conn: asyncio.AsyncSession = fastapi.Depends(database.get_db),
    redis = fastapi.Depends(redis_cache.get_redis),
):
    existing_user = await queries.get_user_by_username(username=user.username, conn=conn)
    if existing_user:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail='Username already taken'
        )

    existing_user = await queries.get_user_by_email(email=user.email, conn=conn)
    if existing_user:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail='Email already registered'
        )

    new_user = user_model.UserDB(
        username=user.username,
        email=user.email,
        age=user.age,
        name=user.name,
        surname=user.surname,
        password=auth_utils.get_password_hash(user.password),
    )

    conn.add(new_user)
    await conn.commit()
    await conn.refresh(new_user)

    result = user_model.UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        age=new_user.age,
        name=new_user.name,
        surname=new_user.surname,
    )

    await redis_cache.invalidate_users_list_cache(redis)
    return result


# PUT /users/update - Обновить пользователя по ID (с инвалидацией кеша)
@router.put('/update', response_model=user_model.UserResponse)
async def update_user(
    user_id: int,
    user_update: user_model.UserBase,
    current_user: user_model.UserDB = fastapi.Depends(auth_utils.get_current_user),
    conn: asyncio.AsyncSession = fastapi.Depends(database.get_db),
    redis = fastapi.Depends(redis_cache.get_redis),
):
    user = await queries.get_user_by_id(id=user_id, conn=conn)
    if not user:
        raise fastapi.HTTPException(status_code=404, detail='User not found')
    user.username = user_update.username
    user.email = user_update.email
    user.name = user_update.name
    user.surname = user_update.surname
    user.age = user_update.age
    try:
        await conn.commit()
        await conn.refresh(user)
    except exc.IntegrityError:
        await conn.rollback()
        raise fastapi.HTTPException(
            status_code=400,
            detail='Username or email already exists'
        )

    result = user_model.UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        age=user.age,
        name=user.name,
        surname=user.surname,
    )

    await redis_cache.invalidate_user_cache(user_id, redis)
    await redis_cache.invalidate_users_list_cache(redis)

    return result


# DELETE /users/delete - Удалить пользователя по ID (с инвалидацией кеша)
@router.delete('/delete')
async def delete_user(
    user_id: int,
    current_user: user_model.UserDB = fastapi.Depends(auth_utils.get_current_user),
    conn: asyncio.AsyncSession = fastapi.Depends(database.get_db),
    redis = fastapi.Depends(redis_cache.get_redis),
):
    user = await queries.get_user_by_id(id=user_id, conn=conn)
    if not user:
        raise fastapi.HTTPException(status_code=404, detail='User not found')
    await conn.delete(user)
    await conn.commit()

    await redis_cache.invalidate_user_cache(user_id, redis)
    await redis_cache.invalidate_users_list_cache(redis)

    return {'message': 'ok'}


# GET /users/cached/list - Получить всех пользователей (с кешированием)
@router.get('/cached/list', response_model=user_model.UserListResponse)
async def get_users_cached(
    login: tp.Optional[str] = None,
    name: tp.Optional[str] = None,
    surname: tp.Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: user_model.UserDB = fastapi.Depends(auth_utils.get_current_user),
    conn: asyncio.AsyncSession = fastapi.Depends(database.get_db),
    redis = fastapi.Depends(redis_cache.get_redis),
):
    cached_users = await redis_cache.get_cached_users(login, name, surname, limit, offset, redis)
    if cached_users:
        return cached_users

    query = future.select(user_model.UserDB)

    if login is not None:
        query = query.filter(user_model.UserDB.username == login)

    if name is not None:
        query = query.filter(user_model.UserDB.name == name)

    if surname is not None:
        query = query.filter(user_model.UserDB.surname == surname)

    query = query.order_by(user_model.UserDB.id).limit(limit).offset(offset)
    result = await conn.execute(query)
    users = result.scalars().all()

    users_result = [
        user_model.UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            age=user.age,
            name=user.name,
            surname=user.surname,
        )
        for user in users
    ]

    response = user_model.UserListResponse(
        items=users_result,
        limit=limit,
        offset=offset+limit,
    )

    await redis_cache.cache_users(response, login, name, surname, limit, offset, redis)

    return response


# GET /users/cached/details - Получить пользователя по ID (с кешированием)
@router.get('/cached/details', response_model=user_model.UserResponse)
async def get_user_cached(
    user_id: int,
    current_user: user_model.UserDB = fastapi.Depends(auth_utils.get_current_user),
    conn: asyncio.AsyncSession = fastapi.Depends(database.get_db),
    redis = fastapi.Depends(redis_cache.get_redis),
):
    cached_user = await redis_cache.get_cached_user(user_id, redis)
    if cached_user:
        return cached_user

    user = await queries.get_user_by_id(id=user_id, conn=conn)
    if not user:
        raise fastapi.HTTPException(status_code=404, detail='User not found')

    result = user_model.UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        age=user.age,
        name=user.name,
        surname=user.surname,
    )

    await redis_cache.cache_user(result, redis)

    return result
