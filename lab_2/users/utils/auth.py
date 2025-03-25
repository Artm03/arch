import datetime as dt
import typing as tp

import fastapi
from fastapi import security
import jose
from jose import jwt
from passlib import context as passlib_context

from models import auth as auth_models
from utils import const

pwd_context = passlib_context.CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = security.OAuth2PasswordBearer(tokenUrl="token")

auth_users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "is_active": True,
    }
}


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    if username not in auth_users_db:
        return False
    user = auth_users_db[username]
    if not verify_password(password, user["hashed_password"]):
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


def add_user_to_auth_db(username: str, email: str, hashed_password: str):
    auth_users_db[username] = {
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "is_active": True,
    }


async def get_current_user(token: str = fastapi.Depends(oauth2_scheme)):
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

    if token_data.username not in auth_users_db:
        raise credentials_exception

    user = auth_users_db[token_data.username]
    if not user:
        raise credentials_exception
    return user
