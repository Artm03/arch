import typing as tp

import fastapi

from models import user as user_model
from utils import auth as auth_utils

router = fastapi.APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[fastapi.Depends(auth_utils.get_current_user)],
)


users_db: tp.List[user_model.User] = [
    user_model.User(
        id=1,
        username="admin",
        email="admin@example.com",
        name="Admin",
        surname="Admin",
        age=30,
    ),
]


# GET /users/validate-token - Проверить токен на корректность
@router.get("/validate-token")
def validate_token(
    current_user: dict = fastapi.Depends(auth_utils.get_current_user)
):
    return {"message": "OK"}


# GET /users - Получить всех пользователей
@router.get("/list", response_model=tp.List[user_model.User])
def get_users(
    login: tp.Optional[str] = fastapi.Query(
        None, description="Логин пользователя для поиска"
    ),
    name: tp.Optional[str] = fastapi.Query(
        None, description="Имя пользователя для поиска"
    ),
    surname: tp.Optional[str] = fastapi.Query(
        None, description="Фамилия пользователя для поиска"
    ),
    current_user: dict = fastapi.Depends(auth_utils.get_current_user),
):
    if login is not None:
        filtered_users = [user for user in users_db if user.username == login]
        if not filtered_users:
            raise fastapi.HTTPException(
                status_code=404, detail=f"User with login {login} not found"
            )
        return filtered_users

    if name is not None or surname is not None:
        # SQL запросами это конечно куда приятнее писать
        filtered_users = users_db.copy()

        if name is not None:
            filtered_users = [
                user for user in filtered_users if name.lower() in user.name.lower()
            ]

        if surname is not None:
            filtered_users = [
                user
                for user in filtered_users
                if surname.lower() in user.surname.lower()
            ]

        if not filtered_users:
            filter_description = []
            if name:
                filter_description.append(f"name containing '{name}'")
            if surname:
                filter_description.append(f"surname containing '{surname}'")

            filter_str = " and ".join(filter_description)
            raise fastapi.HTTPException(
                status_code=404, detail=f"Users with {filter_str} not found"
            )

    return users_db


# GET /users/details - Получить пользователя по ID
@router.get("/details", response_model=user_model.User)
def get_user(
    user_id: int, current_user: dict = fastapi.Depends(auth_utils.get_current_user)
):
    for user in users_db:
        if user.id == user_id:
            return user
    raise fastapi.HTTPException(status_code=404, detail="User not found")


# POST /users/create - Создать нового пользователя
@router.post("/create", response_model=user_model.User, status_code=201)
def create_user(
    user: user_model.UserCreate,
    current_user: dict = fastapi.Depends(auth_utils.get_current_user),
):
    for u in users_db:
        if u.username == user.username:
            raise fastapi.HTTPException(
                status_code=400, detail="Username already taken"
            )
        if u.email == user.email:
            raise fastapi.HTTPException(
                status_code=400, detail="Email already registered"
            )

    user_id = 1 if not users_db else max(u.id for u in users_db) + 1

    new_user = user_model.User(
        id=user_id,
        username=user.username,
        email=user.email,
        age=user.age,
        name=user.name,
        surname=user.surname,
    )

    hashed_password = auth_utils.get_password_hash(user.password)

    auth_utils.add_user_to_auth_db(
        username=user.username, email=user.email, hashed_password=hashed_password
    )

    users_db.append(new_user)

    return new_user


# PUT /users/update- Обновить пользователя по ID
@router.put("/update", response_model=user_model.User)
def update_user(
    user_id: int,
    user_update: user_model.UserBase,
    current_user: dict = fastapi.Depends(auth_utils.get_current_user),
):
    for index, user in enumerate(users_db):
        if user.id == user_id:
            updated_user = user_model.User(
                id=user_id,
                username=user_update.username,
                email=user_update.email,
                age=user_update.age,
            )
            users_db[index] = updated_user
            return updated_user
    raise fastapi.HTTPException(status_code=404, detail="User not found")


# DELETE /users/delete - Удалить пользователя по ID
@router.delete("/delete", response_model=user_model.User)
def delete_user(
    user_id: int, current_user: dict = fastapi.Depends(auth_utils.get_current_user)
):
    for index, user in enumerate(users_db):
        if user.id == user_id:
            deleted_user = users_db.pop(index)
            return deleted_user
    raise fastapi.HTTPException(status_code=404, detail="User not found")

