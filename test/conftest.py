import os

import asyncio
from httpx import AsyncClient
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.db import get_db
from app.db_base import Base
from app.main import app


TEST_DATABASE_URL = os.environ.get("DATABASE_TEST_URL")
TEST_DB_NAME = os.environ.get("TEST_DB_NAME")
POSTGRES_DATABASE_URL = os.environ.get("POSTGRES_DATABASE_URL")


@pytest_asyncio.fixture(scope="session", autouse=True)
def event_loop() -> asyncio.AbstractEventLoop: # type: ignore
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    yield engine
    engine.sync_engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def prepare_db():
    create_db_engine = create_async_engine(
        POSTGRES_DATABASE_URL,
        isolation_level="AUTOCOMMIT",
        echo=True,
    )
    async with create_db_engine.begin() as connection:
        await connection.execute(
            text(
                "drop database if exists {name};".format(
                    name=TEST_DB_NAME
                )
            ),
        )
        await connection.execute(
            text("create database {name};".format(name=TEST_DB_NAME)),
        )


@pytest_asyncio.fixture(scope="session")
async def db_session_engine(engine):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
        TestingSessionLocal = sessionmaker(
            expire_on_commit=False,
            class_=AsyncSession,
            bind=connection,
        )
        async with TestingSessionLocal() as session:
            yield session
            await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_session_engine):
    yield db_session_engine


@pytest_asyncio.fixture(scope="function")
def override_get_db(prepare_db, db_session):
    async def _override_get_db():
        yield db_session

    return _override_get_db


@pytest_asyncio.fixture(scope="function")
async def async_client(override_get_db):
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test", follow_redirects=True) as ac:
        yield ac
