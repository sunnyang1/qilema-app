"""
中间件单元测试
"""

import time
from unittest.mock import AsyncMock, Mock, patch

import pytest
from app.core.exceptions import BaseAppException
from app.core.middleware import (
    SLOW_REQUEST_THRESHOLD,
    EnhancedLoggingMiddleware,
    ExceptionHandlerMiddleware,
)
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.datastructures import Headers


class TestEnhancedLoggingMiddleware:
    """EnhancedLoggingMiddleware测试"""

    @pytest.fixture
    def middleware(self):
        """创建中间件实例"""
        app = Mock()
        return EnhancedLoggingMiddleware(app)

    @pytest.mark.asyncio
    async def test_request_id_generation(self, middleware):
        """测试请求ID生成"""
        # 创建模拟请求
        request = Mock(spec=Request)
        request.url = Mock(path="/test")
        request.method = "GET"
        request.query_params = {}
        request.client = Mock(host="127.0.0.1")
        request.headers = Headers({"user-agent": "test"})

        call_next = AsyncMock()
        response = Mock(spec=Response)
        response.status_code = 200
        response.headers = {}
        call_next.return_value = response

        # 调用中间件
        await middleware.dispatch(request, call_next)

        # 验证请求ID已生成
        assert hasattr(request.state, "request_id")
        assert len(request.state.request_id) == 8  # 8位十六进制

        # 验证响应头包含请求ID
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) == 8

    @pytest.mark.asyncio
    async def test_performance_monitoring(self, middleware):
        """测试性能监控"""
        request = Mock(spec=Request)
        request.url = Mock(path="/test")
        request.method = "GET"
        request.query_params = {}
        request.client = Mock(host="127.0.0.1")
        request.headers = Headers({})

        call_next = AsyncMock()
        response = Mock(spec=Response)
        response.status_code = 200
        response.headers = {}
        call_next.return_value = response

        # 调用中间件
        await middleware.dispatch(request, call_next)

        # call_next应该被调用
        assert call_next.called

    @pytest.mark.asyncio
    async def test_slow_request_detection(self, middleware):
        """测试慢请求检测"""
        request = Mock(spec=Request)
        request.url = Mock(path="/test")
        request.method = "GET"
        request.query_params = {}
        request.client = Mock(host="127.0.0.1")
        request.headers = Headers({})

        # 创建一个慢响应
        async def slow_call_next(request):
            time.sleep(0.6)  # 超过500ms阈值
            response = Mock(spec=Response)
            response.status_code = 200
            response.headers = {}
            return response

        call_next = AsyncMock(side_effect=slow_call_next)

        # 调用中间件
        with patch("app.core.middleware.logger") as mock_logger:
            response = await middleware.dispatch(request, call_next)

            # 验证记录了慢请求警告
            warning_calls = [
                call
                for call in mock_logger.warning.call_args_list
                if "慢请求检测" in str(call)
            ]
            assert len(warning_calls) > 0

    @pytest.mark.asyncio
    async def test_request_id_logging(self, middleware):
        """测试日志包含请求ID"""
        request = Mock(spec=Request)
        request.url = Mock(path="/test")
        request.method = "POST"
        request.query_params = {"key": "value"}
        request.client = Mock(host="127.0.0.1")
        request.headers = Headers({"user-agent": "pytest"})

        call_next = AsyncMock()
        response = Mock(spec=Response)
        response.status_code = 200
        response.headers = {}
        call_next.return_value = response

        # 调用中间件
        with patch("app.core.middleware.logger") as mock_logger:
            await middleware.dispatch(request, call_next)

            # 验证日志调用
            assert mock_logger.info.called
            # 检查日志中包含请求ID
            log_calls = str(mock_logger.info.call_args_list)
            assert "request_id" in log_calls


class TestExceptionHandlerMiddleware:
    """ExceptionHandlerMiddleware测试"""

    @pytest.fixture
    def middleware(self):
        """创建中间件实例"""
        app = Mock()
        return ExceptionHandlerMiddleware(app)

    @pytest.mark.asyncio
    async def test_handles_base_app_exception(self, middleware):
        """测试处理自定义应用异常"""
        request = Mock(spec=Request)
        request.url = Mock(path="/test")
        request.method = "GET"
        request.state = Mock(request_id="test123")

        # 创建自定义异常
        exc = BaseAppException(code="TEST_ERROR", message="测试错误", status_code=400)

        call_next = AsyncMock(side_effect=exc)

        # 调用中间件
        with patch("app.core.middleware.logger") as mock_logger:
            response = await middleware.dispatch(request, call_next)

            # 验证返回JSON响应
            assert isinstance(response, JSONResponse)
            assert response.status_code == 400

            # 验证响应内容
            content = (
                response.body.decode()
                if isinstance(response.body, bytes)
                else response.body
            )
            import json

            data = json.loads(content)
            assert data["code"] == "TEST_ERROR"
            assert data["message"] == "测试错误"
            assert "request_id" in data

    @pytest.mark.asyncio
    async def test_handles_unexpected_exception(self, middleware):
        """测试处理未预期异常"""
        request = Mock(spec=Request)
        request.url = Mock(path="/test")
        request.method = "GET"
        request.state = Mock(request_id="test456")

        # 创建未预期异常
        exc = ValueError("未预期的错误")

        call_next = AsyncMock(side_effect=exc)

        # 调用中间件
        with patch("app.core.middleware.logger") as mock_logger:
            response = await middleware.dispatch(request, call_next)

            # 验证返回500错误
            assert isinstance(response, JSONResponse)
            assert response.status_code == 500

            # 验证响应内容
            content = (
                response.body.decode()
                if isinstance(response.body, bytes)
                else response.body
            )
            import json

            data = json.loads(content)
            assert data["code"] == 500
            assert data["message"] == "服务器内部错误"

    @pytest.mark.asyncio
    async def test_sanitize_sensitive_info(self, middleware):
        """测试敏感信息脱敏"""
        # 测试密码脱敏
        result = middleware._sanitize_sensitive_info('{"password": "secret123"}')
        assert "secret123" not in result
        assert "****" in result

        # 测试token脱敏
        result = middleware._sanitize_sensitive_info('{"token": "abc123xyz"}')
        assert "abc123xyz" not in result
        assert "****" in result

        # 测试secret脱敏
        result = middleware._sanitize_sensitive_info('{"secret": "mysecret"}')
        assert "mysecret" not in result
        assert "****" in result

    @pytest.mark.asyncio
    async def test_normal_request_passes_through(self, middleware):
        """测试正常请求通过"""
        request = Mock(spec=Request)
        request.url = Mock(path="/test")
        request.method = "GET"

        call_next = AsyncMock()
        response = Mock(spec=Response)
        call_next.return_value = response

        # 调用中间件
        result = await middleware.dispatch(request, call_next)

        # 验证正常返回
        assert result == response
        assert call_next.called

    @pytest.mark.asyncio
    async def test_error_logging_with_request_id(self, middleware):
        """测试错误日志包含请求ID"""
        request = Mock(spec=Request)
        request.url = Mock(path="/test")
        request.method = "GET"
        request.state = Mock(request_id="error123")

        exc = ValueError("测试错误")
        call_next = AsyncMock(side_effect=exc)

        # 调用中间件
        with patch("app.core.middleware.logger") as mock_logger:
            await middleware.dispatch(request, call_next)

            # 验证错误日志包含请求ID
            error_calls = str(mock_logger.error.call_args_list)
            assert "error123" in error_calls
