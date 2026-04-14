"""
CacheMixin 单元测试
"""

from unittest.mock import MagicMock, patch

import pytest

from app.core.cache_mixin import CacheMixin


class TestCacheMixin:
    """CacheMixin 测试类"""

    @pytest.fixture
    def cache_service(self):
        """创建测试用的 CacheMixin 子类"""

        class TestService(CacheMixin):
            cache_prefix = "test"
            cache_ttl = 300

        return TestService()

    def test_make_key(self, cache_service):
        """测试缓存键生成"""
        key = cache_service._make_key("user", "123")
        assert key == "test:user:123"

    def test_make_key_multiple_parts(self, cache_service):
        """测试多部分缓存键生成"""
        key = cache_service._make_key("list", "active", "page1")
        assert key == "test:list:active:page1"

    def test_make_pattern(self, cache_service):
        """测试缓存键模式生成"""
        pattern = cache_service._make_pattern("user", "*")
        assert pattern == "test:user:*"

    @patch("app.core.cache_mixin.get_cached")
    def test_get_cache_hit(self, mock_get_cached, cache_service):
        """测试缓存命中"""
        mock_get_cached.return_value = {"id": "123", "name": "Test"}

        result = cache_service._get("test:user:123")

        assert result == {"id": "123", "name": "Test"}
        mock_get_cached.assert_called_once_with("test:user:123")

    @patch("app.core.cache_mixin.get_cached")
    def test_get_cache_miss(self, mock_get_cached, cache_service):
        """测试缓存未命中"""
        mock_get_cached.return_value = None

        result = cache_service._get("test:user:123")

        assert result is None

    @patch("app.core.cache_mixin.get_cached")
    def test_get_cache_error(self, mock_get_cached, cache_service):
        """测试缓存获取异常处理"""
        mock_get_cached.side_effect = Exception("Redis error")

        result = cache_service._get("test:user:123")

        assert result is None

    @patch("app.core.cache_mixin.cache_result")
    def test_set_cache_success(self, mock_cache_result, cache_service):
        """测试缓存写入成功"""
        mock_cache_result.return_value = True

        result = cache_service._set("test:user:123", {"id": "123"})

        assert result is True
        mock_cache_result.assert_called_once_with(
            "test:user:123", {"id": "123"}, ttl=300
        )

    @patch("app.core.cache_mixin.cache_result")
    def test_set_cache_custom_ttl(self, mock_cache_result, cache_service):
        """测试自定义 TTL 缓存写入"""
        result = cache_service._set("test:user:123", {"id": "123"}, ttl=600)

        mock_cache_result.assert_called_once_with(
            "test:user:123", {"id": "123"}, ttl=600
        )

    @patch("app.core.cache_mixin.cache_result")
    def test_set_cache_error(self, mock_cache_result, cache_service):
        """测试缓存写入异常处理"""
        mock_cache_result.side_effect = Exception("Redis error")

        result = cache_service._set("test:user:123", {"id": "123"})

        assert result is False

    @patch("app.core.cache_mixin.invalidate_cache")
    def test_invalidate_cache(self, mock_invalidate, cache_service):
        """测试缓存失效"""
        result = cache_service._invalidate("test:user:123")

        assert result is True
        mock_invalidate.assert_called_once_with("test:user:123")

    @patch("app.core.cache_mixin.invalidate_cache")
    def test_invalidate_pattern(self, mock_invalidate, cache_service):
        """测试按模式缓存失效"""
        result = cache_service._invalidate_pattern("test:user:*")

        assert result is True
        mock_invalidate.assert_called_once_with("test:user:*")

    @patch("app.core.cache_mixin.invalidate_cache")
    def test_invalidate_list_cache(self, mock_invalidate, cache_service):
        """测试列表缓存失效"""
        result = cache_service._invalidate_list_cache("*")

        assert result is True
        mock_invalidate.assert_called_once_with("test:list:*")

    @patch("app.core.cache_mixin.get_cached")
    def test_get_cached_entity(self, mock_get_cached, cache_service):
        """测试获取缓存实体"""
        mock_entity = MagicMock()
        mock_get_cached.return_value = mock_entity

        result = cache_service.get_cached_entity("123")

        assert result == mock_entity
        mock_get_cached.assert_called_once_with("test:123")

    @patch("app.core.cache_mixin.cache_result")
    def test_cache_entity(self, mock_cache_result, cache_service):
        """测试缓存实体"""
        mock_entity = MagicMock()

        result = cache_service.cache_entity("123", mock_entity)

        assert result is True
        mock_cache_result.assert_called_once_with("test:123", mock_entity, ttl=300)

    @patch("app.core.cache_mixin.invalidate_cache")
    def test_invalidate_entity_cache(self, mock_invalidate, cache_service):
        """测试失效实体缓存"""
        result = cache_service.invalidate_entity_cache("123")

        assert result is True
        mock_invalidate.assert_called_once_with("test:123")

    @patch("app.core.cache_mixin.invalidate_cache")
    def test_invalidate_all_cache(self, mock_invalidate, cache_service):
        """测试失效所有缓存"""
        result = cache_service.invalidate_all_cache()

        assert result is True
        mock_invalidate.assert_called_once_with("test:*")


class TestCacheMixinDecorator:
    """CacheMixin 装饰器测试"""

    def test_cached_decorator_with_hit(self):
        """测试缓存装饰器命中"""

        class Service(CacheMixin):
            cache_prefix = "test"

            def get_user(self, user_id: str):
                return {"id": user_id, "name": "Test"}

        service = Service()

        # 使用 _cached 装饰器需要传递 key 参数
        decorated_func = service._cached("user:{user_id}")(service.get_user)

        with patch.object(
            service, "_get", return_value={"id": "123", "name": "Cached"}
        ) as mock_get:
            with patch.object(service, "_set") as mock_set:
                result = decorated_func("123")

                assert result == {"id": "123", "name": "Cached"}
                mock_get.assert_called_once()
                mock_set.assert_not_called()

    def test_cached_decorator_with_miss(self):
        """测试缓存装饰器未命中"""

        class Service(CacheMixin):
            cache_prefix = "test"

            def get_user(self, user_id: str):
                return {"id": user_id, "name": "Test"}

        service = Service()

        decorated_func = service._cached("user:{user_id}")(service.get_user)

        with patch.object(service, "_get", return_value=None) as mock_get:
            with patch.object(service, "_set") as mock_set:
                result = decorated_func("123")

                assert result == {"id": "123", "name": "Test"}
                mock_get.assert_called_once()
                mock_set.assert_called_once()
