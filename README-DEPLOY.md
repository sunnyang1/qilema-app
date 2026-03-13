# 起了吗App - 本地部署指南

## 📋 前置要求

- **Docker Desktop** (安装中...)
- **Git** (已安装)

## 🚀 快速开始

### 1. 安装 Docker Desktop

下载正在进行中，完成后会自动安装。或者你可以：

```bash
# 查看下载进度
tail -f /Users/michelleye/CodeBuddy/qilema-app/docker-install.log

# 手动安装（如果自动安装未完成）
hdiutil attach Docker.dmg
cp -r /Volumes/Docker/Docker.app /Applications/
hdiutil detach /Volumes/Docker
open /Applications/Docker.app
```

### 2. 启动本地部署

Docker 安装完成后，运行：

```bash
# 一键部署（开发环境）
./deploy-local.sh

# 或手动启动
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

### 3. 访问服务

| 服务 | 地址 | 说明 |
|------|------|------|
| API | http://localhost:8000 | 后端 API 服务 |
| Nginx | http://localhost | 反向代理 |
| PostgreSQL | localhost:5432 | 数据库 |
| Redis | localhost:6379 | 缓存 |

### 4. 验证部署

```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 测试 API
curl http://localhost:8000/health
```

## 📁 部署脚本说明

| 脚本 | 用途 |
|------|------|
| `deploy-local.sh` | 启动本地部署（交互式选择环境） |
| `stop-local.sh` | 停止所有服务 |
| `install-docker.sh` | Docker 安装脚本 |

## 🔧 环境配置

环境变量已配置在 `.env` 文件中：

```bash
# 开发环境默认值
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=postgresql://qilema:qilema_dev_password@postgres:5432/qilema_dev
REDIS_URL=redis://redis:6379/0
```

## 📊 常用命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f redis

# 进入容器
docker-compose exec backend bash
docker-compose exec postgres psql -U qilema

# 重新构建
docker-compose up -d --build
```

## 🛠️ 故障排除

### Docker 未运行
```bash
open /Applications/Docker.app
```

### 端口被占用
```bash
# 检查端口占用
lsof -i :8000
lsof -i :5432
lsof -i :6379

# 释放端口
kill -9 <PID>
```

### 容器启动失败
```bash
# 查看详细日志
docker-compose logs

# 重新构建
docker-compose down
docker-compose up -d --build
```

### 数据库连接失败
```bash
# 等待数据库就绪
docker-compose exec postgres pg_isready

# 手动初始化（如果需要）
docker-compose exec backend python -c "from app.core.database import init_db; init_db()"
```

## 📚 更多信息

- [Docker Desktop 文档](https://docs.docker.com/desktop/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
