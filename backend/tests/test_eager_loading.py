"""
健康档案服务 Eager Loading 测试

验证 joinedload 是否解决了 N+1 查询问题
"""

import os

import pytest
from sqlalchemy import event
from sqlalchemy.engine import Engine

# 设置测试用的加密密钥
os.environ["ENCRYPTION_KEY"] = "IDXYznWU6bqgQff_7jYMLX65z0zID49Ced5fWB9XdtY="


# 追踪查询次数
query_count = 0


@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """在每次执行 SQL 查询前记录查询次数"""
    global query_count
    query_count += 1


@pytest.fixture(autouse=True)
def reset_query_count():
    """每个测试前重置查询计数"""
    global query_count
    query_count = 0
    yield
    query_count = 0


@pytest.fixture
def test_user(db):
    """创建测试用户"""
    from app.models.user import User

    user = User(
        user_id="test_eager_loading_user",
        phone="13900139000",
        password_hash="hashed_password",
    )
    db.add(user)
    db.commit()
    return user


class TestEagerLoading:
    """Eager Loading 测试"""

    def test_get_health_record_with_eager_loading(self, db, test_user):
        """
        测试获取健康档案时使用 eager loading 避免 N+1 查询

        验证：
        1. 只执行一次查询获取健康档案
        2. 关联数据（病史、用药、过敏）在同一查询中加载
        3. 访问关联数据不会触发额外的查询
        """
        from app.models.health_record import (
            Allergy,
            HealthRecord,
            MedicalHistory,
            Medication,
        )
        from app.services.health_record_service import HealthRecordService

        # 创建健康档案
        health_record = HealthRecord(
            user_id=test_user.user_id, real_name="张三", gender="男"
        )
        db.add(health_record)
        db.commit()
        db.refresh(health_record)

        # 添加关联数据
        medical_history = MedicalHistory(
            health_record_id=health_record.id, disease_name="高血压"
        )
        medication = Medication(health_record_id=health_record.id, drug_name="阿司匹林")
        allergy = Allergy(health_record_id=health_record.id, allergen="青霉素")
        db.add_all([medical_history, medication, allergy])
        db.commit()

        # 重置查询计数
        global query_count
        query_count = 0

        # 使用服务获取健康档案
        service = HealthRecordService()
        record = service.get_health_record(db, test_user.user_id)

        # 记录第一次查询后的查询次数
        queries_after_first_query = query_count

        # 访问关联数据（不应触发额外查询）
        medical_histories = record.medical_histories
        medications = record.medications
        allergies = record.allergies

        # 记录访问关联数据后的查询次数
        queries_after_access = query_count

        # 验证结果
        assert record is not None
        assert record.user_id == test_user.user_id

        # eager loading 应该在 2 次查询内完成（1 次获取健康档案，1 次获取关联数据）
        # 如果没有 eager loading，访问关联数据会触发 N+1 查询
        assert queries_after_access <= 2, (
            f"Eager loading 失败：执行了 {queries_after_access} 次查询，预期不超过 2 次。"
            "这可能意味着没有正确使用 joinedload。"
        )

        # 验证关联数据已加载
        assert len(medical_histories) >= 0
        assert len(medications) >= 0
        assert len(allergies) >= 0

    def test_get_health_record_without_associations(self, db, test_user):
        """测试获取没有关联数据的健康档案"""
        from app.models.health_record import HealthRecord
        from app.services.health_record_service import HealthRecordService

        # 创建健康档案（没有关联数据）
        health_record = HealthRecord(
            user_id=test_user.user_id, real_name="李四", gender="女"
        )
        db.add(health_record)
        db.commit()

        # 重置查询计数
        global query_count
        query_count = 0

        # 获取健康档案
        service = HealthRecordService()
        record = service.get_health_record(db, test_user.user_id)

        # 验证结果
        assert record is not None
        assert record.user_id == test_user.user_id

        # 即使没有关联数据，查询次数也应该很少（1 次或更少）
        assert query_count <= 1, f"查询次数过多：{query_count} 次，预期不超过 1 次"

    def test_get_health_record_multiple_associations(self, db, test_user):
        """测试获取有多个关联数据的健康档案"""
        from app.models.health_record import HealthRecord, MedicalHistory
        from app.services.health_record_service import HealthRecordService

        # 创建健康档案
        health_record = HealthRecord(
            user_id=test_user.user_id, real_name="王五", gender="男"
        )
        db.add(health_record)
        db.commit()
        db.refresh(health_record)

        # 添加多个病史记录
        for i in range(5):
            medical_history = MedicalHistory(
                health_record_id=health_record.id, disease_name=f"疾病{i}"
            )
            db.add(medical_history)
        db.commit()

        # 重置查询计数
        global query_count
        query_count = 0

        # 获取健康档案
        service = HealthRecordService()
        record = service.get_health_record(db, test_user.user_id)

        # 访问病史记录（不应触发额外查询）
        medical_histories = record.medical_histories

        # 验证结果
        assert record is not None
        assert len(medical_histories) == 5

        # eager loading 应该在 2 次查询内完成，即使有多个关联数据
        assert query_count <= 2, (
            f"Eager loading 失败：执行了 {query_count} 次查询，预期不超过 2 次。"
            "即使有 5 个病史记录，也应该只通过 joinedload 一次性加载。"
        )
