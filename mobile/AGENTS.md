# Mobile 项目 - 开发者指南

## 项目概述
起了吗 App Mobile 端，基于 Expo + React Native + TypeScript 构建。

## 架构模式

### 1. 主题系统
- 使用 `theme-warm.ts` 作为主要主题配置
- 通过 `useTheme()` Hook 获取主题
- **重要**: 始终使用 `Theme` 类型，避免 `any`

```typescript
// ✅ 正确
import type { Theme } from '@/types';
const createStyles = (theme: Theme) => StyleSheet.create({...});

// ❌ 错误
const styles = (theme: any) => StyleSheet.create({...});
```

### 2. 样式优化
- 使用 `createStyles` 命名样式创建函数
- 使用 `useMemo` 缓存样式对象

```typescript
const createStyles = (theme: Theme) => StyleSheet.create({...});

function Component() {
  const { theme } = useTheme();
  const styles = useMemo(() => createStyles(theme), [theme]);
  // ...
}
```

### 3. 错误处理
- 使用 Error Boundary 捕获渲染错误
- 服务层保留 `console.error`，移除 `console.log`
- 使用 Toast 显示用户友好的错误提示

### 4. 类型定义
所有类型定义放在 `client/types/` 目录：
- `theme.ts` - 主题相关类型
- 其他类型按功能模块组织

### 5. 组件拆分原则
当组件超过 300 行时，考虑拆分为：
- **Hooks** - 抽取状态和逻辑 (`useXxx.ts`)
- **子组件** - 抽取 UI 片段 (`components/Xxx.tsx`)
- **主组件** - 仅负责布局和流程控制

示例：contacts-edit 目录结构
```
screens/contacts-edit/
├── index.tsx              # 主组件 (精简版)
├── useContactForm.ts      # 表单逻辑 Hook
└── components/
    ├── index.ts           # 组件导出
    ├── ContactForm.tsx    # 表单 UI
    └── FormHeader.tsx     # 头部组件
```

## 代码规范

### 禁止
- ❌ 使用 `any` 类型
- ❌ 在 production 代码中使用 `console.log`
- ❌ 样式函数内联定义（每次渲染重建）
- ❌ 单个组件文件超过 300 行

### 推荐
- ✅ 显式类型注解
- ✅ 使用 `useMemo` 缓存计算结果
- ✅ 组件文件行数控制在 300 行以内
- ✅ 使用 `React.memo` 优化纯组件
- ✅ 大型组件拆分为子组件 + Hook

## 文件结构

```
client/
├── app/              # Expo Router 路由
├── screens/          # 页面组件
│   └── [screen-name]/
│       ├── index.tsx
│       ├── useXxx.ts         # 页面级 Hook (可选)
│       └── components/       # 子组件 (可选)
├── components/       # 可复用组件
├── services/         # API 服务层
├── hooks/            # 自定义 Hooks
├── utils/            # 工具函数
├── constants/        # 常量配置
├── contexts/         # React Context
└── types/            # TypeScript 类型定义
```

## ESLint 规则

```javascript
// 强制规则
'@typescript-eslint/no-explicit-any': 'error'
'@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }]
'no-console': ['warn', { allow: ['error', 'warn', 'info'] }]
```

## 重构历史

### 2026-03-11 代码质量重构
- 添加完整 Theme 类型定义
- 替换所有 `theme: any`
- 清理 console.log
- 实现 Error Boundary
- 优化样式创建函数
- 拆分 contacts-edit 大型组件 (667行 → 68行)
- 增强 ESLint 规则

## 调试

```bash
# 检查 any 类型使用
grep -rn "theme:\s*any" client/

# 检查 console.log
grep -rn "console\.(log|warn)" client/ --include="*.ts" --include="*.tsx"

# 检查大型组件
wc -l client/screens/*/index.tsx | sort -n

# TypeScript 检查
cd client && npx tsc --noEmit

# ESLint 检查
cd client && npx eslint . --ext .ts,.tsx
```
