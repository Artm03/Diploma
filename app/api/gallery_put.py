import os
import typing as tp

from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import UploadFile, status, Response
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import update

from app.schemas import users as users_models
from app.schemas import neuro as neuro_models
from app import main


async def handle(
    gallery: neuro_models.Gallery,
    current_user: users_models.User,
    conn: AsyncSession,
):
    try:
        await conn.exec(
            update(neuro_models.UserGallery).where(
                neuro_models.UserGallery.user_id == current_user.id,
                neuro_models.UserGallery.id == gallery.id,
            ),
            [
                {
                    "id": gallery.id,
                    "name": gallery.name,
                    "description": gallery.description,
                    "user_id": current_user.id,
                },
            ],
        )
        await conn.commit()
        return Response(status_code=200)
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content="Gallery with this id already exists",
        )
