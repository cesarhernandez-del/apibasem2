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
    """Guarda una tarea nueva con el siguiente id disponible.

    No valida reglas de dominio: eso es responsabilidad de `service.py`.

    Args:
        title: Título de la tarea, ya recortado.
        due_date: Fecha de vencimiento.
        priority: Prioridad de la tarea.
        assignee_id: Identificador del usuario responsable.
        status: Estado inicial de la tarea.

    Returns:
        La tarea guardada, con su `id` asignado.

    Example:
        >>> from datetime import date
        >>> task = add(
        ...     title="Revisar PR",
        ...     due_date=date(2026, 12, 1),
        ...     priority=3,
        ...     assignee_id=1,
        ...     status=TaskStatus.PENDING,
        ... )
        >>> task.id
        1
    """
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
    """Busca las tareas de un responsable que están en un estado dado.

    Args:
        assignee_id: Identificador del usuario responsable.
        status: Estado por el que se filtra.

    Returns:
        Las tareas que cumplen ambos criterios, en orden de creación. Lista vacía
        si no hay ninguna.

    Example:
        >>> pending = find_by_assignee_and_status(1, TaskStatus.PENDING)
        >>> [task.title for task in pending]
        ['Revisar PR']
    """
    return [t for t in _tasks.values() if t.assignee_id == assignee_id and t.status == status]


def reset() -> None:
    """Deja el almacén vacío y reinicia los ids. Se usa entre tests.

    A diferencia de `users`, no hay datos semilla.

    Example:
        >>> reset()
        >>> find_by_assignee_and_status(1, TaskStatus.PENDING)
        []
    """
    global _next_id
    _tasks.clear()
    _next_id = 1
