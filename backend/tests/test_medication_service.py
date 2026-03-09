"""
用药提醒功能测试

测试药品管理、用药计划、服药记录等功能
"""

from datetime import date, datetime, time, timedelta

import pytest
from app.models.medication import (
    LogStatus,
    MedicationReminderItem,
    MedicationReminderLog,
    MedicationReminderNotification,
    MedicationReminderSchedule,
    MedicationType,
    MedicationUnit,
    ReminderStatus,
    ScheduleFrequency,
)
from app.services.medication_service import (
    MedicationLogService,
    MedicationReminderService,
    MedicationScheduleService,
    MedicationService,
)
from sqlalchemy.orm import Session


class TestMedicationService:
    """测试药品服务"""

    def test_create_medication(self, db: Session):
        """测试创建药品"""
        service = MedicationService()
        medication_data = {
            "name": "阿司匹林",
            "generic_name": "乙酰水杨酸",
            "brand_name": "拜阿司匹灵",
            "medication_type": MedicationType.PRESCRIPTION,
            "dosage": 100,
            "unit": MedicationUnit.MG,
            "strength": "100mg/片",
            "instructions": "每日一次，饭后服用",
            "total_quantity": 30,
            "remaining_quantity": 30,
        }

        medication = service.create_medication(db, "user123", medication_data)

        assert medication.name == "阿司匹林"
        assert medication.dosage == 100
        assert medication.unit == MedicationUnit.MG
        assert medication.user_id == "user123"
        assert medication.is_active == True

    def test_get_user_medications(self, db: Session):
        """测试获取用户药品列表"""
        service = MedicationService()

        # 创建多个药品
        for i in range(3):
            service.create_medication(
                db,
                "user123",
                {"name": f"药品{i}", "dosage": 100, "unit": MedicationUnit.MG},
            )

        # 为其他用户创建药品
        service.create_medication(
            db,
            "other_user",
            {"name": "其他药品", "dosage": 100, "unit": MedicationUnit.MG},
        )

        medications = service.get_user_medications(db, "user123")

        assert len(medications) == 3
        for med in medications:
            assert med.user_id == "user123"

    def test_update_medication(self, db: Session):
        """测试更新药品"""
        service = MedicationService()
        medication = service.create_medication(
            db, "user123", {"name": "原名称", "dosage": 100, "unit": MedicationUnit.MG}
        )

        updated = service.update_medication(
            db, medication.id, "user123", {"name": "新名称", "dosage": 200}
        )

        assert updated.name == "新名称"
        assert updated.dosage == 200

    def test_delete_medication(self, db: Session):
        """测试删除药品（软删除）"""
        service = MedicationService()
        medication = service.create_medication(
            db,
            "user123",
            {"name": "测试药品", "dosage": 100, "unit": MedicationUnit.MG},
        )

        success = service.delete_medication(db, medication.id, "user123")

        assert success == True
        # 验证软删除
        deleted_med = service.get_by_id(db, medication.id)
        assert deleted_med.is_active == False

    def test_update_remaining_quantity(self, db: Session):
        """测试更新剩余药量"""
        service = MedicationService()
        medication = service.create_medication(
            db,
            "user123",
            {
                "name": "测试药品",
                "dosage": 100,
                "unit": MedicationUnit.MG,
                "remaining_quantity": 30,
            },
        )

        updated = service.update_remaining_quantity(db, medication.id, "user123", 2)

        assert updated.remaining_quantity == 28


class TestMedicationScheduleService:
    """测试用药计划服务"""

    def test_create_schedule(self, db: Session):
        """测试创建用药计划"""
        # 先创建药品
        med_service = MedicationService()
        medication = med_service.create_medication(
            db,
            "user123",
            {"name": "测试药品", "dosage": 100, "unit": MedicationUnit.MG},
        )

        schedule_service = MedicationScheduleService()
        schedule_data = {
            "medication_id": medication.id,
            "name": "早餐后服用",
            "frequency": ScheduleFrequency.DAILY,
            "times_of_day": "08:00,20:00",
            "start_date": date.today(),
            "reminder_enabled": True,
            "reminder_minutes_before": 10,
        }

        schedule = schedule_service.create_schedule(db, "user123", schedule_data)

        assert schedule.medication_item_id == medication.id
        assert schedule.frequency == ScheduleFrequency.DAILY
        assert schedule.times_of_day == "08:00,20:00"
        assert schedule.reminder_enabled == True

    def test_get_times_list(self, db: Session):
        """测试获取用药时间列表"""
        med_service = MedicationService()
        medication = med_service.create_medication(
            db,
            "user123",
            {"name": "测试药品", "dosage": 100, "unit": MedicationUnit.MG},
        )

        schedule_service = MedicationScheduleService()
        schedule = schedule_service.create_schedule(
            db,
            "user123",
            {
                "medication_id": medication.id,
                "frequency": ScheduleFrequency.DAILY,
                "times_of_day": "08:00,12:00,18:00",
                "start_date": date.today(),
            },
        )

        times = schedule.get_times_list()

        assert len(times) == 3
        assert "08:00" in times
        assert "12:00" in times
        assert "18:00" in times

    def test_pause_and_resume_schedule(self, db: Session):
        """测试暂停和恢复用药计划"""
        med_service = MedicationService()
        medication = med_service.create_medication(
            db,
            "user123",
            {"name": "测试药品", "dosage": 100, "unit": MedicationUnit.MG},
        )

        schedule_service = MedicationScheduleService()
        schedule = schedule_service.create_schedule(
            db,
            "user123",
            {
                "medication_id": medication.id,
                "frequency": ScheduleFrequency.DAILY,
                "times_of_day": "08:00",
                "start_date": date.today(),
            },
        )

        # 暂停
        paused = schedule_service.pause_schedule(db, schedule.id, "user123")
        assert paused.is_paused == True

        # 恢复
        resumed = schedule_service.resume_schedule(db, schedule.id, "user123")
        assert resumed.is_paused == False


class TestMedicationReminderService:
    """测试用药提醒服务"""

    def test_create_reminder(self, db: Session):
        """测试创建提醒"""
        # 创建药品和计划
        med_service = MedicationService()
        medication = med_service.create_medication(
            db,
            "user123",
            {"name": "测试药品", "dosage": 100, "unit": MedicationUnit.MG},
        )

        schedule_service = MedicationScheduleService()
        schedule = schedule_service.create_schedule(
            db,
            "user123",
            {
                "medication_id": medication.id,
                "frequency": ScheduleFrequency.DAILY,
                "times_of_day": "08:00",
                "start_date": date.today(),
            },
        )

        reminder_service = MedicationReminderService()
        scheduled_time = datetime.now() + timedelta(hours=1)
        reminder = reminder_service.create_reminder(
            db, "user123", schedule.id, medication.id, scheduled_time
        )

        assert reminder.user_id == "user123"
        assert reminder.schedule_id == schedule.id
        assert reminder.status == ReminderStatus.PENDING

    def test_mark_as_sent(self, db: Session):
        """测试标记提醒为已发送"""
        med_service = MedicationService()
        medication = med_service.create_medication(
            db,
            "user123",
            {"name": "测试药品", "dosage": 100, "unit": MedicationUnit.MG},
        )

        schedule_service = MedicationScheduleService()
        schedule = schedule_service.create_schedule(
            db,
            "user123",
            {
                "medication_id": medication.id,
                "frequency": ScheduleFrequency.DAILY,
                "times_of_day": "08:00",
                "start_date": date.today(),
            },
        )

        reminder_service = MedicationReminderService()
        scheduled_time = datetime.now() + timedelta(hours=1)
        reminder = reminder_service.create_reminder(
            db, "user123", schedule.id, medication.id, scheduled_time
        )

        updated = reminder_service.mark_as_sent(db, reminder.id, "push")

        assert updated.status == ReminderStatus.SENT
        assert updated.notification_sent == True
        assert updated.notification_type == "push"
        assert updated.sent_at is not None


class TestMedicationLogService:
    """测试服药记录服务"""

    def test_record_taken(self, db: Session):
        """测试记录已服药"""
        # 创建药品
        med_service = MedicationService()
        medication = med_service.create_medication(
            db,
            "user123",
            {
                "name": "测试药品",
                "dosage": 100,
                "unit": MedicationUnit.MG,
                "remaining_quantity": 30,
            },
        )

        log_service = MedicationLogService()
        log = log_service.record_taken(
            db, "user123", medication.id, dosage_taken=1, notes="正常服用"
        )

        assert log.status == LogStatus.TAKEN
        assert log.dosage_taken == 1
        assert log.notes == "正常服用"

        # 验证药量更新 (扣减的是服用数量，不是剂量值)
        updated_med = med_service.get_by_id(db, medication.id)
        assert updated_med.remaining_quantity == 29  # 30 - 1

    def test_record_skipped(self, db: Session):
        """测试记录跳过服药"""
        med_service = MedicationService()
        medication = med_service.create_medication(
            db,
            "user123",
            {"name": "测试药品", "dosage": 100, "unit": MedicationUnit.MG},
        )

        log_service = MedicationLogService()
        log = log_service.record_skipped(db, "user123", medication.id, reason="感觉好转")

        assert log.status == LogStatus.SKIPPED
        assert log.skipped_reason == "感觉好转"

    def test_get_adherence_stats(self, db: Session):
        """测试获取服药依从性统计"""
        med_service = MedicationService()
        medication = med_service.create_medication(
            db,
            "user123",
            {"name": "测试药品", "dosage": 100, "unit": MedicationUnit.MG},
        )

        log_service = MedicationLogService()

        # 创建服药记录：8次服用，2次跳过
        for i in range(8):
            log_service.record_taken(db, "user123", medication.id)
        for i in range(2):
            log_service.record_skipped(db, "user123", medication.id)

        stats = log_service.get_adherence_stats(db, "user123")

        assert stats["total_records"] == 10
        assert stats["taken_count"] == 8
        assert stats["skipped_count"] == 2
        assert stats["adherence_rate"] == 80.0


class TestMedicationModels:
    """测试用药模型"""

    def test_medication_to_dict(self, db: Session):
        """测试药品模型序列化"""
        medication = MedicationReminderItem(
            user_id="user123",
            name="阿司匹林",
            dosage=100,
            unit=MedicationUnit.MG,
            medication_type=MedicationType.PRESCRIPTION,
        )
        db.add(medication)
        db.commit()
        db.refresh(medication)

        data = medication.to_dict()

        assert data["name"] == "阿司匹林"
        assert data["dosage"] == 100
        assert data["unit"] == "mg"
        assert data["medication_type"] == "prescription"

    def test_schedule_to_dict(self, db: Session):
        """测试用药计划模型序列化"""
        medication = MedicationReminderItem(
            user_id="user123", name="阿司匹林", dosage=100, unit=MedicationUnit.MG
        )
        db.add(medication)
        db.commit()

        schedule = MedicationReminderSchedule(
            user_id="user123",
            medication_item_id=medication.id,
            frequency=ScheduleFrequency.DAILY,
            times_of_day="08:00,20:00",
            start_date=date.today(),
        )
        db.add(schedule)
        db.commit()
        db.refresh(schedule)

        data = schedule.to_dict()

        assert data["frequency"] == "daily"
        assert "times_list" in data
        assert len(data["times_list"]) == 2

    def test_reminder_to_dict(self, db: Session):
        """测试提醒模型序列化"""
        medication = MedicationReminderItem(
            user_id="user123", name="阿司匹林", dosage=100, unit=MedicationUnit.MG
        )
        db.add(medication)
        db.commit()

        schedule = MedicationReminderSchedule(
            user_id="user123",
            medication_item_id=medication.id,
            frequency=ScheduleFrequency.DAILY,
            times_of_day="08:00",
            start_date=date.today(),
        )
        db.add(schedule)
        db.commit()

        reminder = MedicationReminderNotification(
            user_id="user123",
            schedule_id=schedule.id,
            medication_item_id=medication.id,
            scheduled_time=datetime.now(),
            reminder_date=date.today(),
            reminder_time=time(8, 0),
            status=ReminderStatus.PENDING,
        )
        db.add(reminder)
        db.commit()
        db.refresh(reminder)

        data = reminder.to_dict()

        assert data["status"] == "pending"
        assert data["medication_name"] == "阿司匹林"

    def test_log_to_dict(self, db: Session):
        """测试服药记录模型序列化"""
        medication = MedicationReminderItem(
            user_id="user123", name="阿司匹林", dosage=100, unit=MedicationUnit.MG
        )
        db.add(medication)
        db.commit()

        log = MedicationReminderLog(
            user_id="user123",
            medication_item_id=medication.id,
            status=LogStatus.TAKEN,
            dosage_taken=100,
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        data = log.to_dict()

        assert data["status"] == "taken"
        assert data["dosage_taken"] == 100
        assert data["medication_name"] == "阿司匹林"
