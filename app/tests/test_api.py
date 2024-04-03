import io
from datetime import timedelta
from typing import NamedTuple

import pytest
import pytest_asyncio
from faker import Faker
from fastapi import UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from PIL import Image

from app.core.config import settings
from app.db.models import Album, Photo, User
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
    hashed_password = await get_password_hash(password)
    user = User(email=faker.email(), hashed_password=hashed_password)
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


@pytest_asyncio.fixture
async def token(user: UserRawPassword):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@pytest_asyncio.fixture
async def album(session, user: UserRawPassword):
    title = faker.name()
    description = faker.text()
    album = Album(title=title, description=description, owner_id=user.id)
    session.add(album)
    await session.commit()
    await session.refresh(album)
    return album


async def test_get_all_users(client, user: UserRawPassword):
    response = await client.get(app.url_path_for("get_all_users"))
    assert response.status_code == 200 and user.id == response.json()[0]["id"]


class TestUsersApi:
    async def test_create_user(self, client):
        email = faker.email()
        password = faker.password()

        response = await client.post(
            app.url_path_for("create_user_by_email"),
            json={
                "email": email,
                "password": password,
            },
        )
        data = response.json()
        assert response.status_code == 200 and data["email"] == email and "id" in data

    async def test_get_user(self, client, user: UserRawPassword, token: Token):
        response = await client.get(
            app.url_path_for("get_me"),
            headers={"Authorization": f"Bearer {token.access_token}"},
        )
        data = response.json()

        assert (
            response.status_code == 200
            and data["email"] == user.email
            and data["id"] == user.id
        )


class TestAlbumApi:

    async def test_get_user_albums(self, client, album, user: UserRawPassword):
        response = await client.get(
            app.url_path_for("get_user_albums_by_id"),
            params={
                "user_id": user.id,
                "skip": 0,
                "limit": 100,
            },
        )
        data = response.json()

        assert response.status_code == 200 and isinstance(data, list) and len(data) == 1

    async def test_create_album(self, client, user: UserRawPassword, token: Token):
        title = faker.name()
        description = faker.text()
        response = await client.post(
            app.url_path_for("create_album_to_user"),
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

    async def test_delete_album(self, client, token: Token, album: Album):
        response = await client.delete(
            app.url_path_for("delete_album_by_id", album_id=album.id),
            headers={"Authorization": f"Bearer {token.access_token}"},
        )

        assert response.status_code == 204

    async def test_update_album(
        self, client, user: UserRawPassword, token: Token, album: Album
    ):
        new_title = faker.name()
        new_description = faker.text()
        is_display = faker.boolean()

        response = await client.put(
            app.url_path_for("update_album_by_id", album_id=album.id),
            headers={"Authorization": f"Bearer {token.access_token}"},
            json={
                "title": new_title,
                "description": new_description,
                "is_display": is_display,
            },
        )
        data = response.json()

        assert response.status_code == 200 and data == {
            "id": album.id,
            "title": new_title,
            "description": new_description,
            "is_display": is_display,
            "owner_id": user.id,
        }


class TestLoginApi:
    class LoginFormData(NamedTuple):
        username: str
        password: str

    @pytest.fixture(autouse=True)
    def override_dependency_auth_form(self, user: UserRawPassword):
        def override_OAuth2PasswordRequestForm():
            return self.LoginFormData(username=user.email, password=user.password)

        app.dependency_overrides[OAuth2PasswordRequestForm] = (
            override_OAuth2PasswordRequestForm
        )
        yield
        del app.dependency_overrides[OAuth2PasswordRequestForm]

    async def test_login(self, client):
        response = await client.post(app.url_path_for("login_for_access_token"))

        assert response.status_code == 200
        token: Token = response.json()
        assert "access_token" in token


class TestPhotoApi:
    @pytest.fixture
    def binary_image(self):
        img = Image.new("RGB", (100, 100))
        in_memory = io.BytesIO()
        img.save(in_memory, format="PNG")
        return in_memory

    @pytest_asyncio.fixture(autouse=True)
    async def photo_in_db(
        self, session, user: UserRawPassword, binary_image: io.BytesIO
    ):
        title = faker.file_name(category="image")
        file = UploadFile(
            filename=title,
            file=binary_image,
        )
        photo = Photo(
            title=title,
            description=faker.text(),
            uploaded_by_id=user.id,
            file=file,
        )
        session.add(photo)
        await session.commit()
        await session.refresh(photo)
        return photo

    async def test_create_photo(self, client, token: Token, binary_image):
        multipart_form_data = {
            "title": (None, faker.name()),
            "description": (None, faker.text()),
            "file": (faker.file_name(category="image"), binary_image),
        }
        response = await client.post(
            app.url_path_for("add_photo_to_current_user"),
            files=multipart_form_data,
            headers={"Authorization": f"Bearer {token.access_token}"},
        )

        assert (
            response.status_code == 200
            and response.json().get("title") == multipart_form_data["title"][-1]
        )

    async def test_get_user_photos(self, client, token: Token):
        response = await client.get(
            app.url_path_for("read_current_user_photos"),
            headers={"Authorization": f"Bearer {token.access_token}"},
            params={"skip": 0, "limit": 100},
        )

        assert response.status_code == 200 and len(response.json()) == 1

    async def test_delete_photo(
        self, session, client, token: Token, photo_in_db: Photo
    ):
        response = await client.delete(
            app.url_path_for("delete_photo_by_id", photo_id=photo_in_db.id),
            headers={"Authorization": f"Bearer {token.access_token}"},
        )

        assert (
            response.status_code == 204
            and await session.get(Photo, photo_in_db.id) is None
        )

    async def test_set_album_to_photo(
        self, session, client, token: Token, album: Album, photo_in_db: Photo
    ):
        photo = await session.get(Photo, photo_in_db.id)
        assert photo.album_id is None

        response = await client.patch(
            app.url_path_for("patch_photo_album", photo_id=photo_in_db.id),
            headers={"Authorization": f"Bearer {token.access_token}"},
            params={"album_id": album.id},
        )
        photo = await session.get(Photo, photo_in_db.id)

        assert (
            response.status_code == 200
            and photo.album_id == album.id
            and response.json().get("id") == photo_in_db.id
        )
