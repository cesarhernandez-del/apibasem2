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
    global _next_id
    task = Task(
        id=_next_id,
        title=title,
        due_date=due_date,
        priority=priority,
        assignee_id=assignee_id,
        status=status,
    )
    _tasks[task.id] = task
    _next_id += 1
    return task


def find_by_assignee_and_status(assignee_id: int, status: TaskStatus) -> list[Task]:
    return [t for t in _tasks.values() if t.assignee_id == assignee_id and t.status == status]


def reset() -> None:
    """Deja el almacén vacío (no hay datos semilla). Se usa entre tests."""
    global _next_id
    _tasks.clear()
    _next_id = 1
