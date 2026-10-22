# Changelog

Todos los cambios relevantes del proyecto se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el
proyecto usa [versionado semántico](https://semver.org/lang/es/).

## [0.2.0] - 2026-10-22

### Agregado

- Recurso `tasks` con el endpoint `POST /tasks`, que crea una tarea en estado
  `pending` asignada a un usuario existente.
- Validaciones de dominio en `tasks/service.py`:
  - título de 3 a 120 caracteres tras recortar espacios (422);
  - fecha de vencimiento igual o posterior a hoy (422);
  - prioridad de 1 a 5 (422);
  - responsable existente (404);
  - idempotencia: rechaza una tarea `pending` del mismo responsable con el mismo
    título, sin distinguir mayúsculas ni espacios repetidos (409).
- Suite `tests/test_tasks.py`: un test por criterio de aceptación, casos límite y
  un test de integración ruta → servicio → repositorio sin mocks.
- Fixture `_reset_tasks` en `tests/conftest.py` para aislar el almacén de tareas
  entre tests.
- Docstrings estilo Google en `tasks/service.py` y `tasks/repository.py`.
- Sección del recurso `tasks` en el README.

### Cambiado

- `CLAUDE.md`: nueva convención; las validaciones de dominio (rangos, fechas,
  unicidad) viven en `service.py` y no en los schemas.
