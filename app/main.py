import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routes.ping import router as ping_routers
from app.routes.users import router as user_routers
from app.routes.email import router as email_routers
from app.routes.neuro import router as neuro_routers
from fastapi_storages import S3Storage
import boto3
from app.utils import get_file_by_path


storage = boto3.client(
    "s3",
    endpoint_url='https://storage.yandexcloud.net',
    use_ssl=True,
    aws_access_key_id=get_file_by_path(os.environ.get('AWS_ACCESS_KEY_ID')),
    aws_secret_access_key=get_file_by_path(os.environ.get('AWS_SECRET_ACCESS_KEY')),
)


app = FastAPI()

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
