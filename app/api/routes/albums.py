from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.crud import (
    create_album,
    delete_album,
    get_album,
    get_user_albums,
    update_album,
)
from app.db.database import get_db
from app.db.schemas import Album, AlbumCreate, AlbumUpdate, User

router = APIRouter()


@router.get("/")
async def get_user_albums_by_id(
    session: Annotated[Session, Depends(get_db)],
    user_id: int,
    skip: int = 0,
    limit: int = 100,
):
    return get_user_albums(session, user_id, skip, limit)


@router.post("/create")
async def create_album_to_user(
    session: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_active_user)],
    album: AlbumCreate,
):
    return create_album(session, owner=user, album=album)


@router.delete("/{album_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_album_by_id(
    session: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_active_user)],
    album_id: int,
):
    album = get_album(session, album_id)
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if not album.owner == user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this photo",
        )
    delete_album(session, album)


@router.put("/{album_id}/update")
async def update_album_by_id(
    session: Annotated[Session, Depends(get_db)],
    album_id: int,
    user: Annotated[User, Depends(get_current_active_user)],
    album_update: AlbumUpdate,
):
    album = get_album(session, album_id)
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if not album.owner == user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this photo",
        )
    return update_album(session, album=album, album_update=album_update)
