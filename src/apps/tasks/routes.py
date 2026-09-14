from fastapi import APIRouter, HTTPException

from src.apps.tasks.models import Task
from src.apps.tasks.schemas import TaskIn, TaskOut

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskOut])
async def list_tasks():
    return await Task.select().order_by(Task.id)


@router.post("", response_model=TaskOut)
async def create_task(task: TaskIn):
    row = Task(**task.model_dump())
    await row.save()
    return row.to_dict()


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: int):
    row = await Task.objects().get(Task.id == task_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return row.to_dict()


@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(task_id: int, task: TaskIn):
    row = await Task.objects().get(Task.id == task_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task.model_dump().items():
        setattr(row, key, value)
    await row.save()
    return row.to_dict()


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int):
    row = await Task.objects().get(Task.id == task_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    await row.remove()
