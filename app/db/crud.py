from typing import Type

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models, schemas
from app.utils import get_password_hash, verify_password


async def add_db_entity(session: AsyncSession, db_entity: Type[models.Base]):
    session.add(db_entity)
    await session.commit()
    await session.refresh(db_entity)
    return db_entity


# ================================= User ============================================


async def get_user(session: AsyncSession, user_id: int) -> models.User:
    stmt = select(models.User).where(models.User.id == user_id)
    return await session.scalar(stmt)


async def get_user_by_email(session: AsyncSession, email: str) -> models.User:
    stmt = select(models.User).where(models.User.email == email)
    return await session.scalar(stmt)


async def get_users(
    session: AsyncSession, skip: int = 0, limit: int = 100
) -> list[models.User]:
    return await session.scalars(models.User).offset(skip).fetch(limit)


async def create_user(session: AsyncSession, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def authenticate_user(session: AsyncSession, email: str, password: str):
    user = await get_user_by_email(session, email)
    return user if user and verify_password(password, user.hashed_password) else False


# ================================= Photo ============================================


async def create_photo(
    session: AsyncSession, photo: schemas.PhotoCreate, uploaded_by: schemas.User
):
    db_photo = models.Photo(**photo.dict(), uploaded_by_id=uploaded_by.id)
    session.add(db_photo)
    await session.commit()
    await session.refresh(db_photo)
    return db_photo


async def get_photo(session: AsyncSession, photo_id: int) -> models.Photo | None:
    return await session.get(models.Photo, photo_id)


async def delete_photo(session: AsyncSession, photo: models.Photo):
    await session.delete(photo)
    await session.commit()


async def get_user_photos(
    session: AsyncSession, user: schemas.User, skip: int, limit: int
) -> list[models.Photo]:
    stmt = select(models.Photo).where(models.Photo.uploaded_by == user)
    return await session.scalars(stmt).offset(skip).fetch(limit)


async def change_photo_album(
    session: AsyncSession,
    photo: models.Photo,
    album_id: int,
) -> models.Photo:
    photo.album_id = album_id
    session.add(photo)
    await session.commit()
    await session.refresh(photo)
    return photo


async def get_single_owner_photos(session: AsyncSession, user: schemas.User):
    stmt = (
        select(models.Photo)
        .where(models.Photo.uploaded_by == user)
        .where(models.Photo.users.any(id=user.id))
    )
    return await session.scalars(stmt)


async def set_on_photo_only_owner(session: AsyncSession, photo: models.Photo):
    photo.users.append(photo.uploaded_by)
    session.add(photo)
    await session.commit()
    await session.refresh(photo)
    return photo


# ================================= Albums ============================================


async def get_user_albums(
    session: AsyncSession, user_id, skip: int, limit: int
) -> list[models.Album]:
    stmt = select(models.Album).where(models.Album.owner_id == user_id)
    return await session.scalars(stmt).offset(skip).fetch(limit)


async def create_album(
    session: AsyncSession, owner: schemas.User, album: schemas.AlbumCreate
) -> models.Album:
    album_db = models.Album(**album.dict(), owner_id=owner.id)
    session.add(album_db)
    await session.commit()
    await session.refresh(album_db)
    return album_db


async def get_album(session: AsyncSession, album_id: int) -> models.Album | None:
    return await session.get(models.Album, album_id)


async def delete_album(session: AsyncSession, album: models.Album):
    await session.delete(album)
    await session.commit()


async def update_album(
    session: AsyncSession, album: models.Album, album_update: schemas.AlbumUpdate
) -> models.Album:
    query = (
        update(models.Album)
        .values(**album_update.dict())
        .where(models.Album.id == album.id)
    )
    await session.execute(query)
    await session.commit()
    await session.refresh(album)
    return album
