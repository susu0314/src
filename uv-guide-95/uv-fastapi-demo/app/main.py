from itertools import count

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)


class Task(BaseModel):
    id: int
    title: str
    done: bool = False


def create_app() -> FastAPI:
    api = FastAPI(title="uv FastAPI demo")
    tasks: dict[int, Task] = {}
    next_id = count(1)

    @api.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @api.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
    def create_task(payload: TaskCreate) -> Task:
        task = Task(id=next(next_id), title=payload.title)
        tasks[task.id] = task
        return task

    @api.get("/tasks/{task_id}", response_model=Task)
    def get_task(task_id: int) -> Task:
        task = tasks.get(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="task not found")
        return task

    @api.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_task(task_id: int) -> None:
        if tasks.pop(task_id, None) is None:
            raise HTTPException(status_code=404, detail="task not found")

    return api


app = create_app()
