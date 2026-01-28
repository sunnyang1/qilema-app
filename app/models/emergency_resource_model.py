"""
急救资源SQLAlchemy模型
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, Text, Boolean
from sqlalchemy.orm import relationship as db_relationship
from app.core.database import Base


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

    # AED特有字段
    aed_status = Column(String(20), nullable=True, comment="AED状态: active/maintenance/inactive/deprecated")
    last_maintenance = Column(DateTime, nullable=True, comment="最后维护时间")

    # 营业时间
    is_24h = Column(Integer, nullable=False, default=0, comment="是否24小时营业: 0=否 1=是")
    open_hours = Column(String(200), nullable=True, comment="营业时间")

    # 其他
    distance = Column(Float, nullable=True, comment="距离(米), 用于查询结果")
    rating = Column(Float, nullable=True, comment="评分(1-5)")
    review_count = Column(Integer, nullable=True, comment="评论数")

    # 状态
    is_active = Column(Integer, nullable=False, default=1, comment="是否启用: 0=否 1=是")

    created_at = Column(DateTime, nullable=False, default=lambda: __import__(datetime).datetime.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=True, comment="更新时间")


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

