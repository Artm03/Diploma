import os
import uuid

from fastapi.responses import JSONResponse
from fastapi import status, UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession

from app.schemas import users as users_models
from app.schemas import neuro as neuro_models
from app import main

PATH_TO_DIR = os.environ.get("PATH_IMAGES")


async def handle(
    pic: UploadFile,
    current_user: users_models.User,
    conn: AsyncSession,
):
    try:
        path = PATH_TO_DIR + str(current_user.email) + '/'
        filename = uuid.uuid4().hex + '.png'
        file_path = path + filename
        main.storage.write(file=pic.file, name=file_path)
    except Exception as err:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=str(err),
        )
    return {"message": "File saved successfully"}
