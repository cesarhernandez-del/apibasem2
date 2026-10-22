"""Rutas HTTP del recurso `tasks`.

Mismo patrón que `users/routes.py`: `response_model=` siempre y la función solo
delega en `service.py`.
"""
from fastapi import APIRouter, status

from tasks import service
from tasks.schemas import Task, TaskCreate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate) -> Task:
    return service.create_task(data)
