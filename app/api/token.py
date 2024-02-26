import datetime

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import insert
from app.oauth2 import AuthJWT

import app.utils.email as email_utils
from app.schemas import users as users_model
from app.utils import users

from fastapi import HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse


async def handle(
    email_code: str,
    request: Request,
    form_data: OAuth2PasswordRequestForm,
    conn: AsyncSession,
    response: Response,
    Authorize: AuthJWT,
):
    code = await email_utils.get_email_code(conn=conn, email=form_data.username, code_type='login')
    if not code or code.code != email_code or code.expired_at < datetime.datetime.utcnow():
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

    response.set_cookie('refresh_token', refresh_token,
                        users.REFRESH_TOKEN_EXPIRE_MINUTES * 60, users.REFRESH_TOKEN_EXPIRE_MINUTES * 60, '/', None, False, True, 'lax')
    response.set_cookie('logged_in', 'True', users.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                        users.ACCESS_TOKEN_EXPIRE_MINUTES * 60, '/', None, False, False, 'lax')

    return users_model.Token(access_token=access_token, token_type="bearer")
