"""
模型字段验证测试

测试 Batch 5 中添加的 @validates 验证器
"""

import pytest

from app.models.checkin import CheckIn
from app.models.user import User


class TestUserValidations:
    """User 模型字段验证测试"""

    def test_valid_phone(self):
        """测试有效的手机号"""
        valid_phones = [
            "13800138000",
            "13912345678",
            "15000000000",
            "18999999999",
            "13666666666",
        ]
        for phone in valid_phones:
            user = User(user_id=f"test_{phone}", phone=phone, password_hash="secret")
            assert user.phone == phone

    def test_invalid_phone(self):
        """测试无效的手机号"""
        # 无效格式的手机号
        invalid_phones = [
            "1380013800",  # 10位
            "138001380000",  # 12位
            "23800138000",  # 不以1开头
            "10800138000",  # 第二位为0
            "1380013800a",  # 包含字母
            "138-0013-8000",  # 包含分隔符
        ]
        for phone in invalid_phones:
            with pytest.raises(ValueError, match="无效的手机号格式"):
                User(user_id="test", phone=phone, password_hash="secret")

    def test_empty_phone(self):
        """测试空手机号"""
        with pytest.raises(ValueError, match="手机号不能为空"):
            User(user_id="test", phone="", password_hash="secret")

    def test_nickname_length_validation(self):
        """测试昵称长度验证"""
        # 有效长度
        user = User(
            user_id="test1",
            phone="13800138000",
            password_hash="secret",
            nickname="A" * 50,
        )
        assert len(user.nickname) == 50

        # 超过长度限制
        with pytest.raises(ValueError, match="昵称长度不能超过50个字符"):
            User(
                user_id="test2",
                phone="13800138001",
                password_hash="secret",
                nickname="A" * 51,
            )

    def test_height_range_validation(self):
        """测试身高范围验证"""
        # 有效范围
        for height in [50, 100, 200, 300]:
            user = User(
                user_id=f"test_h{height}",
                phone=f"138001380{height % 100:02d}",
                password_hash="secret",
                height=height,
            )
            assert user.height == height

        # 无效范围
        with pytest.raises(ValueError, match="身高必须在50-300cm之间"):
            User(
                user_id="test_tall",
                phone="13800138002",
                password_hash="secret",
                height=400,
            )

        with pytest.raises(ValueError, match="身高必须在50-300cm之间"):
            User(
                user_id="test_short",
                phone="13800138003",
                password_hash="secret",
                height=30,
            )

    def test_weight_range_validation(self):
        """测试体重范围验证"""
        # 有效范围
        for weight in [20, 50, 100, 500]:
            user = User(
                user_id=f"test_w{weight}",
                phone=f"138001380{weight % 100:02d}",
                password_hash="secret",
                weight=weight,
            )
            assert user.weight == weight

        # 无效范围
        with pytest.raises(ValueError, match="体重必须在20-500kg之间"):
            User(
                user_id="test_heavy",
                phone="13800138004",
                password_hash="secret",
                weight=600,
            )

        with pytest.raises(ValueError, match="体重必须在20-500kg之间"):
            User(
                user_id="test_light",
                phone="13800138005",
                password_hash="secret",
                weight=10,
            )

    def test_optional_fields_none(self):
        """测试可选字段为 None 时通过验证"""
        user = User(
            user_id="test_optional",
            phone="13800138000",
            password_hash="secret",
            nickname=None,
            height=None,
            weight=None,
        )
        assert user.nickname is None
        assert user.height is None
        assert user.weight is None


class TestCheckInValidations:
    """CheckIn 模型字段验证测试"""

    def test_valid_checkin_date(self):
        """测试有效的签到日期格式"""
        valid_dates = [
            "2024-01-15",
            "2024-12-31",
            "2024-02-29",  # 闰年
            "2023-06-30",
        ]
        for date in valid_dates:
            checkin = CheckIn(user_id="test", checkin_date=date)
            assert checkin.checkin_date == date

    def test_invalid_checkin_date(self):
        """测试无效的签到日期格式"""
        invalid_dates = [
            "2024/01/15",  # 错误分隔符
            "15-01-2024",  # 日-月-年格式
            "2024-1-15",  # 月份没有前导零
            "2024-01",  # 缺少日
            "invalid",
        ]
        for date in invalid_dates:
            with pytest.raises(ValueError, match="无效的日期格式"):
                CheckIn(user_id="test", checkin_date=date)

    def test_empty_checkin_date(self):
        """测试空的签到日期"""
        with pytest.raises(ValueError, match="签到日期不能为空"):
            CheckIn(user_id="test", checkin_date="")

    def test_valid_checkin_method(self):
        """测试有效的签到方式"""
        valid_methods = ["manual", "auto", "device", "app"]
        for method in valid_methods:
            checkin = CheckIn(
                user_id="test", checkin_date="2024-01-15", checkin_method=method
            )
            assert checkin.checkin_method == method

    def test_invalid_checkin_method(self):
        """测试无效的签到方式"""
        with pytest.raises(ValueError, match="无效的签到方式"):
            CheckIn(
                user_id="test",
                checkin_date="2024-01-15",
                checkin_method="invalid_method",
            )

    def test_valid_status(self):
        """测试有效的签到状态"""
        valid_statuses = ["active", "missed", "late", "early", "disabled"]
        for status in valid_statuses:
            checkin = CheckIn(user_id="test", checkin_date="2024-01-15", status=status)
            assert checkin.status == status

    def test_invalid_status(self):
        """测试无效的签到状态"""
        with pytest.raises(ValueError, match="无效的状态"):
            CheckIn(user_id="test", checkin_date="2024-01-15", status="invalid_status")

    def test_notes_length_validation(self):
        """测试备注长度验证"""
        # 有效长度
        checkin = CheckIn(
            user_id="test",
            checkin_date="2024-01-15",
            notes="A" * 200,
        )
        assert len(checkin.notes) == 200

        # 超过长度限制
        with pytest.raises(ValueError, match="备注长度不能超过200个字符"):
            CheckIn(
                user_id="test",
                checkin_date="2024-01-15",
                notes="A" * 201,
            )


class TestToDictIncludeRelations:
    """to_dict() include_relations 参数测试"""

    def test_default_to_dict_excludes_relations(self):
        """测试默认 to_dict 排除所有关联关系"""
        user = User(user_id="test", phone="13800138000", password_hash="secret")
        result = user.to_dict()

        # 关联关系应该被排除
        assert "emergency_contacts" not in result
        assert "checkins" not in result
        assert "notifications" not in result

    def test_to_dict_with_include_relations(self):
        """测试 to_dict 包含指定的关联关系"""
        user = User(user_id="test", phone="13800138000", password_hash="secret")

        # 包含 emergency_contacts
        result = user.to_dict(include_relations=["emergency_contacts"])
        assert "emergency_contacts" in result
        assert "checkins" not in result  # 其他关系仍然被排除

        # 包含多个关系
        result = user.to_dict(
            include_relations=["emergency_contacts", "checkins", "notifications"]
        )
        assert "emergency_contacts" in result
        assert "checkins" in result
        assert "notifications" in result

    def test_to_dict_empty_include_relations(self):
        """测试空的 include_relations 列表"""
        user = User(user_id="test", phone="13800138000", password_hash="secret")
        result = user.to_dict(include_relations=[])

        # 所有关联关系应该被排除
        assert "emergency_contacts" not in result
        assert "checkins" not in result

    def test_to_dict_nonexistent_relation(self):
        """测试包含不存在的关联关系"""
        user = User(user_id="test", phone="13800138000", password_hash="secret")

        # 不应该抛出异常
        result = user.to_dict(include_relations=["nonexistent_relation"])
        assert isinstance(result, dict)


class TestUserDynamicRelations:
    """User 动态关系测试"""

    def test_dynamic_relations_defined(self):
        """测试 _DYNAMIC_RELATIONS 已定义"""
        assert hasattr(User, "_DYNAMIC_RELATIONS")
        expected_relations = {
            "notifications",
            "medication_reminder_notifications",
            "medication_reminder_logs",
        }
        assert User._DYNAMIC_RELATIONS == expected_relations

    def test_relationship_loading_strategies(self):
        """测试关联关系加载策略"""
        # joined 策略
        assert User.alert_settings.property.lazy == "joined"
        assert User.health_record.property.lazy == "joined"

        # select 策略 (修复后)
        assert User.checkins.property.lazy == "select"
        assert User.login_records.property.lazy == "select"

        # dynamic 策略
        assert User.notifications.property.lazy == "dynamic"
