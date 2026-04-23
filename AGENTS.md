<!-- AGENTS.md - Project Knowledge Base for AI Coding Agents -->

**Note**: This file provides project-wide context for AI coding agents. All information is derived from actual source files and configurations, not assumptions. The project primarily uses **Chinese** for comments and documentation.

---

## Project Overview

**Qilema App (起了吗 App)** is an emergency medical assistance platform targeting people living alone (elderly care / solo dwellers). Core features:

- **Daily Check-in** — Users confirm their safety status via daily check-ins
- **Anomaly Alerts** — Automatic alerts triggered when check-in is overdue
- **SOS Emergency** — One-tap emergency signal with automatic location retrieval
- **Emergency Contacts** — Add and manage emergency contacts
- **Health Records** — Medical history, medications, allergies
- **Medication Reminders** — Scheduled reminders with logging
- **Emergency Resources** — Nearby hospitals and AED device locations
- **Knowledge Base** — First-aid articles and categories

**Repository**: `https://github.com/sunnyang1/qilema-app.git`
**License**: MIT

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.8–3.12 + FastAPI 0.104.1 + SQLAlchemy 2.0.23 + Pydantic v2 |
| Mobile | React Native 0.81.5 + Expo 54.0.33 + TypeScript |
| Database | PostgreSQL 15 (prod) / SQLite (dev) + Redis 7 |
| Deployment | Docker + Docker Compose + Nginx + Kubernetes manifests |
| CI/CD | GitHub Actions |

---

## Project Structure

```
qilema-app/
├── backend/                  # Python FastAPI backend
│   ├── main.py               # FastAPI entry point (lifespan context manager)
│   ├── app/
│   │   ├── api/              # API routers (Annotated dependency injection)
│   │   ├── core/             # Config, DB, cache, security, middleware, exceptions
│   │   ├── models/           # SQLAlchemy 2.x models (with BaseModelMixin)
│   │   ├── schemas/          # Pydantic v2 validation/serialization models
│   │   └── services/         # Business service layer (notification subpackage)
│   ├── tests/                # pytest test suite
│   ├── migrations/           # DB migrations
│   ├── pyproject.toml        # Python project config (deps, black, isort, mypy, pytest)
│   ├── requirements.txt      # Runtime dependencies
│   └── Dockerfile            # Multi-stage build (non-root user)
├── mobile/                   # React Native mobile (pnpm workspace)
│   ├── client/               # Expo app source (file-based routing)
│   ├── server/               # Production server build
│   └── package.json          # Workspace root config
├── nginx/                    # Nginx reverse proxy
├── k8s/                      # Kubernetes deployment manifests
├── scripts/                  # Ops scripts
├── docs/                     # Project docs (architecture, deployment, dev, CI/CD)
├── docker-compose.yml        # Base services (postgres + redis + backend + nginx)
├── docker-compose.dev.yml    # Dev overrides (hot reload, relaxed resources)
├── docker-compose.prod.yml   # Prod overrides (strict resources, persistence)
└── .github/workflows/        # GitHub Actions
```

---

## Backend Architecture

### Entry Point & Startup

- **Main entry**: `backend/main.py`
- **Startup commands**:
  ```bash
  cd backend
  uvicorn main:app --reload
  # or
  python -m uvicorn main:app --reload --env-file .env.dev
  ```
- Uses `lifespan` async context manager (FastAPI 0.135.x style); do NOT use `@app.on_event("startup")`.
- Health check endpoints: `GET /health` and `GET /api/v1/health`.

### Core Modules (`app/core/`)

| Module | Responsibility |
|--------|----------------|
| `config.py` | `Settings` class via `pydantic-settings`; loads `.env` / `.env.testing`; includes production security validations |
| `database.py` | SQLAlchemy 2.x `DeclarativeBase`, engine/session manager; supports SQLite (NullPool) and PostgreSQL (QueuePool) |
| `security.py` | JWT, password hashing, current user dependencies (`get_current_user` / `get_current_active_user` / `get_current_admin`) |
| `cache.py` / `cache_mixin.py` / `cache_config.py` | Redis cache wrappers, cache decorators, `CacheMixin` |
| `query_builder.py` | Chainable `QueryBuilder` + `paginate()` helper |
| `middleware.py` | Request logging, request ID, encoding fix middleware |
| `error_handlers.py` | Global exception handlers |
| `response_builder.py` | Unified API response format wrapper |
| `prometheus_metrics.py` | Prometheus `/metrics` endpoint |

### Model Layer (`app/models/`)

- Base class: `app.core.database.Base` (`DeclarativeBase`)
- Universal mixin: `BaseModelMixin` providing `to_dict()`, `to_schema()`, `from_dict()`
- Key entities: `User`, `CheckIn`, `Alert`, `SOSRequest`, `EmergencyContact`, `HealthRecord`, `Device`, `DeviceData`, `MedicationReminderSchedule`, `Notification`, `EmergencyCenter`, `EmergencyResource`, `KnowledgeArticle`, `Anomaly`, etc.
- `models/__init__.py` imports models in dependency order to avoid circular references.
- Modern models should use `Mapped[]` type annotations + `mapped_column()` (SQLAlchemy 2.x style).

### Schema Layer (`app/schemas/`)

- Pydantic v2 schemas only.
- Use `model_config = {"from_attributes": True}` instead of deprecated `orm_mode = True`.
- Correct inheritance order for generics: `class ListResponse(BaseModel, Generic[T])` (NOT `Generic[T], BaseModel`).

### Service Layer (`app/services/`)

- `BaseService[ModelType]` in `base_service.py` provides generic CRUD + Redis caching + `QueryBuilder` integration.
- Domain services: `UserService`, `CheckInService`, `SOSService`, `EmergencyContactService`, `HealthRecordService`, `DeviceService`, `AlertService`, `MedicationService`, `AnomalyService`, `AEDService`, `EmergencyCenterService`, `KnowledgeBaseService`, `HealthReportService`, etc.
- Notification services are grouped under `services/notification/`:
  - `notification_facade.py` — main facade
  - `notification_sender_service.py`
  - `notification_template_service.py`
  - `circuit_breaker_service.py`
  - `notification_stats_service.py`

### API Layer (`app/api/`)

- Router modules per domain: `users.py`, `auth.py`, `checkins.py`, `contacts.py`, `sos_requests.py`, `health_records.py`, `medications.py`, `alerts.py`, `devices.py`, `notifications.py`, `emergency_centers.py`, `emergency_resources.py`, `knowledge.py`, `anomalies.py`, `aed.py`, `health_reports.py`.
- Dependencies defined in `dependencies.py` using `Annotated[..., Depends(...)]` pattern.
- Example:
  ```python
  DbSession = Annotated[Session, Depends(get_db)]
  UserServiceDep = Annotated[UserService, Depends(get_user_service)]
  ```

---

## Mobile Architecture (`mobile/`)

- **Package manager**: pnpm 9 (monorepo workspace)
- **Client framework**: Expo 54.0.33 + React Native 0.81.5 + TypeScript
- **Router**: Expo Router (file-based routing)
- **Entry**: `mobile/client/app/_layout.tsx`
- **Key commands**:
  ```bash
  cd mobile
  pnpm install
  cd client
  pnpm start        # expo start --web --clear
  pnpm test         # jest
  pnpm lint         # expo lint
  pnpm test:perf    # reassure performance tests
  ```
- Client uses path alias `@/*` mapped to `./*`.
- Main directories:
  - `app/` — routes and screens
  - `components/` — reusable UI components
  - `services/` — API service modules (`auth.ts`, `sos.ts`, `contacts.ts`, `checkin.ts`, `storage.ts`)
  - `hooks/` — custom React hooks (`useColorScheme`, `useTheme`, `useSafeRouter`)
  - `contexts/` — React contexts (`AuthContext`)
  - `constants/` — app constants and themes
  - `utils/` — utilities (`api.ts`, `auth-interceptor.ts`)
  - `features/` — feature-based modules

---

## Build & Development Commands

### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run dev server
uvicorn main:app --reload

# Run tests
pytest tests/ -v --cov=app --cov-report=term

# Run specific tests
python -m pytest tests/test_user_service.py tests/test_cache_mixin.py -v

# Code formatting
black .
isort .
flake8
mypy app/
```

### Mobile

```bash
cd mobile
pnpm install
cd client

# Start dev server
pnpm start

# Run tests
pnpm test
pnpm test:perf

# Lint
pnpm lint
pnpm tsc --noEmit
```

### Docker Compose

```bash
# Development
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Pre-commit (repository root)

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

---

## Code Style Guidelines

- **Language**: Python code comments and docstrings are written in **Chinese**.
- **Formatter**: Black, line length 88 (matching pyproject.toml).
- **Import sorter**: isort with `profile = "black"`.
- **Linter**: flake8 with `max-line-length=120` and ignores `E203,W503,E402,E501,F401,F541,F811,F841`.
- **Type checker**: mypy with `disallow_untyped_defs = true`.
- **SQLAlchemy 2.x**: Use `Mapped[int] = mapped_column(primary_key=True)` instead of `Column(Integer, primary_key=True)`.
- **Pydantic v2**: Use `model_config = {"from_attributes": True}`; correct generic inheritance order.
- **FastAPI dependencies**: Prefer `Annotated[..., Depends(...)]` style.

---

## Testing Strategy

### Backend Tests (`backend/tests/`)

- **Framework**: pytest with `pytest-asyncio`, `pytest-cov`, `httpx`.
- **Config**: `pyproject.toml` `[tool.pytest.ini_options]`; `conftest.py` provides `db` fixture using SQLite in-memory.
- **Markers**:
  - `slow` — slow tests (deselect with `-m "not slow"`)
  - `integration` — integration tests
  - `smoke`, `regression`, `stress`, `full` — defined in `conftest.py`
- **Coverage**: source = `app`; omits `tests/`, `migrations/`, `__pycache__/`.
- **Test categories present**:
  - Unit tests for models, services, cache, query builder, config
  - API compliance & response format tests
  - Integration tests for notification pipeline
  - Performance / load tests
  - Security tests (secret key, encryption, CORS)
  - Encoding / middleware tests

### Mobile Tests (`mobile/client/`)

- **Framework**: Jest with `jest-expo` preset.
- **Performance**: Reassure for React Native render performance.
- Setup file: `jest.setup.js`.

---

## CI/CD Pipeline

Located in `.github/workflows/`:

| Workflow | Triggers | Purpose |
|----------|----------|---------|
| `ci.yml` | PR / push to `main`, `develop` | pre-commit, backend tests (matrix 3.10/3.11/3.12), frontend lint, frontend tests |
| `build.yml` | PR / push to `main` / tags `v*` | Validate compose, build & push Docker images (backend + nginx), Trivy security scan |
| `deploy.yml` | push to `main` / tags `v*` / manual | SSH deploy to staging (auto) or production (tag), DB backup, smoke test, rollback on failure |
| `pr-checks.yml` | PR | Dependency review |
| `pr-title-check.yml` | PR | Conventional Commits title validation |

**Deployment behavior**:
- `main` branch → automatic staging deployment
- `v*` tag → automatic production deployment
- Production deploy creates a DB backup before migration and supports rollback on failure.

---

## Deployment Architecture

### Docker Compose

- **Base** (`docker-compose.yml`): PostgreSQL 15, Redis 7, Backend (FastAPI on 8000), Nginx (80/443).
- **Dev** (`docker-compose.dev.yml`): Source mount for hot reload, SQLite allowed, DEBUG=True, test secrets.
- **Prod** (`docker-compose.prod.yml`): Strict resource limits, persistent named volumes, AOF enabled for Redis, DEBUG=False.

### Kubernetes (`k8s/`)

Manifests for: namespace, backend deployment/service/HPA/configmap/secret, nginx deployment/service/configmap, ingress, postgres deployment/service/pvc/configmap/secret, redis deployment/service/pvc/configmap.

### Nginx (`nginx/`)

- Custom `nginx.conf` + `conf.d/backend.conf`
- SSL certs in `nginx/ssl/`
- Health check endpoint configured

---

## Security Considerations

- **SECRET_KEY**: Minimum 64 bytes; production requires strong random key with 3+ character types. Generate via `python backend/scripts/generate_secret_key.py`.
- **CORS**: Strict validation in production — wildcards (`*`) are rejected for origins, methods, and headers.
- **DEBUG**: Forbidden in production; `Settings` validator raises `ValueError` if `ENVIRONMENT=production` and `DEBUG=True`.
- **Secrets scanning**: pre-commit hooks include `detect-secrets` (with `.secrets.baseline`) and `gitleaks` (with `.gitleaks-baseline.json`).
- **Docker**: Backend image runs as non-root user (`appuser`, UID 1001); multi-stage build minimizes attack surface.
- **Rate limiting**: `slowapi` configured with default `200/minute`.
- **Encryption**: `ENCRYPTION_KEY` for sensitive data encryption at rest.

---

## Key Configuration Files

| File | Purpose |
|------|---------|
| `backend/pyproject.toml` | Project metadata, dependencies, black/isort/mypy/pytest/coverage configs |
| `backend/requirements.txt` | Runtime Python dependencies (single source for Docker) |
| `backend/config.dev.yaml` | Dev YAML config (DB=SQLite, debug logging, simulated notifications) |
| `backend/config.prod.yaml` | Prod YAML config |
| `mobile/client/package.json` | Expo client deps & scripts |
| `mobile/tsconfig.json` | TypeScript base config extending `expo/tsconfig.base` |
| `docker-compose.yml` / `.dev.yml` / `.prod.yml` | Orchestration per environment |
| `.pre-commit-config.yaml` | Git hooks: secrets detection, black, isort, flake8, yamllint |
| `.env` / `.env.dev` / `.env.testing` | Environment variables (not committed) |

---

## Development Conventions

### Database & Models
- Use SQLAlchemy 2.x `DeclarativeBase` and `Mapped[]` annotations.
- Add composite indexes in `__table_args__` for query-heavy fields.
- Choose lazy loading strategy by usage frequency:
  - High freq / large data: `lazy="dynamic"`
  - Medium freq / small data: `lazy="select"` (default)
  - One-to-one / always needed: `lazy="joined"`
- Note: `lazy="dynamic"` + `cascade="delete-orphan"` has compatibility issues in SQLAlchemy 2.x; prefer `lazy="select"` when cascade is needed, or clean up manually.

### Caching
- `BaseService` includes built-in Redis caching for `get_by_id`, `create_record`, `update_record`, `delete_record`.
- Cache key pattern: `{cache_prefix}:{pk_column}:{id_value}`.
- Use `CacheMixin` for custom cache invalidation logic.

### Services
- Inherit from `BaseService[ModelType]` and set `model_class`, `cache_prefix`, `cache_ttl`.
- Use `QueryBuilder` for complex list queries instead of raw SQLAlchemy.
- Use `BaseService.transaction(db)` context manager for multi-step operations.

### API Responses
- Use `response_builder.py` for consistent envelope format:
  ```json
  { "code": 200, "message": "OK", "data": { ... } }
  ```

### Notifications
- Notification services are facade-based under `services/notification/`.
- Supports simulated adapters (configurable success rate/delay) for dev/testing.
- Circuit breaker and degradation strategies are configurable via `Settings`.

---

## Important Notes for Agents

1. **Do not assume English for comments** — the codebase uses Chinese extensively in docstrings and inline comments.
2. **Do not use `@app.on_event("startup")`** — use `lifespan` context manager in `main.py`.
3. **Do not use Pydantic v1 patterns** — no `orm_mode = True`, no `.dict()`, no `.json()`; use `model_config`, `model_dump`, `model_dump_json`.
4. **Do not use SQLAlchemy 1.x patterns** — no `declarative_base()`, no `Column(...)` without `Mapped[]` in new files.
5. **Requirements single source of truth**: `requirements.txt` is used by Docker; `pyproject.toml` is used for development tooling. Keep them in sync when adding packages.
6. **Never commit secrets** — the repo has aggressive pre-commit hooks and baseline files for secrets detection.
7. **PR title format** must follow Conventional Commits (e.g., `feat:`, `fix:`, `refactor:`, `docs:`, `ci:`) — enforced by `pr-title-check.yml`.

---

*Last updated: 2026-04-23*
