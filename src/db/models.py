from uuid import uuid4

from sqlalchemy import String, ForeignKey, Boolean, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID


class Base(AsyncSession, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    tasks: Mapped[list['Task']] = relationship("Task", back_populates="owner", cascade="all, delete")


class Task(Base):
    __tablename__ = "tasks"

    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    owner: Mapped['User'] = relationship("User", back_populates="tasks")
