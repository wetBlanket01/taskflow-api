from typing import List, Annotated, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, update, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import TaskCreate, TaskUpdate, TaskRead
from src.api.deps import get_current_user
from src.db.models import Task, User
from src.db.session import get_db

router = APIRouter()


@router.post("/tasks", response_model=TaskRead)
async def create_task(
        task: TaskCreate,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)]
):
    new_task = Task()
    new_task.title = task.title
    new_task.description = task.description
    new_task.completed = task.completed
    new_task.owner_id = current_user.id

    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return TaskRead.model_validate(new_task)


@router.get("/tasks", response_model=List[TaskRead])
async def get_tasks(
        current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)],
        completed: Optional[bool] = Query(None),
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        sort_by: str = Query(default='title'),
        order: str = Query(default='asc', pattern="^(asc|desc)$"),
):
    stmt = select(Task).where(Task.owner_id == current_user.id)

    if completed is not None:
        stmt = stmt.where(Task.completed == completed)

    if sort_by == 'title':
        stmt = stmt.order_by(Task.title.asc() if order == 'asc' else Task.title.desc())

    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)

    return [TaskRead.model_validate(task) for task in result.scalars().all()]


@router.get("/tasks/{task_id}", response_model=TaskRead)
async def get_task(
        task_id: str,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)]
):
    stmt = select(Task).where(
        Task.id == task_id,
        Task.owner_id == current_user.id
    )
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskRead.model_validate(task)


@router.delete("/tasks/{task_id}")
async def delete_task(
        task_id: str,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)]
):
    stmt = delete(Task).where(
        (Task.owner_id == current_user.id) and (Task.id == task_id)
    )
    await db.execute(stmt)
    await db.commit()
    return None


@router.patch("/tasks/{task_id}", response_model=TaskRead)
async def update_task(
        task_id: str,
        task_update: TaskUpdate,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)]
):

    stmt = (
        update(Task)
        .where((Task.owner_id == current_user.id) and (Task.id == task_id))
        .values(**task_update.model_dump(exclude_unset=True))
        .returning(Task)
    )

    result = await db.execute(stmt)
    updated_task = result.scalar_one_or_none()

    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.commit()
    await db.refresh(updated_task)

    return TaskRead.model_validate(updated_task)

