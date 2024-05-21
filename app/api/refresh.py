import datetime

from sqlmodel.ext.asyncio.session import AsyncSession
from app.oauth2 import AuthJWT

from app.schemas import users as users_model
from app.utils import users

from fastapi import HTTPException, status, Response, Request
from fastapi.responses import JSONResponse


async def handle(
    conn: AsyncSession,
    response: Response,
    request: Request,
    Authorize: AuthJWT,
):
    user_id: int
    try:
        Authorize.jwt_refresh_token_required()
        user_id = int(Authorize.get_jwt_subject())
    except Exception as e:
        error = e.__class__.__name__
        if error == 'MissingTokenError':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Please provide refresh token')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not refresh access token')
    user: users_model.User = await users.get_user_by_user_id(id=user_id, conn=conn)
    if not user or user.disabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='User does not exists')

    fingerprint = request.headers.get('X-Fingerprint-ID')
    if (fingerprint is None) or not (await users.authenticate_user_session(conn=conn, fingerprint=fingerprint, user_id=user_id)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='The user belonging to this token no longer exist')

    access_token = Authorize.create_access_token(
        subject=str(user.id), expires_time=datetime.timedelta(minutes=users.ACCESS_TOKEN_EXPIRE_MINUTES))

    return users_model.Token(access_token=access_token, token_type="bearer")
