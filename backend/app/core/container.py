"""
依赖注入容器

使用 dependency-injector 管理应用的所有服务和资源
"""

from app.core.database import get_db, get_engine
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

    # 数据库会话provider - 使用Factory模式，每次请求获取新会话
    # 注意：实际会话管理由 get_db() 处理，这里提供工厂以便DI使用
    db_session = providers.Factory(get_db)

    # Redis provider - 使用工厂函数返回单例实例
    # 注意：RedisManager自身已经是单例模式（通过__new__方法实现）
    def get_redis():
        """工厂函数，返回RedisManager单例实例"""
        return redis_manager

    redis = providers.Factory(get_redis)

    # ========== 业务服务providers ==========
    # 使用Factory模式，每次获取新实例，自动注入db_session
    # 为避免循环导入，使用延迟导入

    def _create_user_service(db):
        """创建用户服务实例"""
        from app.services.user_service import UserService

        return UserService(db)

    def _create_checkin_service(db):
        """创建签到服务实例"""
        from app.services.checkin_service import CheckInService

        return CheckInService(db)

    def _create_sos_service(db):
        """创建SOS服务实例"""
        from app.services.sos_service import SOSService

        return SOSService(db)

    def _create_emergency_contact_service(db):
        """创建紧急联系人服务实例"""
        from app.services.emergency_contact_service import EmergencyContactService

        return EmergencyContactService(db)

    def _create_health_record_service(db):
        """创建健康档案服务实例"""
        from app.services.health_record_service import HealthRecordService

        return HealthRecordService(db)

    def _create_device_service(db):
        """创建设备服务实例"""
        from app.services.device_service import DeviceService

        return DeviceService(db)

    def _create_alert_service(db):
        """创建预警服务实例"""
        from app.services.alert_service import AlertService

        return AlertService(db)

    def _create_medication_service(db):
        """创建用药服务实例"""
        from app.services.medication_service import MedicationService

        return MedicationService(db)

    def _create_anomaly_service(db):
        """创建异常检测服务实例"""
        from app.services.anomaly_service import AnomalyService

        return AnomalyService(db)

    def _create_aed_service(db):
        """创建AED服务实例"""
        from app.services.aed_service import AEDService

        return AEDService(db)

    def _create_emergency_center_service(db):
        """创建急救中心服务实例"""
        from app.services.emergency_center_service import EmergencyCenterService

        return EmergencyCenterService(db)

    def _create_knowledge_service(db):
        """创建知识库服务实例"""
        from app.services.knowledge_service import KnowledgeBaseService

        return KnowledgeBaseService(db)

    def _create_health_report_service(db):
        """创建健康报告服务实例"""
        from app.services.health_report_service import HealthReportService

        return HealthReportService(db)

    def _create_notification_service(db):
        """创建通知服务实例"""
        from app.services.notification import NotificationService

        return NotificationService(db)

    # 服务工厂providers - 自动注入数据库会话
    user_service = providers.Factory(_create_user_service, db=db_session)
    checkin_service = providers.Factory(_create_checkin_service, db=db_session)
    sos_service = providers.Factory(_create_sos_service, db=db_session)
    emergency_contact_service = providers.Factory(
        _create_emergency_contact_service, db=db_session
    )
    health_record_service = providers.Factory(
        _create_health_record_service, db=db_session
    )
    device_service = providers.Factory(_create_device_service, db=db_session)
    alert_service = providers.Factory(_create_alert_service, db=db_session)
    medication_service = providers.Factory(_create_medication_service, db=db_session)
    anomaly_service = providers.Factory(_create_anomaly_service, db=db_session)
    aed_service = providers.Factory(_create_aed_service, db=db_session)
    emergency_center_service = providers.Factory(
        _create_emergency_center_service, db=db_session
    )
    knowledge_service = providers.Factory(_create_knowledge_service, db=db_session)
    health_report_service = providers.Factory(
        _create_health_report_service, db=db_session
    )
    notification_service = providers.Factory(
        _create_notification_service, db=db_session
    )


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


# ========== 便捷的依赖注入函数 ==========


def get_container() -> Container:
    """
    获取容器实例的便捷函数

    Returns:
        Container: 容器实例
    """
    return get_global_container()
