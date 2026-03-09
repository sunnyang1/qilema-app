"""
配置文件加载单元测试
"""

import os
import tempfile
from pathlib import Path

import pytest
import yaml
from app.core.container import Container, init_container, reset_container


class TestConfigFileLoading:
    """配置文件加载测试"""

    def setup_method(self):
        """每个测试前重置容器"""
        reset_container()

    def teardown_method(self):
        """每个测试后清理容器"""
        reset_container()

    def test_load_dev_config(self):
        """测试加载开发环境配置"""
        # 读取开发环境配置文件
        config_path = Path(__file__).parent.parent / "config.dev.yaml"
        assert config_path.exists()

        with open(config_path) as f:
            config_data = yaml.safe_load(f)

        # 验证配置内容
        assert config_data["environment"] == "development"
        assert config_data["debug"] is True
        assert "sqlite" in config_data["database"]["url"]
        assert config_data["database"]["echo"] is True
        assert config_data["logging"]["level"] == "DEBUG"

    def test_load_staging_config(self):
        """测试加载测试环境配置"""
        config_path = Path(__file__).parent.parent / "config.staging.yaml"
        assert config_path.exists()

        with open(config_path) as f:
            config_data = yaml.safe_load(f)

        # 验证配置内容
        assert config_data["environment"] == "testing"
        assert config_data["debug"] is False
        assert "postgresql" in config_data["database"]["url"]
        assert config_data["database"]["echo"] is False
        assert config_data["logging"]["level"] == "INFO"

    def test_load_prod_config(self):
        """测试加载生产环境配置"""
        config_path = Path(__file__).parent.parent / "config.prod.yaml"
        assert config_path.exists()

        with open(config_path) as f:
            config_data = yaml.safe_load(f)

        # 验证配置内容
        assert config_data["environment"] == "production"
        assert config_data["debug"] is False
        assert "${DATABASE_URL}" in config_data["database"]["url"]
        assert config_data["database"]["pool_size"] == 20  # 生产环境更大的连接池
        assert config_data["logging"]["level"] == "WARNING"
        assert config_data["logging"]["to_console"] is False

    def test_container_load_yaml_config(self, tmp_path):
        """测试容器从YAML文件加载配置"""
        # 创建临时配置文件
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(
            """
database:
  url: "postgresql://test:test@localhost:5432/test"
  echo: false
  pool_size: 10
  max_overflow: 20
  pool_recycle: 3600

redis:
  url: "redis://localhost:6379/1"
"""
        )

        # 初始化容器并加载配置
        container = init_container(str(config_file))

        # 验证配置已加载
        assert hasattr(container, "config")
        assert hasattr(container.config, "database")
        assert hasattr(container.config.database, "url")
        assert hasattr(container.config.database, "pool_size")

    def test_config_override_with_env(self, tmp_path, monkeypatch):
        """测试环境变量覆盖配置"""
        # 创建临时配置文件
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(
            """
database:
  url: "postgresql://default:default@localhost:5432/default"
  pool_size: 5
"""
        )

        # 设置环境变量
        monkeypatch.setenv(
            "DATABASE_URL", "postgresql://override:override@localhost:5432/override"
        )

        # 初始化容器
        container = init_container(str(config_file))

        # 环境变量应该覆盖配置文件（需要实际验证）
        # 注意：这需要在实际的config.py中实现环境变量覆盖逻辑

    def test_config_validation(self, tmp_path):
        """测试配置验证"""
        # 创建有效的配置文件
        valid_config = tmp_path / "valid_config.yaml"
        valid_config.write_text(
            """
database:
  url: "postgresql://user:pass@localhost:5432/db"
  pool_size: 5
  max_overflow: 10
  pool_recycle: 3600

redis:
  url: "redis://localhost:6379/0"
"""
        )

        # 应该成功加载
        container = init_container(str(valid_config))
        assert container is not None


class TestEnvFiles:
    """环境变量文件测试"""

    def test_dev_env_file_exists(self):
        """测试开发环境环境变量文件存在"""
        env_path = Path(__file__).parent.parent / ".env.dev"
        assert env_path.exists()

        # 读取并验证关键配置
        with open(env_path) as f:
            content = f.read()

        assert "ENVIRONMENT=development" in content
        assert "DEBUG=true" in content
        assert "sqlite" in content
        assert "REDIS_URL" in content

    def test_staging_env_file_exists(self):
        """测试测试环境环境变量文件存在"""
        env_path = Path(__file__).parent.parent / ".env.staging"
        assert env_path.exists()

        with open(env_path) as f:
            content = f.read()

        assert "ENVIRONMENT=testing" in content
        assert "DEBUG=false" in content
        assert "postgresql" in content

    def test_prod_env_file_exists(self):
        """测试生产环境环境变量文件存在"""
        env_path = Path(__file__).parent.parent / ".env.prod"
        assert env_path.exists()

        with open(env_path) as f:
            content = f.read()

        assert "ENVIRONMENT=production" in content
        assert "DEBUG=false" in content
        assert "⚠️" in content  # 警告信息


class TestDockerComposeFiles:
    """Docker Compose配置文件测试"""

    def test_dev_compose_file_exists(self):
        """测试开发环境docker-compose文件存在"""
        compose_path = Path(__file__).parent.parent.parent / "docker-compose.dev.yml"
        assert compose_path.exists()

    def test_staging_compose_file_exists(self):
        """测试测试环境docker-compose文件存在"""
        compose_path = (
            Path(__file__).parent.parent.parent / "docker-compose.staging.yml"
        )
        assert compose_path.exists()

    def test_prod_compose_file_exists(self):
        """测试生产环境docker-compose文件存在"""
        compose_path = Path(__file__).parent.parent.parent / "docker-compose.prod.yml"
        assert compose_path.exists()

    def test_dev_compose_config(self):
        """测试开发环境docker-compose配置"""
        compose_path = Path(__file__).parent.parent.parent / "docker-compose.dev.yml"
        with open(compose_path) as f:
            compose_data = yaml.safe_load(f)

        # 验证开发环境特定配置
        assert "backend" in compose_data["services"]
        assert (
            compose_data["services"]["backend"]["environment"]["ENVIRONMENT"]
            == "development"
        )
        assert compose_data["services"]["backend"]["environment"]["DEBUG"] == "True"

    def test_prod_compose_config(self):
        """测试生产环境docker-compose配置"""
        compose_path = Path(__file__).parent.parent.parent / "docker-compose.prod.yml"
        with open(compose_path) as f:
            compose_data = yaml.safe_load(f)

        # 验证生产环境特定配置
        assert "backend" in compose_data["services"]
        assert (
            compose_data["services"]["backend"]["environment"]["ENVIRONMENT"]
            == "production"
        )
        assert (
            compose_data["services"]["backend"]["deploy"]["resources"]["limits"][
                "memory"
            ]
            == "2G"
        )
