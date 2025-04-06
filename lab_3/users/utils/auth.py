import datetime as dt
import typing as tp

import fastapi
from fastapi import security
import jose
from jose import jwt
from passlib import context as passlib_context
from sqlalchemy.ext import asyncio

from db import db as database
from db import queries
from models import auth as auth_models
from models import user as user_models
from utils import const


pwd_context = passlib_context.CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = security.OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(username: str, password: str, conn: asyncio.AsyncSession):
    user: user_models.UserDB = await queries.get_user_by_username(username=username, conn=conn)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: tp.Optional[dt.timedelta] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = dt.datetime.now(dt.timezone.utc) + expires_delta
    else:
        expire = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, const.SECRET_KEY, algorithm=const.ALGORITHM
    )

    return encoded_jwt


async def get_current_user(
    conn: asyncio.AsyncSession = fastapi.Depends(database.get_db),
    token: str = fastapi.Depends(oauth2_scheme),
) -> user_models.UserDB:
    credentials_exception = fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, const.SECRET_KEY, algorithms=[const.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = auth_models.TokenData(username=username)
    except jose.JWTError:
        raise credentials_exception

    user: user_models.UserDB = await queries.get_user_by_username(username=token_data.username, conn=conn)
    if not user:
        raise credentials_exception

    if not user:
        raise credentials_exception
    return user
