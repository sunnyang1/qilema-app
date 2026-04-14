# 依赖注入与服务（US-002）

## 两条路径（并存）

| 机制 | 位置 | 用途 |
|------|------|------|
| **FastAPI `Depends` + `Annotated`** | `app/api/dependencies.py` | **HTTP 路由主路径**：每个请求一个 `Session`，`get_*_service(db)` 返回具体服务类实例。 |
| **dependency-injector `Container`** | `app/core/container.py` | 可选：脚本、批处理、或需从 YAML 注入 `Configuration` 的场景；`get_container()` / `init_container()` / `reset_container()`。 |

路由层**优先**使用 `dependencies.py` 中的 `*ServiceDep`，与 FastAPI 生命周期一致；容器用于需要统一从配置文件装配引擎/连接池时的补充入口。

## 容器要点

- `Container`：`providers.Configuration()`、`database`（Singleton 引擎）、`db_session`（Factory）、`redis`、各 `*_service` Factory。
- `init_container(config_file=None)`：可 `from_yaml` 加载；未传文件时依赖代码内默认或后续对 `container.config` 的赋值。
- `reset_container()`：测试或进程内重置单例。

## 多环境配置

- **运行时**：`app.core.config.settings`（`pydantic-settings`），由 `ENVIRONMENT`、`.env` 等驱动（见 `Settings`）。
- **容器内**：`Container.config` 可与 YAML 对齐键名（如 `database.url`）；与 `settings` 并行存在时，以 **路由/服务实际读取的来源** 为准，避免两处漂移——新代码优先 `settings`。

## 接口抽象（Protocol）

- `app/core/service_protocols.py` 定义 **`typing.Protocol`**，描述路由/测试关心的最小方法集。
- 具体类（如 `UserService`）**不必继承** Protocol；`isinstance(x, UserServiceProtocol)` 在 `@runtime_checkable` 下可用于测试与静态检查。

## 可测试性

- **路由**：对 `get_db` / `get_user_service` 使用 `app.dependency_overrides`（FastAPI 文档）。
- **容器**：`reset_container()` 后重新 `init_container()`；服务实例可对 `Session` 使用替身。

## 相关测试

- `tests/test_container.py`：容器生命周期与 provider。
- `tests/test_config_loading.py`：YAML 与容器配置。
- `tests/test_dependencies_injection_us002.py`：`dependencies` 工厂与 Protocol 结构化子类型。
