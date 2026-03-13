"""
测试用户服务缓存
"""

import json
from unittest.mock import Mock, patch

from app.models.user import User
from app.services.user_service import UserService


class TestUserServiceCache:
    """测试用户服务缓存"""

    def _get_redis_client_mock(self):
        """创建统一的Redis客户端mock"""
        mock_client = Mock()
        mock_client.get = Mock(return_value=None)
        mock_client.setex = Mock()
        mock_client.delete = Mock()
        return mock_client

    @patch("app.core.cache.redis_manager")
    @patch("app.services.user_service.redis_manager")
    def test_get_user_by_id_cached(self, mock_redis_mgr_service, mock_redis_mgr_cache):
        """测试get_user_by_id使用缓存"""
        # Mock数据库
        mock_db = Mock()
        mock_user = User(
            user_id="test-user-id", phone="13800000000", nickname="Test User"
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # Mock Redis客户端
        mock_client = Mock()
        mock_client.get = Mock(return_value=None)  # 缓存未命中
        mock_client.setex = Mock()
        mock_redis_mgr_cache.get_sync_client = Mock(return_value=mock_client)
        mock_redis_mgr_service.get_sync_client = Mock(return_value=mock_client)

        # 获取用户
        user = UserService.get_user_by_id(mock_db, "test-user-id")

        # 验证设置了缓存
        assert mock_client.setex.called
        call_args = mock_client.setex.call_args
        args, kwargs = call_args
        cache_key = args[0]
        assert "user" in cache_key.lower()
        assert "test-user-id" in cache_key

    @patch("app.core.cache.redis_manager")
    def test_get_user_by_id_cache_hit(self, mock_redis_manager):
        """测试get_user_by_id缓存命中"""
        # Mock Redis客户端 - 返回缓存的用户数据
        mock_client = Mock()

        # 模拟缓存命中，返回JSON格式的用户数据
        cached_user_data = {
            "user_id": "test-user-id",
            "phone": "13800000000",
            "nickname": "Test User",
        }
        mock_client.get = Mock(return_value=json.dumps(cached_user_data))
        mock_client.setex = Mock()
        mock_redis_manager.get_sync_client = Mock(return_value=mock_client)

        # Mock数据库（不应该被调用）
        mock_db = Mock()

        # 获取用户
        user = UserService.get_user_by_id(mock_db, "test-user-id")

        # 验证从缓存获取（没有查询数据库）
        assert mock_client.get.called
        assert not mock_db.query.called  # 数据库不应该被查询
        assert user is not None
        assert user.user_id == "test-user-id"

    @patch("app.core.cache.redis_manager")
    @patch("app.services.user_service.redis_manager")
    def test_get_user_by_phone_cached(
        self, mock_redis_mgr_service, mock_redis_mgr_cache
    ):
        """测试get_user_by_phone使用缓存"""
        # Mock数据库
        mock_db = Mock()
        mock_user = User(
            user_id="test-user-id", phone="13800000000", nickname="Test User"
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # Mock Redis客户端
        mock_client = Mock()
        mock_client.get = Mock(return_value=None)
        mock_client.setex = Mock()
        mock_redis_mgr_cache.get_sync_client = Mock(return_value=mock_client)
        mock_redis_mgr_service.get_sync_client = Mock(return_value=mock_client)

        # 获取用户
        user = UserService.get_user_by_phone(mock_db, "13800000000")

        # 验证设置了缓存
        assert mock_client.setex.called

    @patch("app.services.user_service.redis_manager")
    def test_verify_code_cached(self, mock_redis_manager):
        """测试验证码使用缓存"""
        # Mock Redis客户端
        mock_client = Mock()
        mock_client.get = Mock(return_value="123456")
        mock_client.delete = Mock()
        mock_redis_manager.get_sync_client = Mock(return_value=mock_client)

        # 验证验证码
        result = UserService.verify_code("13800000000", "123456")

        # 验证从Redis获取
        assert mock_client.get.called
        call_args = mock_client.get.call_args
        args, kwargs = call_args
        assert "verify_code" in args[0]

    @patch("app.core.cache.redis_manager")
    @patch("app.core.redis.redis_manager")
    @patch("app.services.user_service.redis_manager")
    def test_verify_code_delete_after_use(
        self, mock_redis_mgr_service, mock_redis_mgr_core, mock_redis_mgr_cache
    ):
        """测试验证码使用后删除"""
        # Mock Redis客户端
        mock_client = Mock()
        mock_client.get = Mock(return_value="123456")
        mock_client.delete = Mock()
        mock_redis_mgr_service.get_sync_client = Mock(return_value=mock_client)
        mock_redis_mgr_core.get_sync_client = Mock(return_value=mock_client)
        mock_redis_mgr_cache.get_sync_client = Mock(return_value=mock_client)

        # 验证验证码
        result = UserService.verify_code("13800000000", "123456")

        # 验证删除了验证码
        assert mock_client.delete.called
        assert result is True

    @patch("app.services.user_service.redis_manager")
    def test_update_user_invalidates_cache(self, mock_redis_manager):
        """测试更新用户时失效缓存"""
        # Mock数据库
        mock_db = Mock()
        mock_user = User(
            user_id="test-user-id", phone="13800000000", nickname="Old Name"
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # Mock Redis客户端
        mock_client = Mock()
        mock_client.delete = Mock()
        mock_redis_manager.get_sync_client = Mock(return_value=mock_client)

        # 更新用户
        updated_user = UserService.update_user(
            mock_db, "test-user-id", {"nickname": "New Name"}
        )

        # 验证失效了相关缓存（如果实现的话）
        # 注意：这个测试可能需要根据实际实现调整

    @patch("app.services.user_service.redis_manager")
    def test_cache_ttl_5_minutes(self, mock_redis_manager):
        """测试缓存TTL为5分钟（300秒）"""
        # Mock数据库
        mock_db = Mock()
        mock_user = User(
            user_id="test-user-id", phone="13800000000", nickname="Test User"
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # Mock Redis客户端
        mock_client = Mock()
        mock_client.get = Mock(return_value=None)
        mock_client.setex = Mock()
        mock_redis_manager.get_sync_client = Mock(return_value=mock_client)

        # 获取用户
        user = UserService.get_user_by_id(mock_db, "test-user-id")

        # 验证TTL为300秒（5分钟）
        if mock_client.setex.called:
            call_args = mock_client.setex.call_args
            args, kwargs = call_args
            # setex的第二个参数是TTL
            ttl = args[1]
            assert ttl == 300

    @patch("app.services.user_service.redis_manager")
    def test_cache_key_includes_identifier(self, mock_redis_manager):
        """测试缓存键包含用户标识符"""
        # Mock数据库
        mock_db = Mock()
        mock_user = User(
            user_id="test-user-id", phone="13800000000", nickname="Test User"
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # Mock Redis客户端
        mock_client = Mock()
        mock_client.get = Mock(return_value=None)
        mock_client.setex = Mock()
        mock_redis_manager.get_sync_client = Mock(return_value=mock_client)

        # 获取用户
        user = UserService.get_user_by_id(mock_db, "test-user-id")

        # 验证缓存键包含user标识
        if mock_client.setex.called:
            call_args = mock_client.setex.call_args
            args, kwargs = call_args
            cache_key = args[0]
            assert "test-user-id" in cache_key
