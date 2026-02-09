"""
急救资源SQLAlchemy模型
"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, Text, Boolean, Enum
from sqlalchemy.orm import relationship as db_relationship
from app.core.database import Base


class AEDStatus(str, PyEnum):
    """AED设备状态"""
    ACTIVE = "active"           # 可用
    MAINTENANCE = "maintenance" # 维护中
    INACTIVE = "inactive"       # 不可用
    DEPRECATED = "deprecated"   # 已废弃


class EmergencyResource(Base):
    """急救资源模型"""
    __tablename__ = "emergency_resources"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    resource_type = Column(String(50), nullable=False, index=True, comment="资源类型: hospital/aed/emergency_station/pharmacy/first_aid_point")
    resource_name = Column(String(200), nullable=False, comment="资源名称")
    description = Column(Text, nullable=True, comment="资源描述")

    # 位置信息
    latitude = Column(Float, nullable=False, comment="纬度")
    longitude = Column(Float, nullable=False, comment="经度")
    address = Column(String(500), nullable=True, comment="详细地址")
    province = Column(String(100), nullable=True, comment="省份")
    city = Column(String(100), nullable=False, comment="城市")
    district = Column(String(100), nullable=True, comment="区县")

    # 联系信息
    phone = Column(String(20), nullable=True, comment="联系电话")
    website = Column(String(255), nullable=True, comment="网站")
    email = Column(String(100), nullable=True, comment="邮箱")

    # 医院特有字段
    hospital_level = Column(String(50), nullable=True, comment="医院等级: tier_1/tier_2/tier_3/community/specialized")
    has_emergency = Column(Integer, nullable=False, default=0, comment="是否有急诊: 0=否 1=是")
    has_ambulance = Column(Integer, nullable=False, default=0, comment="是否有救护车: 0=否 1=是")
    bed_count = Column(Integer, nullable=True, comment="床位数")
    emergency_beds = Column(Integer, nullable=True, comment="急诊床位数")

    # AED特有字段（基础）
    aed_status = Column(String(20), nullable=True, comment="AED状态: active/maintenance/inactive/deprecated")
    last_maintenance = Column(DateTime, nullable=True, comment="最后维护时间")
    
    # AED特有字段（扩展）
    aed_brand = Column(String(100), nullable=True, comment="AED品牌/厂商")
    aed_model = Column(String(100), nullable=True, comment="AED型号")
    aed_sn = Column(String(100), nullable=True, comment="AED序列号")
    aed_location_desc = Column(String(500), nullable=True, comment="AED具体位置描述（如：一楼大厅电梯旁）")
    aed_access_instructions = Column(String(500), nullable=True, comment="AED获取说明（如：24小时开放/需联系物业）")
    aed_installation_date = Column(DateTime, nullable=True, comment="AED安装日期")
    aed_battery_expiry = Column(DateTime, nullable=True, comment="AED电池过期日期")
    aed_pad_expiry = Column(DateTime, nullable=True, comment="AED电极片过期日期")
    aed_last_inspection = Column(DateTime, nullable=True, comment="AED最后检查日期")
    aed_manager_name = Column(String(100), nullable=True, comment="AED负责人姓名")
    aed_manager_phone = Column(String(20), nullable=True, comment="AED负责人电话")
    aed_image_url = Column(String(500), nullable=True, comment="AED设备照片URL")
    aed_photos = Column(Text, nullable=True, comment="AED多角度照片URL（JSON数组）")

    # 营业时间
    is_24h = Column(Integer, nullable=False, default=0, comment="是否24小时营业: 0=否 1=是")
    open_hours = Column(String(200), nullable=True, comment="营业时间")

    # 其他
    distance = Column(Float, nullable=True, comment="距离(米), 用于查询结果")
    rating = Column(Float, nullable=True, comment="评分(1-5)")
    review_count = Column(Integer, nullable=True, comment="评论数")

    # 状态
    is_active = Column(Integer, nullable=False, default=1, comment="是否启用: 0=否 1=是")

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow, comment="更新时间")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        data = {
            "id": self.id,
            "resource_type": self.resource_type,
            "resource_name": self.resource_name,
            "description": self.description,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "province": self.province,
            "city": self.city,
            "district": self.district,
            "phone": self.phone,
            "website": self.website,
            "email": self.email,
            "hospital_level": self.hospital_level,
            "has_emergency": bool(self.has_emergency),
            "has_ambulance": bool(self.has_ambulance),
            "bed_count": self.bed_count,
            "emergency_beds": self.emergency_beds,
            "is_24h": bool(self.is_24h),
            "open_hours": self.open_hours,
            "distance": self.distance,
            "rating": self.rating,
            "review_count": self.review_count,
            "is_active": bool(self.is_active),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # AED专用字段
        if self.resource_type == "aed":
            data.update({
                "aed_status": self.aed_status,
                "last_maintenance": self.last_maintenance.isoformat() if self.last_maintenance else None,
                "aed_brand": self.aed_brand,
                "aed_model": self.aed_model,
                "aed_sn": self.aed_sn,
                "aed_location_desc": self.aed_location_desc,
                "aed_access_instructions": self.aed_access_instructions,
                "aed_installation_date": self.aed_installation_date.isoformat() if self.aed_installation_date else None,
                "aed_battery_expiry": self.aed_battery_expiry.isoformat() if self.aed_battery_expiry else None,
                "aed_pad_expiry": self.aed_pad_expiry.isoformat() if self.aed_pad_expiry else None,
                "aed_last_inspection": self.aed_last_inspection.isoformat() if self.aed_last_inspection else None,
                "aed_manager_name": self.aed_manager_name,
                "aed_manager_phone": self.aed_manager_phone,
                "aed_image_url": self.aed_image_url,
                "aed_photos": self.aed_photos,
            })
        
        return data


class ResourceFacility(Base):
    """资源设施模型"""
    __tablename__ = "resource_facilities"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    resource_id = Column(Integer, ForeignKey("emergency_resources.id"), nullable=False, index=True, comment="资源ID")
    facility_name = Column(String(100), nullable=False, comment="设施名称")
    facility_type = Column(String(50), nullable=False, comment="设施类型")
    description = Column(Text, nullable=True, comment="设施描述")
    is_available = Column(Integer, nullable=False, default=1, comment="是否可用: 0=否 1=是")
    created_at = Column(DateTime, nullable=False, default=lambda: __import__(datetime).datetime.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=True, comment="更新时间")


class ResourceDepartment(Base):
    """资源科室模型"""
    __tablename__ = "resource_departments"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    resource_id = Column(Integer, ForeignKey("emergency_resources.id"), nullable=False, index=True, comment="资源ID")
    department_name = Column(String(100), nullable=False, comment="科室名称")
    department_code = Column(String(50), nullable=True, comment="科室代码")
    description = Column(Text, nullable=True, comment="科室描述")
    phone = Column(String(20), nullable=True, comment="联系电话")
    is_active = Column(Integer, nullable=False, default=1, comment="是否启用: 0=否 1=是")
    created_at = Column(DateTime, nullable=False, default=lambda: __import__(datetime).datetime.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=True, comment="更新时间")


class ResourceUsageLog(Base):
    """资源使用日志模型"""
    __tablename__ = "resource_usage_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    resource_id = Column(Integer, ForeignKey("emergency_resources.id"), nullable=False, index=True, comment="资源ID")
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True, index=True, comment="用户ID")
    usage_type = Column(String(50), nullable=False, comment="使用类型: navigation/inquiry/favorite")
    usage_time = Column(DateTime, nullable=False, comment="使用时间")
    extra_data = Column(Text, nullable=True, comment="元数据(JSON)")
    created_at = Column(DateTime, nullable=False, default=lambda: __import__(datetime).datetime.now(), comment="创建时间")


class NavigationRoute(Base):
    """导航路线模型"""
    __tablename__ = "navigation_routes"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True, comment="用户ID")
    start_latitude = Column(Float, nullable=False, comment="起点纬度")
    start_longitude = Column(Float, nullable=False, comment="起点经度")
    end_latitude = Column(Float, nullable=False, comment="终点纬度")
    end_longitude = Column(Float, nullable=False, comment="终点经度")
    end_resource_id = Column(Integer, ForeignKey("emergency_resources.id"), nullable=True, index=True, comment="终点资源ID")
    route_type = Column(String(50), nullable=False, comment="路线类型")
    distance = Column(Float, nullable=True, comment="距离(米)")
    duration = Column(Integer, nullable=True, comment="预计时长(秒)")
    route_data = Column(Text, nullable=True, comment="路线数据(JSON)")
    created_at = Column(DateTime, nullable=False, default=lambda: __import__(datetime).datetime.now(), comment="创建时间")

