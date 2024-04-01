from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import DBSessionDep, get_current_active_user
from app.db.crud import (
    create_album,
    delete_album,
    get_album,
    get_user_albums,
    update_album,
)
from app.db.schemas import Album, AlbumCreate, AlbumUpdate, User

router = APIRouter()


@router.get("/")
async def get_user_albums_by_id(
    session: DBSessionDep,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
):
    return await get_user_albums(session, user_id, skip, limit)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_album_to_user(
    session: DBSessionDep,
    user: Annotated[User, Depends(get_current_active_user)],
    album: AlbumCreate,
):
    return await create_album(session, owner=user, album=album)


@router.delete("/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_album_by_id(
    session: DBSessionDep,
    user: Annotated[User, Depends(get_current_active_user)],
    album_id: int,
):
    album = await get_album(session, album_id)
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if not album.owner == user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this photo",
        )
    await delete_album(session, album)


@router.put("/{album_id}")
async def update_album_by_id(
    session: DBSessionDep,
    album_id: int,
    user: Annotated[User, Depends(get_current_active_user)],
    album_update: AlbumUpdate,
):
    album = await get_album(session, album_id)
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if not album.owner == user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this photo",
        )
    return await update_album(session, album=album, album_update=album_update)
