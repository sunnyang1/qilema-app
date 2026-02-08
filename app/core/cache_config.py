"""
统一缓存配置模块

定义全系统缓存策略的TTL和键前缀规范
"""


class CacheConfig:
    """缓存配置类
    
    包含所有缓存的TTL（生存时间）和键前缀常量
    所有服务应使用此配置以保持一致性
    """
    
    # ==================== TTL配置（秒）====================
    
    # 用户相关
    TTL_USER_INFO = 300                    # 用户信息：5分钟
    TTL_USER_LIST = 60                     # 用户列表：1分钟
    
    # 设备相关
    TTL_DEVICE_INFO = 300                  # 设备信息：5分钟
    TTL_DEVICE_STATUS = 60                 # 设备状态：1分钟
    
    # 签到相关
    TTL_CHECKIN_STATS = 1800               # 签到统计：30分钟
    TTL_CHECKIN_LIST = 300                 # 签到列表：5分钟
    TTL_CHECKIN_STREAK = 600               # 连续签到：10分钟
    
    # 预警相关
    TTL_ALERT_SETTING = 1800               # 预警配置：30分钟
    TTL_ALERT_LIST = 300                   # 预警列表：5分钟
    TTL_ALERT_DETAIL = 600                 # 预警详情：10分钟
    TTL_ALERT_STATS = 300                  # 预警统计：5分钟
    
    # 健康档案相关
    TTL_HEALTH_RECORD = 600                # 健康档案：10分钟
    TTL_HEALTH_SUMMARY = 300               # 健康摘要：5分钟
    
    # 紧急联系人相关
    TTL_EMERGENCY_CONTACT = 600            # 单个联系人：10分钟
    TTL_EMERGENCY_CONTACTS_LIST = 600      # 联系人列表：10分钟
    
    # 通知相关
    TTL_NOTIFICATION_LIST = 300            # 通知列表：5分钟
    TTL_NOTIFICATION_PREFS = 1800          # 通知偏好：30分钟
    
    # 异常检测相关
    TTL_ANOMALY_LIST = 300                 # 异常列表：5分钟
    TTL_ANOMALY_STATS = 600                # 异常统计：10分钟
    
    # SOS相关
    TTL_SOS_HISTORY = 300                  # SOS历史：5分钟
    
    # 位置相关
    TTL_LOCATION_HISTORY = 300             # 位置历史：5分钟
    TTL_LOCATION_LATEST = 60               # 最新位置：1分钟
    
    # 紧急中心和资源
    TTL_EMERGENCY_CENTER = 1800            # 紧急中心：30分钟
    TTL_EMERGENCY_RESOURCE = 1800          # 紧急资源：30分钟
    
    # 默认TTL
    TTL_DEFAULT = 300                      # 默认：5分钟
    TTL_SHORT = 60                         # 短缓存：1分钟
    TTL_LONG = 3600                        # 长缓存：1小时
    
    # ==================== 缓存键前缀配置 ====================
    
    # 用户
    PREFIX_USER = "user"
    PREFIX_USER_LIST = "user:list"
    
    # 设备
    PREFIX_DEVICE = "device"
    PREFIX_DEVICE_STATUS = "device:status"
    
    # 签到
    PREFIX_CHECKIN = "checkin"
    PREFIX_CHECKIN_LIST = "checkin:list"
    PREFIX_CHECKIN_STATS = "checkin:stats"
    PREFIX_CHECKIN_STREAK = "checkin:streak"
    
    # 预警
    PREFIX_ALERT = "alert"
    PREFIX_ALERT_SETTING = "alert:setting"
    PREFIX_ALERT_LIST = "alert:list"
    PREFIX_ALERT_DETAIL = "alert:detail"
    PREFIX_ALERT_STATS = "alert:stats"
    
    # 健康档案
    PREFIX_HEALTH = "health"
    PREFIX_HEALTH_RECORD = "health:record"
    PREFIX_HEALTH_SUMMARY = "health:summary"
    
    # 紧急联系人
    PREFIX_EMERGENCY = "emergency"
    PREFIX_EMERGENCY_CONTACT = "emergency:contact"
    PREFIX_EMERGENCY_CONTACTS = "emergency:contacts"
    
    # 通知
    PREFIX_NOTIFICATION = "notification"
    PREFIX_NOTIFICATION_LIST = "notification:list"
    PREFIX_NOTIFICATION_PREFS = "notification:prefs"
    
    # 异常
    PREFIX_ANOMALY = "anomaly"
    PREFIX_ANOMALY_LIST = "anomaly:list"
    
    # SOS
    PREFIX_SOS = "sos"
    PREFIX_SOS_HISTORY = "sos:history"
    
    # 位置
    PREFIX_LOCATION = "location"
    PREFIX_LOCATION_LATEST = "location:latest"
    
    # 紧急中心和资源
    PREFIX_EMERGENCY_CENTER = "emergency:center"
    PREFIX_EMERGENCY_RESOURCE = "emergency:resource"
    
    # ==================== 辅助方法 ====================
    
    @staticmethod
    def make_key(prefix: str, *parts) -> str:
        """构建缓存键
        
        Args:
            prefix: 键前缀
            *parts: 键的组成部分
            
        Returns:
            完整的缓存键，格式：prefix:part1:part2:...
            
        Example:
            >>> CacheConfig.make_key(CacheConfig.PREFIX_USER, "123", "info")
            'user:123:info'
        """
        if parts:
            return f"{prefix}:{':'.join(str(p) for p in parts)}"
        return prefix
    
    @staticmethod
    def make_pattern(prefix: str, *parts) -> str:
        """构建缓存键匹配模式（用于批量失效）
        
        Args:
            prefix: 键前缀
            *parts: 键的组成部分（可使用 * 作为通配符）
            
        Returns:
            缓存键匹配模式
            
        Example:
            >>> CacheConfig.make_pattern(CacheConfig.PREFIX_USER, "*")
            'user:*'
        """
        if parts:
            return f"{prefix}:{':'.join(str(p) for p in parts)}"
        return f"{prefix}:*"


# 为了向后兼容，提供简化的缓存键构建函数
def cache_key(prefix: str, *parts) -> str:
    """构建缓存键的快捷函数
    
    Args:
        prefix: 键前缀
        *parts: 键的组成部分
        
    Returns:
        完整的缓存键
        
    Example:
        >>> cache_key("user", "123", "info")
        'user:123:info'
    """
    return CacheConfig.make_key(prefix, *parts)


def cache_pattern(prefix: str, *parts) -> str:
    """构建缓存键匹配模式的快捷函数
    
    Args:
        prefix: 键前缀
        *parts: 键的组成部分（可使用 * 作为通配符）
        
    Returns:
        缓存键匹配模式
        
    Example:
        >>> cache_pattern("user", "*")
        'user:*'
    """
    return CacheConfig.make_pattern(prefix, *parts)