from fastapi import UploadFile
from pydantic import BaseModel

#

#
#
# class UserForPhoto(UserBase):
#     id: int
#     is_active: bool
#
#
# class PhotoBase(BaseModel):
#     title: str
#     description: str | None = None
#     file: UploadFile
#
#
# class PhotoCreate(PhotoBase):
#     pass
#
#
# class Photo(PhotoBase):
#     id: int
#     album_id: int
#     owner_id: int
#     users: list[UserForPhoto]
#
#
# class User(UserBase):
#     id: int
#     is_active: bool
#     photos: list[Photo] = []
#
#     class Config:
#         orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    full_name: str | None = None
    is_active: bool | None = None


class UserInDB(User):
    hashed_password: str


#
# class AlbumBase(BaseModel):
#     title: str
#     description: str | None = None
#
#
# class AlbumCreate(AlbumBase):
#     pass
#
#
# class Album(AlbumBase):
#     is_display: bool = True
#     photos: list[Photo] = []
#
#     class Config:
#         orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
