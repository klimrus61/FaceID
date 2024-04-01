from typing import List

from fastapi_storages.integrations.sqlalchemy import ImageType
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base, storage

user_to_photo = Table(
    "user_to_photo",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("photo_id", ForeignKey("photos.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)

    on_photos: Mapped[List["Photo"]] = relationship(
        secondary="user_to_photo", back_populates="users"
    )
    uploaded_photos: Mapped[List["Photo"]] = relationship(back_populates="uploaded_by")
    own_albums: Mapped[List["Album"]] = relationship(back_populates="owner")


class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String)
    is_display = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    photos = relationship("Photo", back_populates="album")
    owner = relationship("User", back_populates="own_albums")


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String)
    file = Column(ImageType(storage=storage))
    album_id = Column(Integer, ForeignKey("albums.id"))
    uploaded_by_id = Column(Integer, ForeignKey("users.id"))

    uploaded_by = relationship("User", back_populates="uploaded_photos")
    album = relationship("Album", back_populates="photos")
    users = relationship("User", secondary="user_to_photo", back_populates="on_photos")
