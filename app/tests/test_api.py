from dataclasses import dataclass
from datetime import timedelta
from typing import NamedTuple

import pytest
import pytest_asyncio
from faker import Faker

from app.core.config import settings
from app.db.models import User
from app.db.schemas import Token
from app.main import app
from app.utils import create_access_token, get_password_hash

faker = Faker()


class UserRawPassword(NamedTuple):
    id: int
    email: str
    hashed_password: str
    password: str
    is_active: bool


@pytest_asyncio.fixture
async def user(session):
    password = faker.password()
    user = User(email=faker.email(), hashed_password=get_password_hash(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return UserRawPassword(
        id=user.id,
        email=user.email,
        hashed_password=user.hashed_password,
        password=password,
        is_active=True,
    )


@pytest.fixture()
def token(user: UserRawPassword):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@pytest.fixture
def album(session, user: UserRawPassword):
    title = faker.name()
    description = faker.text()
    album = Album(title=title, description=description, owner_id=user.id)
    session.add(album)
    session.commit()
    session.refresh(album)
    return album


async def test_get_all_users(client, user: UserRawPassword):
    response = await client.get(app.url_path_for("get_all_users"))
    assert response.status_code == 200 and user.id == response.json()[0]["id"]
