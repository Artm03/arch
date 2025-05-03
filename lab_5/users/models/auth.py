import typing as tp

import pydantic


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str


class TokenData(pydantic.BaseModel):
    username: tp.Optional[str] = None
