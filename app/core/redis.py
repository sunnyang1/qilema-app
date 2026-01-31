"""
Redis连接管理
"""
import redis
import redis.asyncio as aioredis
from typing import Optional, Any, Union
from contextlib import asynccontextmanager
import json
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisConnectionError(Exception):
    """Redis连接异常"""
    pass


class RedisManager:
    """Redis连接管理器（单例模式）"""

    _instance = None
    _sync_client: Optional[redis.Redis] = None
    _async_client: Optional[aioredis.Redis] = None

    def __new__(cls):
        """确保单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_sync_client(cls) -> redis.Redis:
        """获取同步Redis客户端

        Returns:
            redis.Redis: 同步Redis客户端

        Raises:
            RedisConnectionError: Redis连接失败
        """
        if cls._sync_client is None:
            try:
                cls._sync_client = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                # 测试连接
                cls._sync_client.ping()
                logger.info("Redis同步客户端连接成功")
            except Exception as e:
                logger.error(f"Redis同步客户端连接失败: {e}")
                raise RedisConnectionError(f"Redis连接失败: {e}")

        return cls._sync_client

    @classmethod
    def get_async_client(cls) -> aioredis.Redis:
        """获取异步Redis客户端

        Returns:
            aioredis.Redis: 异步Redis客户端

        Raises:
            RedisConnectionError: Redis连接失败
        """
        if cls._async_client is None:
            try:
                cls._async_client = aioredis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                # 测试连接
                import asyncio
                asyncio.run(cls._async_client.ping())
                logger.info("Redis异步客户端连接成功")
            except Exception as e:
                logger.error(f"Redis异步客户端连接失败: {e}")
                raise RedisConnectionError(f"Redis连接失败: {e}")

        return cls._async_client

    @classmethod
    def check_health(cls) -> bool:
        """检查Redis健康状态

        Returns:
            bool: Redis是否健康
        """
        try:
            client = cls.get_sync_client()
            client.ping()
            return True
        except Exception as e:
            logger.warning(f"Redis健康检查失败: {e}")
            return False

    @classmethod
    def close(cls):
        """关闭Redis连接"""
        if cls._sync_client:
            try:
                cls._sync_client.close()
                cls._sync_client = None
                logger.info("Redis同步客户端已关闭")
            except Exception as e:
                logger.error(f"关闭Redis同步客户端失败: {e}")

        if cls._async_client:
            try:
                import asyncio
                asyncio.run(cls._async_client.close())
                cls._async_client = None
                logger.info("Redis异步客户端已关闭")
            except Exception as e:
                logger.error(f"关闭Redis异步客户端失败: {e}")


# 全局Redis管理器实例
redis_manager = RedisManager()


def get_redis_client() -> redis.Redis:
    """获取同步Redis客户端（依赖注入使用）

    Returns:
        redis.Redis: 同步Redis客户端
    """
    return redis_manager.get_sync_client()


def get_async_redis_client() -> aioredis.Redis:
    """获取异步Redis客户端（依赖注入使用）

    Returns:
        aioredis.Redis: 异步Redis客户端
    """
    return redis_manager.get_async_client()


def check_redis_health() -> bool:
    """检查Redis健康状态

    Returns:
        bool: Redis是否健康
    """
    return redis_manager.check_health()
