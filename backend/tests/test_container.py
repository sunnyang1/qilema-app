"""
依赖注入容器单元测试
"""

from unittest.mock import Mock, patch

import pytest
from app.core.container import (
    Container,
    get_global_container,
    init_container,
    reset_container,
)


class TestContainer:
    """Container类测试"""

    def setup_method(self):
        """每个测试前重置容器"""
        reset_container()

    def teardown_method(self):
        """每个测试后清理容器"""
        reset_container()

    def test_container_initialization(self):
        """测试容器初始化"""
        container_instance = Container()
        assert container_instance is not None
        assert hasattr(container_instance, "config")
        assert hasattr(container_instance.config, "providers")

    def test_config_provider_exists(self):
        """测试配置provider存在"""
        container_instance = Container()
        assert container_instance.config is not None
        # config 应该是Configuration类型的provider
        from dependency_injector.providers import Configuration

        assert isinstance(container_instance.config, Configuration)

    def test_get_global_container(self):
        """测试get_global_container函数"""
        container_instance = get_global_container()
        # 容器实例应该存在，不一定是Container类型（可能是DynamicContainer）
        assert container_instance is not None
        # 验证它有config属性
        assert hasattr(container_instance, "config")

    def test_global_container_singleton(self):
        """测试get_global_container返回单例"""
        container1 = get_global_container()
        container2 = get_global_container()
        assert container1 is container2

    def test_container_independent_instances(self):
        """测试独立容器实例"""
        container1 = Container()
        container2 = Container()
        # 两个实例应该不同
        assert container1 is not container2
        # 验证它们都是有效的容器对象
        assert hasattr(container1, "config")
        assert hasattr(container2, "config")

    def test_container_config_access(self):
        """测试容器配置访问"""
        container_instance = Container()
        # 可以访问config provider
        assert container_instance.config is not None

    def test_init_container_without_config(self):
        """测试不提供配置文件初始化容器"""
        reset_container()
        container_instance = init_container()
        assert container_instance is not None
        assert hasattr(container_instance, "config")

    def test_init_container_with_yaml_file(self, tmp_path):
        """测试从YAML文件初始化容器"""
        reset_container()
        # 创建临时配置文件
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(
            """
database:
  url: "postgresql://test:test@localhost/test"
redis:
  url: "redis://localhost:6379/0"
"""
        )

        container_instance = init_container(str(config_file))
        assert container_instance is not None
        assert hasattr(container_instance, "config")

    def test_init_container_singleton(self):
        """测试init_container也使用单例模式"""
        reset_container()
        container1 = init_container()
        container2 = init_container()
        assert container1 is container2

    def test_reset_container(self):
        """测试reset_container函数"""
        container1 = get_global_container()
        reset_container()
        container2 = get_global_container()
        assert container1 is not container2

    def test_container_attributes(self):
        """测试容器基本属性"""
        container_instance = Container()
        # 检查容器的基本属性
        assert hasattr(container_instance, "config")
        # 现在应该有database和redis provider
        assert hasattr(container_instance, "database")
        assert hasattr(container_instance, "redis")


class TestDatabaseProvider:
    """Database Provider测试"""

    def setup_method(self):
        """每个测试前重置容器"""
        reset_container()

    def teardown_method(self):
        """每个测试后清理容器"""
        reset_container()

    def test_database_provider_exists(self):
        """测试database provider存在"""
        container_instance = Container()
        assert hasattr(container_instance, "database")
        # database 应该是Singleton类型的provider
        from dependency_injector.providers import Singleton

        assert isinstance(container_instance.database, Singleton)

    def test_database_singleton(self):
        """测试database provider返回单例"""
        container_instance = Container()

        # 配置数据库参数
        container_instance.config.database.url.from_value("sqlite:///./test.db")
        container_instance.config.database.echo.from_value(False)
        container_instance.config.database.pool_size.from_value(5)
        container_instance.config.database.max_overflow.from_value(10)
        container_instance.config.database.pool_recycle.from_value(3600)

        # 获取两次database实例
        db1 = container_instance.database()
        db2 = container_instance.database()

        # 应该是同一个实例（Singleton）
        assert db1 is db2

    def test_database_with_different_config(self):
        """测试不同配置返回不同实例"""
        container1 = Container()
        container2 = Container()

        # Mock get_engine函数
        with patch("app.core.database.get_engine") as mock_get_engine:
            mock_engine1 = Mock()
            mock_engine2 = Mock()
            mock_get_engine.side_effect = [mock_engine1, mock_engine2]

            # 配置两个容器
            container1.config.database.url.from_value("sqlite:///./test1.db")
            container2.config.database.url.from_value("sqlite:///./test2.db")

            # 获取实例
            db1 = container1.database()
            db2 = container2.database()

            # 不同容器应该返回不同实例
            assert db1 is not db2


class TestRedisProvider:
    """Redis Provider测试"""

    def setup_method(self):
        """每个测试前重置容器"""
        reset_container()

    def teardown_method(self):
        """每个测试后清理容器"""
        reset_container()

    def test_redis_provider_exists(self):
        """测试redis provider存在"""
        container_instance = Container()
        assert hasattr(container_instance, "redis")
        # redis 应该是Factory类型的provider
        from dependency_injector.providers import Factory

        assert isinstance(container_instance.redis, Factory)

    def test_redis_singleton(self):
        """测试redis provider返回单例"""
        container_instance = Container()
        # 获取两次redis实例
        redis1 = container_instance.redis()
        redis2 = container_instance.redis()

        # 应该是同一个实例（RedisManager本身就是单例）
        assert redis1 is redis2

    def test_redis_manager_type(self):
        """测试返回的是RedisManager实例"""
        container_instance = Container()
        redis_manager = container_instance.redis()

        # 应该是RedisManager类型
        from app.core.redis import RedisManager

        assert isinstance(redis_manager, RedisManager)
