from typing import List, Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends

from src.models import TaskCreate, Task, tasks_table
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

