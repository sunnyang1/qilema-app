# 后端目录与分层约定（US-001）

本仓库采用单包布局 **`backend/app/`**（等价于常见教程里的「项目根下的 `app` 包」）。不在磁盘上强制使用名为 `config/`、`routes/` 的顶层目录名；职责由下表映射。

## 目录职责

| 路径 | 职责 | 典型内容 |
|------|------|----------|
| `app/core/` | 横切能力与应用内核 | `config.py`（Settings）、`database.py`、`security.py`、`middleware.py`、`error_handlers.py`、缓存/指标/容器等 |
| `app/models/` | SQLAlchemy ORM 模型 | 表映射、`relationship`、`@validates` |
| `app/services/` | 业务逻辑与持久化编排 | `*Service`、调用 `Session`、领域规则；可含子包（如 `notification/`） |
| `app/api/` | HTTP 接口层 | `routes.py` 集中挂载 v1 子路由、各 `*.py` 路由模块、`dependencies.py`、`openapi_tags.py`（OpenAPI 分组与 PRD §2.1 对齐，R-W2） |
| `app/schemas/` | Pydantic 请求/响应与校验 | API 入参/出参模型，与 ORM 分离 |
| `tests/` | 自动化测试 | `pytest`、与 `app` 并行的 `tests/` 根（工作目录常为 `backend/`） |

第三方边界简述：**SQLAlchemy** 仅出现在 `models`（及迁移若存在）；**FastAPI 路由**仅通过 `app/api` 注册进 `main.py` 的 `api_router`；**Pydantic** 以 `schemas` 为主，避免在路由里堆业务规则。

依赖注入与服务分层约定见 **[DI_AND_SERVICES.md](./DI_AND_SERVICES.md)**（与 **US-002** 对齐）。

产品与 API 模块对照见 **[PRD_MODULE_MAP.md](./PRD_MODULE_MAP.md)**（链到仓库根目录 `docs/PRD_MODULE_MAP.md`，R-W1）。

## 硬约定（与代码一致）

1. **对外 HTTP API**：仅由 `main.py` 挂载 `app.api.api_router`（定义于 `app/api/routes.py`），统一前缀来自 `app.core.config.settings.API_V1_PREFIX`（默认 `/api/v1`）。
2. **运行时配置**：单一入口为 `app.core.config.settings`（`pydantic-settings`），环境变量与 `.env` 在此收敛；业务代码不直接读 `os.environ`（测试等特殊场景除外）。
3. **依赖注入**：服务与 DB 等通过 `app/api/dependencies.py` 中 `Annotated[..., Depends(...)]` 类型别名注入路由；容器见 `app/core/container.py`。

## 后续可选重构（非 US-001 范围）

若将来要物理拆分 `config/`、`routes/` 等顶层目录，应单独立项：同步修正 **import 路径、pytest、`PYTHONPATH`、Docker/CI**，并保留迁移前对照表。

## 质量门控（项目约定命令）

当前 **`pytest tests/` 全量**仍存在历史失败用例（与本次目录文档无关）；合并前在 `backend/` 下至少执行下列**核心回归**（与 `progress.txt` / US-001 收口一致）：

```bash
cd backend && python -m pytest \
  tests/test_api_us004.py \
  tests/test_model_validations.py \
  tests/test_security.py \
  tests/test_exception_system.py \
  tests/test_encoding_middleware.py \
  tests/test_dependencies_injection_us002.py \
  -q
```

`tests/test_database_migration.py` 在缺少 `scripts/migrate_sqlite_to_postgresql.py` 时整模块跳过。全量绿测与覆盖率目标见 **US-006**。
