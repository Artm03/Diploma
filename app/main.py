from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routes.ping import router as ping_routers
from app.routes.users import router as user_routers
from app.routes.email import router as email_routers
from app.routes.neuro import router as neuro_routers
from fastapi_storages import S3Storage


class PublicAssetS3Storage(S3Storage):
    AWS_ACCESS_KEY_ID = "YCAJEruKxQxS6NJaUksNavcx6"
    AWS_SECRET_ACCESS_KEY = "YCPzT5CGSCubYFR8ZuXxBvfT7blteqlhJz1-PV4q"
    AWS_S3_BUCKET_NAME = "neurobucket"
    AWS_S3_ENDPOINT_URL = "storage.yandexcloud.net"
    AWS_S3_USE_SSL = True


app = FastAPI()
storage = PublicAssetS3Storage()

origins = ["http://localhost:3000"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": str(exc.detail)},
    )


app.include_router(ping_routers)
app.include_router(user_routers)
app.include_router(email_routers)
app.include_router(neuro_routers)
