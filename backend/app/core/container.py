"""
依赖注入容器

使用 dependency-injector 管理应用的所有服务和资源
"""

from app.core.database import get_engine
from app.core.redis import redis_manager
from dependency_injector import containers, providers


class Container(containers.DeclarativeContainer):
    """
    依赖注入容器

    管理应用的所有服务和资源，包括：
    - 配置（Configuration）
    - 数据库（Database）
    - Redis
    - 业务服务（UserService, CheckInService等）
    """

    # 配置provider - 支持从YAML文件或环境变量加载
    config = providers.Configuration()

    # 数据库provider - 使用Singleton确保整个应用只有一个引擎实例
    # 数据库连接参数：
    # - pool_size: 连接池大小
    # - max_overflow: 连接池溢出大小
    # - pool_recycle: 连接回收时间（秒），防止连接长时间使用后失效
    database = providers.Singleton(
        get_engine,
        database_url=config.database.url,
        echo=config.database.echo,
        pool_size=config.database.pool_size,
        max_overflow=config.database.max_overflow,
        pool_recycle=config.database.pool_recycle,
    )

    # Redis provider - 使用工厂函数返回单例实例
    # 注意：RedisManager自身已经是单例模式（通过__new__方法实现）
    def get_redis():
        """工厂函数，返回RedisManager单例实例"""
        return redis_manager

    redis = providers.Factory(get_redis)

    # 业务服务provider（Factory模式，每次获取新实例）
    # 注意：当前服务类主要使用类方法，这里提供工厂注册以便未来使用实例方法
    # 为避免循环导入，使用延迟导入
    def get_checkin_service():
        from app.services.checkin_service import CheckInService

        return CheckInService

    def get_user_service():
        from app.services.user_service import UserService

        return UserService

    def get_sos_service():
        from app.services.sos_service import SosService

        return SosService

    def get_emergency_contact_service():
        from app.services.emergency_contact_service import EmergencyContactService

        return EmergencyContactService

    def get_health_record_service():
        from app.services.health_record_service import HealthRecordService

        return HealthRecordService

    def get_notification_service():
        from app.services.notification_service import NotificationService

        return NotificationService

    def get_device_service():
        from app.services.device_service import DeviceService

        return DeviceService

    def get_alert_service():
        from app.services.alert_service import AlertService

        return AlertService

    checkin_service = providers.Factory(get_checkin_service)
    user_service = providers.Factory(get_user_service)
    sos_service = providers.Factory(get_sos_service)
    emergency_contact_service = providers.Factory(get_emergency_contact_service)
    health_record_service = providers.Factory(get_health_record_service)
    notification_service = providers.Factory(get_notification_service)
    device_service = providers.Factory(get_device_service)
    alert_service = providers.Factory(get_alert_service)


# 全局容器实例（延迟初始化）
_global_container: Container = None


def get_global_container() -> Container:
    """
    获取全局容器实例（单例模式）

    Returns:
        Container: 全局容器实例，如果不存在则创建
    """
    global _global_container
    if _global_container is None:
        _global_container = Container()
    return _global_container


def init_container(config_file: str = None) -> Container:
    """
    初始化容器并加载配置

    Args:
        config_file: 配置文件路径（YAML格式），可选

    Returns:
        Container: 初始化后的容器实例

    Example:
        >>> # 不加载配置文件
        >>> container = init_container()

        >>> # 从YAML文件加载配置
        >>> container = init_container("config.yaml")
    """
    global _global_container

    # 创建容器实例（如果不存在）
    if _global_container is None:
        _global_container = Container()

    # 如果提供了配置文件，从文件加载配置
    if config_file:
        _global_container.config.from_yaml(config_file)

    return _global_container


def reset_container():
    """
    重置全局容器实例（主要用于测试）

    Warning:
        这会清除当前容器实例，所有provider将被重新创建
    """
    global _global_container
    _global_container = None
