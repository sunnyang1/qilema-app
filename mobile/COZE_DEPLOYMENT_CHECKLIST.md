# Coze 部署配置检查清单

## 必需文件清单

✅ 根目录必需文件：
- [x] `package.json` - 项目配置文件
- [x] `README.md` - 项目说明文档
- [x] `LICENSE` - 开源许可证
- [x] `.coze` - Coze 部署配置
- [x] `project.json` - 项目元数据

✅ 目录结构：
- [x] `client/` - Expo 前端应用
- [x] `server/` - Express 静态文件服务器
- [x] `server/dist/` - 构建输出目录
- [x] `server/dist/index.js` - 服务器入口文件

## 配置文件检查

### .coze 配置
```toml
[project]
name = "qilema-app"
displayName = "起了吗 App"
description = "为独居人群提供紧急医疗救助服务"
version = "1.0.0"
status = "production"
entrypoint = "server.js"
requires = ["nodejs-24"]

[deploy]
build = ["bash", ".cozeproj/scripts/prod_build.sh"]
run = ["bash", ".cozeproj/scripts/prod_run.sh"]
build_app_dir = "./client"
port = 5000
health_check = "/api/v1/health"
```

### package.json 检查
```json
{
  "name": "qilema-app",
  "version": "1.0.0",
  "description": "起了吗 App - 为独居人群提供紧急医疗救助服务",
  "main": "server/dist/index.js",
  "author": "Qilema Team",
  "license": "MIT",
  "keywords": ["expo", "react-native", "emergency", "medical"]
}
```

### server/package.json 检查
```json
{
  "name": "@qilema/app-server",
  "version": "1.0.0",
  "description": "起了吗 App 前端静态文件服务器",
  "scripts": {
    "build": "node build.js",
    "start": "NODE_ENV=production PORT=${PORT:-5000} node dist/index.js"
  }
}
```

## 构建验证

### 测试构建
```bash
cd /workspace/projects/mobile
bash .cozeproj/scripts/prod_build.sh
```

### 检查构建输出
```bash
# 检查 dist 目录是否存在
ls -la server/dist/

# 检查 index.js 是否存在
ls -lh server/dist/index.js

# 查看文件内容（前20行）
head -20 server/dist/index.js
```

### 测试启动
```bash
PORT=5000 timeout 5 bash .cozeproj/scripts/prod_run.sh
```

### 健康检查
```bash
# 启动服务
cd /workspace/projects/mobile/server
PORT=5000 node dist/index.js &

# 测试健康检查
curl http://localhost:5000/api/v1/health

# 预期响应
# {"status":"ok","message":"起了吗 App 前端服务器运行正常"}
```

## 关键配置说明

### 1. 入口文件
- `.coze` 中配置的 `entrypoint = "server.js"`
- 对应实际文件：`server/dist/index.js`

### 2. 运行时要求
- `requires = ["nodejs-24"]`
- 指定使用 Node.js 24 运行时

### 3. 构建目录
- `build_app_dir = "./client"`
- 指定构建应用的主目录

### 4. 端口配置
- `port = 5000`
- Express 服务器监听的端口

### 5. 健康检查
- `health_check = "/api/v1/health"`
- Coze 用于检测服务健康状态的端点

## 常见问题排查

### 问题：项目显示"仍在开发中，不支持部署"

可能原因：
1. ✅ 缺少 LICENSE 文件 → 已解决
2. ✅ package.json 不完整 → 已解决
3. ✅ .coze 配置不完整 → 已解决
4. ✅ 缺少项目元数据 → 已解决
5. ❌ 可能是 Coze 平台的缓存问题

### 问题：构建失败

检查：
1. ✅ 所有依赖已安装 (`pnpm install`)
2. ✅ server 构建成功 (`cd server && pnpm run build`)
3. ✅ dist/index.js 存在且可读

### 问题：启动失败

检查：
1. ✅ 端口配置正确 (5000)
2. ✅ health_check 端点可访问
3. ✅ Express 监听 0.0.0.0

## 部署状态总结

✅ **已完成配置**：
- [x] 完整的 package.json
- [x] LICENSE 文件
- [x] project.json 元数据
- [x] .coze 配置
- [x] README.md 文档
- [x] 构建脚本
- [x] 启动脚本
- [x] 健康检查端点
- [x] Express 静态文件服务器
- [x] 清理冗余文件

✅ **验证通过**：
- [x] 构建脚本成功运行
- [x] dist/index.js 生成正确
- [x] 健康检查端点响应正常

⚠️ **待确认**：
- [ ] Coze 平台是否识别项目配置
- [ ] 部署流程是否通过 Coze 检查

## 下一步操作

1. 在 Coze 平台刷新项目页面
2. 清除浏览器缓存后重试部署
3. 如果仍然显示"不支持部署"，请联系 Coze 技术支持
4. 确认项目是否符合 Coze 的部署要求（可能是特定类型的应用才支持部署）

## 参考文档

- [Coze 部署文档](./DEPLOYMENT.md)
- [项目 README](./README.md)
- [后端部署文档](../backend/README.md)
