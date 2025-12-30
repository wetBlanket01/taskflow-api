from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.models import UserCreate, users_table, UserOut, Token
from src.core.security import get_password_hash, authenticate_user, create_access_token

router = APIRouter(prefix='/auth')


@router.post("/register", response_model=UserOut)
def register_user(user_in: UserCreate):
    for user in users_table:
        if user['username'] == user_in.username or user['email'] == user_in.email:
            raise HTTPException(status_code=400, detail="Username or email already exists")

    hashed_password = get_password_hash(user_in.password)

    new_user = {
        'id': str(uuid4()),
        'username': user_in.username,
        'email': user_in.email,
        'password': hashed_password
    }

    users_table.append(new_user)

    return UserOut(
        id=new_user['id'],
        username=new_user['username'],
        email=new_user['email'],
    )


@router.post("/token", response_model=Token)
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username, email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(data={"sub": user['id']})

    return Token(access_token=access_token, token_type="bearer")
