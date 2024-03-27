from datetime import timedelta
from typing import NamedTuple

import pytest
from faker import Faker

from app.core.config import settings
from app.db.models import Album, User
from app.db.schemas import Token, UserCreate
from app.utils import create_access_token, get_password_hash

faker = Faker()

api_url = settings.API_V1_STR


class UserRawPassword(NamedTuple):
    id: int
    email: str
    hashed_password: str
    password: str


@pytest.fixture()
def user(session):
    password = faker.password()
    user = User(email=faker.email(), hashed_password=get_password_hash(password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserRawPassword(
        id=user.id,
        email=user.email,
        hashed_password=user.hashed_password,
        password=password,
    )


@pytest.fixture()
def token(user):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


class TestUsersApi:

    def test_create_user(self, client):
        email = faker.email()
        password = faker.password()

        response = client.post(
            f"{api_url}/users/create",
            json={
                "email": email,
                "password": password,
            },
        )
        data = response.json()
        assert response.status_code == 200 and data["email"] == email and "id" in data

    def test_get_user(self, client, user, token):
        response = client.get(
            f"{api_url}/users/me",
            headers={"Authorization": f"Bearer {token.access_token}"},
        )
        data = response.json()

        assert (
            response.status_code == 200
            and data["email"] == user.email
            and data["id"] == user.id
        )


class TestAlbumApi:
    @pytest.fixture()
    def album(self, session, user):
        title = faker.name()
        description = faker.text()
        album = Album(title=title, description=description, owner_id=user.id)
        session.add(album)
        session.commit()
        session.refresh(album)
        return album

    def test_get_user_albums(self, client, album, user):
        response = client.get(
            f"{api_url}/albums",
            params={
                "user_id": user.id,
                "skip": 0,
                "limit": 100,
            },
        )
        data = response.json()

        assert response.status_code == 200 and isinstance(data, list) and len(data) == 1

    def test_create_album(self, client, user, token):
        title = faker.name()
        description = faker.text()
        response = client.post(
            f"{api_url}/albums/create",
            headers={"Authorization": f"Bearer {token.access_token}"},
            json={
                "title": title,
                "description": description,
            },
        )
        data = response.json()

        assert (
            response.status_code == 201
            and data["title"] == title
            and data["owner_id"] == user.id
        )

    def test_delete_album(self, client, token, album):
        response = client.delete(
            f"{api_url}/albums/{album.id}/delete",
            headers={"Authorization": f"Bearer {token.access_token}"},
        )

        assert response.status_code == 204

    def test_update_album(self, client, user, token, album):
        new_title = faker.name()
        new_description = faker.text()
        is_display = faker.boolean()

        response = client.put(
            f"{api_url}/albums/{album.id}/update",
            headers={"Authorization": f"Bearer {token.access_token}"},
            json={
                "title": new_title,
                "description": new_description,
                "is_display": is_display,
            },
        )
        data = response.json()

        assert (
            response.status_code == 200
            and data["title"] == new_title
            and data["description"] == new_description
            and data["is_display"] == is_display
            and data["owner_id"] == user.id
        )


class TestLoginApi:
    pass


class TestPhotoApi:
    pass
