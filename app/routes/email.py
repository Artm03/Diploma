import typing as tp

from fastapi import BackgroundTasks, Depends
from fastapi import APIRouter, Body
from sqlmodel.ext.asyncio.session import AsyncSession

from app import db
from app.schemas.email import EmailSchema
from app.schemas import users as users_models
from app.api import email_registry
from app.api import email_login
from app.api import email_recovery


router = APIRouter()


@router.post("/api/v1/email/registry")
async def send_register(
    email: tp.Annotated[EmailSchema, Body()],
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
    background_tasks: BackgroundTasks,
):
    return await email_registry.handle(email=email, conn=conn, background_tasks=background_tasks)


@router.post("/api/v1/email/login")
async def send_login(
    user_request: tp.Annotated[users_models.UserAuthorize, Body()],
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
    background_tasks: BackgroundTasks,
):
    return await email_login.handle(user_request=user_request, conn=conn, background_tasks=background_tasks)


@router.post("/api/v1/email/recovery")
async def send_recovery(
    email: tp.Annotated[EmailSchema, Body()],
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
    background_tasks: BackgroundTasks,
):
    return await email_recovery.handle(email=email, conn=conn, background_tasks=background_tasks)
