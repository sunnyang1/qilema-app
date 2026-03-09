"""
FastAPI应用主入口
"""

import logging

from app.api import api_router
from app.core.config import settings, setup_logging
from app.core.database import init_db
from app.core.error_handlers import register_exception_handlers
from app.core.middleware import setup_middleware
from app.core.prometheus_metrics import app_info, metrics
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# 创建速率限制器
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    debug=settings.DEBUG,
    # 重新启用 OpenAPI 文档
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
)

# 设置自定义中间件（异常处理、请求日志、请求ID）
setup_middleware(app)

# 注册全局异常处理器
register_exception_handlers(app)

# 注册API路由
app.include_router(api_router)

# 注册Prometheus metrics端点
app.add_route("/metrics", metrics)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
