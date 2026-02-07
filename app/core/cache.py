"""
通用缓存装饰器
"""
import json
import hashlib
from functools import wraps
from typing import Optional, Callable, Any
import logging
import time

from app.core.redis import redis_manager

logger = logging.getLogger(__name__)


def cache(
    ttl: int,
    key_prefix: str,
    key_builder: Optional[Callable] = None,
    condition: Optional[Callable] = None
):
    """缓存装饰器

    Args:
        ttl: 缓存生存时间（秒）
        key_prefix: 缓存键前缀
        key_builder: 自定义缓存键生成函数，签名为 key_builder(*args, **kwargs)
        condition: 缓存条件函数，签名为 condition(*args, **kwargs)，返回True则缓存

    Returns:
        装饰器函数

    Example:
        @cache(ttl=300, key_prefix="user")
        def get_user(user_id):
            return db.query(User).filter(User.user_id == user_id).first()
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 记录请求
            redis_manager._record_request()

            # 检查缓存条件
            if condition:
                try:
                    if not condition(*args, **kwargs):
                        # 不满足条件，直接执行函数
                        redis_manager._record_success()
                        return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"缓存条件检查失败: {e}")

            # 生成缓存键
            if key_builder:
                cache_key = key_prefix + ":" + key_builder(*args, **kwargs)
            else:
                # 默认键生成策略：基于函数名和参数
                args_str = str(args) + str(sorted(kwargs.items()))
                args_hash = hashlib.md5(args_str.encode()).hexdigest()
                cache_key = f"{key_prefix}:{func.__name__}:{args_hash}"

            try:
                # 获取Redis客户端
                start_time = time.time()
                redis_client = redis_manager.get_sync_client()
                if redis_client is None:
                    # Redis不可用，跳过缓存，直接执行函数
                    logger.warning("Redis不可用，跳过缓存")
                    redis_manager._record_failure()
                    return func(*args, **kwargs)

                # 尝试从缓存获取
                cached_value = redis_client.get(cache_key)
                if cached_value is not None:
                    # 缓存命中
                    redis_manager._record_cache_hit()
                    redis_manager._record_success()
                    redis_manager._update_avg_latency((time.time() - start_time) * 1000)

                    # 反序列化
                    try:
                        return json.loads(cached_value)
                    except json.JSONDecodeError:
                        # 不是JSON格式，直接返回
                        return cached_value

                # 缓存未命中
                redis_manager._record_cache_miss()

                # 执行函数
                result = func(*args, **kwargs)

                # 序列化并缓存结果
                try:
                    if isinstance(result, (dict, list, int, float, bool, str)) or result is None:
                        # 可序列化的类型，使用JSON
                        cached_value = json.dumps(result)
                    else:
                        # 其他类型，直接存储
                        cached_value = str(result)
                except (TypeError, ValueError) as e:
                    logger.warning(f"缓存结果序列化失败: {e}")
                    redis_manager._record_success()
                    return result

                # 设置缓存（带TTL）
                redis_client.setex(cache_key, ttl, cached_value)

                redis_manager._record_success()
                redis_manager._update_avg_latency((time.time() - start_time) * 1000)

                return result

            except Exception as e:
                # Redis错误，降级到直接执行函数
                logger.warning(f"缓存操作失败，降级到直接执行: {e}")
                redis_manager._record_failure()
                return func(*args, **kwargs)

        return wrapper
    return decorator


def cache_result(key: str, value: Any, ttl: int = 3600):
    """缓存结果

    Args:
        key: 缓存键
        value: 缓存值
        ttl: 缓存生存时间（秒）
    """
    try:
        redis_manager._record_request()
        start_time = time.time()

        redis_client = redis_manager.get_sync_client()
        if redis_client is None:
            # Redis不可用，跳过缓存
            logger.warning("Redis不可用，跳过缓存结果")
            redis_manager._record_failure()
            return

        # 序列化值
        if isinstance(value, (dict, list, int, float, bool, str)) or value is None:
            cached_value = json.dumps(value)
        else:
            cached_value = str(value)

        # 设置缓存
        redis_client.setex(key, ttl, cached_value)

        redis_manager._record_success()
        redis_manager._update_avg_latency((time.time() - start_time) * 1000)

    except Exception as e:
        logger.warning(f"缓存结果失败: {e}")
        redis_manager._record_failure()


def get_cached(key: str) -> Optional[Any]:
    """获取缓存值

    Args:
        key: 缓存键

    Returns:
        缓存值，如果不存在则返回None
    """
    try:
        redis_manager._record_request()
        start_time = time.time()

        redis_client = redis_manager.get_sync_client()
        cached_value = redis_client.get(key)

        if cached_value is not None:
            redis_manager._record_cache_hit()
            redis_manager._record_success()
            redis_manager._update_avg_latency((time.time() - start_time) * 1000)

            try:
                return json.loads(cached_value)
            except json.JSONDecodeError:
                return cached_value

        redis_manager._record_cache_miss()
        redis_manager._record_success()
        redis_manager._update_avg_latency((time.time() - start_time) * 1000)

        return None

    except Exception as e:
        logger.warning(f"获取缓存失败: {e}")
        redis_manager._record_failure()
        return None


def invalidate_cache(key: str):
    """失效缓存

    Args:
        key: 缓存键（支持通配符）
    """
    try:
        redis_manager._record_request()
        start_time = time.time()

        redis_client = redis_manager.get_sync_client()
        if redis_client is None:
            # Redis不可用，跳过缓存失效
            logger.warning("Redis不可用，跳过缓存失效")
            redis_manager._record_failure()
            return

        redis_client.delete(key)

        redis_manager._record_success()
        redis_manager._update_avg_latency((time.time() - start_time) * 1000)

    except Exception as e:
        logger.warning(f"失效缓存失败: {e}")
        redis_manager._record_failure()


def cache_clear(pattern: str = "*"):
    """清除匹配模式的缓存

    Args:
        pattern: 缓存键模式，支持通配符
    """
    try:
        redis_manager._record_request()
        start_time = time.time()

        redis_client = redis_manager.get_sync_client()

        # 获取匹配的所有键
        keys = redis_client.keys(pattern)

        if keys:
            # 删除所有匹配的键
            redis_client.delete(*keys)
            logger.info(f"清除了 {len(keys)} 个缓存键")

        redis_manager._record_success()
        redis_manager._update_avg_latency((time.time() - start_time) * 1000)

    except Exception as e:
        logger.warning(f"清除缓存失败: {e}")
        redis_manager._record_failure()


class CacheInvalidator:
    """缓存失效管理器"""

    def __init__(self, key_prefix: str):
        """初始化

        Args:
            key_prefix: 缓存键前缀
        """
        self.key_prefix = key_prefix

    def invalidate(self, *keys):
        """失效指定键的缓存

        Args:
            *keys: 缓存键的后缀部分
        """
        for key_suffix in keys:
            full_key = f"{self.key_prefix}:{key_suffix}"
            invalidate_cache(full_key)

    def invalidate_pattern(self, pattern: str):
        """失效匹配模式的缓存

        Args:
            pattern: 键后缀模式
        """
        full_pattern = f"{self.key_prefix}:{pattern}"
        cache_clear(full_pattern)

    def invalidate_all(self):
        """失效所有相关缓存"""
        cache_clear(f"{self.key_prefix}:*")


# 缓存穿透防护 - 空值缓存键标记
NULL_VALUE_MARKER = "__CACHE_NULL__"
NULL_VALUE_TTL = 60  # 空值缓存TTL（秒）


def get_cached_with_null_protection(key: str) -> tuple[Optional[Any], bool]:
    """获取缓存值（带缓存穿透防护）

    Args:
        key: 缓存键

    Returns:
        tuple: (缓存值, 是否为空值标记)
               如果缓存不存在，返回 (None, False)
               如果缓存是空值标记，返回 (None, True)
               如果缓存存在正常值，返回 (值, False)
    """
    cached_value = get_cached(key)

    if cached_value is None:
        return None, False

    if cached_value == NULL_VALUE_MARKER:
        # 命中空值缓存，防止缓存穿透
        logger.debug(f"命中空值缓存，防止缓存穿透: {key}")
        return None, True

    return cached_value, False


def cache_result_with_null_protection(key: str, value: Any, ttl: int = 3600):
    """缓存结果（带缓存穿透防护）

    当值为None时，缓存空值标记以防止缓存穿透

    Args:
        key: 缓存键
        value: 缓存值（如果为None，则缓存空值标记）
        ttl: 正常值的缓存生存时间（秒）
    """
    if value is None:
        # 缓存空值标记，防止缓存穿透
        # 空值的TTL较短，避免长期缓存无效数据
        cache_result(key, NULL_VALUE_MARKER, ttl=NULL_VALUE_TTL)
        logger.debug(f"缓存空值标记，防止缓存穿透: {key}")
    else:
        cache_result(key, value, ttl=ttl)


def cache_with_null_protection(
    ttl: int,
    key_prefix: str,
    key_builder: Optional[Callable] = None,
    null_ttl: int = NULL_VALUE_TTL
):
    """缓存装饰器（带缓存穿透防护）

    当函数返回None时，缓存空值标记以防止缓存穿透

    Args:
        ttl: 正常值的缓存生存时间（秒）
        key_prefix: 缓存键前缀
        key_builder: 自定义缓存键生成函数
        null_ttl: 空值的缓存生存时间（秒）

    Returns:
        装饰器函数

    Example:
        @cache_with_null_protection(ttl=300, key_prefix="user")
        def get_user(user_id):
            return db.query(User).filter(User.user_id == user_id).first()
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_builder:
                cache_key = key_prefix + ":" + key_builder(*args, **kwargs)
            else:
                args_str = str(args) + str(sorted(kwargs.items()))
                args_hash = hashlib.md5(args_str.encode()).hexdigest()
                cache_key = f"{key_prefix}:{func.__name__}:{args_hash}"

            # 尝试从缓存获取
            cached_value, is_null = get_cached_with_null_protection(cache_key)

            if is_null:
                # 命中空值缓存，直接返回None
                return None

            if cached_value is not None:
                # 命中正常缓存
                return cached_value

            # 缓存未命中，执行函数
            result = func(*args, **kwargs)

            # 缓存结果（包含空值防护）
            if result is None:
                cache_result(cache_key, NULL_VALUE_MARKER, ttl=null_ttl)
            else:
                cache_result(cache_key, result, ttl=ttl)

            return result

        return wrapper
    return decorator
