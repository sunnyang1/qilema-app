"""
用药提醒API路由

提供药品管理、用药计划、服药记录等接口
使用 ApiResponseBuilder 统一构建响应
"""

from datetime import date, timedelta
from typing import Optional

from app.api.dependencies import (
    get_medication_log_service,
    get_medication_reminder_service,
    get_medication_schedule_service,
    get_medication_service,
)
from app.core.response_builder import ApiResponseBuilder
from app.core.security import get_current_user
from app.models.user import User
from app.services.medication_service import (
    MedicationLogService,
    MedicationReminderService,
    MedicationScheduleService,
    MedicationService,
)
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(tags=["用药提醒"])


# ============== 药品管理 ==============


@router.get("/")
async def get_medications(
    only_active: bool = True,
    medication_service: MedicationService = Depends(get_medication_service),
    current_user: User = Depends(get_current_user),
):
    """获取用户的药品列表"""
    medications = medication_service.get_user_medications(
        current_user.user_id, only_active
    )
    return ApiResponseBuilder.success(
        data=[m.to_dict() for m in medications], message="获取药品列表成功"
    )


@router.post("/")
async def create_medication(
    medication_data: dict,
    medication_service: MedicationService = Depends(get_medication_service),
    current_user: User = Depends(get_current_user),
):
    """创建药品信息"""
    medication = medication_service.create_medication(
        current_user.user_id, medication_data
    )
    return ApiResponseBuilder.success(data=medication.to_dict(), message="药品创建成功")


@router.get("/{medication_id}")
async def get_medication(
    medication_id: int,
    medication_service: MedicationService = Depends(get_medication_service),
    current_user: User = Depends(get_current_user),
):
    """获取药品详情"""
    medication = medication_service.get_by_id(medication_id)
    if not medication or medication.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="药品不存在")
    return ApiResponseBuilder.success(data=medication.to_dict(), message="获取药品详情成功")


@router.put("/{medication_id}")
async def update_medication(
    medication_id: int,
    update_data: dict,
    medication_service: MedicationService = Depends(get_medication_service),
    current_user: User = Depends(get_current_user),
):
    """更新药品信息"""
    medication = medication_service.update_medication(
        medication_id, current_user.user_id, update_data
    )
    if not medication:
        raise HTTPException(status_code=404, detail="药品不存在")
    return ApiResponseBuilder.success(data=medication.to_dict(), message="药品更新成功")


@router.delete("/{medication_id}")
async def delete_medication(
    medication_id: int,
    medication_service: MedicationService = Depends(get_medication_service),
    current_user: User = Depends(get_current_user),
):
    """删除药品"""
    success = medication_service.delete_medication(medication_id, current_user.user_id)
    if not success:
        raise HTTPException(status_code=404, detail="药品不存在")
    return ApiResponseBuilder.success(message="药品删除成功")


# ============== 用药计划 ==============


@router.get("/schedules/")
async def get_schedules(
    medication_id: Optional[int] = None,
    only_active: bool = True,
    schedule_service: MedicationScheduleService = Depends(
        get_medication_schedule_service
    ),
    current_user: User = Depends(get_current_user),
):
    """获取用药计划列表"""
    if medication_id:
        schedules = schedule_service.get_medication_schedules(
            medication_id, current_user.user_id
        )
    else:
        schedules = schedule_service.get_user_schedules(
            current_user.user_id, only_active
        )
    return ApiResponseBuilder.success(
        data=[s.to_dict() for s in schedules], message="获取用药计划列表成功"
    )


@router.post("/schedules/")
async def create_schedule(
    schedule_data: dict,
    schedule_service: MedicationScheduleService = Depends(
        get_medication_schedule_service
    ),
    current_user: User = Depends(get_current_user),
):
    """创建用药计划"""
    schedule = schedule_service.create_schedule(current_user.user_id, schedule_data)
    return ApiResponseBuilder.success(data=schedule.to_dict(), message="用药计划创建成功")


@router.get("/schedules/{schedule_id}")
async def get_schedule(
    schedule_id: int,
    schedule_service: MedicationScheduleService = Depends(
        get_medication_schedule_service
    ),
    current_user: User = Depends(get_current_user),
):
    """获取用药计划详情"""
    schedule = schedule_service.get_by_id(schedule_id)
    if not schedule or schedule.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="用药计划不存在")
    return ApiResponseBuilder.success(data=schedule.to_dict(), message="获取用药计划详情成功")


@router.put("/schedules/{schedule_id}")
async def update_schedule(
    schedule_id: int,
    update_data: dict,
    schedule_service: MedicationScheduleService = Depends(
        get_medication_schedule_service
    ),
    current_user: User = Depends(get_current_user),
):
    """更新用药计划"""
    schedule = schedule_service.update_schedule(
        schedule_id, current_user.user_id, update_data
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="用药计划不存在")
    return ApiResponseBuilder.success(data=schedule.to_dict(), message="用药计划更新成功")


@router.post("/schedules/{schedule_id}/pause")
async def pause_schedule(
    schedule_id: int,
    schedule_service: MedicationScheduleService = Depends(
        get_medication_schedule_service
    ),
    current_user: User = Depends(get_current_user),
):
    """暂停用药计划"""
    schedule = schedule_service.pause_schedule(schedule_id, current_user.user_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="用药计划不存在")
    return ApiResponseBuilder.success(data=schedule.to_dict(), message="用药计划已暂停")


@router.post("/schedules/{schedule_id}/resume")
async def resume_schedule(
    schedule_id: int,
    schedule_service: MedicationScheduleService = Depends(
        get_medication_schedule_service
    ),
    current_user: User = Depends(get_current_user),
):
    """恢复用药计划"""
    schedule = schedule_service.resume_schedule(schedule_id, current_user.user_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="用药计划不存在")
    return ApiResponseBuilder.success(data=schedule.to_dict(), message="用药计划已恢复")


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: int,
    schedule_service: MedicationScheduleService = Depends(
        get_medication_schedule_service
    ),
    current_user: User = Depends(get_current_user),
):
    """删除用药计划"""
    success = schedule_service.delete_schedule(schedule_id, current_user.user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用药计划不存在")
    return ApiResponseBuilder.success(message="用药计划删除成功")


# ============== 提醒管理 ==============


@router.get("/reminders/")
async def get_reminders(
    reminder_date: Optional[date] = None,
    status: Optional[str] = None,
    reminder_service: MedicationReminderService = Depends(
        get_medication_reminder_service
    ),
    current_user: User = Depends(get_current_user),
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
        current_user.user_id, reminder_date, reminder_status
    )
    return ApiResponseBuilder.success(
        data=[r.to_dict() for r in reminders], message="获取用药提醒列表成功"
    )


@router.get("/reminders/today")
async def get_today_reminders(
    reminder_service: MedicationReminderService = Depends(
        get_medication_reminder_service
    ),
    current_user: User = Depends(get_current_user),
):
    """获取今日提醒"""
    reminders = reminder_service.get_today_reminders(current_user.user_id)
    return ApiResponseBuilder.success(
        data=[r.to_dict() for r in reminders], message="获取今日提醒成功"
    )


# ============== 服药记录 ==============


@router.get("/logs/")
async def get_logs(
    medication_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    log_service: MedicationLogService = Depends(get_medication_log_service),
    current_user: User = Depends(get_current_user),
):
    """获取服药记录"""
    logs = log_service.get_user_logs(
        current_user.user_id, start_date, end_date, medication_id
    )
    return ApiResponseBuilder.success(
        data=[log.to_dict() for log in logs], message="获取服药记录成功"
    )


@router.post("/logs/taken")
async def record_taken(
    data: dict,
    log_service: MedicationLogService = Depends(get_medication_log_service),
    current_user: User = Depends(get_current_user),
):
    """记录已服药"""
    medication_id = data.get("medication_id")
    reminder_id = data.get("reminder_id")
    dosage_taken = data.get("dosage_taken")
    notes = data.get("notes")

    if not medication_id:
        raise HTTPException(status_code=400, detail="药品ID不能为空")

    log = log_service.record_taken(
        current_user.user_id, medication_id, reminder_id, dosage_taken, notes
    )
    return ApiResponseBuilder.success(data=log.to_dict(), message="服药记录成功")


@router.post("/logs/skipped")
async def record_skipped(
    data: dict,
    log_service: MedicationLogService = Depends(get_medication_log_service),
    current_user: User = Depends(get_current_user),
):
    """记录跳过服药"""
    medication_id = data.get("medication_id")
    reminder_id = data.get("reminder_id")
    reason = data.get("reason")

    if not medication_id:
        raise HTTPException(status_code=400, detail="药品ID不能为空")

    log = log_service.record_skipped(
        current_user.user_id, medication_id, reminder_id, reason
    )
    return ApiResponseBuilder.success(data=log.to_dict(), message="跳过服药记录成功")


@router.get("/logs/stats")
async def get_adherence_stats(
    medication_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    log_service: MedicationLogService = Depends(get_medication_log_service),
    current_user: User = Depends(get_current_user),
):
    """获取服药依从性统计"""
    stats = log_service.get_adherence_stats(
        current_user.user_id, medication_id, start_date, end_date
    )
    return ApiResponseBuilder.success(data=stats, message="获取服药依从性统计成功")


# ============== 仪表盘 ==============


@router.get("/dashboard")
async def get_dashboard(
    medication_service: MedicationService = Depends(get_medication_service),
    schedule_service: MedicationScheduleService = Depends(
        get_medication_schedule_service
    ),
    reminder_service: MedicationReminderService = Depends(
        get_medication_reminder_service
    ),
    log_service: MedicationLogService = Depends(get_medication_log_service),
    current_user: User = Depends(get_current_user),
):
    """获取用药仪表盘数据"""
    today = date.today()

    # 今日提醒
    today_reminders = reminder_service.get_today_reminders(current_user.user_id)

    # 活跃计划数
    active_schedules = schedule_service.get_user_schedules(
        current_user.user_id, only_active=True
    )

    # 药品数量
    medications = medication_service.get_user_medications(
        current_user.user_id, only_active=True
    )

    # 本周依从性
    week_start = today - timedelta(days=today.weekday())
    stats = log_service.get_adherence_stats(
        current_user.user_id, start_date=week_start, end_date=today
    )

    return ApiResponseBuilder.success(
        data={
            "today_reminders": [r.to_dict() for r in today_reminders],
            "today_reminders_count": len(today_reminders),
            "active_schedules_count": len(active_schedules),
            "medications_count": len(medications),
            "weekly_adherence": stats,
        },
        message="获取用药仪表盘数据成功",
    )
