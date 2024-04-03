from typing import List

from fastapi_storages.integrations.sqlalchemy import ImageType
from sqlalchemy import Column, ForeignKey, Integer, Table
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
    uploaded_photos: Mapped[List["Photo"]] = relationship(
        "Photo", back_populates="uploaded_by"
    )
    own_albums: Mapped[List["Album"]] = relationship(back_populates="owner")

    def __repr__(self) -> str:
        return f"User(id={self.id!r})"


class Album(Base):
    __tablename__ = "albums"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column()
    is_display: Mapped[bool] = mapped_column(default=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    photos: Mapped[List["Photo"]] = relationship(back_populates="album")
    owner: Mapped["User"] = relationship(back_populates="own_albums")


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column()
    file = Column(ImageType(storage=storage))
    album_id: Mapped[int | None] = mapped_column(ForeignKey("albums.id"))
    uploaded_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    uploaded_by: Mapped["User"] = relationship(back_populates="uploaded_photos")
    album: Mapped["Album"] = relationship(back_populates="photos")
    users: Mapped[List["User"]] = relationship(
        secondary="user_to_photo", back_populates="on_photos"
    )
