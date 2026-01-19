from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class TaskRead(TaskCreate):
    id: UUID
    owner_id: UUID

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str
