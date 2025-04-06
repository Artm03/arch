import typing as tp

import pydantic
import sqlalchemy
from sqlalchemy.ext import declarative


Base = declarative.declarative_base()

class UserBase(pydantic.BaseModel):
    username: str
    email: pydantic.EmailStr
    name: str
    surname: str
    age: tp.Optional[int] = None


class User(UserBase):
    password: str


class UserResponse(UserBase):
    id: int


class UserListResponse(pydantic.BaseModel):
    items: tp.List[UserResponse]
    limit: int
    offset: int


class UserDB(Base):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, index=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False, index=True)
    password = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
