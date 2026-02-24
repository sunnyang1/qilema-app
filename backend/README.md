# 起了吗 App - 后端服务

"起了吗 App"后端服务，采用 Python FastAPI 框架，为移动端提供 RESTful API 服务。

## 项目概述

后端服务负责处理用户认证、签到记录、SOS求助、联系人管理、健康档案等核心业务逻辑，并与前端移动端配合，构建完整的紧急医疗服务闭环。

## 技术栈

### 核心框架
- **Python 3.12.3** - 编程语言
- **FastAPI 0.104+** - Web 框架
- **SQLAlchemy 2.0** - ORM 框架
- **Pydantic v2** - 数据验证

### 数据库与缓存
- **SQLite** - 开发/测试数据库
- **PostgreSQL** - 生产数据库
- **Redis** - 缓存与会话管理

### 认证与安全
- **JWT (PyJWT)** - 令牌认证
- **OAuth2.0** - 授权框架
- **Passlib** - 密码哈希
- **slowapi** - 速率限制

### 监控与测试
- **Prometheus** - 监控指标
- **pytest** - 测试框架
- **pytest-cov** - 测试覆盖率

## 项目结构

```
backend/
├── app/                        # 应用核心代码
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用配置
│   ├── config.py               # 配置管理
│   ├── models/                 # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── user.py             # 用户模型
│   │   ├── signin.py           # 签到模型
│   │   ├── contact.py          # 联系人模型
│   │   ├── sos.py              # SOS 模型
│   │   ├── alert.py            # 预警模型
│   │   └── health.py           # 健康档案模型
│   ├── schemas/                # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── user.py             # 用户 Schema
│   │   ├── signin.py           # 签到 Schema
│   │   ├── contact.py          # 联系人 Schema
│   │   ├── sos.py              # SOS Schema
│   │   └── alert.py            # 预警 Schema
│   ├── services/               # 业务服务层
│   │   ├── __init__.py
│   │   ├── base.py             # 基础服务
│   │   ├── auth.py             # 认证服务
│   │   ├── signin.py           # 签到服务
│   │   ├── contact.py          # 联系人服务
│   │   ├── sos.py              # SOS 服务
│   │   └── alert.py            # 预警服务
│   ├── api/                    # API 路由
│   │   ├── __init__.py
│   │   ├── auth.py             # 认证 API
│   │   ├── signin.py           # 签到 API
│   │   ├── contact.py          # 联系人 API
│   │   └── sos.py              # SOS API
│   ├── core/                   # 核心功能
│   │   ├── __init__.py
│   │   ├── security.py         # 安全工具（JWT、密码哈希）
│   │   ├── dependencies.py     # 依赖注入
│   │   └── cache.py            # 缓存工具
│   ├── db/                     # 数据库
│   │   ├── __init__.py
│   │   ├── session.py          # 数据库会话
│   │   └── base.py             # Base 模型
│   └── utils/                  # 工具函数
│       └── __init__.py
├── tests/                      # 测试代码
│   ├── __init__.py
│   ├── conftest.py             # pytest 配置
│   ├── test_auth.py            # 认证测试
│   ├── test_signin.py          # 签到测试
│   └── test_api.py             # API 测试
├── scripts/                    # 脚本工具
│   └── init_db.py              # 数据库初始化
├── logs/                       # 日志目录
│   ├── app.log                 # 应用日志
│   └── error.log               # 错误日志
├── main.py                     # 应用入口
├── requirements.txt            # Python 依赖
├── Dockerfile                  # Docker 配置
└── README.md                   # 本文件
```

## 核心功能模块

### 用户认证模块 (`app/api/auth.py`)
- 用户注册
- 用户登录
- Token 刷新
- 登录速率限制（5次/分钟）

### 签到模块 (`app/api/signin.py`)
- 每日签到打卡
- 签到历史查询
- 签到统计

### 联系人模块 (`app/api/contact.py`)
- 添加紧急联系人
- 编辑联系人
- 删除联系人
- 联系人列表查询

### SOS 紧急求助模块 (`app/api/sos.py`)
- 发起 SOS 求助
- SOS 状态查询
- SOS 历史记录

### 预警模块 (`app/api/alert.py`)
- 异常预警触发
- 预警通知发送
- 预警历史查询

## API 路由

所有 API 路由统一使用 `/api/v1` 前缀。

### 认证相关
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/register` | 用户注册 |
| POST | `/api/v1/auth/login` | 用户登录 |
| POST | `/api/v1/auth/refresh` | 刷新 Token |

### 签到相关
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/signin` | 每日签到 |
| GET | `/api/v1/signin/history` | 签到历史 |
| GET | `/api/v1/signin/stats` | 签到统计 |

### 联系人相关
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/contacts` | 联系人列表 |
| POST | `/api/v1/contacts` | 添加联系人 |
| GET | `/api/v1/contacts/{id}` | 联系人详情 |
| PUT | `/api/v1/contacts/{id}` | 编辑联系人 |
| DELETE | `/api/v1/contacts/{id}` | 删除联系人 |

### SOS 相关
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/sos` | 发起 SOS |
| GET | `/api/v1/sos/{id}` | SOS 详情 |
| GET | `/api/v1/sos/history` | SOS 历史 |

### 健康检查
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/health` | 服务健康检查 |

## 快速开始

### 环境要求

- Python 3.12+
- SQLite 3（开发环境）
- PostgreSQL 15+（生产环境）
- Redis 7+

### 安装依赖

```bash
cd /workspace/projects/backend
pip install -r requirements.txt
```

### 配置环境变量

在 `.env` 文件中配置：

```bash
# 应用配置
APP_NAME="起了吗 App"
APP_ENV=development
DEBUG=True

# 数据库配置
DATABASE_URL=sqlite:///./qilema.db

# JWT 配置
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS 配置
CORS_ORIGINS=*

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# 速率限制配置
RATE_LIMIT_ENABLED=True
LOGIN_RATE_LIMIT=5/minute
```

### 初始化数据库

```bash
python -c "from app.db.session import init_db; init_db()"
```

### 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动

### 访问 API 文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 测试

### 运行所有测试

```bash
pytest tests/ -v
```

### 运行测试并生成覆盖率报告

```bash
pytest tests/ -v --cov=app --cov-report=html
```

### 查看覆盖率报告

```bash
open htmlcov/index.html
```

## 核心设计模式

### BaseService 基类

所有服务类继承 `BaseService[T]`，提供统一的 CRUD 能力：

```python
class ContactService(BaseService[Contact]):
    model_class = Contact
    cache_prefix = CacheConfig.PREFIX_CONTACT
    cache_ttl = CacheConfig.TTL_CONTACT_LIST
```

### Pydantic Schema

所有 API 请求/响应使用 Pydantic Schema 进行数据验证：

```python
class ContactCreate(BaseModel):
    name: str
    phone: str
    priority: int = 1
    relationship: Optional[str] = None
```

### 依赖注入

使用 FastAPI 的依赖注入系统管理数据库会话：

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 安全特性

### 认证
- JWT 令牌认证
- OAuth2.0 密码流
- 令牌自动刷新

### 速率限制
- 登录端点：5次/分钟
- 使用 `slowapi` 实现
- 熔断器线程安全

### 密码安全
- Passlib bcrypt 哈希
- 密码复杂度验证
- 安全存储

### CORS
- 开发环境：允许所有来源
- 生产环境：配置允许的来源列表

## 数据库模型

### User（用户）
- `user_id`: UUID
- `phone`: 手机号
- `password_hash`: 密码哈希
- `nickname`: 昵称
- `created_at`: 创建时间

### Signin（签到）
- `signin_id`: UUID
- `user_id`: 用户ID
- `check_in_time`: 签到时间
- `status`: 签到状态

### Contact（紧急联系人）
- `contact_id`: UUID
- `user_id`: 用户ID
- `name`: 姓名
- `phone`: 电话
- `priority`: 优先级

### SOS（紧急求助）
- `sos_id`: UUID
- `user_id`: 用户ID
- `location`: 位置
- `status`: 状态

### Alert（预警）
- `alert_id`: UUID
- `user_id`: 用户ID
- `alert_type`: 预警类型
- `status`: 状态

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t qilema-backend .

# 运行容器
docker run -p 8000:8000 --env-file .env qilema-backend
```

### 生产环境配置

```bash
# 使用 PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/qilema

# 使用 Redis
REDIS_URL=redis://localhost:6379/0

# 关闭调试模式
DEBUG=False

# 限制 CORS
CORS_ORIGINS=https://yourdomain.com
```

## 监控

### Prometheus 指标

服务自动暴露以下指标：

- `http_requests_total` - HTTP 请求总数
- `http_request_duration_seconds` - 请求耗时
- `active_users` - 活跃用户数

### 日志

- `logs/app.log` - 应用日志
- `logs/error.log` - 错误日志

## 测试账号

- **手机号**: 13800138000
- **密码**: Test123456

## 常见问题

### 数据库连接失败

检查 `DATABASE_URL` 配置是否正确。

### CORS 错误

检查 `CORS_ORIGINS` 配置是否包含前端地址。

### Token 过期

使用 `/api/v1/auth/refresh` 端点刷新令牌。

## 参考文档

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Pydantic v2 文档](https://docs.pydantic.dev/)
- [项目主文档](../README.md)

## 许可证

MIT License

---

**当前版本**: v1.0.0

**最后更新**: 2024-02-24
