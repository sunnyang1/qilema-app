"""
AED设备服务

提供AED设备管理、批量导入、地图查询、导航等功能
"""

import json
import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app.models.emergency_resource_model import AEDStatus, EmergencyResource
from app.services.base_service import BaseService
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session


class AEDService(BaseService[EmergencyResource]):
    """AED设备服务"""

    model_class = EmergencyResource
    cache_prefix = "aed"

    @classmethod
    def get_nearby_aeds(
        cls,
        db: Session,
        latitude: float,
        longitude: float,
        radius: float = 5000,  # 默认5公里
        only_active: bool = True,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        获取附近的AED设备

        Args:
            db: 数据库会话
            latitude: 中心点纬度
            longitude: 中心点经度
            radius: 搜索半径（米）
            only_active: 是否只返回可用状态的AED
            limit: 返回数量限制

        Returns:
            AED设备列表，包含距离信息
        """
        # 计算搜索边界
        boundaries = cls._calculate_search_boundaries(latitude, longitude, radius)

        # 基础查询
        query = db.query(EmergencyResource).filter(
            EmergencyResource.resource_type == "aed",
            EmergencyResource.is_active == 1,
            EmergencyResource.latitude >= boundaries["min_lat"],
            EmergencyResource.latitude <= boundaries["max_lat"],
            EmergencyResource.longitude >= boundaries["min_lon"],
            EmergencyResource.longitude <= boundaries["max_lon"],
        )

        # 只返回可用状态的AED
        if only_active:
            query = query.filter(
                or_(
                    EmergencyResource.aed_status == AEDStatus.ACTIVE.value,
                    EmergencyResource.aed_status == None,
                )
            )

        # 获取候选结果
        candidates = query.limit(limit * 2).all()

        # 计算精确距离并筛选
        results = []
        for aed in candidates:
            distance = cls._calculate_distance(
                latitude, longitude, aed.latitude, aed.longitude
            )

            if distance <= radius:
                aed_dict = aed.to_dict()
                aed_dict["distance"] = round(distance, 2)
                aed_dict["distance_text"] = cls._format_distance(distance)
                # 估算到达时间（步行速度约1.2m/s）
                duration_seconds = int(distance / 1.2)
                aed_dict["duration_seconds"] = duration_seconds
                aed_dict["duration_text"] = cls._format_duration(duration_seconds)
                results.append(aed_dict)

        # 按距离排序
        results.sort(key=lambda x: x["distance"])

        return results[:limit]

    @classmethod
    def get_aed_navigation_url(
        cls,
        from_lat: float,
        from_lon: float,
        to_lat: float,
        to_lon: float,
        nav_type: str = "walking",
    ) -> Dict[str, str]:
        """
        获取AED导航链接

        支持高德地图、百度地图、腾讯地图、苹果地图、谷歌地图

        Args:
            from_lat: 起点纬度
            from_lon: 起点经度
            to_lat: 终点纬度
            to_lon: 终点经度
            nav_type: 导航类型 walking/driving/bus

        Returns:
            各平台的导航链接
        """
        from_coord_lonlat = f"{from_lon},{from_lat}"
        to_coord_lonlat = f"{to_lon},{to_lat}"
        from_coord_latlon = f"{from_lat},{from_lon}"
        to_coord_latlon = f"{to_lat},{to_lon}"

        return {
            "amap": (
                f"https://uri.amap.com/navigation?"
                f"from={from_coord_lonlat},起点&to={to_coord_lonlat},AED位置&mode={nav_type}&callnative=1"
            ),
            "baidu": (
                f"https://api.map.baidu.com/direction?origin=latlng:{from_coord_latlon}|"
                f"name:起点&destination=latlng:{to_coord_latlon}|name:AED&mode={nav_type}"
            ),
            "qqmap": (
                f"https://apis.map.qq.com/tools/routeplan/type={nav_type}&"
                f"from=起点&fromcoord={from_coord_latlon}&"
                f"to=AED位置&tocoord={to_coord_latlon}"
            ),
            "apple": (
                f"http://maps.apple.com/?saddr={from_lat},{from_lon}&"
                f"daddr={to_lat},{to_lon}&dirflg={cls._get_apple_nav_flag(nav_type)}"
            ),
            "google": (
                f"https://www.google.com/maps/dir/?api=1&origin={from_lat},{from_lon}&"
                f"destination={to_lat},{to_lon}&travelmode={nav_type}"
            ),
        }

    @classmethod
    def import_aeds_batch(
        cls,
        db: Session,
        aed_data_list: List[Dict[str, Any]],
        operator_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        批量导入AED设备

        Args:
            db: 数据库会话
            aed_data_list: AED数据列表
            operator_id: 操作人ID

        Returns:
            导入结果统计
        """
        success_count = 0
        failed_count = 0
        errors = []

        for idx, data in enumerate(aed_data_list):
            try:
                aed = cls._create_aed_from_dict(db, data)
                success_count += 1
            except Exception as e:
                failed_count += 1
                errors.append(
                    {
                        "row": idx + 1,
                        "error": str(e),
                        "data": data.get("resource_name", "unknown"),
                    }
                )

        db.commit()

        return {
            "total": len(aed_data_list),
            "success": success_count,
            "failed": failed_count,
            "errors": errors[:10],  # 最多返回10个错误
        }

    @classmethod
    def get_aed_statistics(
        cls, db: Session, city: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取AED统计信息

        Args:
            db: 数据库会话
            city: 城市名称（可选，不传则统计全部）

        Returns:
            统计数据
        """
        query = db.query(EmergencyResource).filter(
            EmergencyResource.resource_type == "aed"
        )

        if city:
            query = query.filter(EmergencyResource.city == city)

        total = query.count()

        # 按状态统计
        status_counts = {}
        for status in AEDStatus:
            count = query.filter(EmergencyResource.aed_status == status.value).count()
            status_counts[status.value] = count

        # 未设置状态的
        unknown_count = query.filter(EmergencyResource.aed_status == None).count()
        status_counts["unknown"] = unknown_count

        # 按城市统计（前10）
        city_stats = (
            db.query(
                EmergencyResource.city, func.count(EmergencyResource.id).label("count")
            )
            .filter(EmergencyResource.resource_type == "aed")
            .group_by(EmergencyResource.city)
            .order_by(func.count(EmergencyResource.id).desc())
            .limit(10)
            .all()
        )

        return {
            "total": total,
            "status_distribution": status_counts,
            "city_distribution": [{"city": c[0], "count": c[1]} for c in city_stats],
            "active_rate": (
                round(
                    (status_counts.get("active", 0) + status_counts.get("unknown", 0))
                    / total
                    * 100,
                    2,
                )
                if total > 0
                else 0
            ),
        }

    @classmethod
    def update_aed_status(
        cls,
        db: Session,
        aed_id: int,
        status: str,
        inspection_data: Optional[Dict] = None,
    ) -> Optional[EmergencyResource]:
        """
        更新AED设备状态

        Args:
            db: 数据库会话
            aed_id: AED设备ID
            status: 新状态
            inspection_data: 检查数据（可选）

        Returns:
            更新后的AED设备
        """
        aed = cls.get_by_id(db, aed_id)
        if not aed or aed.resource_type != "aed":
            return None

        aed.aed_status = status
        aed.aed_last_inspection = datetime.utcnow()

        if inspection_data:
            if "battery_expiry" in inspection_data:
                aed.aed_battery_expiry = inspection_data["battery_expiry"]
            if "pad_expiry" in inspection_data:
                aed.aed_pad_expiry = inspection_data["pad_expiry"]
            if "notes" in inspection_data:
                # 可以添加到description或使用新字段
                pass

        db.commit()
        db.refresh(aed)
        return aed

    @classmethod
    def get_expiring_aeds(cls, db: Session, days: int = 30) -> List[Dict[str, Any]]:
        """
        获取即将过期的AED设备（电池或电极片）

        Args:
            db: 数据库会话
            days: 提前多少天预警

        Returns:
            即将过期的AED列表
        """
        expiry_date = datetime.utcnow() + timedelta(days=days)

        aeds = (
            db.query(EmergencyResource)
            .filter(
                EmergencyResource.resource_type == "aed",
                EmergencyResource.is_active == 1,
                or_(
                    EmergencyResource.aed_battery_expiry <= expiry_date,
                    EmergencyResource.aed_pad_expiry <= expiry_date,
                ),
            )
            .all()
        )

        results = []
        for aed in aeds:
            expiring_items = []

            if aed.aed_battery_expiry and aed.aed_battery_expiry <= expiry_date:
                days_left = (aed.aed_battery_expiry - datetime.utcnow()).days
                expiring_items.append(
                    {
                        "type": "battery",
                        "name": "电池",
                        "expiry_date": aed.aed_battery_expiry.isoformat(),
                        "days_left": days_left,
                    }
                )

            if aed.aed_pad_expiry and aed.aed_pad_expiry <= expiry_date:
                days_left = (aed.aed_pad_expiry - datetime.utcnow()).days
                expiring_items.append(
                    {
                        "type": "pad",
                        "name": "电极片",
                        "expiry_date": aed.aed_pad_expiry.isoformat(),
                        "days_left": days_left,
                    }
                )

            results.append({**aed.to_dict(), "expiring_items": expiring_items})

        return results

    @classmethod
    def _create_aed_from_dict(
        cls, db: Session, data: Dict[str, Any]
    ) -> EmergencyResource:
        """从字典创建AED设备"""
        aed = EmergencyResource(
            resource_type="aed",
            resource_name=data.get("resource_name") or data.get("name", "未命名AED"),
            description=data.get("description"),
            latitude=float(data["latitude"]),
            longitude=float(data["longitude"]),
            address=data.get("address"),
            province=data.get("province"),
            city=data.get("city"),
            district=data.get("district"),
            phone=data.get("phone"),
            aed_status=data.get("aed_status", AEDStatus.ACTIVE.value),
            aed_brand=data.get("aed_brand") or data.get("brand"),
            aed_model=data.get("aed_model") or data.get("model"),
            aed_sn=data.get("aed_sn") or data.get("sn") or data.get("serial_number"),
            aed_location_desc=data.get("aed_location_desc")
            or data.get("location_desc"),
            aed_access_instructions=data.get("aed_access_instructions")
            or data.get("access_instructions"),
            aed_manager_name=data.get("aed_manager_name") or data.get("manager_name"),
            aed_manager_phone=data.get("aed_manager_phone")
            or data.get("manager_phone"),
            aed_image_url=data.get("aed_image_url") or data.get("image_url"),
            is_active=1,
        )

        # 处理日期字段
        date_fields = [
            ("aed_installation_date", ["installation_date", "install_date"]),
            ("aed_battery_expiry", ["battery_expiry", "battery_expire_date"]),
            ("aed_pad_expiry", ["pad_expiry", "pad_expire_date", "electrode_expiry"]),
            ("last_maintenance", ["maintenance_date", "last_check"]),
        ]

        for field_name, possible_keys in date_fields:
            for key in possible_keys:
                if key in data and data[key]:
                    try:
                        if isinstance(data[key], str):
                            date_val = datetime.fromisoformat(
                                data[key].replace("Z", "+00:00")
                            )
                        else:
                            date_val = data[key]
                        setattr(aed, field_name, date_val)
                        break
                    except (ValueError, TypeError):
                        continue

        # 处理照片列表
        photos = data.get("aed_photos") or data.get("photos")
        if photos:
            if isinstance(photos, list):
                aed.aed_photos = json.dumps(photos, ensure_ascii=False)
            else:
                aed.aed_photos = photos

        db.add(aed)
        db.flush()  # 获取ID但不提交
        return aed

    @staticmethod
    def _calculate_distance(
        lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """计算两点间距离（米）使用Haversine公式"""
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        earth_radius = 6371000  # 地球半径（米）

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        return earth_radius * c

    @staticmethod
    def _calculate_search_boundaries(
        latitude: float, longitude: float, radius: float
    ) -> Dict[str, float]:
        """计算搜索边界的经纬度"""
        lat_delta = radius / 111000.0
        lon_delta = radius / (111000.0 * math.cos(math.radians(latitude)))

        return {
            "min_lat": latitude - lat_delta,
            "max_lat": latitude + lat_delta,
            "min_lon": longitude - lon_delta,
            "max_lon": longitude + lon_delta,
        }

    @staticmethod
    def _format_distance(distance: float) -> str:
        """格式化距离显示"""
        if distance < 1000:
            return f"{int(distance)}米"
        else:
            return f"{distance/1000:.1f}公里"

    @staticmethod
    def _format_duration(seconds: int) -> str:
        """格式化时长显示"""
        if seconds < 60:
            return "1分钟"
        elif seconds < 3600:
            return f"{seconds // 60}分钟"
        else:
            hours = seconds // 3600
            mins = (seconds % 3600) // 60
            if mins > 0:
                return f"{hours}小时{mins}分钟"
            return f"{hours}小时"

    @staticmethod
    def _get_apple_nav_flag(nav_type: str) -> str:
        """获取苹果地图导航类型标识"""
        flags = {"walking": "w", "driving": "d", "bus": "r"}
        return flags.get(nav_type, "d")
