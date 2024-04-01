import tempfile

import pytest
from faker import Faker
from fastapi import UploadFile
from PIL import Image

from app.db.crud import create_photo, create_user, get_photo
from app.db.schemas import PhotoCreate, UserCreate

faker = Faker()


@pytest.fixture()
def default_photo():
    image = Image.new("RGB", (100, 100))
    tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg")
    image.save(tmp_file)
    tmp_file.seek(0)
    return tmp_file


@pytest.fixture()
def photo_uploaded_by(session):
    user = UserCreate(email=faker.email(), password=faker.password(length=12))
    return create_user(session, user)


@pytest.fixture()
def photo_in_db(session, photo_uploaded_by, default_photo):
    title = faker.file_name(category="image")
    photo = PhotoCreate(
        title=title,
        description=faker.text(max_nb_chars=25),
        file=UploadFile(filename=title, file=default_photo),  # noqa
    )
    return create_photo(session, photo, photo_uploaded_by)


# ============================================= Photo ===================================================


@pytest.mark.skip
class TestPhoto:
    def test_create_photo(self, session, default_photo, photo_uploaded_by):
        title = faker.file_name(category="image")
        description = faker.text()
        image = UploadFile(filename=title, file=default_photo)  # noqa

        photo = create_photo(
            session,
            PhotoCreate(title=title, description=description, file=image),
            uploaded_by=photo_uploaded_by,
        )
        assert hasattr(photo, "id") and photo.file.name == image.filename

    def test_get_photo(self, session, photo_in_db):
        photo = get_photo(session, photo_in_db.id)

        assert (
            photo.title == photo_in_db.title
            and photo.description == photo_in_db.description
        )


# ============================================= Photo ===================================================
