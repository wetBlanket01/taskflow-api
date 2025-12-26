from typing import List
from uuid import uuid4

from fastapi import APIRouter

from src.models import TaskCreate, Task, tasks_table

router = APIRouter()


@router.post("/tasks", response_model=Task)
def create_task(task: TaskCreate):
    new_task = task.dict()
    new_task['id'] = str(uuid4())
    tasks_table.append(new_task)
    return new_task


@router.get("/tasks", response_model=List[Task])
def get_tasks():
    return tasks_table

