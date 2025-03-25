import datetime as dt

import fastapi
from fastapi import security

from utils import const
from utils import auth as auth_utils
from models import auth as auth_models

router = fastapi.APIRouter(tags=["authentication"])


@router.post("/token", response_model=auth_models.Token)
async def login_for_access_token(
    form_data: security.OAuth2PasswordRequestForm = fastapi.Depends(),
):
    user = auth_utils.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = dt.timedelta(minutes=const.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_utils.create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
