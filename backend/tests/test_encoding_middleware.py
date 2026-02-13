"""
测试 UTF-8 编码中间件

验证所有响应都使用 UTF-8 编码，解决中文乱码问题
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.middleware import EncodingMiddleware


def test_encoding_middleware_adds_charset():
    """测试编码中间件确保所有响应包含 charset=utf-8"""
    app = FastAPI()
    app.add_middleware(EncodingMiddleware)

    @app.get("/test-encoding")
    def test_encoding():
        return {"message": "测试中文", "status": "success"}

    client = TestClient(app)
    response = client.get("/test-encoding")

    # 验证响应状态码
    assert response.status_code == 200

    # 验证 Content-Type 包含 charset=utf-8
    content_type = response.headers.get("content-type", "")
    assert "application/json" in content_type
    assert "charset=utf-8" in content_type.lower()

    # 验证响应内容正确
    assert response.json()["message"] == "测试中文"


def test_encoding_middleware_error_response():
    """测试编码中间件在错误响应中也能正确处理中文"""
    from app.core.exceptions import BaseAppException
    from app.core.middleware import ExceptionHandlerMiddleware

    app = FastAPI()
    app.add_middleware(EncodingMiddleware)
    app.add_middleware(ExceptionHandlerMiddleware)

    @app.get("/test-error")
    def test_error():
        raise BaseAppException(code=500, message="这是一个中文错误信息")

    client = TestClient(app)
    response = client.get("/test-error")

    # 验证 Content-Type 包含 charset=utf-8
    content_type = response.headers.get("content-type", "")
    assert "charset=utf-8" in content_type.lower()

    # 打印实际响应内容用于调试
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.text}")

    # 验证响应中包含正确的中文消息（不在乱码形式）
    response_text = response.text
    assert "这是" in response_text  # 验证中文字符存在
    assert "æ" not in response_text  # 验证没有乱码


def test_encoding_middleware_preserves_existing_charset():
    """测试编码中间件保留已有的 charset 设置"""
    app = FastAPI()
    app.add_middleware(EncodingMiddleware)

    @app.get("/test-custom-charset")
    def test_custom_charset():
        from fastapi import Response
        return Response(
            content='{"message":"测试"}',
            media_type="application/json; charset=UTF-8"
        )

    client = TestClient(app)
    response = client.get("/test-custom-charset")

    # 验证原有的 charset 被保留
    content_type = response.headers.get("content-type", "")
    assert "charset" in content_type.lower()


def test_chinese_characters_no_mojibake():
    """测试中文字符不会出现乱码"""
    app = FastAPI()
    app.add_middleware(EncodingMiddleware)

    test_messages = [
        "无法连接到后端服务",  # 原始错误消息
        "操作成功",
        "数据库连接失败",
        "用户不存在",
        "权限验证失败",
    ]

    @app.get("/test/{index}")
    def test_chinese(index: int):
        return {
            "message": test_messages[index],
            "status": "success"
        }

    client = TestClient(app)

    for idx, expected_message in enumerate(test_messages):
        response = client.get(f"/test/{idx}")

        # 验证响应状态码
        assert response.status_code == 200

        # 验证 Content-Type 包含 charset=utf-8
        content_type = response.headers.get("content-type", "")
        assert "charset=utf-8" in content_type.lower()

        # 验证中文字符没有被编码为乱码
        actual_message = response.json()["message"]
        assert actual_message == expected_message, f"期望: {expected_message}, 实际: {actual_message}"

        # 验证不包含乱码模式（原始乱码示例）
        assert "æ" not in actual_message
        assert "è" not in actual_message
        assert "å" not in actual_message
        assert "¸" not in actual_message


def test_json_response_with_chinese():
    """测试 JSONResponse 中的中文字符正确编码"""
    from fastapi.responses import JSONResponse

    app = FastAPI()
    app.add_middleware(EncodingMiddleware)

    @app.get("/test-json-response")
    def test_json():
        return JSONResponse(
            content={
                "success": True,
                "message": "请求处理成功",
                "data": {
                    "items": ["项目1", "项目2", "项目3"],
                    "description": "这是一些测试数据"
                }
            }
        )

    client = TestClient(app)
    response = client.get("/test-json-response")

    # 验证响应内容
    data = response.json()
    assert data["message"] == "请求处理成功"
    assert data["data"]["items"][0] == "项目1"
    assert data["data"]["description"] == "这是一些测试数据"

    # 验证 Content-Type
    content_type = response.headers.get("content-type", "")
    assert "charset=utf-8" in content_type.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
