import json
import os

import fastapi
from fastapi import responses
from fastapi.middleware import cors
import contextlib

from api import product


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    print("Products service starting...")
    with open("openapi.json", "w") as f:
        json.dump(app.openapi(), f)

    yield

    print("Products service shutting down...")


app = fastapi.FastAPI(
    title="Product Catalog API",
    description="API для управления каталогом товаров",
    version="1.0.0",
    lifespan=lifespan,
    openapi_url="/product-service/openapi.json"
)

app.add_middleware(
    cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product.router)


@app.get("/", tags=["root"])
def read_root():
    return {"message": "Welcome to Product Catalog API. Visit /docs for documentation."}


@app.get("/openapi.json", tags=["root"])
def get_operapi():
    return responses.FileResponse(os.path.join("/app", "openapi.json"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
