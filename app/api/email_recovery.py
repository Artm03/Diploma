from fastapi import BackgroundTasks, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

import app.schemas.email as email_models
import app.utils.email as email_utils
import app.utils.users as users_utils


async def handle(
    email: email_models.EmailSchema,
    conn: AsyncSession,
    background_tasks: BackgroundTasks,
):
    user = await users_utils.get_user_by_email(conn=conn, email=email.email)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"User with email {email.email} don't exists"},
        )
    return await email_utils.send_code(email=email, conn=conn, background_tasks=background_tasks, code_type='recovery')
