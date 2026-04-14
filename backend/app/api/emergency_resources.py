"""
急救资源地图API路由

提供周边搜索、导航、资源管理等RESTful接口
使用 ApiResponseBuilder 统一构建响应
使用 Annotated 依赖注入模式 (FastAPI 0.135.x)
"""

from fastapi import APIRouter, status

from app.api.dependencies import CurrentUserDep, EmergencyResourceServiceDep
from app.api.openapi_tags import TAG_EMERGENCY_RESOURCE
from app.core.exceptions import NotFoundException
from app.core.response_builder import ApiResponseBuilder
from app.schemas.emergency_resource import (
    NavigationRequest,
    NearbySearchRequest,
    ResourceCreate,
    ResourceDepartmentCreate,
    ResourceDepartmentResponse,
    ResourceFacilityCreate,
    ResourceFacilityResponse,
    ResourceQuery,
    ResourceResponse,
    ResourceUpdate,
)

router = APIRouter(tags=[TAG_EMERGENCY_RESOURCE])


# ========== 资源管理 ==========


@router.post("", status_code=status.HTTP_201_CREATED)
def create_resource(
    resource_data: ResourceCreate,
    current_user: CurrentUserDep,
    resource_service: EmergencyResourceServiceDep,
):
    """
    创建急救资源

    添加医院、AED设备、急救站等急救资源信息
    """
    resource = resource_service.create_resource(resource_data)
    return ApiResponseBuilder.from_model(resource, ResourceResponse, message="急救资源创建成功")


@router.get("/{resource_id}")
def get_resource(
    resource_id: int,
    resource_service: EmergencyResourceServiceDep,
):
    """
    获取急救资源详情

    返回资源的完整信息,包括设施、科室等
    """
    resource = resource_service.get_resource(resource_id)
    if not resource:
        raise NotFoundException("资源不存在")
    return ApiResponseBuilder.from_model(resource, ResourceResponse, message="获取资源详情成功")


@router.get("")
def query_resources(
    query_params: ResourceQuery,
    resource_service: EmergencyResourceServiceDep,
):
    """
    查询急救资源

    支持按类型、状态、城市、区县、医院等级等条件筛选
    """
    resources = resource_service.query_resources(query_params)
    return ApiResponseBuilder.from_model(
        resources, ResourceResponse, message="查询急救资源成功"
    )


@router.put("/{resource_id}")
def update_resource(
    resource_id: int,
    update_data: ResourceUpdate,
    current_user: CurrentUserDep,
    resource_service: EmergencyResourceServiceDep,
):
    """
    更新急救资源

    更新资源的名称、地址、联系方式、状态等信息
    """
    resource = resource_service.update_resource(resource_id, update_data)
    if not resource:
        raise NotFoundException("资源不存在")
    return ApiResponseBuilder.from_model(resource, ResourceResponse, message="资源更新成功")


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(
    resource_id: int,
    current_user: CurrentUserDep,
    resource_service: EmergencyResourceServiceDep,
):
    """
    删除急救资源

    删除指定的急救资源记录
    """
    success = resource_service.delete_resource(resource_id)
    if not success:
        raise NotFoundException("资源不存在")
    return None


# ========== 周边搜索 ==========


@router.post("/nearby/search")
def search_nearby(
    request: NearbySearchRequest,
    current_user: CurrentUserDep,
    resource_service: EmergencyResourceServiceDep,
):
    """
    搜索周边急救资源

    基于当前位置和搜索半径,查找附近的医院、AED等急救资源
    """
    resources = resource_service.search_nearby_resources(
        request, user_id=current_user.user_id
    )
    return ApiResponseBuilder.success(
        data={"count": len(resources), "resources": resources},
        message="搜索周边资源成功",
    )


# ========== 导航功能 ==========


@router.post("/navigation")
def get_navigation_route(
    request: NavigationRequest,
    current_user: CurrentUserDep,
    resource_service: EmergencyResourceServiceDep,
):
    """
    获取导航路线

    调用地图API获取从起点到终点的最佳导航路线
    """
    route = resource_service.get_navigation_route(request, user_id=current_user.user_id)
    return ApiResponseBuilder.success(data=route, message="获取导航路线成功")


# ========== 资源设施管理 ==========


@router.post("/{resource_id}/facilities", status_code=status.HTTP_201_CREATED)
def create_facility(
    resource_id: int,
    facility_data: ResourceFacilityCreate,
    current_user: CurrentUserDep,
    resource_service: EmergencyResourceServiceDep,
):
    """
    创建资源设施

    为资源添加设施信息(如手术室、ICU等)
    """
    facility_data.resource_id = resource_id
    facility = resource_service.create_facility(facility_data)
    return ApiResponseBuilder.from_model(
        facility, ResourceFacilityResponse, message="设施创建成功"
    )


@router.get("/{resource_id}/facilities")
def get_resource_facilities(
    resource_id: int,
    resource_service: EmergencyResourceServiceDep,
):
    """
    获取资源设施列表

    返回资源的所有设施信息
    """
    facilities = resource_service.get_resource_facilities(resource_id)
    return ApiResponseBuilder.from_model(
        facilities, ResourceFacilityResponse, message="获取设施列表成功"
    )


# ========== 资源科室管理 ==========


@router.post("/{resource_id}/departments", status_code=status.HTTP_201_CREATED)
def create_department(
    resource_id: int,
    department_data: ResourceDepartmentCreate,
    current_user: CurrentUserDep,
    resource_service: EmergencyResourceServiceDep,
):
    """
    创建资源科室

    为医院资源添加科室信息
    """
    department_data.resource_id = resource_id
    department = resource_service.create_department(department_data)
    return ApiResponseBuilder.from_model(
        department, ResourceDepartmentResponse, message="科室创建成功"
    )


@router.get("/{resource_id}/departments")
def get_resource_departments(
    resource_id: int,
    resource_service: EmergencyResourceServiceDep,
):
    """
    获取资源科室列表

    返回医院的所有科室信息
    """
    departments = resource_service.get_resource_departments(resource_id)
    return ApiResponseBuilder.from_model(
        departments, ResourceDepartmentResponse, message="获取科室列表成功"
    )


# ========== 统计分析 ==========


@router.get("/statistics/overview")
def get_resource_statistics(
    resource_service: EmergencyResourceServiceDep,
):
    """
    获取资源统计信息

    返回急救资源的统计数据,包括按类型、状态、城市分组等
    """
    statistics = resource_service.get_resource_statistics()
    return ApiResponseBuilder.success(data=statistics, message="获取资源统计成功")


@router.get("/statistics/popular")
def get_popular_resources(
    resource_service: EmergencyResourceServiceDep,
    limit: int = 10,
):
    """
    获取热门资源

    返回使用次数最多的急救资源
    """
    popular = resource_service.get_popular_resources(limit)
    return ApiResponseBuilder.success(
        data={"count": len(popular), "resources": popular}, message="获取热门资源成功"
    )


# ========== 一键导航快捷接口 ==========


@router.post("/quick-navigate")
def quick_navigate_to_resource(
    resource_id: int,
    current_lat: float,
    current_lon: float,
    current_user: CurrentUserDep,
    resource_service: EmergencyResourceServiceDep,
    route_type: str = "driving",
):
    """
    一键导航到资源

    快速生成从当前位置到指定资源的导航路线
    """
    # 获取目标资源
    resource = resource_service.get_resource(resource_id)
    if not resource:
        raise NotFoundException("资源不存在")

    # 创建导航请求
    request = NavigationRequest(
        start_latitude=current_lat,
        start_longitude=current_lon,
        end_latitude=resource.latitude,
        end_longitude=resource.longitude,
        route_type=route_type,
    )

    # 获取导航路线
    route = resource_service.get_navigation_route(request, user_id=current_user.user_id)

    return ApiResponseBuilder.success(
        data={"resource": resource.to_dict(), "route": route.dict()},
        message="获取导航路线成功",
    )


# ========== 资源验证 ==========


@router.post("/{resource_id}/verify")
def verify_resource(
    resource_id: int,
    current_user: CurrentUserDep,
    resource_service: EmergencyResourceServiceDep,
):
    """
    验证资源信息

    标记资源信息为已验证,并更新验证时间
    """
    resource = resource_service.get_resource(resource_id)
    if not resource:
        raise NotFoundException("资源不存在")

    update_data = ResourceUpdate(verified=True)
    resource = resource_service.update_resource(resource_id, update_data)

    return ApiResponseBuilder.success(data=resource.to_dict(), message="资源验证成功")
