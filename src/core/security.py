from datetime import timedelta, datetime
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from src.models import users_table

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

SECRET_KEY = "your-super-secret-key-change-it-in-production-please"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_username_or_email(identifier: str):
    for user in users_table:
        if user['username'] == identifier or user['email'] == identifier:
            return user
    return None


def authenticate_user(identifier: str, password: str):
    user = get_user_by_username_or_email(identifier)
    if not user:
        return False
    if not verify_password(password, user['password']):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
