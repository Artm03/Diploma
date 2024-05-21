from app.oauth2 import AuthJWT

from fastapi import Response, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import delete

from app.schemas import users


async def handle(
    response: Response,
    user: users.User,
    Authorize: AuthJWT,
    conn: AsyncSession,
):
    conn.exec(delete(users.Sessions).where(users.Sessions.user_id == user.id))
    await conn.commit()

    Authorize.unset_jwt_cookies()
    return response
