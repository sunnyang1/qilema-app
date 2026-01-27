"""
120急救中心对接API路由

提供一键拨打120、救护车追踪、救援记录等RESTful接口
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.emergency_center import (
    EmergencyCenterCreate, EmergencyCenterUpdate, EmergencyCenterResponse,
    EmergencyCallCreate, EmergencyCallUpdate, EmergencyCallResponse,
    AmbulanceCreate, AmbulanceUpdate, AmbulanceResponse, AmbulanceLocation,
    RescueRecordCreate, RescueRecordUpdate, RescueRecordResponse,
    Call120Request, Call120Response,
    HealthSummary, AmbulanceTracking
)
from app.services.emergency_center_service import EmergencyCenterService

router = APIRouter(prefix="/api/emergency-centers", tags=["120急救中心"])
emergency_center_service = EmergencyCenterService()


# ========== 120一键拨打 ==========

@router.post("/call-120", response_model=Call120Response, status_code=status.HTTP_201_CREATED)
def call_120(
    request: Call120Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    一键拨打120
    
    创建急救呼叫记录,拨打120电话,自动发送位置和健康档案
    """
    try:
        response = emergency_center_service.call_120(db, request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ========== 急救呼叫管理 ==========

@router.get("/calls/{call_id}", response_model=EmergencyCallResponse)
def get_emergency_call(
    call_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取急救呼叫记录详情
    
    返回呼叫记录的完整信息
    """
    call = emergency_center_service.get_emergency_call(db, call_id)
    if not call:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="呼叫记录不存在")
    
    # 权限检查
    if call.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问")
    
    return call


@router.get("/calls/my-calls", response_model=List[EmergencyCallResponse])
def get_my_emergency_calls(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取我的急救呼叫记录
    
    返回当前用户的所有急救呼叫记录
    """
    calls = emergency_center_service.get_user_emergency_calls(db, current_user.user_id, limit)
    return calls


@router.put("/calls/{call_id}", response_model=EmergencyCallResponse)
def update_emergency_call(
    call_id: int,
    update_data: EmergencyCallUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新急救呼叫记录
    
    更新呼叫状态、通话备注等信息
    """
    call = emergency_center_service.get_emergency_call(db, call_id)
    if not call:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="呼叫记录不存在")
    
    # 权限检查
    if call.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限操作")
    
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(call, field, value)
    
    db.commit()
    db.refresh(call)
    return call


# ========== 救护车管理 ==========

@router.post("/ambulances/{emergency_call_id}/dispatch", response_model=AmbulanceResponse)
def dispatch_ambulance(
    emergency_call_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    派出救护车
    
    为急救呼叫创建救护车记录并标记为已派出
    """
    try:
        ambulance = emergency_center_service.dispatch_ambulance(db, emergency_call_id)
        return ambulance
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/ambulances/location", response_model=AmbulanceResponse)
def update_ambulance_location(
    location_data: AmbulanceLocation,
    db: Session = Depends(get_db)
):
    """
    更新救护车位置
    
    接收救护车位置更新并保存
    """
    try:
        ambulance = emergency_center_service.update_ambulance_location(db, location_data)
        return ambulance
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/ambulances/{emergency_call_id}/track", response_model=AmbulanceTracking)
def track_ambulance(
    emergency_call_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    追踪救护车
    
    获取救护车的实时位置和状态
    """
    try:
        tracking = emergency_center_service.track_ambulance(db, emergency_call_id)
        return tracking
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ========== 救援记录管理 ==========

@router.post("/rescue-records", response_model=RescueRecordResponse, status_code=status.HTTP_201_CREATED)
def create_rescue_record(
    record_data: RescueRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建救援记录
    
    记录完整的救援过程信息
    """
    try:
        record = emergency_center_service.create_rescue_record(db, record_data)
        return record
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/rescue-records/{record_id}", response_model=RescueRecordResponse)
def update_rescue_record(
    record_id: int,
    update_data: RescueRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新救援记录
    
    更新救援过程、结果、费用等信息
    """
    try:
        record = emergency_center_service.update_rescue_record(db, record_id, update_data)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="救援记录不存在")
        return record
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ========== 健康档案摘要 ==========

@router.post("/health-summary/{user_id}", response_model=HealthSummary)
def get_health_summary(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取健康档案摘要
    
    生成用户的健康档案摘要,包括基本信息、健康档案、设备数据、异常记录等
    """
    try:
        summary = emergency_center_service.generate_health_summary(db, user_id)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ========== 急救中心管理(管理员) ==========

@router.post("/centers", response_model=EmergencyCenterResponse, status_code=status.HTTP_201_CREATED)
def create_emergency_center(
    center_data: EmergencyCenterCreate,
    db: Session = Depends(get_db)
):
    """
    创建急救中心(管理员接口)
    
    添加新的急救中心配置
    """
    try:
        center = emergency_center_service.create_emergency_center(db, center_data)
        return center
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/centers", response_model=List[EmergencyCenterResponse])
def get_emergency_centers(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    获取急救中心列表(管理员接口)
    
    返回所有急救中心配置
    """
    centers = emergency_center_service.get_emergency_centers(db, active_only)
    return centers


# ========== 统计分析 ==========

@get("/statistics/overview")
def get_rescue_statistics(
    db: Session = Depends(get_db)
):
    """
    获取救援统计信息(管理员接口)
    
    返回救援次数、成功率、平均响应时间等统计数据
    """
    # 这里应该实现详细的统计分析
    return {
        "total_rescues": 0,
        "successful_rescues": 0,
        "average_response_time": 0,
        "average_duration": 0,
        "user_satisfaction": 0
    }


# ========== 快捷接口 ==========

@post("/quick-call-120")
def quick_call_120(
    current_lat: float,
    current_lon: float,
    send_health_summary: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    快速拨打120
    
    使用当前位置快速拨打120,简化版接口
    """
    request = Call120Request(
        user_id=current_user.user_id,
        caller_location=f"{current_lon},{current_lat}",
        send_health_summary=send_health_summary
    )
    
    response = emergency_center_service.call_120(db, request)
    return response


@get("/my-health-summary", response_model=HealthSummary)
def get_my_health_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取我的健康档案摘要
    
    快速获取当前用户的健康档案摘要
    """
    try:
        summary = emergency_center_service.generate_health_summary(db, current_user.user_id)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))