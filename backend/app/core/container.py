"""
依赖注入容器

使用 dependency-injector 管理应用的所有服务和资源
"""

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

    # 数据库provider（占位，将在US-ARCH-003中完善）
    # database = providers.Singleton(Database, db_url=config.database.url)

    # Redis provider（占位，将在US-ARCH-003中完善）
    # redis = providers.Singleton(Redis, url=config.redis.url)

    # 业务服务provider（占位，将在后续任务中添加）
    # user_service = providers.Factory(UserService, db=database)
    # checkin_service = providers.Factory(CheckInService, db=database)


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
