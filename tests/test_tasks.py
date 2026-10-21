"""Tests del recurso `tasks` (POST /tasks).

Cada test cubre un criterio de aceptación (CA-n). Mismo estilo que `test_users.py`:
arrange / act / assert separados por una línea en blanco.
"""
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient


def _valid_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "title": "Revisar PR",
        "due_date": date.today().isoformat(),
        "priority": 3,
        "assignee_id": 1,
    }
    payload.update(overrides)
    return payload


# CA-1
def test_create_task_datos_validos_devuelve_201_y_la_tarea_completa(
    client: TestClient,
) -> None:
    due_date = (date.today() + timedelta(days=7)).isoformat()
    payload = _valid_payload(due_date=due_date, priority=2, assignee_id=3)

    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "title": "Revisar PR",
        "due_date": due_date,
        "priority": 2,
        "assignee_id": 3,
        "status": "pending",
    }


def test_create_task_devuelve_el_titulo_sin_espacios_en_los_extremos(
    client: TestClient,
) -> None:
    payload = _valid_payload(title="  Revisar PR  ")

    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    assert response.json()["title"] == "Revisar PR"


# CA-2
@pytest.mark.parametrize(
    "title",
    ["", "   ", "ab", "  ab  ", "a" * 121],
    ids=["vacio", "solo_espacios", "dos_caracteres", "dos_tras_recortar", "121_caracteres"],
)
def test_create_task_titulo_invalido_devuelve_422(client: TestClient, title: str) -> None:
    payload = _valid_payload(title=title)

    response = client.post("/tasks", json=payload)

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, str)
    assert "título" in detail


@pytest.mark.parametrize(
    "title",
    ["abc", "a" * 120],
    ids=["3_caracteres", "120_caracteres"],
)
def test_create_task_titulo_en_los_limites_devuelve_201(
    client: TestClient, title: str
) -> None:
    payload = _valid_payload(title=title)

    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    assert response.json()["title"] == title


# CA-3
def test_create_task_fecha_anterior_a_hoy_devuelve_422(client: TestClient) -> None:
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    payload = _valid_payload(due_date=yesterday)

    response = client.post("/tasks", json=payload)

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, str)
    assert "fecha" in detail


def test_create_task_fecha_de_hoy_devuelve_201(client: TestClient) -> None:
    today = date.today().isoformat()
    payload = _valid_payload(due_date=today)

    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    assert response.json()["due_date"] == today


# CA-4
@pytest.mark.parametrize("priority", [0, 6], ids=["cero", "seis"])
def test_create_task_prioridad_fuera_de_rango_devuelve_422(
    client: TestClient, priority: int
) -> None:
    payload = _valid_payload(priority=priority)

    response = client.post("/tasks", json=payload)

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, str)
    assert "prioridad" in detail


@pytest.mark.parametrize("priority", [1, 5], ids=["uno", "cinco"])
def test_create_task_prioridad_en_los_limites_devuelve_201(
    client: TestClient, priority: int
) -> None:
    payload = _valid_payload(priority=priority)

    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    assert response.json()["priority"] == priority


# CA-5
def test_create_task_responsable_inexistente_devuelve_404(client: TestClient) -> None:
    payload = _valid_payload(assignee_id=999)

    response = client.post("/tasks", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "usuario no encontrado: 999"


# CA-6
def test_create_task_duplicada_pendiente_mismo_responsable_devuelve_409(
    client: TestClient,
) -> None:
    client.post("/tasks", json=_valid_payload(title="Revisar PR", assignee_id=1))
    payload = _valid_payload(title="  revisar   pr ", assignee_id=1)

    response = client.post("/tasks", json=payload)

    assert response.status_code == 409
    assert "ya existe" in response.json()["detail"]


def test_create_task_mismo_titulo_otro_responsable_devuelve_201(
    client: TestClient,
) -> None:
    client.post("/tasks", json=_valid_payload(title="Revisar PR", assignee_id=1))
    payload = _valid_payload(title="Revisar PR", assignee_id=2)

    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 2
    assert body["assignee_id"] == 2
