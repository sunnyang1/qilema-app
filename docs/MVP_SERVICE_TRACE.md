# MVP（US-P01～P06）主路由 ↔ 主服务追踪（R-W3）

**目的**：把产品故事与 `backend/app` 中的 **HTTP 入口**、**领域服务**、**依赖注入别名** 对齐，便于评审与增量改造。
**范围**：仅后端；移动端见 `docs/PRD_MODULE_MAP.md`「移动端」一节。

**依赖注入**：服务工厂与 `*Dep` 类型别名定义于 `backend/app/api/dependencies.py`。

---

## 追踪表

| US | 产品故事 | 主 HTTP 路由模块（`app/api/`） | 挂载前缀（相对 `API_V1_PREFIX`） | 主领域服务（`app/services/`） | `dependencies` 中典型别名 |
|----|----------|--------------------------------|----------------------------------|--------------------------------|----------------------------|
| **P01** | 用户认证与安全 | `auth.py` | `/auth` | `UserService`（登录校验用户）、`create_access_token` 等见 `core/security.py` | `UserServiceDep`、`CurrentUserDep` |
| **P01** | （账户） | `users.py` | `/users` | `UserService` | `UserServiceDep`、`CurrentUserDep` |
| **P02** | 每日签到打卡 | `checkins.py` | `/checkins` | `CheckInService` | `CheckInServiceDep` |
| **P03** | 异常预警机制 | `anomalies.py` | `/anomalies` | `AnomalyService`（含与通知协作，见服务内实现） | `AnomalyServiceDep` |
| **P03** | 预警阈值与设置（REST） | `alerts.py` | `/alerts` | `AlertService`（`alert_service.py`） | `AlertServiceDep` |
| **P04** | SOS 紧急求助 | `sos_requests.py` | `/sos` | `SOSService` | `SOSServiceDep` |
| **P05** | 紧急联系人管理 | `contacts.py` | `/contacts` | `EmergencyContactService` | `EmergencyContactServiceDep` |
| **P06** | 消息通知模块 | `notifications.py` | `/notifications` | `app/services/notification` 包暴露的 `NotificationService`（门面） | `NotificationServiceDep` |

**横向能力**：`core/security.py`（JWT/OAuth2 密码流）、`core/auth_policy.py`（公开路径策略）支撑 P01；P06 的发送实现可能经 `notification` 子包内各适配器（短信等），以代码为准。

---

## 与 OpenAPI 分组关系（R-W2）

标签常量见 `backend/app/api/openapi_tags.py`。P02+P03 在 Swagger 中同属 **`签到监测`** 标签（`checkins` + `anomalies` + **`alerts`**）；P01 拆为 **`用户认证与安全`**（auth）与 **`用户设置`**（users）。

---

## Backlog（缺口与建议）

以下条目为 **R-W3 审计结论**，不阻塞文档完成；实现时建议拆成独立用户故事或缺陷单。

| 优先级 | 说明 |
|--------|------|
| ~~**P0**~~ | ~~**`AlertServiceDep` 未在任何 `api/*.py` 路由中使用**~~ — **已关闭（I-W2，2026-04-12）**：`alerts.py` 提供 **`GET` / `PUT /api/v1/alerts/me/settings`**（`CurrentUserDep` + `AlertServiceDep`），用于读写当前用户 `AlertSetting`。 |
| **P1** | **签到未签自动预警链路**：需在代码层明确调度入口（定时任务、worker 或 `checkin` 写后钩子）是否调用 `AlertService`；若仅依赖 `AnomalyService`+通知，应在文档中写明，避免与产品「连续未签到」语义混淆。 |
| **P2** | **P06 与 P03/P04 的集成图**：在架构文档中补「谁调用 `NotificationService.send_*`」的序列图（可选）。 |

---

## 维护

| 日期 | 变更 |
|------|------|
| 2026-04-12 | R-W3 首版：追踪表 + backlog |
| 2026-04-12 | I-W2：`alerts.py` + `/alerts/me/settings`；P0 backlog 关闭 |

相关：**[PRD_MODULE_MAP.md](./PRD_MODULE_MAP.md)**、**[prd.md](./prd.md)** §2.2。
