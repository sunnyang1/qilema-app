# 起了吗 App - Coze 部署指南

## 项目概述

"起了吗 App" - 面向独居人群的紧急医疗服务应用

**技术栈:**
- 前端: Expo 54 + React Native + TypeScript
- 后端: Python 3.12.3 + FastAPI + SQLAlchemy + SQLite
- 部署: Coze 平台

---

## 部署修复状态

### ✅ 已完成的修复

1. **根目录部署配置**
   - 在根目录创建 `.coze` 配置文件
   - 创建根目录的 `package.json` 和 `project.json`
   - 创建根目录的 `LICENSE` 文件
   - 修改构建和启动脚本支持从根目录运行

2. **Android 包名格式错误**
   - 修复 Android 包名生成逻辑
   - 添加 `getSafePackageName` 函数
   - 确保所有情况下都生成有效的包名

3. **部署文档完善**
   - 创建 `ANDROID_BUILD_FIX.md` - Android 构建错误修复说明
   - 创建 `COZE_DEPLOYMENT_CHECKLIST.md` - 部署检查清单
   - 创建 `DEPLOYMENT_FIX_SUMMARY.md` - 部署修复总结
   - 更新 `DEPLOYMENT.md` - 部署说明

4. **推送脚本**
   - 创建 `push-to-github.sh` - 代码推送脚本
   - 支持多种推送方式
   - 提供详细的错误提示

---

## 快速部署指南

### 步骤 1: 推送代码到 GitHub

#### 方式 A: 使用推送脚本（推荐）

```bash
cd /workspace/projects
./push-to-github.sh
```

#### 方式 B: 手动推送

```bash
cd /workspace/projects

# 使用 GitHub CLI
gh auth login
git push origin main

# 或使用 Personal Access Token
git remote set-url origin https://<TOKEN>@github.com/sunnyang1/qilema-app.git
git push origin main

# 或使用 SSH 密钥
git remote set-url origin git@github.com:sunnyang1/qilema-app.git
git push origin main
```

### 步骤 2: 在 Coze 平台部署

1. **访问项目页面**
   - 打开 Coze 平台的项目页面
   - 确保 URL 包含 `gitUrl=https://github.com/sunnyang1/qilema-app.git`

2. **刷新页面**
   - 按 Ctrl+Shift+Delete 清除浏览器缓存
   - 或使用无痕模式重新访问

3. **检查部署配置**
   ```toml
   [project]
   name = "起了吗 App"
   type = "Expo"
   entrypoint = "mobile/client/app.config.ts"

   [dev]
   build = ["bash", "mobile/.cozeproj/scripts/dev_build.sh"]
   run = ["bash", "mobile/.cozeproj/scripts/dev_run.sh"]

   [prod]
   build = ["bash", ".cozeproj/scripts/prod_build.sh"]
   run = ["bash", ".cozeproj/scripts/prod_run.sh"]
   ```

4. **触发部署**
   - 点击"部署"按钮
   - 观察部署日志

### 步骤 3: 验证部署

```bash
# 检查应用健康状态
curl https://your-coze-app-url.com/api/v1/health

# 预期响应
{
  "code": 200,
  "message": "OK",
  "data": {
    "status": "healthy",
    "database": "connected"
  }
}
```

---

## 部署流程详解

### 阶段 1: [code] - 代码拉取

**验证要点:**
- ✅ 从 GitHub 成功拉取代码
- ✅ 识别为 Expo 项目
- ✅ 读取 `.coze` 配置文件

**可能问题:**
- Git 认证失败 → 检查仓库访问权限
- 分支不存在 → 确认 main 分支存在
- 配置文件缺失 → 确认 `.coze` 文件存在

### 阶段 2: [android] - Android 构建

**验证要点:**
- ✅ 依赖安装成功
- ✅ Expo 配置验证通过
- ✅ Android 包名格式正确
- ✅ APK/AAB 生成成功

**已修复问题:**
- ❌ ~~Android 包名格式错误~~ → ✅ 已修复

**验证命令:**
```bash
cd mobile/client
npx expo config --type prebuild
```

### 阶段 3: [runtime] - 运行时构建

**验证要点:**
- ✅ 后端依赖安装成功
- ✅ Python 环境配置正确
- ✅ 数据库初始化成功
- ✅ 启动脚本可执行

**关键文件:**
- `mobile/server/main.py` - FastAPI 主应用
- `mobile/.cozeproj/scripts/prod_run.sh` - 运行时启动脚本

### 阶段 4: 部署完成

**验证要点:**
- ✅ 应用成功启动
- ✅ 健康检查通过
- ✅ 端口监听正常
- ✅ 环境变量配置正确

---

## 常见问题排查

### 问题 1: "项目开发中，不支持部署"

**原因:**
- Coze 平台缓存
- 配置文件识别失败

**解决方案:**
1. 等待 5-10 分钟后重试
2. 清除浏览器所有缓存
3. 尝试使用不同的浏览器
4. 检查 `.coze` 文件格式

### 问题 2: Android 构建失败

**错误信息:**
```
Invalid format of Android package name
```

**解决方案:**
1. 检查 `mobile/client/app.config.ts`
2. 确认 `getSafePackageName` 函数存在
3. 验证包名格式

### 问题 3: 运行时构建失败

**错误信息:**
```
Cannot find module './server/dist/index.js'
```

**解决方案:**
1. 检查 `mobile/.cozeproj/scripts/prod_build.sh`
2. 确保 `npm run build` 执行成功
3. 验证 `dist` 目录存在

### 问题 4: 健康检查失败

**错误信息:**
```
Connection refused
```

**解决方案:**
1. 检查端口配置（默认 8000）
2. 确认防火墙规则
3. 验证环境变量

---

## 配置文件说明

### 根目录 `.coze`

```toml
[project]
name = "起了吗 App"
type = "Expo"
description = "面向独居人群的紧急医疗服务应用"
version = "1.0.0"

[dev]
build = ["bash", "mobile/.cozeproj/scripts/dev_build.sh"]
run = ["bash", "mobile/.cozeproj/scripts/dev_run.sh"]

[prod]
build = ["bash", ".cozeproj/scripts/prod_build.sh"]
run = ["bash", ".cozeproj/scripts/prod_run.sh"]
```

### 根目录 `package.json`

```json
{
  "name": "qilema-app",
  "version": "1.0.0",
  "description": "起了吗 App - 面向独居人群的紧急医疗服务应用",
  "main": "mobile/server/main.py",
  "scripts": {
    "prod:build": "bash .cozeproj/scripts/prod_build.sh",
    "prod:run": "bash .cozeproj/scripts/prod_run.sh"
  }
}
```

### 根目录 `project.json`

```json
{
  "name": "起了吗 App",
  "type": "expo",
  "version": "1.0.0",
  "description": "面向独居人群的紧急医疗服务应用"
}
```

---

## 测试账号

- **手机号**: 13800138000
- **密码**: Test123456

---

## 相关文档

| 文档 | 说明 |
|------|------|
| `DEPLOYMENT_FIX_SUMMARY.md` | 部署修复总结 |
| `ANDROID_BUILD_FIX.md` | Android 构建错误修复 |
| `COZE_DEPLOYMENT_CHECKLIST.md` | 部署检查清单 |
| `DEPLOYMENT.md` | 部署说明 |
| `README.md` | 项目说明 |
| `push-to-github.sh` | 代码推送脚本 |

---

## 技术支持

如果遇到其他问题：

1. 查看详细日志
2. 检查配置文件
3. 参考 Expo 官方文档
4. 联系 Coze 技术支持

---

**最后更新**: 2024-02-24
**版本**: 1.0.0
**维护者**: Coze User
