"""
急救资源服务

实现周边搜索、导航、资源管理等核心功能
"""

import math
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.emergency_resource_model import (
    EmergencyResource,
    NavigationRoute,
    ResourceDepartment,
    ResourceFacility,
    ResourceUsageLog,
)
from app.schemas.emergency_resource import (
    NavigationRequest,
    NavigationResponse,
    NearbySearchRequest,
    PopularResource,
    ResourceCreate,
    ResourceDepartmentCreate,
    ResourceFacilityCreate,
    ResourceQuery,
    ResourceStatistics,
    ResourceStatus,
    ResourceType,
    ResourceUpdate,
)


class EmergencyResourceService:
    """急救资源服务"""

    # 地图配置(实际应该从配置文件读取)
    AMAP_API_KEY = "your_amap_api_key"  # 高德地图API密钥
    BAIDU_API_KEY = "your_baidu_api_key"  # 百度地图API密钥

    def calculate_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """
        计算两点间距离(米)

        使用Haversine公式计算球面距离
        """
        # 将经纬度转换为弧度
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # 地球半径(米)
        earth_radius = 6371000

        # Haversine公式
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )

        c = 2 * math.asin(math.sqrt(a))

        distance = earth_radius * c

        return round(distance, 2)

    def search_nearby_resources(
        self, db: Session, request: NearbySearchRequest, user_id: Optional[str] = None
    ) -> List[Dict]:
        """
        搜索周边急救资源

        基于用户位置和搜索半径,查找附近的急救资源
        """
        boundaries = self._calculate_search_boundaries(
            request.latitude, request.longitude, request.radius
        )
        resources = self._query_resources_in_bounds(db, request, boundaries)
        results = self._calculate_distances_and_filter(resources, request)

        if request.sort_by == "distance":
            self._enrich_with_route_info(results, request)
            self._sort_results(results, "distance")
        elif request.sort_by == "rating":
            self._sort_results(results, "rating")

        # 记录使用日志
        if user_id and results:
            self._log_resource_usage_batch(
                db, results, user_id, f"{request.longitude},{request.latitude}"
            )

        # 截取指定数量
        return results[: request.limit]

    def _calculate_search_boundaries(
        self, latitude: float, longitude: float, radius: float
    ) -> Dict[str, float]:
        """计算搜索边界的经纬度"""
        # 纬度1度约等于111公里
        lat_delta = radius / 111000.0
        # 经度1度的距离随纬度变化,这里简化处理
        lon_delta = radius / (111000.0 * math.cos(math.radians(latitude)))

        return {
            "min_lat": latitude - lat_delta,
            "max_lat": latitude + lat_delta,
            "min_lon": longitude - lon_delta,
            "max_lon": longitude + lon_delta,
        }

    def _query_resources_in_bounds(
        self, db: Session, request: NearbySearchRequest, boundaries: Dict[str, float]
    ) -> List[EmergencyResource]:
        """查询边界内的资源并应用筛选条件"""
        query = db.query(EmergencyResource).filter(
            EmergencyResource.is_active == 1,
            EmergencyResource.latitude >= boundaries["min_lat"],
            EmergencyResource.latitude <= boundaries["max_lat"],
            EmergencyResource.longitude >= boundaries["min_lon"],
            EmergencyResource.longitude <= boundaries["max_lon"],
        )

        # 应用筛选条件
        if request.resource_type:
            query = query.filter(
                EmergencyResource.resource_type == request.resource_type.value
            )

        if request.is_24h is not None:
            query = query.filter(
                EmergencyResource.is_24h == (1 if request.is_24h else 0)
            )

        if request.has_emergency is not None:
            query = query.filter(
                EmergencyResource.has_emergency == (1 if request.has_emergency else 0)
            )

        if request.hospital_level:
            query = query.filter(
                EmergencyResource.hospital_level == request.hospital_level.value
            )

        # 多取一些,后续筛选
        return query.limit(request.limit * 2).all()

    def _calculate_distances_and_filter(
        self, resources: List[EmergencyResource], request: NearbySearchRequest
    ) -> List[Dict]:
        """计算距离并筛选符合条件的资源"""
        results = []
        for resource in resources:
            distance = self.calculate_distance(
                request.latitude,
                request.longitude,
                resource.latitude,
                resource.longitude,
            )

            if distance <= request.radius:
                result = resource.to_dict()
                result["distance"] = distance
                result["duration"] = None
                result["_resource_id"] = resource.id  # 临时保存用于日志记录
                results.append(result)

        return results

    def _enrich_with_route_info(
        self, results: List[Dict], request: NearbySearchRequest
    ):
        """为结果添加路线信息"""
        for result in results:
            route_info = self._get_route_info(
                request.latitude,
                request.longitude,
                result["latitude"],
                result["longitude"],
                "driving",
            )
            result["duration"] = route_info.get("duration", None)

    def _sort_results(self, results: List[Dict], sort_by: str):
        """对结果进行排序"""
        if sort_by == "distance":
            results.sort(key=lambda x: x["distance"])
        elif sort_by == "rating":
            results.sort(key=lambda x: x["rating"] or 0, reverse=True)

    def _log_resource_usage_batch(
        self, db: Session, results: List[Dict], user_id: str, user_location: str
    ):
        """批量记录资源使用日志"""
        for result in results:
            self._log_resource_usage(
                db,
                result["_resource_id"],
                user_id,
                "view",
                user_location,
                result["distance"],
            )
            # 移除临时字段
            del result["_resource_id"]

    def get_navigation_route(
        self, db: Session, request: NavigationRequest, user_id: Optional[str] = None
    ) -> NavigationResponse:
        """
        获取导航路线

        调用地图API获取最佳导航路线
        """
        # 调用高德/百度地图API获取路线
        route_info = self._get_route_info(
            request.start_latitude,
            request.start_longitude,
            request.end_latitude,
            request.end_longitude,
            request.route_type,
        )

        # 创建导航记录
        if user_id:
            navigation = NavigationRoute(
                user_id=user_id,
                start_latitude=request.start_latitude,
                start_longitude=request.start_longitude,
                end_latitude=request.end_latitude,
                end_longitude=request.end_longitude,
                distance=route_info["distance"],
                duration=route_info["duration"],
                route_type=request.route_type,
                status="planned",
            )
            db.add(navigation)
            db.commit()

        # 查找目标资源
        resource = (
            db.query(EmergencyResource)
            .filter(
                EmergencyResource.latitude == request.end_latitude,
                EmergencyResource.longitude == request.end_longitude,
            )
            .first()
        )

        return NavigationResponse(
            distance=route_info["distance"],
            duration=route_info["duration"],
            route_type=request.route_type,
            route_steps=route_info.get("steps", []),
            target_resource_id=resource.id if resource else None,
            target_resource_name=resource.resource_name if resource else None,
        )

    def _get_route_info(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        route_type: str,
    ) -> Dict:
        """
        获取路线信息

        调用地图API获取实际路线、距离和耗时
        """
        # 实际应该调用高德/百度地图API
        # 这里返回模拟数据

        # 计算直线距离
        distance = self.calculate_distance(start_lat, start_lon, end_lat, end_lon)

        # 估算耗时
        if route_type == "walking":
            # 步行速度: 5km/h
            duration = int(distance / 5000 * 3600)
        else:  # driving
            # 驾车速度: 30km/h(考虑城市路况)
            duration = int(distance / 30000 * 3600)

        return {
            "distance": distance,
            "duration": duration,
            "steps": [
                {"instruction": "出发", "distance": 0},
                {
                    "instruction": f"前往目的地,距离{distance:.0f}米",
                    "distance": distance,
                },
            ],
        }

    # ========== 资源管理 ==========

    def create_resource(
        self, db: Session, resource_data: ResourceCreate
    ) -> EmergencyResource:
        """创建急救资源"""
        resource = EmergencyResource(**resource_data.dict())
        db.add(resource)
        db.commit()
        db.refresh(resource)
        return resource

    def update_resource(
        self, db: Session, resource_id: int, update_data: ResourceUpdate
    ) -> Optional[EmergencyResource]:
        """更新急救资源"""
        resource = (
            db.query(EmergencyResource)
            .filter(EmergencyResource.id == resource_id)
            .first()
        )
        if not resource:
            return None

        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(resource, field, value)

        resource.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(resource)
        return resource

    def get_resource(
        self, db: Session, resource_id: int
    ) -> Optional[EmergencyResource]:
        """获取急救资源详情"""
        return (
            db.query(EmergencyResource)
            .filter(EmergencyResource.id == resource_id)
            .first()
        )

    def query_resources(
        self, db: Session, query_params: ResourceQuery
    ) -> List[EmergencyResource]:
        """查询急救资源"""
        query = db.query(EmergencyResource)

        if query_params.resource_type:
            query = query.filter(
                EmergencyResource.resource_type == query_params.resource_type.value
            )

        if query_params.status:
            query = query.filter(EmergencyResource.status == query_params.status.value)

        if query_params.city:
            query = query.filter(EmergencyResource.city == query_params.city)

        if query_params.district:
            query = query.filter(EmergencyResource.district == query_params.district)

        if query_params.is_24h is not None:
            query = query.filter(EmergencyResource.is_24h == query_params.is_24h)

        if query_params.has_emergency is not None:
            query = query.filter(
                EmergencyResource.has_emergency == query_params.has_emergency
            )

        if query_params.hospital_level:
            query = query.filter(
                EmergencyResource.hospital_level == query_params.hospital_level.value
            )

        if query_params.has_icu is not None:
            query = query.filter(EmergencyResource.has_icu == query_params.has_icu)

        return (
            query.order_by(EmergencyResource.created_at.desc())
            .offset(query_params.offset)
            .limit(query_params.limit)
            .all()
        )

    def delete_resource(self, db: Session, resource_id: int) -> bool:
        """删除急救资源"""
        resource = (
            db.query(EmergencyResource)
            .filter(EmergencyResource.id == resource_id)
            .first()
        )
        if not resource:
            return False

        db.delete(resource)
        db.commit()
        return True

    # ========== 资源设施管理 ==========

    def create_facility(
        self, db: Session, facility_data: ResourceFacilityCreate
    ) -> ResourceFacility:
        """创建资源设施"""
        facility = ResourceFacility(**facility_data.dict())
        db.add(facility)
        db.commit()
        db.refresh(facility)
        return facility

    def get_resource_facilities(
        self, db: Session, resource_id: int
    ) -> List[ResourceFacility]:
        """获取资源设施列表"""
        return (
            db.query(ResourceFacility)
            .filter(ResourceFacility.resource_id == resource_id)
            .all()
        )

    # ========== 资源科室管理 ==========

    def create_department(
        self, db: Session, department_data: ResourceDepartmentCreate
    ) -> ResourceDepartment:
        """创建资源科室"""
        department = ResourceDepartment(**department_data.dict())
        db.add(department)
        db.commit()
        db.refresh(department)
        return department

    def get_resource_departments(
        self, db: Session, resource_id: int
    ) -> List[ResourceDepartment]:
        """获取资源科室列表"""
        return (
            db.query(ResourceDepartment)
            .filter(ResourceDepartment.resource_id == resource_id)
            .all()
        )

    # ========== 统计分析 ==========

    def get_resource_statistics(self, db: Session) -> ResourceStatistics:
        """获取资源统计信息"""
        # 总资源数
        total_resources = db.query(func.count(EmergencyResource.id)).scalar()

        # 按类型分组
        by_type = {}
        for resource_type in ResourceType:
            count = (
                db.query(func.count(EmergencyResource.id))
                .filter(EmergencyResource.resource_type == resource_type.value)
                .scalar()
            )
            by_type[resource_type.value] = count

        # 按状态分组
        by_status = {}
        for status in ResourceStatus:
            count = (
                db.query(func.count(EmergencyResource.id))
                .filter(EmergencyResource.status == status.value)
                .scalar()
            )
            by_status[status.value] = count

        # 按城市分组
        by_city = {}
        cities = (
            db.query(EmergencyResource.city)
            .filter(EmergencyResource.city.isnot(None))
            .distinct()
            .all()
        )
        for city in cities:
            count = (
                db.query(func.count(EmergencyResource.id))
                .filter(EmergencyResource.city == city[0])
                .scalar()
            )
            by_city[city[0]] = count

        # 统计特定资源
        hospitals_with_emergency = (
            db.query(func.count(EmergencyResource.id))
            .filter(
                EmergencyResource.resource_type == ResourceType.HOSPITAL.value,
                EmergencyResource.has_emergency.is_(True),
            )
            .scalar()
        )

        aed_count = (
            db.query(func.count(EmergencyResource.id))
            .filter(EmergencyResource.resource_type == ResourceType.AED.value)
            .scalar()
        )

        aed_24h_accessible = (
            db.query(func.count(EmergencyResource.id))
            .filter(
                EmergencyResource.resource_type == ResourceType.AED.value,
                EmergencyResource.is_24h.is_(True),
            )
            .scalar()
        )

        return ResourceStatistics(
            total_resources=total_resources,
            by_type=by_type,
            by_status=by_status,
            by_city=by_city,
            hospitals_with_emergency=hospitals_with_emergency,
            aed_count=aed_count,
            aed_24h_accessable=aed_24h_accessible,
        )

    def get_popular_resources(
        self, db: Session, limit: int = 10
    ) -> List[PopularResource]:
        """获取热门资源"""
        # 统计查看次数和导航次数
        view_counts = (
            db.query(
                ResourceUsageLog.resource_id,
                func.count(ResourceUsageLog.id).label("view_count"),
            )
            .filter(ResourceUsageLog.usage_type == "view")
            .group_by(ResourceUsageLog.resource_id)
            .all()
        )

        navigate_counts = (
            db.query(
                ResourceUsageLog.resource_id,
                func.count(ResourceUsageLog.id).label("navigate_count"),
            )
            .filter(ResourceUsageLog.usage_type == "navigate")
            .group_by(ResourceUsageLog.resource_id)
            .all()
        )

        # 合并统计结果
        resource_stats = {}
        for resource_id, view_count in view_counts:
            resource_stats[resource_id] = {
                "view_count": view_count,
                "navigate_count": 0,
            }

        for resource_id, navigate_count in navigate_counts:
            if resource_id in resource_stats:
                resource_stats[resource_id]["navigate_count"] = navigate_count
            else:
                resource_stats[resource_id] = {
                    "view_count": 0,
                    "navigate_count": navigate_count,
                }

        # 获取资源详情并排序
        popular_resources = []
        for resource_id, stats in resource_stats.items():
            resource = (
                db.query(EmergencyResource)
                .filter(EmergencyResource.id == resource_id)
                .first()
            )

            if resource:
                popular_resources.append(
                    PopularResource(
                        id=resource.id,
                        resource_type=resource.resource_type,
                        resource_name=resource.resource_name,
                        view_count=stats["view_count"],
                        navigate_count=stats["navigate_count"],
                    )
                )

        # 按总使用次数排序
        popular_resources.sort(
            key=lambda x: x.view_count + x.navigate_count, reverse=True
        )

        return popular_resources[:limit]

    # ========== 辅助方法 ==========

    def _log_resource_usage(
        self,
        db: Session,
        resource_id: int,
        user_id: str,
        usage_type: str,
        user_location: str,
        distance: float,
    ):
        """记录资源使用日志"""
        log = ResourceUsageLog(
            resource_id=resource_id,
            user_id=user_id,
            usage_type=usage_type,
            user_location=user_location,
            distance=distance,
        )
        db.add(log)
        db.commit()
