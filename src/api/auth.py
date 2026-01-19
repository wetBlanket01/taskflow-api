from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.models import UserCreate, UserOut, Token
from src.core.security import get_password_hash, verify_password, create_access_token
from src.db.models import User
from src.db.session import get_db

router = APIRouter(prefix='/auth')


@router.post("/register", response_model=UserOut)
async def register_user(
        user_in: UserCreate,
        db: Annotated[AsyncSession, Depends(get_db)]
):
    stmt = select(User).where(
        (User.username == user_in.username) or (User.email == user_in.email)
    )
    existing = await db.execute(stmt)

    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )

    hashed_password = get_password_hash(user_in.password)

    db_user = User()
    db_user.username = user_in.username
    db_user.email = user_in.email
    db_user.password_hash = hashed_password

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return UserOut.from_orm(db_user)


@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Annotated[AsyncSession, Depends(get_db)]
):
    stmt = select(User).where(User.username == form_data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return Token(access_token=access_token, token_type="bearer")
