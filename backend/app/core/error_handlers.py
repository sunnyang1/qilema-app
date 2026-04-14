"""
全局异常处理器

统一处理应用中所有异常，返回标准化的错误响应
"""

import logging
from typing import Optional

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.config import settings
from app.core.exceptions import BaseAppException
from app.core.response import APIResponse

logger = logging.getLogger(__name__)


def _request_id(request: Request) -> Optional[str]:
    return getattr(request.state, "request_id", None)


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
    resp = APIResponse.error(
        message=exc.message,
        error_code=str(exc.code),
        details=exc.detail,
        status_code=exc.status_code,
    )
    return _merge_request_id_into_json_response(resp, request)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    统一 FastAPI/Starlette HTTPException 响应体，并保留 detail 以兼容既有客户端（US-004）。

    必须透传 exc.headers（如 OAuth2 401 的 WWW-Authenticate），否则破坏标准客户端与 Swagger Authorize。
    """
    detail = exc.detail
    if isinstance(detail, str):
        message = detail
    elif detail is None:
        message = "请求无法处理"
    else:
        message = str(detail)
    rid = _request_id(request)
    hdrs = dict(exc.headers) if exc.headers else None
    return JSONResponse(
        status_code=exc.status_code,
        media_type="application/json; charset=utf-8",
        content={
            "detail": detail,
            "success": False,
            "message": message,
            "error_code": f"HTTP_{exc.status_code}",
            "request_id": rid,
        },
        headers=hdrs,
    )


def _merge_request_id_into_json_response(
    resp: JSONResponse, request: Request
) -> JSONResponse:
    rid = _request_id(request)
    if rid is None:
        return resp
    import json

    try:
        body = json.loads(resp.body.decode("utf-8"))
    except (json.JSONDecodeError, AttributeError, TypeError):
        return resp
    if isinstance(body, dict) and "request_id" not in body:
        body["request_id"] = rid
        return JSONResponse(
            status_code=resp.status_code,
            media_type=resp.media_type,
            content=body,
        )
    return resp


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

    rid = _request_id(request)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        media_type="application/json; charset=utf-8",
        content={
            "success": False,
            "message": "数据验证失败",
            "error_code": "VALIDATION_ERROR",
            "details": errors,
            "request_id": rid,
        },
    )


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
    logger.error(
        "SQLAlchemyError: %s",
        error_message,
        exc_info=exc,
        extra={"request_id": _request_id(request)},
    )

    # 根据错误类型提供友好的消息
    if "duplicate" in error_message.lower() or "unique" in error_message.lower():
        message = "数据已存在"
    elif "foreign key" in error_message.lower():
        message = "关联数据不存在"
    elif "constraint" in error_message.lower():
        message = "数据约束冲突"
    else:
        message = "数据库操作失败"

    client_details = error_message if settings.DEBUG else None
    resp = APIResponse.error(
        message=message,
        error_code="DATABASE_ERROR",
        details=client_details,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    return _merge_request_id_into_json_response(resp, request)


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
    logger.warning(
        "IntegrityError: %s",
        error_message,
        exc_info=exc,
        extra={"request_id": _request_id(request)},
    )

    # 分析具体的完整性错误
    if "UNIQUE constraint failed" in error_message:
        message = "数据已存在，请勿重复添加"
    elif "FOREIGN KEY constraint failed" in error_message:
        message = "关联的数据不存在"
    elif "NOT NULL constraint failed" in error_message:
        message = "必填字段不能为空"
    else:
        message = "数据完整性错误"

    client_details = error_message if settings.DEBUG else None
    resp = APIResponse.error(
        message=message,
        error_code="INTEGRITY_ERROR",
        details=client_details,
        status_code=status.HTTP_400_BAD_REQUEST,
    )
    return _merge_request_id_into_json_response(resp, request)


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """
    处理值错误

    Args:
        request: 请求对象
        exc: 值错误

    Returns:
        JSONResponse: 标准化的错误响应
    """
    if settings.DEBUG:
        message = str(exc) or "请求参数错误"
    else:
        message = "请求参数错误"
    resp = APIResponse.bad_request(message=message)
    return _merge_request_id_into_json_response(resp, request)


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

    resp = APIResponse.server_error(message="服务器内部错误，请稍后重试")
    return _merge_request_id_into_json_response(resp, request)


def register_exception_handlers(app):
    """
    注册所有异常处理器到FastAPI应用

    Args:
        app: FastAPI应用实例
    """
    # 应用自定义异常
    app.add_exception_handler(BaseAppException, base_app_exception_handler)

    # 通用 HTTP 异常（需在 BaseAppException 之后注册；子类仍走上方处理器）
    app.add_exception_handler(HTTPException, http_exception_handler)

    # 参数验证异常
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # 数据库异常
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)

    # 值错误
    app.add_exception_handler(ValueError, value_error_handler)

    # 通用异常（最后注册）
    app.add_exception_handler(Exception, generic_exception_handler)
