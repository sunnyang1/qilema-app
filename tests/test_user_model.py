"""
User模型单元测试 - 测试重构后的to_dict方法
"""
import pytest
from datetime import datetime
from app.models.user import User, GenderEnum, BloodTypeEnum


class TestUserModel:
    """测试User模型"""

    def test_user_to_dict_basic(self):
        """测试基本的to_dict功能"""
        user = User()
        user.user_id = "user-123"
        user.phone = "13800138000"
        user.nickname = "测试用户"
        user.password_hash = "hashed_password"
        user.gender = GenderEnum.MALE
        user.blood_type = BloodTypeEnum.A
        user.height = 175
        user.weight = 70
        
        result = user.to_dict()
        
        assert result["user_id"] == "user-123"
        assert result["phone"] == "13800138000"
        assert result["nickname"] == "测试用户"
        assert result["gender"] == "1"  # Enum转换为value
        assert result["blood_type"] == "A"
        assert result["height"] == 175
        assert result["weight"] == 70

    def test_user_to_dict_excludes_password(self):
        """测试to_dict默认排除password_hash字段"""
        user = User()
        user.user_id = "user-123"
        user.phone = "13800138000"
        user.password_hash = "secret_hash"
        user.nickname = "测试用户"
        
        result = user.to_dict()
        
        # password_hash不应该在结果中
        assert "password_hash" not in result
        assert "password" not in result

    def test_user_to_dict_with_datetime(self):
        """测试to_dict处理datetime字段"""
        user = User()
        user.user_id = "user-123"
        user.phone = "13800138000"
        user.created_at = datetime(2024, 1, 15, 10, 30, 0)
        user.updated_at = datetime(2024, 1, 16, 12, 0, 0)
        user.last_sign_in = datetime(2024, 1, 20, 8, 0, 0)
        user.birth_date = datetime(1990, 5, 20, 0, 0, 0)
        
        result = user.to_dict()
        
        assert result["created_at"] == "2024-01-15T10:30:00"
        assert result["updated_at"] == "2024-01-16T12:00:00"
        assert result["last_sign_in"] == "2024-01-20T08:00:00"
        assert result["birth_date"] == "1990-05-20T00:00:00"

    def test_user_to_dict_with_none_values(self):
        """测试to_dict处理None值"""
        user = User()
        user.user_id = "user-123"
        user.phone = "13800138000"
        user.nickname = None
        user.gender = None
        user.blood_type = None
        user.birth_date = None
        user.height = None
        user.weight = None
        user.last_sign_in = None
        
        result = user.to_dict()
        
        assert result["nickname"] is None
        assert result["gender"] is None
        assert result["blood_type"] is None
        assert result["birth_date"] is None
        assert result["height"] is None
        assert result["weight"] is None
        assert result["last_sign_in"] is None

    def test_user_to_dict_with_enum_unknown(self):
        """测试to_dict处理Unknown枚举值"""
        user = User()
        user.user_id = "user-123"
        user.phone = "13800138000"
        user.gender = GenderEnum.UNKNOWN
        user.blood_type = BloodTypeEnum.UNKNOWN
        
        result = user.to_dict()
        
        assert result["gender"] == "0"
        assert result["blood_type"] == "UNKNOWN"

    def test_user_to_dict_excludes_sqlalchemy_attrs(self):
        """测试to_dict排除SQLAlchemy内部属性"""
        user = User()
        user.user_id = "user-123"
        user.phone = "13800138000"
        
        result = user.to_dict()
        
        # SQLAlchemy内部属性不应该在结果中
        assert "_sa_instance_state" not in result

    def test_user_to_dict_include_fields(self):
        """测试to_dict使用include参数只包含指定字段"""
        user = User()
        user.user_id = "user-123"
        user.phone = "13800138000"
        user.nickname = "测试用户"
        user.height = 175
        user.weight = 70
        
        result = user.to_dict(include=["user_id", "nickname"])
        
        assert result["user_id"] == "user-123"
        assert result["nickname"] == "测试用户"
        assert "phone" not in result
        assert "height" not in result
        assert "weight" not in result

    def test_user_to_dict_exclude_additional_fields(self):
        """测试to_dict使用exclude参数排除额外字段"""
        user = User()
        user.user_id = "user-123"
        user.phone = "13800138000"
        user.nickname = "测试用户"
        user.height = 175
        user.weight = 70
        
        result = user.to_dict(exclude=["height", "weight"])
        
        assert result["user_id"] == "user-123"
        assert result["phone"] == "13800138000"
        assert result["nickname"] == "测试用户"
        assert "height" not in result
        assert "weight" not in result
        # password_hash默认就被排除了
        assert "password_hash" not in result

    def test_user_to_dict_output_format_backward_compatible(self):
        """测试to_dict输出格式向后兼容"""
        user = User()
        user.user_id = "user-123"
        user.phone = "13800138000"
        user.nickname = "测试用户"
        user.gender = GenderEnum.MALE
        user.blood_type = BloodTypeEnum.O
        user.height = 175
        user.weight = 70
        user.birth_date = None
        user.created_at = datetime(2024, 1, 15, 10, 30, 0)
        user.updated_at = datetime(2024, 1, 16, 12, 0, 0)
        user.last_sign_in = None
        
        result = user.to_dict()
        
        # 验证所有预期的字段都存在且格式正确
        assert "user_id" in result
        assert "phone" in result
        assert "nickname" in result
        assert "gender" in result
        assert "birth_date" in result
        assert "blood_type" in result
        assert "height" in result
        assert "weight" in result
        assert "created_at" in result
        assert "updated_at" in result
        assert "last_sign_in" in result
        
        # 验证格式
        assert isinstance(result["user_id"], str)
        assert isinstance(result["phone"], str)
        assert result["gender"] in ["0", "1", "2", None]  # Enum value或None
        assert result["blood_type"] in ["A", "B", "O", "AB", "UNKNOWN", None]
