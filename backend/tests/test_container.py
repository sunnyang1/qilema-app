"""
依赖注入容器单元测试
"""

import pytest
from app.core.container import Container, get_global_container, init_container, reset_container


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
        assert hasattr(container_instance, 'config')
        assert hasattr(container_instance.config, 'providers')

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
        assert hasattr(container_instance, 'config')

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
        assert hasattr(container1, 'config')
        assert hasattr(container2, 'config')

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
        assert hasattr(container_instance, 'config')

    def test_init_container_with_yaml_file(self, tmp_path):
        """测试从YAML文件初始化容器"""
        reset_container()
        # 创建临时配置文件
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
database:
  url: "postgresql://test:test@localhost/test"
redis:
  url: "redis://localhost:6379/0"
""")

        container_instance = init_container(str(config_file))
        assert container_instance is not None
        assert hasattr(container_instance, 'config')

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
        assert hasattr(container_instance, 'config')
        # 未来添加的provider也应该能访问
        # assert hasattr(container_instance, 'database')
        # assert hasattr(container_instance, 'redis')
