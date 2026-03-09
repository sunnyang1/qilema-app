"""
API路由模块
"""

from app.api import (
    aed,
    anomalies,
    auth,
    checkins,
    contacts,
    devices,
    emergency_centers,
    emergency_resources,
    health_records,
    health_reports,
    knowledge,
    medications,
    notifications,
    sos_requests,
    users,
)
from app.core.config import settings
from fastapi import APIRouter

# 创建主路由
api_router = APIRouter(prefix=settings.API_V1_PREFIX)

# 注册子路由
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(checkins.router, prefix="/checkins", tags=["签到"])
api_router.include_router(sos_requests.router, prefix="/sos", tags=["SOS求助"])
api_router.include_router(devices.router, prefix="/devices", tags=["设备"])
api_router.include_router(
    health_records.router, prefix="/health-records", tags=["健康档案"]
)
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["急救知识库"])
api_router.include_router(medications.router, prefix="/medications", tags=["用药提醒"])
api_router.include_router(aed.router, prefix="/aed", tags=["AED设备"])
api_router.include_router(
    health_reports.router, prefix="/health-reports", tags=["健康报告"]
)
api_router.include_router(anomalies.router, prefix="/anomalies", tags=["异常监测"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["紧急联系人"])
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(
    emergency_centers.router, prefix="/emergency-centers", tags=["120急救中心"]
)
api_router.include_router(
    emergency_resources.router, prefix="/emergency-resources", tags=["急救资源"]
)
api_router.include_router(notifications.router, prefix="/notifications", tags=["消息通知"])

__all__ = ["api_router"]
