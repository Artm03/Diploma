import datetime

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import insert
from app.oauth2 import AuthJWT

import app.utils.email as email_utils
from app.schemas import users as users_model
from app.utils import users

from fastapi import HTTPException, status, Response, Request
from fastapi.responses import JSONResponse


async def handle(
    request: Request,
    form_data: users_model.UserLogin,
    conn: AsyncSession,
    response: Response,
    Authorize: AuthJWT,
):
    code = await email_utils.get_email_code(conn=conn, email=form_data.username, code_type='login')
    if not code or code.code != form_data.email_code or code.expired_at < datetime.datetime.now(datetime.timezone.utc):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Incorrect or expired email code"},
        )
    user: users_model.User = await users.authenticate_user(conn, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    fingerprint = request.headers.get('X-Fingerprint-ID')
    if not fingerprint:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect session",
        )
    session = await users.authenticate_user_session(conn=conn, fingerprint=fingerprint, user_id=user.id)
    if not session:
        await conn.exec(
            insert(users_model.Sessions),
            [
                {
                    "user_id": user.id,
                    "session_id": fingerprint,
                },
            ],
        )
        await conn.commit()

    access_token = Authorize.create_access_token(
        subject=str(user.id), expires_time=datetime.timedelta(minutes=users.ACCESS_TOKEN_EXPIRE_MINUTES))

    refresh_token = Authorize.create_refresh_token(
        subject=str(user.id), expires_time=datetime.timedelta(minutes=users.REFRESH_TOKEN_EXPIRE_MINUTES))

    response.set_cookie(key='refresh_token', value=refresh_token, max_age=users.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
                        expires=users.REFRESH_TOKEN_EXPIRE_MINUTES * 60, secure=False, httponly=True)

    return users_model.Token(access_token=access_token, token_type="bearer")
