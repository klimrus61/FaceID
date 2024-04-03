import asyncio
import time

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.database import Base, get_db_session
from app.main import app

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{settings.POSTGRESQL_USERNAME}:{settings.POSTGRESQL_PASSWORD}@{settings.POSTGRESQL_HOSTNAME}:{settings.POSTGRESQL_PORT}/hr_test_db"

# engine = create_async_engine("sqlite+aiosqlite:///./test_db.sqlite")
engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def set_up_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(set_up_db())


@pytest.fixture
async def session():
    async with async_session() as session:
        yield session


@pytest.fixture
async def client(session):
    def override_get_db():
        yield session

    app.dependency_overrides[get_db_session] = override_get_db
    yield AsyncClient(app=app, base_url="http://testserver")
    del app.dependency_overrides[get_db_session]
