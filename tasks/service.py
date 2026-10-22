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
    """Valida las reglas de dominio y crea una tarea en estado `pending`.

    Las validaciones se aplican en este orden y se detienen en el primer error:
    título, fecha de vencimiento, prioridad, existencia del responsable y
    duplicado. El título se guarda sin espacios en los extremos.

    Args:
        data: Datos de entrada de la tarea, ya validados en forma por Pydantic.

    Returns:
        La tarea creada, con `id` asignado y `status` igual a `TaskStatus.PENDING`.

    Raises:
        HTTPException: 422 (`invalid_request`) si el título no mide entre 3 y 120
            caracteres tras recortarlo, si `due_date` es anterior a hoy o si la
            prioridad no está entre 1 y 5.
        HTTPException: 404 (`not_found`) si `assignee_id` no corresponde a un
            usuario existente.
        HTTPException: 409 (`already_exists`) si el responsable ya tiene una
            tarea pendiente con el mismo título normalizado.

    Example:
        >>> from datetime import date
        >>> data = TaskCreate(
        ...     title="  Revisar PR  ",
        ...     due_date=date.today(),
        ...     priority=3,
        ...     assignee_id=1,
        ... )
        >>> task = create_task(data)
        >>> task.title, task.status
        ('Revisar PR', <TaskStatus.PENDING: 'pending'>)
    """
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
    """Comprueba el largo del título y lo devuelve recortado.

    Args:
        title: Título tal como llegó en la petición.

    Returns:
        El título sin espacios en los extremos.

    Raises:
        HTTPException: 422 (`invalid_request`) si, tras recortarlo, el título no
            mide entre `TITLE_MIN_LENGTH` y `TITLE_MAX_LENGTH` caracteres.
    """
    stripped_title = title.strip()
    if not TITLE_MIN_LENGTH <= len(stripped_title) <= TITLE_MAX_LENGTH:
        raise errors.invalid_request(
            f"El título debe tener entre {TITLE_MIN_LENGTH} y {TITLE_MAX_LENGTH} caracteres"
        )
    return stripped_title


def _validate_due_date(due_date: date) -> None:
    """Rechaza fechas de vencimiento pasadas. Hoy es una fecha válida.

    Args:
        due_date: Fecha de vencimiento de la tarea.

    Raises:
        HTTPException: 422 (`invalid_request`) si `due_date` es anterior a
            `date.today()`.
    """
    if due_date < date.today():
        raise errors.invalid_request("La fecha de vencimiento no puede ser anterior a hoy")


def _validate_priority(priority: int) -> None:
    """Comprueba que la prioridad esté en el rango permitido, ambos extremos incluidos.

    Args:
        priority: Prioridad de la tarea.

    Raises:
        HTTPException: 422 (`invalid_request`) si `priority` no está entre
            `PRIORITY_MIN` y `PRIORITY_MAX`.
    """
    if not PRIORITY_MIN <= priority <= PRIORITY_MAX:
        raise errors.invalid_request(
            f"La prioridad debe estar entre {PRIORITY_MIN} y {PRIORITY_MAX}"
        )


def _validate_assignee_exists(assignee_id: int) -> None:
    """Comprueba que el responsable sea un usuario existente.

    Args:
        assignee_id: Identificador del usuario responsable.

    Raises:
        HTTPException: 404 (`not_found`) si no hay un usuario con ese id.
    """
    if users_repository.get(assignee_id) is None:
        raise errors.not_found("usuario", assignee_id)


def _validate_not_duplicated(title: str, assignee_id: int) -> None:
    """Idempotencia: rechaza una tarea pendiente repetida para el mismo responsable.

    Dos títulos se consideran iguales si coinciden tras `_normalize_title`.

    Args:
        title: Título ya recortado de la nueva tarea.
        assignee_id: Identificador del usuario responsable.

    Raises:
        HTTPException: 409 (`already_exists`) si el responsable ya tiene una tarea
            en estado `pending` con el mismo título normalizado.
    """
    normalized_title = _normalize_title(title)
    pending_tasks = repository.find_by_assignee_and_status(assignee_id, TaskStatus.PENDING)
    if any(_normalize_title(task.title) == normalized_title for task in pending_tasks):
        raise errors.already_exists("tarea", title)


def _normalize_title(title: str) -> str:
    """Construye la clave de comparación para la idempotencia.

    Args:
        title: Título a normalizar.

    Returns:
        El título en minúsculas, sin espacios en los extremos y con los espacios
        internos colapsados a uno solo.
    """
    return " ".join(title.lower().split())
