import datetime

from sqlmodel.ext.asyncio.session import AsyncSession
from app.oauth2 import AuthJWT

from app.schemas import users as users_model
from app.utils import users

from fastapi import HTTPException, status, Response, Request


async def handle(
    conn: AsyncSession,
    response: Response,
    request: Request,
    Authorize: AuthJWT,
):
    try:
        Authorize.jwt_refresh_token_required()

        user_id = int(Authorize.get_jwt_subject())
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not refresh access token')
        user: users_model.User = await users.get_user_by_user_id(id=user_id, conn=conn)
        if not user or user.disabled:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='The user belonging to this token no logger exist')
        access_token = Authorize.create_access_token(
            subject=str(user.id), expires_time=datetime.timedelta(minutes=users.ACCESS_TOKEN_EXPIRE_MINUTES))
    except Exception as e:
        error = e.__class__.__name__
        if error == 'MissingTokenError':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Please provide refresh token')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    response.set_cookie('logged_in', 'True', users.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                        users.ACCESS_TOKEN_EXPIRE_MINUTES * 60, '/', None, False, False, 'lax')

    return users_model.Token(access_token=access_token, token_type="bearer")
