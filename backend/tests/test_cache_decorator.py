"""
测试通用缓存装饰器
"""

from unittest.mock import Mock, patch

import pytest
from app.core.cache import cache, cache_clear, cache_result, invalidate_cache


class TestCacheDecorator:
    """测试缓存装饰器"""

    @patch("app.core.cache.redis_manager")
    def test_cache_decorator_basic(self, mock_redis_manager):
        """测试基本缓存装饰器"""
        # Mock Redis客户端
        mock_client = Mock()
        mock_client.get = Mock(return_value=None)  # 缓存未命中
        mock_client.setex = Mock()  # 设置缓存
        mock_redis_manager.get_sync_client = Mock(return_value=mock_client)

        # 定义带缓存的函数
        @cache(ttl=60, key_prefix="test")
        def expensive_function(x):
            return x * 2

        # 第一次调用（缓存未命中）
        result1 = expensive_function(5)
        assert result1 == 10

        # 验证调用了原函数
        assert mock_client.setex.called

    @patch("app.core.cache.redis_manager")
    def test_cache_decorator_hit(self, mock_redis_manager):
        """测试缓存命中"""
        # Mock Redis客户端
        mock_client = Mock()
        mock_client.get = Mock(return_value="10")  # 缓存命中
        mock_client.setex = Mock()  # 设置缓存
        mock_redis_manager.get_sync_client = Mock(return_value=mock_client)

        @cache(ttl=60, key_prefix="test")
        def expensive_function(x):
            return x * 2

        # 第一次调用（缓存命中）
        result = expensive_function(5)
        assert result == 10

        # 验证没有调用原函数（缓存命中，不执行函数体）
        assert not mock_client.setex.called

    @patch("app.core.cache.redis_manager")
    def test_cache_ttl_configuration(self, mock_redis_manager):
        """测试TTL配置"""
        # Mock Redis客户端
        mock_client = Mock()
        mock_client.get = Mock(return_value=None)
        mock_client.setex = Mock()
        mock_redis_manager.get_sync_client = Mock(return_value=mock_client)

        @cache(ttl=300, key_prefix="test")
        def expensive_function():
            return "result"

        expensive_function()

        # 验证TTL设置正确
        call_args = mock_client.setex.call_args
        assert call_args is not None
        args, kwargs = call_args
        # setex的第二个参数是TTL（秒）
        assert args[1] == 300

    @patch("app.core.cache.redis_manager")
    def test_cache_custom_key(self, mock_redis_manager):
        """测试自定义缓存键"""
        # Mock Redis客户端
        mock_client = Mock()
        mock_client.get = Mock(return_value=None)
        mock_client.setex = Mock()
        mock_redis_manager.get_sync_client = Mock(return_value=mock_client)

        def custom_key_builder(*args, **kwargs):
            return f"custom:{args[0]}"

        @cache(ttl=60, key_prefix="test", key_builder=custom_key_builder)
        def expensive_function(x):
            return x * 2

        expensive_function(5)

        # 验证使用了自定义键
        call_args = mock_client.setex.call_args
        args, kwargs = call_args
        cache_key = args[0]
        assert "custom:5" in cache_key

    @patch("app.core.cache.redis_manager")
    def test_cache_with_multiple_arguments(self, mock_redis_manager):
        """测试多个参数的缓存键"""
        # Mock Redis客户端
        mock_client = Mock()
        mock_client.get = Mock(return_value=None)
        mock_client.setex = Mock()
        mock_redis_manager.get_sync_client = Mock(return_value=mock_client)

        @cache(ttl=60, key_prefix="test")
        def expensive_function(a, b, c=None):
            return a + b + (c or 0)

        # 调用一次
        expensive_function(1, 2, c=3)
        first_key = mock_client.setex.call_args[0][0]

        # 用不同参数调用
        mock_client.get = Mock(return_value=None)
        mock_client.setex = Mock()
        expensive_function(2, 3, c=4)
        second_key = mock_client.setex.call_args[0][0]

        # 验证不同参数生成不同的缓存键
        assert first_key != second_key
        assert "test:expensive_function" in first_key
        assert "test:expensive_function" in second_key

    @patch("app.core.cache.redis_manager")
    def test_cache_condition(self, mock_redis_manager):
        """测试条件缓存"""
        # Mock Redis客户端
        mock_client = Mock()
        mock_client.get = Mock(return_value=None)
        mock_client.setex = Mock()
        mock_redis_manager.get_sync_client = Mock(return_value=mock_client)

        @cache(ttl=60, key_prefix="test", condition=lambda x: x > 0)
        def expensive_function(x):
            return x * 2

        # 满足条件的调用（应该缓存）
        expensive_function(5)
        assert mock_client.setex.call_count == 1

        # 不满足条件的调用（不应该缓存）
        expensive_function(-1)
        assert mock_client.setex.call_count == 1  # 还是1，没有增加

    @patch("app.core.cache.redis_manager")
    def test_cache_clear(self, mock_redis_manager):
        """测试清除缓存"""
        # Mock Redis客户端
        mock_client = Mock()
        mock_client.keys = Mock(return_value=["test:key1", "test:key2"])
        mock_client.delete = Mock()
        mock_redis_manager.get_sync_client = Mock(return_value=mock_client)

        # 清除缓存
        cache_clear("test:*")

        # 验证调用删除
        assert mock_client.delete.called

    @patch("app.core.cache.redis_manager")
    def test_cache_result_function(self, mock_redis_manager):
        """测试cache_result辅助函数"""
        # Mock Redis客户端
        mock_client = Mock()
        mock_client.setex = Mock()
        mock_redis_manager.get_sync_client = Mock(return_value=mock_client)

        # 缓存结果
        cache_result("test:key", "value", ttl=60)

        # 验证设置了缓存
        assert mock_client.setex.called

    @patch("app.core.cache.redis_manager")
    def test_invalidate_cache(self, mock_redis_manager):
        """测试缓存失效"""
        # Mock Redis客户端
        mock_client = Mock()
        mock_client.delete = Mock()
        mock_redis_manager.get_sync_client = Mock(return_value=mock_client)

        # 失效缓存
        invalidate_cache("test:key")

        # 验证调用了删除
        assert mock_client.delete.called
        call_args = mock_client.delete.call_args
        args, kwargs = call_args
        assert "test:key" in args

    @patch("app.core.cache.redis_manager")
    def test_cache_json_serialization(self, mock_redis_manager):
        """测试JSON序列化"""
        # Mock Redis客户端
        mock_client = Mock()
        mock_client.get = Mock(return_value='{"x": 10}')
        mock_client.setex = Mock()
        mock_redis_manager.get_sync_client = Mock(return_value=mock_client)

        @cache(ttl=60, key_prefix="test")
        def expensive_function(x):
            return {"x": x * 2}

        # 第一次调用（缓存命中）
        result = expensive_function(5)
        assert result == {"x": 10}
        assert isinstance(result, dict)

    @patch("app.core.cache.redis_manager")
    def test_cache_with_exception(self, mock_redis_manager):
        """测试函数抛出异常时的缓存行为"""
        # Mock Redis客户端
        mock_client = Mock()
        mock_client.get = Mock(return_value=None)
        mock_client.setex = Mock()
        mock_redis_manager.get_sync_client = Mock(return_value=mock_client)

        @cache(ttl=60, key_prefix="test")
        def expensive_function():
            raise ValueError("Test error")

        # 调用应该抛出异常
        with pytest.raises(ValueError):
            expensive_function()

        # 验证没有设置缓存（函数失败）
        assert not mock_client.setex.called
