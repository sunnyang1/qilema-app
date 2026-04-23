"""
异步数据库连接和会话管理 (SQLAlchemy 2.x async 风格)

提供 AsyncEngine、AsyncSession 和依赖注入函数，
用于全面异步化后端服务。
"""

from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings


# 将同步数据库 URL 转换为异步 URL
# sqlite -> aiosqlite, postgresql -> asyncpg
def _make_async_url(url: str) -> str:
    """将同步数据库 URL 转换为异步驱动 URL"""
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///")
    elif url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://")
    elif url.startswith("postgresql+psycopg2://"):
        return url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
    return url


# 异步数据库引擎（用于 API 服务主进程）
_async_engine = None


def get_async_engine(database_url: Optional[str] = None):
    """获取或创建异步数据库引擎（单例）

    Args:
        database_url: 数据库连接字符串，如果为 None 则使用 settings.DATABASE_URL

    Returns:
        AsyncEngine: 异步数据库引擎
    """
    global _async_engine
    if _async_engine is None:
        url = _make_async_url(database_url or settings.DATABASE_URL)

        # SQLite 使用 NullPool（异步 SQLite 不支持连接池）
        if "sqlite" in url:
            connect_args = {"check_same_thread": False}
            poolclass = NullPool
        else:
            connect_args = {}
            poolclass = None

        engine_kwargs = {
            "echo": settings.DEBUG,
            "connect_args": connect_args,
        }
        if poolclass:
            engine_kwargs["poolclass"] = poolclass
        else:
            # PostgreSQL 连接池优化配置
            engine_kwargs["pool_size"] = 10
            engine_kwargs["max_overflow"] = 20
            engine_kwargs["pool_recycle"] = 3600
            engine_kwargs["pool_pre_ping"] = True

        _async_engine = create_async_engine(url, **engine_kwargs)

    return _async_engine


# 异步会话工厂（写库 / 默认）
AsyncSessionLocal = async_sessionmaker(
    get_async_engine(),
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Phase 5: 读库引擎（可选，当配置读写分离时启用）
_read_engine = None


def get_async_read_engine():
    """获取异步读库引擎（单例）

    从环境变量 DATABASE_READ_URL 构建，如果没有则回退到写库。
    """
    global _read_engine
    if _read_engine is None:
        import os

        read_url = os.environ.get("DATABASE_READ_URL")
        if read_url:
            url = _make_async_url(read_url)
            _read_engine = create_async_engine(
                url,
                pool_size=20,
                max_overflow=40,
                pool_recycle=3600,
                pool_pre_ping=True,
                echo=settings.DEBUG,
            )
        else:
            # 未配置读库，回退到写库
            _read_engine = get_async_engine()
    return _read_engine


# 异步读库会话工厂
AsyncReadSessionLocal = async_sessionmaker(
    get_async_read_engine(),
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """获取异步数据库会话（写操作，依赖注入使用）

    用法:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_async_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_async_read_db() -> AsyncGenerator[AsyncSession, None]:
    """Phase 5: 获取异步数据库读会话（读操作，走从库）

    当配置了 DATABASE_READ_URL 时走从库，否则回退到写库。

    用法:
        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_async_read_db)):
            ...
    """
    async with AsyncReadSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_async_database_health() -> bool:
    """异步检查数据库健康状态

    Returns:
        bool: 数据库是否健康
    """
    import logging

    logger = logging.getLogger(__name__)
    try:
        engine = get_async_engine()
        async with engine.connect() as conn:
            from sqlalchemy import text

            result = await conn.execute(text("SELECT 1"))
            row = result.fetchone()
            return row is not None and row[0] == 1
    except Exception as e:
        logger.error(f"异步数据库健康检查失败: {e}")
        return False
