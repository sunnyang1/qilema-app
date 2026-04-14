# PRD v1.1 全局对齐 — 重构方案（Planner）

**依据**：`docs/prd.md` v1.1、`prd.json`（US-P01～US-P12）。
**原则**（Superpowers / Harness）：仓库即真相；**每次会话只交付一个波浪（wave）**；改前基线绿；禁止无迁移计划的大范围物理搬迁。

---

## 1. 目标

将代码库在**可维护边界**上与产品「九大模块 + 横切」一致（§2.1），使团队能按 **US-Pxx** 验收，而不是按历史目录习惯摸索。

---

## 2. 策略选项（择一为主）

| 选项 | 做法 | 优点 | 风险 |
|------|------|------|------|
| **A. 文档优先 + 映射表** | 不先搬目录；在 `backend/docs`、`mobile/client/docs` 建立 **PRD 模块 ↔ 代码路径** 对照表 | 低成本、立刻可审计 | 目录名仍可能不「像产品」 |
| **B. Strangler（绞杀者）** | 新代码进「域」包；旧代码薄封装 re-export，逐模块迁移 | 风险可控、可并行 | 过渡期双结构，需纪律 |
| **C. 大爆炸搬迁** | 一次性重排 `api/`、`services/`、`app/` 目录 | 目录「干净」 | 冲突多、易坏 CI、违背单切片 |
| **D. 仅 API 分组** | 只把 OpenAPI/路由按模块分组（tag、router 前缀） | 对前后端契约友好 | 服务层仍可能杂乱 |
| **E. 客户端按 feature 拆栈** | `mobile/client` 下 `features/<module>/` | 与产品语言一致 | 与 expo-router 文件路由需协调 |

**推荐**：**A + B + D** 组合 — 先做映射与路由/API 语义分组（A、D），再按模块把服务与 schema 迁向清晰边界（B）；**不选 C** 除非单独立项并有专门迁移分支。

---

## 3. PRD 模块 ↔ 现有代码映射（基线，随 R-W1 细化）

| PRD 模块（§2.1） | 后端主要落点（现状） | 客户端主要落点（现状） |
|------------------|----------------------|-------------------------|
| 用户认证与安全 | `api/auth.py`, `api/users.py`, `core/security.py` | `app/login`, `app/register`, `contexts/AuthContext` |
| 签到监测 | `api/checkins.py`, `services/checkin_service.py`, `models/checkin.py` | `app/(tabs)/index`, `signin/history`, `services/checkin` |
| 紧急联系人 | `api/contacts.py`, `services/emergency_contact_service.py` | `app/(tabs)/contacts`, `contacts/*` |
| SOS 紧急求助 | `api/sos_requests.py`, `services/sos_service.py` | `app/(tabs)/sos`, `sos`, `sos-status` |
| 健康档案 | `api/health_records.py`, `services/health_record_service.py` | `health`, `history`, `medication`, `allergies` |
| 智能设备联动 | `api/devices.py`, `services/device_service.py` | `devices/*` |
| 急救资源对接 | `api/emergency_*`, `api/aed.py`, `services/emergency_*`, `aed_service` | `emergency/*` |
| 消息通知 | `api/notifications.py`, `services/notification/*` | Toast / 通知相关 UI、推送适配 |
| 用户设置 | `schemas/user_setting.py`, 用户模型侧设置 | 设置类页面与 `user_setting` |

**异常/知识库等**：与 §5 Phase 2/3 及 US-P11 对齐，单独子表，避免挤进 MVP 映射。

---

## 4. 执行波浪（`refactorProgram.waves`）

每波结束：更新根 `prd.json` 对应 `passes`、写 `progress.txt` 一行、小步提交。

| ID | 内容 | 完成判据（摘要） |
|----|------|------------------|
| **R-W1** | 文档与映射基线 | 对照表入库（backend + mobile 各一篇或统一 `docs/` 链过去）；评审通过 |
| **R-W2** | API 面按模块可导航 | OpenAPI tags / `routes.py` 注释与 PRD 模块名一致；核心回归 pytest 绿 |
| **R-W3** | 服务层与 US-P 对齐度检查 | 每个 US-P01～P06 有一条「主服务 + 主路由」追踪说明；缺口列进 backlog |
| **R-W4** | Phase2 域预清理 | US-P07～P10 相关代码边界声明；废弃示例 `example_*` 收敛策略 |
| **R-W5** | 客户端 feature 目录试验 | 选一个模块试点 `features/` 或约定 screens 前缀，不破坏 expo-router |
| **R-W6** | 横切 US-P12 | CI、监控、客户端 perf 基线与文档交叉引用 |

**说明**：产品 **US-P01～P12** 仍是验收北极星；**R-Wx** 是工程落地切片，二者通过映射表关联，不互相替换 ID。

---

## 5. 风险与缓解

- **范围爆炸**：严格一次一波；任何全目录 rename 必须单独故事 + 迁移清单。
- **测试债务**：backend 全量 `tests/` 历史问题用核心回归 + 目标模块增量测，不混在「映射文档」波里大改。
- **双轨 progress.txt**：旧「阶段 4/5」段落保留作历史；新重构以 `refactorProgram` + 本文件为准。

---

## 6. Generator 下一刀（默认）

执行 **`R-W1`**：在 `backend/docs` 与 `mobile/client/docs`（或 `docs/` 统一入口）增加 **PRD 模块 ↔ 路径** 表，并自链到 `docs/prd.md` §2.1。

---

## 7. Evaluator 检查点

每波结束后：对照本文件「完成判据」；随机抽 2 个 API 路径是否仍可从映射表找到；CI 与本地核心命令是否仍绿。
