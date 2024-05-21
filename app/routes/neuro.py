import typing as tp

from fastapi import APIRouter, Depends, Response, Request, UploadFile, File
from sqlmodel.ext.asyncio.session import AsyncSession
from app.oauth2 import AuthJWT

from app import db
from app.schemas import users as users_models
from app.schemas import neuro as neuro_models
from app.api import detect_files, gallery_delete, gallery_post, gallery_put, upload_files
from app.api import upload_file
from app.api import images_get
from app.api import gallery_get
from app.utils import users


router = APIRouter()


@router.post('/api/v1/neuro/upload')
async def upload_images(
    pics: tp.List[UploadFile],
    names: tp.List[str],
    gallery_id: str,
    current_user: tp.Annotated[users_models.User, Depends(users.get_current_active_user)],
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
):
    return await upload_files.handle(pics=pics, gallery=gallery_id, names=names, current_user=current_user, conn=conn)


@router.post('/api/v1/neuro/detect')
async def detect_images(
    pics: tp.List[UploadFile],
    gallery_id: str,
    current_user: tp.Annotated[users_models.User, Depends(users.get_current_active_user)],
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
):
    return await detect_files.handle(pics=pics, gallery=gallery_id, current_user=current_user, conn=conn)


@router.post('/api/upload')
async def upload_image(
    pic: UploadFile,
    current_user: tp.Annotated[users_models.User, Depends(users.get_current_active_user)],
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
):
    return await upload_file.handle(pic=pic, current_user=current_user, conn=conn)


@router.get('/api/v1/images')
async def get_images(
    gallery_id: str,
    current_user: tp.Annotated[users_models.User, Depends(users.get_current_active_user)],
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
):
    return await images_get.handle(current_user=current_user, conn=conn, gallery_id=gallery_id)


@router.get('/api/v1/gallery')
async def get_galleries(
    current_user: tp.Annotated[users_models.User, Depends(users.get_current_active_user)],
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
    gallery_id: tp.Optional[str] = None,
):
    return await gallery_get.handle(gallery_id=gallery_id, current_user=current_user, conn=conn)


@router.post('/api/v1/gallery')
async def create_galleries(
    gallery: neuro_models.Gallery,
    current_user: tp.Annotated[users_models.User, Depends(users.get_current_active_user)],
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
):
    return await gallery_post.handle(gallery=gallery, current_user=current_user, conn=conn)


@router.put('/api/v1/gallery')
async def update_galleries(
    gallery: neuro_models.Gallery,
    current_user: tp.Annotated[users_models.User, Depends(users.get_current_active_user)],
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
):
    return await gallery_put.handle(gallery=gallery, current_user=current_user, conn=conn)


@router.delete('/api/v1/gallery')
async def delete_galleries(
    gallery_id: str,
    current_user: tp.Annotated[users_models.User, Depends(users.get_current_active_user)],
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
):
    return await gallery_delete.handle(gallery_id=gallery_id, current_user=current_user, conn=conn)
