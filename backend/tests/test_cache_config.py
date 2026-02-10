"""缓存配置模块测试"""
import pytest
from app.core.cache_config import CacheConfig, cache_key, cache_pattern


class TestCacheConfig:
    """测试缓存配置类"""

    def test_ttl_constants_exist(self):
        """测试所有TTL常量存在且为正整数"""
        ttl_attrs = [
            'TTL_USER_INFO', 'TTL_USER_LIST',
            'TTL_DEVICE_INFO', 'TTL_DEVICE_STATUS',
            'TTL_CHECKIN_STATS', 'TTL_CHECKIN_LIST', 'TTL_CHECKIN_STREAK',
            'TTL_ALERT_SETTING', 'TTL_ALERT_LIST', 'TTL_ALERT_DETAIL', 'TTL_ALERT_STATS',
            'TTL_HEALTH_RECORD', 'TTL_HEALTH_SUMMARY',
            'TTL_EMERGENCY_CONTACT', 'TTL_EMERGENCY_CONTACTS_LIST',
            'TTL_NOTIFICATION_LIST', 'TTL_NOTIFICATION_PREFS',
            'TTL_ANOMALY_LIST', 'TTL_ANOMALY_STATS',
            'TTL_SOS_HISTORY',
            'TTL_LOCATION_HISTORY', 'TTL_LOCATION_LATEST',
            'TTL_EMERGENCY_CENTER', 'TTL_EMERGENCY_RESOURCE',
            'TTL_DEFAULT', 'TTL_SHORT', 'TTL_LONG'
        ]
        
        for attr in ttl_attrs:
            assert hasattr(CacheConfig, attr), f"Missing TTL constant: {attr}"
            value = getattr(CacheConfig, attr)
            assert isinstance(value, int), f"{attr} should be an integer"
            assert value > 0, f"{attr} should be positive"

    def test_prefix_constants_exist(self):
        """测试所有前缀常量存在且为非空字符串"""
        prefix_attrs = [
            'PREFIX_USER', 'PREFIX_USER_LIST',
            'PREFIX_DEVICE', 'PREFIX_DEVICE_STATUS',
            'PREFIX_CHECKIN', 'PREFIX_CHECKIN_STATS', 'PREFIX_CHECKIN_STREAK',
            'PREFIX_ALERT', 'PREFIX_ALERT_SETTING', 'PREFIX_ALERT_LIST', 
            'PREFIX_ALERT_DETAIL', 'PREFIX_ALERT_STATS',
            'PREFIX_HEALTH', 'PREFIX_HEALTH_RECORD', 'PREFIX_HEALTH_SUMMARY',
            'PREFIX_EMERGENCY', 'PREFIX_EMERGENCY_CONTACT', 'PREFIX_EMERGENCY_CONTACTS',
            'PREFIX_NOTIFICATION', 'PREFIX_NOTIFICATION_LIST', 'PREFIX_NOTIFICATION_PREFS',
            'PREFIX_ANOMALY', 'PREFIX_ANOMALY_LIST',
            'PREFIX_SOS', 'PREFIX_SOS_HISTORY',
            'PREFIX_LOCATION', 'PREFIX_LOCATION_LATEST',
            'PREFIX_EMERGENCY_CENTER', 'PREFIX_EMERGENCY_RESOURCE'
        ]
        
        for attr in prefix_attrs:
            assert hasattr(CacheConfig, attr), f"Missing prefix constant: {attr}"
            value = getattr(CacheConfig, attr)
            assert isinstance(value, str), f"{attr} should be a string"
            assert len(value) > 0, f"{attr} should not be empty"


class TestCacheKeyBuilder:
    """测试缓存键构建功能"""

    def test_make_key_with_single_part(self):
        """测试构建单个部分的键"""
        key = CacheConfig.make_key(CacheConfig.PREFIX_USER, "123")
        assert key == "user:123"

    def test_make_key_with_multiple_parts(self):
        """测试构建多个部分的键"""
        key = CacheConfig.make_key(CacheConfig.PREFIX_USER, "123", "info", "profile")
        assert key == "user:123:info:profile"

    def test_make_key_with_no_parts(self):
        """测试构建无额外部分的键"""
        key = CacheConfig.make_key(CacheConfig.PREFIX_USER)
        assert key == "user"

    def test_make_key_with_integer_parts(self):
        """测试构建包含整数部分的键"""
        key = CacheConfig.make_key(CacheConfig.PREFIX_ALERT, 123, "detail")
        assert key == "alert:123:detail"

    def test_make_pattern_with_wildcard(self):
        """测试构建通配符模式"""
        pattern = CacheConfig.make_pattern(CacheConfig.PREFIX_USER, "*")
        assert pattern == "user:*"

    def test_make_pattern_with_multiple_parts(self):
        """测试构建多部分通配符模式"""
        pattern = CacheConfig.make_pattern(CacheConfig.PREFIX_ALERT, "123", "*")
        assert pattern == "alert:123:*"

    def test_make_pattern_with_no_parts(self):
        """测试构建无额外部分的通配符模式"""
        pattern = CacheConfig.make_pattern(CacheConfig.PREFIX_USER)
        assert pattern == "user:*"


class TestCacheKeyShortcuts:
    """测试缓存键快捷函数"""

    def test_cache_key_function(self):
        """测试cache_key快捷函数"""
        key = cache_key("user", "123", "info")
        assert key == "user:123:info"

    def test_cache_pattern_function(self):
        """测试cache_pattern快捷函数"""
        pattern = cache_pattern("user", "*")
        assert pattern == "user:*"

    def test_cache_key_equivalent_to_make_key(self):
        """测试cache_key与make_key等价"""
        key1 = cache_key(CacheConfig.PREFIX_USER, "123", "info")
        key2 = CacheConfig.make_key(CacheConfig.PREFIX_USER, "123", "info")
        assert key1 == key2

    def test_cache_pattern_equivalent_to_make_pattern(self):
        """测试cache_pattern与make_pattern等价"""
        pattern1 = cache_pattern(CacheConfig.PREFIX_USER, "*")
        pattern2 = CacheConfig.make_pattern(CacheConfig.PREFIX_USER, "*")
        assert pattern1 == pattern2


class TestCacheConsistency:
    """测试缓存配置一致性"""

    def test_ttl_values_are_reasonable(self):
        """测试TTL值在合理范围内"""
        # 短缓存应该在1-5分钟
        assert 60 <= CacheConfig.TTL_SHORT <= 300
        # 默认缓存应该在5-10分钟
        assert 300 <= CacheConfig.TTL_DEFAULT <= 600
        # 长缓存应该在30-120分钟
        assert 1800 <= CacheConfig.TTL_LONG <= 7200

    def test_prefixes_use_colon_separator(self):
        """测试前缀使用冒号分隔符"""
        prefixes = [
            CacheConfig.PREFIX_USER,
            CacheConfig.PREFIX_DEVICE,
            CacheConfig.PREFIX_CHECKIN,
            CacheConfig.PREFIX_ALERT,
        ]
        
        for prefix in prefixes:
            assert ':' not in prefix, f"Base prefix should not contain colon: {prefix}"