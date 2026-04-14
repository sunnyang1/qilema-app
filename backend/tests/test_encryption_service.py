"""加密服务测试"""

import os
from unittest.mock import patch

import pytest
from cryptography.fernet import Fernet

from app.services.health_record_service import EncryptionService


class TestEncryptionService:
    """加密服务测试类"""

    def test_init_without_encryption_key_raises_error(self):
        """测试当ENCRYPTION_KEY未设置时抛出ValueError"""
        # Given: 环境变量未设置
        with patch.dict(os.environ, {}, clear=True):
            # When/Then: 应该抛出ValueError
            with pytest.raises(ValueError) as exc_info:
                EncryptionService()

            error_msg = str(exc_info.value)
            assert "ENCRYPTION_KEY environment variable is not set" in error_msg
            assert "generate a key" in error_msg
            assert "export ENCRYPTION_KEY" in error_msg

    def test_init_with_valid_key_succeeds(self):
        """测试使用有效密钥初始化成功"""
        # Given: 有效的加密密钥
        valid_key = Fernet.generate_key().decode()

        with patch.dict(os.environ, {"ENCRYPTION_KEY": valid_key}):
            # When
            service = EncryptionService()

            # Then: 应该成功创建
            assert service is not None
            assert service.cipher is not None

    def test_init_with_invalid_key_raises_error(self):
        """测试使用无效密钥时抛出ValueError"""
        # Given: 无效的加密密钥
        invalid_key = "invalid-key"

        with patch.dict(os.environ, {"ENCRYPTION_KEY": invalid_key}):
            # When/Then: 应该抛出ValueError
            with pytest.raises(ValueError) as exc_info:
                EncryptionService()

            assert "Invalid ENCRYPTION_KEY" in str(exc_info.value)

    def test_encrypt_decrypt_roundtrip(self):
        """测试加密解密往返正确"""
        # Given: 有效的密钥和明文
        valid_key = Fernet.generate_key().decode()
        plaintext = "敏感信息测试"

        with patch.dict(os.environ, {"ENCRYPTION_KEY": valid_key}):
            service = EncryptionService()

            # When: 加密
            encrypted = service.encrypt(plaintext)

            # Then: 密文应该与明文不同
            assert encrypted != plaintext

            # When: 解密
            decrypted = service.decrypt(encrypted)

            # Then: 应该恢复原文
            assert decrypted == plaintext

    def test_encrypt_empty_string_returns_empty(self):
        """测试加密空字符串返回空字符串"""
        valid_key = Fernet.generate_key().decode()

        with patch.dict(os.environ, {"ENCRYPTION_KEY": valid_key}):
            service = EncryptionService()

            # When/Then
            assert service.encrypt("") == ""
            assert service.encrypt(None) is None

    def test_decrypt_empty_string_returns_empty(self):
        """测试解密空字符串返回空字符串"""
        valid_key = Fernet.generate_key().decode()

        with patch.dict(os.environ, {"ENCRYPTION_KEY": valid_key}):
            service = EncryptionService()

            # When/Then
            assert service.decrypt("") == ""
            assert service.decrypt(None) is None
