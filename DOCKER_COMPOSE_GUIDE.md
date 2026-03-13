# Docker Compose Usage Guide

## 快速开始

### 开发环境
```bash
# 启动服务（自动应用 docker-compose.override.yml）
docker compose up

# 使用文件监听热重载
docker compose watch

# 查看日志
docker compose logs -f backend
```

### 生产环境
```bash
# 启动服务
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 查看服务状态
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps

# 停止服务
docker compose -f docker-compose.yml -f docker-compose.prod.yml down
```

### 测试环境
```bash
# 启动测试环境
docker compose -f docker-compose.yml -f docker-compose.test.yml up

# 运行测试
docker compose -f docker-compose.yml -f docker-compose.test.yml exec backend pytest
```

## 关键特性

### 1. 多阶段构建（Multi-stage Build）
后端 Dockerfile 使用多阶段构建：
- **构建阶段**：安装编译依赖，编译 Python 包
- **运行阶段**：只包含运行时依赖，镜像体积减少约 50%

### 2. 健康检查（Healthcheck）
所有服务都配置了健康检查：
- PostgreSQL：使用 `pg_isready` 检查数据库连接
- Redis：使用 `redis-cli ping` 检查缓存连接
- Backend：使用 `/health` 端点检查应用状态
- Nginx：使用 `wget` 检查 HTTP 连通性

### 3. 服务依赖管理
后端依赖数据库和缓存启动完成：
```yaml
depends_on:
  postgres:
    condition: service_healthy
  redis:
    condition: service_healthy
```

### 4. 网络隔离
使用命名网络隔离容器通信：
```yaml
networks:
  qilema_network:
    driver: bridge
```

### 5. 持久化存储
使用具名卷(Named Volumes)管理数据：
- `postgres_data`：数据库数据
- `redis_data`：缓存数据
- `postgres_prod_data`/`redis_prod_data`：生产环境数据

### 6. 资源限制
不同环境设置不同资源限制：
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '1.0'
      memory: 1G
```

### 7. 热重载（Hot Reload）
开发环境自动监听源码变化并重建：
```yaml
develop:
  watch:
    - path: ./backend
      action: rebuild
      target: /app
```

## 常用命令

### 启动/停止/重启
```bash
docker compose up              # 启动所有服务
docker compose down            # 停止并删除容器
docker compose restart         # 重启所有服务
docker compose restart backend # 重启特定服务
```

### 查看日志
```bash
docker compose logs            # 查看所有日志
docker compose logs -f backend # 实时查看后端日志
docker compose logs --tail=50  # 查看最后 50 行日志
```

### 执行命令
```bash
docker compose exec backend bash              # 进入后端容器
docker compose exec backend python -m pytest  # 运行测试
docker compose exec postgres psql -U qilema  # 进入数据库
```

### 构建镜像
```bash
docker compose build           # 构建所有镜像
docker compose build --no-cache # 不使用缓存重建
docker compose build backend   # 只构建后端镜像
```

### 清理资源
```bash
docker compose down -v           # 删除容器和卷
docker system prune             # 清理未使用资源
docker system prune -a          # 清理所有未使用资源
```

## 环境变量

### 开发环境
- `ENVIRONMENT=development`
- `DEBUG=True`
- `LOG_LEVEL=DEBUG`
- 数据库：`qilema_dev`
- 宽松的健康检查间隔

### 生产环境
- `ENVIRONMENT=production`
- `DEBUG=False`
- `LOG_LEVEL=WARNING`
- 数据库：`qilema_prod`
- 严格的健康检查和资源限制
- 自动重启策略

### 测试环境
- `ENVIRONMENT=testing`
- `DEBUG=True`
- `LOG_LEVEL=INFO`
- 数据库：`qilema_test`
- 中等资源限制

## 最佳实践

1. **使用 .dockerignore**：减少构建上下文，加快构建速度
2. **多阶段构建**：最小化最终镜像体积
3. **健康检查**：确保服务正常运行
4. **资源限制**：防止资源耗尽
5. **非 root 用户**：提高容器安全性
6. **具名卷**：便于数据管理和备份
7. **网络隔离**：提高应用安全性
8. **环境变量**：灵活配置不同环境

## 故障排除

### 容器无法启动
```bash
# 查看容器日志
docker compose logs backend

# 检查健康状态
docker compose ps

# 进入容器调试
docker compose exec backend bash
```

### 数据库连接失败
```bash
# 检查数据库健康状态
docker compose exec postgres pg_isready -U qilema

# 检查网络连接
docker compose exec backend curl http://postgres:5432
```

### 端口占用
```bash
# 修改 docker-compose.yml 中的端口映射
# 或杀死占用端口的进程
lsof -i :8000
```

### 清理并重新启动
```bash
docker compose down -v
docker compose up --build
```
