from fastapi import UploadFile
from pydantic import BaseModel


class UserBase(BaseModel):
    email: str


class UserForPhoto(UserBase):
    id: int
    is_active: bool


class PhotoBase(BaseModel):
    title: str
    description: str | None


class PhotoCreate(PhotoBase):
    file: UploadFile
    pass


class Photo(PhotoBase):
    id: int
    file: str
    album_id: int | None = None
    uploaded_by_id: int
    users: list[UserForPhoto] | None


#
#
# class User(UserBase):
#     id: int
#     is_active: bool
#     photos: list[Photo] = []
#
#     class Config:
#         orm_mode = True


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    full_name: str | None = None
    is_active: bool | None = None


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str


class AlbumBase(BaseModel):
    title: str
    description: str | None = None


class AlbumCreate(AlbumBase):
    pass


class AlbumUpdate(AlbumBase):
    is_display: bool


class Album(AlbumBase):
    is_display: bool = True
    photos: list[Photo] = []
