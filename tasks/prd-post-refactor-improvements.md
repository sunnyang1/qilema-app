# 后重构改进计划（Superpowers · Planner）

**依据**：`refactorProgram` 已 **complete**（R-W1～R-W6）；审计结论见 `docs/MVP_SERVICE_TRACE.md`、`ADVERSARIAL_REVIEW_REPORT.md`；近期工程讨论（CI、tsc、API 一致性）。
**原则**：与 `tasks/prd-global-refactor.md` 相同 — **一次会话只交付一个波浪**；**仓库即真相**；产品故事仍以 **US-P01～P12** 为北极星，本计划的 **I-Wx** 为工程补齐切片。

---

## 1. 目标

在不大改目录的前提下，补齐 **可验收性**（API 与 PRD 对齐）、**质量门禁可信度**（CI）、**前后端契约一致**（联系人等），并收敛 **文档/进度叙事** 歧义。

---

## 2. 方案选项（Planner 权衡）

| 选项 | 做法 | 优点 | 风险 |
|------|------|------|------|
| **A. 门禁优先** | 先让 `tsc`、再让 Jest 在 CI 中失败即失败 | 回归可见 | Jest 若有历史红测需先修或分阶段 |
| **B. 产品缺口优先** | 先暴露 `AlertService` REST（US-P03） | 直接解锁验收 | 需产品/架构定路径与 schema |
| **C. 契约优先** | 统一 `emergency-contacts` 与客户端详情页 | 减少 404/字段漂移 | 需兼容旧路径或显式废弃 |
| **D. 仅文档** | 只更新 `progress.txt` 与 backlog | 成本极低 | 不解决运行时问题 |

**推荐顺序**：**B+C 可与 A 并行立项**，但 **Generator 执行时仍单波**：默认 **I-W1（门禁）→ I-W3（契约）→ I-W2（Alert）** 若团队更在意「先绿 CI」则 **A→C→B**。

---

## 3. 执行波浪（`improvementProgram.waves`）

每波结束：根 `prd.json` 对应 `passes: true`、`progress.txt` 一段、可合并的小步提交。

| ID | 标题 | 完成判据（摘要） |
|----|------|------------------|
| **I-W1** | CI 前端类型门禁收紧 | `.github/workflows/ci.yml` 的 `frontend-lint` 中 **`pnpm tsc --noEmit` 失败则 job 失败**（去掉「non-blocking」echo）；**不改变** `pnpm test` 的 `|| true` 行为，除非另开故事先修红测 |
| **I-W2** | US-P03：`AlertService` 对外 API 面 | 至少一条 **authenticated** 路由使用 `AlertServiceDep`（读/写与用户相关的预警设置或列表，具体路径以 `contacts`/`users` 域现有惯例为准）；**更新** `docs/MVP_SERVICE_TRACE.md` 表格与 backlog 行；**新增或扩展** `pytest` 覆盖该路由 |
| **I-W3** | 客户端联系人详情 API 与列表一致 | 使用后端实际挂载的 **`/api/v1/contacts`**（见 `routes.py`）；`contactsService` 解包 **`ApiResponseBuilder`**；详情/列表/编辑以 **`id`（数据库主键）** 作为路径参数；**`npx tsc --noEmit`** 通过 |
| **I-W4** | 进度与叙事收敛 | 根 `progress.txt`（或顶部摘要）明确：**全局重构以根 `prd.json` 的 `refactorProgram` 为准**；历史「阶段 4/5」段落标为归档或 **Closed**，避免与 `refactorProgram.status: complete` 冲突 |

**可选后续（不纳入当前 I-W 必做）**：

- `frontend-tests` 去掉 `pnpm test ... || true`，前提是 Jest 全绿或显式 `testPathIgnore` 仅针对废弃目录。
- 对抗性审查 **P2**：选定 1～2 个 `dict` 响应改为 Pydantic 模型。

---

## 4. 与产品故事映射

| 波浪 | 主要支撑 |
|------|----------|
| I-W1 | **US-P12**（质量门禁可信度） |
| I-W2 | **US-P03**（可配置阈值 + 可追踪服务入口） |
| I-W3 | **US-P05**（联系人端到端一致） |
| I-W4 | 元信息（不单独对应某 US-P） |

---

## 5. Generator 下一刀（默认）

执行 **`I-W1`**：改 `ci.yml`，使 `pnpm tsc --noEmit` 在 `frontend-lint` 中为硬门禁；本地 `mobile/client` 跑同一命令确认绿后再推。

**（2026-04-12）** I-W1～I-W4 已全部落地；`improvementProgram.status` 在根 `prd.json` 中为 **`complete`**。后续增量请新开 `improvementProgram` 或产品故事，勿与已归档的 `progress.txt`「阶段 4」旧状态混淆。

---

## 6. Evaluator 检查点

每波：对照上表「完成判据」；**I-W2** 随机抽 Swagger 中一条新路由与 `MVP_SERVICE_TRACE` 是否一致；**I-W3** 用网络面板或 mock 确认详情请求前缀与列表一致。
