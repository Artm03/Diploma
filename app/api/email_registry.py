from fastapi import BackgroundTasks
from sqlmodel.ext.asyncio.session import AsyncSession

import app.schemas.email as email_models
import app.utils.email as email_utils


async def handle(
    email: email_models.EmailSchema,
    conn: AsyncSession,
    background_tasks: BackgroundTasks,
):
    return await email_utils.send_code(email=email, conn=conn, background_tasks=background_tasks, code_type='registry')
