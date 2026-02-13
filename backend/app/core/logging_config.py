"""
结构化日志配置

使用 Python logging 模块配置 JSON 格式日志输出
支持日志轮转和敏感信息脱敏
"""

import logging
import logging.handlers
import json
import sys
import re
from datetime import datetime
from typing import Any, Dict
from pathlib import Path


# 敏感信息字段列表（自动脱敏）
SENSITIVE_FIELDS = {
    'password', 'pwd', 'passwd', 'secret', 'token', 'authorization',
    'api_key', 'apikey', 'access_token', 'refresh_token',
    'id_token', 'client_secret', 'private_key', 'credit_card',
    'ssn', 'social_security', 'cvv', 'pin'
}


class JSONFormatter(logging.Formatter):
    """
    JSON 格式化器

    输出结构化 JSON 日志，包含：
    - timestamp: ISO 8601 格式时间戳
    - level: 日志级别
    - logger: 日志记录器名称
    - message: 日志消息
    - request_id: 请求 ID（如果有）
    - user_id: 用户 ID（如果有）
    - module: 模块名称
    - function: 函数名称
    - line: 行号
    - extra: 额外字段
    - exception: 异常信息（如果有）
    """

    def __init__(self):
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录为 JSON

        Args:
            record: 日志记录

        Returns:
            str: JSON 格式的日志字符串
        """
        # 基础日志字段
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # 添加请求 ID（如果有）
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id

        # 添加用户 ID（如果有）
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id

        # 添加异常信息（如果有）
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }

        # 添加额外字段（如果有）
        if hasattr(record, 'extra_fields') and isinstance(record.extra_fields, dict):
            # 脱敏敏感信息
            log_data['extra'] = self._sanitize_extra_fields(record.extra_fields)

        return json.dumps(log_data, ensure_ascii=False)

    def _sanitize_extra_fields(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        脱敏额外字段中的敏感信息

        Args:
            fields: 原始字段字典

        Returns:
            Dict[str, Any]: 脱敏后的字段字典
        """
        sanitized = {}
        for key, value in fields.items():
            # 检查字段名是否包含敏感关键词
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in SENSITIVE_FIELDS):
                # 脱敏处理
                sanitized[key] = self._mask_value(value)
            else:
                sanitized[key] = value
        return sanitized

    def _mask_value(self, value: Any) -> str:
        """
        脱敏处理值

        Args:
            value: 原始值

        Returns:
            str: 脱敏后的字符串
        """
        if value is None:
            return 'null'

        if isinstance(value, str):
            # 如果是字符串，保留前 2 位和后 2 位，中间用 * 代替
            if len(value) <= 4:
                return '****'
            return value[:2] + '*' * (len(value) - 4) + value[-2:]

        return '****'


class ContextFilter(logging.Filter):
    """
    上下文过滤器

    从 request.state 或 context 中提取请求 ID 和用户 ID
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        过滤并添加上下文信息

        Args:
            record: 日志记录

        Returns:
            bool: 总是返回 True
        """
        # 尝试从上下文中获取请求 ID
        try:
            from contextvars import ContextVar

            request_id_var = ContextVar('request_id', default=None)
            request_id = request_id_var.get()
            if request_id:
                record.request_id = request_id
        except:
            pass

        # 尝试从上下文中获取用户 ID
        try:
            from contextvars import ContextVar

            user_id_var = ContextVar('user_id', default=None)
            user_id = user_id_var.get()
            if user_id:
                record.user_id = user_id
        except:
            pass

        return True


def setup_logging(
    log_level: str = 'INFO',
    log_file: str = None,
    log_to_console: bool = True
) -> logging.Logger:
    """
    配置日志系统

    Args:
        log_level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        log_file: 日志文件路径（可选）
        log_to_console: 是否输出到控制台

    Returns:
        logging.Logger: 配置好的根日志记录器
    """
    # 转换日志级别
    level = getattr(logging, log_level.upper(), logging.INFO)

    # 创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 清除现有处理器
    root_logger.handlers.clear()

    # 创建 JSON 格式化器
    json_formatter = JSONFormatter()

    # 创建上下文过滤器
    context_filter = ContextFilter()

    # 控制台处理器
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(json_formatter)
        console_handler.addFilter(context_filter)
        root_logger.addHandler(console_handler)

    # 文件处理器（带日志轮转）
    if log_file:
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # 创建轮转文件处理器
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(json_formatter)
        file_handler.addFilter(context_filter)
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        logging.Logger: 日志记录器实例
    """
    return logging.getLogger(name)


# 简易示例（如果直接运行此文件）
if __name__ == '__main__':
    # 配置日志
    setup_logging(log_level='DEBUG', log_to_console=True)

    # 获取日志记录器
    logger = get_logger('example')

    # 记录普通日志
    logger.info('Application started')

    # 记录带请求 ID 的日志
    request_id_logger = get_logger('example')
    request_id_logger.info('Processing request', extra={'extra_fields': {'request_id': '12345678'}})

    # 记录带敏感信息的日志
    logger.info('User login attempt', extra={
        'extra_fields': {
            'username': 'test@example.com',
            'password': 'secret123',
            'api_key': 'sk-1234567890abcdef'
        }
    })

    # 记录异常日志
    try:
        1 / 0
    except Exception as e:
        logger.error('Division by zero', exc_info=True)
