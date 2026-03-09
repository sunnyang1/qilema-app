"""
全局异常处理器

统一处理应用中所有异常，返回标准化的错误响应
"""

from typing import Union

from app.core.exceptions import BaseAppException
from app.core.response import APIResponse
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


async def base_app_exception_handler(
    request: Request, exc: BaseAppException
) -> JSONResponse:
    """
    处理应用自定义异常

    Args:
        request: 请求对象
        exc: 应用异常

    Returns:
        JSONResponse: 标准化的错误响应
    """
    return APIResponse.error(
        message=exc.message,
        error_code=str(exc.code),
        details=exc.detail,
        status_code=exc.status_code,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    处理请求参数验证异常

    Args:
        request: 请求对象
        exc: 验证异常

    Returns:
        JSONResponse: 标准化的错误响应
    """
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    return APIResponse.validation_error(details=errors)


async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """
    处理数据库异常

    Args:
        request: 请求对象
        exc: SQLAlchemy异常

    Returns:
        JSONResponse: 标准化的错误响应
    """
    error_message = str(exc)

    # 根据错误类型提供友好的消息
    if "duplicate" in error_message.lower() or "unique" in error_message.lower():
        message = "数据已存在"
    elif "foreign key" in error_message.lower():
        message = "关联数据不存在"
    elif "constraint" in error_message.lower():
        message = "数据约束冲突"
    else:
        message = "数据库操作失败"

    return APIResponse.error(
        message=message,
        error_code="DATABASE_ERROR",
        details=error_message,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def integrity_error_handler(
    request: Request, exc: IntegrityError
) -> JSONResponse:
    """
    处理数据库完整性错误

    Args:
        request: 请求对象
        exc: 完整性错误

    Returns:
        JSONResponse: 标准化的错误响应
    """
    error_message = str(exc.orig) if hasattr(exc, "orig") else str(exc)

    # 分析具体的完整性错误
    if "UNIQUE constraint failed" in error_message:
        message = "数据已存在，请勿重复添加"
    elif "FOREIGN KEY constraint failed" in error_message:
        message = "关联的数据不存在"
    elif "NOT NULL constraint failed" in error_message:
        message = "必填字段不能为空"
    else:
        message = "数据完整性错误"

    return APIResponse.error(
        message=message,
        error_code="INTEGRITY_ERROR",
        details=error_message,
        status_code=status.HTTP_400_BAD_REQUEST,
    )


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """
    处理值错误

    Args:
        request: 请求对象
        exc: 值错误

    Returns:
        JSONResponse: 标准化的错误响应
    """
    return APIResponse.bad_request(message=str(exc) or "请求参数错误")


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    处理通用异常

    Args:
        request: 请求对象
        exc: 通用异常

    Returns:
        JSONResponse: 标准化的错误响应
    """
    # 记录错误日志
    import logging

    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return APIResponse.server_error(message="服务器内部错误，请稍后重试")


def register_exception_handlers(app):
    """
    注册所有异常处理器到FastAPI应用

    Args:
        app: FastAPI应用实例
    """
    # 应用自定义异常
    app.add_exception_handler(BaseAppException, base_app_exception_handler)

    # 参数验证异常
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # 数据库异常
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)

    # 值错误
    app.add_exception_handler(ValueError, value_error_handler)

    # 通用异常（最后注册）
    app.add_exception_handler(Exception, generic_exception_handler)
