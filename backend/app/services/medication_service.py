"""
用药提醒服务

提供药品管理、用药计划、服药记录等功能
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.medication import (
    LogStatus,
    MedicationReminderItem,
    MedicationReminderLog,
    MedicationReminderNotification,
    MedicationReminderSchedule,
    MedicationType,
    ReminderStatus,
)
from app.services.base_service import BaseService


class MedicationService(BaseService[MedicationReminderItem]):
    """药品信息服务"""

    model_class = MedicationReminderItem
    cache_prefix = "medication"

    def __init__(self, db: Session):
        self.db = db

    def get_user_medications(
        self, user_id: str, only_active: bool = True
    ) -> List[MedicationReminderItem]:
        """获取用户的药品列表"""
        query = self.db.query(MedicationReminderItem).filter(
            MedicationReminderItem.user_id == user_id
        )
        if only_active:
            query = query.filter(MedicationReminderItem.is_active.is_(True))
        return query.order_by(MedicationReminderItem.created_at.desc()).all()

    def create_medication(
        self, user_id: str, medication_data: Dict[str, Any]
    ) -> MedicationReminderItem:
        """创建药品信息"""
        medication = MedicationReminderItem(
            user_id=user_id,
            name=medication_data["name"],
            generic_name=medication_data.get("generic_name"),
            brand_name=medication_data.get("brand_name"),
            medication_type=medication_data.get(
                "medication_type", MedicationType.PRESCRIPTION
            ),
            dosage=medication_data["dosage"],
            unit=medication_data["unit"],
            strength=medication_data.get("strength"),
            color=medication_data.get("color"),
            shape=medication_data.get("shape"),
            imprint=medication_data.get("imprint"),
            instructions=medication_data.get("instructions"),
            side_effects=medication_data.get("side_effects"),
            storage=medication_data.get("storage"),
            prescription_info=medication_data.get("prescription_info"),
            expiry_date=medication_data.get("expiry_date"),
            total_quantity=medication_data.get("total_quantity"),
            remaining_quantity=medication_data.get(
                "remaining_quantity", medication_data.get("total_quantity")
            ),
        )
        self.db.add(medication)
        self.db.commit()
        self.db.refresh(medication)
        return medication

    def update_medication(
        self, medication_id: int, user_id: str, update_data: Dict[str, Any]
    ) -> Optional[MedicationReminderItem]:
        """更新药品信息"""
        medication = self.get_by_id(medication_id)
        if not medication or medication.user_id != user_id:
            return None

        for key, value in update_data.items():
            if hasattr(medication, key) and value is not None:
                setattr(medication, key, value)

        medication.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(medication)
        return medication

    def delete_medication(self, medication_id: int, user_id: str) -> bool:
        """删除药品（软删除）"""
        medication = self.get_by_id(medication_id)
        if not medication or medication.user_id != user_id:
            return False

        medication.is_active = False
        self.db.commit()
        return True

    def update_remaining_quantity(
        self, medication_id: int, user_id: str, used_amount: float
    ) -> Optional[MedicationReminderItem]:
        """更新剩余药量"""
        medication = self.get_by_id(medication_id)
        if not medication or medication.user_id != user_id:
            return None

        if medication.remaining_quantity is not None:
            medication.remaining_quantity = max(
                0, medication.remaining_quantity - used_amount
            )
            self.db.commit()
            self.db.refresh(medication)
        return medication


class MedicationScheduleService(BaseService[MedicationReminderSchedule]):
    """用药计划服务"""

    model_class = MedicationReminderSchedule
    cache_prefix = "medication_schedule"

    def __init__(self, db: Session):
        self.db = db

    def get_user_schedules(
        self, user_id: str, only_active: bool = True
    ) -> List[MedicationReminderSchedule]:
        """获取用户的用药计划列表"""
        query = self.db.query(MedicationReminderSchedule).filter(
            MedicationReminderSchedule.user_id == user_id
        )
        if only_active:
            query = query.filter(
                MedicationReminderSchedule.is_active.is_(True),
                MedicationReminderSchedule.is_paused.is_(False),
            )
        return query.order_by(MedicationReminderSchedule.created_at.desc()).all()

    def get_medication_schedules(
        self, medication_id: int, user_id: str
    ) -> List[MedicationReminderSchedule]:
        """获取某个药品的用药计划"""
        return (
            self.db.query(MedicationReminderSchedule)
            .filter(
                MedicationReminderSchedule.medication_item_id == medication_id,
                MedicationReminderSchedule.user_id == user_id,
                MedicationReminderSchedule.is_active.is_(True),
            )
            .all()
        )

    def create_schedule(
        self, user_id: str, schedule_data: Dict[str, Any]
    ) -> MedicationReminderSchedule:
        """创建用药计划"""
        schedule = MedicationReminderSchedule(
            user_id=user_id,
            medication_item_id=schedule_data["medication_id"],
            name=schedule_data.get("name"),
            frequency=schedule_data["frequency"],
            times_of_day=schedule_data["times_of_day"],
            days_of_week=schedule_data.get("days_of_week"),
            specific_dates=schedule_data.get("specific_dates"),
            start_date=schedule_data["start_date"],
            end_date=schedule_data.get("end_date"),
            custom_dosage=schedule_data.get("custom_dosage"),
            custom_unit=schedule_data.get("custom_unit"),
            reminder_enabled=schedule_data.get("reminder_enabled", True),
            reminder_minutes_before=schedule_data.get("reminder_minutes_before", 0),
            timezone=schedule_data.get("timezone", "Asia/Shanghai"),
        )
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def update_schedule(
        self, schedule_id: int, user_id: str, update_data: Dict[str, Any]
    ) -> Optional[MedicationReminderSchedule]:
        """更新用药计划"""
        schedule = self.get_by_id(schedule_id)
        if not schedule or schedule.user_id != user_id:
            return None

        for key, value in update_data.items():
            if hasattr(schedule, key) and value is not None:
                setattr(schedule, key, value)

        schedule.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def pause_schedule(
        self,
        schedule_id: int,
        user_id: str,
        pause_until: Optional[datetime] = None,
    ) -> Optional[MedicationReminderSchedule]:
        """暂停用药计划"""
        schedule = self.get_by_id(schedule_id)
        if not schedule or schedule.user_id != user_id:
            return None

        schedule.is_paused = True
        schedule.pause_until = pause_until
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def resume_schedule(
        self, schedule_id: int, user_id: str
    ) -> Optional[MedicationReminderSchedule]:
        """恢复用药计划"""
        schedule = self.get_by_id(schedule_id)
        if not schedule or schedule.user_id != user_id:
            return None

        schedule.is_paused = False
        schedule.pause_until = None
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def delete_schedule(self, schedule_id: int, user_id: str) -> bool:
        """删除用药计划"""
        schedule = self.get_by_id(schedule_id)
        if not schedule or schedule.user_id != user_id:
            return False

        schedule.is_active = False
        self.db.commit()
        return True


class MedicationReminderService(BaseService[MedicationReminderNotification]):
    """用药提醒服务"""

    model_class = MedicationReminderNotification
    cache_prefix = "medication_reminder"

    def __init__(self, db: Session):
        self.db = db

    def get_user_reminders(
        self,
        user_id: str,
        reminder_date: Optional[date] = None,
        status: Optional[ReminderStatus] = None,
    ) -> List[MedicationReminderNotification]:
        """获取用户的提醒列表"""
        query = self.db.query(MedicationReminderNotification).filter(
            MedicationReminderNotification.user_id == user_id
        )

        if reminder_date:
            query = query.filter(
                MedicationReminderNotification.reminder_date == reminder_date
            )

        if status:
            query = query.filter(MedicationReminderNotification.status == status)

        return query.order_by(MedicationReminderNotification.scheduled_time).all()

    def create_reminder(
        self,
        user_id: str,
        schedule_id: int,
        medication_id: int,
        scheduled_time: datetime,
    ) -> MedicationReminderNotification:
        """创建提醒记录"""
        reminder = MedicationReminderNotification(
            user_id=user_id,
            schedule_id=schedule_id,
            medication_item_id=medication_id,
            scheduled_time=scheduled_time,
            reminder_date=scheduled_time.date(),
            reminder_time=scheduled_time.time(),
            status=ReminderStatus.PENDING,
        )
        self.db.add(reminder)
        self.db.commit()
        self.db.refresh(reminder)
        return reminder

    def mark_as_sent(
        self, reminder_id: int, notification_type: str
    ) -> Optional[MedicationReminderNotification]:
        """标记提醒为已发送"""
        reminder = self.get_by_id(reminder_id)
        if not reminder:
            return None

        reminder.status = ReminderStatus.SENT
        reminder.sent_at = datetime.utcnow()
        reminder.notification_sent = True
        reminder.notification_type = notification_type
        self.db.commit()
        self.db.refresh(reminder)
        return reminder

    def mark_as_responded(
        self, reminder_id: int, action: str
    ) -> Optional[MedicationReminderNotification]:
        """标记用户已响应"""
        reminder = self.get_by_id(reminder_id)
        if not reminder:
            return None

        reminder.responded_at = datetime.utcnow()
        reminder.response_action = action

        if action == "taken":
            reminder.status = ReminderStatus.CONFIRMED
        elif action == "skipped":
            reminder.status = ReminderStatus.DISMISSED

        self.db.commit()
        self.db.refresh(reminder)
        return reminder

    def get_today_reminders(self, user_id: str) -> List[MedicationReminderNotification]:
        """获取今日提醒"""
        today = date.today()
        return self.get_user_reminders(user_id, reminder_date=today)


class MedicationLogService(BaseService[MedicationReminderLog]):
    """服药记录服务"""

    model_class = MedicationReminderLog
    cache_prefix = "medication_log"

    def __init__(self, db: Session):
        self.db = db

    def get_user_logs(
        self,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        medication_id: Optional[int] = None,
    ) -> List[MedicationReminderLog]:
        """获取用户的服药记录"""
        query = self.db.query(MedicationReminderLog).filter(
            MedicationReminderLog.user_id == user_id
        )

        if start_date:
            query = query.filter(MedicationReminderLog.scheduled_date >= start_date)
        if end_date:
            query = query.filter(MedicationReminderLog.scheduled_date <= end_date)
        if medication_id:
            query = query.filter(
                MedicationReminderLog.medication_item_id == medication_id
            )

        return query.order_by(MedicationReminderLog.created_at.desc()).all()

    def create_log(
        self, user_id: str, log_data: Dict[str, Any]
    ) -> MedicationReminderLog:
        """创建服药记录"""
        log = MedicationReminderLog(
            user_id=user_id,
            medication_item_id=log_data["medication_id"],
            schedule_id=log_data.get("schedule_id"),
            reminder_id=log_data.get("reminder_id"),
            scheduled_date=log_data.get("scheduled_date"),
            scheduled_time=log_data.get("scheduled_time"),
            taken_at=log_data.get("taken_at", datetime.utcnow()),
            status=log_data["status"],
            dosage_taken=log_data.get("dosage_taken"),
            unit=log_data.get("unit"),
            notes=log_data.get("notes"),
            side_effects_noted=log_data.get("side_effects_noted"),
            skipped_reason=log_data.get("skipped_reason"),
            location=log_data.get("location"),
            device_id=log_data.get("device_id"),
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def record_taken(
        self,
        user_id: str,
        medication_id: int,
        reminder_id: Optional[int] = None,
        dosage_taken: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> MedicationReminderLog:
        """记录已服药"""
        log_data = {
            "medication_id": medication_id,
            "reminder_id": reminder_id,
            "status": LogStatus.TAKEN,
            "dosage_taken": dosage_taken,
            "notes": notes,
            "taken_at": datetime.utcnow(),
        }

        # 如果有提醒，获取计划信息
        if reminder_id:
            reminder = (
                self.db.query(MedicationReminderNotification)
                .filter(MedicationReminderNotification.id == reminder_id)
                .first()
            )
            if reminder:
                log_data["schedule_id"] = reminder.schedule_id
                log_data["scheduled_date"] = reminder.reminder_date
                log_data["scheduled_time"] = reminder.reminder_time

        log = self.create_log(user_id, log_data)

        # 更新提醒状态
        if reminder_id:
            reminder_service = MedicationReminderService(self.db)
            reminder_service.mark_as_responded(reminder_id, "taken")

        # 更新药品剩余量
        if dosage_taken:
            medication_service = MedicationService(self.db)
            medication_service.update_remaining_quantity(
                medication_id, user_id, dosage_taken
            )

        return log

    def record_skipped(
        self,
        user_id: str,
        medication_id: int,
        reminder_id: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> MedicationReminderLog:
        """记录跳过服药"""
        log_data = {
            "medication_id": medication_id,
            "reminder_id": reminder_id,
            "status": LogStatus.SKIPPED,
            "skipped_reason": reason,
        }

        if reminder_id:
            reminder = (
                self.db.query(MedicationReminderNotification)
                .filter(MedicationReminderNotification.id == reminder_id)
                .first()
            )
            if reminder:
                log_data["schedule_id"] = reminder.schedule_id
                log_data["scheduled_date"] = reminder.reminder_date
                log_data["scheduled_time"] = reminder.reminder_time

        log = self.create_log(user_id, log_data)

        # 更新提醒状态
        if reminder_id:
            reminder_service = MedicationReminderService(self.db)
            reminder_service.mark_as_responded(reminder_id, "skipped")

        return log

    def get_adherence_stats(
        self,
        user_id: str,
        medication_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """获取服药依从性统计"""
        query = self.db.query(MedicationReminderLog).filter(
            MedicationReminderLog.user_id == user_id
        )

        if medication_id:
            query = query.filter(
                MedicationReminderLog.medication_item_id == medication_id
            )
        if start_date:
            query = query.filter(MedicationReminderLog.scheduled_date >= start_date)
        if end_date:
            query = query.filter(MedicationReminderLog.scheduled_date <= end_date)

        logs = query.all()

        total = len(logs)
        taken = sum(1 for log in logs if log.status == LogStatus.TAKEN)
        missed = sum(1 for log in logs if log.status == LogStatus.MISSED)
        skipped = sum(1 for log in logs if log.status == LogStatus.SKIPPED)

        adherence_rate = (taken / total * 100) if total > 0 else 0

        return {
            "total_records": total,
            "taken_count": taken,
            "missed_count": missed,
            "skipped_count": skipped,
            "adherence_rate": round(adherence_rate, 2),
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
        }
