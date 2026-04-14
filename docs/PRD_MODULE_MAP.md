# PRD §2.1 模块 ↔ 代码映射（R-W1 基线）

**来源**：`docs/prd.md` v1.1 §2.1、`prd.json`（US-P01～US-P12）。
**维护**：产品模块或路由有重大调整时同步更新本表；物理目录搬迁前先改本文件再动代码。

---

## 总览

| PRD 模块（§2.1） | 产品故事 ID | 说明 |
|------------------|-------------|------|
| 用户认证与安全 | US-P01 | JWT + OAuth2，注册/登录 |
| 签到监测 | US-P02、US-P03 | 签到 + 异常预警（产品上分两模块，后端共享 checkin/anomaly 能力） |
| 紧急联系人 | US-P05 | |
| SOS 紧急求助 | US-P04 | |
| 健康档案 | US-P07 | 含病史/用药/过敏等 |
| 智能设备联动 | US-P08 | |
| 急救资源对接 | US-P09 | 医院、AED、急救资源等 |
| 消息通知 | US-P06 | 短信/推送等渠道 |
| 用户设置 | US-P10 | 偏好、阈值等与 `UserSetting` 相关 |

**扩展能力（未单独列为 §2.1 顶层模块）**：急救知识库、用药提醒、健康报告、异常监测 API 等见下文「扩展与 Phase 2/3」。

---

## 后端（`backend/app/`）

路径均相对于 `backend/app/`。HTTP 前缀默认为 `settings.API_V1_PREFIX`（默认 `/api/v1`），与 `app/api/routes.py` 一致。

| PRD 模块 | US-P | 路由模块 | `routes.py` 挂载前缀 | OpenAPI tag（R-W2，`app/api/openapi_tags.py`） | 主要服务 | 主要模型/模式 |
|----------|------|----------|----------------------|-----------------------------------------------|----------|----------------|
| 用户认证与安全 | P01 | `api/auth.py` | `/auth` | `用户认证与安全` | `user_service`、安全/token | `User`、`schemas/token` |
| 用户设置 | P10 | `api/users.py` | `/users` | `用户设置` | `user_service` | `User`、`schemas/user_setting` |
| 签到监测 | P02 | `api/checkins.py` | `/checkins` | `签到监测` | `checkin_service` | `CheckIn`、`schemas/checkin` |
| 签到监测 / 异常预警 | P03 | `api/anomalies.py` | `/anomalies` | `签到监测` | `anomaly_service` 等 | `Anomaly`、`schemas/anomaly` |
| 签到监测 / 预警设置 | P03 | `api/alerts.py` | `/alerts` | `签到监测` | `alert_service` | `AlertSetting`、`schemas/alert` |
| SOS 紧急求助 | P04 | `api/sos_requests.py` | `/sos` | `SOS紧急求助` | `sos_service` | `SosRequest`、`schemas/sos_request` |
| 紧急联系人 | P05 | `api/contacts.py` | `/contacts` | `紧急联系人` | `emergency_contact_service` | `EmergencyContact`、`schemas/emergency_contact` |
| 消息通知 | P06 | `api/notifications.py` | `/notifications` | `消息通知` | `notification` 子包各服务 | `Notification` 等 |
| 健康档案 | P07 | `api/health_records.py` | `/health-records` | `健康档案` | `health_record_service` | `HealthRecord`、`schemas/health_record` |
| 健康档案 | P07 | `api/medications.py` | `/medications` | `健康档案` | `medication_service` | `Medication` 等 |
| 健康档案 | P07 | `api/health_reports.py` | `/health-reports` | `健康档案` | `health_report_service` | 与报告相关 schema |
| 智能设备联动 | P08 | `api/devices.py` | `/devices` | `智能设备联动` | `device_service` | `Device`、`schemas/device` |
| 急救资源对接 | P09 | `api/emergency_centers.py` | `/emergency-centers` | `急救资源对接` | `emergency_center_service` | `EmergencyCenter` 等 |
| 急救资源对接 | P09 | `api/emergency_resources.py` | `/emergency-resources` | `急救资源对接` | `emergency_resource_service` | `EmergencyResource` 等 |
| 急救资源对接 | P09 | `api/aed.py` | `/aed` | `急救资源对接` | `aed_service` | AED 相关模型 |
| 横切 | P12 | `core/security.py`、`core/middleware.py`、`core/error_handlers.py` | — | — | — | — |

| 扩展 · 急救知识库 | P11 | `api/knowledge.py` | `/knowledge` | `急救知识库` | `knowledge_service` | 文章/分类等 |

**集中路由注册**：`app/api/routes.py` → `create_api_v1_router()`；标签常量 **`app/api/openapi_tags.py`**（R-W2）。

**扩展与 Phase 2/3**：`api/knowledge.py`（OpenAPI tag **`急救知识库`**，US-P11 相关）；与 PRD §5 Phase 3 规划条目对应时在迭代中补全本表「验收入口」列。

---

## 移动端（`mobile/client/`）

路径均相对于 `mobile/client/`。路由以 **expo-router** 文件为准；`_layout.tsx` 中声明但尚无对应文件的屏幕为 **已规划待补文件**。

| PRD 模块 | US-P | 主要路由/入口（`app/`） | 说明 |
|----------|------|-------------------------|------|
| 用户认证与安全 | P01 | `app/login.tsx`、`app/register.tsx` | 登录/注册 |
| 用户认证与安全 | P01 | `contexts/AuthContext.tsx`、`components/RouteGuard.tsx` | 会话与路由守卫 |
| 签到监测 | P02 | `app/(tabs)/index.tsx`（首页/签到） | 入口见各 screen 实现 |
| 签到监测 | P02 | `app/signin/history.tsx` | `_layout` 已登记「签到历史」；若磁盘无文件则由 expo-router 生成或待补 |
| 异常预警 | P03 | 与设置/通知联动 | 阈值等多半在用户设置或后端策略；UI 分散时需随功能迭代标到具体屏 |
| SOS 紧急求助 | P04 | `app/(tabs)/sos.tsx`、`app/sos.tsx`、`app/sos-status.tsx` | Tab 与栈内 SOS 流 |
| 紧急联系人 | P05 | `app/(tabs)/contacts.tsx`、`app/contacts.tsx`、`app/contacts/edit.tsx`、`app/contact-detail.tsx` | |
| 健康档案 | P07 | `app/(tabs)/health.tsx` | Tab 健康入口 |
| 健康档案 | P07 | `app/health.tsx`、`app/history.tsx`、`app/medication.tsx`、`app/allergies.tsx` | `_layout` 已登记；文件若未创建则待实现 |
| 急救知识库 | P11 | `app/(tabs)/knowledge.tsx` | Tab 知识库 |
| 急救知识库 | P11 | `app/knowledge/categories.tsx`、`articles.tsx`、`article-detail.tsx` | `_layout` 已登记；子目录若未创建则待实现 |
| 用药提醒 | P07/P11 | `app/medication/reminders.tsx`、`medication/add.tsx` | `_layout` 已登记 |
| 智能设备联动 | P08 | `app/devices/list.tsx`、`app/devices/data.tsx` | `_layout` 已登记 |
| 急救资源对接 | P09 | `app/emergency/hospitals.tsx`、`app/emergency/aed.tsx` | `_layout` 已登记 |
| 消息通知 | P06 | `react-native-toast-message`（根 `_layout`）、各业务成功/失败提示 | 推送通道随原生配置扩展 |
| 用户设置 | P10 | 分散在主题/用户相关 hooks 与后续设置页 | 与 `UserSetting` 后端契约对齐时补链接 |

**根布局**：`app/_layout.tsx`（含 `Stack.Screen` 清单）、`app/(tabs)/_layout.tsx`（底部 Tab）。

**性能基线**：见 `mobile/client/docs/PERF_BASELINE.md`（US-P12 客户端部分）。

---

## 相关文档

| 文档 | 用途 |
|------|------|
| [docs/prd.md](./prd.md) | 产品需求正文 |
| [MVP_SERVICE_TRACE.md](./MVP_SERVICE_TRACE.md) | **R-W3**：US-P01～P06 主路由↔主服务追踪与 backlog |
| [PHASE2_DOMAIN_BOUNDARIES.md](./PHASE2_DOMAIN_BOUNDARIES.md) | **R-W4**：US-P07～P10 域边界与 `example_*` 示例归属 |
| [mobile/client/docs/FEATURE_STRUCTURE.md](../mobile/client/docs/FEATURE_STRUCTURE.md) | **R-W5**：`features/` 试点与 expo-router 约定 |
| [backend/docs/BACKEND_LAYOUT.md](../backend/docs/BACKEND_LAYOUT.md) | 后端目录职责 |
| [backend/docs/DI_AND_SERVICES.md](../backend/docs/DI_AND_SERVICES.md) | 依赖注入与服务 |
| [tasks/prd-global-refactor.md](../tasks/prd-global-refactor.md) | 全局重构波浪 R-Wx |
| [DEPLOYMENT.md](../DEPLOYMENT.md) | **R-W6**：部署步骤、`/health` 与 `/metrics`（Prometheus） |
| [ci.yml](../.github/workflows/ci.yml)（`frontend-tests` job） | **R-W6**：`pnpm run test:perf`（Reassure）在 CI 中运行 |

---

## 变更记录

| 日期 | 内容 |
|------|------|
| 2026-04-12 | R-W1：首版基线，与当前 `routes.py` 及 `app/` 路由声明对齐 |
| 2026-04-12 | R-W2：OpenAPI 标签与 §2.1 对齐，`openapi_tags.py` 为唯一字符串来源 |
| 2026-04-12 | R-W6：`PERF_BASELINE`、`DEPLOYMENT`、CI 与 US-P12 横切交叉引用 |
