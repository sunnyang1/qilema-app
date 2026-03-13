"""
ApiResponseBuilder单元测试
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# 定义测试用的Schema
class TestUserSchema(BaseModel):
    """测试用户Schema"""

    id: int
    name: str
    email: Optional[str] = None


class TestResponseBuilder:
    """测试ApiResponseBuilder"""

    def test_success_response_basic(self):
        """测试基本成功响应"""
        from app.core.response_builder import ApiResponseBuilder

        response = ApiResponseBuilder.success()

        assert response["code"] == 200
        assert response["message"] == "success"
        assert response["data"] is None
        assert "timestamp" in response
        assert isinstance(response["timestamp"], int)

    def test_success_response_with_data(self):
        """测试带数据的成功响应"""
        from app.core.response_builder import ApiResponseBuilder

        data = {"id": 1, "name": "测试"}
        response = ApiResponseBuilder.success(data=data)

        assert response["code"] == 200
        assert response["message"] == "success"
        assert response["data"] == data

    def test_success_response_with_custom_message(self):
        """测试自定义消息的成功响应"""
        from app.core.response_builder import ApiResponseBuilder

        response = ApiResponseBuilder.success(message="创建成功")

        assert response["code"] == 200
        assert response["message"] == "创建成功"

    def test_success_response_with_custom_code(self):
        """测试自定义状态码的成功响应"""
        from app.core.response_builder import ApiResponseBuilder

        response = ApiResponseBuilder.success(code=201, message="创建成功")

        assert response["code"] == 201
        assert response["message"] == "创建成功"

    def test_error_response(self):
        """测试错误响应"""
        from app.core.response_builder import ApiResponseBuilder

        response = ApiResponseBuilder.error(
            code=400, message="请求参数错误", detail="手机号格式不正确"
        )

        assert response["code"] == 400
        assert response["message"] == "请求参数错误"
        assert response["detail"] == "手机号格式不正确"
        assert "timestamp" in response

    def test_error_response_without_detail(self):
        """测试无详细信息的错误响应"""
        from app.core.response_builder import ApiResponseBuilder

        response = ApiResponseBuilder.error(code=404, message="用户不存在")

        assert response["code"] == 404
        assert response["message"] == "用户不存在"
        assert response["detail"] is None

    def test_paginated_response(self):
        """测试分页响应"""
        from app.core.response_builder import ApiResponseBuilder

        items = [{"id": 1}, {"id": 2}, {"id": 3}]
        response = ApiResponseBuilder.paginated(
            items=items, total=100, page=1, page_size=10
        )

        assert response["code"] == 200
        assert response["message"] == "success"
        assert response["data"]["items"] == items
        assert response["data"]["total"] == 100
        assert response["data"]["page"] == 1
        assert response["data"]["page_size"] == 10
        assert response["data"]["total_pages"] == 10

    def test_paginated_response_calculate_total_pages(self):
        """测试分页响应总页数计算"""
        from app.core.response_builder import ApiResponseBuilder

        # 测试有余数的情况
        response = ApiResponseBuilder.paginated(
            items=[], total=25, page=1, page_size=10
        )
        assert response["data"]["total_pages"] == 3

        # 测试整除的情况
        response = ApiResponseBuilder.paginated(
            items=[], total=30, page=1, page_size=10
        )
        assert response["data"]["total_pages"] == 3

        # 测试0条数据
        response = ApiResponseBuilder.paginated(items=[], total=0, page=1, page_size=10)
        assert response["data"]["total_pages"] == 0

    def test_from_model_with_pydantic_schema(self):
        """测试从模型转换为Pydantic Schema"""
        from app.core.response_builder import ApiResponseBuilder

        # 模拟模型对象
        class MockModel:
            def __init__(self, id, name, email):
                self.id = id
                self.name = name
                self.email = email

        model = MockModel(id=1, name="张三", email="zhangsan@example.com")
        response = ApiResponseBuilder.from_model(model, TestUserSchema)

        assert response["code"] == 200
        assert response["data"]["id"] == 1
        assert response["data"]["name"] == "张三"
        assert response["data"]["email"] == "zhangsan@example.com"

    def test_from_model_list(self):
        """测试从模型列表转换"""
        from app.core.response_builder import ApiResponseBuilder

        class MockModel:
            def __init__(self, id, name, email=None):
                self.id = id
                self.name = name
                self.email = email

        models = [
            MockModel(id=1, name="张三", email="zs@example.com"),
            MockModel(id=2, name="李四", email="ls@example.com"),
        ]

        response = ApiResponseBuilder.from_model(models, TestUserSchema)

        assert response["code"] == 200
        assert len(response["data"]) == 2
        assert response["data"][0]["id"] == 1
        assert response["data"][1]["id"] == 2

    def test_from_model_with_message(self):
        """测试从模型转换并自定义消息"""
        from app.core.response_builder import ApiResponseBuilder

        class MockModel:
            def __init__(self, id, name):
                self.id = id
                self.name = name

        model = MockModel(id=1, name="张三")
        response = ApiResponseBuilder.from_model(model, TestUserSchema, message="获取成功")

        assert response["message"] == "获取成功"

    def test_timestamp_format(self):
        """测试时间戳格式"""
        from app.core.response_builder import ApiResponseBuilder

        before = int(datetime.now().timestamp())
        response = ApiResponseBuilder.success()
        after = int(datetime.now().timestamp())

        assert before <= response["timestamp"] <= after
