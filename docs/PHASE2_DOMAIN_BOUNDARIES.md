# Phase 2 域边界与示例代码（R-W4）

**产品范围**：`docs/prd.md` Phase 2 / `prd.json` **US-P07～US-P10**（健康档案、智能设备、急救资源、用户设置）。
**后端根路径**：`backend/app/`。

---

## 1. US-P07～P10 域边界（主入口）

「主路由」指 `app/api/routes.py` 通过 `include_router` 挂载的模块；「主服务」为常见业务入口，跨域协作在备注中说明。

### US-P07 健康档案

| 边界 | 路径 |
|------|------|
| HTTP | `api/health_records.py`（`/health-records`）、`api/medications.py`（`/medications`）、`api/health_reports.py`（`/health-reports`） |
| 领域服务 | `services/health_record_service.py`、`services/medication_service.py`（含子服务）、`services/health_report_service.py` |
| 模型/模式 | `models/health_record.py`、`models/medication.py`、对应 `schemas/` |
| OpenAPI 标签 | 均为 **`健康档案`**（见 `api/openapi_tags.py`） |

**边界说明**：用药、报告与健康档案在产品上同属「健康档案模块」；急救知识库（`api/knowledge.py`）归属扩展/US-P11，不并入本域验收。

### US-P08 智能设备联动

| 边界 | 路径 |
|------|------|
| HTTP | `api/devices.py`（`/devices`） |
| 领域服务 | `services/device_service.py` |
| 模型/模式 | `models/device.py`、`models/device_data.py`、对应 `schemas/device.py` |
| OpenAPI 标签 | **`智能设备联动`** |

**与 P03 关系**：设备侧异常可进 `anomalies` / `AnomalyService`；本域负责绑定、数据上传与阈值配置等。

### US-P09 急救资源对接

| 边界 | 路径 |
|------|------|
| HTTP | `api/emergency_centers.py`、`api/emergency_resources.py`、`api/aed.py` |
| 领域服务 | `services/emergency_center_service.py`、`emergency_resource_service.py`、`aed_service.py` |
| OpenAPI 标签 | 均为 **`急救资源对接`** |

**边界说明**：120、周边资源、AED 统一归本域；与 Phase 3「与 120 深度对接」的增量在 `prd.json` US-P11 跟踪。

### US-P10 用户设置与个性化

| 边界 | 路径 |
|------|------|
| HTTP | `api/users.py`（账户资料等）、预警相关若未来挂载则见 `MVP_SERVICE_TRACE` backlog |
| 领域服务 | `services/user_service.py`；设置实体见 `models/user_setting_model.py`、`schemas/user_setting.py` |
| OpenAPI 标签 | **`用户设置`**（`/users` 路由组） |

**边界说明**：认证登录仍在 **US-P01** / `api/auth.py`；本域侧重资料与偏好类持久化，与 `UserSetting` 对齐。

---

## 2. `example_*` 示例代码归属（非生产路径）

以下文件用于 **模式演示 / 重构模板**，**默认不挂载**到生产 `api_router`，也不作为 Alembic 必选模型。

| 文件 | 用途 | 生产挂载 | 维护策略 |
|------|------|----------|----------|
| `app/api/example_modern.py` | FastAPI Annotated、Pydantic v2 写法示例 | **否**（未在 `routes.py` 注册） | 保留作教程；若与当前框架版本偏离，以 `dependencies` + 真实路由为准 |
| `app/services/example_refactored_service.py` | `CacheMixin` / `QueryBuilder` 服务模板 | **否**（非 DI 默认实现） | 新服务可复制模式；业务逻辑以 `user_service` 等为准 |
| `app/models/example_modern.py` | SQLAlchemy 2.x `Mapped` 示例（含 `ModernUser`） | **否** | **勿与生产 `models/user.py` 混用**；迁移与表结构以生产模型为准 |

**结论**：示例代码归属 **「开发者参考」**，不参与 US-P 验收；删除或搬迁需单独立项并更新本文档。

---

## 3. 相关链接

- [PRD_MODULE_MAP.md](./PRD_MODULE_MAP.md) — 全模块路径映射
- [MVP_SERVICE_TRACE.md](./MVP_SERVICE_TRACE.md) — MVP US-P01～P06
- [BACKEND_LAYOUT.md](../backend/docs/BACKEND_LAYOUT.md) — 目录职责

---

## 变更记录

| 日期 | 内容 |
|------|------|
| 2026-04-12 | R-W4 首版：Phase2 边界 + example_* 归属 |
