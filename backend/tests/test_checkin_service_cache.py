"""
测试签到服务缓存功能
"""

from datetime import date, timedelta
from unittest.mock import MagicMock, Mock, patch

import pytest
from app.schemas.checkin import CheckInCreate
from app.services.checkin_service import CheckInService
from sqlalchemy.orm import Session


class TestCheckInServiceCache:
    """测试签到服务缓存"""

    @pytest.fixture
    def mock_db(self):
        """Mock 数据库会话"""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_redis_client(self):
        """Mock Redis 客户端"""
        client = Mock()
        client.get.return_value = None
        return client

    def test_get_user_checkins_uses_cache(self, mock_db, mock_redis_client):
        """测试获取签到记录使用缓存"""
        # Mock Redis 缓存命中 - 返回一个非空列表（truthy 值）
        mock_redis_client.get.return_value = '[{"id":1}]'.encode("utf-8")

        with patch("app.core.cache.redis_manager") as mock_redis_mgr:
            mock_redis_mgr.get_sync_client.return_value = mock_redis_client
            mock_redis_mgr.check_health.return_value = True

            # 第一次调用，应该从缓存获取
            result1 = CheckInService.get_user_checkins(mock_db, "user123", days=7)

            # 验证第一次调用也没有查询数据库（直接从缓存获取）
            mock_db.query.assert_not_called()

            # 第二次调用，也应该从缓存获取
            result2 = CheckInService.get_user_checkins(mock_db, "user123", days=7)

            # 验证数据库没有被查询（全部从缓存获取）
            mock_db.query.assert_not_called()

    def test_get_user_checkins_cache_miss(self, mock_db, mock_redis_client):
        """测试缓存未命中时查询数据库"""
        # Mock Redis 缓存未命中
        mock_redis_client.get.return_value = None

        with patch("app.core.cache.redis_manager") as mock_redis_mgr:
            mock_redis_mgr.get_sync_client.return_value = mock_redis_client
            mock_redis_mgr.check_health.return_value = True

            # 调用函数
            CheckInService.get_user_checkins(mock_db, "user123", days=7)

            # 验证数据库被查询
            assert mock_db.query.called

            # 验证缓存被设置
            assert mock_redis_client.setex.called

            # 验证TTL为3600秒（1小时）
            call_args = mock_redis_client.setex.call_args
            assert call_args[0][1] == 3600

    def test_get_checkin_stats_uses_cache(self, mock_db, mock_redis_client):
        """测试获取签到统计使用缓存"""
        from app.schemas.checkin import CheckInStatsResponse

        # Mock Redis 缓存命中
        mock_redis_client.get.return_value = '{"total_checkins":30,"current_streak":7,"longest_streak":15,"checkin_rate":100.0}'.encode(
            "utf-8"
        )

        with patch("app.core.cache.redis_manager") as mock_redis_mgr:
            mock_redis_mgr.get_sync_client.return_value = mock_redis_client
            mock_redis_mgr.check_health.return_value = True

            # 第一次调用，应该从缓存获取
            result1 = CheckInService.get_checkin_stats(mock_db, "user123", days=30)

            # 第二次调用，也应该从缓存获取
            result2 = CheckInService.get_checkin_stats(mock_db, "user123", days=30)

            # 验证数据库没有被查询（全部从缓存获取）
            mock_db.query.assert_not_called()

            # 验证返回的是 dict 类型（缓存返回的JSON反序列化后）
            assert isinstance(result1, dict) or isinstance(
                result1, CheckInStatsResponse
            )
            if isinstance(result1, dict):
                assert result1["total_checkins"] == 30
            else:
                assert result1.total_checkins == 30

    def test_get_checkin_stats_cache_miss(self, mock_db, mock_redis_client):
        """测试缓存未命中时查询数据库"""
        # Mock Redis 缓存未命中
        mock_redis_client.get.return_value = None

        # Mock 数据库查询结果
        mock_checkin = Mock()
        mock_checkin.checkin_date = "2026-01-30"
        mock_db.query.return_value.filter.return_value.scalar.return_value = 30
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            mock_checkin
        ]

        with patch("app.core.cache.redis_manager") as mock_redis_mgr:
            mock_redis_mgr.get_sync_client.return_value = mock_redis_client
            mock_redis_mgr.check_health.return_value = True

            # 调用函数
            result = CheckInService.get_checkin_stats(mock_db, "user123", days=30)

            # 验证数据库被查询
            assert mock_db.query.called

            # 验证返回的统计信息
            assert result.total_checkins == 30

            # 验证缓存被设置
            assert mock_redis_client.setex.called

            # 验证TTL为1800秒（30分钟）
            call_args = mock_redis_client.setex.call_args
            assert call_args[0][1] == 1800

    def test_get_checkin_status_uses_cache(self, mock_db, mock_redis_client):
        """测试获取签到状态使用缓存"""
        from app.schemas.checkin import CheckInStatusResponse

        # Mock Redis 缓存命中
        mock_redis_client.get.return_value = (
            '{"is_checked_in":true,"checkin_time":"2026-01-30T10:00:00"}'.encode(
                "utf-8"
            )
        )

        with patch("app.core.cache.redis_manager") as mock_redis_mgr:
            mock_redis_mgr.get_sync_client.return_value = mock_redis_client
            mock_redis_mgr.check_health.return_value = True

            # 第一次调用，应该从缓存获取
            result1 = CheckInService.get_checkin_status(mock_db, "user123")

            # 第二次调用，也应该从缓存获取
            result2 = CheckInService.get_checkin_status(mock_db, "user123")

            # 验证数据库没有被查询（全部从缓存获取）
            mock_db.query.assert_not_called()

            # 验证返回的是 dict 类型（缓存返回的JSON反序列化后）
            assert isinstance(result1, dict) or isinstance(
                result1, CheckInStatusResponse
            )
            if isinstance(result1, dict):
                assert result1["is_checked_in"] is True
            else:
                assert result1.is_checked_in is True

    def test_get_checkin_status_cache_miss(self, mock_db, mock_redis_client):
        """测试缓存未命中时查询数据库"""
        # Mock Redis 缓存未命中
        mock_redis_client.get.return_value = None

        with patch("app.core.cache.redis_manager") as mock_redis_mgr:
            mock_redis_mgr.get_sync_client.return_value = mock_redis_client
            mock_redis_mgr.check_health.return_value = True

            # Mock 数据库查询结果
            mock_checkin = Mock()
            mock_checkin.checkin_time = "2026-01-30T10:00:00"
            mock_db.query.return_value.filter.return_value.first.return_value = (
                mock_checkin
            )

            # 调用函数
            result = CheckInService.get_checkin_status(mock_db, "user123")

            # 验证数据库被查询
            assert mock_db.query.called

            # 验证缓存被设置
            assert mock_redis_client.setex.called

            # 验证TTL为600秒（10分钟）
            call_args = mock_redis_client.setex.call_args
            assert call_args[0][1] == 600

    def test_create_checkin_invalidates_cache(self, mock_db, mock_redis_client):
        """测试创建签到时失效缓存"""
        # Mock Redis 客户端 - 缓存失效时不返回数据
        mock_db.query.return_value.filter.return_value.first.return_value = (
            None  # 今天未签到
        )

        checkin_data = CheckInCreate(
            latitude="39.9042",
            longitude="116.4074",
            checkin_method="manual",
            notes="测试签到",
        )

        with patch("app.core.cache.redis_manager") as mock_redis_mgr:
            mock_redis_mgr.get_sync_client.return_value = mock_redis_client
            mock_redis_mgr.check_health.return_value = True

            # 创建签到
            CheckInService.create_checkin(mock_db, "user123", checkin_data)

            # 验证缓存被失效（delete 被调用）
            assert mock_redis_client.delete.called

            # 验证 delete 调用次数（3个通配符）
            assert mock_redis_client.delete.call_count == 3

    def test_redis_unavailable_fallback(self, mock_db):
        """测试 Redis 不可用时降级处理"""
        with patch("app.core.cache.redis_manager") as mock_redis_mgr:
            # Mock Redis 不可用
            mock_redis_mgr.get_sync_client.return_value = None

            # Mock 数据库查询
            mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = (
                []
            )

            # 调用函数，应该降级到数据库查询
            result = CheckInService.get_user_checkins(mock_db, "user123", days=7)

            # 验证数据库被查询
            assert mock_db.query.called

            # 验证返回结果
            assert result == []
