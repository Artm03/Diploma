from fastapi.responses import JSONResponse
from fastapi import status, Response
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import delete

from app.schemas import users as users_models
from app.schemas import neuro as neuro_models


async def handle(
    gallery_id: str,
    current_user: users_models.User,
    conn: AsyncSession,
):
    try:
        await conn.exec(
            delete(neuro_models.UserGallery).where(
                neuro_models.UserGallery.user_id == current_user.id,
                neuro_models.UserGallery.id == gallery_id,
            )
        )
        await conn.commit()
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Gallery not found",
        )

    return Response(status_code=200)
