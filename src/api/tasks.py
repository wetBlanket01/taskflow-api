from typing import List, Annotated, Union
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.openapi.models import Response

from src.models import TaskCreate, Task, tasks_table, TaskUpdate
from src.api.deps import get_current_user

router = APIRouter()


@router.post("/tasks", response_model=Task)
def create_task(task: TaskCreate, current_user: Annotated[dict, Depends(get_current_user)]):
    new_task = task.dict()
    new_task['owner_id'] = current_user['id']
    new_task['id'] = str(uuid4())
    tasks_table.append(new_task)
    return new_task


@router.get("/tasks", response_model=List[Task])
def get_tasks(current_user: Annotated[dict, Depends(get_current_user)]):
    user_tasks = [task for task in tasks_table if task['owner_id'] == current_user['id']]
    return user_tasks


@router.delete("/tasks/{task_id}")
def delete_task(task_id: str, current_user: Annotated[dict, Depends(get_current_user)]):
    task = _get_task_by_id(task_id, current_user)
    tasks_table.remove(task)
    return Response(status_code=204)


@router.patch("/tasks/{task_id}", response_model=Task)
def update_task(
        task_id: str,
        task_update: TaskUpdate,
        current_user: Annotated[dict, Depends(get_current_user)]
):
    task = _get_task_by_id(task_id, current_user)
    update_data = task_update.dict(exclude_unset=True)
    task.update(update_data)
    return Task(**task)


def _get_task_by_id(task_id: str, current_user: dict) -> dict:
    user_tasks = [task for task in tasks_table if task['owner_id'] == current_user['id']]
    for task in user_tasks:
        if task['id'] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")
