"""
缓存混合类 (CacheMixin)

提供统一的缓存管理功能，可被服务类混入使用
"""

import json
import logging
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from app.core.cache import cache_result, get_cached, invalidate_cache
from app.core.cache_config import CacheConfig

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CacheMixin:
    """
    缓存混合类

    提供统一的缓存管理功能，包括：
    - 缓存键生成
    - 缓存读取
    - 缓存写入
    - 缓存失效

    使用示例:
        >>> class UserService(CacheMixin):
        ...     cache_prefix = "user"
        ...     cache_ttl = 300
        ...
        ...     def get_by_id(self, user_id: str):
        ...         # 生成缓存键
        ...         cache_key = self._make_key(user_id)
        ...         # 尝试从缓存获取
        ...         cached = self._get(cache_key)
        ...         if cached:
        ...             return cached
        ...         # 查询数据库
        ...         user = self.db.query(User).filter(...).first()
        ...         # 写入缓存
        ...         self._set(cache_key, user)
        ...         return user
    """

    # 子类需要设置的属性
    cache_prefix: str = ""
    cache_ttl: int = 300  # 默认5分钟

    def __init__(self):
        """验证必要的属性"""
        if not self.cache_prefix:
            raise ValueError(f"{self.__class__.__name__} 必须设置 cache_prefix 属性")

    def _make_key(self, *parts: Any) -> str:
        """
        生成缓存键

        Args:
            *parts: 缓存键的组成部分

        Returns:
            str: 完整的缓存键

        Example:
            >>> self._make_key("user", 123)
            'prefix:user:123'
        """
        return CacheConfig.make_key(self.cache_prefix, *parts)

    def _make_pattern(self, *parts: Any) -> str:
        """
        生成缓存键模式（用于批量失效）

        Args:
            *parts: 缓存键模式的组成部分

        Returns:
            str: 缓存键模式

        Example:
            >>> self._make_pattern("user", "*")
            'prefix:user:*'
        """
        return CacheConfig.make_pattern(self.cache_prefix, *parts)

    def _get(self, key: str) -> Optional[Any]:
        """
        从缓存获取数据

        Args:
            key: 缓存键

        Returns:
            缓存的数据或 None
        """
        try:
            data = get_cached(key)
            if data is not None:
                logger.debug(f"Cache hit: {key}")
            return data
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None

    def _set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        写入缓存

        Args:
            key: 缓存键
            value: 要缓存的数据
            ttl: 过期时间（秒），默认使用 self.cache_ttl

        Returns:
            bool: 是否成功
        """
        try:
            expire = ttl if ttl is not None else self.cache_ttl
            cache_result(key, value, ttl=expire)
            logger.debug(f"Cache set: {key} (ttl={expire})")
            return True
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False

    def _invalidate(self, key: str) -> bool:
        """
        失效单个缓存

        Args:
            key: 缓存键

        Returns:
            bool: 是否成功
        """
        try:
            invalidate_cache(key)
            logger.debug(f"Cache invalidated: {key}")
            return True
        except Exception as e:
            logger.warning(f"Cache invalidate error: {e}")
            return False

    def _invalidate_pattern(self, pattern: str) -> bool:
        """
        按模式批量失效缓存

        Args:
            pattern: 缓存键模式

        Returns:
            bool: 是否成功
        """
        try:
            invalidate_cache(pattern)
            logger.debug(f"Cache invalidated by pattern: {pattern}")
            return True
        except Exception as e:
            logger.warning(f"Cache invalidate pattern error: {e}")
            return False

    def _invalidate_list_cache(self, pattern: str = "*") -> bool:
        """
        失效列表缓存

        Args:
            pattern: 缓存键模式，默认为 "*"

        Returns:
            bool: 是否成功
        """
        key = f"{self.cache_prefix}:list:{pattern}"
        return self._invalidate_pattern(key)

    def _cached(
        self,
        key_template: str,
        ttl: Optional[int] = None,
    ) -> Callable:
        """
        装饰器：缓存方法结果

        Args:
            key_template: 缓存键模板（支持 {arg_name} 格式）
            ttl: 过期时间（秒）

        Returns:
            装饰器函数

        Example:
            >>> @self._cached("user:{user_id}")
            ... def get_user(self, user_id: str):
            ...     return self.db.query(User).filter(...).first()
        """

        def decorator(func: Callable) -> Callable:
            import functools
            import inspect

            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())

            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                # 构建格式化参数
                format_args = {}
                for i, (name, value) in enumerate(zip(param_names, args)):
                    format_args[name] = value
                format_args.update(kwargs)

                # 生成缓存键
                try:
                    cache_key = key_template.format(**format_args)
                except KeyError as e:
                    # 如果格式化失败，记录警告并使用原始模板
                    logger.warning(
                        f"缓存键模板格式化失败: {key_template}, " f"参数: {format_args}, 错误: {e}"
                    )
                    cache_key = key_template

                full_key = self._make_key(cache_key)

                # 尝试从缓存获取
                cached = self._get(full_key)
                if cached is not None:
                    return cached

                # 执行函数
                result = func(*args, **kwargs)

                # 写入缓存
                if result is not None:
                    self._set(full_key, result, ttl)

                return result

            return wrapper

        return decorator

    def cache_entity(
        self,
        entity_id: str,
        entity: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        缓存单个实体

        Args:
            entity_id: 实体ID
            entity: 实体对象
            ttl: 过期时间

        Returns:
            bool: 是否成功
        """
        key = self._make_key(entity_id)
        return self._set(key, entity, ttl)

    def get_cached_entity(self, entity_id: str) -> Optional[Any]:
        """
        获取缓存的实体

        Args:
            entity_id: 实体ID

        Returns:
            实体对象或 None
        """
        key = self._make_key(entity_id)
        return self._get(key)

    def invalidate_entity_cache(self, entity_id: str) -> bool:
        """
        失效单个实体的缓存

        Args:
            entity_id: 实体ID

        Returns:
            bool: 是否成功
        """
        key = self._make_key(entity_id)
        return self._invalidate(key)

    def invalidate_all_cache(self) -> bool:
        """
        失效该服务的所有缓存

        Returns:
            bool: 是否成功
        """
        pattern = self._make_pattern("*")
        return self._invalidate_pattern(pattern)
