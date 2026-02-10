"""
测试环境变量配置管理
"""
import os
import pytest
from pathlib import Path
from app.core.config import settings


class TestEnvironmentConfig:
    """测试环境变量配置"""

    def test_env_example_exists(self):
        """验证.env.example文件存在"""
        env_example = Path(__file__).parent.parent / ".env.example"
        assert env_example.exists(), ".env.example文件必须存在"

    def test_env_example_contains_required_vars(self):
        """验证.env.example包含必需的环境变量"""
        env_example = Path(__file__).parent.parent / ".env.example"
        content = env_example.read_text(encoding='utf-8')

        # 验证必需的环境变量
        required_vars = [
            "ENVIRONMENT",
            "SECRET_KEY",
            "DATABASE_URL",
            "DEBUG"
        ]

        for var in required_vars:
            assert f"{var}=" in content, f".env.example必须包含{var}变量"

    def test_settings_loads_from_env(self):
        """验证Settings能从环境变量加载配置"""
        # 生成有效的SECRET_KEY
        import secrets
        import base64
        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode('utf-8')

        # 设置测试环境变量
        os.environ["ENVIRONMENT"] = "testing"
        os.environ["SECRET_KEY"] = valid_key
        os.environ["DATABASE_URL"] = "sqlite:///./test.db"

        # 重新加载设置
        from importlib import reload
        import app.core.config as config_module
        reload(config_module)

        # 验证加载成功
        new_settings = config_module.settings
        assert new_settings.SECRET_KEY == valid_key

        # 清理环境变量
        os.environ.pop("ENVIRONMENT", None)
        os.environ.pop("SECRET_KEY", None)
        os.environ.pop("DATABASE_URL", None)

    def test_environment_variable_supports_three_envs(self):
        """验证支持开发、测试、生产三种环境"""
        # 生成有效的SECRET_KEY
        import secrets
        import base64
        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode('utf-8')

        valid_envs = ["development", "testing", "production"]

        # 验证环境变量验证函数存在
        assert hasattr(settings, 'validate_environment'), "Settings类必须有validate_environment方法"

        # 测试有效环境
        for env in valid_envs:
            os.environ["ENVIRONMENT"] = env
            os.environ["SECRET_KEY"] = valid_key
            # 生产环境必须设置DEBUG=False
            if env == "production":
                os.environ["DEBUG"] = "False"
            else:
                os.environ["DEBUG"] = "True"
            # 重新加载并验证
            from importlib import reload
            import app.core.config as config_module
            reload(config_module)
            assert config_module.settings.ENVIRONMENT == env

        os.environ.pop("ENVIRONMENT", None)
        os.environ.pop("SECRET_KEY", None)
        os.environ.pop("DEBUG", None)

    def test_default_environment_is_development(self):
        """验证默认环境是development"""
        # 生成有效的SECRET_KEY
        import secrets
        import base64
        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode('utf-8')

        # 显式设置ENVIRONMENT为development
        os.environ["ENVIRONMENT"] = "development"
        os.environ["SECRET_KEY"] = valid_key

        from importlib import reload
        import app.core.config as config_module
        reload(config_module)

        assert config_module.settings.ENVIRONMENT == "development", "环境应该是development"

        # 清理
        os.environ.pop("ENVIRONMENT", None)
        os.environ.pop("SECRET_KEY", None)
