"""
集中注册 API v1 子路由。

单一入口便于维护 tags、前缀与路由清单（US-004）。

OpenAPI 分组标签与 docs/prd.md §2.1 产品模块对齐（R-W2），常量见 ``openapi_tags``；
子路由模块内 ``APIRouter(tags=...)`` 为唯一标签来源，此处 ``include_router`` 不再重复传 tags。
"""

from fastapi import APIRouter

from app.api import (
    aed,
    alerts,
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


def create_api_v1_router() -> APIRouter:
    """构建挂载在 API_V1_PREFIX 下的主路由器。"""
    router = APIRouter(prefix=settings.API_V1_PREFIX)

    router.include_router(users.router, prefix="/users")
    router.include_router(checkins.router, prefix="/checkins")
    router.include_router(sos_requests.router, prefix="/sos")
    router.include_router(devices.router, prefix="/devices")
    router.include_router(health_records.router, prefix="/health-records")
    router.include_router(knowledge.router, prefix="/knowledge")
    router.include_router(medications.router, prefix="/medications")
    router.include_router(aed.router, prefix="/aed")
    router.include_router(health_reports.router, prefix="/health-reports")
    router.include_router(anomalies.router, prefix="/anomalies")
    router.include_router(alerts.router, prefix="/alerts")
    router.include_router(contacts.router, prefix="/contacts")
    router.include_router(auth.router, prefix="/auth")
    router.include_router(emergency_centers.router, prefix="/emergency-centers")
    router.include_router(
        emergency_resources.router,
        prefix="/emergency-resources",
    )
    router.include_router(notifications.router, prefix="/notifications")

    return router


api_router = create_api_v1_router()

__all__ = ["api_router", "create_api_v1_router"]
