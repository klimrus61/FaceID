from typing import Annotated

from fastapi import Depends
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.db import models, schemas
from app.utils import get_password_hash, verify_password

# ================================= User ============================================


def get_user(session: Session, user_id: int):
    return session.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(session: Session, email: str) -> models.User:
    return session.query(models.User).filter(models.User.email == email).first()


def get_users(session: Session, skip: int = 0, limit: int = 100):
    return session.query(models.User).offset(skip).limit(limit).all()


def create_user(session: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def authenticate_user(session: Session, email: str, password: str):
    user = get_user_by_email(session, email)
    return user if user and verify_password(password, user.hashed_password) else False


# ================================= User ============================================

# ================================= Photo ============================================


def create_photo(
    session: Session,
    photo: schemas.PhotoCreate,
    owner: Annotated[models.User, Depends(get_user_by_email)],
):
    db_photo = models.Photo(**photo.dict(), owner_id=owner.id)
    session.add(db_photo)
    session.commit()
    session.refresh(db_photo)
    return db_photo


def get_photo(session: Session, photo_id: int):
    return session.get(models.Photo, photo_id)


def delete_photo(session: Session, photo: models.Photo):
    session.delete(photo)
    session.commit()


def get_user_photos(
    session: Session, user: models.User, skip: int, limit: int
) -> list[models.Photo]:
    return (
        session.query(models.Photo)
        .filter(models.Photo.owner == user)
        .offset(skip)
        .limit(limit)
        .all()
    )


def change_photo_album(
    session: Session,
    photo: models.Photo,
    album_id: int,
):
    photo.album_id = album_id
    session.add(photo)
    session.commit()
    session.refresh(photo)
    return photo


# ================================= Photo ============================================

# ================================= Albums ============================================


def get_user_albums(session: Session, user_id, skip: int, limit: int):
    return (
        session.query(models.Album)
        .filter(models.Album.owner_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_album(session: Session, owner: schemas.User, album: schemas.AlbumCreate):
    album_db = models.Album(**album.dict(), owner_id=owner.id)
    session.add(album_db)
    session.commit()
    session.refresh(album_db)
    return album_db


def get_album(session: Session, album_id: int):
    return session.get(models.Album, album_id)


def delete_album(session: Session, album: models.Album):
    session.delete(album)
    session.commit()


def update_album(
    session: Session, album: models.Album, album_update: schemas.AlbumUpdate
):
    query = (
        update(models.Album)
        .values(**album_update.dict())
        .where(models.Album.id == album.id)
    )
    session.execute(query)
    session.commit()
    session.refresh(album)
    return album


# ================================= Albums ============================================
