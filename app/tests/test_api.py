import io
from datetime import timedelta
from typing import NamedTuple

import pytest
from fastapi import UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from PIL import Image

from app.core.config import settings
from app.db.models import Album, Photo, User
from app.db.schemas import Token
from app.main import app
from app.tests.conftest import faker
from app.utils import create_access_token, get_password_hash


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


@pytest.fixture
def album(session, user):
    title = faker.name()
    description = faker.text()
    album = Album(title=title, description=description, owner_id=user.id)
    session.add(album)
    session.commit()
    session.refresh(album)
    return album


class TestUsersApi:

    def test_create_user(self, client):
        email = faker.email()
        password = faker.password()

        response = client.post(
            app.url_path_for("create_user_by_email"),
            json={
                "email": email,
                "password": password,
            },
        )
        data = response.json()
        assert response.status_code == 200 and data["email"] == email and "id" in data

    def test_get_user(self, client, user, token):
        response = client.get(
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

    def test_get_user_albums(self, client, album, user):
        response = client.get(
            app.url_path_for("get_user_albums_by_id"),
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

    def test_delete_album(self, client, token, album):
        response = client.delete(
            app.url_path_for("delete_album_by_id", album_id=album.id),
            headers={"Authorization": f"Bearer {token.access_token}"},
        )

        assert response.status_code == 204

    def test_update_album(self, client, user, token, album):
        new_title = faker.name()
        new_description = faker.text()
        is_display = faker.boolean()

        response = client.put(
            app.url_path_for("update_album_by_id", album_id=album.id),
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
    class FormData(NamedTuple):
        username: str
        password: str

    @pytest.fixture(autouse=True)
    def override_dependency_auth_form(self, user):
        def override_OAuth2PasswordRequestForm():
            return self.FormData(username=user.email, password=user.password)

        app.dependency_overrides[OAuth2PasswordRequestForm] = (
            override_OAuth2PasswordRequestForm
        )
        yield
        del app.dependency_overrides[OAuth2PasswordRequestForm]

    def test_login(self, client):
        response = client.post(app.url_path_for("login_for_access_token"))

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

    @pytest.fixture(autouse=True)
    def photo_in_db(self, session, user, binary_image):
        title = faker.file_name(category="image")
        photo = Photo(
            title=title,
            description=faker.text(),
            uploaded_by_id=user.id,
            file=UploadFile(
                filename=title,
                file=binary_image,
            ),
        )
        session.add(photo)
        session.commit()
        session.refresh(photo)
        return photo

    def test_create_photo(self, client, token, binary_image):
        multipart_form_data = {
            "title": (None, faker.name()),
            "description": (None, faker.text()),
            "file": (faker.file_name(category="image"), binary_image),
        }
        response = client.post(
            app.url_path_for("add_photo_to_current_user"),
            files=multipart_form_data,
            headers={"Authorization": f"Bearer {token.access_token}"},
        )

        assert (
            response.status_code == 200
            and response.json().get("title") == multipart_form_data["title"][-1]
        )

    def test_get_user_photos(self, client, token):
        response = client.get(
            app.url_path_for("read_current_user_photos"),
            headers={"Authorization": f"Bearer {token.access_token}"},
            params={"skip": 0, "limit": 100},
        )

        assert response.status_code == 200 and len(response.json()) == 1

    def test_delete_photo(self, session, client, token, photo_in_db):
        response = client.delete(
            app.url_path_for("delete_photo_by_id", photo_id=photo_in_db.id),
            headers={"Authorization": f"Bearer {token.access_token}"},
        )

        assert (
            response.status_code == 204 and session.get(Photo, photo_in_db.id) is None
        )

    def test_set_album_to_photo(self, session, client, token, album, photo_in_db):
        assert session.get(Photo, photo_in_db.id).album_id is None

        response = client.patch(
            app.url_path_for("patch_photo_album", photo_id=photo_in_db.id),
            headers={"Authorization": f"Bearer {token.access_token}"},
            params={"album_id": album.id},
        )

        assert (
            response.status_code == 200
            and session.get(Photo, photo_in_db.id).album_id == album.id
            and response.json().get("id") == photo_in_db.id
        )
