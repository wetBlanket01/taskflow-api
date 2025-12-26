from uuid import uuid4

from fastapi import APIRouter, HTTPException

from src.models import UserCreate, users_table, UserOut
from src.core.security import get_password_hash

router = APIRouter(prefix='/auth')


@router.post("/register")
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
        email=new_user['email']
    )


