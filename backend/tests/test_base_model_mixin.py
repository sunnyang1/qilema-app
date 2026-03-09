"""
BaseModelMixin单元测试
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional

import pytest
from pydantic import BaseModel


# 测试用的枚举
class StatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"


class TestBaseModelMixin:
    """测试BaseModelMixin"""

    def test_to_dict_basic(self):
        """测试基本to_dict功能"""
        from app.models.base_mixin import BaseModelMixin

        class TestModel(BaseModelMixin):
            def __init__(self):
                self.id = 1
                self.name = "测试"
                self.age = 25

        model = TestModel()
        result = model.to_dict()

        assert result["id"] == 1
        assert result["name"] == "测试"
        assert result["age"] == 25

    def test_to_dict_with_datetime(self):
        """测试to_dict处理datetime"""
        from app.models.base_mixin import BaseModelMixin

        class TestModel(BaseModelMixin):
            def __init__(self):
                self.id = 1
                self.created_at = datetime(2024, 1, 15, 10, 30, 0)

        model = TestModel()
        result = model.to_dict()

        assert result["created_at"] == "2024-01-15T10:30:00"

    def test_to_dict_with_date(self):
        """测试to_dict处理date"""
        from app.models.base_mixin import BaseModelMixin

        class TestModel(BaseModelMixin):
            def __init__(self):
                self.id = 1
                self.birth_date = date(1990, 5, 20)

        model = TestModel()
        result = model.to_dict()

        assert result["birth_date"] == "1990-05-20"

    def test_to_dict_with_enum(self):
        """测试to_dict处理enum"""
        from app.models.base_mixin import BaseModelMixin

        class TestModel(BaseModelMixin):
            def __init__(self):
                self.id = 1
                self.status = StatusEnum.ACTIVE
                self.gender = GenderEnum.MALE

        model = TestModel()
        result = model.to_dict()

        assert result["status"] == "active"
        assert result["gender"] == "male"

    def test_to_dict_with_none(self):
        """测试to_dict处理None值"""
        from app.models.base_mixin import BaseModelMixin

        class TestModel(BaseModelMixin):
            def __init__(self):
                self.id = 1
                self.name = None
                self.description = None

        model = TestModel()
        result = model.to_dict()

        assert result["id"] == 1
        assert result["name"] is None
        assert result["description"] is None

    def test_to_dict_exclude_fields(self):
        """测试to_dict排除字段"""
        from app.models.base_mixin import BaseModelMixin

        class TestModel(BaseModelMixin):
            def __init__(self):
                self.id = 1
                self.name = "测试"
                self.password = "secret"
                self.internal_field = "internal"

        model = TestModel()
        result = model.to_dict(exclude=["password", "internal_field"])

        assert result["id"] == 1
        assert result["name"] == "测试"
        assert "password" not in result
        assert "internal_field" not in result

    def test_to_dict_include_only(self):
        """测试to_dict只包含指定字段"""
        from app.models.base_mixin import BaseModelMixin

        class TestModel(BaseModelMixin):
            def __init__(self):
                self.id = 1
                self.name = "测试"
                self.age = 25
                self.email = "test@example.com"

        model = TestModel()
        result = model.to_dict(include=["id", "name"])

        assert result["id"] == 1
        assert result["name"] == "测试"
        assert "age" not in result
        assert "email" not in result

    def test_to_dict_exclude_private(self):
        """测试to_dict自动排除私有字段"""
        from app.models.base_mixin import BaseModelMixin

        class TestModel(BaseModelMixin):
            def __init__(self):
                self.id = 1
                self.name = "测试"
                self._private = "private"
                self.__very_private = "very_private"

        model = TestModel()
        result = model.to_dict()

        assert result["id"] == 1
        assert result["name"] == "测试"
        assert "_private" not in result
        assert "__very_private" not in result

    def test_to_dict_sqlalchemy_attrs(self):
        """测试to_dict排除SQLAlchemy内部属性"""
        from app.models.base_mixin import BaseModelMixin

        class TestModel(BaseModelMixin):
            def __init__(self):
                self.id = 1
                self.name = "测试"
                self._sa_instance_state = "sqlalchemy_state"

        model = TestModel()
        result = model.to_dict()

        assert result["id"] == 1
        assert result["name"] == "测试"
        assert "_sa_instance_state" not in result

    def test_to_schema(self):
        """测试to_schema方法"""
        from app.models.base_mixin import BaseModelMixin

        class UserSchema(BaseModel):
            id: int
            name: str
            email: Optional[str] = None

        class TestModel(BaseModelMixin):
            def __init__(self):
                self.id = 1
                self.name = "测试用户"
                self.email = "test@example.com"

        model = TestModel()
        schema = model.to_schema(UserSchema)

        assert schema.id == 1
        assert schema.name == "测试用户"
        assert schema.email == "test@example.com"

    def test_from_dict(self):
        """测试from_dict类方法"""
        from app.models.base_mixin import BaseModelMixin

        class TestModel(BaseModelMixin):
            def __init__(self):
                self.id = None
                self.name = None
                self.age = None

        data = {"id": 1, "name": "测试", "age": 25}
        model = TestModel.from_dict(data)

        assert model.id == 1
        assert model.name == "测试"
        assert model.age == 25

    def test_from_dict_with_datetime_string(self):
        """测试from_dict处理ISO格式日期字符串"""
        from app.models.base_mixin import BaseModelMixin

        class TestModel(BaseModelMixin):
            def __init__(self):
                self.id = 1
                self.created_at = None

        data = {"id": 1, "created_at": "2024-01-15T10:30:00"}
        model = TestModel.from_dict(data)

        assert model.id == 1
        assert isinstance(model.created_at, datetime)
        assert model.created_at.year == 2024

    def test_from_dict_with_date_string(self):
        """测试from_dict处理日期字符串"""
        from app.models.base_mixin import BaseModelMixin

        class TestModel(BaseModelMixin):
            def __init__(self):
                self.id = 1
                self.birth_date = None

        data = {"id": 1, "birth_date": "1990-05-20"}
        model = TestModel.from_dict(data)

        assert model.id == 1
        assert isinstance(model.birth_date, date)
        assert model.birth_date.year == 1990
