"""
FastAPI应用主入口 (FastAPI 0.135.x 规范)

参考 FastAPI 0.135.x 文档:
- 使用 Lifespan 上下文管理器替代 @app.on_event
- 使用 Annotated[..., Depends(...)] 模式
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api import api_router
from app.core.config import settings, setup_logging
from app.core.database import init_db
from app.core.error_handlers import register_exception_handlers
from app.core.limiter import limiter
from app.core.message_queue import MessageQueue
from app.core.middleware import setup_middleware
from app.core.prometheus_metrics import app_info, metrics


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 0.135.x 推荐的 Lifespan 上下文管理器

    替代已弃用的 @app.on_event("startup") / @app.on_event("shutdown")

    在应用启动时执行初始化，在应用关闭时执行清理
    """
    # ===== 启动逻辑 =====
    # 初始化日志系统
    setup_logging(settings)
    logger = logging.getLogger(__name__)
    logger.info(f"启动{settings.APP_NAME} v{settings.APP_VERSION}")

    # 设置应用信息
    app_info.info(
        {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }
    )

    # 验证配置
    config_errors = settings.validate_configuration()
    if config_errors:
        error_message = "配置错误:\n" + "\n".join(f"- {error}" for error in config_errors)
        logger.error(error_message)
        raise RuntimeError(error_message)

    # 初始化数据库
    init_db()
    logger.info("数据库初始化完成")

    yield  # 应用运行期间

    # ===== 关闭逻辑（可选） =====
    logger.info(f"关闭{settings.APP_NAME}")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    debug=settings.DEBUG,
    lifespan=lifespan,  # 使用 lifespan 上下文管理器
)

# 设置速率限制器
app.state.limiter = limiter

# 注册速率限制异常处理器
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
    expose_headers=settings.CORS_EXPOSE_HEADERS,
)

# 设置自定义中间件（异常处理、请求日志、请求ID）
setup_middleware(app)

# 注册全局异常处理器
register_exception_handlers(app)

# 注册API路由
app.include_router(api_router)

# 注册Prometheus metrics端点
app.add_route("/metrics", metrics)


@app.get("/api/versions", tags=["meta"])
async def api_versions():
    """列出当前支持的 API 版本（US-004）。"""
    return {
        "current": "v1",
        "prefix": settings.API_V1_PREFIX,
        "versions": [
            {"name": "v1", "status": "current", "path": settings.API_V1_PREFIX},
        ],
    }


@app.get("/")
async def root():
    """根路径"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    from app.core.database import check_database_health
    from app.core.redis import check_redis_health

    # 检查数据库健康状态
    db_healthy = check_database_health()
    redis_healthy = check_redis_health()

    # 整体健康状态
    all_healthy = db_healthy and redis_healthy

    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "redis": "connected" if redis_healthy else "disconnected",
    }


@app.get("/api/v1/health")
async def health_check_v1():
    """健康检查 v1 API"""
    from app.core.database import check_database_health
    from app.core.redis import check_redis_health

    # 检查数据库健康状态
    db_healthy = check_database_health()
    redis_healthy = check_redis_health()

    # 整体健康状态
    all_healthy = db_healthy and redis_healthy

    return {
        "code": 200,
        "message": "OK",
        "data": {
            "status": "healthy" if all_healthy else "unhealthy",
            "database": "connected" if db_healthy else "disconnected",
            "redis": "connected" if redis_healthy else "disconnected",
        },
    }


@app.get("/health/detailed", tags=["monitoring"])
async def detailed_health():
    """Phase 4: 详细健康检查

    检查所有组件状态：数据库、Redis、消息队列、Worker。
    返回结构化状态，便于监控系统集成。
    """
    import asyncio
    from datetime import datetime

    from app.core.async_database import check_async_database_health
    from app.core.database import check_database_health
    from app.core.message_queue import MessageQueue
    from app.core.prometheus_metrics import BusinessMetrics
    from app.core.redis import check_redis_health

    checks = await asyncio.gather(
        _safe_check(check_database_health),
        _safe_check(check_redis_health),
        _safe_check(check_async_database_health),
        _safe_check(_check_queue_health),
        return_exceptions=True,
    )

    db_ok, redis_ok, async_db_ok, queue_ok = [
        c if not isinstance(c, Exception) else False for c in checks
    ]

    # 核心服务必须健康，Worker 降级不影响整体状态
    core_healthy = db_ok and redis_ok and async_db_ok
    status = "healthy" if core_healthy else "degraded"

    # 更新 Prometheus 指标
    BusinessMetrics.update_healthcheck("database", 1 if db_ok else 0)
    BusinessMetrics.update_healthcheck("redis", 1 if redis_ok else 0)
    BusinessMetrics.update_healthcheck("async_db", 1 if async_db_ok else 0)
    BusinessMetrics.update_healthcheck("queue", 1 if queue_ok else 0)

    return {
        "status": status,
        "components": {
            "database": {
                "status": "up" if db_ok else "down",
                "type": "sync",
            },
            "redis": {
                "status": "up" if redis_ok else "down",
            },
            "async_database": {
                "status": "up" if async_db_ok else "down",
                "type": "async",
            },
            "message_queue": {
                "status": "up" if queue_ok else "down",
                "type": "redis_streams",
            },
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


async def _safe_check(check_func):
    """安全执行健康检查，捕获异常"""
    try:
        if asyncio.iscoroutinefunction(check_func):
            return await check_func()
        return check_func()
    except Exception:
        return False


async def _check_queue_health() -> bool:
    """检查消息队列健康状态"""
    try:
        queue = MessageQueue()
        client = await queue.redis
        await client.ping()
        return True
    except Exception:
        return False


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
