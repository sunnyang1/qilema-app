# 移动端性能基线（US-P12 客户端部分）

## 技术栈（记录日：请在更新 Expo/RN 时同步修改）

| 项 | 版本/说明 |
|----|-----------|
| Expo SDK | 54（见 `mobile/client/package.json`） |
| 路由 | expo-router |
| 新架构 | `newArchEnabled: true`（`app.config.ts`） |

## 建议复现场景（填设备与数字）

在真机或模拟器上各跑 3 次取中位数，记录日期与 Git SHA。

| 场景 | 设备 | 冷启动→首屏可交互 (ms) | Tab 切换卡顿主观 1–5 | 备注 |
|------|------|--------------------------|------------------------|------|
| 冷启动 | | | | |
| 登录后进入 Tab 首页 | | | | |
| 连续切换 5 个 Tab | | | | |

测量方式（任选其一，保持前后一致）：

- React Native：`npx react-native log-android` / Xcode Instruments 粗略观察；
- Expo：开发模式下 **不计入** 正式基线，以 **release** 或 **production** 构建为准。

## 已实施优化（与基线对比时请注明）

- `react-native-screens`：`enableFreeze(true)`（根 `_layout`）
- 底部 Tab：`freezeOnBlur: true`，非当前 Tab 界面冻结，减少后台重渲染与 JS 压力

## 自动化渲染性能回归（Reassure）

在 `mobile/client` 下：

| 命令 | 说明 |
|------|------|
| `pnpm run test:perf` | 跑 `perf/*.perf-test.tsx`，与 `.reassure/baseline.perf` 对比并生成 `.reassure/output.md`（本地/CI） |
| `pnpm run test:perf:baseline` | 在**有意更新基线**时重写 `baseline.perf`（例如 Tab 图标或场景变更后） |

首次克隆或基线缺失时，先跑一次 `pnpm run test:perf:baseline` 再提交 `baseline.perf`。对比结果对机器负载敏感，若持续误报可重采 baseline 或在 PR 中说明。

## CI 中的回归（与仓库对齐）

GitHub Actions **`.github/workflows/ci.yml`** 任务 **`frontend-tests`** 在 `mobile/client` 下执行 **`pnpm run test:perf`**（与上表命令一致；本地若无 pnpm 可用 `npm run test:perf`）。合并前若修改 Tab 布局或 perf 场景，请确认该 job 仍绿或已在 PR 中更新基线。

## 相关链接

- 仓库根目录 **`docs/PRD_MODULE_MAP.md`** — 产品模块 ↔ 路径总表（含本文件与 **R-W6** 交叉引用）
- **`mobile/client/docs/FEATURE_STRUCTURE.md`** — R-W5 客户端 `features/` 约定

## 后续候选（未做）

- 长列表换 `FlashList`、图片统一 `expo-image` 与固定尺寸
- 对重型屏做 `React.memo` / 拆分 selector
