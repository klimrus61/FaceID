from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_current_active_user
from app.db.schemas import User

router = APIRouter(prefix="/me")


@router.get("/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@router.get("/items")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.username}]
