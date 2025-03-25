import typing as tp

import pydantic


class UserBase(pydantic.BaseModel):
    username: str
    email: pydantic.EmailStr
    name: str
    surname: str
    age: tp.Optional[int] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int


class UserInDB(User):
    hashed_password: str
