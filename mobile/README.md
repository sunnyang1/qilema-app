# 起了吗 App - Expo + React Native 版本

"起了吗 App"移动端应用，采用 Expo 54 + React Native 技术栈，应用"温暖守护"设计风格（晨光橙 + 生命绿）。

## 项目结构

```
mobile/
├── client/
│   ├── app/                    # Expo Router 路由
│   │   ├── _layout.tsx         # 根布局（Stack 导航）
│   │   ├── login.tsx           # 登录路由
│   │   ├── register.tsx        # 注册路由
│   │   └── (tabs)/             # 主应用 Tab 导航
│   │       └── _layout.tsx     # Tab 布局
│   ├── screens/                # 页面实现
│   │   ├── login/              # 登录页面 ✓
│   │   └── register/           # 注册页面 ✓
│   ├── services/               # 业务服务
│   │   └── auth.ts             # 认证服务 ✓
│   ├── utils/                  # 工具函数
│   │   ├── api.ts              # API 客户端 ✓
│   │   └── auth-interceptor.ts # 认证拦截器 ✓
│   ├── contexts/               # React Context
│   │   └── AuthContext.tsx     # 认证上下文 ✓
│   ├── constants/              # 常量配置
│   │   ├── app.ts              # 应用常量 ✓
│   │   └── theme.ts            # 主题配置 ✓
│   └── package.json
├── .coze                       # Coze 配置
└── README.md
```

## 已完成功能

### 1. 项目初始化 ✅
- Expo 54 + React Native 项目结构
- pnpm workspace 配置
- TypeScript 支持

### 2. 主题系统 ✅
- 浅色/深色主题支持
- 蓝色主色调（匹配 Flutter 版本）
- 响应式设计常量

### 3. API 客户端 ✅
- 统一的 HTTP 请求封装
- 请求/响应拦截器
- 错误处理
- 自动令牌刷新

### 4. 认证服务 ✅
- 登录/注册功能
- Token 管理
- 本地存储
- 自动令牌刷新

### 5. 认证上下文 ✅
- React Context 封装
- 全局状态管理
- 加载状态处理

### 6. 页面 ✅
- 登录页面
- 注册页面

## 核心功能模块

| 功能模块 | React Native 路由 | 状态 |
|---------|-------------------|------|
| 认证 | /login, /register | ✅ |
| 首页（签到） | /(tabs)/index | ⏳ |
| SOS（紧急求助） | /(tabs)/sos, /sos-status | ⏳ |
| 联系人 | /(tabs)/contacts, /contact-detail | ⏳ |
| 健康 | /(tabs)/health, /medical-histories, /medications, /allergies | ⏳ |
| 设备 | /devices, /device-data | ⏳ |
| 紧急资源 | /aed-map, /hospitals | ⏳ |
| 知识库 | /(tabs)/knowledge | ⏳ |
| 用药提醒 | /medication | ⏳ |

## 需要完成的页面

### 1. 主应用 Tab 导航
```typescript
// client/app/(tabs)/_layout.tsx
- 首页（签到）
- SOS（紧急求助）
- 联系人
- 健康
- 更多...
```

### 2. 主要功能页面
- `screens/home/index.tsx` - 签到首页
- `screens/sos/index.tsx` - SOS 紧急求助
- `screens/contacts/index.tsx` - 联系人列表
- `screens/health/index.tsx` - 健康档案
- `screens/knowledge/index.tsx` - 知识库
- 等等...

### 3. API 服务
- `services/signin.ts` - 签到服务
- `services/sos.ts` - SOS 服务
- `services/contacts.ts` - 联系人服务
- 等等...

## 运行项目

```bash
# 启动开发服务器
cd /workspace/projects/mobile
coze dev

# 或者手动启动前端
cd /workspace/projects/mobile/client
npx expo start
```

## 环境变量

在 `.env` 文件中配置：

```bash
EXPO_PUBLIC_BACKEND_BASE_URL=http://localhost:9091
```

## 依赖说明

### 已安装的 Expo 包
- `expo-router` - 路由
- `expo-status-bar` - 状态栏
- `expo-linear-gradient` - 渐变
- `expo-blur` - 模糊效果
- `expo-haptics` - 触觉反馈
- `react-native-safe-area-context` - 安全区
- `react-native-gesture-handler` - 手势
- `react-native-reanimated` - 动画
- `@react-native-async-storage/async-storage` - 本地存储
- `react-native-toast-message` - 提示消息
- `@expo/vector-icons` - 图标

### 需要添加的依赖（根据功能需要）
```bash
# 地图
npx expo install react-native-maps

# 位置
npx expo install expo-location

# 相机
npx expo install expo-camera

# 图片选择
npx expo install expo-image-picker

# 通知
npx expo install expo-notifications

# 图表
cd client && pnpm add react-native-chart-kit react-native-svg
```

## 技术栈

### 框架
- Expo 54 + React Native 0.81.5
- TypeScript 5.8+

### 路由
- Expo Router 6.0

### 状态管理
- React Context

### UI 组件
- React Native 原生组件
- Expo 模块（expo-status-bar, expo-linear-gradient, expo-haptics 等）
- react-native-safe-area-context
- react-native-gesture-handler
- react-native-reanimated
- @expo/vector-icons

### 工具库
- @react-native-async-storage/async-storage - 本地存储
- react-native-toast-message - 提示消息

## 后续开发建议

1. **优先级 1 - 核心功能**
   - [ ] 完成首页（签到）页面
   - [ ] 完成 SOS 紧急求助页面
   - [ ] 完成联系人管理页面

2. **优先级 2 - 次要功能**
   - [ ] 健康档案页面
   - [ ] 知识库页面
   - [ ] 用药提醒功能

3. **优先级 3 - 增强功能**
   - [ ] 地图集成
   - [ ] 位置服务
   - [ ] 推送通知
   - [ ] 设备连接

## 技术亮点

1. **统一的主题系统** - 支持深色模式
2. **类型安全的 API 客户端** - TypeScript 完整类型
3. **自动令牌刷新** - 无缝认证体验
4. **模块化架构** - 易于维护和扩展
5. **遵循 Expo 最佳实践** - 兼容三端（Android + iOS + Web）

## 参考文档

- [Expo Router 文档](https://docs.expo.dev/router/introduction/)
- [React Native 文档](https://reactnative.dev/)
- [Expo 文档](https://docs.expo.dev/)

---

**注意**：这是一个大型项目，当前版本已完成核心架构搭建和认证功能。继续开发请参考上述结构和迁移指南。
