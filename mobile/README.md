# 起了吗 App - 移动端

"起了吗 App"移动端应用，采用 Expo 54 + React Native 技术栈，应用"温暖守护"设计风格（晨光橙 + 生命绿）。

## 项目概述

移动端应用为独居人群提供便捷的日常签到、紧急求助、健康档案管理等功能，与后端 FastAPI 服务配合，构建完整的紧急医疗服务闭环。

## 项目结构

```
mobile/
├── client/                    # React Native 应用
│   ├── app/                   # Expo Router 路由
│   │   ├── _layout.tsx        # 根布局（Stack 导航）
│   │   ├── login.tsx          # 登录路由
│   │   ├── register.tsx       # 注册路由
│   │   ├── sos-status.tsx     # SOS 状态页
│   │   └── (tabs)/            # 主应用 Tab 导航
│   │       ├── _layout.tsx    # Tab 布局
│   │       ├── index.tsx      # 首页（签到）
│   │       ├── sos.tsx        # SOS 紧急求助
│   │       ├── contacts.tsx   # 联系人
│   │       ├── health.tsx     # 健康
│   │       └── knowledge.tsx  # 知识库
│   ├── screens/               # 页面实现
│   │   ├── login/             # 登录页面
│   │   ├── register/          # 注册页面
│   │   ├── home/              # 首页（签到）
│   │   ├── sos/               # SOS 紧急求助
│   │   ├── contacts/          # 联系人管理
│   │   ├── health/            # 健康档案
│   │   └── knowledge/         # 知识库
│   ├── components/            # 可复用组件
│   │   ├── Screen.tsx         # 页面容器
│   │   ├── ThemedText.tsx     # 主题文本
│   │   ├── ThemedView.tsx     # 主题视图
│   │   └── SOSButton.tsx      # SOS 按钮
│   ├── services/              # 业务服务
│   │   ├── api.ts             # API 客户端
│   │   ├── auth-interceptor.ts # 认证拦截器
│   │   ├── auth.ts            # 认证服务
│   │   ├── signin.ts          # 签到服务
│   │   ├── sos.ts             # SOS 服务
│   │   └── contacts.ts        # 联系人服务
│   ├── contexts/              # React Context
│   │   └── AuthContext.tsx    # 认证上下文
│   ├── utils/                 # 工具函数
│   │   └── index.ts           # 通用工具
│   ├── constants/             # 常量配置
│   │   ├── app.ts             # 应用常量
│   │   └── theme.ts           # 主题配置
│   └── package.json
├── .coze/                     # Coze 配置
│   ├── project.toml
│   └── scripts/
├── pnpm-workspace.yaml
└── README.md
```

## 技术栈

### 核心框架
- **Expo SDK 54** - React Native 开发框架
- **React Native 0.81.5** - 移动 UI 框架
- **TypeScript 5.8+** - 类型安全
- **Expo Router 6.0** - 文件系统路由
- **React Context** - 全局状态管理

### UI/UX
- **React Native 原生组件** - View, Text, ScrollView 等
- **Expo 模块**
  - `expo-status-bar` - 状态栏
  - `expo-linear-gradient` - 渐变效果
  - `expo-blur` - 模糊效果
  - `expo-haptics` - 触觉反馈
  - `expo-location` - 位置服务
  - `expo-camera` - 相机
  - `expo-image-picker` - 图片选择
  - `expo-notifications` - 推送通知
- **第三方库**
  - `react-native-safe-area-context` - 安全区
  - `react-native-gesture-handler` - 手势
  - `react-native-reanimated` - 动画
  - `@react-native-async-storage/async-storage` - 本地存储
  - `react-native-toast-message` - 提示消息
  - `@expo/vector-icons` - 图标

### 工具
- **pnpm** - 包管理器
- **ESLint** - 代码规范
- **TypeScript** - 类型检查

## 已完成功能

### 基础功能
- [x] 项目初始化（Expo 54 + React Native）
- [x] TypeScript 配置
- [x] 主题系统（浅色/深色模式）
- [x] 路由系统（Expo Router）
- [x] API 客户端封装
- [x] 认证拦截器（自动 Token 刷新）

### 认证模块
- [x] 登录页面
- [x] 注册页面
- [x] 认证服务
- [x] 认证上下文（全局状态管理）
- [x] Token 自动刷新

### 页面
- [x] 登录页面 (`/login`)
- [x] 注册页面 (`/register`)

## 核心功能模块

| 功能模块 | 路由 | 状态 | 说明 |
|---------|------|------|------|
| **认证** | | | |
| 登录 | `/login` | ✅ | 手机号 + 密码登录 |
| 注册 | `/register` | ✅ | 手机号 + 密码注册 |
| **主功能** | | | |
| 首页（签到） | `/(tabs)/index` | ✅ | 每日签到打卡 |
| SOS（紧急求助） | `/(tabs)/sos` | ✅ | 一键紧急求助 |
| SOS 状态 | `/sos-status` | ✅ | SOS 求助状态跟踪 |
| 联系人 | `/(tabs)/contacts` | ✅ | 紧急联系人管理 |
| 健康 | `/(tabs)/health` | ⏳ | 健康档案管理 |
| 知识库 | `/(tabs)/knowledge` | ⏳ | 急救知识库 |
| **子页面** | | | |
| 联系人详情 | `/contact-detail/:id` | ✅ | 编辑联系人信息 |

## 快速开始

### 环境要求

- Node.js 20+
- pnpm 8+
- Expo CLI
- Expo Go (移动端) 或浏览器

### 安装依赖

```bash
cd /workspace/projects/mobile
pnpm install
```

### 配置环境变量

在 `client/.env` 文件中配置：

```bash
EXPO_PUBLIC_BACKEND_BASE_URL=http://9.128.55.77:8000
```

### 启动开发服务器

```bash
# 使用 Coze 脚本启动
coze dev

# 或手动启动前端
cd client
npx expo start
```

### 访问应用

- **Web 端**: 浏览器访问 `http://localhost:19006`
- **Android**: 使用 Expo Go 扫描二维码
- **iOS**: 使用 Expo Go 扫描二维码

## 测试账号

- **手机号**: 13800138000
- **密码**: Test123456

## 设计规范

### 主题颜色

| 用途 | 颜色 | 十六进制 |
|------|------|----------|
| 晨光橙（主色） | #FF8A65 | 晨光橙 |
| 生命绿（强调色） | #66BB6A | 生命绿 |
| 警示红（SOS） | #EF5350 | 警示红 |
| 文字主色 | #212121 | 主文本 |
| 文字辅色 | #757575 | 辅助文本 |
| 背景根色 | #FAFAFA | 根背景 |

### UI 组件规范

所有页面必须使用以下组件：

- **Screen** - 页面容器（自动处理安全区）
- **ThemedText** - 主题文本（支持主题色）
- **ThemedView** - 主题视图（支持主题色）
- **SOSButton** - SOS 按钮（长按触发）

### 页面开发规范

每个页面必须遵循以下结构：

```
screens/[pageName]/
├── index.tsx      # 页面组件
└── styles.ts      # 样式文件（createStyles 工厂模式）
```

## 后续开发计划

### 优先级 1 - 核心功能增强
- [ ] 健康档案页面
- [ ] 知识库页面
- [ ] 用药提醒功能

### 优先级 2 - 地图与定位
- [ ] 周边医院地图
- [ ] AED 设备定位
- [ ] 导航功能

### 优先级 3 - 设备联动
- [ ] 智能手环绑定
- [ ] 实时生理数据展示
- [ ] 异常数据预警

### 优先级 4 - 用户体验优化
- [ ] 推送通知
- [ ] 语音交互
- [ ] 无障碍优化

## 常见问题

### Expo Go 无法连接后端

确保环境变量配置正确：

```bash
# 开发环境（本地）
EXPO_PUBLIC_BACKEND_BASE_URL=http://localhost:8000

# 真机测试（使用机器 IP）
EXPO_PUBLIC_BACKEND_BASE_URL=http://9.128.55.77:8000
```

### 路由白屏问题

确保：
1. 页面文件存在 (`screens/*/index.tsx`)
2. 路由文件正确 re-export (`app/*tsx`)
3. 路由配置与文件名匹配

### 样式不生效

确保：
1. 使用 `createStyles(theme)` 工厂函数
2. 通过 `useMemo` 缓存样式
3. 颜色使用 `theme.*` 而非硬编码

## 参考文档

- [Expo 官方文档](https://docs.expo.dev/)
- [React Native 官方文档](https://reactnative.dev/)
- [Expo Router 文档](https://docs.expo.dev/router/introduction/)
- [项目主文档](../README.md)

## 许可证

MIT License

---

**当前版本**: v1.0.0

**最后更新**: 2024-02-24
