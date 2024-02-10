from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import select

from app.schemas import users


async def get_user_by_email(email: str, conn: AsyncSession):
    query = select(users.User.email, users.User.first_name, users.User.last_name).where(users.User.email == email)
    res = (await conn.exec(query)).all()
    return res[0] if res else None
