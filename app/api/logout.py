from app.oauth2 import AuthJWT

from fastapi import Response, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import delete

from app.schemas import users


async def handle(
    response: Response,
    request: Request,
    Authorize: AuthJWT,
    conn: AsyncSession,
):
    # TO DO: Change logic for logout
    fingerprint = request.headers.get('X-Fingerprint-ID')
    conn.exec(delete(users.Sessions).where(users.Sessions.session_id == fingerprint))
    await conn.commit()
    Authorize.unset_jwt_cookies()
    response.set_cookie('logged_in', '', -1)

    return {'status': 'success'}
