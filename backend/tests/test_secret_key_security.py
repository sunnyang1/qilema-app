"""
测试SECRET_KEY安全性
"""

import os
from pathlib import Path

import pytest
from app.core.config import Settings, settings


class TestSecretKeySecurity:
    """测试SECRET_KEY安全性"""

    def test_secret_key_validation_rejects_default(self):
        """验证SECRET_KEY验证会拒绝默认值"""
        try:
            # 在生产环境下使用默认值应该失败
            Settings(
                ENVIRONMENT="production",
                SECRET_KEY="your-secret-key-change-in-production",
            )
            assert False, "应该抛出ValueError"
        except ValueError as e:
            assert "SECRET_KEY不能使用默认值" in str(e)

    def test_secret_key_validation_rejects_short_key(self):
        """验证SECRET_KEY验证会拒绝短密钥"""
        try:
            # 使用短密钥创建Settings应该失败
            Settings(ENVIRONMENT="development", SECRET_KEY="short-key")
            assert False, "应该抛出ValueError"
        except ValueError as e:
            assert "SECRET_KEY长度至少64字节" in str(e)

    def test_secret_key_validation_accepts_valid_key(self):
        """验证SECRET_KEY验证接受有效的强随机密钥"""
        # 生成一个有效的强随机密钥
        import base64
        import secrets

        valid_key = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8")

        # 应该成功创建Settings
        settings_obj = Settings(ENVIRONMENT="development", SECRET_KEY=valid_key)
        assert settings_obj.SECRET_KEY == valid_key

    def test_generate_secret_key_script_exists(self):
        """验证密钥生成脚本存在"""
        script_path = (
            Path(__file__).parent.parent / "scripts" / "generate_secret_key.py"
        )
        assert script_path.exists(), f"密钥生成脚本{script_path}必须存在"

    def test_generate_secret_key_script_works(self):
        """验证密钥生成脚本能生成有效密钥"""
        # 动态导入并运行脚本
        import sys

        # 添加scripts目录到路径
        scripts_dir = Path(__file__).parent.parent / "scripts"
        sys.path.insert(0, str(scripts_dir))

        # 导入密钥生成函数
        try:
            from generate_secret_key import generate_secret_key

            # 生成密钥
            secret_key = generate_secret_key()

            # 验证密钥长度
            assert len(secret_key.encode("utf-8")) >= 64, "生成的密钥长度至少64字节"

            # 验证可以通过Settings验证
            settings_obj = Settings(ENVIRONMENT="development", SECRET_KEY=secret_key)
            assert settings_obj.SECRET_KEY == secret_key

        finally:
            # 清理路径
            if str(scripts_dir) in sys.path:
                sys.path.remove(str(scripts_dir))
