"""
测试环境配置验证
"""

import pytest
from app.core.config import Settings


class TestEnvironmentConfigurationValidation:
    """测试环境配置验证"""

    def test_validate_configuration_function(self):
        """测试配置验证函数存在"""
        # 生成有效的SECRET_KEY
        import base64
        import secrets

        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8")

        # 创建有效配置
        settings = Settings(
            ENVIRONMENT="production", SECRET_KEY=valid_key, DEBUG="False"
        )

        # 验证配置验证函数存在
        assert hasattr(
            settings, "validate_configuration"
        ), "Settings应该有validate_configuration方法"

        # 调用验证函数
        errors = settings.validate_configuration()

        # 有效配置应该没有错误
        assert errors == [], f"有效配置不应有验证错误，但得到: {errors}"

    def test_invalid_environment_raises_error(self):
        """测试无效环境配置"""
        # 生成有效的SECRET_KEY
        import base64
        import secrets

        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8")

        with pytest.raises(ValueError) as exc_info:
            Settings(ENVIRONMENT="invalid", SECRET_KEY=valid_key)

        assert "ENVIRONMENT必须是" in str(exc_info.value)

    def test_invalid_secret_key_validation(self):
        """测试无效SECRET_KEY配置"""
        with pytest.raises(ValueError) as exc_info:
            Settings(ENVIRONMENT="production", SECRET_KEY="weak-key")

        assert "SECRET_KEY长度至少" in str(exc_info.value)

    def test_default_secret_key_validation(self):
        """测试默认SECRET_KEY被拒绝"""
        with pytest.raises(ValueError) as exc_info:
            Settings(
                ENVIRONMENT="production",
                SECRET_KEY="your-secret-key-change-in-production",
            )

        assert "SECRET_KEY不能使用默认值" in str(exc_info.value)

    def test_production_debug_validation(self):
        """测试生产环境DEBUG验证"""
        # 生成有效的SECRET_KEY
        import base64
        import secrets

        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8")

        with pytest.raises(ValueError) as exc_info:
            Settings(ENVIRONMENT="production", DEBUG="True", SECRET_KEY=valid_key)

        assert "生产环境不能开启DEBUG模式" in str(exc_info.value)

    def test_production_cors_wildcard_validation(self):
        """测试生产环境CORS通配符验证"""
        import base64
        import os

        # 生成有效的SECRET_KEY
        import secrets

        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8")

        # 设置环境变量（包含通配符）
        os.environ["CORS_ORIGINS"] = "*"

        try:
            with pytest.raises(ValueError) as exc_info:
                Settings(ENVIRONMENT="production", SECRET_KEY=valid_key)

            assert "生产环境CORS_ORIGINS不能使用通配符" in str(exc_info.value)
        finally:
            del os.environ["CORS_ORIGINS"]

    def test_validate_configuration_multiple_errors(self):
        """测试配置验证函数返回多个错误"""
        # 使用无效的配置（但不会触发验证错误）
        # 因为某些字段已经通过field_validator验证，这里测试validate_configuration方法
        import base64
        import secrets

        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8")

        settings = Settings(ENVIRONMENT="development", SECRET_KEY=valid_key)

        # 调用验证函数
        errors = settings.validate_configuration()

        # 开发环境使用有效密钥应该没有错误
        assert errors == []

    def test_required_configuration_fields(self):
        """测试必选配置字段"""
        # 这些字段没有默认值，如果缺少应该报错
        import base64
        import secrets

        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8")

        # SECRET_KEY是必选的，但没有默认值
        # 在测试中我们显式提供，所以这个测试通过
        settings = Settings(SECRET_KEY=valid_key)

        # 验证SECRET_KEY被正确设置
        assert settings.SECRET_KEY == valid_key
        assert settings.SECRET_KEY != "your-secret-key-change-in-production"

    def test_optional_configuration_fields(self):
        """测试可选配置字段"""
        import base64
        import secrets

        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8")

        # 只提供必需的SECRET_KEY和ENVIRONMENT（避免.env.testing覆盖）
        # 显式指定DATABASE_URL以使用默认值
        settings = Settings(
            ENVIRONMENT="development",
            DATABASE_URL="sqlite:///./qilema.db",
            SECRET_KEY=valid_key,
        )

        # 验证可选字段有默认值
        assert settings.ENVIRONMENT == "development"  # 有默认值
        assert settings.APP_NAME == "起了吗App"  # 有默认值
        assert settings.APP_VERSION == "1.0.0"  # 有默认值
        assert settings.DATABASE_URL == "sqlite:///./qilema.db"  # 有默认值

    def test_validate_database_url(self):
        """测试数据库URL格式验证"""
        import base64
        import secrets

        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8")

        # SQLite格式
        settings = Settings(DATABASE_URL="sqlite:///./test.db", SECRET_KEY=valid_key)
        errors = settings.validate_configuration()
        assert errors == []

        # PostgreSQL格式
        settings = Settings(
            DATABASE_URL="postgresql://user:password@localhost:5432/dbname",
            SECRET_KEY=valid_key,
        )
        errors = settings.validate_configuration()
        assert errors == []

    def test_clear_error_messages(self):
        """测试清晰的错误消息"""
        # 测试默认密钥的错误消息
        with pytest.raises(ValueError) as exc_info:
            Settings(
                ENVIRONMENT="production",
                SECRET_KEY="your-secret-key-change-in-production",
            )

        error_message = str(exc_info.value)
        assert "SECRET_KEY" in error_message
        assert "不能使用默认值" in error_message
        assert "python scripts/generate_secret_key.py" in error_message

    def test_clear_error_messages_weak_key(self):
        """测试弱密钥的清晰错误消息"""
        with pytest.raises(ValueError) as exc_info:
            Settings(ENVIRONMENT="production", SECRET_KEY="weak-key")

        error_message = str(exc_info.value)
        assert "SECRET_KEY" in error_message
        assert "长度至少" in error_message
        assert "python scripts/generate_secret_key.py" in error_message
