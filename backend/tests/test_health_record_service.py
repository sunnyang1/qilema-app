"""健康档案服务单元测试"""

import os
from datetime import datetime

import pytest
from cryptography.fernet import Fernet
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base

# 导入数据库相关的模型
from app.models.user import User
from app.schemas.health_record import (
    AllergyCreate,
    AllergyUpdate,
    HealthRecordCreate,
    HealthRecordUpdate,
    MedicalHistoryCreate,
    MedicalHistoryUpdate,
    MedicationCreate,
    MedicationUpdate,
)
from app.services.health_record_service import HealthRecordService

# 测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def health_service():
    """创建健康档案服务实例"""
    # 设置测试用的加密密钥
    test_key = Fernet.generate_key().decode()
    os.environ["ENCRYPTION_KEY"] = test_key
    try:
        yield HealthRecordService(db)
    finally:
        # 清理环境变量
        if "ENCRYPTION_KEY" in os.environ:
            del os.environ["ENCRYPTION_KEY"]


@pytest.fixture
def test_user(db):
    """创建测试用户"""
    user = User(
        user_id="test_user_006",
        phone="13900139000",
        password_hash="hashed_password",
        nickname="测试用户006",
    )
    db.add(user)
    db.commit()
    return user


class TestHealthRecordService:
    """测试健康档案服务"""

    def test_create_health_record(self, db, test_user, health_service):
        """测试创建健康档案"""
        data = HealthRecordCreate(
            user_id=test_user.user_id,
            real_name="张三",
            gender="男",
            blood_type="A",
            height=175.0,
            weight=70.0,
            age=30,
            emergency_contact_name="李四",
            emergency_contact_phone="13900139001",
            emergency_contact_relation="配偶",
        )

        health_record = health_service.create_health_record(db, data, encrypt=False)

        assert health_record.id is not None
        assert health_record.user_id == test_user.user_id
        assert health_record.real_name == "张三"
        assert health_record.gender == "男"
        assert health_record.blood_type == "A"
        assert health_record.height == 175.0
        assert health_record.weight == 70.0
        assert health_record.age == 30
        assert health_record.emergency_contact_name == "李四"
        assert health_record.emergency_contact_phone == "13900139001"
        assert health_record.emergency_contact_relation == "配偶"

    def test_create_health_record_duplicate(self, db, test_user, health_service):
        """测试创建重复健康档案(应该失败)"""
        data1 = HealthRecordCreate(
            user_id=test_user.user_id, real_name="张三", gender="男"
        )
        health_service.create_health_record(db, data1, encrypt=False)

        data2 = HealthRecordCreate(
            user_id=test_user.user_id, real_name="李四", gender="女"
        )

        with pytest.raises(ValueError, match="该用户已存在健康档案"):
            health_service.create_health_record(db, data2, encrypt=False)

    def test_create_health_record_invalid_gender(self, db, test_user, health_service):
        """测试创建健康档案时性别验证"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="性别必须是"):
            data = HealthRecordCreate(
                user_id=test_user.user_id, real_name="张三", gender="未知"
            )
            health_service.create_health_record(db, data, encrypt=False)

    def test_create_health_record_invalid_blood_type(
        self, db, test_user, health_service
    ):
        """测试创建健康档案时血型验证"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="血型必须是"):
            data = HealthRecordCreate(
                user_id=test_user.user_id, real_name="张三", gender="男", blood_type="C"
            )
            health_service.create_health_record(db, data, encrypt=False)

    def test_get_health_record(self, db, test_user, health_service):
        """测试获取健康档案"""
        data = HealthRecordCreate(
            user_id=test_user.user_id, real_name="张三", gender="男", blood_type="A"
        )
        health_service.create_health_record(db, data, encrypt=False)

        health_record = health_service.get_health_record(db, test_user.user_id)

        assert health_record is not None
        assert health_record.real_name == "张三"
        assert health_record.gender == "男"
        assert health_record.blood_type == "A"

    def test_get_health_record_not_found(self, db, health_service):
        """测试获取不存在的健康档案"""
        health_record = health_service.get_health_record(db, "non_existent_user")
        assert health_record is None

    def test_update_health_record(self, db, test_user, health_service):
        """测试更新健康档案"""
        create_data = HealthRecordCreate(
            user_id=test_user.user_id, real_name="张三", gender="男", age=30
        )
        health_service.create_health_record(db, create_data, encrypt=False)

        update_data = HealthRecordUpdate(age=31, height=180.0)
        health_record = health_service.update_health_record(
            db, test_user.user_id, update_data
        )

        assert health_record.age == 31
        assert health_record.height == 180.0

    def test_update_health_record_not_found(self, db, health_service):
        """测试更新不存在的健康档案(应该失败)"""
        update_data = HealthRecordUpdate(age=31)

        with pytest.raises(ValueError, match="健康档案不存在"):
            health_service.update_health_record(db, "non_existent_user", update_data)

    def test_add_medical_history(self, db, test_user, health_service):
        """测试添加病史记录"""
        # 先创建健康档案
        record_data = HealthRecordCreate(
            user_id=test_user.user_id, real_name="张三", gender="男"
        )
        health_record = health_service.create_health_record(
            db, record_data, encrypt=False
        )

        # 添加病史记录
        history_data = MedicalHistoryCreate(
            health_record_id=health_record.id,
            disease_name="高血压",
            diagnosis_date=datetime(2020, 1, 1),
            description="原发性高血压",
            severity="中等",
            is_chronic=1,
        )

        medical_history = health_service.add_medical_history(
            db, health_record.id, history_data
        )

        assert medical_history.id is not None
        assert medical_history.disease_name == "高血压"
        assert medical_history.severity == "中等"
        assert medical_history.is_chronic == 1

    def test_get_medical_histories(self, db, test_user, health_service):
        """测试获取病史记录列表"""
        # 创建健康档案
        record_data = HealthRecordCreate(
            user_id=test_user.user_id, real_name="张三", gender="男"
        )
        health_record = health_service.create_health_record(
            db, record_data, encrypt=False
        )

        # 添加多条病史记录
        history_data1 = MedicalHistoryCreate(
            health_record_id=health_record.id, disease_name="高血压", is_chronic=1
        )
        history_data2 = MedicalHistoryCreate(
            health_record_id=health_record.id, disease_name="糖尿病", is_chronic=1
        )

        health_service.add_medical_history(db, health_record.id, history_data1)
        health_service.add_medical_history(db, health_record.id, history_data2)

        # 获取病史记录列表
        histories = health_service.get_medical_histories(db, health_record.id)

        assert len(histories) == 2

    def test_update_medical_history(self, db, test_user, health_service):
        """测试更新病史记录"""
        # 创建健康档案和病史记录
        record_data = HealthRecordCreate(
            user_id=test_user.user_id, real_name="张三", gender="男"
        )
        health_record = health_service.create_health_record(
            db, record_data, encrypt=False
        )

        history_data = MedicalHistoryCreate(
            health_record_id=health_record.id, disease_name="高血压", severity="轻微"
        )
        medical_history = health_service.add_medical_history(
            db, health_record.id, history_data
        )

        # 更新病史记录
        update_data = MedicalHistoryUpdate(severity="中等")
        updated_history = health_service.update_medical_history(
            db, medical_history.id, update_data
        )

        assert updated_history.severity == "中等"

    def test_delete_medical_history(self, db, test_user, health_service):
        """测试删除病史记录"""
        # 创建健康档案和病史记录
        record_data = HealthRecordCreate(
            user_id=test_user.user_id, real_name="张三", gender="男"
        )
        health_record = health_service.create_health_record(
            db, record_data, encrypt=False
        )

        history_data = MedicalHistoryCreate(
            health_record_id=health_record.id, disease_name="高血压"
        )
        medical_history = health_service.add_medical_history(
            db, health_record.id, history_data
        )

        # 删除病史记录
        result = health_service.delete_medical_history(db, medical_history.id)

        assert result is True

        # 验证已删除
        histories = health_service.get_medical_histories(db, health_record.id)
        assert len(histories) == 0

    def test_add_medication(self, db, test_user, health_service):
        """测试添加用药信息"""
        # 创建健康档案
        record_data = HealthRecordCreate(
            user_id=test_user.user_id, real_name="张三", gender="男"
        )
        health_record = health_service.create_health_record(
            db, record_data, encrypt=False
        )

        # 添加用药信息
        medication_data = MedicationCreate(
            health_record_id=health_record.id,
            drug_name="氨氯地平",
            dosage="5mg",
            frequency="每日一次",
            is_current=1,
        )

        medication = health_service.add_medication(
            db, health_record.id, medication_data
        )

        assert medication.id is not None
        assert medication.drug_name == "氨氯地平"
        assert medication.dosage == "5mg"
        assert medication.frequency == "每日一次"
        assert medication.is_current == 1

    def test_get_medications_current_only(self, db, test_user, health_service):
        """测试获取当前正在使用的药品"""
        # 创建健康档案
        record_data = HealthRecordCreate(
            user_id=test_user.user_id, real_name="张三", gender="男"
        )
        health_record = health_service.create_health_record(
            db, record_data, encrypt=False
        )

        # 添加第一条用药信息(当前使用)
        medication_data1 = MedicationCreate(
            health_record_id=health_record.id, drug_name="氨氯地平", is_current=1
        )
        med1 = health_service.add_medication(db, health_record.id, medication_data1)

        # 添加第二条用药信息(历史用药)
        medication_data2 = MedicationCreate(
            health_record_id=health_record.id, drug_name="阿司匹林", is_current=0
        )
        health_service.add_medication(db, health_record.id, medication_data2)

        # 获取当前用药
        current_medications = health_service.get_medications(
            db, health_record.id, current_only=True
        )

        # 验证只返回一条当前用药
        assert len(current_medications) == 1
        assert current_medications[0].drug_name == "氨氯地平"
        assert current_medications[0].is_current == 1

    def test_update_medication(self, db, test_user, health_service):
        """测试更新用药信息"""
        # 创建健康档案和用药信息
        record_data = HealthRecordCreate(
            user_id=test_user.user_id, real_name="张三", gender="男"
        )
        health_record = health_service.create_health_record(
            db, record_data, encrypt=False
        )

        medication_data = MedicationCreate(
            health_record_id=health_record.id, drug_name="氨氯地平", dosage="5mg"
        )
        medication = health_service.add_medication(
            db, health_record.id, medication_data
        )

        # 更新用药信息
        update_data = MedicationUpdate(dosage="10mg")
        updated_medication = health_service.update_medication(
            db, medication.id, update_data
        )

        assert updated_medication.dosage == "10mg"

    def test_delete_medication(self, db, test_user, health_service):
        """测试删除用药信息"""
        # 创建健康档案和用药信息
        record_data = HealthRecordCreate(
            user_id=test_user.user_id, real_name="张三", gender="男"
        )
        health_record = health_service.create_health_record(
            db, record_data, encrypt=False
        )

        medication_data = MedicationCreate(
            health_record_id=health_record.id, drug_name="氨氯地平"
        )
        medication = health_service.add_medication(
            db, health_record.id, medication_data
        )

        # 删除用药信息
        result = health_service.delete_medication(db, medication.id)

        assert result is True

        # 验证已删除
        medications = health_service.get_medications(db, health_record.id)
        assert len(medications) == 0

    def test_add_allergy(self, db, test_user, health_service):
        """测试添加过敏史"""
        # 创建健康档案
        record_data = HealthRecordCreate(
            user_id=test_user.user_id, real_name="张三", gender="男"
        )
        health_record = health_service.create_health_record(
            db, record_data, encrypt=False
        )

        # 添加过敏史
        allergy_data = AllergyCreate(
            health_record_id=health_record.id,
            allergen="青霉素",
            allergic_reaction="皮疹、呼吸困难",
            severity="严重",
        )

        allergy = health_service.add_allergy(db, health_record.id, allergy_data)

        assert allergy.id is not None
        assert allergy.allergen == "青霉素"
        assert allergy.allergic_reaction == "皮疹、呼吸困难"
        assert allergy.severity == "严重"

    def test_get_allergies(self, db, test_user, health_service):
        """测试获取过敏史列表"""
        # 创建健康档案
        record_data = HealthRecordCreate(
            user_id=test_user.user_id, real_name="张三", gender="男"
        )
        health_record = health_service.create_health_record(
            db, record_data, encrypt=False
        )

        # 添加多条过敏史
        allergy_data1 = AllergyCreate(
            health_record_id=health_record.id, allergen="青霉素", severity="严重"
        )
        allergy_data2 = AllergyCreate(
            health_record_id=health_record.id, allergen="花粉", severity="轻微"
        )

        health_service.add_allergy(db, health_record.id, allergy_data1)
        health_service.add_allergy(db, health_record.id, allergy_data2)

        # 获取过敏史列表
        allergies = health_service.get_allergies(db, health_record.id)

        assert len(allergies) == 2

    def test_update_allergy(self, db, test_user, health_service):
        """测试更新过敏史"""
        # 创建健康档案和过敏史
        record_data = HealthRecordCreate(
            user_id=test_user.user_id, real_name="张三", gender="男"
        )
        health_record = health_service.create_health_record(
            db, record_data, encrypt=False
        )

        allergy_data = AllergyCreate(
            health_record_id=health_record.id, allergen="青霉素", severity="中等"
        )
        allergy = health_service.add_allergy(db, health_record.id, allergy_data)

        # 更新过敏史
        update_data = AllergyUpdate(severity="严重")
        updated_allergy = health_service.update_allergy(db, allergy.id, update_data)

        assert updated_allergy.severity == "严重"

    def test_delete_allergy(self, db, test_user, health_service):
        """测试删除过敏史"""
        # 创建健康档案和过敏史
        record_data = HealthRecordCreate(
            user_id=test_user.user_id, real_name="张三", gender="男"
        )
        health_record = health_service.create_health_record(
            db, record_data, encrypt=False
        )

        allergy_data = AllergyCreate(health_record_id=health_record.id, allergen="青霉素")
        allergy = health_service.add_allergy(db, health_record.id, allergy_data)

        # 删除过敏史
        result = health_service.delete_allergy(db, allergy.id)

        assert result is True

        # 验证已删除
        allergies = health_service.get_allergies(db, health_record.id)
        assert len(allergies) == 0

    def test_generate_summary(self, db, test_user, health_service):
        """测试生成健康档案摘要"""
        # 创建健康档案
        record_data = HealthRecordCreate(
            user_id=test_user.user_id,
            real_name="张三",
            gender="男",
            age=30,
            blood_type="A",
            emergency_contact_name="李四",
            emergency_contact_phone="13900139001",
        )
        health_record = health_service.create_health_record(
            db, record_data, encrypt=False
        )

        # 添加慢性病
        history_data1 = MedicalHistoryCreate(
            health_record_id=health_record.id, disease_name="高血压", is_chronic=1
        )
        health_service.add_medical_history(db, health_record.id, history_data1)

        # 添加当前用药
        medication_data1 = MedicationCreate(
            health_record_id=health_record.id, drug_name="氨氯地平", is_current=1
        )
        health_service.add_medication(db, health_record.id, medication_data1)

        # 添加严重过敏
        allergy_data1 = AllergyCreate(
            health_record_id=health_record.id, allergen="青霉素", severity="严重"
        )
        health_service.add_allergy(db, health_record.id, allergy_data1)

        # 生成摘要
        summary = health_service.generate_summary(db, test_user.user_id)

        assert summary.real_name == "张三"
        assert summary.gender == "男"
        assert summary.age == 30
        assert summary.blood_type == "A"
        assert "高血压" in summary.chronic_diseases
        assert "氨氯地平" in summary.current_medications
        assert "青霉素" in summary.allergies  # 字段名已更改
        # 检查紧急联系人
        assert len(summary.emergency_contacts) == 1
        assert summary.emergency_contacts[0]["name"] == "李四"
        assert summary.emergency_contacts[0]["phone"] == "13900139001"

        # 测试生成文本摘要（如果存在）
        if hasattr(summary, "generate_summary_text"):
            summary_text = summary.generate_summary_text()
            assert "张三" in summary_text
            assert "高血压" in summary_text

    def test_generate_summary_record_not_found(self, db, health_service):
        """测试生成摘要时健康档案不存在(应该失败)"""
        with pytest.raises(ValueError, match="健康档案不存在"):
            health_service.generate_summary(db, "non_existent_user")


class TestEncryptionService:
    """测试加密服务"""

    def test_encrypt_decrypt_text(self, health_service):
        """测试加密和解密文本"""
        original_text = "张三"
        encrypted = health_service.encryption_service.encrypt(original_text)
        decrypted = health_service.encryption_service.decrypt(encrypted)

        assert original_text == decrypted
        assert encrypted != original_text

    def test_encrypt_empty_text(self, health_service):
        """测试加密空文本"""
        encrypted = health_service.encryption_service.encrypt("")
        assert encrypted == ""

    def test_encrypt_null_text(self, health_service):
        """测试加密None值"""
        encrypted = health_service.encryption_service.encrypt(None)
        assert encrypted is None
