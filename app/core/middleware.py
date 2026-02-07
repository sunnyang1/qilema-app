"""
中间件模块

提供全局异常处理、请求日志、CORS等中间件功能
"""

import time
import uuid
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.exceptions import BaseAppException

# 设置日志
logger = logging.getLogger(__name__)


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """全局异常处理中间件

    捕获所有应用异常，统一返回格式化的错误响应
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并捕获异常

        Args:
            request: 请求对象
            call_next: 下一个中间件/路由处理函数

        Returns:
            Response: 响应对象
        """
        try:
            response = await call_next(request)
            return response
        except BaseAppException as exc:
            # 处理自定义应用异常
            return await self._handle_app_exception(request, exc)
        except Exception as exc:
            # 处理未捕获的异常
            return await self._handle_unexpected_exception(request, exc)

    async def _handle_app_exception(self, request: Request, exc: BaseAppException) -> JSONResponse:
        """处理应用异常

        Args:
            request: 请求对象
            exc: 应用异常

        Returns:
            JSONResponse: 格式化的错误响应
        """
        request_id = getattr(request.state, "request_id", "unknown")

        # 记录错误日志
        logger.error(
            f"[{request_id}] 应用异常: {exc.code} - {exc.message}",
            extra={
                "request_id": request_id,
                "error_code": exc.code,
                "error_message": exc.message,
                "detail": exc.detail,
                "path": request.url.path,
                "method": request.method
            },
            exc_info=exc
        )

        # 返回格式化的错误响应
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.code,
                "message": exc.message,
                "detail": exc.detail,
                "timestamp": int(time.time())
            }
        )

    async def _handle_unexpected_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """处理未预期的异常

        Args:
            request: 请求对象
            exc: 异常对象

        Returns:
            JSONResponse: 格式化的服务器错误响应
        """
        request_id = getattr(request.state, "request_id", "unknown")

        # 记录错误日志
        logger.error(
            f"[{request_id}] 未预期的异常: {type(exc).__name__} - {str(exc)}",
            extra={
                "request_id": request_id,
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "path": request.url.path,
                "method": request.method
            },
            exc_info=exc
        )

        # 返回格式化的错误响应
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "服务器内部错误",
                "detail": str(exc) if logger.isEnabledFor(logging.DEBUG) else None,
                "timestamp": int(time.time())
            }
        )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件

    记录所有HTTP请求的详细信息，包括请求ID、响应时间等
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并记录日志

        Args:
            request: 请求对象
            call_next: 下一个中间件/路由处理函数

        Returns:
            Response: 响应对象
        """
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # 记录请求开始时间
        start_time = time.time()

        # 记录请求日志
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - 开始处理",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent")
            }
        )

        try:
            # 调用下一个中间件/路由
            response = await call_next(request)

            # 计算响应时间
            process_time = (time.time() - start_time) * 1000  # 转换为毫秒

            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.2f}ms"

            # 记录响应日志
            logger.info(
                f"[{request_id}] {request.method} {request.url.path} - 完成 "
                f"({response.status_code}, {process_time:.2f}ms)",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time_ms": process_time
                }
            )

            return response

        except Exception as exc:
            # 计算响应时间
            process_time = (time.time() - start_time) * 1000

            # 记录错误日志
            logger.error(
                f"[{request_id}] {request.method} {request.url.path} - 失败 "
                f"({process_time:.2f}ms): {str(exc)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "process_time_ms": process_time,
                    "exception": str(exc)
                },
                exc_info=exc
            )

            # 重新抛出异常，由ExceptionHandlerMiddleware处理
            raise


class RequestIDMiddleware(BaseHTTPMiddleware):
    """请求ID中间件

    为每个请求生成唯一的请求ID，用于追踪和日志关联
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并添加请求ID

        Args:
            request: 请求对象
            call_next: 下一个中间件/路由处理函数

        Returns:
            Response: 响应对象
        """
        # 生成或使用现有的请求ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        # 调用下一个中间件/路由
        response = await call_next(request)

        # 添加请求ID到响应头
        response.headers["X-Request-ID"] = request_id

        return response


def setup_middleware(app: ASGIApp):
    """设置所有中间件

    Args:
        app: FastAPI应用实例
    """
    # 按顺序添加中间件
    # 注意：中间件的执行顺序与添加顺序相反
    app.add_middleware(ExceptionHandlerMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)
