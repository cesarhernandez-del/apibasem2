# m2-api-base

API REST de usuarios y tareas usada como base en el **Módulo 2 · Clase 1 — Generación de código con IA**.

Es un proyecto pequeño pero completo: tiene convenciones, capas separadas, catálogo
de errores y una suite de tests que pasa. Le falta **una** feature — la que vas a
construir en el laboratorio.

## Requisitos

- Python 3.10 o superior
- [uv](https://docs.astral.sh/uv/)
- (Recomendado) Claude Code instalado

## Instalación

```bash
uv venv                              # crea .venv con un Python 3.10 o superior
uv pip install -r requirements.txt   # instala las dependencias en .venv
```

> Los comandos de las secciones siguientes van con el prefijo `uv run`, que los
> ejecuta dentro de `.venv`. Sin el prefijo y sin activar el entorno, el shell no
> encuentra `pytest`, `ruff` ni `uvicorn`, o usa los del Python del sistema, que no
> tiene las dependencias del proyecto.

## Uso

```bash
uv run uvicorn main:app --reload   # http://127.0.0.1:8000  ·  Swagger en /docs
```

Endpoints actuales:

| Método | Ruta              | Descripción                     |
|--------|-------------------|---------------------------------|
| GET    | `/health`         | Estado del servicio             |
| GET    | `/users`          | Lista de usuarios               |
| GET    | `/users/{id}`     | Un usuario por id (404 si no existe) |
| POST   | `/users`          | Crea un usuario (409 si el email ya existe) |
| POST   | `/tasks`          | Crea una tarea asignada a un usuario (ver [Recurso `tasks`](#recurso-tasks)) |

## Recurso `tasks`

`POST /tasks` crea una tarea asignada a un usuario existente. La tarea nace siempre
en estado `pending`. Antes de guardarla, el servicio aplica estas reglas en orden y
se detiene en la primera que falla:

1. **Título:** entre 3 y 120 caracteres después de quitar los espacios de los
   extremos. Se guarda recortado.
2. **Fecha de vencimiento (`due_date`):** formato `YYYY-MM-DD`; hoy o una fecha
   posterior.
3. **Prioridad:** entero de 1 a 5, ambos incluidos.
4. **Responsable (`assignee_id`):** debe ser un usuario existente.
5. **Sin duplicados:** el responsable no puede tener otra tarea `pending` con el
   mismo título. Para comparar se ignoran mayúsculas y espacios repetidos:
   `"  revisar   PR "` cuenta como `"Revisar PR"`.

### Ejemplo

Petición:

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Revisar PR", "due_date": "2026-11-15", "priority": 3, "assignee_id": 1}'
```

Respuesta `201 Created`:

```json
{
  "title": "Revisar PR",
  "due_date": "2026-11-15",
  "priority": 3,
  "assignee_id": 1,
  "id": 1,
  "status": "pending"
}
```

### Códigos de error

| Código | Causa | `detail` de la respuesta |
|--------|-------|--------------------------|
| 422 | Título con menos de 3 o más de 120 caracteres tras recortarlo (incluye vacío o solo espacios) | `"El título debe tener entre 3 y 120 caracteres"` |
| 422 | `due_date` anterior a hoy | `"La fecha de vencimiento no puede ser anterior a hoy"` |
| 422 | `priority` fuera del rango 1–5 | `"La prioridad debe estar entre 1 y 5"` |
| 422 | Falta un campo o tiene un tipo inválido (lo detecta Pydantic) | Lista de errores de validación de FastAPI |
| 404 | `assignee_id` no corresponde a ningún usuario | `"usuario no encontrado: <assignee_id>"` |
| 409 | El responsable ya tiene una tarea `pending` con el mismo título normalizado | `"tarea ya existe: <title>"` |

### Comportamiento conocido

- **Espacios internos del título:** el título se guarda tal como lo escribió el
  usuario, recortado en los extremos pero conservando los espacios internos
  (`"  Preparar   demo "` se guarda como `"Preparar   demo"`). La comparación de
  duplicados sí los colapsa.
- **Zona horaria de `due_date`:** la validación de fecha usa la fecha local del
  servidor; no hay zona horaria de referencia definida.
- **Dos formatos de 422:** `detail` es texto cuando el error viene del catálogo de
  dominio (`core/errors.py`), y una lista de objetos cuando lo genera la validación
  de Pydantic.

## Tests y calidad

```bash
uv run pytest                                    # correr la suite
uv run pytest --cov=. --cov-report=term-missing  # con cobertura
uv run ruff check .                              # linter
```

## Ramas del módulo

`main` es la base de la **Clase 1**. Cada clase tiene su rama de trabajo y su
rama de solución:

| Clase | Rama de trabajo | Solución | Qué añade |
|-------|-----------------|----------|-----------|
| 1 · Generación | `main` | `solucion-clase1` | La base. Falta `GET /users/search`. |
| 2 · Testing | `clase2-testing` | `solucion-clase2` | `users/validation.py` sin tests → llévalo a >80%. |
| 3 · Debugging | `clase3-debugging` | `solucion-clase3` | Recurso `reports/` con 3 bugs plantados. |
| 4 · Review | `clase4-review` | `solucion-clase4` | PR de `GET /reports/export` con issues (verde). |

```bash
git switch clase2-testing     # o la que toque
```

## Tarea del laboratorio (Clase 1)

Añadir `GET /users/search?email=<email>`:

- **200** con el usuario si existe
- **422** si el formato del email es inválido
- **404** si no hay ningún usuario con ese email
- con su test en `tests/test_users.py`, siguiendo el estilo del archivo

Lee `CLAUDE.md` antes de empezar: ahí están las convenciones que tu código debe respetar.
