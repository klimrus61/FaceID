from fastapi_storages.integrations.sqlalchemy import ImageType
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from .database import Base, storage

# user_to_photo = Table(
#     "user_to_photo",
#     Base.metadata,
#     Column("user_id", ForeignKey("users.id"), primary_key=True),
#     Column("photo_id", ForeignKey("photos.id"), primary_key=True),
# )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    # photos = relationship(secondary="user_to_photo", back_populates="users")


# class Album(Base):
#     __tablename__ = "albums"
#
#     id = Column(Integer, primary_key=True)
#     title = Column(String, index=True)
#     description = Column(String)
#     is_display = Column(Boolean, default=True)
#
#     photos = relationship("Photo", back_populates="album")
#
#
# class Photo(Base):
#     __tablename__ = "photos"
#
#     id = Column(Integer, primary_key=True)
#     title = Column(String, index=True)
#     description = Column(String)
#     file = Column(ImageType(storage=storage))
#     album_id = Column(Integer, ForeignKey("albums.id"))
#     owner_id = Column(Integer, ForeignKey("users.id"))
#
#     owner = relationship("User", back_populates="own_photos")
#     album = relationship("Album", back_populates="photos")
#     users = relationship(secondary="user_to_photo", back_populates="photos")
