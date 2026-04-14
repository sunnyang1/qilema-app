"""
预警设置 HTTP 入口（US-P03 / I-W2）

通过 AlertServiceDep 暴露当前用户的预警配置读写，与 docs/MVP_SERVICE_TRACE.md 对齐。
"""

from typing import Any, Optional

from fastapi import APIRouter

from app.api.dependencies import AlertServiceDep, CurrentUserDep
from app.api.openapi_tags import TAG_CHECKIN_MONITOR
from app.core.response_builder import ApiResponseBuilder
from app.models.alert import AlertSetting
from app.schemas.alert import AlertSettingCreate, AlertSettingResponse

router = APIRouter(tags=[TAG_CHECKIN_MONITOR])


def _alert_setting_to_response_data(setting: AlertSetting) -> dict[str, Any]:
    """将 ORM 转为与 AlertSettingResponse 一致的 dict（兼容 notification_channels 存为 str 的旧数据）。"""
    raw = setting.notification_channels
    if raw is None:
        channels: Optional[list[str]] = None
    elif isinstance(raw, str):
        channels = [c.strip() for c in raw.split(",") if c.strip()] or None
    else:
        channels = list(raw) if raw else None

    resp = AlertSettingResponse(
        id=setting.id,
        user_id=setting.user_id,
        checkin_enabled=setting.checkin_enabled,
        checkin_threshold_hours=setting.checkin_threshold_hours,
        abnormal_enabled=setting.abnormal_enabled,
        enable_notification=setting.enable_notification,
        heart_rate_min=setting.heart_rate_min,
        heart_rate_max=setting.heart_rate_max,
        blood_pressure_systolic_min=setting.blood_pressure_systolic_min,
        blood_pressure_systolic_max=setting.blood_pressure_systolic_max,
        blood_pressure_diastolic_min=setting.blood_pressure_diastolic_min,
        blood_pressure_diastolic_max=setting.blood_pressure_diastolic_max,
        blood_oxygen_min=setting.blood_oxygen_min,
        notification_channels=channels,
        emergency_contact_notify=setting.emergency_contact_notify,
        auto_resolve=setting.auto_resolve,
        created_at=setting.created_at,
        updated_at=setting.updated_at,
    )
    return resp.model_dump()


@router.get("/me/settings", summary="获取当前用户预警设置")
async def get_my_alert_settings(
    current_user: CurrentUserDep,
    alert_service: AlertServiceDep,
):
    """返回当前登录用户的预警配置；若从未配置则 data 为 null。"""
    setting = alert_service.get_setting(current_user.user_id)
    if not setting:
        return ApiResponseBuilder.success(data=None, message="暂无预警配置")
    return ApiResponseBuilder.success(data=_alert_setting_to_response_data(setting))


@router.put("/me/settings", summary="创建或更新当前用户预警设置")
async def put_my_alert_settings(
    body: AlertSettingCreate,
    current_user: CurrentUserDep,
    alert_service: AlertServiceDep,
):
    """创建或全量更新预警配置（与 AlertService.create_or_update_setting 语义一致）。"""
    setting = alert_service.create_or_update_setting(current_user.user_id, body)
    return ApiResponseBuilder.success(
        data=_alert_setting_to_response_data(setting),
        message="保存成功",
    )
