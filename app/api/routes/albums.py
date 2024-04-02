from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import DBSessionDep, get_current_active_user
from app.db.crud import AlbumStorage as AS
from app.db.schemas import Album, AlbumCreate, AlbumUpdate, User

router = APIRouter()


@router.get("/")
async def get_user_albums_by_id(
    session: DBSessionDep,
    user_id: int,
    offset: int = 0,
    limit: int = 100,
):
    return await AS.get_user_albums(session, user_id, offset, limit)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_album_to_user(
    session: DBSessionDep,
    user: Annotated[User, Depends(get_current_active_user)],
    album: AlbumCreate,
):
    return await AS.create_album(session, owner=user, album=album)


@router.get("/{album_id}")
async def get_album_by_id(session: DBSessionDep, album_id: int):
    return await AS.get_album(session, album_id)


@router.delete("/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_album_by_id(
    session: DBSessionDep,
    user: Annotated[User, Depends(get_current_active_user)],
    album_id: int,
):
    album = await AS.get_album(session, album_id)
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if not album.owner == user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this photo",
        )
    await AS.delete_album(session, album)


@router.put("/{album_id}")
async def update_album_by_id(
    session: DBSessionDep,
    album_id: int,
    user: Annotated[User, Depends(get_current_active_user)],
    album_update: AlbumUpdate,
):
    album = await AS.get_album(session, album_id)
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if not album.owner == user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this photo",
        )
    return await AS.update_album(session, album=album, album_update=album_update)
