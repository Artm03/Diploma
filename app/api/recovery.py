import datetime

from sqlmodel.ext.asyncio.session import AsyncSession

import app.utils.email as email_utils
from app.schemas import users as users_models
from app.utils import users

from fastapi import status, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy import update, delete
from sqlalchemy.util._collections import immutabledict


async def handle(
    form_data: users_models.UserLogin,
    conn: AsyncSession,
):
    code = await email_utils.get_email_code(conn=conn, email=form_data.username, code_type='recovery')
    if not code or code.code != form_data.email_code or code.expired_at < datetime.datetime.now(datetime.timezone.utc):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Incorrect or expired email code"},
        )
    user: users_models.User = await users.get_user_by_email(email=form_data.username, conn=conn)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"User with email {form_data.username} don't exists"},
        )
    await conn.exec(
        update(users_models.User).where(users_models.User.email == form_data.username),
        [
            {
                "password": users.get_password_hash(form_data.password)
            },
        ],
        execution_options=immutabledict({"synchronize_session": 'fetch'})
    )
    await conn.exec(delete(users_models.Sessions).where(users_models.Sessions.user_id == user.id))
    await conn.commit()
    return Response(status_code=status.HTTP_200_OK)
