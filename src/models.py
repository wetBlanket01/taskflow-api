from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

tasks_table = []
users_table = []


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class Task(TaskCreate):
    id: str
    owner_id: str = 'user1'


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: UUID


class Token(BaseModel):
    access_token: str
    token_type: str
