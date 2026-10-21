"""Lógica de negocio del recurso `tasks`.

Aquí viven las validaciones de dominio y todas las decisiones de error del
recurso (usando `core.errors`). Para comprobar que el responsable existe se
consulta `users.repository`, pero el `not_found` se decide en este módulo.
"""
from datetime import date

from core import errors
from tasks import repository
from tasks.schemas import Task, TaskCreate, TaskStatus
from users import repository as users_repository

TITLE_MIN_LENGTH = 3
TITLE_MAX_LENGTH = 120
PRIORITY_MIN = 1
PRIORITY_MAX = 5


def create_task(data: TaskCreate) -> Task:
    title = _validate_title(data.title)
    _validate_due_date(data.due_date)
    _validate_priority(data.priority)
    _validate_assignee_exists(data.assignee_id)
    _validate_not_duplicated(title, data.assignee_id)
    return repository.add(
        title=title,
        due_date=data.due_date,
        priority=data.priority,
        assignee_id=data.assignee_id,
        status=TaskStatus.PENDING,
    )


def _validate_title(title: str) -> str:
    """Devuelve el título sin espacios en los extremos."""
    stripped_title = title.strip()
    if not TITLE_MIN_LENGTH <= len(stripped_title) <= TITLE_MAX_LENGTH:
        raise errors.invalid_request(
            f"El título debe tener entre {TITLE_MIN_LENGTH} y {TITLE_MAX_LENGTH} caracteres"
        )
    return stripped_title


def _validate_due_date(due_date: date) -> None:
    """Hoy es una fecha válida; solo se rechazan fechas pasadas."""
    if due_date < date.today():
        raise errors.invalid_request("La fecha de vencimiento no puede ser anterior a hoy")


def _validate_priority(priority: int) -> None:
    if not PRIORITY_MIN <= priority <= PRIORITY_MAX:
        raise errors.invalid_request(
            f"La prioridad debe estar entre {PRIORITY_MIN} y {PRIORITY_MAX}"
        )


def _validate_assignee_exists(assignee_id: int) -> None:
    if users_repository.get(assignee_id) is None:
        raise errors.not_found("usuario", assignee_id)


def _validate_not_duplicated(title: str, assignee_id: int) -> None:
    """Idempotencia: misma tarea pendiente para el mismo responsable."""
    normalized_title = _normalize_title(title)
    pending_tasks = repository.find_by_assignee_and_status(assignee_id, TaskStatus.PENDING)
    if any(_normalize_title(task.title) == normalized_title for task in pending_tasks):
        raise errors.already_exists("tarea", title)


def _normalize_title(title: str) -> str:
    """Clave de comparación para la idempotencia: minúsculas y espacios colapsados."""
    return " ".join(title.lower().split())
