"""
用药提醒服务

提供药品管理、用药计划、服药记录等功能
"""

from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.services.base_service import BaseService
from app.models.medication import (
    MedicationReminderItem, MedicationReminderSchedule,
    MedicationReminderNotification, MedicationReminderLog,
    MedicationType, MedicationUnit, ScheduleFrequency, ReminderStatus, LogStatus
)


class MedicationService(BaseService[MedicationReminderItem]):
    """药品信息服务"""
    
    model_class = MedicationReminderItem
    cache_prefix = "medication"
    
    @classmethod
    def get_user_medications(cls, db: Session, user_id: str, 
                            only_active: bool = True) -> List[MedicationReminderItem]:
        """获取用户的药品列表"""
        query = db.query(MedicationReminderItem).filter(MedicationReminderItem.user_id == user_id)
        if only_active:
            query = query.filter(MedicationReminderItem.is_active == True)
        return query.order_by(MedicationReminderItem.created_at.desc()).all()
    
    @classmethod
    def create_medication(cls, db: Session, user_id: str, 
                         medication_data: Dict[str, Any]) -> MedicationReminderItem:
        """创建药品信息"""
        medication = MedicationReminderItem(
            user_id=user_id,
            name=medication_data["name"],
            generic_name=medication_data.get("generic_name"),
            brand_name=medication_data.get("brand_name"),
            medication_type=medication_data.get("medication_type", MedicationType.PRESCRIPTION),
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
            remaining_quantity=medication_data.get("remaining_quantity", medication_data.get("total_quantity"))
        )
        db.add(medication)
        db.commit()
        db.refresh(medication)
        return medication
    
    @classmethod
    def update_medication(cls, db: Session, medication_id: int, 
                         user_id: str, update_data: Dict[str, Any]) -> Optional[MedicationReminderItem]:
        """更新药品信息"""
        medication = cls.get_by_id(db, medication_id)
        if not medication or medication.user_id != user_id:
            return None
        
        for key, value in update_data.items():
            if hasattr(medication, key) and value is not None:
                setattr(medication, key, value)
        
        medication.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(medication)
        return medication
    
    @classmethod
    def delete_medication(cls, db: Session, medication_id: int, user_id: str) -> bool:
        """删除药品（软删除）"""
        medication = cls.get_by_id(db, medication_id)
        if not medication or medication.user_id != user_id:
            return False
        
        medication.is_active = False
        db.commit()
        return True
    
    @classmethod
    def update_remaining_quantity(cls, db: Session, medication_id: int, 
                                  user_id: str, used_amount: float) -> Optional[MedicationReminderItem]:
        """更新剩余药量"""
        medication = cls.get_by_id(db, medication_id)
        if not medication or medication.user_id != user_id:
            return None
        
        if medication.remaining_quantity is not None:
            medication.remaining_quantity = max(0, medication.remaining_quantity - used_amount)
            db.commit()
            db.refresh(medication)
        return medication


class MedicationScheduleService(BaseService[MedicationReminderSchedule]):
    """用药计划服务"""
    
    model_class = MedicationReminderSchedule
    cache_prefix = "medication_schedule"
    
    @classmethod
    def get_user_schedules(cls, db: Session, user_id: str,
                          only_active: bool = True) -> List[MedicationReminderSchedule]:
        """获取用户的用药计划列表"""
        query = db.query(MedicationReminderSchedule).filter(
            MedicationReminderSchedule.user_id == user_id
        )
        if only_active:
            query = query.filter(
                MedicationReminderSchedule.is_active == True,
                MedicationReminderSchedule.is_paused == False
            )
        return query.order_by(MedicationReminderSchedule.created_at.desc()).all()
    
    @classmethod
    def get_medication_schedules(cls, db: Session, medication_id: int, 
                                 user_id: str) -> List[MedicationReminderSchedule]:
        """获取某个药品的用药计划"""
        return db.query(MedicationReminderSchedule).filter(
            MedicationReminderSchedule.medication_item_id == medication_id,
            MedicationReminderSchedule.user_id == user_id,
            MedicationReminderSchedule.is_active == True
        ).all()
    
    @classmethod
    def create_schedule(cls, db: Session, user_id: str, 
                       schedule_data: Dict[str, Any]) -> MedicationReminderSchedule:
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
            timezone=schedule_data.get("timezone", "Asia/Shanghai")
        )
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        return schedule
    
    @classmethod
    def update_schedule(cls, db: Session, schedule_id: int, 
                       user_id: str, update_data: Dict[str, Any]) -> Optional[MedicationReminderSchedule]:
        """更新用药计划"""
        schedule = cls.get_by_id(db, schedule_id)
        if not schedule or schedule.user_id != user_id:
            return None
        
        for key, value in update_data.items():
            if hasattr(schedule, key) and value is not None:
                setattr(schedule, key, value)
        
        schedule.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(schedule)
        return schedule
    
    @classmethod
    def pause_schedule(cls, db: Session, schedule_id: int, 
                      user_id: str, pause_until: Optional[datetime] = None) -> Optional[MedicationReminderSchedule]:
        """暂停用药计划"""
        schedule = cls.get_by_id(db, schedule_id)
        if not schedule or schedule.user_id != user_id:
            return None
        
        schedule.is_paused = True
        schedule.pause_until = pause_until
        db.commit()
        db.refresh(schedule)
        return schedule
    
    @classmethod
    def resume_schedule(cls, db: Session, schedule_id: int, 
                       user_id: str) -> Optional[MedicationReminderSchedule]:
        """恢复用药计划"""
        schedule = cls.get_by_id(db, schedule_id)
        if not schedule or schedule.user_id != user_id:
            return None
        
        schedule.is_paused = False
        schedule.pause_until = None
        db.commit()
        db.refresh(schedule)
        return schedule
    
    @classmethod
    def delete_schedule(cls, db: Session, schedule_id: int, user_id: str) -> bool:
        """删除用药计划"""
        schedule = cls.get_by_id(db, schedule_id)
        if not schedule or schedule.user_id != user_id:
            return False
        
        schedule.is_active = False
        db.commit()
        return True


class MedicationReminderService(BaseService[MedicationReminderNotification]):
    """用药提醒服务"""
    
    model_class = MedicationReminderNotification
    cache_prefix = "medication_reminder"
    
    @classmethod
    def get_user_reminders(cls, db: Session, user_id: str, 
                          reminder_date: Optional[date] = None,
                          status: Optional[ReminderStatus] = None) -> List[MedicationReminderNotification]:
        """获取用户的提醒列表"""
        query = db.query(MedicationReminderNotification).filter(
            MedicationReminderNotification.user_id == user_id
        )
        
        if reminder_date:
            query = query.filter(MedicationReminderNotification.reminder_date == reminder_date)
        
        if status:
            query = query.filter(MedicationReminderNotification.status == status)
        
        return query.order_by(MedicationReminderNotification.scheduled_time).all()
    
    @classmethod
    def create_reminder(cls, db: Session, user_id: str, schedule_id: int,
                       medication_id: int, scheduled_time: datetime) -> MedicationReminderNotification:
        """创建提醒记录"""
        reminder = MedicationReminderNotification(
            user_id=user_id,
            schedule_id=schedule_id,
            medication_item_id=medication_id,
            scheduled_time=scheduled_time,
            reminder_date=scheduled_time.date(),
            reminder_time=scheduled_time.time(),
            status=ReminderStatus.PENDING
        )
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        return reminder
    
    @classmethod
    def mark_as_sent(cls, db: Session, reminder_id: int, 
                    notification_type: str) -> Optional[MedicationReminderNotification]:
        """标记提醒为已发送"""
        reminder = cls.get_by_id(db, reminder_id)
        if not reminder:
            return None
        
        reminder.status = ReminderStatus.SENT
        reminder.sent_at = datetime.utcnow()
        reminder.notification_sent = True
        reminder.notification_type = notification_type
        db.commit()
        db.refresh(reminder)
        return reminder
    
    @classmethod
    def mark_as_responded(cls, db: Session, reminder_id: int, 
                         action: str) -> Optional[MedicationReminderNotification]:
        """标记用户已响应"""
        reminder = cls.get_by_id(db, reminder_id)
        if not reminder:
            return None
        
        reminder.responded_at = datetime.utcnow()
        reminder.response_action = action
        
        if action == "taken":
            reminder.status = ReminderStatus.CONFIRMED
        elif action == "skipped":
            reminder.status = ReminderStatus.DISMISSED
        
        db.commit()
        db.refresh(reminder)
        return reminder
    
    @classmethod
    def get_today_reminders(cls, db: Session, user_id: str) -> List[MedicationReminderNotification]:
        """获取今日提醒"""
        today = date.today()
        return cls.get_user_reminders(db, user_id, reminder_date=today)


class MedicationLogService(BaseService[MedicationReminderLog]):
    """服药记录服务"""
    
    model_class = MedicationReminderLog
    cache_prefix = "medication_log"
    
    @classmethod
    def get_user_logs(cls, db: Session, user_id: str,
                     start_date: Optional[date] = None,
                     end_date: Optional[date] = None,
                     medication_id: Optional[int] = None) -> List[MedicationReminderLog]:
        """获取用户的服药记录"""
        query = db.query(MedicationReminderLog).filter(MedicationReminderLog.user_id == user_id)
        
        if start_date:
            query = query.filter(MedicationReminderLog.scheduled_date >= start_date)
        if end_date:
            query = query.filter(MedicationReminderLog.scheduled_date <= end_date)
        if medication_id:
            query = query.filter(MedicationReminderLog.medication_item_id == medication_id)
        
        return query.order_by(MedicationReminderLog.created_at.desc()).all()
    
    @classmethod
    def create_log(cls, db: Session, user_id: str, 
                  log_data: Dict[str, Any]) -> MedicationReminderLog:
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
            device_id=log_data.get("device_id")
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    
    @classmethod
    def record_taken(cls, db: Session, user_id: str, medication_id: int,
                    reminder_id: Optional[int] = None,
                    dosage_taken: Optional[float] = None,
                    notes: Optional[str] = None) -> MedicationReminderLog:
        """记录已服药"""
        log_data = {
            "medication_id": medication_id,
            "reminder_id": reminder_id,
            "status": LogStatus.TAKEN,
            "dosage_taken": dosage_taken,
            "notes": notes,
            "taken_at": datetime.utcnow()
        }
        
        # 如果有提醒，获取计划信息
        if reminder_id:
            reminder = db.query(MedicationReminderNotification).filter(
                MedicationReminderNotification.id == reminder_id
            ).first()
            if reminder:
                log_data["schedule_id"] = reminder.schedule_id
                log_data["scheduled_date"] = reminder.reminder_date
                log_data["scheduled_time"] = reminder.reminder_time
        
        log = cls.create_log(db, user_id, log_data)
        
        # 更新提醒状态
        if reminder_id:
            MedicationReminderService.mark_as_responded(db, reminder_id, "taken")
        
        # 更新药品剩余量
        if dosage_taken:
            MedicationService.update_remaining_quantity(
                db, medication_id, user_id, dosage_taken
            )
        
        return log
    
    @classmethod
    def record_skipped(cls, db: Session, user_id: str, medication_id: int,
                      reminder_id: Optional[int] = None,
                      reason: Optional[str] = None) -> MedicationReminderLog:
        """记录跳过服药"""
        log_data = {
            "medication_id": medication_id,
            "reminder_id": reminder_id,
            "status": LogStatus.SKIPPED,
            "skipped_reason": reason
        }
        
        if reminder_id:
            reminder = db.query(MedicationReminderNotification).filter(
                MedicationReminderNotification.id == reminder_id
            ).first()
            if reminder:
                log_data["schedule_id"] = reminder.schedule_id
                log_data["scheduled_date"] = reminder.reminder_date
                log_data["scheduled_time"] = reminder.reminder_time
        
        log = cls.create_log(db, user_id, log_data)
        
        # 更新提醒状态
        if reminder_id:
            MedicationReminderService.mark_as_responded(db, reminder_id, "skipped")
        
        return log
    
    @classmethod
    def get_adherence_stats(cls, db: Session, user_id: str,
                           medication_id: Optional[int] = None,
                           start_date: Optional[date] = None,
                           end_date: Optional[date] = None) -> Dict[str, Any]:
        """获取服药依从性统计"""
        query = db.query(MedicationReminderLog).filter(MedicationReminderLog.user_id == user_id)
        
        if medication_id:
            query = query.filter(MedicationReminderLog.medication_item_id == medication_id)
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
            "end_date": end_date.isoformat() if end_date else None
        }
