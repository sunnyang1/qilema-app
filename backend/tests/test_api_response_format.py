"""
测试统一API响应格式

验证响应Schema的正确性和一致性
"""

from app.schemas.common import (
    ApiResponse,
    ErrorResponse,
    SuccessResponse,
    error_response,
    paginated_response,
    success_response,
)


class TestApiResponse:
    """测试ApiResponse模型"""

    def test_basic_api_response(self):
        """测试基本的API响应"""
        response = ApiResponse(
            code=200, message="success", data={"id": 1, "name": "测试"}
        )

        assert response.code == 200
        assert response.message == "success"
        assert response.data == {"id": 1, "name": "测试"}
        assert isinstance(response.timestamp, int)
        assert response.timestamp > 0

    def test_api_response_with_defaults(self):
        """测试使用默认值的API响应"""
        response = ApiResponse()

        assert response.code == 200
        assert response.message == "success"
        assert response.data is None
        assert isinstance(response.timestamp, int)

    def test_api_response_serialization(self):
        """测试API响应序列化"""
        response = ApiResponse(code=200, message="success", data={"items": [1, 2, 3]})

        json_data = response.model_dump()
        assert json_data["code"] == 200
        assert json_data["message"] == "success"
        assert json_data["data"] == {"items": [1, 2, 3]}
        assert isinstance(json_data["timestamp"], int)

    def test_api_response_model_dump_json(self):
        """测试API响应JSON序列化"""
        response = ApiResponse(code=200, message="success", data={"test": "data"})

        json_str = response.model_dump_json()
        assert '"code":200' in json_str
        assert '"message":"success"' in json_str
        assert (
            '"data":{ "test":"data"}' in json_str
            or '"data":{"test":"data"}' in json_str
        )

    def test_api_response_with_none_data(self):
        """测试data为None的API响应"""
        response = ApiResponse(data=None)

        assert response.data is None
        assert response.code == 200


class TestErrorResponse:
    """测试ErrorResponse模型"""

    def test_basic_error_response(self):
        """测试基本的错误响应"""
        response = ErrorResponse(
            code=1001, message="该手机号已注册", detail="手机号: 13800138000"
        )

        assert response.code == 1001
        assert response.message == "该手机号已注册"
        assert response.detail == "手机号: 13800138000"
        assert isinstance(response.timestamp, int)

    def test_error_response_without_detail(self):
        """测试没有detail的错误响应"""
        response = ErrorResponse(code=404, message="用户不存在")

        assert response.code == 404
        assert response.message == "用户不存在"
        assert response.detail is None

    def test_error_response_validation_errors(self):
        """测试各种错误码的响应"""
        # 400 验证错误
        error_400 = ErrorResponse(code=400, message="参数验证失败")
        assert error_400.code == 400

        # 401 认证错误
        error_401 = ErrorResponse(code=401, message="未授权访问")
        assert error_401.code == 401

        # 404 未找到
        error_404 = ErrorResponse(code=404, message="资源不存在")
        assert error_404.code == 404

        # 500 服务器错误
        error_500 = ErrorResponse(code=500, message="服务器内部错误")
        assert error_500.code == 500

        # 1001 业务错误
        error_1001 = ErrorResponse(code=1001, message="用户已存在")
        assert error_1001.code == 1001


class TestSuccessResponse:
    """测试SuccessResponse模型"""

    def test_basic_success_response(self):
        """测试基本的成功响应"""
        response = SuccessResponse(message="操作成功", data={"id": 1, "name": "测试"})

        assert response.message == "操作成功"
        assert response.data == {"id": 1, "name": "测试"}
        assert isinstance(response.timestamp, int)

    def test_success_response_with_defaults(self):
        """测试使用默认值的成功响应"""
        response = SuccessResponse()

        assert response.message == "success"
        assert response.data is None
        assert isinstance(response.timestamp, int)

    def test_success_response_without_data(self):
        """测试没有data的成功响应"""
        response = SuccessResponse(message="删除成功")

        assert response.message == "删除成功"
        assert response.data is None


class TestSuccessResponseFunction:
    """测试success_response工具函数"""

    def test_success_response_with_data(self):
        """测试带数据的成功响应"""
        response = success_response(data={"id": 1, "name": "测试"}, message="操作成功")

        assert response["code"] == 200
        assert response["message"] == "操作成功"
        assert response["data"] == {"id": 1, "name": "测试"}
        assert isinstance(response["timestamp"], int)

    def test_success_response_with_defaults(self):
        """测试使用默认值的成功响应"""
        response = success_response()

        assert response["code"] == 200
        assert response["message"] == "success"
        assert response["data"] is None
        assert isinstance(response["timestamp"], int)

    def test_success_response_custom_code(self):
        """测试自定义响应码的成功响应"""
        response = success_response(data={"status": "ok"}, code=201)

        assert response["code"] == 201
        assert response["data"] == {"status": "ok"}

    def test_success_response_timestamp_increment(self):
        """测试时间戳递增"""
        import time

        response1 = success_response(data={"id": 1})
        time.sleep(0.01)  # 等待10ms
        response2 = success_response(data={"id": 2})

        assert response2["timestamp"] >= response1["timestamp"]


class TestPaginatedResponseFunction:
    """测试paginated_response工具函数"""

    def test_paginated_response_basic(self):
        """测试基本的分页响应"""
        items = [{"id": 1}, {"id": 2}, {"id": 3}]
        response = paginated_response(items=items, total=10, page=1, page_size=10)

        assert response["code"] == 200
        assert response["message"] == "success"
        assert response["data"]["items"] == items
        assert response["data"]["total"] == 10
        assert response["data"]["page"] == 1
        assert response["data"]["page_size"] == 10
        assert response["data"]["total_pages"] == 1

    def test_paginated_response_multiple_pages(self):
        """测试多页的分页响应"""
        items = [{"id": 1}, {"id": 2}]
        response = paginated_response(items=items, total=12, page=1, page_size=5)

        assert response["data"]["total"] == 12
        assert response["data"]["page"] == 1
        assert response["data"]["page_size"] == 5
        assert response["data"]["total_pages"] == 3  # ceil(12/5) = 3
        assert len(response["data"]["items"]) == 2

    def test_paginated_response_last_page(self):
        """测试最后一页的分页响应"""
        items = [{"id": 11}, {"id": 12}]
        response = paginated_response(items=items, total=12, page=3, page_size=5)

        assert response["data"]["page"] == 3
        assert response["data"]["total_pages"] == 3
        assert len(response["data"]["items"]) == 2

    def test_paginated_response_empty_items(self):
        """测试空数据的分页响应"""
        response = paginated_response(items=[], total=0, page=1, page_size=10)

        assert response["data"]["items"] == []
        assert response["data"]["total"] == 0
        assert response["data"]["total_pages"] == 0

    def test_paginated_response_custom_message(self):
        """测试自定义消息的分页响应"""
        response = paginated_response(
            items=[{"id": 1}], total=1, page=1, page_size=10, message="查询成功"
        )

        assert response["message"] == "查询成功"


class TestErrorResponseFunction:
    """测试error_response工具函数"""

    def test_error_response_basic(self):
        """测试基本的错误响应"""
        response = error_response(code=1001, message="用户已存在")

        assert response["code"] == 1001
        assert response["message"] == "用户已存在"
        assert response["detail"] is None
        assert isinstance(response["timestamp"], int)

    def test_error_response_with_detail(self):
        """测试带详细信息的错误响应"""
        response = error_response(
            code=400,
            message="参数验证失败",
            detail={"field": "phone", "error": "格式不正确"},
        )

        assert response["code"] == 400
        assert response["message"] == "参数验证失败"
        assert response["detail"] == {"field": "phone", "error": "格式不正确"}

    def test_error_response_different_codes(self):
        """测试不同错误码的响应"""
        # 业务错误码
        response_1001 = error_response(code=1001, message="用户已存在")
        assert response_1001["code"] == 1001

        # HTTP错误码
        response_404 = error_response(code=404, message="资源不存在")
        assert response_404["code"] == 404

        response_500 = error_response(code=500, message="服务器错误")
        assert response_500["code"] == 500


class TestResponseFormatConsistency:
    """测试响应格式一致性"""

    def test_all_responses_have_timestamp(self):
        """测试所有响应都有timestamp字段"""
        # ApiResponse
        api_resp = ApiResponse(data={"test": "data"})
        assert hasattr(api_resp, "timestamp")
        assert isinstance(api_resp.timestamp, int)

        # ErrorResponse
        error_resp = ErrorResponse(code=1001, message="error")
        assert hasattr(error_resp, "timestamp")
        assert isinstance(error_resp.timestamp, int)

        # SuccessResponse
        success_resp = SuccessResponse(data={"test": "data"})
        assert hasattr(success_resp, "timestamp")
        assert isinstance(success_resp.timestamp, int)

        # Functions
        success_func_resp = success_response()
        assert "timestamp" in success_func_resp
        assert isinstance(success_func_resp["timestamp"], int)

        error_func_resp = error_response(code=1001, message="error")
        assert "timestamp" in error_func_resp
        assert isinstance(error_func_resp["timestamp"], int)

        paginated_func_resp = paginated_response([], 0, 1, 10)
        assert "timestamp" in paginated_func_resp
        assert isinstance(paginated_func_resp["timestamp"], int)

    def test_error_codes_consistency(self):
        """测试错误码的一致性"""
        # 标准HTTP错误码
        standard_codes = [400, 401, 403, 404, 429, 500]

        for code in standard_codes:
            resp = error_response(code=code, message="测试")
            assert resp["code"] == code

        # 自定义业务错误码
        custom_codes = [1001, 1003, 1101, 1201, 1301, 1401]

        for code in custom_codes:
            resp = error_response(code=code, message="测试")
            assert resp["code"] == code
