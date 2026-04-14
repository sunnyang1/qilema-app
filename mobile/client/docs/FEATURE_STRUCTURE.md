# 客户端 Feature 目录约定（R-W5 试点）

## 原则

- **expo-router 文件路由**仍只使用 `app/`（及 `app/(tabs)/`）；**不**把业务页面直接放进 `app/features` 以免破坏路由生成。
- **`features/<领域>/`**：放可复用的屏级实现（如 `ContactListScreen`）、后续可拆 hooks、子组件。
- **`screens/<领域>/`**：保留为 **路由薄封装**，`export { default } from '@/features/...'` 或一行 re-export，便于历史路径与文档兼容。

## 试点：紧急联系人（US-P05）

| 路由文件 | 薄封装 | 实现 |
|----------|--------|------|
| `app/(tabs)/contacts.tsx` | `export { default } from "@/screens/contacts"` | — |
| `screens/contacts/index.tsx` | `export { default } from "@/features/contacts/ContactListScreen"` | `features/contacts/ContactListScreen.tsx` |

其他模块可逐步按同一模式迁移；未迁移前仍可直接使用 `screens/*`。

## 相关文档

- [PRD_MODULE_MAP.md](../../../docs/PRD_MODULE_MAP.md) — 产品模块 ↔ 路径
- [PERF_BASELINE.md](./PERF_BASELINE.md) — 性能基线
