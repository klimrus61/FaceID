from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import DBSessionDep, get_current_active_user
from app.db.crud import UserStorage as US
from app.db.schemas import User, UserCreate

router = APIRouter()


@router.get("/me", response_model=User)
async def get_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


@router.post("/", response_model=User)
async def create_user_by_email(session: DBSessionDep, user_in: UserCreate):
    user = await US.get_user_by_email(session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = await US.create_user(session, user=user_in)
    return user


@router.get("/", response_model=list[User])
async def get_all_users(session: DBSessionDep, offset: int = 0, limit: int = 100):
    return await US.get_users(session, offset, limit)
