# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

University workshop ("Taller 3") skeleton: a REST API for music (usuarios, canciones, favoritos) built with FastAPI + SQLModel + Pydantic. The code is **intentionally incomplete** — most work consists of resolving `# TODO` / `# FIXME` comments. Code, comments, identifiers and commit messages are in Spanish; keep that convention.

The workshop tasks (from README.md) that shape what changes are expected:
- Resolve each `# TODO` / `# FIXME`, **one commit per item**, using Pydantic for data validation.
- Add `pre-commit` hooks and a GitHub Actions workflow running **ruff** (lint + format) and **pytest**.
- Implement the automated tests in `tests/test_api.py`.
- Implement two items from README's "Sugerencias de Mejora" (JWT/OAuth2, pagination, PostgreSQL, Docker, logging, cache, stats, file upload).

## Commands

```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

uvicorn main:app --reload          # dev server; Swagger at /docs, ReDoc at /redoc

pytest                              # all tests
pytest tests/test_api.py::TestUsuarios::test_crear_usuario   # single test
pytest -k favorito                  # by keyword

ruff check . && ruff format .       # once ruff is added (not yet in requirements.txt)
```

## Architecture

- `main.py` — FastAPI app: lifespan calls `create_db_and_tables()`, CORS from `settings.cors_origins`, mounts the three routers under `/api/...`, plus `/` and `/health` (checks DB with `SELECT 1`). Endpoint list is in README.md.
- `musica_api/config.py` — `pydantic-settings` reading `.env` (gitignored). `get_settings()` picks Development/Testing (`test_musica.db`)/Production by `ENVIRONMENT`. Default DB `sqlite:///./musica.db`.
- `musica_api/database.py` — module-level `engine` built from settings at import time, `create_db_and_tables()`, and the `get_session` dependency (override this in tests).
- `musica_api/models.py` — per entity: `XBase` (fields), `X` (`table=True`), `XCreate`/`XUpdate` (input), `XRead` (output). **Validators live only on Create/Update** because SQLModel skips validation on table models; they delegate to `utils.py` (`validar_correo`, `validar_año`). `Favorito` has a unique `(id_usuario, id_cancion)` constraint and ORM `cascade_delete` from Usuario/Cancion.
- `musica_api/routers/` — `favoritos.marcar_favorito()` is the shared create-favorite logic (existence checks → 404, duplicate → 400) also used by `usuarios` nested routes. In `canciones`, `/buscar` must stay declared before `/{id}`. Lists accept `offset`/`limit`.
- `tests/test_api.py` — skeleton (bodies still TODO). Intended pattern: in-memory SQLite with `StaticPool`, `app.dependency_overrides[get_session]`, `TestClient`. `pyproject.toml` sets `pythonpath = ["."]` so tests can import root modules.
- Field `año` uses a non-ASCII identifier/column name on purpose (matches README); keep it.
- Leftover movie naming from the original template still exists in tests (commented fixture with `director`/`sinopsis`, `cancions` names).
