"""
中间件模块

提供全局异常处理、请求日志、CORS等中间件功能
"""

import time
import uuid
import logging
import re
from typing import Callable, Optional
from fastapi import Request, Response, FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.exceptions import BaseAppException

# 设置日志
logger = logging.getLogger(__name__)

# 慢请求阈值（毫秒）
SLOW_REQUEST_THRESHOLD = 500


class EncodingMiddleware(BaseHTTPMiddleware):
    """编码中间件

    强制所有响应使用 UTF-8 编码，解决中文乱码问题
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并确保响应使用 UTF-8 编码"""
        response = await call_next(request)

        # 检查并修改响应头
        headers = dict(response.headers)

        # 检查是否已有 Content-Type
        content_type = headers.get("content-type", "")

        if content_type:
            # 确保包含 charset=utf-8
            if "charset" not in content_type.lower():
                headers["content-type"] = f"{content_type}; charset=utf-8"
        else:
            # 添加默认的 JSON 响应头
            headers["content-type"] = "application/json; charset=utf-8"

        # 更新响应头
        response.headers.update(headers)

        return response


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
            return await self._handle_app_exception(request, exc)
        except Exception as exc:
            return await self._handle_unexpected_exception(request, exc)

    async def _handle_app_exception(self, request: Request, exc: BaseAppException) -> JSONResponse:
        """处理应用异常"""
        request_id = getattr(request.state, "request_id", "unknown")

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

        sanitized_detail = self._sanitize_sensitive_info(exc.detail)

        return JSONResponse(
            status_code=exc.status_code,
            media_type="application/json; charset=utf-8",
            content={
                "code": exc.code,
                "message": exc.message,
                "detail": sanitized_detail,
                "request_id": request_id,
                "timestamp": int(time.time())
            }
        )

    async def _handle_unexpected_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """处理未预期的异常"""
        request_id = getattr(request.state, "request_id", "unknown")

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

        sanitized_message = self._sanitize_sensitive_info(str(exc))

        return JSONResponse(
            status_code=500,
            media_type="application/json; charset=utf-8",
            content={
                "code": 500,
                "message": "服务器内部错误",
                "detail": sanitized_message if logger.isEnabledFor(logging.DEBUG) else None,
                "request_id": request_id,
                "timestamp": int(time.time())
            }
        )

    def _sanitize_sensitive_info(self, info: Optional[any]) -> Optional[str]:
        """脱敏敏感信息（密码、token等）"""
        if not info:
            return None

        info_str = str(info)

        # 脱敏密码字段
        info_str = re.sub(r'(["\']?password["\']?\s*[:=]\s*["\']?)([^"\'\s,}]+)', r'\1****', info_str, flags=re.IGNORECASE)
        # 脱敏token字段
        info_str = re.sub(r'(["\']?token["\']?\s*[:=]\s*["\']?)([^"\'\s,}]+)', r'\1****', info_str, flags=re.IGNORECASE)
        # 脱敏secret字段
        info_str = re.sub(r'(["\']?secret["\']?\s*[:=]\s*["\']?)([^"\'\s,}]+)', r'\1****', info_str, flags=re.IGNORECASE)

        return info_str


class EnhancedLoggingMiddleware(BaseHTTPMiddleware):
    """增强的日志中间件

    支持请求ID生成、性能监控、慢请求标记
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并记录详细日志"""
        # 生成8位十六进制请求ID
        request_id = uuid.uuid4().hex[:8]
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

            # 计算响应时间（毫秒）
            duration_ms = (time.time() - start_time) * 1000

            # 添加响应头
            response.headers["X-Request-ID"] = request_id

            # 识别慢请求并标记
            is_slow = duration_ms > SLOW_REQUEST_THRESHOLD
            if is_slow:
                logger.warning(
                    f"[{request_id}] 慢请求检测: {request.method} {request.url.path} "
                    f"耗时 {duration_ms:.2f}ms（阈值: {SLOW_REQUEST_THRESHOLD}ms）",
                    extra={
                        "request_id": request_id,
                        "method": request.method,
                        "path": request.url.path,
                        "duration_ms": duration_ms,
                        "slow_request": True
                    }
                )

            # 记录响应日志
            logger.info(
                f"[{request_id}] {request.method} {request.url.path} - 完成 "
                f"({response.status_code}, {duration_ms:.2f}ms)",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "slow_request": is_slow
                }
            )

            return response

        except Exception as exc:
            # 计算响应时间
            duration_ms = (time.time() - start_time) * 1000

            # 记录错误日志
            logger.error(
                f"[{request_id}] {request.method} {request.url.path} - 失败 "
                f"({duration_ms:.2f}ms): {str(exc)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                    "exception": str(exc)
                },
                exc_info=exc
            )
            raise


# 保留旧的RequestLoggingMiddleware作为别名，保持向后兼容
RequestLoggingMiddleware = EnhancedLoggingMiddleware


def setup_middleware(app: FastAPI) -> None:
    """设置所有中间件

    Args:
        app: FastAPI应用实例
    """
    # 编码中间件 - 确保所有响应使用 UTF-8 编码（最先添加）
    app.add_middleware(EncodingMiddleware)

    # 异常处理中间件
    app.add_middleware(ExceptionHandlerMiddleware)

    # 请求日志中间件
    app.add_middleware(EnhancedLoggingMiddleware)
