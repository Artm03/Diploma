import typing as tp
import datetime
import random

from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm.exc import NoResultFound


from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, MessageType
from sqlalchemy import insert, select, update
from sqlmodel.ext.asyncio.session import AsyncSession

import app.schemas.email as email_models

import app.schemas.email as email_models

from fastapi_mail import ConnectionConfig


conf = ConnectionConfig(
    MAIL_USERNAME="artyomrylit",
    MAIL_PASSWORD="jsrenfntzgpeapgg",
    MAIL_FROM="artyomrylit@yandex.ru",
    MAIL_PORT=465,
    MAIL_SERVER="smtp.yandex.ru",
    MAIL_FROM_NAME="Awesome Program",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


async def get_email_code(
    conn: AsyncSession, email: str, code_type: str
) -> tp.Optional[email_models.EmailSend]:
    try:
        email_code = (
            (
                await conn.exec(
                    select(email_models.EmailSend).where(
                        email_models.EmailSend.email == email,
                        email_models.EmailSend.type == code_type,
                    ),
                )
            )
            .scalars()
            .one()
        )
    except NoResultFound:
        email_code = None

    return email_code


def generate_code():
    return "".join([str(random.randint(0, 999)).zfill(3) for _ in range(2)])


async def send_code(
    email: email_models.EmailSchema,
    conn: AsyncSession,
    background_tasks: BackgroundTasks,
    code_type: str,
):
    email_code = await get_email_code(conn=conn, email=email.email, code_type=code_type)
    code = generate_code()
    while (
        await conn.exec(
            select(email_models.EmailSend).where(
                email_models.EmailSend.code == code,
                email_models.EmailSend.expired_at < datetime.datetime.now(),
            ),
        )
    ).fetchall():
        code = generate_code()

    html = f"""<p>Your {code_type} code is {code}</p> """
    if email_code:
        if email_code.created_at + datetime.timedelta(
            minutes=1
        ) > datetime.datetime.now(datetime.timezone.utc):
            return JSONResponse(
                status_code=400, content={"message": "please try later"}
            )
        await conn.exec(
            update(email_models.EmailSend).where(
                email_models.EmailSend.id == email_code.id
            ),
            [
                {
                    "created_at": datetime.datetime.now(datetime.timezone.utc),
                    "expired_at": (
                        datetime.datetime.now(datetime.timezone.utc)
                        + datetime.timedelta(minutes=10)
                    ),
                    "code": code,
                },
            ],
        )
        await conn.commit()
    else:
        await conn.exec(
            insert(email_models.EmailSend),
            [
                {
                    "email": email.email,
                    "type": code_type,
                    "code": code,
                    "created_at": datetime.datetime.now(datetime.timezone.utc),
                    "expired_at": (
                        datetime.datetime.now(datetime.timezone.utc)
                        + datetime.timedelta(minutes=10)
                    ),
                },
            ],
        )
        await conn.commit()

    message = MessageSchema(
        subject="Code for register",
        recipients=[email.email],
        body=html,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)

    background_tasks.add_task(fm.send_message, message)

    return JSONResponse(status_code=200, content={"message": "email has been sent"})
