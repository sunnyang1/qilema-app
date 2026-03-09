"""
测试缓存预热功能
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from app.core.cache_warmer import CacheWarmer, warm_cache_on_startup


class TestCacheWarmer:
    """缓存预热测试"""

    @patch("app.core.cache_warmer.redis_manager")
    def test_warm_all_redis_unavailable(self, mock_redis_manager):
        """测试Redis不可用时跳过预热"""
        mock_redis_manager.check_health.return_value = False

        warmer = CacheWarmer()
        result = warmer.warm_all()

        assert result["success"] is False
        assert result["message"] == "Redis不可用"
        assert result["warmed_count"] == 0

    @patch("app.core.cache_warmer.redis_manager")
    def test_warm_all_success(self, mock_redis_manager):
        """测试缓存预热成功"""
        mock_redis_manager.check_health.return_value = True

        mock_db = Mock()

        warmer = CacheWarmer()

        with patch.object(warmer, "_warm_active_users", return_value=1) as mock_active:
            with patch.object(
                warmer, "_warm_alert_settings", return_value=2
            ) as mock_alert:
                with patch.object(
                    warmer, "_warm_emergency_contacts", return_value=3
                ) as mock_contact:
                    result = warmer.warm_all(mock_db)

        assert result["success"] is True
        assert "duration_ms" in result
        # 验证各个预热方法被调用
        mock_active.assert_called_once_with(mock_db)
        mock_alert.assert_called_once_with(mock_db)
        mock_contact.assert_called_once_with(mock_db)

    @patch("app.core.cache_warmer.redis_manager")
    def test_warm_active_users_empty(self, mock_redis_manager):
        """测试没有活跃用户时返回0"""
        mock_redis_manager.check_health.return_value = True

        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = (
            []
        )

        warmer = CacheWarmer()
        count = warmer._warm_active_users(mock_db)

        assert count == 0

    @patch("app.core.cache_warmer.redis_manager")
    def test_warm_alert_settings_empty(self, mock_redis_manager):
        """测试没有预警配置时返回0"""
        mock_redis_manager.check_health.return_value = True

        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = (
            []
        )

        warmer = CacheWarmer()
        count = warmer._warm_alert_settings(mock_db)

        assert count == 0

    @patch("app.core.cache_warmer.redis_manager")
    def test_warm_emergency_contacts_empty(self, mock_redis_manager):
        """测试没有紧急联系人时返回0"""
        mock_redis_manager.check_health.return_value = True

        mock_db = Mock()
        mock_db.query.return_value.distinct.return_value.limit.return_value.all.return_value = (
            []
        )

        warmer = CacheWarmer()
        count = warmer._warm_emergency_contacts(mock_db)

        assert count == 0

    @patch("app.core.cache_warmer.cache_warmer")
    def test_warm_cache_on_startup(self, mock_cache_warmer):
        """测试启动时预热缓存函数"""
        mock_cache_warmer.warm_all.return_value = {
            "success": True,
            "warmed_count": 10,
            "duration_ms": 100,
        }

        result = warm_cache_on_startup()

        assert result["success"] is True
        assert result["warmed_count"] == 10
        mock_cache_warmer.warm_all.assert_called_once()

    @patch("app.core.cache_warmer.redis_manager")
    def test_warm_all_with_exception(self, mock_redis_manager):
        """测试预热过程中出现异常时处理"""
        mock_redis_manager.check_health.return_value = True

        mock_db = Mock()

        warmer = CacheWarmer()

        with patch.object(warmer, "_warm_active_users", side_effect=Exception("测试异常")):
            result = warmer.warm_all(mock_db)

        assert result["success"] is False
        assert "测试异常" in result["message"]
        assert "warmed_count" in result
