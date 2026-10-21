"""Schemas Pydantic del recurso `tasks`.

Solo validan forma (tipos). Las reglas de dominio —largo del título, fecha no
anterior a hoy, rango de prioridad— viven en `service.py`.
"""
from datetime import date
from enum import Enum

from pydantic import BaseModel


class TaskStatus(str, Enum):
    PENDING = "pending"


class TaskBase(BaseModel):
    title: str
    due_date: date
    priority: int
    assignee_id: int


class TaskCreate(TaskBase):
    """Cuerpo de entrada para crear una tarea."""


class Task(TaskBase):
    """Tarea tal como la devuelve la API."""

    id: int
    status: TaskStatus
