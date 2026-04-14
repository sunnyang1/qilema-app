"""
AED设备地图API路由

提供AED设备查询、导航、批量导入等RESTful接口
使用 ApiResponseBuilder 统一构建响应
"""

from typing import List, Optional

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

from fastapi import APIRouter, Query, status
from pydantic import BaseModel, Field

from app.api.dependencies import AEDServiceDep, CurrentActiveUserDep, DbSession
from app.api.openapi_tags import TAG_EMERGENCY_RESOURCE
from app.core.exceptions import NotFoundException
from app.core.response_builder import ApiResponseBuilder

router = APIRouter(tags=[TAG_EMERGENCY_RESOURCE])


# ========== 请求/响应模型 ==========


class NearbyAEDRequest(BaseModel):
    """附近AED查询请求"""

    latitude: float = Field(..., ge=-90, le=90, description="纬度")
    longitude: float = Field(..., ge=-180, le=180, description="经度")
    radius: float = Field(default=5000, ge=100, le=50000, description="搜索半径（米）")
    only_active: bool = Field(default=True, description="仅返回可用设备")
    limit: int = Field(default=20, ge=1, le=100, description="返回数量限制")


class NavigationRequest(BaseModel):
    """导航请求"""

    from_lat: float = Field(..., ge=-90, le=90, description="起点纬度")
    from_lon: float = Field(..., ge=-180, le=180, description="起点经度")
    to_aed_id: int = Field(..., description="目标AED设备ID")
    nav_type: str = Field(default="walking", description="导航类型: walking/driving/bus")


class AEDStatusUpdateRequest(BaseModel):
    """AED状态更新请求"""

    status: str = Field(..., description="新状态: active/maintenance/inactive/deprecated")
    battery_expiry: Optional[str] = Field(None, description="电池过期日期（ISO格式）")
    pad_expiry: Optional[str] = Field(None, description="电极片过期日期（ISO格式）")
    notes: Optional[str] = Field(None, description="备注")


class BatchImportResponse(BaseModel):
    """批量导入响应"""

    total: int
    success: int
    failed: int
    errors: List[dict]


class AEDStatistics(BaseModel):
    """AED统计信息"""

    total: int
    status_distribution: dict
    city_distribution: List[dict]
    active_rate: float


# ========== API端点 ==========


@router.get("/nearby", response_model=dict)
def get_nearby_aeds(
    current_user: CurrentActiveUserDep,
    service: AEDServiceDep,
    latitude: Annotated[float, Query(ge=-90, le=90, description="纬度")],
    longitude: Annotated[float, Query(ge=-180, le=180, description="经度")],
    radius: Annotated[float, Query(ge=100, le=50000, description="搜索半径（米）")] = 5000,
    only_active: Annotated[bool, Query(description="仅返回可用设备")] = True,
    limit: Annotated[int, Query(ge=1, le=100, description="返回数量限制")] = 20,
):
    """
    获取附近的AED设备

    基于当前位置搜索附近可用的AED设备，返回距离和预估到达时间
    """
    aeds = service.get_nearby_aeds(
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        only_active=only_active,
        limit=limit,
    )

    return {
        "count": len(aeds),
        "user_location": {"latitude": latitude, "longitude": longitude},
        "aeds": aeds,
    }


@router.post("/navigation")
def get_aed_navigation(
    request: NavigationRequest,
    current_user: CurrentActiveUserDep,
    service: AEDServiceDep,
):
    """
    获取AED导航链接

    返回多个地图平台的导航链接，支持高德、百度、腾讯、苹果、谷歌地图
    """
    # 获取目标AED位置
    aed = service.get_by_id(request.to_aed_id)
    if not aed or aed.resource_type != "aed":
        raise NotFoundException("AED设备不存在")

    # 生成导航链接
    nav_urls = service.get_aed_navigation_url(
        from_lat=request.from_lat,
        from_lon=request.from_lon,
        to_lat=aed.latitude,
        to_lon=aed.longitude,
        nav_type=request.nav_type,
    )

    return ApiResponseBuilder.success(
        data={
            "from": {"latitude": request.from_lat, "longitude": request.from_lon},
            "to": {
                "aed_id": aed.id,
                "name": aed.resource_name,
                "latitude": aed.latitude,
                "longitude": aed.longitude,
                "address": aed.address,
                "location_desc": aed.aed_location_desc,
            },
            "navigation_urls": nav_urls,
        },
        message="获取AED导航链接成功",
    )


@router.get("/nearest")
def get_nearest_aed(
    current_user: CurrentActiveUserDep,
    service: AEDServiceDep,
    latitude: Annotated[float, Query(ge=-90, le=90, description="纬度")],
    longitude: Annotated[float, Query(ge=-180, le=180, description="经度")],
):
    """
    获取最近的AED设备

    快速找到距离当前位置最近的可用AED设备
    """
    aeds = service.get_nearby_aeds(
        latitude=latitude,
        longitude=longitude,
        radius=10000,  # 搜索10公里
        only_active=True,
        limit=1,
    )

    if not aeds:
        return ApiResponseBuilder.success(
            data={
                "found": False,
                "user_location": {"latitude": latitude, "longitude": longitude},
            },
            message="附近未找到可用的AED设备",
        )

    nearest = aeds[0]

    # 生成导航链接
    nav_urls = service.get_aed_navigation_url(
        from_lat=latitude,
        from_lon=longitude,
        to_lat=nearest["latitude"],
        to_lon=nearest["longitude"],
    )

    return ApiResponseBuilder.success(
        data={
            "found": True,
            "user_location": {"latitude": latitude, "longitude": longitude},
            "aed": nearest,
            "navigation_urls": nav_urls,
        },
        message="获取最近AED设备成功",
    )


@router.get("/{aed_id}")
def get_aed_detail(
    aed_id: int,
    current_user: CurrentActiveUserDep,
    service: AEDServiceDep,
):
    """
    获取AED设备详情

    返回AED设备的完整信息，包括位置、状态、负责人等
    """
    aed = service.get_by_id(aed_id)
    if not aed or aed.resource_type != "aed":
        raise NotFoundException("AED设备不存在")

    return ApiResponseBuilder.success(data=aed.to_dict(), message="获取AED设备详情成功")


@router.put("/{aed_id}/status")
def update_aed_status(
    aed_id: int,
    request: AEDStatusUpdateRequest,
    current_user: CurrentActiveUserDep,
    service: AEDServiceDep,
):
    """
    更新AED设备状态

    更新AED的状态（可用/维护中/不可用/废弃），记录检查信息
    """
    inspection_data = {}
    if request.battery_expiry:
        inspection_data["battery_expiry"] = request.battery_expiry
    if request.pad_expiry:
        inspection_data["pad_expiry"] = request.pad_expiry
    if request.notes:
        inspection_data["notes"] = request.notes

    updated = service.update_aed_status(
        aed_id, request.status, inspection_data if inspection_data else None
    )

    if not updated:
        raise NotFoundException("AED设备不存在")

    return ApiResponseBuilder.success(data=updated.to_dict(), message="AED设备状态更新成功")


@router.post("/import", status_code=status.HTTP_201_CREATED)
def import_aeds_batch(
    import_data: List[dict],
    current_user: CurrentActiveUserDep,
    service: AEDServiceDep,
):
    """
    批量导入AED设备

    批量导入AED设备数据，支持以下字段：
    - resource_name/name: 设备名称
    - latitude, longitude: 位置坐标
    - address: 详细地址
    - city, district: 城市和区县
    - aed_brand/brand: 品牌
    - aed_model/model: 型号
    - aed_sn/sn/serial_number: 序列号
    - aed_location_desc/location_desc: 具体位置描述
    - aed_access_instructions/access_instructions: 获取说明
    - aed_manager_name/manager_name: 负责人姓名
    - aed_manager_phone/manager_phone: 负责人电话
    - installation_date/install_date: 安装日期
    - battery_expiry: 电池过期日期
    - pad_expiry/electrode_expiry: 电极片过期日期
    """
    result = service.import_aeds_batch(import_data, operator_id=current_user.user_id)

    return ApiResponseBuilder.success(data=result, message="批量导入AED设备成功")


@router.get("/statistics/overview")
def get_aed_statistics(
    current_user: CurrentActiveUserDep,
    service: AEDServiceDep,
    city: Annotated[Optional[str], Query(description="城市名称（不传则统计全部）")] = None,
):
    """
    获取AED统计信息

    返回AED设备的统计数据，包括总数、状态分布、城市分布、可用率等
    """
    stats = service.get_aed_statistics(city=city)
    return ApiResponseBuilder.success(data=stats, message="获取AED统计信息成功")


@router.get("/maintenance/expiring")
def get_expiring_aeds(
    current_user: CurrentActiveUserDep,
    service: AEDServiceDep,
    days: Annotated[int, Query(ge=1, le=365, description="提前多少天预警")] = 30,
):
    """
    获取即将过期的AED设备

    查询电池或电极片即将过期的AED设备，用于维护提醒
    """
    aeds = service.get_expiring_aeds(days=days)

    return ApiResponseBuilder.success(
        data={"count": len(aeds), "warning_days": days, "aeds": aeds},
        message="获取即将过期的AED设备成功",
    )


@router.get("/map/bounds")
def get_aeds_in_bounds(
    current_user: CurrentActiveUserDep,
    db: DbSession,
    min_lat: Annotated[float, Query(ge=-90, le=90, description="最小纬度")],
    max_lat: Annotated[float, Query(ge=-90, le=90, description="最大纬度")],
    min_lon: Annotated[float, Query(ge=-180, le=180, description="最小经度")],
    max_lon: Annotated[float, Query(ge=-180, le=180, description="最大经度")],
    only_active: Annotated[bool, Query(description="仅返回可用设备")] = True,
):
    """
    获取地图边界内的AED设备

    用于地图展示，根据视口范围查询AED设备
    """
    from app.models.emergency_resource_model import EmergencyResource

    query = db.query(EmergencyResource).filter(
        EmergencyResource.resource_type == "aed",
        EmergencyResource.is_active == 1,
        EmergencyResource.latitude >= min_lat,
        EmergencyResource.latitude <= max_lat,
        EmergencyResource.longitude >= min_lon,
        EmergencyResource.longitude <= max_lon,
    )

    if only_active:
        from sqlalchemy import or_

        from app.models.emergency_resource_model import AEDStatus

        query = query.filter(
            or_(
                EmergencyResource.aed_status == AEDStatus.ACTIVE.value,
                EmergencyResource.aed_status.is_(None),
            )
        )

    aeds = query.all()

    return ApiResponseBuilder.success(
        data={
            "count": len(aeds),
            "bounds": {
                "min_lat": min_lat,
                "max_lat": max_lat,
                "min_lon": min_lon,
                "max_lon": max_lon,
            },
            "aeds": [aed.to_dict() for aed in aeds],
        },
        message="获取地图边界内的AED设备成功",
    )
