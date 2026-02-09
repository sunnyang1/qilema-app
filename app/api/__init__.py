"""
API路由模块
"""
from fastapi import APIRouter
from app.core.config import settings

from app.api import users, checkins, sos_requests, health_records, devices, knowledge, medications, aed, health_reports

# 创建主路由
api_router = APIRouter(prefix=settings.API_V1_PREFIX)

# 注册子路由
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(checkins.router, prefix="/checkins", tags=["签到"])
api_router.include_router(sos_requests.router, prefix="/sos", tags=["SOS求助"])
api_router.include_router(health_records.router, prefix="/health-records", tags=["健康档案"])
api_router.include_router(devices.router, prefix="/devices", tags=["设备"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["急救知识库"])
api_router.include_router(medications.router, prefix="/medications", tags=["用药提醒"])
api_router.include_router(aed.router, tags=["AED设备"])
api_router.include_router(health_reports.router, tags=["健康报告"])

__all__ = ['api_router']
