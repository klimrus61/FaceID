from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.crud import create_photo, get_user_photos
from app.db.database import get_db
from app.db.schemas import Photo, PhotoCreate, User

router = APIRouter()


@router.get("/")
async def read_current_user_photos(
    session: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_active_user)],
    skip: int = 0,
    limit: int = 100,
):
    return get_user_photos(session, user, skip, limit)


@router.post("/create", response_model=Photo)
async def add_photo_to_current_user(
    session: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_active_user)],
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
):
    photo_in = PhotoCreate(title=title, description=description, file=file)
    photo = create_photo(session, photo=photo_in, owner=user)
    return photo
