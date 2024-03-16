import typing as tp

from fastapi import APIRouter, Depends, Response, Request, UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession
from app.oauth2 import AuthJWT

from app import db
from app.schemas import users as users_models
from app.schemas import neuro as neuro_models
from app.api import upload_files
from app.api import upload_file
from app.utils import users


router = APIRouter()


@router.post('/api/v1/neuro/upload')
async def upload_images(
    pics: tp.List[neuro_models.FileWithName],
    current_user: tp.Annotated[users_models.User, Depends(users.get_current_active_user)],
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
):
    return await upload_files.handle(pics=pics, current_user=current_user, conn=conn)


@router.post('/api/upload')
async def upload_images(
    pic: UploadFile,
    current_user: tp.Annotated[users_models.User, Depends(users.get_current_active_user)],
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
):
    return await upload_file.handle(pic=pic, current_user=current_user, conn=conn)
