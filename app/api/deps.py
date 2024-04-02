from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exeptions import CredentialsException
from app.db.crud import UserStorage as US
from app.db.database import get_db_session
from app.db.schemas import TokenData, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/token")


DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]


async def get_current_user(
    session: DBSessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise CredentialsException
        token_data = TokenData(email=email)
    except JWTError:
        raise CredentialsException
    user = await US.get_user_by_email(session, email=token_data.email)
    if user is None:
        raise CredentialsException
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
