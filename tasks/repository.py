"""Almacén en memoria del recurso `tasks`.

Mismo contrato que `users/repository.py`: la capa de `service.py` no debería
notar que no hay una base de datos real detrás.
"""
from datetime import date

from tasks.schemas import Task, TaskStatus

_tasks: dict[int, Task] = {}
_next_id: int = 1


def add(
    *,
    title: str,
    due_date: date,
    priority: int,
    assignee_id: int,
    status: TaskStatus,
) -> Task:
    # TODO: construir la Task con _next_id, guardarla en _tasks e incrementar _next_id.
    raise NotImplementedError


def find_by_assignee_and_status(assignee_id: int, status: TaskStatus) -> list[Task]:
    # TODO: devolver las tareas de `assignee_id` que estén en `status`.
    raise NotImplementedError


def reset() -> None:
    """Deja el almacén vacío (no hay datos semilla). Se usa entre tests."""
    global _next_id
    _tasks.clear()
    _next_id = 1
