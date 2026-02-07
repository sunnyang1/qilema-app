"""
Redis连接管理
"""
import redis
import redis.asyncio as aioredis
from typing import Optional, Any, Union, Dict
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import json
import logging
import time
from dataclasses import dataclass, field

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisConnectionError(Exception):
    """Redis连接异常"""
    pass


@dataclass
class RedisHealthInfo:
    """Redis健康信息"""
    is_healthy: bool
    latency_ms: float
    connected_clients: int = 0
    used_memory_human: str = ""
    uptime_in_seconds: int = 0
    redis_version: str = ""
    error_message: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RedisStats:
    """Redis统计信息"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_cache_hits: int = 0
    total_cache_misses: int = 0
    avg_latency_ms: float = 0.0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None


class RedisManager:
    """Redis连接管理器（单例模式）"""

    _instance = None
    _sync_client: Optional[redis.Redis] = None
    _async_client: Optional[aioredis.Redis] = None
    _stats = RedisStats()
    _connection_pool: Optional[redis.ConnectionPool] = None

    def __new__(cls):
        """确保单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_sync_client(cls) -> Optional[redis.Redis]:
        """获取同步Redis客户端

        Returns:
            Optional[redis.Redis]: 同步Redis客户端，如果连接失败返回None

        Note:
            Redis连接失败时不会抛出异常，而是返回None
            调用方应该检查返回值是否为None
        """
        if cls._sync_client is None or cls._connection_pool is None:
            try:
                # 创建连接池
                cls._connection_pool = redis.ConnectionPool.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    socket_keepalive=True,
                    socket_keepalive_options={},
                    health_check_interval=30,
                    retry_on_timeout=True,
                    max_connections=50
                )

                # 创建客户端
                cls._sync_client = redis.Redis(
                    connection_pool=cls._connection_pool
                )

                # 测试连接（带重试）
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        start_time = time.time()
                        cls._sync_client.ping()
                        latency_ms = (time.time() - start_time) * 1000
                        logger.info(f"Redis同步客户端连接成功 (延迟: {latency_ms:.2f}ms)")
                        break
                    except Exception as e:
                        if attempt == max_retries - 1:
                            # 最后一次重试失败，记录警告但不抛出异常
                            logger.warning(f"Redis连接失败（降级模式）: {e}")
                            cls._sync_client = None
                            cls._connection_pool = None
                            cls._record_error(f"连接失败: {e}")
                            return None
                        logger.warning(f"Redis连接重试 {attempt + 1}/{max_retries}: {e}")
                        time.sleep(0.5 * (attempt + 1))

            except Exception as e:
                logger.warning(f"Redis同步客户端连接失败（降级模式）: {e}")
                cls._sync_client = None
                cls._connection_pool = None
                cls._record_error(f"连接失败: {e}")
                return None

        return cls._sync_client

    @classmethod
    def get_async_client(cls) -> Optional[aioredis.Redis]:
        """获取异步Redis客户端

        Returns:
            Optional[aioredis.Redis]: 异步Redis客户端，如果连接失败返回None

        Note:
            Redis连接失败时不会抛出异常，而是返回None
        """
        if cls._async_client is None:
            try:
                # 创建异步连接池
                cls._async_client = aioredis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    health_check_interval=30,
                    retry_on_timeout=True,
                    max_connections=50
                )

                # 测试连接
                import asyncio
                start_time = time.time()
                asyncio.run(cls._async_client.ping())
                latency_ms = (time.time() - start_time) * 1000
                logger.info(f"Redis异步客户端连接成功 (延迟: {latency_ms:.2f}ms)")

            except Exception as e:
                logger.warning(f"Redis异步客户端连接失败（降级模式）: {e}")
                cls._async_client = None
                cls._record_error(f"异步连接失败: {e}")

        return cls._async_client

    @classmethod
    def check_health(cls) -> bool:
        """检查Redis健康状态

        Returns:
            bool: Redis是否健康
        """
        try:
            client = cls.get_sync_client()
            start_time = time.time()
            client.ping()
            latency_ms = (time.time() - start_time) * 1000

            # 记录成功的健康检查
            cls._stats.successful_requests += 1
            cls._update_avg_latency(latency_ms)

            return True
        except Exception as e:
            cls._record_error(f"健康检查失败: {e}")
            logger.warning(f"Redis健康检查失败: {e}")
            return False

    @classmethod
    def get_health_info(cls) -> RedisHealthInfo:
        """获取详细的Redis健康信息

        Returns:
            RedisHealthInfo: 健康信息对象
        """
        try:
            client = cls.get_sync_client()

            # 测量延迟
            start_time = time.time()
            client.ping()
            latency_ms = (time.time() - start_time) * 1000

            # 获取Redis信息
            info = client.info()

            return RedisHealthInfo(
                is_healthy=True,
                latency_ms=latency_ms,
                connected_clients=info.get('connected_clients', 0),
                used_memory_human=info.get('used_memory_human', ''),
                uptime_in_seconds=info.get('uptime_in_seconds', 0),
                redis_version=info.get('redis_version', ''),
                timestamp=datetime.utcnow()
            )

        except Exception as e:
            cls._record_error(f"获取健康信息失败: {e}")
            return RedisHealthInfo(
                is_healthy=False,
                latency_ms=0,
                error_message=str(e),
                timestamp=datetime.utcnow()
            )

    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """获取Redis统计信息

        Returns:
            Dict[str, Any]: 统计信息字典
        """
        return {
            "total_requests": cls._stats.total_requests,
            "successful_requests": cls._stats.successful_requests,
            "failed_requests": cls._stats.failed_requests,
            "total_cache_hits": cls._stats.total_cache_hits,
            "total_cache_misses": cls._stats.total_cache_misses,
            "cache_hit_rate": cls._calculate_hit_rate(),
            "avg_latency_ms": cls._stats.avg_latency_ms,
            "success_rate": cls._calculate_success_rate(),
            "last_error": cls._stats.last_error,
            "last_error_time": cls._stats.last_error_time.isoformat() if cls._stats.last_error_time else None
        }

    @classmethod
    def get_connection_pool_info(cls) -> Dict[str, Any]:
        """获取连接池信息

        Returns:
            Dict[str, Any]: 连接池信息
        """
        if cls._connection_pool is None:
            return {"status": "未初始化"}

        try:
            return {
                "status": "已初始化",
                "connection_kwargs": cls._connection_pool.connection_kwargs,
                "max_connections": cls._connection_pool.max_connections,
                "created_connections": getattr(cls._connection_pool, 'created_connections', 'N/A'),
                "available_connections": getattr(cls._connection_pool, 'available_connections', 'N/A'),
            }
        except Exception as e:
            return {
                "status": "错误",
                "error": str(e)
            }

    @classmethod
    def _record_request(cls):
        """记录请求"""
        cls._stats.total_requests += 1

    @classmethod
    def _record_success(cls):
        """记录成功请求"""
        cls._stats.successful_requests += 1

    @classmethod
    def _record_failure(cls):
        """记录失败请求"""
        cls._stats.failed_requests += 1

    @classmethod
    def _record_cache_hit(cls):
        """记录缓存命中"""
        cls._stats.total_cache_hits += 1

    @classmethod
    def _record_cache_miss(cls):
        """记录缓存未命中"""
        cls._stats.total_cache_misses += 1

    @classmethod
    def _record_error(cls, error_message: str):
        """记录错误"""
        cls._stats.last_error = error_message
        cls._stats.last_error_time = datetime.utcnow()
        cls._stats.failed_requests += 1

    @classmethod
    def _update_avg_latency(cls, latency_ms: float):
        """更新平均延迟"""
        total = cls._stats.total_requests
        if total == 0:
            cls._stats.avg_latency_ms = latency_ms
        else:
            # 使用指数移动平均
            alpha = 0.1
            cls._stats.avg_latency_ms = alpha * latency_ms + (1 - alpha) * cls._stats.avg_latency_ms

    @classmethod
    def _calculate_hit_rate(cls) -> float:
        """计算缓存命中率"""
        total = cls._stats.total_cache_hits + cls._stats.total_cache_misses
        if total == 0:
            return 0.0
        return (cls._stats.total_cache_hits / total) * 100

    @classmethod
    def _calculate_success_rate(cls) -> float:
        """计算请求成功率"""
        if cls._stats.total_requests == 0:
            return 0.0
        return (cls._stats.successful_requests / cls._stats.total_requests) * 100

    @classmethod
    def reset_stats(cls):
        """重置统计信息"""
        cls._stats = RedisStats()
        logger.info("Redis统计信息已重置")

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

        if cls._connection_pool:
            try:
                cls._connection_pool.disconnect()
                cls._connection_pool = None
                logger.info("Redis连接池已关闭")
            except Exception as e:
                logger.error(f"关闭Redis连接池失败: {e}")

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


def get_redis_health_info() -> RedisHealthInfo:
    """获取详细的Redis健康信息

    Returns:
        RedisHealthInfo: 健康信息对象
    """
    return redis_manager.get_health_info()


def get_redis_stats() -> Dict[str, Any]:
    """获取Redis统计信息

    Returns:
        Dict[str, Any]: 统计信息字典
    """
    return redis_manager.get_stats()


def get_redis_connection_pool_info() -> Dict[str, Any]:
    """获取Redis连接池信息

    Returns:
        Dict[str, Any]: 连接池信息
    """
    return redis_manager.get_connection_pool_info()


def reset_redis_stats():
    """重置Redis统计信息"""
    redis_manager.reset_stats()
