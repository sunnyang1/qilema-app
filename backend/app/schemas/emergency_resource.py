"""
急救资源Schema验证

提供急救资源查询、周边搜索、导航等数据验证
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum

from app.core.schemas import BaseSchema


# ========== 枚举定义 ==========

class ResourceType(str, Enum):
    """资源类型枚举"""
    HOSPITAL = "hospital"
    AED = "aed"
    EMERGENCY_STATION = "emergency_station"
    PHARMACY = "pharmacy"
    FIRST_AID_POINT = "first_aid_point"


class HospitalLevel(str, Enum):
    """医院等级枚举"""
    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"
    COMMUNITY = "community"
    SPECIALIZED = "specialized"


class ResourceStatus(str, Enum):
    """资源状态枚举"""
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"


# ========== 急救资源相关 ==========

class ResourceBase(BaseModel):
    """急救资源基础模型"""
    resource_type: ResourceType = Field(..., description="资源类型")
    resource_name: str = Field(..., min_length=1, max_length=200, description="资源名称")
    description: Optional[str] = Field(None, description="资源描述")


class ResourceCreate(ResourceBase):
    """创建急救资源"""
    address: str = Field(..., min_length=1, description="详细地址")
    latitude: float = Field(..., ge=-90, le=90, description="纬度")
    longitude: float = Field(..., ge=-180, le=180, description="经度")
    city: Optional[str] = Field(None, description="城市")
    district: Optional[str] = Field(None, description="区县")
    province: Optional[str] = Field(None, description="省份")
    
    phone: Optional[str] = Field(None, description="联系电话")
    emergency_phone: Optional[str] = Field(None, description="急救电话")
    website: Optional[str] = Field(None, description="官网")
    
    status: ResourceStatus = Field(ResourceStatus.ACTIVE, description="资源状态")
    is_24h: bool = Field(False, description="是否24小时服务")
    has_emergency: bool = Field(False, description="是否有急诊")
    
    # 医院特有字段
    hospital_level: Optional[HospitalLevel] = Field(None, description="医院等级")
    bed_count: Optional[int] = Field(None, ge=0, description="床位数")
    has_icu: bool = Field(False, description="是否有ICU")
    has_surgery: bool = Field(False, description="是否有手术室")
    has_ambulance: bool = Field(False, description="是否有救护车")
    
    # AED设备特有字段
    aed_location: Optional[str] = Field(None, description="AED具体位置")
    floor: Optional[str] = Field(None, description="楼层")
    accessible_hours: Optional[str] = Field(None, description="可获取时间")
    access_instructions: Optional[str] = Field(None, description="获取说明")
    
    service_radius: Optional[int] = Field(None, ge=0, description="服务半径(米)")
    capacity: Optional[int] = Field(None, ge=0, description="服务能力(人/天)")
    
    source: Optional[str] = Field(None, description="数据来源")
    
    @validator('latitude', 'longitude')
    def validate_coordinates(cls, v):
        if v == 0:
            raise ValueError('坐标不能为0')
        return v


class ResourceUpdate(BaseModel):
    """更新急救资源"""
    resource_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    address: Optional[str] = Field(None, min_length=1)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    phone: Optional[str] = None
    emergency_phone: Optional[str] = None
    status: Optional[ResourceStatus] = None
    is_24h: Optional[bool] = None
    hospital_level: Optional[HospitalLevel] = None
    bed_count: Optional[int] = Field(None, ge=0)
    has_icu: Optional[bool] = None
    has_surgery: Optional[bool] = None
    has_ambulance: Optional[bool] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    verified: Optional[bool] = None


class ResourceResponse(ResourceBase):
    """急救资源响应"""
    id: int
    address: str
    latitude: float
    longitude: float
    city: Optional[str]
    district: Optional[str]
    province: Optional[str]
    phone: Optional[str]
    emergency_phone: Optional[str]
    website: Optional[str]
    status: ResourceStatus
    is_24h: bool
    has_emergency: bool
    hospital_level: Optional[HospitalLevel]
    bed_count: Optional[int]
    has_icu: bool
    has_surgery: bool
    has_ambulance: bool
    aed_location: Optional[str]
    floor: Optional[str]
    accessible_hours: Optional[str]
    access_instructions: Optional[str]
    service_radius: Optional[int]
    capacity: Optional[int]
    rating: Optional[float]
    review_count: Optional[int]
    source: Optional[str]
    verified: bool
    last_verified_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ResourceQuery(BaseModel):
    """急救资源查询"""
    resource_type: Optional[ResourceType] = Field(None, description="资源类型")
    status: Optional[ResourceStatus] = Field(ResourceStatus.ACTIVE, description="资源状态")
    city: Optional[str] = Field(None, description="城市")
    district: Optional[str] = Field(None, description="区县")
    is_24h: Optional[bool] = Field(None, description="是否24小时服务")
    has_emergency: Optional[bool] = Field(None, description="是否有急诊")
    hospital_level: Optional[HospitalLevel] = Field(None, description="医院等级")
    has_icu: Optional[bool] = Field(None, description="是否有ICU")
    
    limit: int = Field(50, ge=1, le=200, description="返回数量限制")
    offset: int = Field(0, ge=0, description="偏移量")


# ========== 周边搜索 ==========

class NearbySearchRequest(BaseModel):
    """周边搜索请求"""
    latitude: float = Field(..., ge=-90, le=90, description="当前位置纬度")
    longitude: float = Field(..., ge=-180, le=180, description="当前位置经度")
    resource_type: Optional[ResourceType] = Field(None, description="资源类型(不指定则搜索所有)")
    radius: int = Field(3000, ge=100, le=20000, description="搜索半径(米)")
    
    is_24h: Optional[bool] = Field(None, description="是否24小时服务")
    has_emergency: Optional[bool] = Field(None, description="是否有急诊")
    hospital_level: Optional[HospitalLevel] = Field(None, description="医院等级")
    
    sort_by: str = Field("distance", description="排序方式(distance/rating)")
    limit: int = Field(20, ge=1, le=100, description="返回数量限制")


class NearbyResource(BaseModel):
    """周边资源"""
    id: int
    resource_type: ResourceType
    resource_name: str
    address: str
    latitude: float
    longitude: float
    distance: float = Field(..., description="距离(米)")
    duration: Optional[int] = Field(None, description="预计时间(秒)")
    phone: Optional[str]
    emergency_phone: Optional[str]
    is_24h: bool
    has_emergency: bool
    hospital_level: Optional[HospitalLevel]
    rating: Optional[float]
    has_icu: bool
    has_ambulance: bool
    
    class Config:
        from_attributes = True


# ========== 导航相关 ==========

class NavigationRequest(BaseModel):
    """导航请求"""
    start_latitude: float = Field(..., ge=-90, le=90, description="起点纬度")
    start_longitude: float = Field(..., ge=-180, le=180, description="起点经度")
    end_latitude: float = Field(..., ge=-90, le=90, description="终点纬度")
    end_longitude: float = Field(..., ge=-180, le=180, description="终点经度")
    route_type: str = Field("driving", description="路线类型(driving/walking)")


class NavigationResponse(BaseModel):
    """导航响应"""
    distance: float = Field(..., description="距离(米)")
    duration: int = Field(..., description="预计时间(秒)")
    route_type: str = Field(..., description="路线类型")
    route_steps: List[dict] = Field(default_factory=list, description="路线步骤")
    
    # 目标信息
    target_resource_id: Optional[int] = Field(None, description="目标资源ID")
    target_resource_name: Optional[str] = Field(None, description="目标资源名称")


# ========== 资源设施相关 ==========

class ResourceFacilityCreate(BaseModel):
    """创建资源设施"""
    resource_id: int = Field(..., description="资源ID")
    facility_type: str = Field(..., description="设施类型")
    facility_name: Optional[str] = Field(None, description="设施名称")
    description: Optional[str] = Field(None, description="设施描述")
    quantity: Optional[int] = Field(None, ge=0, description="数量")
    is_available: bool = Field(True, description="是否可用")


class ResourceFacilityResponse(BaseModel):
    """资源设施响应"""
    id: int
    resource_id: int
    facility_type: str
    facility_name: Optional[str]
    description: Optional[str]
    quantity: Optional[int]
    is_available: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== 资源科室相关 ==========

class ResourceDepartmentCreate(BaseModel):
    """创建资源科室"""
    resource_id: int = Field(..., description="资源ID")
    department_name: str = Field(..., description="科室名称")
    department_type: Optional[str] = Field(None, description="科室类型")
    is_emergency: bool = Field(False, description="是否急诊科室")
    phone: Optional[str] = Field(None, description="科室电话")
    has_beds: bool = Field(True, description="是否有床位")
    available_beds: Optional[int] = Field(None, ge=0, description="可用床位数")


class ResourceDepartmentResponse(BaseModel):
    """资源科室响应"""
    id: int
    resource_id: int
    department_name: str
    department_type: Optional[str]
    is_emergency: bool
    phone: Optional[str]
    has_beds: bool
    available_beds: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== 使用日志相关 ==========

class ResourceUsageLogCreate(BaseModel):
    """创建资源使用日志"""
    resource_id: Optional[int] = Field(None, description="资源ID")
    usage_type: str = Field(..., description="使用类型(view/navigate/call)")
    user_location: Optional[str] = Field(None, description="用户位置(经度,纬度)")
    distance: Optional[float] = Field(None, ge=0, description="距离(米)")


class ResourceUsageLogResponse(BaseModel):
    """资源使用日志响应"""
    id: int
    resource_id: Optional[int]
    user_id: Optional[str]
    usage_type: str
    user_location: Optional[str]
    distance: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== 统计信息 ==========

class ResourceStatistics(BaseModel):
    """资源统计信息"""
    total_resources: int = Field(..., description="总资源数")
    by_type: dict = Field(default_factory=dict, description="按类型分组")
    by_status: dict = Field(default_factory=dict, description="按状态分组")
    by_city: dict = Field(default_factory=dict, description="按城市分组")
    
    hospitals_with_emergency: int = Field(0, description="有急诊的医院数")
    aed_count: int = Field(0, description="AED设备数")
    aed_24h_accessible: int = Field(0, description="24小时可获取的AED数")


class PopularResource(BaseModel):
    """热门资源"""
    id: int
    resource_type: ResourceType
    resource_name: str
    view_count: int = Field(..., description="查看次数")
    navigate_count: int = Field(..., description="导航次数")