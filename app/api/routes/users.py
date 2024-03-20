from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.crud import create_user, get_user_by_email
from app.db.database import get_db
from app.db.schemas import User, UserCreate

router = APIRouter()


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@router.get("/me/items")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.email}]


@router.post("/create", response_model=User)
async def create_user_by_email(
    session: Annotated[Session, Depends(get_db)], user_in: UserCreate
):
    user = get_user_by_email(session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = create_user(session, user=user_in)
    return user
