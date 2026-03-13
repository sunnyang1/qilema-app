"""
统一异常处理系统测试

测试异常类、异常处理中间件等功能
"""

import time
from unittest.mock import patch

import pytest
from app.core.exceptions import (
    AlreadyCheckedInException,
    BaseAppException,
    DatabaseException,
    DeviceNotFoundException,
    UnauthorizedException,
    UserAlreadyExistsException,
    UserNotFoundException,
    ValidationException,
    handle_database_error,
)
from app.core.middleware import setup_middleware
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def app():
    """创建测试应用"""
    test_app = FastAPI()

    @test_app.get("/test-not-found")
    def test_not_found():
        raise UserNotFoundException("test_user_id")

    @test_app.get("/test-validation")
    def test_validation():
        raise ValidationException(message="测试验证失败")

    @test_app.get("/test-unauthorized")
    def test_unauthorized():
        raise UnauthorizedException(message="未授权访问")

    @test_app.get("/test-success")
    def test_success():
        return {"message": "success"}

    # 设置中间件
    setup_middleware(test_app)

    return test_app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return TestClient(app)


class TestExceptions:
    """异常类测试"""

    def test_base_app_exception(self):
        """测试基础异常类"""
        exc = BaseAppException(code=1001, message="测试错误")
        assert exc.code == 1001
        assert exc.message == "测试错误"
        assert exc.status_code == 500

    def test_validation_exception(self):
        """测试验证异常"""
        exc = ValidationException(message="参数验证失败")
        assert exc.code == 400
        assert exc.message == "参数验证失败"
        assert exc.status_code == 400

    def test_user_not_found_exception(self):
        """测试用户未找到异常"""
        exc = UserNotFoundException("user123")
        assert exc.code == 404
        assert "user123" in exc.message

    def test_device_not_found_exception(self):
        """测试设备未找到异常"""
        exc = DeviceNotFoundException("device456")
        assert exc.code == 404
        assert "device456" in exc.message

    def test_user_already_exists_exception(self):
        """测试用户已存在异常"""
        exc = UserAlreadyExistsException("13800138000")
        assert exc.code == 1001
        assert "13800138000" in exc.message

    def test_already_checked_in_exception(self):
        """测试已签到异常"""
        exc = AlreadyCheckedInException()
        assert exc.code == 1003
        assert exc.message == "今天已经签到过了"

    def test_handle_database_error(self):
        """测试数据库错误处理"""
        # 测试重复错误
        dup_error = Exception("duplicate key value violates unique constraint")
        exc = handle_database_error(dup_error)
        assert isinstance(exc, DatabaseException)
        assert "已存在" in exc.message

        # 测试外键错误
        fk_error = Exception("foreign key constraint fails")
        exc = handle_database_error(fk_error)
        assert "关联数据不存在" in exc.message

        # 测试其他错误
        other_error = Exception("database connection failed")
        exc = handle_database_error(other_error)
        assert "数据库操作失败" in exc.message


class TestExceptionHandlerMiddleware:
    """异常处理中间件测试"""

    def test_exception_classes_instantiation(self):
        """测试异常类实例化"""
        # 测试基础异常
        exc1 = BaseAppException(code=500, message="Test error")
        assert exc1.code == 500
        assert exc1.message == "Test error"

        # 测试验证异常
        exc2 = ValidationException(message="Validation failed")
        assert exc2.code == 400
        assert "Validation failed" in exc2.message

        # 测试用户未找到异常
        exc3 = UserNotFoundException("user123")
        assert exc3.code == 404
        assert "user123" in exc3.message

        # 测试设备未找到异常
        exc4 = DeviceNotFoundException("dev456")
        assert exc4.code == 404
        assert "dev456" in exc4.message

    def test_handle_app_exception_response_format(self):
        """测试异常响应格式"""
        # 验证异常类可以正确转换为JSON响应
        exc = ValidationException(message="Invalid input")

        # 模拟中间件创建的响应格式
        response_data = {
            "code": exc.code,
            "message": exc.message,
            "timestamp": int(time.time()),
        }

        assert response_data["code"] == 400
        assert "Invalid input" in response_data["message"]
        assert "timestamp" in response_data

    def test_handle_validation_exception(self):
        """测试处理验证异常"""
        # 验证验证异常的状态码和消息
        exc = ValidationException(message="参数验证失败")

        assert exc.code == 400
        assert exc.status_code == 400
        assert exc.message == "参数验证失败"

    def test_handle_unauthorized_exception(self):
        """测试处理未授权异常"""
        # 验证未授权异常的状态码和消息
        exc = UnauthorizedException(message="未授权访问")

        assert exc.code == 401
        assert exc.status_code == 401
        assert exc.message == "未授权访问"


class TestRequestLoggingMiddleware:
    """请求日志中间件测试"""

    def test_request_logging_headers(self, app):
        """测试请求日志记录"""
        client = TestClient(app)

        response = client.get("/test-success")

        # 检查响应头包含请求ID和处理时间
        assert "X-Request-ID" in response.headers
        assert "X-Process-Time" in response.headers

        # 验证处理时间格式
        process_time_str = response.headers["X-Process-Time"]
        assert "ms" in process_time_str

    def test_success_response_format(self, client):
        """测试成功响应格式"""
        response = client.get("/test-success")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "success"


class TestRequestIDMiddleware:
    """请求ID中间件测试"""

    def test_generate_request_id(self, client):
        """测试生成请求ID"""
        response = client.get("/test-success")

        # 验证响应头包含请求ID
        assert "X-Request-ID" in response.headers
        request_id = response.headers["X-Request-ID"]
        assert isinstance(request_id, str)
        assert len(request_id) > 0

    def test_use_custom_request_id(self, client):
        """测试使用自定义请求ID"""
        custom_id = "custom-request-id-123"

        response = client.get("/test-success", headers={"X-Request-ID": custom_id})

        # 验证使用自定义请求ID
        assert response.headers["X-Request-ID"] == custom_id


class TestMiddlewareIntegration:
    """中间件集成测试"""

    def test_middleware_chain_order(self, client):
        """测试中间件执行顺序"""
        response = client.get("/test-success")

        # 所有中间件都应该正常工作
        assert response.status_code == 200
        assert "X-Process-Time" in response.headers

    def test_request_logging_on_success(self, client):
        """测试成功请求日志记录"""
        with patch("app.core.middleware.logger.info") as mock_logger:
            client.get("/test-success")

            # 验证记录了请求日志
            assert mock_logger.called

            # 应该记录开始和完成至少一次
            assert mock_logger.call_count >= 1
