# 起了吗 App - 后端服务

基于 FastAPI 的高性能后端服务，为"起了吗 App"提供完整的 API 支持。

## 项目概述

后端服务采用现代化 Python 技术栈，提供用户认证、签到管理、异常预警、紧急求助等核心功能的 RESTful API。

### 技术栈

- **语言**: Python 3.12+
- **框架**: FastAPI 0.109+
- **ORM**: SQLAlchemy 2.0+
- **数据库**: SQLite (开发/测试), PostgreSQL (生产)
- **认证**: JWT + OAuth2.0
- **依赖注入**: dependency-injector
- **监控**: Prometheus
- **测试**: pytest + pytest-cov
- **速率限制**: slowapi

### 核心特性

- ✅ 依赖注入架构
- ✅ 统一错误处理
- ✅ JWT 认证机制
- ✅ 数据库 ORM 映射
- ✅ API 文档自动生成
- ✅ 速率限制保护
- ✅ 健康检查端点
- ✅ 完整的单元测试

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── dependencies.py      # 依赖注入容器
│   ├── database.py          # 数据库连接
│   ├── models/              # 数据库模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── checkin.py
│   │   ├── anomaly.py
│   │   ├── contact.py
│   │   └── health_record.py
│   ├── schemas/             # Pydantic Schema
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── checkin.py
│   │   ├── anomaly.py
│   │   ├── contact.py
│   │   └── common.py
│   ├── api/                 # API 路由
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── checkins.py
│   │   ├── anomalies.py
│   │   ├── contacts.py
│   │   └── health_records.py
│   ├── services/            # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── checkin_service.py
│   │   ├── anomaly_service.py
│   │   └── notification_service.py
│   ├── core/                # 核心功能
│   │   ├── __init__.py
│   │   ├── security.py
│   │   ├── exceptions.py
│   │   └── middleware.py
│   └── utils/               # 工具函数
│       ├── __init__.py
│       └── helpers.py
├── tests/                   # 测试代码
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_checkins.py
│   └── test_anomalies.py
├── scripts/                 # 脚本工具
│   ├── init_db.py
│   └── seed_data.py
├── .env.example             # 环境变量示例
├── requirements.txt         # Python 依赖
├── pytest.ini              # pytest 配置
└── README.md               # 本文件
```

## 快速开始

### 环境要求

- Python 3.12 或更高版本
- pip 或 poetry
- SQLite 3 (开发环境)

### 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，配置必要的参数
# DATABASE_URL=sqlite:///./qilema.db
# SECRET_KEY=your-secret-key-here
# ALGORITHM=HS256
# ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 初始化数据库

```bash
# 创建数据库表
python scripts/init_db.py

# (可选) 填充测试数据
python scripts/seed_data.py
```

### 启动服务

```bash
# 开发模式（自动重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

服务启动后，访问：
- API 文档 (Swagger UI): http://localhost:8000/docs
- ReDoc 文档: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/api/v1/health

## API 文档

### 认证相关

#### 用户注册
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "phone": "13800138000",
  "password": "yourpassword",
  "nickname": "张三"
}
```

#### 用户登录
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=13800138000&password=yourpassword
```

#### 获取当前用户信息
```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

### 签到相关

#### 创建签到记录
```http
POST /api/v1/checkins
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "location_lat": 39.9042,
  "location_lng": 116.4074,
  "note": "今天感觉不错"
}
```

#### 获取签到历史
```http
GET /api/v1/checkins?user_id=<user_id>&limit=10
Authorization: Bearer <access_token>
```

### 异常预警相关

#### 创建异常记录
```http
POST /api/v1/anomalies
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "user_id": "<user_id>",
  "anomaly_type": "missed_checkin",
  "severity": "high",
  "description": "超过24小时未签到"
}
```

#### 获取异常列表
```http
GET /api/v1/anomalies?user_id=<user_id>&status=pending
Authorization: Bearer <access_token>
```

### 紧急联系人相关

#### 添加紧急联系人
```http
POST /api/v1/contacts
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "user_id": "<user_id>",
  "name": "张三",
  "phone": "13800138001",
  "relationship": "friend",
  "priority": 1
}
```

#### 获取联系人列表
```http
GET /api/v1/contacts?user_id=<user_id>
Authorization: Bearer <access_token>
```

### 健康记录相关

#### 创建健康记录
```http
POST /api/v1/health_records
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "user_id": "<user_id>",
  "blood_pressure_systolic": 120,
  "blood_pressure_diastolic": 80,
  "heart_rate": 75,
  "weight": 65.5
}
```

#### 获取健康记录
```http
GET /api/v1/health_records?user_id=<user_id>
Authorization: Bearer <access_token>
```

详细的 API 文档请访问：http://localhost:8000/docs

## 测试

### 运行所有测试

```bash
pytest tests/ -v
```

### 运行测试并生成覆盖率报告

```bash
pytest tests/ -v --cov=app --cov-report=html --cov-report=term
```

### 运行特定测试

```bash
# 运行认证相关测试
pytest tests/test_auth.py -v

# 运行特定测试用例
pytest tests/test_checkins.py::test_create_checkin -v
```

## 开发规范

### 代码风格

- 遵循 PEP 8 规范
- 使用 Black 进行代码格式化
- 使用 isort 进行 import 排序

```bash
# 格式化代码
black app/

# 排序 import
isort app/
```

### 提交规范

遵循 Conventional Commits 规范：

```
feat: 添加新功能
fix: 修复 bug
refactor: 代码重构
docs: 文档更新
test: 测试相关
chore: 构建/工具相关
```

### 分支策略

- `main` - 主分支，稳定版本
- `develop` - 开发分支
- `feature/*` - 功能分支
- `bugfix/*` - 修复分支

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t qilema-backend .

# 运行容器
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@db:5432/qilema \
  -e SECRET_KEY=your-secret-key \
  qilema-backend
```

### Docker Compose 部署

```bash
# 启动所有服务
docker-compose -f docker-compose.prod.yml up -d

# 查看日志
docker-compose logs -f backend
```

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DATABASE_URL | 数据库连接字符串 | sqlite:///./qilema.db |
| SECRET_KEY | JWT 密钥 | 必须设置 |
| ALGORITHM | 加密算法 | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token 过期时间（分钟） | 30 |
| CORS_ORIGINS | CORS 允许的来源 | * |

## 监控与日志

### Prometheus 指标

服务暴露 Prometheus 指标端点：

```bash
http://localhost:8000/metrics
```

### 日志配置

日志级别通过环境变量配置：

- `LOG_LEVEL=DEBUG` - 调试信息
- `LOG_LEVEL=INFO` - 一般信息（默认）
- `LOG_LEVEL=WARNING` - 警告信息
- `LOG_LEVEL=ERROR` - 错误信息

## 故障排查

### 常见问题

#### 1. 数据库连接失败

**问题**: `OperationalError: unable to open database file`

**解决方案**:
```bash
# 确保数据库目录存在
mkdir -p data

# 检查 DATABASE_URL 配置
# 开发环境: sqlite:///./qilema.db
# 生产环境: postgresql://user:pass@host:5432/dbname
```

#### 2. JWT Token 验证失败

**问题**: `Could not validate credentials`

**解决方案**:
- 检查 `SECRET_KEY` 配置
- 确认 Token 未过期
- 检查 Token 格式是否正确

#### 3. 速率限制触发

**问题**: `Too many requests`

**解决方案**:
- 默认限制: 100 请求/分钟
- 修改 `slowapi` 配置
- 或等待限制重置

## 性能优化

### 数据库连接池

```python
# 在 config.py 中配置
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)
```

### 缓存策略

建议使用 Redis 缓存常用数据：

```python
# 安装依赖
pip install redis

# 配置缓存
redis_client = redis.Redis(host='localhost', port=6379, db=0)
```

### 异步处理

对于耗时操作（如发送通知），建议使用 Celery：

```bash
# 安装依赖
pip install celery redis

# 启动 Celery worker
celery -A app.tasks.celery_app worker --loglevel=info
```

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: 添加 AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

MIT License - 详见项目根目录的 LICENSE 文件

## 联系方式

- 项目主页: https://github.com/sunnyang1/qilema-app
- 问题反馈: https://github.com/sunnyang1/qilema-app/issues

---

**最后更新**: 2024-02-24
**版本**: 1.0.0
**维护者**: Coze User
