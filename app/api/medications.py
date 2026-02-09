"""
用药提醒API路由

提供药品管理、用药计划、服药记录等接口
"""

from datetime import date, datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.medication_service import (
    MedicationService, MedicationScheduleService,
    MedicationReminderService, MedicationLogService
)
from app.schemas.response import ResponseModel

router = APIRouter()

# 服务实例
medication_service = MedicationService()
schedule_service = MedicationScheduleService()
reminder_service = MedicationReminderService()
log_service = MedicationLogService()


# ============== 药品管理 ==============

@router.get("/medications", response_model=ResponseModel)
async def get_medications(
    only_active: bool = True,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取用户的药品列表"""
    medications = medication_service.get_user_medications(
        db, current_user.user_id, only_active
    )
    return ResponseModel(
        data=[m.to_dict() for m in medications],
        meta={"total": len(medications)}
    )


@router.post("/medications", response_model=ResponseModel)
async def create_medication(
    medication_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建药品信息"""
    medication = medication_service.create_medication(
        db, current_user.user_id, medication_data
    )
    return ResponseModel(data=medication.to_dict())


@router.get("/medications/{medication_id}", response_model=ResponseModel)
async def get_medication(
    medication_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取药品详情"""
    medication = medication_service.get_by_id(db, medication_id)
    if not medication or medication.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="药品不存在")
    return ResponseModel(data=medication.to_dict())


@router.put("/medications/{medication_id}", response_model=ResponseModel)
async def update_medication(
    medication_id: int,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新药品信息"""
    medication = medication_service.update_medication(
        db, medication_id, current_user.user_id, update_data
    )
    if not medication:
        raise HTTPException(status_code=404, detail="药品不存在")
    return ResponseModel(data=medication.to_dict())


@router.delete("/medications/{medication_id}", response_model=ResponseModel)
async def delete_medication(
    medication_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除药品"""
    success = medication_service.delete_medication(
        db, medication_id, current_user.user_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="药品不存在")
    return ResponseModel(message="删除成功")


# ============== 用药计划 ==============

@router.get("/schedules", response_model=ResponseModel)
async def get_schedules(
    medication_id: Optional[int] = None,
    only_active: bool = True,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取用药计划列表"""
    if medication_id:
        schedules = schedule_service.get_medication_schedules(
            db, medication_id, current_user.user_id
        )
    else:
        schedules = schedule_service.get_user_schedules(
            db, current_user.user_id, only_active
        )
    return ResponseModel(
        data=[s.to_dict() for s in schedules],
        meta={"total": len(schedules)}
    )


@router.post("/schedules", response_model=ResponseModel)
async def create_schedule(
    schedule_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建用药计划"""
    schedule = schedule_service.create_schedule(
        db, current_user.user_id, schedule_data
    )
    return ResponseModel(data=schedule.to_dict())


@router.get("/schedules/{schedule_id}", response_model=ResponseModel)
async def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取用药计划详情"""
    schedule = schedule_service.get_by_id(db, schedule_id)
    if not schedule or schedule.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="用药计划不存在")
    return ResponseModel(data=schedule.to_dict())


@router.put("/schedules/{schedule_id}", response_model=ResponseModel)
async def update_schedule(
    schedule_id: int,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新用药计划"""
    schedule = schedule_service.update_schedule(
        db, schedule_id, current_user.user_id, update_data
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="用药计划不存在")
    return ResponseModel(data=schedule.to_dict())


@router.post("/schedules/{schedule_id}/pause", response_model=ResponseModel)
async def pause_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """暂停用药计划"""
    schedule = schedule_service.pause_schedule(
        db, schedule_id, current_user.user_id
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="用药计划不存在")
    return ResponseModel(data=schedule.to_dict())


@router.post("/schedules/{schedule_id}/resume", response_model=ResponseModel)
async def resume_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """恢复用药计划"""
    schedule = schedule_service.resume_schedule(
        db, schedule_id, current_user.user_id
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="用药计划不存在")
    return ResponseModel(data=schedule.to_dict())


@router.delete("/schedules/{schedule_id}", response_model=ResponseModel)
async def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除用药计划"""
    success = schedule_service.delete_schedule(
        db, schedule_id, current_user.user_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="用药计划不存在")
    return ResponseModel(message="删除成功")


# ============== 提醒管理 ==============

@router.get("/reminders", response_model=ResponseModel)
async def get_reminders(
    reminder_date: Optional[date] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取用药提醒列表"""
    from app.models.medication import ReminderStatus
    
    reminder_status = None
    if status:
        try:
            reminder_status = ReminderStatus(status)
        except ValueError:
            pass
    
    reminders = reminder_service.get_user_reminders(
        db, current_user.user_id, reminder_date, reminder_status
    )
    return ResponseModel(
        data=[r.to_dict() for r in reminders],
        meta={"total": len(reminders)}
    )


@router.get("/reminders/today", response_model=ResponseModel)
async def get_today_reminders(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取今日提醒"""
    reminders = reminder_service.get_today_reminders(db, current_user.user_id)
    return ResponseModel(
        data=[r.to_dict() for r in reminders],
        meta={"total": len(reminders)}
    )


# ============== 服药记录 ==============

@router.get("/logs", response_model=ResponseModel)
async def get_logs(
    medication_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取服药记录"""
    logs = log_service.get_user_logs(
        db, current_user.user_id, start_date, end_date, medication_id
    )
    return ResponseModel(
        data=[log.to_dict() for log in logs],
        meta={"total": len(logs)}
    )


@router.post("/logs/taken", response_model=ResponseModel)
async def record_taken(
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """记录已服药"""
    medication_id = data.get("medication_id")
    reminder_id = data.get("reminder_id")
    dosage_taken = data.get("dosage_taken")
    notes = data.get("notes")
    
    if not medication_id:
        raise HTTPException(status_code=400, detail="药品ID不能为空")
    
    log = log_service.record_taken(
        db, current_user.user_id, medication_id,
        reminder_id, dosage_taken, notes
    )
    return ResponseModel(data=log.to_dict())


@router.post("/logs/skipped", response_model=ResponseModel)
async def record_skipped(
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """记录跳过服药"""
    medication_id = data.get("medication_id")
    reminder_id = data.get("reminder_id")
    reason = data.get("reason")
    
    if not medication_id:
        raise HTTPException(status_code=400, detail="药品ID不能为空")
    
    log = log_service.record_skipped(
        db, current_user.user_id, medication_id, reminder_id, reason
    )
    return ResponseModel(data=log.to_dict())


@router.get("/logs/stats", response_model=ResponseModel)
async def get_adherence_stats(
    medication_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取服药依从性统计"""
    stats = log_service.get_adherence_stats(
        db, current_user.user_id, medication_id, start_date, end_date
    )
    return ResponseModel(data=stats)


# ============== 仪表盘 ==============

@router.get("/dashboard", response_model=ResponseModel)
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取用药仪表盘数据"""
    today = date.today()
    
    # 今日提醒
    today_reminders = reminder_service.get_today_reminders(db, current_user.user_id)
    
    # 活跃计划数
    active_schedules = schedule_service.get_user_schedules(
        db, current_user.user_id, only_active=True
    )
    
    # 药品数量
    medications = medication_service.get_user_medications(
        db, current_user.user_id, only_active=True
    )
    
    # 本周依从性
    week_start = today - timedelta(days=today.weekday())
    stats = log_service.get_adherence_stats(
        db, current_user.user_id, start_date=week_start, end_date=today
    )
    
    return ResponseModel(data={
        "today_reminders": [r.to_dict() for r in today_reminders],
        "today_reminders_count": len(today_reminders),
        "active_schedules_count": len(active_schedules),
        "medications_count": len(medications),
        "weekly_adherence": stats
    })
