"""
健康档案 Schema 单元测试

测试 HealthRecordResponse, MedicalHistoryResponse, MedicationResponse, AllergyResponse 的序列化逻辑
"""

import pytest
from datetime import datetime
from app.schemas.health_record import (
    HealthRecordResponse,
    MedicalHistoryResponse,
    MedicationResponse,
    AllergyResponse,
    HealthRecordCreate,
    HealthRecordUpdate,
)


# 模拟 ORM 对象
class MockHealthRecord:
    """模拟 HealthRecord ORM 对象"""
    def __init__(self):
        self.id = 1
        self.user_id = "user123"
        self.real_name = "张三"
        self.gender = "男"
        self.blood_type = "A"
        self.height = 175.0
        self.weight = 70.0
        self.age = 30
        self.emergency_contact_name = "李四"
        self.emergency_contact_phone = "13800138000"
        self.emergency_contact_relation = "配偶"
        self.is_encrypted = 0
        self.created_at = datetime(2024, 1, 1, 12, 0, 0)
        self.updated_at = datetime(2024, 1, 2, 12, 0, 0)
        self.medical_histories = []
        self.medications = []
        self.allergies = []


class MockMedicalHistory:
    """模拟 MedicalHistory ORM 对象"""
    def __init__(self):
        self.id = 1
        self.health_record_id = 1
        self.disease_name = "高血压"
        self.diagnosis_date = datetime(2023, 1, 1, 0, 0, 0)
        self.description = "慢性高血压"
        self.severity = "中等"
        self.is_chronic = 1
        self.created_at = datetime(2023, 1, 1, 0, 0, 0)
        self.updated_at = datetime(2023, 1, 1, 0, 0, 0)


class MockMedication:
    """模拟 Medication ORM 对象"""
    def __init__(self):
        self.id = 1
        self.health_record_id = 1
        self.drug_name = "阿司匹林"
        self.dosage = "100mg"
        self.frequency = "每日一次"
        self.start_date = datetime(2023, 1, 1, 0, 0, 0)
        self.end_date = None
        self.is_current = 1
        self.notes = "餐后服用"
        self.created_at = datetime(2023, 1, 1, 0, 0, 0)
        self.updated_at = datetime(2023, 1, 1, 0, 0, 0)


class MockAllergy:
    """模拟 Allergy ORM 对象"""
    def __init__(self):
        self.id = 1
        self.health_record_id = 1
        self.allergen = "青霉素"
        self.allergic_reaction = "皮疹"
        self.severity = "严重"
        self.discovered_date = datetime(2022, 1, 1, 0, 0, 0)
        self.notes = "避免使用"
        self.created_at = datetime(2022, 1, 1, 0, 0, 0)
        self.updated_at = datetime(2022, 1, 1, 0, 0, 0)


class TestHealthRecordResponse:
    """HealthRecordResponse 序列化测试"""

    def test_serialize_complete_health_record(self):
        """测试序列化完整的健康档案"""
        mock_record = MockHealthRecord()
        response = HealthRecordResponse.model_validate(mock_record)
        data = response.model_dump()

        assert data["id"] == 1
        assert data["user_id"] == "user123"
        assert data["real_name"] == "张三"
        assert data["gender"] == "男"
        assert data["blood_type"] == "A"
        assert data["height"] == 175.0
        assert data["weight"] == 70.0
        assert data["age"] == 30
        assert data["emergency_contact_name"] == "李四"
        assert data["emergency_contact_phone"] == "13800138000"
        assert data["emergency_contact_relation"] == "配偶"
        assert data["is_encrypted"] == 0
        assert data["created_at"] is not None
        assert data["updated_at"] is not None

    def test_serialize_with_optional_fields_null(self):
        """测试序列化时可选字段为 None"""
        class MockHealthRecordPartial:
            def __init__(self):
                self.id = 1
                self.user_id = "user123"
                self.real_name = "张三"
                self.gender = "男"
                self.blood_type = None
                self.height = None
                self.weight = None
                self.age = None
                self.emergency_contact_name = None
                self.emergency_contact_phone = None
                self.emergency_contact_relation = None
                self.is_encrypted = 0
                self.created_at = datetime(2024, 1, 1, 12, 0, 0)
                self.updated_at = None

        mock_record = MockHealthRecordPartial()
        response = HealthRecordResponse.model_validate(mock_record)
        data = response.model_dump()

        assert data["blood_type"] is None
        assert data["height"] is None
        assert data["weight"] is None
        assert data["age"] is None
        assert data["emergency_contact_name"] is None
        assert data["emergency_contact_phone"] is None
        assert data["emergency_contact_relation"] is None
        assert data["updated_at"] is None


class TestMedicalHistoryResponse:
    """MedicalHistoryResponse 序列化测试"""

    def test_serialize_medical_history(self):
        """测试序列化病史记录"""
        mock_history = MockMedicalHistory()
        response = MedicalHistoryResponse.model_validate(mock_history)
        data = response.model_dump()

        assert data["id"] == 1
        assert data["health_record_id"] == 1
        assert data["disease_name"] == "高血压"
        assert data["diagnosis_date"] is not None
        assert data["description"] == "慢性高血压"
        assert data["severity"] == "中等"
        assert data["is_chronic"] == 1
        assert data["created_at"] is not None


class TestMedicationResponse:
    """MedicationResponse 序列化测试"""

    def test_serialize_medication(self):
        """测试序列化用药信息"""
        mock_medication = MockMedication()
        response = MedicationResponse.model_validate(mock_medication)
        data = response.model_dump()

        assert data["id"] == 1
        assert data["health_record_id"] == 1
        assert data["drug_name"] == "阿司匹林"
        assert data["dosage"] == "100mg"
        assert data["frequency"] == "每日一次"
        assert data["start_date"] is not None
        assert data["end_date"] is None
        assert data["is_current"] == 1
        assert data["notes"] == "餐后服用"
        assert data["created_at"] is not None


class TestAllergyResponse:
    """AllergyResponse 序列化测试"""

    def test_serialize_allergy(self):
        """测试序列化过敏史"""
        mock_allergy = MockAllergy()
        response = AllergyResponse.model_validate(mock_allergy)
        data = response.model_dump()

        assert data["id"] == 1
        assert data["health_record_id"] == 1
        assert data["allergen"] == "青霉素"
        assert data["allergic_reaction"] == "皮疹"
        assert data["severity"] == "严重"
        assert data["discovered_date"] is not None
        assert data["notes"] == "避免使用"
        assert data["created_at"] is not None


class TestHealthRecordCreate:
    """HealthRecordCreate 验证测试"""

    def test_valid_health_record_create(self):
        """测试有效的健康档案创建数据"""
        data = HealthRecordCreate(
            user_id="user123",
            real_name="张三",
            gender="男",
            blood_type="A",
            height=175.0,
            weight=70.0,
            age=30
        )
        assert data.user_id == "user123"
        assert data.real_name == "张三"
        assert data.gender == "男"

    def test_gender_validation_invalid(self):
        """测试性别验证 - 无效值"""
        with pytest.raises(ValueError) as exc_info:
            HealthRecordCreate(
                user_id="user123",
                real_name="张三",
                gender="unknown"  # 无效值
            )
        assert "性别必须是男、女或其他" in str(exc_info.value)

    def test_blood_type_validation_invalid(self):
        """测试血型验证 - 无效值"""
        with pytest.raises(ValueError) as exc_info:
            HealthRecordCreate(
                user_id="user123",
                real_name="张三",
                gender="男",
                blood_type="X"  # 无效值
            )
        assert "血型必须是A、B、O、AB或其他" in str(exc_info.value)


class TestHealthRecordUpdate:
    """HealthRecordUpdate 验证测试"""

    def test_partial_update(self):
        """测试部分更新"""
        data = HealthRecordUpdate(
            height=180.0,
            weight=75.0
        )
        assert data.height == 180.0
        assert data.weight == 75.0
        assert data.real_name is None
        assert data.gender is None

    def test_all_fields_optional(self):
        """测试所有字段都是可选的"""
        data = HealthRecordUpdate()
        assert data.real_name is None
        assert data.gender is None
        assert data.blood_type is None
