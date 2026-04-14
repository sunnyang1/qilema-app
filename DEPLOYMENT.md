# 起了吗App 部署指南

## 系统要求

- Python 3.8+
- SQLite (开发) 或 PostgreSQL (生产)
- Redis (可选，用于缓存)

## 快速开始

### 1. 克隆代码

```bash
git clone <repository-url>
cd qilema-app/backend
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置必要的环境变量
```

### 5. 初始化数据库

```bash
python -c "from app.core.database import init_db; init_db()"
```

### 6. 运行应用

```bash
python main.py
```

访问: http://localhost:8000

### 健康检查与 Prometheus 指标（运维 / US-P12）

与 `docs/prd.md` 技术栈（Prometheus + Grafana）及代码一致，后端进程暴露：

| 端点 | 说明 |
|------|------|
| `GET /health` | 聚合健康状态（数据库、Redis），适合负载均衡或探针 |
| `GET /api/v1/health` | 与 v1 API 风格一致的健康检查 |
| `GET /metrics` | Prometheus 抓取端点（`app.core.prometheus_metrics`） |

生产环境请将 Grafana 指向 Prometheus，并由 Prometheus 抓取部署实例的 `/metrics`；存活探针可使用 `/health`。

---

## 关键配置说明

### ADMIN_USER_IDS (必需)

管理员用户ID列表，这些用户将有权限访问管理员端点。

**配置方法**:

1. 首先创建一个普通用户（通过注册API）
2. 获取该用户的 `user_id`
3. 在 `.env` 文件中配置:

```bash
ADMIN_USER_IDS=user_abc123xyz,user_def456uvw
```

**验证配置**:

```python
from app.core.config import settings
print(settings.ADMIN_USER_IDS)  # 应该输出配置的用户ID列表
```

**管理员端点**:

- `GET /api/v1/anomalies/admin/all` - 获取所有异常记录
- `GET /api/v1/notifications/admin/statistics` - 获取通知统计
- `POST /api/v1/emergency-centers/centers` - 创建急救中心
- `GET /api/v1/devices/admin/check-offline` - 检查离线设备

---

### SECRET_KEY (必需)

JWT签名密钥，生产环境必须修改为强随机密钥。

**生成方法**:

```bash
python -c "import secrets; print(secrets.token_hex(64))"
```

---

### ENCRYPTION_KEY (必需)

敏感数据加密密钥。

**生成方法**:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

### DATABASE_URL

数据库连接字符串。

**开发环境**:
```bash
DATABASE_URL=sqlite:///./qilema.db
```

**生产环境 (PostgreSQL)**:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/qilema
```

---

## Docker 部署

### 使用 Docker Compose

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止
docker-compose down
```

### 环境变量配置

在 `docker-compose.yml` 中设置环境变量:

```yaml
services:
  backend:
    environment:
      - ENVIRONMENT=production
      - ADMIN_USER_IDS=${ADMIN_USER_IDS}
      - SECRET_KEY=${SECRET_KEY}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
```

---

## 数据库迁移

### 创建迁移 (使用 Alembic)

```bash
# 安装 Alembic
pip install alembic

# 初始化
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "Initial migration"

# 应用迁移
alembic upgrade head
```

---

## 生产环境检查清单

- [ ] 修改 `SECRET_KEY` 为强随机密钥
- [ ] 配置 `ENCRYPTION_KEY`
- [ ] 配置 `ADMIN_USER_IDS`
- [ ] 修改 `DATABASE_URL` 为生产数据库
- [ ] 配置 `REDIS_URL` (推荐)
- [ ] 设置 `ENVIRONMENT=production`
- [ ] 设置 `DEBUG=False`
- [ ] 配置 `CORS_ORIGINS` 为具体域名
- [ ] 配置短信服务 API 密钥
- [ ] 配置高德地图 API 密钥
- [ ] 配置 SSL/TLS 证书
- [ ] 设置日志收集
- [ ] 配置监控告警

---

## 故障排查

### 问题: 管理员端点返回 403 Forbidden

**原因**: `ADMIN_USER_IDS` 未配置或用户ID不在列表中

**解决**:
1. 检查 `.env` 文件中的 `ADMIN_USER_IDS`
2. 确认用户ID正确
3. 重启应用

### 问题: 数据库连接失败

**原因**: 数据库URL配置错误或数据库未启动

**解决**:
1. 检查 `DATABASE_URL` 格式
2. 确认数据库服务已启动
3. 检查网络连接

### 问题: Redis 连接失败

**原因**: Redis 服务未启动或配置错误

**解决**:
1. 检查 `REDIS_URL` 配置
2. 确认 Redis 服务已启动
3. 应用会自动降级到无缓存模式

---

## 安全建议

1. **定期更换密钥**: SECRET_KEY 和 ENCRYPTION_KEY 建议每季度更换
2. **限制管理员数量**: ADMIN_USER_IDS 只应包含必要的管理员
3. **启用 HTTPS**: 生产环境必须使用 HTTPS
4. **日志审计**: 定期检查管理员操作日志
5. **数据库备份**: 定期备份数据库

---

## 支持

如有问题，请查看:
- 文档: `docs/` 目录
- API 文档: http://localhost:8000/docs (Swagger UI)
- 测试: `tests/` 目录

---

*最后更新: 2026-03-18*
