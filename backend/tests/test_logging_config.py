"""
测试结构化日志配置
"""

import json
import logging
import os
import sys
from io import StringIO

import pytest

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.logging_config import (
    SENSITIVE_FIELDS,
    ContextFilter,
    JSONFormatter,
    get_logger,
    setup_logging,
)


class TestJSONFormatter:
    """测试 JSON 格式化器"""

    def test_formatter_creates_valid_json(self):
        """测试格式化器输出有效的 JSON"""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        data = json.loads(output)
        assert data["level"] == "INFO"
        assert data["message"] == "Test message"
        assert "timestamp" in data

    def test_formatter_includes_request_id(self):
        """测试格式化器包含请求 ID"""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.request_id = "abc123"
        output = formatter.format(record)
        data = json.loads(output)
        assert data["request_id"] == "abc123"

    def test_formatter_sanitizes_sensitive_fields(self):
        """测试敏感字段脱敏"""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.extra_fields = {
            "username": "test",
            "password": "secret123",
            "api_key": "sk-1234567890abcdef",
        }
        output = formatter.format(record)
        data = json.loads(output)
        assert data["extra"]["password"] == "se*****23"
        assert data["extra"]["api_key"] == "sk***************ef"
        assert data["extra"]["username"] == "test"

    def test_formatter_masks_short_values(self):
        """测试脱敏短值"""
        formatter = JSONFormatter()
        assert formatter._mask_value("abc") == "****"
        assert formatter._mask_value("ab") == "****"
        assert formatter._mask_value("") == "****"

    def test_formatter_masks_none_values(self):
        """测试脱敏 None 值"""
        formatter = JSONFormatter()
        assert formatter._mask_value(None) == "null"

    def test_formatter_includes_exception(self):
        """测试包含异常信息"""
        formatter = JSONFormatter()
        try:
            1 / 0
        except Exception as e:
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=1,
                msg="Test error",
                args=(),
                exc_info=sys.exc_info(),
            )
            output = formatter.format(record)
            data = json.loads(output)
            assert "exception" in data
            assert data["exception"]["type"] == "ZeroDivisionError"


class TestContextFilter:
    """测试上下文过滤器"""

    def test_filter_passes(self):
        """测试过滤器总是通过"""
        filter_obj = ContextFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        assert filter_obj.filter(record) is True


class TestSetupLogging:
    """测试日志配置"""

    def test_setup_logging_console(self):
        """测试控制台日志配置"""
        logger = setup_logging(log_level="INFO", log_to_console=True)
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0
        # 清理处理器
        logger.handlers.clear()

    def test_setup_logging_file(self, tmp_path):
        """测试文件日志配置"""
        log_file = tmp_path / "test.log"
        logger = setup_logging(
            log_level="DEBUG", log_file=str(log_file), log_to_console=False
        )
        assert logger.level == logging.DEBUG

        # 记录一条日志
        test_logger = get_logger("test")
        test_logger.info("Test message")

        # 验证文件存在
        assert log_file.exists()

        # 验证文件内容是 JSON
        with open(log_file, "r") as f:
            content = f.read()
            data = json.loads(content)
            assert data["message"] == "Test message"

        # 清理
        logger.handlers.clear()


class TestGetLogger:
    """测试获取日志记录器"""

    def test_get_logger_returns_logger(self):
        """测试返回日志记录器实例"""
        logger = get_logger("test")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test"

    def test_get_logger_same_instance(self):
        """测试相同名称返回相同实例"""
        logger1 = get_logger("test")
        logger2 = get_logger("test")
        assert logger1 is logger2


class TestSensitiveFields:
    """测试敏感字段配置"""

    def test_sensitive_fields_set(self):
        """测试敏感字段集合存在"""
        assert "password" in SENSITIVE_FIELDS
        assert "token" in SENSITIVE_FIELDS
        assert "secret" in SENSITIVE_FIELDS
        assert "api_key" in SENSITIVE_FIELDS
        assert "authorization" in SENSITIVE_FIELDS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
