# 起了吗 App — 后端架构重构方案

> 版本：v2.0 | 日期：2026-04-23 | 作者：后端架构师

---

## 目录

1. [现状评估与问题诊断](#1-现状评估与问题诊断)
2. [架构设计目标](#2-架构设计目标)
3. [目标架构总览](#3-目标架构总览)
4. [分层架构详细设计](#4-分层架构详细设计)
5. [数据库架构重设计](#5-数据库架构重设计)
6. [缓存策略](#6-缓存策略)
7. [消息队列与异步处理](#7-消息队列与异步处理)
8. [安全加固方案](#8-安全加固方案)
9. [可观测性体系](#9-可观测性体系)
10. [部署与扩缩容策略](#10-部署与扩缩容策略)
11. [分阶段迁移路线图](#11-分阶段迁移路线图)
12. [关键代码规范](#12-关键代码规范)

---

## 1. 现状评估与问题诊断

### 1.1 现有架构结构

```
FastAPI (单进程) → SQLAlchemy ORM → PostgreSQL / SQLite
                 → Redis (缓存)
                 → 通知服务 (同步调用)
```

**服务清单（16 个领域服务全部集中在一个进程中）**：
`UserService` · `CheckInService` · `SOSService` · `AlertService` · `NotificationService` · `HealthRecordService` · `MedicationService` · `DeviceService` · `AEDService` · `EmergencyCenterService` · `KnowledgeBaseService` · `AnomalyService` · `LocationService` · `HealthReportService` · `EmergencyContactService` · `EmergencyResourceService`

### 1.2 已识别的架构问题

| 类别 | 问题描述 | 严重程度 |
|------|---------|---------|
| **扩展性** | 所有服务耦合在单进程中，无法对高频模块单独扩容 | 🔴 P0 |
| **可靠性** | SOS/通知走同步调用链，任一环节超时即拖垮整个请求 | 🔴 P0 |
| **数据库** | 生产环境仍允许 SQLite（NullPool），无读写分离 | 🔴 P0 |
| **缓存** | `get_by_id` 缓存命中后仍回查数据库（二次 IO），缓存价值打折 | 🟠 P1 |
| **服务边界** | `BaseService` 全部是类方法，无法持有状态/注入依赖，测试困难 | 🟠 P1 |
| **异步** | FastAPI 路由全部是同步函数，阻塞 uvicorn event loop | 🟠 P1 |
| **连接池** | `check_database_health` 每次创建新 engine 且不复用，存在连接泄露风险 | 🟠 P1 |
| **通知熔断** | 熔断器状态默认不持久化，重启即失效 | 🟡 P2 |
| **任务调度** | 每日签到超期检测无独立 worker，依赖请求触发 | 🟡 P2 |
| **API 版本** | 只有 v1 前缀，无 API 演化机制 | 🟡 P2 |

---

## 2. 架构设计目标

### 2.1 非功能指标

| 指标 | 当前 | 目标 |
|------|------|------|
| API P95 响应时间 | ~300ms | **< 100ms** |
| SOS 触达时间 | ~2s（同步链） | **< 500ms（异步推送）** |
| 系统可用性 | ~98% | **99.9%（3 个 9）** |
| 最大并发用户 | ~500 | **10,000+** |
| 数据库查询平均 | ~50ms | **< 20ms** |
| 部署回滚时间 | 手动 ~10min | **自动 < 2min** |

### 2.2 设计原则

- **关注点分离**：每个服务只对一个业务领域负责
- **异步优先**：I/O 密集型操作全部异步化（`async/await`）
- **防御性设计**：熔断 + 降级 + 重试，任何外部依赖故障不应级联
- **可观测优先**：日志、指标、链路追踪三位一体
- **渐进式迁移**：新架构可与现有系统并行运行，不停服迁移

---

## 3. 目标架构总览

```
┌─────────────────────────────────────────────────────────┐
│                     客户端 (React Native)                │
└────────────────────────┬────────────────────────────────┘
                         │ HTTPS
┌────────────────────────▼────────────────────────────────┐
│               Nginx API Gateway                          │
│   • SSL 终结  • 限流  • 路由  • 静态资源                  │
└────┬──────────────────┬──────────────────────┬──────────┘
     │                  │                      │
┌────▼──────┐  ┌────────▼──────┐  ┌────────────▼─────────┐
│  核心 API  │  │  媒体/文件 API │  │    WebSocket 服务     │
│  服务群    │  │  (未来扩展)    │  │  (实时告警推送)        │
│  (水平扩展)│  └───────────────┘  └──────────────────────┘
└────┬──────┘
     │
┌────▼────────────────────────────────────────────────────┐
│                    内部服务层                             │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ 用户服务  │  │ 签到服务  │  │ SOS 服务 │  │ 通知服务 │ │
│  └──────────┘  └──────────┘  └──────────┘  └────┬────┘ │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │      │
│  │ 健康档案  │  │ 药物提醒  │  │ 知识库服务│       │      │
│  └──────────┘  └──────────┘  └──────────┘       │      │
└──────────────────────────┬──────────────────────┼───────┘
                           │                      │
          ┌────────────────┼──────────────────────┤
          │                │                      │
┌─────────▼──┐  ┌──────────▼──┐  ┌───────────────▼─────┐
│ PostgreSQL  │  │    Redis     │  │    消息队列 (Redis   │
│  主库(写)   │  │  缓存 + 会话 │  │    Streams / RQ)    │
│  从库(读)   │  │  + 分布式锁  │  │   异步任务 / 通知     │
└────────────┘  └─────────────┘  └─────────────────────┘
                                          │
                              ┌───────────▼──────────┐
                              │    Worker 进程群       │
                              │  • 通知发送 Worker     │
                              │  • 签到超期 Worker     │
                              │  • 报告生成 Worker     │
                              └──────────────────────┘
```

---

## 4. 分层架构详细设计

### 4.1 路由层 → 彻底异步化

**现状问题**：所有路由是同步函数，`def` 而非 `async def`，会阻塞 event loop。

**目标规范**：

```python
# ✅ 目标写法：全部使用 async def + 异步 Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_db

@router.post("/sos", response_model=SOSResponse)
async def trigger_sos(
    request: SOSRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await sos_service.trigger(db, user_id=current_user.id, data=request)
    return result
```

### 4.2 服务层 → 实例化 + 依赖注入

**现状问题**：`BaseService` 全是 `@classmethod`，无法持有状态，测试时无法 mock 依赖。

**目标规范**：

```python
# ✅ 目标：实例化服务 + 接口定义
from abc import ABC, abstractmethod

class SOSServiceProtocol(ABC):
    @abstractmethod
    async def trigger(self, db: AsyncSession, user_id: int, data: SOSRequestSchema) -> SOS:
        ...

class SOSService(SOSServiceProtocol):
    def __init__(
        self,
        notification_service: NotificationServiceProtocol,
        location_service: LocationServiceProtocol,
        cache: CacheService,
    ):
        self._notification = notification_service
        self._location = location_service
        self._cache = cache

    async def trigger(self, db: AsyncSession, user_id: int, data: SOSRequestSchema) -> SOS:
        # 1. 保存 SOS 记录
        sos = await self._create_sos_record(db, user_id, data)
        # 2. 异步发布通知任务（不阻塞主请求）
        await self._notification.enqueue_sos_alert(sos)
        return sos
```

**依赖注入容器**（`app/core/container.py` 扩展）：

```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # 基础设施
    cache = providers.Singleton(CacheService, redis_url=config.REDIS_URL)
    message_queue = providers.Singleton(MessageQueue, redis_url=config.REDIS_URL)

    # 领域服务
    notification_service = providers.Factory(
        NotificationService,
        queue=message_queue,
        circuit_breaker=providers.Factory(CircuitBreaker, config=config),
    )
    sos_service = providers.Factory(
        SOSService,
        notification_service=notification_service,
        cache=cache,
    )
```

### 4.3 数据访问层 → Repository 模式

在 Service 和 ORM 之间引入 Repository 层，隔离数据访问细节：

```python
# app/repositories/base_repository.py
from typing import Generic, TypeVar, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

ModelT = TypeVar("ModelT")

class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id: int) -> Optional[ModelT]:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        **filters,
    ) -> tuple[List[ModelT], int]:
        stmt = select(self.model)
        count_stmt = select(func.count()).select_from(self.model)
        for field, value in filters.items():
            if value is not None and hasattr(self.model, field):
                condition = getattr(self.model, field) == value
                stmt = stmt.where(condition)
                count_stmt = count_stmt.where(condition)
        total = (await self.db.execute(count_stmt)).scalar_one()
        items = (await self.db.execute(stmt.offset(offset).limit(limit))).scalars().all()
        return list(items), total

    async def create(self, **data) -> ModelT:
        instance = self.model(**data)
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def save(self, instance: ModelT) -> ModelT:
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def delete(self, instance: ModelT) -> None:
        await self.db.delete(instance)
        await self.db.flush()
```

---

## 5. 数据库架构重设计

### 5.1 读写分离

```python
# app/core/database.py — 目标版本
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# 写库（主库）
write_engine = create_async_engine(
    settings.DATABASE_WRITE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,           # 自动检测连接存活
    pool_recycle=3600,
    echo=settings.DEBUG,
)

# 读库（从库，可多个）
read_engine = create_async_engine(
    settings.DATABASE_READ_URL,   # 从库 URL
    pool_size=20,                 # 读库连接池更大
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600,
)

AsyncWriteSession = async_sessionmaker(write_engine, expire_on_commit=False)
AsyncReadSession = async_sessionmaker(read_engine, expire_on_commit=False)

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """写操作专用会话"""
    async with AsyncWriteSession() as session:
        yield session

async def get_read_db() -> AsyncGenerator[AsyncSession, None]:
    """读操作专用会话（走从库）"""
    async with AsyncReadSession() as session:
        yield session
```

### 5.2 连接池优化配置

```yaml
# config.prod.yaml 目标配置
database:
  write_url: "postgresql+asyncpg://user:pass@pg-primary:5432/qilema"
  read_url: "postgresql+asyncpg://user:pass@pg-replica:5432/qilema"
  pool_size: 10          # 基础连接数
  max_overflow: 20       # 突发额外连接
  pool_timeout: 30       # 等待连接超时
  pool_recycle: 3600     # 连接最大存活时间
  pool_pre_ping: true    # 健康检测
  connect_timeout: 5     # 连接超时
  command_timeout: 30    # 查询超时
```

### 5.3 关键索引补全

```sql
-- 签到表（高频查询）
CREATE INDEX CONCURRENTLY idx_checkins_user_created
    ON checkins(user_id, created_at DESC)
    WHERE deleted_at IS NULL;

-- SOS 请求表
CREATE INDEX CONCURRENTLY idx_sos_user_status
    ON sos_requests(user_id, status, created_at DESC);

-- 告警表
CREATE INDEX CONCURRENTLY idx_alerts_user_unread
    ON alerts(user_id, is_read, created_at DESC)
    WHERE is_read = false;

-- 药物提醒表
CREATE INDEX CONCURRENTLY idx_medication_next_reminder
    ON medication_reminder_schedules(user_id, next_reminder_at)
    WHERE is_active = true;

-- 设备数据时序索引（分区建议）
CREATE INDEX CONCURRENTLY idx_device_data_device_time
    ON device_data(device_id, recorded_at DESC);
```

### 5.4 数据库迁移策略

使用 **Alembic + 在线迁移** 确保零停机：

```bash
# 生成迁移文件
alembic revision --autogenerate -m "add_async_support_and_indexes"

# 生产环境迁移（在线，不锁表）
alembic upgrade head --sql | psql $DATABASE_URL  # 先审查 SQL

# 回滚
alembic downgrade -1
```

---

## 6. 缓存策略

### 6.1 多级缓存架构

```
请求 → L1: 进程内 LRU (5s TTL, 配置/静态数据)
          ↓ Miss
     L2: Redis (分级 TTL)
          ↓ Miss
     L3: 数据库
```

### 6.2 缓存分级 TTL 策略

| 数据类型 | TTL | 失效策略 |
|---------|-----|---------|
| 用户基础信息 | 5 分钟 | 写时删除 |
| 医疗急救中心 | 1 小时 | 定时刷新 |
| AED 设备位置 | 6 小时 | 定时刷新 |
| 知识库文章 | 24 小时 | 发布时删除 |
| JWT 黑名单 | 与 Token 等期 | 过期自动清除 |
| 签到状态 | 1 分钟 | 写时删除 |
| 当天药物提醒 | 30 分钟 | 写时删除 |

### 6.3 修复当前缓存"假命中"问题

```python
# ❌ 当前问题：缓存命中后依然回查数据库
cached_data = get_cached(cache_key)
cache_exists = cached_data is not None
result = query.first()  # ← 缓存命中时仍执行！

# ✅ 修复：真正的缓存返回，不需要再查 DB
class CacheService:
    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Awaitable[T]],
        ttl: int,
        schema: type[BaseModel] | None = None,
    ) -> T:
        raw = await self.redis.get(key)
        if raw is not None:
            data = json.loads(raw)
            return schema.model_validate(data) if schema else data
        result = await factory()
        if result is not None:
            payload = result.model_dump() if hasattr(result, "model_dump") else result
            await self.redis.setex(key, ttl, json.dumps(payload, default=str))
        return result
```

### 6.4 分布式锁（防止缓存击穿）

```python
async def get_user_with_lock(self, user_id: int) -> User | None:
    cache_key = f"user:{user_id}"
    lock_key = f"lock:user:{user_id}"

    # 尝试从缓存获取
    cached = await self.cache.get(cache_key)
    if cached:
        return User.model_validate(cached)

    # 获取分布式锁，防止缓存击穿
    async with self.cache.lock(lock_key, timeout=5):
        # 双重检查
        cached = await self.cache.get(cache_key)
        if cached:
            return User.model_validate(cached)
        # 查数据库
        user = await self.repo.get_by_id(user_id)
        if user:
            await self.cache.set(cache_key, user.model_dump(), ttl=300)
        return user
```

---

## 7. 消息队列与异步处理

### 7.1 为什么需要消息队列

SOS 触发时当前调用链：
```
POST /sos → [同步] → 查联系人 → [同步] → 发短信 → [同步] → 发推送 → 返回
              ↑ 任意环节 >30s 即超时，用户看到失败
```

引入消息队列后：
```
POST /sos → 保存 SOS 记录 → 发布 sos.triggered 事件 → 立即返回 200
                                    ↓ 异步
                             通知 Worker 消费事件
                             → 并行发短信 + 推送 + 电话
```

### 7.2 推荐方案：Redis Streams

利用已有 Redis 基础设施，无需引入新组件：

```python
# app/core/message_queue.py
import asyncio
import json
from redis.asyncio import Redis

class MessageQueue:
    STREAM_SOS = "stream:sos"
    STREAM_NOTIFICATION = "stream:notification"
    STREAM_CHECKIN_ALERT = "stream:checkin_alert"

    def __init__(self, redis: Redis):
        self.redis = redis

    async def publish(self, stream: str, event_type: str, payload: dict) -> str:
        """发布事件到 Stream"""
        message_id = await self.redis.xadd(
            stream,
            {
                "event_type": event_type,
                "payload": json.dumps(payload, default=str),
                "timestamp": int(asyncio.get_event_loop().time() * 1000),
            },
            maxlen=10000,  # 保留最近 1 万条
        )
        return message_id

    async def consume(
        self,
        stream: str,
        group: str,
        consumer: str,
        count: int = 10,
    ) -> list[dict]:
        """消费 Stream 消息（Consumer Group 保证 at-least-once）"""
        messages = await self.redis.xreadgroup(
            groupname=group,
            consumername=consumer,
            streams={stream: ">"},
            count=count,
            block=2000,  # 阻塞 2 秒等待
        )
        return messages or []

    async def ack(self, stream: str, group: str, message_id: str):
        """确认消息已处理"""
        await self.redis.xack(stream, group, message_id)
```

### 7.3 Worker 进程设计

```python
# workers/notification_worker.py
import asyncio
import logging
from app.core.message_queue import MessageQueue
from app.services.notification import NotificationService

logger = logging.getLogger(__name__)

class NotificationWorker:
    def __init__(self, queue: MessageQueue, service: NotificationService):
        self.queue = queue
        self.service = service
        self.running = False

    async def run(self):
        """Worker 主循环"""
        self.running = True
        logger.info("通知 Worker 启动")

        # 确保 Consumer Group 存在
        try:
            await self.queue.redis.xgroup_create(
                MessageQueue.STREAM_NOTIFICATION, "notification-workers", "$", mkstream=True
            )
        except Exception:
            pass  # Group 已存在

        while self.running:
            try:
                messages = await self.queue.consume(
                    MessageQueue.STREAM_NOTIFICATION,
                    group="notification-workers",
                    consumer="worker-1",
                )
                for stream, msgs in messages:
                    for msg_id, fields in msgs:
                        await self._process(msg_id, fields)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker 处理消息失败: {e}", exc_info=True)
                await asyncio.sleep(1)

    async def _process(self, msg_id: bytes, fields: dict):
        event_type = fields.get(b"event_type", b"").decode()
        payload = json.loads(fields.get(b"payload", b"{}"))

        try:
            if event_type == "sos.triggered":
                await self.service.send_sos_alerts(payload)
            elif event_type == "checkin.overdue":
                await self.service.send_overdue_alerts(payload)

            await self.queue.ack(
                MessageQueue.STREAM_NOTIFICATION, "notification-workers", msg_id
            )
        except Exception as e:
            logger.error(f"处理事件 {event_type} 失败: {e}", exc_info=True)
            # 消息不 ack，等待 PEL 超时后重试
```

### 7.4 定时任务 Worker（签到超期检测）

```python
# workers/checkin_scheduler.py
import asyncio
from datetime import datetime, timedelta

class CheckInScheduler:
    """每分钟扫描超期未签到用户，发布告警事件"""

    async def run(self):
        while True:
            try:
                await self._scan_and_alert()
            except Exception as e:
                logger.error(f"签到扫描失败: {e}")
            await asyncio.sleep(60)  # 每分钟执行

    async def _scan_and_alert(self):
        threshold = datetime.utcnow() - timedelta(hours=settings.DEFAULT_CHECKIN_HOURS)
        # 查找超期用户（使用读库）
        async with AsyncReadSession() as db:
            overdue_users = await checkin_repo.get_overdue_users(db, threshold)
            for user in overdue_users:
                await self.queue.publish(
                    MessageQueue.STREAM_CHECKIN_ALERT,
                    "checkin.overdue",
                    {"user_id": user.id, "last_checkin": str(user.last_checkin_at)},
                )
```

---

## 8. 安全加固方案

### 8.1 JWT 安全增强

```python
# 当前问题：ACCESS_TOKEN_EXPIRE_MINUTES=30，无 Refresh Token 机制
# 目标：双 Token + 黑名单

class TokenService:
    ACCESS_TTL = timedelta(minutes=15)   # 短期 Access Token
    REFRESH_TTL = timedelta(days=7)      # 长期 Refresh Token

    async def create_token_pair(self, user_id: int) -> TokenPair:
        access_token = self._sign(
            {"sub": str(user_id), "type": "access"},
            self.ACCESS_TTL,
        )
        refresh_token = self._sign(
            {"sub": str(user_id), "type": "refresh", "jti": uuid4().hex},
            self.REFRESH_TTL,
        )
        # 存储 refresh token 指纹到 Redis（用于撤销）
        await self.cache.setex(
            f"refresh:{refresh_token[:32]}",
            int(self.REFRESH_TTL.total_seconds()),
            str(user_id),
        )
        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    async def revoke_refresh_token(self, refresh_token: str):
        """登出：注销 Refresh Token"""
        await self.cache.delete(f"refresh:{refresh_token[:32]}")
```

### 8.2 API 限流分级

```python
# 不同端点差异化限流
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# 认证端点：严格限流，防暴力破解
@router.post("/auth/login")
@limiter.limit("5/minute")
async def login(...): ...

# SOS 端点：宽松限流，紧急场景
@router.post("/sos")
@limiter.limit("10/minute")
async def trigger_sos(...): ...

# 普通查询：标准限流
@router.get("/health-records")
@limiter.limit("200/minute")
async def list_health_records(...): ...
```

### 8.3 敏感数据加密

```python
# 手机号、身份证、医疗记录等敏感字段加密存储
from app.core.encryption import FieldEncryptor

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)

    # 手机号加密存储，建立哈希索引用于查询
    _phone_encrypted: Mapped[str | None] = mapped_column("phone_encrypted", String(512))
    _phone_hash: Mapped[str | None] = mapped_column("phone_hash", String(64), index=True)

    @property
    def phone(self) -> str | None:
        if self._phone_encrypted:
            return FieldEncryptor.decrypt(self._phone_encrypted)
        return None

    @phone.setter
    def phone(self, value: str | None):
        if value:
            self._phone_encrypted = FieldEncryptor.encrypt(value)
            self._phone_hash = FieldEncryptor.hash(value)  # 用于查询
        else:
            self._phone_encrypted = None
            self._phone_hash = None
```

### 8.4 SQL 注入防护

```python
# ✅ 始终使用参数化查询
stmt = select(User).where(User.email == email)  # ← SQLAlchemy 自动参数化

# ❌ 永远禁止
stmt = text(f"SELECT * FROM users WHERE email = '{email}'")  # SQL 注入风险！
```

---

## 9. 可观测性体系

### 9.1 结构化日志

```python
# 统一 JSON 日志格式（便于 ELK/Loki 采集）
import structlog

logger = structlog.get_logger()

# 使用示例
logger.info(
    "sos_triggered",
    user_id=user_id,
    sos_id=sos.id,
    location=sos.location,
    contact_count=len(contacts),
    duration_ms=elapsed_ms,
)
```

**日志字段规范**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `trace_id` | string | 分布式追踪 ID（X-Request-ID） |
| `user_id` | int | 当前用户（匿名请求为 null） |
| `event` | string | 事件名称（snake_case） |
| `duration_ms` | float | 操作耗时（毫秒） |
| `error` | string | 错误信息（仅错误日志） |
| `level` | string | 日志级别 |

### 9.2 Prometheus 指标增强

```python
# app/core/prometheus_metrics.py — 扩展版
from prometheus_client import Counter, Histogram, Gauge

# 已有指标保留，新增以下：

# SOS 触发总数
sos_triggered_total = Counter(
    "sos_triggered_total", "SOS触发总数", ["status"]
)

# 通知发送指标
notification_sent_total = Counter(
    "notification_sent_total", "通知发送总数", ["channel", "status"]
)

# 数据库连接池状态
db_pool_checked_out = Gauge(
    "db_pool_checked_out", "当前活跃数据库连接数"
)

# 消息队列积压
queue_backlog = Gauge(
    "queue_backlog_messages", "消息队列积压数量", ["stream"]
)

# 缓存命中率
cache_operations_total = Counter(
    "cache_operations_total", "缓存操作总数", ["operation", "result"]
)
```

### 9.3 健康检查细化

```python
@app.get("/health/detailed")
async def detailed_health():
    checks = await asyncio.gather(
        check_database_health(),
        check_redis_health(),
        check_queue_health(),
        check_worker_health(),
        return_exceptions=True,
    )
    db_ok, redis_ok, queue_ok, worker_ok = [
        not isinstance(c, Exception) and c for c in checks
    ]
    status = "healthy" if all([db_ok, redis_ok, queue_ok]) else "degraded"
    return {
        "status": status,
        "components": {
            "database": {"status": "up" if db_ok else "down"},
            "redis": {"status": "up" if redis_ok else "down"},
            "message_queue": {"status": "up" if queue_ok else "down"},
            "workers": {"status": "up" if worker_ok else "degraded"},
        },
        "timestamp": datetime.utcnow().isoformat(),
    }
```

---

## 10. 部署与扩缩容策略

### 10.1 容器化改进

```dockerfile
# backend/Dockerfile — 目标版本（多阶段，最小镜像）
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12-slim AS runtime
# 非 root 用户（已有，保持）
RUN useradd -m -u 1001 appuser
WORKDIR /app
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .
USER appuser

# 新增：Worker 启动脚本
COPY --chown=appuser:appuser scripts/start_worker.sh .

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "4", "--loop", "uvloop", "--http", "httptools"]
```

### 10.2 docker-compose 生产扩展

```yaml
# docker-compose.prod.yml 目标扩展
services:
  backend:
    deploy:
      replicas: 3           # 3 个 API 实例
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 256M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3

  # 新增：通知 Worker
  notification-worker:
    build: ./backend
    command: python -m workers.notification_worker
    environment:
      - ENVIRONMENT=production
    deploy:
      replicas: 2
    depends_on:
      - redis
      - postgres

  # 新增：签到调度 Worker
  checkin-scheduler:
    build: ./backend
    command: python -m workers.checkin_scheduler
    deploy:
      replicas: 1          # 单实例，避免重复调度

  # PostgreSQL 主从（生产必须）
  postgres-primary:
    image: postgres:15
    environment:
      POSTGRES_REPLICATION_MODE: master
    volumes:
      - pg_primary_data:/var/lib/postgresql/data

  postgres-replica:
    image: postgres:15
    environment:
      POSTGRES_REPLICATION_MODE: slave
      POSTGRES_MASTER_HOST: postgres-primary
    depends_on:
      - postgres-primary
```

### 10.3 Kubernetes HPA 扩缩容

```yaml
# k8s/backend-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60       # CPU 60% 触发扩容
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 70       # 内存 70% 触发扩容
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60  # 1 分钟内不重复扩容
      policies:
        - type: Pods
          value: 2
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300 # 5 分钟内不缩容（防抖）
```

---

## 11. 分阶段迁移路线图

### Phase 1 — 基础加固（第 1-2 周）优先级 P0

**目标**：不改变功能，消除现有关键风险

| 任务 | 影响 | 难度 |
|------|------|------|
| 修复 `check_database_health` 连接泄露 | 稳定性 ↑ | 低 |
| 修复缓存"假命中"（命中后仍回查 DB） | 性能 ↑ | 低 |
| 将 SQLite 生产路径关闭（强制 PostgreSQL） | 稳定性 ↑ | 低 |
| 补全关键索引（签到、SOS、告警） | 性能 ↑ | 低 |
| `BaseService` 添加 async 方法变体 | 兼容性 | 中 |

```bash
# Phase 1 分支
git checkout -b arch/phase1-stability-fix
```

### Phase 2 — 异步化（第 3-4 周）优先级 P0

**目标**：核心链路全面异步，释放 event loop

| 任务 | 影响 | 难度 |
|------|------|------|
| 引入 `asyncpg` + `SQLAlchemy async engine` | 性能 ↑↑ | 中 |
| 将 SOS / 签到 / 通知路由改为 `async def` | 性能 ↑↑ | 中 |
| 引入 Repository 层（SOS、User 先行） | 可测性 ↑ | 中 |
| 服务层改为实例化 + Protocol 定义 | 可测性 ↑ | 中 |

### Phase 3 — 消息队列（第 5-6 周）优先级 P1

**目标**：SOS/通知从同步调用改为事件驱动

| 任务 | 影响 | 难度 |
|------|------|------|
| 引入 Redis Streams 消息队列 | 可靠性 ↑↑ | 中 |
| 实现 NotificationWorker | 可靠性 ↑↑ | 中 |
| 实现 CheckinScheduler Worker | 实时性 ↑ | 低 |
| SOS 服务改为发布事件 | 响应时间 ↑↑ | 中 |

### Phase 4 — 可观测性（第 7 周）优先级 P1

**目标**：完善监控告警，实现主动发现问题

| 任务 | 影响 | 难度 |
|------|------|------|
| 引入 structlog 结构化日志 | 运维 ↑ | 低 |
| 扩展 Prometheus 指标 | 运维 ↑ | 低 |
| 细化 `/health/detailed` | 运维 ↑ | 低 |
| 接入 Grafana 告警规则 | 运维 ↑↑ | 中 |

### Phase 5 — 读写分离 & 扩容（第 8-10 周）优先级 P2

**目标**：支撑 10x 流量增长

| 任务 | 影响 | 难度 |
|------|------|------|
| PostgreSQL 主从复制配置 | 可扩展 ↑↑ | 高 |
| 引入读写分离 Session 路由 | 性能 ↑↑ | 中 |
| Kubernetes HPA 配置 | 弹性 ↑↑ | 中 |
| JWT Refresh Token 机制 | 安全 ↑ | 中 |

---

## 12. 关键代码规范

### 12.1 新代码必须遵守的规范

```python
# ✅ 强制：所有路由使用 async def
@router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_async_db)):
    ...

# ✅ 强制：依赖注入使用 Annotated 语法
from typing import Annotated
DbSession = Annotated[AsyncSession, Depends(get_async_db)]
CurrentUser = Annotated[User, Depends(get_current_active_user)]

# ✅ 强制：服务层通过 Protocol 定义接口
class UserServiceProtocol(Protocol):
    async def get_user(self, db: AsyncSession, user_id: int) -> User | None: ...

# ✅ 强制：Repository 负责所有数据库操作，Service 不直接用 Session
class UserService:
    def __init__(self, repo: UserRepository, cache: CacheService): ...
    async def get_user(self, db: AsyncSession, user_id: int) -> User | None:
        return await self.repo.get_by_id(user_id)

# ✅ 强制：异常要有明确的错误码
raise AppException(
    status_code=404,
    code="USER_NOT_FOUND",
    message=f"用户 {user_id} 不存在",
)
```

### 12.2 性能规范

```python
# ✅ 批量查询代替 N+1
users = await user_repo.get_by_ids(db, user_ids)          # 1 次查询
# ❌ 禁止
users = [await user_repo.get_by_id(db, uid) for uid in user_ids]  # N 次查询

# ✅ 使用 select_in_loading 避免 N+1
stmt = (
    select(User)
    .options(selectinload(User.emergency_contacts))  # 一次性加载关联
    .where(User.id == user_id)
)

# ✅ 只查询需要的字段
stmt = select(User.id, User.name, User.phone_hash).where(User.id == user_id)
```

---

## 附录：架构决策记录 (ADR)

| 决策 | 选择 | 备选方案 | 原因 |
|------|------|---------|------|
| 消息队列 | Redis Streams | RabbitMQ / Kafka | 复用已有 Redis，运维简单，满足当前规模 |
| 异步框架 | asyncpg + SQLAlchemy async | Tortoise ORM | 与现有 SQLAlchemy 模型兼容，迁移成本低 |
| 服务发现 | Docker Compose / K8s Service | Consul / Etcd | 项目规模不需要独立注册中心 |
| 日志格式 | structlog (JSON) | loguru | 更易于日志聚合系统（ELK/Loki）解析 |
| 缓存 | Redis (已有) | Memcached | Redis 功能更丰富（Stream/Lock/Sorted Set） |

---

> 📋 **下一步行动**
>
> 1. 团队评审本方案，确认 Phase 1 启动时间
> 2. 创建 `arch/phase1-stability-fix` 分支
> 3. 按优先级逐步落地，每个 Phase 结束后进行性能基准测试
>
> 预期完成时间：**10 周**（可根据团队规模调整）
