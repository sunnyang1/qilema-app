"""
端到端测试：验证中文编码修复

模拟原始问题场景：验证 "无法连接到后端服务" 不会出现乱码
"""

import pytest
from app.core.exceptions import BaseAppException
from app.core.middleware import (
    EncodingMiddleware,
    ExceptionHandlerMiddleware,
    setup_middleware,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_backend_connection_error_no_mojibake():
    """测试原始错误消息不会出现乱码"""
    # 创建 FastAPI 应用并设置所有中间件
    app = FastAPI()
    setup_middleware(app)

    @app.get("/test-backend-connection")
    def test_backend_connection():
        # 模拟原始错误场景
        raise BaseAppException(code=1000, message="无法连接到后端服务", status_code=500)

    client = TestClient(app)
    response = client.get("/test-backend-connection")

    # 验证响应状态码
    assert response.status_code == 500

    # 验证 Content-Type 包含 charset=utf-8
    content_type = response.headers.get("content-type", "")
    assert "application/json" in content_type
    assert "charset=utf-8" in content_type.lower()

    # 验证响应内容
    response_text = response.text

    # 验证原始乱码模式不存在
    assert "æ— æ³•è¿žæŽ¥åˆ°åŽç«¯æœåŠ¡" not in response_text

    # 验证中文字符正确存在
    assert "无法连接到后端服务" in response_text

    # 验证不包含乱码字符
    assert "æ" not in response_text
    assert "è" not in response_text
    assert "å" not in response_text
    assert "¸" not in response_text

    print(f"✓ 测试通过！响应内容正确: {response_text}")


def test_common_chinese_error_messages():
    """测试常见的中文错误消息"""
    app = FastAPI()
    setup_middleware(app)

    test_cases = [
        ("操作成功", 200, "success"),
        ("参数验证失败", 400, "validation"),
        ("未授权访问", 401, "unauthorized"),
        ("资源不存在", 404, "not_found"),
        ("服务器内部错误", 500, "server_error"),
        ("数据库连接失败", 500, "database"),
        ("网络请求超时", 504, "timeout"),
    ]

    for message, status_code, endpoint in test_cases:

        @app.get(f"/test/{endpoint}")
        def test_endpoint():
            if status_code >= 400:
                raise BaseAppException(
                    code=status_code, message=message, status_code=status_code
                )
            return {"message": message}

    client = TestClient(app)

    for message, status_code, endpoint in test_cases:
        response = client.get(f"/test/{endpoint}")

        # 验证状态码
        assert response.status_code == status_code

        # 验证中文正确显示
        response_text = response.text
        assert message in response_text, f"期望消息 '{message}' 在响应中找到"

        # 验证没有乱码
        assert "æ" not in response_text
        assert "è" not in response_text

        print(f"✓ [{endpoint}] 消息 '{message}' 正确显示")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
