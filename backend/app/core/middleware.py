"""
中间件模块

提供全局异常处理、请求日志、CORS等中间件功能
"""

import logging
import re
import time
import uuid
from typing import Any, Callable, Optional

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.auth_policy import is_public_path
from app.core.config import settings
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

    async def _handle_app_exception(
        self, request: Request, exc: BaseAppException
    ) -> JSONResponse:
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
                "method": request.method,
            },
            exc_info=exc,
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
                "timestamp": int(time.time()),
            },
        )

    async def _handle_unexpected_exception(
        self, request: Request, exc: Exception
    ) -> JSONResponse:
        """处理未预期的异常"""
        request_id = getattr(request.state, "request_id", "unknown")

        logger.error(
            f"[{request_id}] 未预期的异常: {type(exc).__name__} - {str(exc)}",
            extra={
                "request_id": request_id,
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "path": request.url.path,
                "method": request.method,
            },
            exc_info=exc,
        )

        sanitized_message = self._sanitize_sensitive_info(str(exc))

        return JSONResponse(
            status_code=500,
            media_type="application/json; charset=utf-8",
            content={
                "code": 500,
                "message": "服务器内部错误",
                "detail": (
                    sanitized_message if logger.isEnabledFor(logging.DEBUG) else None
                ),
                "request_id": request_id,
                "timestamp": int(time.time()),
            },
        )

    def _sanitize_sensitive_info(self, info: Optional[Any]) -> Optional[str]:
        """脱敏敏感信息（密码、token等）"""
        if not info:
            return None

        info_str = str(info)

        # 脱敏密码字段
        info_str = re.sub(
            r'(["\']?password["\']?\s*[:=]\s*["\']?)([^"\'\s,}]+)',
            r"\1****",
            info_str,
            flags=re.IGNORECASE,
        )
        # 脱敏token字段
        info_str = re.sub(
            r'(["\']?token["\']?\s*[:=]\s*["\']?)([^"\'\s,}]+)',
            r"\1****",
            info_str,
            flags=re.IGNORECASE,
        )
        # 脱敏secret字段
        info_str = re.sub(
            r'(["\']?secret["\']?\s*[:=]\s*["\']?)([^"\'\s,}]+)',
            r"\1****",
            info_str,
            flags=re.IGNORECASE,
        )

        return info_str


class EnhancedLoggingMiddleware(BaseHTTPMiddleware):
    """增强的日志中间件

    支持请求ID生成、性能监控、慢请求标记
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并记录详细日志"""
        # 请求 ID：优先使用客户端传入的 X-Request-ID（便于分布式追踪）
        incoming_rid = request.headers.get("x-request-id") or request.headers.get(
            "X-Request-ID"
        )
        if incoming_rid and incoming_rid.strip():
            raw = incoming_rid.strip()[:128]
            # 去掉 ASCII 控制字符与 DEL，保留 UTF-8（含中文）用于关联 ID
            request_id = (
                re.sub(r"[\x00-\x1f\x7f]", "", raw)[:128] or uuid.uuid4().hex[:8]
            )
        else:
            request_id = uuid.uuid4().hex[:8]
        request.state.request_id = request_id
        request.state.is_public_path = is_public_path(request.url.path)

        # 记录请求开始时间
        start_time = time.time()

        # 记录请求日志
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - 开始处理",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "is_public_path": request.state.is_public_path,
                "query_params": str(request.query_params),
                "client": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            },
        )

        try:
            # 调用下一个中间件/路由
            response = await call_next(request)

            # 计算响应时间（毫秒）
            duration_ms = (time.time() - start_time) * 1000

            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"

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
                        "is_public_path": request.state.is_public_path,
                        "duration_ms": duration_ms,
                        "slow_request": True,
                    },
                )

            # 记录响应日志
            logger.info(
                f"[{request_id}] {request.method} {request.url.path} - 完成 "
                f"({response.status_code}, {duration_ms:.2f}ms)",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "is_public_path": request.state.is_public_path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "slow_request": is_slow,
                },
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
                    "is_public_path": request.state.is_public_path,
                    "duration_ms": duration_ms,
                    "exception": str(exc),
                },
                exc_info=exc,
            )
            raise


# 保留旧的RequestLoggingMiddleware作为别名，保持向后兼容
RequestLoggingMiddleware = EnhancedLoggingMiddleware


class ApiVersionResponseMiddleware(BaseHTTPMiddleware):
    """为 v1 API 响应附加 X-API-Version（US-004 / 版本可观测性）。"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        path = request.url.path
        if path.startswith(settings.API_V1_PREFIX):
            response.headers["X-API-Version"] = "1"
        return response


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

    # API 版本响应头（最后添加 = 中间件链最外层，响应最后写出）
    app.add_middleware(ApiVersionResponseMiddleware)
