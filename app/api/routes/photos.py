from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.api.deps import DBSessionDep, get_current_active_user
from app.db.crud import (
    change_photo_album,
    create_photo,
    delete_photo,
    get_album,
    get_photo,
    get_single_owner_photos,
    get_user_photos,
    get_users_from_photo,
    set_on_photo_only_owner,
)
from app.db.schemas import Photo, PhotoCreate, User
from app.face_id.utils import is_one_person_on_photo, is_person_same

router = APIRouter()


@router.get("/")
async def read_current_user_photos(
    session: DBSessionDep,
    user: Annotated[User, Depends(get_current_active_user)],
    offset: int = 0,
    limit: int = 100,
):
    return await get_user_photos(session, user, offset, limit)


@router.post("/")
async def add_photo_to_current_user(
    session: DBSessionDep,
    user: Annotated[User, Depends(get_current_active_user)],
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
):
    photo_in = PhotoCreate(title=title, description=description, file=file)
    return await create_photo(session, photo=photo_in, uploaded_by=user)


@router.get("/only-created-by-current-user")
async def get_photos_there_only_owner(
    session: DBSessionDep,
    user: Annotated[User, Depends(get_current_active_user)],
):
    photos = await get_single_owner_photos(session, user)
    return photos


@router.get("/{photo_id}", response_model=Photo)
async def get_photo_by_id(
    session: DBSessionDep,
    photo_id: int,
):
    users_on_photo = await get_users_from_photo(session, photo_id)
    return users_on_photo


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo_by_id(
    photo_id: int,
    user: Annotated[User, Depends(get_current_active_user)],
    session: DBSessionDep,
):
    photo = await get_photo(session, photo_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if not photo.uploaded_by == user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this photo",
        )
    await delete_photo(session, photo)


@router.patch("/{photo_id}/set-album")
async def patch_photo_album(
    session: DBSessionDep,
    photo_id: int,
    album_id: int,
):
    photo = await get_photo(session, photo_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo does not exist"
        )
    album = await get_album(session, album_id)
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Album does not exist"
        )
    return await change_photo_album(session, photo, album)


@router.patch("/{photo_id}/set-it-is-me")
async def patch_photo_me(
    session: DBSessionDep,
    user: Annotated[User, Depends(get_current_active_user)],
    photo_id: int,
):
    photo = await get_photo(session, photo_id)
    if photo is None:
        raise HTTPException(status_code=404, detail="photo not found")
    if photo.uploaded_by != user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to set up user on this photo this photo",
        )
    if not await is_one_person_on_photo(photo):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="On photo have to one person",
        )
    single_owner_photos = await get_single_owner_photos(session, user)
    if single_owner_photos:
        if not await is_person_same(single_owner_photos, photo):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The person on this photo not the user: {user.email}",
            )
    return await set_on_photo_only_owner(session, photo)
