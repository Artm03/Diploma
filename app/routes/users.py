from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app import db
from app.api import v1_user_registry_post as user_registry_api
from app.schemas import users


router = APIRouter()

@router.post('/v1/user/registry/')
async def v1_user_registry_post(user: users.UserCreate, conn: AsyncSession = Depends(db.get_db)):
    return await user_registry_api.handle(user=user, conn=conn)
