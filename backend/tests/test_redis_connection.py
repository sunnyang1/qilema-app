"""
测试Redis连接管理
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from app.core.redis import (
    RedisConnectionError,
    RedisManager,
    check_redis_health,
    get_async_redis_client,
    get_redis_client,
    redis_manager,
)


class TestRedisConnectionManagement:
    """测试Redis连接管理"""

    @patch("app.core.redis.redis")
    def test_redis_manager_singleton(self, mock_redis_module):
        """测试Redis管理器是单例"""
        manager1 = RedisManager()
        manager2 = RedisManager()

        assert manager1 is manager2

    @patch("app.core.redis.redis")
    def test_get_sync_client(self, mock_redis_module):
        """测试获取同步Redis客户端"""
        # Mock redis.ConnectionPool
        mock_pool = Mock()
        mock_client = Mock()
        mock_client.ping = Mock(return_value=True)
        mock_redis_module.ConnectionPool.from_url = Mock(return_value=mock_pool)
        mock_redis_module.Redis = Mock(return_value=mock_client)

        # 清除缓存的客户端
        RedisManager._sync_client = None
        RedisManager._connection_pool = None

        # 获取客户端
        client = RedisManager.get_sync_client()

        # 验证
        assert client is not None
        assert client is mock_client
        mock_redis_module.ConnectionPool.from_url.assert_called_once()
        mock_redis_module.Redis.assert_called_once()

    @patch("app.core.redis.redis")
    def test_get_sync_client_caches_instance(self, mock_redis_module):
        """测试同步Redis客户端被缓存"""
        # Mock redis.ConnectionPool
        mock_pool = Mock()
        mock_client = Mock()
        mock_client.ping = Mock(return_value=True)
        mock_redis_module.ConnectionPool.from_url = Mock(return_value=mock_pool)
        mock_redis_module.Redis = Mock(return_value=mock_client)

        # 清除缓存的客户端
        RedisManager._sync_client = None
        RedisManager._connection_pool = None

        # 获取客户端两次
        client1 = RedisManager.get_sync_client()
        client2 = RedisManager.get_sync_client()

        # 验证只调用了一次from_url
        assert client1 is client2
        mock_redis_module.ConnectionPool.from_url.assert_called_once()
        mock_redis_module.Redis.assert_called_once()

    @patch("app.core.redis.redis")
    def test_get_sync_client_connection_failure(self, mock_redis_module):
        """测试同步Redis客户端连接失败"""
        # Mock redis.ConnectionPool抛出异常
        mock_redis_module.ConnectionPool.from_url = Mock(
            side_effect=Exception("Connection failed")
        )

        # 清除缓存的客户端
        RedisManager._sync_client = None
        RedisManager._connection_pool = None

        # 获取客户端应该返回None（优雅降级）
        client = RedisManager.get_sync_client()

        # 验证返回None而不是抛出异常
        assert client is None

    @patch("redis.asyncio")
    @patch("app.core.redis.aioredis")
    def test_get_async_client(self, mock_aioredis, mock_asyncio):
        """测试获取异步Redis客户端"""
        # Mock aioredis.from_url
        mock_client = Mock()

        # 创建一个返回协程的ping mock
        async def mock_ping():
            return True

        mock_client.ping = Mock(return_value=mock_ping())
        mock_aioredis.from_url = Mock(return_value=mock_client)

        # Mock asyncio.run
        mock_asyncio.run = Mock(return_value=True)

        # 清除缓存的客户端
        RedisManager._async_client = None

        # 获取客户端
        client = RedisManager.get_async_client()

        # 验证
        assert client is not None
        assert client is mock_client
        mock_aioredis.from_url.assert_called_once()

    @patch("app.core.redis.redis")
    def test_check_health_success(self, mock_redis_module):
        """测试Redis健康检查成功"""
        # Mock redis.ConnectionPool
        mock_pool = Mock()
        mock_client = Mock()
        mock_client.ping = Mock(return_value=True)
        mock_redis_module.ConnectionPool.from_url = Mock(return_value=mock_pool)
        mock_redis_module.Redis = Mock(return_value=mock_client)

        # 清除缓存的客户端
        RedisManager._sync_client = None
        RedisManager._connection_pool = None

        # 健康检查
        is_healthy = RedisManager.check_health()

        # 验证
        assert is_healthy is True
        # ping至少被调用一次
        assert mock_client.ping.call_count >= 1

    @patch("app.core.redis.redis")
    def test_check_health_failure(self, mock_redis_module):
        """测试Redis健康检查失败"""
        # Mock redis.ConnectionPool
        mock_pool = Mock()
        mock_client = Mock()
        mock_client.ping = Mock(side_effect=Exception("Connection lost"))
        mock_redis_module.ConnectionPool.from_url = Mock(return_value=mock_pool)
        mock_redis_module.Redis = Mock(return_value=mock_client)

        # 清除缓存的客户端
        RedisManager._sync_client = None
        RedisManager._connection_pool = None

        # 健康检查
        is_healthy = RedisManager.check_health()

        # 验证
        assert is_healthy is False

    @patch("app.core.redis.redis")
    def test_close_connection(self, mock_redis_module):
        """测试关闭Redis连接"""
        # Mock客户端
        mock_client = Mock()
        mock_client.close = Mock()
        mock_redis_module.from_url = Mock(return_value=mock_client)

        # 设置客户端
        RedisManager._sync_client = mock_client

        # 关闭连接
        RedisManager.close()

        # 验证
        mock_client.close.assert_called_once()
        assert RedisManager._sync_client is None

    def test_global_redis_manager_instance(self):
        """测试全局Redis管理器实例"""
        assert redis_manager is not None
        assert isinstance(redis_manager, RedisManager)

    @patch("app.core.redis.redis")
    def test_get_redis_client_function(self, mock_redis_module):
        """测试get_redis_client函数"""
        # Mock redis.ConnectionPool
        mock_pool = Mock()
        mock_client = Mock()
        mock_client.ping = Mock(return_value=True)
        mock_redis_module.ConnectionPool.from_url = Mock(return_value=mock_pool)
        mock_redis_module.Redis = Mock(return_value=mock_client)

        # 清除缓存的客户端
        RedisManager._sync_client = None
        RedisManager._connection_pool = None

        # 获取客户端
        client = get_redis_client()

        # 验证
        assert client is not None
        assert isinstance(client, Mock)

    @patch("redis.asyncio")
    @patch("app.core.redis.aioredis")
    def test_get_async_redis_client_function(self, mock_aioredis, mock_asyncio):
        """测试get_async_redis_client函数"""
        # Mock客户端
        mock_client = Mock()

        # 创建一个返回协程的ping mock
        async def mock_ping():
            return True

        mock_client.ping = Mock(return_value=mock_ping())
        mock_aioredis.from_url = Mock(return_value=mock_client)

        # Mock asyncio.run
        mock_asyncio.run = Mock(return_value=True)

        # 清除缓存的客户端
        RedisManager._async_client = None

        # 获取客户端
        client = get_async_redis_client()

        # 验证
        assert client is not None
        assert isinstance(client, Mock)

    @patch("app.core.redis.redis")
    def test_check_redis_health_function(self, mock_redis_module):
        """测试check_redis_health函数"""
        # Mock redis.ConnectionPool
        mock_pool = Mock()
        mock_client = Mock()
        mock_client.ping = Mock(return_value=True)
        mock_redis_module.ConnectionPool.from_url = Mock(return_value=mock_pool)
        mock_redis_module.Redis = Mock(return_value=mock_client)

        # 清除缓存的客户端
        RedisManager._sync_client = None
        RedisManager._connection_pool = None

        # 健康检查
        is_healthy = check_redis_health()

        # 验证
        assert is_healthy is True

    @patch("app.core.redis.redis")
    def test_redis_connection_from_url_with_config(self, mock_redis_module):
        """测试使用配置的Redis URL创建连接"""
        # Mock redis.ConnectionPool
        mock_pool = Mock()
        mock_client = Mock()
        mock_client.ping = Mock(return_value=True)
        mock_redis_module.ConnectionPool.from_url = Mock(return_value=mock_pool)
        mock_redis_module.Redis = Mock(return_value=mock_client)

        # 清除缓存的客户端
        RedisManager._sync_client = None
        RedisManager._connection_pool = None

        # 获取客户端
        RedisManager.get_sync_client()

        # 验证ConnectionPool.from_url被调用
        mock_redis_module.ConnectionPool.from_url.assert_called_once()
        call_args = mock_redis_module.ConnectionPool.from_url.call_args

        # 验证包含正确的参数
        assert call_args is not None
        args, kwargs = call_args
        # URL应该来自settings
        assert len(args) > 0
