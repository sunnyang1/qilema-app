"""
急救资源地图API路由

提供周边搜索、导航、资源管理等RESTful接口
"""

from typing import List
from fastapi import APIRouter, Depends, status
from app.core.exceptions import NotFoundException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.emergency_resource import (
    ResourceCreate, ResourceUpdate, ResourceResponse, ResourceQuery,
    NearbySearchRequest, NavigationRequest, NavigationResponse,
    ResourceFacilityCreate, ResourceFacilityResponse,
    ResourceDepartmentCreate, ResourceDepartmentResponse,
    ResourceStatistics, PopularResource
)
from app.services.emergency_resource_service import EmergencyResourceService

router = APIRouter(prefix="/api/emergency-resources", tags=["急救资源"])
resource_service = EmergencyResourceService()


# ========== 资源管理 ==========

@router.post("", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
def create_resource(
    resource_data: ResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建急救资源
    
    添加医院、AED设备、急救站等急救资源信息
    """
    resource = resource_service.create_resource(db, resource_data)
    return resource


@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(
    resource_id: int,
    db: Session = Depends(get_db)
):
    """
    获取急救资源详情
    
    返回资源的完整信息,包括设施、科室等
    """
    resource = resource_service.get_resource(db, resource_id)
    if not resource:
        raise NotFoundException("资源不存在")
    return resource


@router.get("", response_model=List[ResourceResponse])
def query_resources(
    query_params: ResourceQuery,
    db: Session = Depends(get_db)
):
    """
    查询急救资源
    
    支持按类型、状态、城市、区县、医院等级等条件筛选
    """
    resources = resource_service.query_resources(db, query_params)
    return resources


@router.put("/{resource_id}", response_model=ResourceResponse)
def update_resource(
    resource_id: int,
    update_data: ResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新急救资源
    
    更新资源的名称、地址、联系方式、状态等信息
    """
    resource = resource_service.update_resource(db, resource_id, update_data)
    if not resource:
        raise NotFoundException("资源不存在")
    return resource


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除急救资源
    
    删除指定的急救资源记录
    """
    success = resource_service.delete_resource(db, resource_id)
    if not success:
        raise NotFoundException("资源不存在")
    return None


# ========== 周边搜索 ==========

@router.post("/nearby/search")
def search_nearby(
    request: NearbySearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    搜索周边急救资源
    
    基于当前位置和搜索半径,查找附近的医院、AED等急救资源
    """
    resources = resource_service.search_nearby_resources(
        db,
        request,
        user_id=current_user.user_id
    )
    return {
        "count": len(resources),
        "resources": resources
    }


# ========== 导航功能 ==========

@router.post("/navigation", response_model=NavigationResponse)
def get_navigation_route(
    request: NavigationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取导航路线
    
    调用地图API获取从起点到终点的最佳导航路线
    """
    route = resource_service.get_navigation_route(
        db,
        request,
        user_id=current_user.user_id
    )
    return route


# ========== 资源设施管理 ==========

@router.post("/{resource_id}/facilities", response_model=ResourceFacilityResponse, status_code=status.HTTP_201_CREATED)
def create_facility(
    resource_id: int,
    facility_data: ResourceFacilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建资源设施
    
    为资源添加设施信息(如手术室、ICU等)
    """
    facility_data.resource_id = resource_id
    facility = resource_service.create_facility(db, facility_data)
    return facility


@router.get("/{resource_id}/facilities", response_model=List[ResourceFacilityResponse])
def get_resource_facilities(
    resource_id: int,
    db: Session = Depends(get_db)
):
    """
    获取资源设施列表
    
    返回资源的所有设施信息
    """
    facilities = resource_service.get_resource_facilities(db, resource_id)
    return facilities


# ========== 资源科室管理 ==========

@router.post("/{resource_id}/departments", response_model=ResourceDepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    resource_id: int,
    department_data: ResourceDepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建资源科室
    
    为医院资源添加科室信息
    """
    department_data.resource_id = resource_id
    department = resource_service.create_department(db, department_data)
    return department


@router.get("/{resource_id}/departments", response_model=List[ResourceDepartmentResponse])
def get_resource_departments(
    resource_id: int,
    db: Session = Depends(get_db)
):
    """
    获取资源科室列表
    
    返回医院的所有科室信息
    """
    departments = resource_service.get_resource_departments(db, resource_id)
    return departments


# ========== 统计分析 ==========

@router.get("/statistics/overview")
def get_resource_statistics(
    db: Session = Depends(get_db)
):
    """
    获取资源统计信息
    
    返回急救资源的统计数据,包括按类型、状态、城市分组等
    """
    statistics = resource_service.get_resource_statistics(db)
    return statistics


@router.get("/statistics/popular")
def get_popular_resources(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    获取热门资源
    
    返回使用次数最多的急救资源
    """
    popular = resource_service.get_popular_resources(db, limit)
    return {
        "count": len(popular),
        "resources": popular
    }


# ========== 一键导航快捷接口 ==========

@router.post("/quick-navigate")
def quick_navigate_to_resource(
    resource_id: int,
    current_lat: float,
    current_lon: float,
    route_type: str = "driving",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    一键导航到资源
    
    快速生成从当前位置到指定资源的导航路线
    """
    # 获取目标资源
    resource = resource_service.get_resource(db, resource_id)
    if not resource:
        raise NotFoundException("资源不存在")
    
    # 创建导航请求
    request = NavigationRequest(
        start_latitude=current_lat,
        start_longitude=current_lon,
        end_latitude=resource.latitude,
        end_longitude=resource.longitude,
        route_type=route_type
    )
    
    # 获取导航路线
    route = resource_service.get_navigation_route(
        db,
        request,
        user_id=current_user.user_id
    )
    
    return {
        "resource": resource.to_dict(),
        "route": route.dict()
    }


# ========== 资源验证 ==========

@router.post("/{resource_id}/verify")
def verify_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    验证资源信息
    
    标记资源信息为已验证,并更新验证时间
    """
    resource = resource_service.get_resource(db, resource_id)
    if not resource:
        raise NotFoundException("资源不存在")
    
    update_data = ResourceUpdate(verified=True)
    resource = resource_service.update_resource(db, resource_id, update_data)
    
    return {
        "message": "资源验证成功",
        "resource": resource.to_dict()
    }