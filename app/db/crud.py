from typing import Sequence, Type

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationships, selectinload

from app.db import models, schemas
from app.utils import get_password_hash, verify_password


async def add_db_entity(session: AsyncSession, db_entity: Type[models.Base]):
    session.add(db_entity)
    await session.commit()
    await session.refresh(db_entity)
    return db_entity


# ================================= User ============================================


class UserStorage:
    @staticmethod
    async def get_user(session: AsyncSession, user_id: int) -> models.User | None:
        stmt = select(models.User).where(models.User.id == user_id)
        result = await session.execute(stmt)
        return result.scalar()

    @staticmethod
    async def get_user_by_email(
        session: AsyncSession, email: str
    ) -> models.User | None:
        stmt = select(models.User).where(models.User.email == email)
        result = await session.execute(stmt)
        return result.scalar()

    @staticmethod
    async def get_users(
        session: AsyncSession, offset: int, limit: int
    ) -> Sequence[models.User]:
        stmt = select(models.User).offset(offset).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def create_user(session: AsyncSession, user: schemas.UserCreate):
        hashed_password = await get_password_hash(user.password)
        db_user = models.User(email=user.email, hashed_password=hashed_password)
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return db_user

    @staticmethod
    async def authenticate_user(session: AsyncSession, email: str, password: str):
        user = await UserStorage.get_user_by_email(session, email)
        return (
            user
            if user and await verify_password(password, user.hashed_password)
            else False
        )


# ================================= Photo ============================================


class PhotoStorage:
    @staticmethod
    async def get_photo(session: AsyncSession, photo_id: int) -> models.Photo | None:
        stmt = select(models.Photo).where(models.Photo.id == photo_id)
        result = await session.execute(stmt)
        return result.scalar()

    @staticmethod
    async def create_photo(
        session: AsyncSession,
        photo: schemas.PhotoCreate,
        uploaded_by: schemas.User,
    ):
        db_photo = models.Photo(**photo.dict(), uploaded_by_id=uploaded_by.id)
        session.add(db_photo)
        await session.commit()
        await session.refresh(db_photo)
        return db_photo

    @staticmethod
    async def get_users_from_photo(session: AsyncSession, photo_id: int):
        stmt = (
            select(models.Photo)
            .where(models.Photo.id == photo_id)
            .options(selectinload(models.Photo.users))
        )
        result = await session.execute(stmt)
        return result.scalar()

    @staticmethod
    async def delete_photo(session: AsyncSession, photo: models.Photo):
        await session.delete(photo)
        await session.commit()

    @staticmethod
    async def get_user_photos(
        session: AsyncSession, user: schemas.User, offset: int, limit: int
    ) -> Sequence[models.Photo]:
        stmt = (
            select(models.Photo)
            .where(models.Photo.uploaded_by_id == user.id)
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def change_photo_album(
        session: AsyncSession,
        photo: models.Photo,
        album: models.Album,
    ) -> models.Photo:
        photo.album = album
        session.add(photo)
        await session.commit()
        await session.refresh(photo)
        return photo

    @staticmethod
    async def get_single_owner_photos(
        session: AsyncSession, user: schemas.User
    ) -> Sequence[models.Photo] | None:
        subquery = (
            select(models.user_to_photo.c.photo_id)
            .group_by(models.user_to_photo.c.photo_id)
            .having(func.count(models.user_to_photo.c.user_id) == 1)
        )
        query = select(models.Photo).where(
            (models.Photo.uploaded_by == user) & (models.Photo.id.in_(subquery))
        )
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def set_on_photo_only_owner(session: AsyncSession, photo: models.Photo):
        await session.execute(
            models.user_to_photo.insert(),
            [{"user_id": photo.uploaded_by_id, "photo_id": photo.id}],
        )
        await session.commit()
        await session.refresh(photo)
        return photo


# ================================= Albums ============================================


class AlbumStorage:
    @staticmethod
    async def get_user_albums(
        session: AsyncSession, user_id, offset: int, limit: int
    ) -> Sequence[models.Album]:
        stmt = (
            select(models.Album)
            .where(models.Album.owner_id == user_id)
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def create_album(
        session: AsyncSession, owner: schemas.User, album: schemas.AlbumCreate
    ) -> models.Album:
        album_db = models.Album(**album.dict(), owner_id=owner.id)
        session.add(album_db)
        await session.commit()
        await session.refresh(album_db)
        return album_db

    @staticmethod
    async def get_album(session: AsyncSession, album_id: int) -> models.Album | None:
        return await session.get(models.Album, album_id)

    @staticmethod
    async def delete_album(session: AsyncSession, album: models.Album):
        await session.delete(album)
        await session.commit()

    @staticmethod
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
