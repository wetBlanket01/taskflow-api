from typing import Annotated

from fastapi import HTTPException
from jose import jwt, JWTError
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from src.models import users_table
from src.core.security import SECRET_KEY, ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)
        user_id = payload.get('sub')

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    for user in users_table:
        if user['id'] == user_id:
            return user

    raise credentials_exception

