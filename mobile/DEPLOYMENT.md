# 起了吗 App - 部署说明

## 部署架构

起了吗 App 采用前后端分离架构：

```
┌─────────────────────────────────────────┐
│         Coze 部署环境                    │
├─────────────────────────────────────────┤
│  Express 服务器 (端口 5000)              │
│  - 提供前端静态文件服务                  │
│  - 健康检查端点                          │
│  - SPA 路由支持                          │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  前端应用 (Expo + React Native)          │
│  - Web 端: 由 Express 提供静态文件       │
│  - 移动端: 通过 Expo Go 访问             │
└─────────────────────────────────────────┘
                    ↓ API 调用
┌─────────────────────────────────────────┐
│  后端 API (Python FastAPI)               │
│  - 端口: 8000                            │
│  - 提供所有业务逻辑                      │
│  - 数据库: SQLite / PostgreSQL           │
└─────────────────────────────────────────┘
```

## 项目结构

```
mobile/
├── client/                    # 前端 Expo 应用
│   ├── app/                   # Expo Router 路由
│   ├── screens/               # 页面组件
│   ├── services/              # API 服务
│   ├── app.config.ts          # Expo 配置
│   └── package.json
├── server/                    # Express 静态文件服务器
│   ├── src/                   # 源代码
│   ├── dist/                  # 构建输出
│   ├── build.js               # 构建脚本
│   └── package.json
├── .coze/                     # Coze 部署配置
│   └── project.toml
└── .cozeproj/                 # Coze 项目脚本
    └── scripts/
        ├── dev_build.sh       # 开发构建
        ├── dev_run.sh         # 开发运行
        ├── prod_build.sh      # 生产构建
        └── prod_run.sh        # 生产运行
```

## 部署配置

### .coze 配置文件

```toml
[project]
entrypoint = "server.js"
requires = ["nodejs-24"]

[dev]
build = ["bash", ".cozeproj/scripts/dev_build.sh"]
run = ["bash", ".cozeproj/scripts/dev_run.sh"]

[deploy]
build = ["bash", ".cozeproj/scripts/prod_build.sh"]
run = ["bash", ".cozeproj/scripts/prod_run.sh"]
build_app_dir = "./client"
```

### 关键配置说明

1. **entrypoint = "server.js"**
   - Express 服务器的入口文件
   - 位于 `server/dist/index.js`

2. **requires = ["nodejs-24"]**
   - 指定 Node.js 版本要求

3. **build_app_dir = "./client"**
   - 构建应用的主目录

## 部署流程

### 1. 开发环境

```bash
# 安装依赖
pnpm install

# 启动开发服务器
coze dev
```

### 2. 生产构建

```bash
# 执行生产构建
bash .cozeproj/scripts/prod_build.sh
```

构建步骤：
1. 安装 Node 依赖
2. 构建 Express 服务器 (`server/dist/`)
3. 准备静态文件

### 3. 生产部署

```bash
# 启动生产服务
bash .cozeproj/scripts/prod_run.sh
```

服务启动后：
- Express 服务器运行在 `0.0.0.0:5000`
- 健康检查: `http://localhost:5000/api/v1/health`
- 前端应用: `http://localhost:5000/`

## 环境变量

### 前端环境变量 (client/.env)

```bash
# 后端 API 地址
EXPO_PUBLIC_BACKEND_BASE_URL=http://9.128.55.77:8000
```

### 后端环境变量 (server/.env)

```bash
# 服务端口
PORT=5000

# Node 环境
NODE_ENV=production
```

## 常见问题

### Q: 为什么项目显示"仍在开发中，不支持部署"？

A: 可能的原因：
1. Express 服务器构建失败
2. 缺少必要的依赖
3. 配置文件不正确

解决方案：
1. 运行 `pnpm install` 安装所有依赖
2. 运行 `cd server && pnpm run build` 测试构建
3. 检查 `.coze` 配置文件格式

### Q: 前端如何调用后端 API？

A: 前端通过环境变量配置的后端地址调用 API：

```typescript
const API_BASE_URL = process.env.EXPO_PUBLIC_BACKEND_BASE_URL || 'http://localhost:8000';
```

### Q: 为什么需要 Express 服务器？

A: Express 服务器的作用：
1. 提供前端静态文件服务（用于 Web 端）
2. 处理 SPA 路由
3. 提供健康检查端点
4. 满足 Coze 部署要求

### Q: 如何测试部署？

A: 本地测试步骤：

```bash
# 1. 构建项目
bash .cozeproj/scripts/prod_build.sh

# 2. 启动服务
PORT=5000 bash .cozeproj/scripts/prod_run.sh

# 3. 测试健康检查
curl http://localhost:5000/api/v1/health

# 4. 访问前端应用
# 浏览器打开: http://localhost:5000/
```

## 端口配置

| 服务 | 端口 | 说明 |
|------|------|------|
| Express 服务器 | 5000 | 前端静态文件服务器 |
| FastAPI 后端 | 8000 | 业务逻辑 API |
| Expo 开发服务器 | 19006 | Expo Web 端开发 |

## 注意事项

1. **后端 API 独立运行**
   - FastAPI 后端需要单独部署和运行
   - Express 服务器不处理业务逻辑，只提供静态文件服务

2. **环境变量配置**
   - 前端需要配置正确的后端 API 地址
   - 生产环境使用真实的后端服务器地址

3. **构建产物**
   - Express 服务器的构建产物在 `server/dist/`
   - 确保 `dist/index.js` 存在且可执行

4. **CORS 配置**
   - Express 服务器已配置 CORS
   - 允许跨域请求

## 部署检查清单

- [ ] 所有依赖已安装 (`pnpm install`)
- [ ] Express 服务器构建成功 (`cd server && pnpm run build`)
- [ ] `.coze` 配置文件正确
- [ ] 环境变量已配置
- [ ] 健康检查端点可访问
- [ ] 前端应用可正常访问
- [ ] 后端 API 可正常调用

## 相关文档

- [主项目 README](../README.md)
- [后端文档](../backend/README.md)
- [前端文档](./README.md)
- [API 文档](../docs/api.md)
