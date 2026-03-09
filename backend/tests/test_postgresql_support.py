"""
测试PostgreSQL支持
"""

import pytest

# 检查psycopg2是否安装
try:
    pass

    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

from app.core.config import Settings
from app.core.database import get_engine


class TestPostgreSQLSupport:
    """测试PostgreSQL数据库支持"""

    def test_sqlite_database_url(self):
        """测试SQLite数据库URL"""
        # 生成有效的SECRET_KEY
        import base64
        import secrets

        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8")

        settings = Settings(DATABASE_URL="sqlite:///./test.db", SECRET_KEY=valid_key)

        # 验证数据库URL
        assert settings.DATABASE_URL == "sqlite:///./test.db"

    def test_postgresql_database_url(self):
        """测试PostgreSQL数据库URL"""
        # 生成有效的SECRET_KEY
        import base64
        import secrets

        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8")

        settings = Settings(
            DATABASE_URL="postgresql://user:password@localhost:5432/qilema",
            SECRET_KEY=valid_key,
        )

        # 验证数据库URL
        assert (
            settings.DATABASE_URL == "postgresql://user:password@localhost:5432/qilema"
        )

    def test_database_engine_recognizes_sqlite(self):
        """测试数据库引擎识别SQLite"""
        # 生成有效的SECRET_KEY
        import base64
        import secrets

        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8")

        settings = Settings(DATABASE_URL="sqlite:///./test.db", SECRET_KEY=valid_key)

        # 获取数据库引擎
        engine = get_engine(settings.DATABASE_URL)

        # 验证引擎类型
        assert engine.dialect.name == "sqlite"

    @pytest.mark.skipif(not POSTGRESQL_AVAILABLE, reason="psycopg2未安装")
    def test_database_engine_recognizes_postgresql(self):
        """测试数据库引擎识别PostgreSQL"""
        # 生成有效的SECRET_KEY
        import base64
        import secrets

        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8")

        # 注意：这个测试可能需要PostgreSQL连接，可能会失败
        # 这里我们只测试引擎创建，不测试实际连接
        settings = Settings(
            DATABASE_URL="postgresql://user:password@localhost:5432/qilema",
            SECRET_KEY=valid_key,
        )

        # 获取数据库引擎
        engine = get_engine(settings.DATABASE_URL)

        # 验证引擎类型（即使没有连接，引擎类型也应该正确）
        assert engine.dialect.name == "postgresql"

    @pytest.mark.skipif(not POSTGRESQL_AVAILABLE, reason="psycopg2未安装")
    def test_switch_between_sqlite_and_postgresql(self):
        """测试在SQLite和PostgreSQL之间切换"""
        # 生成有效的SECRET_KEY
        import base64
        import secrets

        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8")

        # SQLite
        settings_sqlite = Settings(
            DATABASE_URL="sqlite:///./test.db", SECRET_KEY=valid_key
        )
        engine_sqlite = get_engine(settings_sqlite.DATABASE_URL)
        assert engine_sqlite.dialect.name == "sqlite"

        # PostgreSQL
        settings_postgres = Settings(
            DATABASE_URL="postgresql://user:password@localhost:5432/qilema",
            SECRET_KEY=valid_key,
        )
        engine_postgres = get_engine(settings_postgres.DATABASE_URL)
        assert engine_postgres.dialect.name == "postgresql"

    def test_invalid_database_url_format(self):
        """测试无效的数据库URL格式"""
        # 生成有效的SECRET_KEY
        import base64
        import secrets

        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8")

        settings = Settings(DATABASE_URL="invalid://database", SECRET_KEY=valid_key)

        # 验证配置错误
        errors = settings.validate_configuration()
        assert len(errors) > 0
        assert any("DATABASE_URL格式无效" in error for error in errors)

    def test_environment_variable_database_url(self):
        """测试通过环境变量配置数据库URL"""
        import base64
        import os

        # 生成有效的SECRET_KEY
        import secrets

        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8")

        # 设置环境变量
        os.environ["DATABASE_URL"] = "postgresql://user:password@localhost:5432/qilema"

        try:
            settings = Settings(SECRET_KEY=valid_key)

            # 验证数据库URL
            assert (
                settings.DATABASE_URL
                == "postgresql://user:password@localhost:5432/qilema"
            )
        finally:
            del os.environ["DATABASE_URL"]
