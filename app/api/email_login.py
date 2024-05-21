from fastapi import BackgroundTasks, status, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from app.schemas import users as users_models
import app.schemas.users as users_model
import app.schemas.email as email_models
import app.utils.email as email_utils
import app.utils.users as users_utils


async def handle(
    user_request: users_models.UserAuthorize,
    conn: AsyncSession,
    background_tasks: BackgroundTasks,
):
    user: users_model.User = await users_utils.authenticate_user(conn, user_request.username, user_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await email_utils.send_code(email=email_models.EmailSchema(email=user_request.username), conn=conn, background_tasks=background_tasks, code_type='login')
