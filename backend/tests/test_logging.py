"""
统一日志系统测试

测试日志配置、格式、请求ID追踪等功能
"""

import logging
import tempfile
from pathlib import Path

from app.core.config import RequestIDFilter, Settings, get_logger, setup_logging


class TestRequestIDFilter:
    """请求ID过滤器测试"""

    def test_filter_with_request_id(self):
        """测试带有请求ID的过滤"""
        log_filter = RequestIDFilter()

        # 创建日志记录
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test message",
            args=(),
            exc_info=None,
        )

        # 设置request_id
        record.request_id = "test-request-123"

        # 过滤
        result = log_filter.filter(record)

        # 验证
        assert result is True
        assert record.request_id == "test-request-123"

    def test_filter_without_request_id(self):
        """测试没有请求ID的过滤"""
        log_filter = RequestIDFilter()

        # 创建日志记录
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test message",
            args=(),
            exc_info=None,
        )

        # 不过滤
        result = log_filter.filter(record)

        # 验证
        assert result is True
        assert record.request_id == "N/A"

    def test_filter_with_user_id(self):
        """测试带有用户ID的过滤"""
        log_filter = RequestIDFilter()

        # 创建日志记录
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test message",
            args=(),
            exc_info=None,
        )

        # 设置user_id
        record.user_id = "user-456"

        # 过滤
        result = log_filter.filter(record)

        # 验证
        assert result is True
        assert record.user_id == "user-456"


class TestSetupLogging:
    """日志系统配置测试"""

    def test_setup_logging_with_default_settings(self):
        """测试使用默认配置设置日志"""
        setup_logging()

        # 验证根日志记录器
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO  # 默认INFO级别

        # 验证有处理器
        assert len(root_logger.handlers) > 0

    def test_setup_logging_with_custom_settings(self):
        """测试使用自定义配置设置日志"""
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_settings = Settings(
                LOG_LEVEL="DEBUG",
                LOG_TO_CONSOLE=False,
                LOG_TO_FILE=True,
                LOG_DIR=temp_dir,
            )

            setup_logging(custom_settings)

            # 验证日志级别
            root_logger = logging.getLogger()
            assert root_logger.level == logging.DEBUG

    def test_log_file_creation(self):
        """测试日志文件创建"""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_settings = Settings(
                LOG_LEVEL="INFO",
                LOG_TO_CONSOLE=False,
                LOG_TO_FILE=True,
                LOG_DIR=temp_dir,
            )

            setup_logging(custom_settings)

            # 验证日志文件创建
            log_dir = Path(temp_dir)
            log_file = log_dir / f"{custom_settings.APP_NAME}.log"
            assert log_file.exists()

            # 验证错误日志文件
            error_log_file = log_dir / f"{custom_settings.APP_NAME}_error.log"
            assert error_log_file.exists()

    def test_log_format(self):
        """测试日志格式"""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_settings = Settings(
                LOG_LEVEL="INFO",
                LOG_TO_CONSOLE=True,
                LOG_TO_FILE=False,
                LOG_DIR=temp_dir,
            )

            setup_logging(custom_settings)

            # 获取日志记录器
            logger = logging.getLogger("test_format")

            # 验证日志格式包含request_id和user_id
            handlers = logging.getLogger().handlers
            assert len(handlers) > 0

            formatter = handlers[0].formatter
            assert "%(request_id)s" in formatter._fmt
            assert "%(user_id)s" in formatter._fmt


class TestGetLogger:
    """获取日志记录器测试"""

    def test_get_logger(self):
        """测试获取日志记录器"""
        logger = get_logger("test_module")

        # 验证返回的是Logger对象
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_get_logger_with_different_names(self):
        """测试获取不同名称的日志记录器"""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        # 验证是不同的记录器
        assert logger1 != logger2
        assert logger1.name == "module1"
        assert logger2.name == "module2"

    def test_get_logger_returns_same_instance(self):
        """测试获取相同名称的日志记录器返回同一实例"""
        logger1 = get_logger("same_module")
        logger2 = get_logger("same_module")

        # 验证是同一实例
        assert logger1 is logger2


class TestLogLevels:
    """日志级别测试"""

    def test_log_level_debug(self):
        """测试DEBUG日志级别"""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_settings = Settings(LOG_LEVEL="DEBUG", LOG_DIR=temp_dir)
            setup_logging(custom_settings)

            root_logger = logging.getLogger()
            assert root_logger.level == logging.DEBUG

    def test_log_level_info(self):
        """测试INFO日志级别"""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_settings = Settings(LOG_LEVEL="INFO", LOG_DIR=temp_dir)
            setup_logging(custom_settings)

            root_logger = logging.getLogger()
            assert root_logger.level == logging.INFO

    def test_log_level_warning(self):
        """测试WARNING日志级别"""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_settings = Settings(LOG_LEVEL="WARNING", LOG_DIR=temp_dir)
            setup_logging(custom_settings)

            root_logger = logging.getLogger()
            assert root_logger.level == logging.WARNING

    def test_log_level_error(self):
        """测试ERROR日志级别"""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_settings = Settings(LOG_LEVEL="ERROR", LOG_DIR=temp_dir)
            setup_logging(custom_settings)

            root_logger = logging.getLogger()
            assert root_logger.level == logging.ERROR


class TestLogOutput:
    """日志输出测试"""

    def test_log_to_console(self):
        """测试日志输出到控制台"""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_settings = Settings(
                LOG_TO_CONSOLE=True, LOG_TO_FILE=False, LOG_DIR=temp_dir
            )
            setup_logging(custom_settings)

            # 验证有StreamHandler
            root_logger = logging.getLogger()
            stream_handlers = [
                h for h in root_logger.handlers if isinstance(h, logging.StreamHandler)
            ]
            assert len(stream_handlers) > 0

    def test_log_to_file(self):
        """测试日志输出到文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_settings = Settings(
                LOG_TO_CONSOLE=False, LOG_TO_FILE=True, LOG_DIR=temp_dir
            )
            setup_logging(custom_settings)

            # 验证有FileHandler
            root_logger = logging.getLogger()
            file_handlers = [
                h for h in root_logger.handlers if hasattr(h, "baseFilename")
            ]
            assert len(file_handlers) >= 2  # 应用日志 + 错误日志

    def test_log_message_writing(self):
        """测试日志消息写入"""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_settings = Settings(
                LOG_TO_CONSOLE=False, LOG_TO_FILE=True, LOG_DIR=temp_dir
            )
            setup_logging(custom_settings)

            # 获取日志记录器
            logger = get_logger("test_writing")

            # 写入日志
            test_message = "Test log message"
            logger.info(test_message)

            # 验证日志文件包含消息
            log_dir = Path(temp_dir)
            log_file = log_dir / f"{custom_settings.APP_NAME}.log"
            log_content = log_file.read_text(encoding="utf-8")

            assert test_message in log_content


class TestRequestIDTracking:
    """请求ID追踪测试"""

    def test_log_with_request_id(self):
        """测试带有请求ID的日志"""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_settings = Settings(
                LOG_TO_CONSOLE=False, LOG_TO_FILE=True, LOG_DIR=temp_dir
            )
            setup_logging(custom_settings)

            # 获取日志记录器
            logger = get_logger("test_request_id")

            # 设置请求ID
            record = logging.LogRecord(
                name="test_request_id",
                level=logging.INFO,
                pathname="test.py",
                lineno=1,
                msg="test message",
                args=(),
                exc_info=None,
            )
            record.request_id = "req-123"
            record.user_id = "user-456"

            # 过滤
            log_filter = RequestIDFilter()
            log_filter.filter(record)

            # 验证
            assert record.request_id == "req-123"
            assert record.user_id == "user-456"


class TestThirdPartyLogging:
    """第三方库日志配置测试"""

    def test_uvicorn_logging_level(self):
        """测试uvicorn日志级别"""
        setup_logging()

        uvicorn_logger = logging.getLogger("uvicorn")
        assert uvicorn_logger.level == logging.WARNING

    def test_sqlalchemy_logging_level(self):
        """测试sqlalchemy日志级别"""
        setup_logging()

        sqlalchemy_logger = logging.getLogger("sqlalchemy")
        assert sqlalchemy_logger.level == logging.WARNING

    def test_httpx_logging_level(self):
        """测试httpx日志级别"""
        setup_logging()

        httpx_logger = logging.getLogger("httpx")
        assert httpx_logger.level == logging.WARNING
