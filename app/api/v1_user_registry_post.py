import datetime

from fastapi import status, Response
from fastapi.responses import JSONResponse

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import insert

import app.utils.email as email_utils
from app.schemas import users as users_model
from app.utils import users



async def handle(user: users_model.UserCreate, conn: AsyncSession):
    email_code = await email_utils.get_email_code(conn=conn, email=user.email, code_type='registry')
    if not email_code or email_code.code != user.email_code or email_code.expired_at < datetime.datetime.now(datetime.timezone.utc):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Incorrect or expired email code"},
        )

    get_user = await users.get_user_by_email(email=user.email, conn=conn)
    if get_user:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": f"User with email {user.email} already exists"},
        )

    await conn.exec(
        insert(users_model.User),
        [
            {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "password": users.get_password_hash(user.password),
            },
        ],
    )
    await conn.commit()

    return Response(status_code=status.HTTP_201_CREATED)
