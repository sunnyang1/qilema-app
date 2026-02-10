"""
测试CORS配置优化
"""
import os
import pytest
from app.core.config import Settings


class TestCORSConfiguration:
    """测试CORS配置优化"""

    def test_default_cors_origins(self):
        """测试默认的CORS来源"""
        # 生成有效的SECRET_KEY
        import secrets
        import base64
        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode('utf-8')

        settings = Settings(
            SECRET_KEY=valid_key
        )

        # 验证默认CORS来源
        assert "http://localhost:3000" in settings.CORS_ORIGINS
        assert "http://localhost:8080" in settings.CORS_ORIGINS
        assert "http://localhost:5173" in settings.CORS_ORIGINS

    def test_cors_origins_from_env(self):
        """测试从环境变量配置CORS来源"""
        # 生成有效的SECRET_KEY
        import secrets
        import base64
        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode('utf-8')

        # 设置环境变量
        os.environ["CORS_ORIGINS"] = "https://example.com,https://api.example.com"

        try:
            settings = Settings(
                SECRET_KEY=valid_key
            )

            # 验证CORS来源
            assert "https://example.com" in settings.CORS_ORIGINS
            assert "https://api.example.com" in settings.CORS_ORIGINS
        finally:
            del os.environ["CORS_ORIGINS"]

    def test_cors_allow_methods_default(self):
        """测试默认的允许HTTP方法"""
        # 生成有效的SECRET_KEY
        import secrets
        import base64
        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode('utf-8')

        settings = Settings(
            SECRET_KEY=valid_key
        )

        # 验证默认允许的方法（不应包含通配符）
        assert "*" not in settings.CORS_ALLOW_METHODS
        assert "GET" in settings.CORS_ALLOW_METHODS
        assert "POST" in settings.CORS_ALLOW_METHODS

    def test_cors_allow_methods_from_env(self):
        """测试从环境变量配置允许的HTTP方法"""
        # 生成有效的SECRET_KEY
        import secrets
        import base64
        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode('utf-8')

        # 设置环境变量
        os.environ["CORS_ALLOW_METHODS"] = "GET,POST,PUT,DELETE"

        try:
            settings = Settings(
                SECRET_KEY=valid_key
            )

            # 验证允许的方法
            assert "GET" in settings.CORS_ALLOW_METHODS
            assert "POST" in settings.CORS_ALLOW_METHODS
            assert "PUT" in settings.CORS_ALLOW_METHODS
            assert "DELETE" in settings.CORS_ALLOW_METHODS
        finally:
            del os.environ["CORS_ALLOW_METHODS"]

    def test_cors_allow_headers_default(self):
        """测试默认的允许HTTP头部"""
        # 生成有效的SECRET_KEY
        import secrets
        import base64
        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode('utf-8')

        settings = Settings(
            SECRET_KEY=valid_key
        )

        # 验证默认允许的头部（不应包含通配符）
        assert "*" not in settings.CORS_ALLOW_HEADERS
        assert "Content-Type" in settings.CORS_ALLOW_HEADERS
        assert "Authorization" in settings.CORS_ALLOW_HEADERS

    def test_cors_allow_headers_from_env(self):
        """测试从环境变量配置允许的HTTP头部"""
        # 生成有效的SECRET_KEY
        import secrets
        import base64
        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode('utf-8')

        # 设置环境变量
        os.environ["CORS_ALLOW_HEADERS"] = "Content-Type,Authorization,X-Requested-With"

        try:
            settings = Settings(
                SECRET_KEY=valid_key
            )

            # 验证允许的头部
            assert "Content-Type" in settings.CORS_ALLOW_HEADERS
            assert "Authorization" in settings.CORS_ALLOW_HEADERS
            assert "X-Requested-With" in settings.CORS_ALLOW_HEADERS
        finally:
            del os.environ["CORS_ALLOW_HEADERS"]

    def test_production_cors_origins_validation(self):
        """测试生产环境CORS来源验证（拒绝通配符）"""
        # 生成有效的SECRET_KEY
        import secrets
        import base64
        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode('utf-8')

        # 设置环境变量（包含通配符）
        os.environ["CORS_ORIGINS"] = "*"

        with pytest.raises(ValueError) as exc_info:
            Settings(
                ENVIRONMENT="production",
                SECRET_KEY=valid_key
            )

        assert "生产环境CORS_ORIGINS不能使用通配符" in str(exc_info.value)
        del os.environ["CORS_ORIGINS"]

    def test_production_cors_allow_methods_validation(self):
        """测试生产环境允许的HTTP方法验证（拒绝通配符）"""
        # 生成有效的SECRET_KEY
        import secrets
        import base64
        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode('utf-8')

        # 设置环境变量（包含通配符）
        os.environ["CORS_ALLOW_METHODS"] = "*"

        with pytest.raises(ValueError) as exc_info:
            Settings(
                ENVIRONMENT="production",
                SECRET_KEY=valid_key
            )

        assert "生产环境CORS_ALLOW_METHODS不能使用通配符" in str(exc_info.value)
        del os.environ["CORS_ALLOW_METHODS"]

    def test_production_cors_allow_headers_validation(self):
        """测试生产环境允许的HTTP头部验证（拒绝通配符）"""
        # 生成有效的SECRET_KEY
        import secrets
        import base64
        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode('utf-8')

        # 设置环境变量（包含通配符）
        os.environ["CORS_ALLOW_HEADERS"] = "*"

        with pytest.raises(ValueError) as exc_info:
            Settings(
                ENVIRONMENT="production",
                SECRET_KEY=valid_key
            )

        assert "生产环境CORS_ALLOW_HEADERS不能使用通配符" in str(exc_info.value)
        del os.environ["CORS_ALLOW_HEADERS"]

    def test_development_can_use_wildcard_in_cors(self):
        """测试开发环境可以使用通配符"""
        # 生成有效的SECRET_KEY
        import secrets
        import base64
        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode('utf-8')

        # 设置环境变量
        os.environ["CORS_ORIGINS"] = "*"
        os.environ["CORS_ALLOW_METHODS"] = "*"
        os.environ["CORS_ALLOW_HEADERS"] = "*"

        try:
            settings = Settings(
                ENVIRONMENT="development",
                SECRET_KEY=valid_key
            )

            # 开发环境允许通配符
            assert "*" in settings.CORS_ORIGINS
            assert "*" in settings.CORS_ALLOW_METHODS
            assert "*" in settings.CORS_ALLOW_HEADERS
        finally:
            if "CORS_ORIGINS" in os.environ:
                del os.environ["CORS_ORIGINS"]
            if "CORS_ALLOW_METHODS" in os.environ:
                del os.environ["CORS_ALLOW_METHODS"]
            if "CORS_ALLOW_HEADERS" in os.environ:
                del os.environ["CORS_ALLOW_HEADERS"]
