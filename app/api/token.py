import datetime

from sqlmodel.ext.asyncio.session import AsyncSession

from app.schemas import users as users_model
from app.utils import users

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm


async def handle(
    form_data: OAuth2PasswordRequestForm,
    conn: AsyncSession
):
    user: users_model.User = await users.authenticate_user(conn, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = datetime.timedelta(minutes=users.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = users.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires,
    )
    return users_model.Token(access_token=access_token, token_type="bearer")
