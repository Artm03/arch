import contextlib
import json
import os

import fastapi
from fastapi import responses
from fastapi.middleware import cors

from api import user as user_api
from api import jwt as jwt_api


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    with open("openapi.json", "w") as f:
        json.dump(app.openapi(), f)

    yield


app = fastapi.FastAPI(
    title="User Management API",
    description="API для управления пользователями с JWT аутентификацией",
    version="1.0.0",
    lifespan=lifespan,
    openapi_url="/user-service/openapi.json"
)

app.add_middleware(
    cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jwt_api.router)
app.include_router(user_api.router)


@app.get("/", tags=["root"])
def read_root():
    return {"message": "Welcome to User Management API. Visit /docs for documentation."}


@app.get("/openapi.json", tags=["root"])
def get_operapi():
    return responses.FileResponse(os.path.join("/app", "openapi.json"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
