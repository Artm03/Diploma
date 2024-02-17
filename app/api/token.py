import datetime

from sqlmodel.ext.asyncio.session import AsyncSession
from app.oauth2 import AuthJWT

from app.schemas import users as users_model
from app.utils import users

from fastapi import HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm


async def handle(
    form_data: OAuth2PasswordRequestForm,
    conn: AsyncSession,
    response: Response,
    Authorize: AuthJWT,
):
    user: users_model.User = await users.authenticate_user(conn, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = Authorize.create_access_token(
        subject=str(user.id), expires_time=datetime.timedelta(minutes=users.ACCESS_TOKEN_EXPIRE_MINUTES))

    refresh_token = Authorize.create_refresh_token(
        subject=str(user.id), expires_time=datetime.timedelta(minutes=users.REFRESH_TOKEN_EXPIRE_MINUTES))

    response.set_cookie('refresh_token', refresh_token,
                        users.REFRESH_TOKEN_EXPIRE_MINUTES * 60, users.REFRESH_TOKEN_EXPIRE_MINUTES * 60, '/', None, False, True, 'lax')
    response.set_cookie('logged_in', 'True', users.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                        users.ACCESS_TOKEN_EXPIRE_MINUTES * 60, '/', None, False, False, 'lax')

    return users_model.Token(access_token=access_token, token_type="bearer")
