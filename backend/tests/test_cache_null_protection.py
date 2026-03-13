"""
测试缓存穿透防护功能
"""

from unittest.mock import patch

from app.core.cache import (
    NULL_VALUE_MARKER,
    cache_result_with_null_protection,
    cache_with_null_protection,
    get_cached_with_null_protection,
)


class TestCacheNullProtection:
    """缓存穿透防护测试"""

    @patch("app.core.cache.get_cached")
    def test_get_cached_with_null_protection_cache_miss(self, mock_get_cached):
        """测试缓存未命中"""
        mock_get_cached.return_value = None

        value, is_null = get_cached_with_null_protection("test:key")

        assert value is None
        assert is_null is False

    @patch("app.core.cache.get_cached")
    def test_get_cached_with_null_protection_null_marker(self, mock_get_cached):
        """测试命中空值缓存"""
        mock_get_cached.return_value = NULL_VALUE_MARKER

        value, is_null = get_cached_with_null_protection("test:key")

        assert value is None
        assert is_null is True

    @patch("app.core.cache.get_cached")
    def test_get_cached_with_null_protection_normal_value(self, mock_get_cached):
        """测试命中正常缓存值"""
        mock_get_cached.return_value = {"id": 1, "name": "test"}

        value, is_null = get_cached_with_null_protection("test:key")

        assert value == {"id": 1, "name": "test"}
        assert is_null is False

    @patch("app.core.cache.cache_result")
    def test_cache_result_with_null_protection_normal_value(self, mock_cache_result):
        """测试缓存正常值"""
        cache_result_with_null_protection("test:key", {"id": 1}, ttl=300)

        mock_cache_result.assert_called_once_with("test:key", {"id": 1}, ttl=300)

    @patch("app.core.cache.cache_result")
    def test_cache_result_with_null_protection_null_value(self, mock_cache_result):
        """测试缓存空值（应缓存空值标记）"""
        cache_result_with_null_protection("test:key", None, ttl=300)

        mock_cache_result.assert_called_once()
        args = mock_cache_result.call_args[0]
        assert args[0] == "test:key"
        assert args[1] == NULL_VALUE_MARKER
        # 空值TTL应使用默认值

    @patch("app.core.cache.get_cached_with_null_protection")
    @patch("app.core.cache.cache_result")
    def test_cache_decorator_with_null_protection_cache_hit(
        self, mock_cache_result, mock_get_cached
    ):
        """测试装饰器缓存命中"""
        mock_get_cached.return_value = ({"id": 1}, False)

        @cache_with_null_protection(ttl=300, key_prefix="test")
        def get_data():
            return {"id": 2}  # 这个不会被执行

        result = get_data()

        assert result == {"id": 1}
        mock_cache_result.assert_not_called()

    @patch("app.core.cache.get_cached_with_null_protection")
    @patch("app.core.cache.cache_result")
    def test_cache_decorator_with_null_protection_null_hit(
        self, mock_cache_result, mock_get_cached
    ):
        """测试装饰器命中空值缓存"""
        mock_get_cached.return_value = (None, True)

        @cache_with_null_protection(ttl=300, key_prefix="test")
        def get_data():
            return {"id": 2}  # 这个不会被执行

        result = get_data()

        assert result is None
        mock_cache_result.assert_not_called()

    @patch("app.core.cache.get_cached_with_null_protection")
    @patch("app.core.cache.cache_result")
    def test_cache_decorator_with_null_protection_cache_miss_normal(
        self, mock_cache_result, mock_get_cached
    ):
        """测试装饰器缓存未命中，函数返回正常值"""
        mock_get_cached.return_value = (None, False)

        @cache_with_null_protection(ttl=300, key_prefix="test")
        def get_data():
            return {"id": 1}

        result = get_data()

        assert result == {"id": 1}
        # 验证缓存结果被调用，缓存键包含函数名和哈希
        mock_cache_result.assert_called_once()
        args = mock_cache_result.call_args[0]
        assert args[0].startswith("test:get_data:")
        assert args[1] == {"id": 1}

    @patch("app.core.cache.get_cached_with_null_protection")
    @patch("app.core.cache.cache_result")
    def test_cache_decorator_with_null_protection_cache_miss_null(
        self, mock_cache_result, mock_get_cached
    ):
        """测试装饰器缓存未命中，函数返回None（应缓存空值标记）"""
        mock_get_cached.return_value = (None, False)

        @cache_with_null_protection(ttl=300, key_prefix="test")
        def get_data():
            return None

        result = get_data()

        assert result is None
        mock_cache_result.assert_called_once()
        args = mock_cache_result.call_args[0]
        assert args[0].startswith("test:get_data:")
        assert args[1] == NULL_VALUE_MARKER
