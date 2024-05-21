import os
import typing as tp

from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import UploadFile, status, Response
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import select
from sqlalchemy import func

from app.schemas import users as users_models
from app.schemas import neuro as neuro_models
from app import main

PATH_TO_DIR = os.environ.get("PATH_IMAGES")


async def handle(
    gallery_id: str,
    current_user: users_models.User,
    conn: AsyncSession,
):
    user_id = current_user.id
    images = (
        await conn.exec(
            select(
                neuro_models.UsersImages.filename,
                neuro_models.UsersImages.id,
                neuro_models.UsersImages.created_at,
                func.array_agg(neuro_models.ImagesPeople.name).label("names"),
            )
            .where(user_id == neuro_models.UsersImages.user_id, gallery_id == neuro_models.UsersImages.gallery_id)
            .join(
                neuro_models.ImagesPeople,
                neuro_models.UsersImages.id == neuro_models.ImagesPeople.image_id,
            )
            .group_by(neuro_models.UsersImages.filename, neuro_models.UsersImages.id)
            .order_by(neuro_models.UsersImages.created_at.desc())
        )
    ).fetchall()
    response = []
    for image in images:
        # file = main.storage.get_object(Bucket='neurobucket', Key=image.filename).get('Body')
        item = {
            "url": main.storage.generate_presigned_url(
                "get_object",
                Params={"Bucket": "neurobucket", "Key": image.filename},
                ExpiresIn=3600,
            ),
            "names": image.names,
            "created_at": image.created_at.isoformat(),
        }
        response.append(item)
    return JSONResponse(status_code=200, content={"items": response})
