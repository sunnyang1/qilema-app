"""
智能设备API路由

提供设备绑定、数据上传、阈值配置等RESTful接口
使用 ApiResponseBuilder 统一构建响应
"""

from datetime import datetime

from app.api.dependencies import get_device_service
from app.core.exceptions import (
    DeviceNotFoundException,
    ThresholdNotFoundException,
    ValidationException,
)
from app.core.response_builder import ApiResponseBuilder
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.device import (
    DeviceBind,
    DeviceDataQuery,
    DeviceDataResponse,
    DeviceDataUpload,
    DeviceResponse,
    DeviceStatusUpdate,
    DeviceThresholdCreate,
    DeviceThresholdResponse,
    DeviceThresholdUpdate,
    DeviceUpdate,
)
from app.services.device_service import DeviceService
from fastapi import APIRouter, Depends, status

router = APIRouter(tags=["设备管理"])


# ========== 设备绑定管理 ==========


@router.post("/bind", status_code=status.HTTP_201_CREATED)
def bind_device(
    device_data: DeviceBind,
    current_user: User = Depends(get_current_user),
    service: DeviceService = Depends(get_device_service),
):
    """
    绑定智能设备

    支持绑定智能手环、智能手表等健康监测设备
    """
    try:
        device = service.bind_device(current_user.user_id, device_data)
        return ApiResponseBuilder.from_model(device, DeviceResponse, message="设备绑定成功")
    except ValueError as e:
        raise ValidationException(detail=str(e))


@router.post("/{device_id}/unbind", status_code=status.HTTP_200_OK)
def unbind_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    service: DeviceService = Depends(get_device_service),
):
    """
    解绑智能设备

    解绑后设备将无法上传数据,但历史数据保留
    """
    try:
        service.unbind_device(device_id, current_user.user_id)
        return ApiResponseBuilder.success(message="设备解绑成功")
    except ValueError as e:
        raise ValidationException(detail=str(e))


@router.get("")
def get_user_devices(
    include_inactive: bool = False,
    current_user: User = Depends(get_current_user),
    service: DeviceService = Depends(get_device_service),
):
    """
    获取当前用户的设备列表

    include_inactive: 是否包含已解绑设备
    """
    devices = service.get_user_devices(current_user.user_id, include_inactive)
    return ApiResponseBuilder.from_model(devices, DeviceResponse, message="获取设备列表成功")


@router.get("/{device_id}")
def get_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    service: DeviceService = Depends(get_device_service),
):
    """
    获取设备详细信息
    """
    device = service.get_device(device_id, current_user.user_id)
    if not device:
        raise DeviceNotFoundException(device_id)
    return ApiResponseBuilder.from_model(device, DeviceResponse, message="获取设备信息成功")


@router.put("/{device_id}", response_model=DeviceResponse)
def update_device(
    device_id: str,
    device_data: DeviceUpdate,
    current_user: User = Depends(get_current_user),
    service: DeviceService = Depends(get_device_service),
):
    """
    更新设备信息

    支持修改设备名称和备注信息
    """
    try:
        device = service.update_device(device_id, current_user.user_id, device_data)
        return device
    except ValueError as e:
        raise ValidationException(detail=str(e))


@router.patch("/{device_id}/status")
def update_device_status(
    device_id: str,
    status_data: DeviceStatusUpdate,
    current_user: User = Depends(get_current_user),
    service: DeviceService = Depends(get_device_service),
):
    """
    更新设备状态

    更新设备在线状态和电池电量
    """
    try:
        device = service.update_device_status(
            device_id, current_user.user_id, status_data
        )
        return ApiResponseBuilder.from_model(device, DeviceResponse, message="设备状态更新成功")
    except ValueError as e:
        raise ValidationException(detail=str(e))


# ========== 设备数据管理 ==========


@router.post(
    "/data/upload",
    response_model=DeviceDataResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_device_data(
    data: DeviceDataUpload,
    current_user: User = Depends(get_current_user),
    service: DeviceService = Depends(get_device_service),
):
    """
    上传设备生理数据

    支持上传心率、步数、睡眠、血压、血氧、体温等数据
    """
    try:
        device_data = service.upload_device_data(current_user.user_id, data)
        return device_data
    except ValueError as e:
        raise ValidationException(detail=str(e))


@router.post("/data/query")
def query_device_data(
    query_params: DeviceDataQuery,
    current_user: User = Depends(get_current_user),
    service: DeviceService = Depends(get_device_service),
):
    """
    查询设备数据

    支持按设备ID、时间范围、数据类型筛选
    """
    device_data_list = service.get_device_data(current_user.user_id, query_params)
    return ApiResponseBuilder.from_model(
        device_data_list, DeviceDataResponse, message="查询设备数据成功"
    )


@router.get("/{device_id}/statistics")
def get_device_statistics(
    device_id: str,
    data_type: str,
    start_time: datetime,
    end_time: datetime,
    current_user: User = Depends(get_current_user),
    service: DeviceService = Depends(get_device_service),
):
    """
    获取设备数据统计

    支持计算平均值、最小值、最大值、趋势等统计信息
    """
    try:
        # 验证设备归属
        device = service.get_device(device_id, current_user.user_id)
        if not device:
            raise DeviceNotFoundException(device_id)

        statistics = service.get_device_statistics(
            device_id, data_type, start_time, end_time
        )
        return statistics
    except ValueError as e:
        raise ValidationException(detail=str(e))


# ========== 阈值配置管理 ==========


@router.post("/thresholds", status_code=status.HTTP_201_CREATED)
def create_threshold(
    threshold_data: DeviceThresholdCreate,
    current_user: User = Depends(get_current_user),
    service: DeviceService = Depends(get_device_service),
):
    """
    创建设备异常阈值配置

    设置心率、血压、血氧、体温等生理数据的异常阈值
    """
    try:
        # 验证设备归属
        device = service.get_device(threshold_data.device_id, current_user.user_id)
        if not device:
            raise DeviceNotFoundException(threshold_data.device_id)

        threshold = service.create_threshold(threshold_data)
        return ApiResponseBuilder.from_model(
            threshold, DeviceThresholdResponse, message="阈值配置创建成功"
        )
    except ValueError as e:
        raise ValidationException(detail=str(e))


@router.get("/{device_id}/threshold", response_model=DeviceThresholdResponse)
def get_threshold(
    device_id: str,
    current_user: User = Depends(get_current_user),
    service: DeviceService = Depends(get_device_service),
):
    """
    获取设备异常阈值配置
    """
    # 验证设备归属
    device = service.get_device(device_id, current_user.user_id)
    if not device:
        raise DeviceNotFoundException(device_id)

    threshold = service.get_threshold(device_id)
    if not threshold:
        raise ThresholdNotFoundException()

    return threshold


@router.put("/{device_id}/threshold")
def update_threshold(
    device_id: str,
    threshold_data: DeviceThresholdUpdate,
    current_user: User = Depends(get_current_user),
    service: DeviceService = Depends(get_device_service),
):
    """
    更新设备异常阈值配置
    """
    try:
        # 验证设备归属
        device = service.get_device(device_id, current_user.user_id)
        if not device:
            raise DeviceNotFoundException(device_id)

        threshold = service.update_threshold(device_id, threshold_data)
        return ApiResponseBuilder.from_model(
            threshold, DeviceThresholdResponse, message="阈值配置更新成功"
        )
    except ValueError as e:
        raise ValidationException(detail=str(e))


# ========== 设备监控 ==========


@router.get("/admin/check-offline")
def check_offline_devices(
    offline_threshold_minutes: int = 60,
    service: DeviceService = Depends(get_device_service),
):
    """
    检查离线设备(管理员接口)

    定时任务调用,检查长时间未同步数据的设备并标记为离线
    """
    offline_devices = service.check_offline_devices(offline_threshold_minutes)

    return {
        "message": f"检查完成,发现{len(offline_devices)}个离线设备",
        "offline_devices": [device.to_dict() for device in offline_devices],
    }


@router.get("/admin/alerts")
def get_device_alerts(
    service: DeviceService = Depends(get_device_service),
):
    """
    获取设备异常预警列表(管理员接口)
    """
    # 这里可以实现预警历史查询功能
    return ApiResponseBuilder.success(data={"alerts": []}, message="预警历史查询功能待实现")
