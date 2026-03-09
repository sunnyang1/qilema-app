"""
测试DEBUG模式根据环境配置
"""

import os

import pytest
from app.core.config import Settings


class TestDebugEnvironmentConfiguration:
    """测试DEBUG模式根据环境配置"""

    def test_production_auto_debug_false(self):
        """生产环境自动设置DEBUG为False（显式设置为False）"""
        # 生成有效的SECRET_KEY
        import base64
        import secrets

        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8")

        # 显式设置DEBUG为False，生产环境应保持为False
        settings = Settings(
            ENVIRONMENT="production", DEBUG="False", SECRET_KEY=valid_key
        )

        # 验证DEBUG为False
        assert settings.DEBUG is False, "生产环境DEBUG应该为False"

    def test_development_auto_debug_true(self):
        """开发环境自动设置DEBUG为True（未显式设置时）"""
        # 生成有效的SECRET_KEY
        import base64
        import secrets

        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8")

        # 不设置DEBUG，依赖自动配置
        settings = Settings(ENVIRONMENT="development", SECRET_KEY=valid_key)

        # 验证DEBUG为True
        assert settings.DEBUG is True, "开发环境DEBUG默认应该为True"

    def test_testing_auto_debug_true(self):
        """测试环境自动设置DEBUG为True（未显式设置时）"""
        # 生成有效的SECRET_KEY
        import base64
        import secrets

        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8")

        # 不设置DEBUG，依赖自动配置
        settings = Settings(ENVIRONMENT="testing", SECRET_KEY=valid_key)

        # 验证DEBUG为True
        assert settings.DEBUG is True, "测试环境DEBUG默认应该为True"

    def test_production_debug_validation_raises_error(self):
        """生产环境尝试显式开启DEBUG会抛出验证错误"""
        # 生成有效的SECRET_KEY
        import base64
        import secrets

        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8")

        with pytest.raises(ValueError) as exc_info:
            Settings(ENVIRONMENT="production", DEBUG="True", SECRET_KEY=valid_key)

        assert "生产环境不能开启DEBUG模式" in str(exc_info.value)

    def test_development_can_explicitly_disable_debug(self):
        """开发环境可以显式关闭DEBUG"""
        # 生成有效的SECRET_KEY
        import base64
        import secrets

        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8")

        # 显式设置DEBUG为False
        settings = Settings(
            ENVIRONMENT="development", DEBUG="False", SECRET_KEY=valid_key
        )

        # 验证DEBUG为False
        assert settings.DEBUG is False, "开发环境可以显式关闭DEBUG"

    def test_development_can_explicitly_enable_debug(self):
        """开发环境可以显式开启DEBUG"""
        # 生成有效的SECRET_KEY
        import base64
        import secrets

        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8")

        # 显式设置DEBUG为True
        settings = Settings(
            ENVIRONMENT="development", DEBUG="True", SECRET_KEY=valid_key
        )

        # 验证DEBUG为True
        assert settings.DEBUG is True, "开发环境可以显式开启DEBUG"
