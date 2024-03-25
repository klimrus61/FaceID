from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.crud import (
    change_photo_album,
    create_photo,
    delete_photo,
    get_photo,
    get_user_photos,
)
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
    return create_photo(session, photo=photo_in, owner=user)


@router.delete("/{photo_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo_by_id(
    photo_id: int,
    user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_db)],
):
    photo = get_photo(session, photo_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if not photo.owner == user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this photo",
        )
    delete_photo(session, photo)


@router.patch("/{photo_id}/set-album")
async def patch_photo_album(
    session: Annotated[Session, Depends(get_db)],
    photo_id: int,
    album_id: int,
):
    photo = get_photo(session, photo_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return change_photo_album(session, photo, album_id)
