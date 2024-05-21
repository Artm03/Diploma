import os
import typing as tp

from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import UploadFile, status, Response
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import select, distinct
from sqlalchemy import func

from app.schemas import users as users_models
from app.schemas import neuro as neuro_models
from app import main


async def handle(
    gallery_id: tp.Optional[str],
    current_user: users_models.User,
    conn: AsyncSession,
):
    if not gallery_id:
        subquery = select(neuro_models.UsersImages.gallery_id, neuro_models.UsersImages.filename).distinct(neuro_models.UsersImages.gallery_id).order_by(neuro_models.UsersImages.gallery_id, neuro_models.UsersImages.created_at.desc()).subquery()
        galleries = (
            await conn.exec(
                select(
                    neuro_models.UserGallery.id,
                    neuro_models.UserGallery.name,
                    neuro_models.UserGallery.description,
                    subquery.c.filename,
                ).where(current_user.id == neuro_models.UserGallery.user_id).
                join(subquery, subquery.c.gallery_id == neuro_models.UserGallery.id, isouter=True)
            )
        ).fetchall()
        response = [
            {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "url": main.storage.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": "neurobucket", "Key": item.filename},
                    ExpiresIn=3600,
                ) if item.filename else None
            }
            for item in (galleries or [])
        ]
        return JSONResponse(status_code=200, content={"items": response})
    else:
        try:
            gallery = (
                await conn.exec(
                    select(
                        neuro_models.UserGallery.id,
                        neuro_models.UserGallery.name,
                        neuro_models.UserGallery.description,
                    ).where(
                        current_user.id == neuro_models.UserGallery.user_id,
                        neuro_models.UserGallery.id == gallery_id,
                    )
                )
            ).fetchone()
            response = {
                "id": gallery.id,
                "name": gallery.name,
                "description": gallery.description,
            }
            return JSONResponse(status_code=200, content=response)
        except Exception:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content="This gallery is not found",
            )
