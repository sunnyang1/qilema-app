"""
BaseSchema 单元测试
"""

from datetime import datetime
from typing import Optional

import pytest
from app.core.schemas import (
    BaseSchema,
    ErrorResponse,
    ListResponse,
    PaginationResponse,
    SuccessResponse,
    TimestampMixin,
)


# 测试用的模拟ORM对象
class MockUser:
    """模拟用户ORM对象"""

    def __init__(self, id, phone, nickname=None):
        self.id = id
        self.phone = phone
        self.nickname = nickname
        self.created_at = datetime(2024, 1, 1, 12, 0, 0)
        self.updated_at = datetime(2024, 1, 2, 12, 0, 0)


# 测试用的Schema实现
class UserResponse(BaseSchema):
    """用户响应Schema - 继承BaseSchema并实现from_orm"""

    user_id: str
    phone: str
    nickname: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    @classmethod
    def from_orm(cls, user: MockUser) -> "UserResponse":
        """从MockUser对象转换为UserResponse"""
        return cls(
            user_id=str(user.id),
            phone=user.phone,
            nickname=user.nickname,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class TestBaseSchema:
    """BaseSchema基类测试"""

    def test_schema_inherits_from_base_schema(self):
        """测试Schema正确继承BaseSchema"""
        assert issubclass(UserResponse, BaseSchema)

    def test_schema_has_model_config(self):
        """测试Schema有正确的model_config"""
        assert hasattr(UserResponse, "model_config")
        assert UserResponse.model_config["from_attributes"] is True

    def test_from_orm_converts_single_object(self):
        """测试from_orm转换单个对象"""
        mock_user = MockUser(id=1, phone="13800138000", nickname="测试用户")
        user_response = UserResponse.from_orm(mock_user)

        assert isinstance(user_response, UserResponse)
        assert user_response.user_id == "1"
        assert user_response.phone == "13800138000"
        assert user_response.nickname == "测试用户"
        assert isinstance(user_response.created_at, datetime)

    def test_from_orm_list_converts_multiple_objects(self):
        """测试from_orm_list转换对象列表"""
        mock_users = [
            MockUser(id=1, phone="13800138000", nickname="用户1"),
            MockUser(id=2, phone="13800138001", nickname="用户2"),
            MockUser(id=3, phone="13800138002", nickname=None),
        ]
        user_responses = UserResponse.from_orm_list(mock_users)

        assert len(user_responses) == 3
        assert all(isinstance(u, UserResponse) for u in user_responses)
        assert user_responses[0].nickname == "用户1"
        assert user_responses[1].nickname == "用户2"
        assert user_responses[2].nickname is None

    def test_safe_from_orm_converts_valid_object(self):
        """测试safe_from_orm转换有效对象"""
        mock_user = MockUser(id=1, phone="13800138000")
        user_response = UserResponse.safe_from_orm(mock_user)

        assert isinstance(user_response, UserResponse)
        assert user_response.user_id == "1"

    def test_safe_from_orm_returns_default_on_none(self):
        """测试safe_from_orm对None返回默认值"""
        user_response = UserResponse.safe_from_orm(None, default="default")

        assert user_response == "default"

    def test_safe_from_orm_handles_exception(self):
        """测试safe_from_orm处理异常"""

        # 创建一个会导致异常的对象
        class BadUser:
            pass

        bad_user = BadUser()
        user_response = UserResponse.safe_from_orm(bad_user, default="error")

        assert user_response == "error"

    def test_from_orm_abstract_method_raises_error(self):
        """测试未实现的from_orm方法会抛出错误"""

        class IncompleteSchema(BaseSchema):
            name: str

        # 这个类没有实现from_orm方法，应该会失败
        with pytest.raises(NotImplementedError):
            IncompleteSchema.from_orm(MockUser(id=1, phone="13800138000"))


class TestTimestampMixin:
    """TimestampMixin测试"""

    def test_timestamp_mixin_has_fields(self):
        """测试TimestampMixin有正确的时间字段"""

        class TimestampedSchema(TimestampMixin):
            name: str

        schema = TimestampedSchema(
            name="test",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 2, 12, 0, 0),
        )

        assert schema.created_at == datetime(2024, 1, 1, 12, 0, 0)
        assert schema.updated_at == datetime(2024, 1, 2, 12, 0, 0)

    def test_timestamp_mixin_updated_at_optional(self):
        """测试updated_at字段是可选的"""

        class TimestampedSchema(TimestampMixin):
            name: str

        schema = TimestampedSchema(
            name="test", created_at=datetime(2024, 1, 1, 12, 0, 0), updated_at=None
        )

        assert schema.updated_at is None


class TestPaginationResponse:
    """PaginationResponse测试"""

    def test_pagination_response_fields(self):
        """测试PaginationResponse字段验证"""
        pagination = PaginationResponse(total=100, page=1, page_size=20, total_pages=5)

        assert pagination.total == 100
        assert pagination.page == 1
        assert pagination.page_size == 20
        assert pagination.total_pages == 5

    def test_pagination_response_validation(self):
        """测试PaginationResponse字段验证"""
        with pytest.raises(Exception):  # page < 1 应该失败
            PaginationResponse(total=100, page=0, page_size=20, total_pages=5)

        with pytest.raises(Exception):  # page_size > 100 应该失败
            PaginationResponse(total=100, page=1, page_size=101, total_pages=1)


class TestListResponse:
    """ListResponse测试"""

    def test_list_response_default_values(self):
        """测试ListResponse默认值"""
        response = ListResponse[UserResponse]()

        assert response.items == []
        assert response.total == 0
        assert response.page == 1
        assert response.page_size == 20

    def test_list_response_with_data(self):
        """测试ListResponse包含数据"""
        items = [
            UserResponse(
                user_id="1",
                phone="13800138000",
                nickname="用户1",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            UserResponse(
                user_id="2",
                phone="13800138001",
                nickname="用户2",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]

        response = ListResponse[UserResponse](
            items=items, total=2, page=1, page_size=20
        )

        assert len(response.items) == 2
        assert response.total == 2
        assert response.page == 1


class TestSuccessResponse:
    """SuccessResponse测试"""

    def test_success_response_default(self):
        """测试SuccessResponse默认值"""
        response = SuccessResponse()

        assert response.success is True
        assert response.message == "操作成功"
        assert response.data is None

    def test_success_response_custom(self):
        """测试SuccessResponse自定义值"""
        response = SuccessResponse(message="创建成功", data={"id": 1})

        assert response.success is True
        assert response.message == "创建成功"
        assert response.data == {"id": 1}


class TestErrorResponse:
    """ErrorResponse测试"""

    def test_error_response_required_fields(self):
        """测试ErrorResponse必填字段"""
        with pytest.raises(Exception):  # 缺少error字段
            ErrorResponse(message="错误消息")

        with pytest.raises(Exception):  # 缺少message字段
            ErrorResponse(error="ValidationError")

    def test_error_response_with_details(self):
        """测试ErrorResponse包含详情"""
        response = ErrorResponse(
            error="ValidationError",
            message="字段验证失败",
            details={"field": "phone", "reason": "格式不正确"},
        )

        assert response.success is False
        assert response.error == "ValidationError"
        assert response.message == "字段验证失败"
        assert response.details == {"field": "phone", "reason": "格式不正确"}

    def test_error_response_without_details(self):
        """测试ErrorResponse不包含详情"""
        response = ErrorResponse(error="ServerError", message="服务器内部错误")

        assert response.success is False
        assert response.error == "ServerError"
        assert response.message == "服务器内部错误"
        assert response.details is None


class TestUserResponseSerialization:
    """UserResponse 序列化测试"""

    def test_user_response_from_real_user_model(self):
        """测试从真实 User ORM 对象序列化"""
        from app.models.user import User
        from app.schemas.user import BloodTypeEnum, GenderEnum, UserResponse

        # 创建一个模拟的 User 对象
        user = User()
        user.user_id = "test-user-001"
        user.phone = "13800138000"
        user.nickname = "测试用户"
        user.gender = GenderEnum.MALE
        user.birth_date = datetime(1990, 1, 1, 0, 0, 0)
        user.blood_type = BloodTypeEnum.A
        user.height = 175
        user.weight = 70
        user.created_at = datetime(2024, 1, 1, 12, 0, 0)
        user.updated_at = datetime(2024, 1, 2, 12, 0, 0)
        user.last_sign_in = datetime(2024, 1, 3, 8, 0, 0)

        # 使用 Pydantic 的 model_validate 方法序列化
        user_response = UserResponse.model_validate(user)

        # 验证所有字段都正确序列化
        assert user_response.user_id == "test-user-001"
        assert user_response.phone == "13800138000"
        assert user_response.nickname == "测试用户"
        assert user_response.gender == GenderEnum.MALE
        assert user_response.birth_date == datetime(1990, 1, 1, 0, 0, 0)
        assert user_response.blood_type == BloodTypeEnum.A
        assert user_response.height == 175
        assert user_response.weight == 70
        assert user_response.created_at == datetime(2024, 1, 1, 12, 0, 0)
        assert user_response.updated_at == datetime(2024, 1, 2, 12, 0, 0)
        assert user_response.last_sign_in == datetime(2024, 1, 3, 8, 0, 0)

    def test_user_response_excludes_password_hash(self):
        """测试 UserResponse 不包含敏感字段 password_hash"""
        from app.models.user import User
        from app.schemas.user import BloodTypeEnum, GenderEnum, UserResponse

        user = User()
        user.user_id = "test-user-002"
        user.phone = "13800138001"
        user.password_hash = "hashed_password_123"  # 敏感字段
        user.nickname = "用户2"
        user.gender = GenderEnum.FEMALE
        user.blood_type = BloodTypeEnum.UNKNOWN  # 设置默认值
        user.created_at = datetime.now()

        user_response = UserResponse.model_validate(user)

        # 确保敏感字段不在响应中
        assert not hasattr(user_response, "password_hash")
        # 确保其他字段正常
        assert user_response.user_id == "test-user-002"
        assert user_response.phone == "13800138001"

    def test_user_response_handles_optional_fields(self):
        """测试 UserResponse 正确处理可选字段"""
        from app.models.user import User
        from app.schemas.user import BloodTypeEnum, GenderEnum, UserResponse

        user = User()
        user.user_id = "test-user-003"
        user.phone = "13800138002"
        user.nickname = None  # 可选字段为空
        user.gender = GenderEnum.UNKNOWN
        user.birth_date = None  # 可选字段为空
        user.blood_type = BloodTypeEnum.UNKNOWN
        user.height = None  # 可选字段为空
        user.weight = None  # 可选字段为空
        user.created_at = datetime.now()
        user.updated_at = None  # 可选字段为空
        user.last_sign_in = None  # 可选字段为空

        user_response = UserResponse.model_validate(user)

        assert user_response.user_id == "test-user-003"
        assert user_response.nickname is None
        assert user_response.birth_date is None
        assert user_response.height is None
        assert user_response.weight is None
        assert user_response.updated_at is None
        assert user_response.last_sign_in is None

    def test_user_response_enum_serialization(self):
        """测试枚举类型的序列化"""
        from app.models.user import User
        from app.schemas.user import BloodTypeEnum, GenderEnum, UserResponse

        # 测试所有性别枚举值
        for gender in [GenderEnum.UNKNOWN, GenderEnum.MALE, GenderEnum.FEMALE]:
            user = User()
            user.user_id = f"user-{gender.value}"
            user.phone = "13800138003"
            user.gender = gender
            user.blood_type = BloodTypeEnum.UNKNOWN  # 设置默认值
            user.created_at = datetime.now()

            user_response = UserResponse.model_validate(user)
            assert user_response.gender == gender
            assert isinstance(user_response.gender, GenderEnum)

        # 测试所有血型枚举值
        for blood_type in [
            BloodTypeEnum.A,
            BloodTypeEnum.B,
            BloodTypeEnum.O,
            BloodTypeEnum.AB,
            BloodTypeEnum.UNKNOWN,
        ]:
            user = User()
            user.user_id = f"user-{blood_type.value}"
            user.phone = "13800138004"
            user.gender = GenderEnum.UNKNOWN  # 设置默认值
            user.blood_type = blood_type
            user.created_at = datetime.now()

            user_response = UserResponse.model_validate(user)
            assert user_response.blood_type == blood_type
            assert isinstance(user_response.blood_type, BloodTypeEnum)

    def test_user_response_serialization_to_json(self):
        """测试序列化为 JSON"""
        import json

        from app.models.user import User
        from app.schemas.user import BloodTypeEnum, GenderEnum, UserResponse

        user = User()
        user.user_id = "test-user-004"
        user.phone = "13800138005"
        user.nickname = "JSON测试用户"
        user.gender = GenderEnum.FEMALE
        user.birth_date = datetime(1995, 5, 15, 0, 0, 0)
        user.blood_type = BloodTypeEnum.O
        user.created_at = datetime(2024, 1, 1, 12, 0, 0)

        user_response = UserResponse.model_validate(user)

        # 转换为 JSON
        json_str = user_response.model_dump_json()
        json_data = json.loads(json_str)

        # 验证 JSON 数据
        assert json_data["user_id"] == "test-user-004"
        assert json_data["phone"] == "13800138005"
        assert json_data["nickname"] == "JSON测试用户"
        assert json_data["gender"] == "2"  # GenderEnum.FEMALE 的值
        assert json_data["blood_type"] == "O"
        assert "password_hash" not in json_data  # 确保敏感字段不在 JSON 中
