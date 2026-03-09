"""
AED设备服务测试

测试AED查询、导航、批量导入、统计等功能
"""

from datetime import datetime, timedelta

from app.models.emergency_resource_model import AEDStatus, EmergencyResource
from app.services.aed_service import AEDService
from sqlalchemy.orm import Session


class TestAEDService:
    """测试AED服务"""

    def _create_test_aed(self, db: Session, **kwargs):
        """创建测试AED设备"""
        defaults = {
            "resource_type": "aed",
            "resource_name": "测试AED",
            "latitude": 31.2304,
            "longitude": 121.4737,
            "address": "测试地址",
            "city": "上海市",
            "district": "黄浦区",
            "aed_status": AEDStatus.ACTIVE.value,
            "is_active": 1,
        }
        defaults.update(kwargs)

        aed = EmergencyResource(**defaults)
        db.add(aed)
        db.commit()
        db.refresh(aed)
        return aed

    def test_get_nearby_aeds(self, db: Session):
        """测试获取附近AED设备"""
        # 创建多个AED设备
        self._create_test_aed(
            db, resource_name="AED-1", latitude=31.2304, longitude=121.4737
        )
        self._create_test_aed(
            db, resource_name="AED-2", latitude=31.2314, longitude=121.4747
        )
        self._create_test_aed(
            db, resource_name="AED-3", latitude=31.2324, longitude=121.4757
        )
        # 远离的AED
        self._create_test_aed(
            db, resource_name="AED-远", latitude=31.3000, longitude=121.5500
        )

        # 搜索附近的AED
        aeds = AEDService.get_nearby_aeds(
            db, latitude=31.2304, longitude=121.4737, radius=1000, limit=10  # 1公里
        )

        assert len(aeds) == 3  # 应该找到3个近的
        assert aeds[0]["resource_name"] == "AED-1"  # 最近的排第一
        assert "distance" in aeds[0]
        assert "distance_text" in aeds[0]
        assert "duration_text" in aeds[0]

    def test_get_nearby_aeds_only_active(self, db: Session):
        """测试只返回可用状态的AED"""
        self._create_test_aed(
            db, resource_name="可用AED", aed_status=AEDStatus.ACTIVE.value
        )
        self._create_test_aed(
            db, resource_name="维护AED", aed_status=AEDStatus.MAINTENANCE.value
        )
        self._create_test_aed(
            db, resource_name="不可用AED", aed_status=AEDStatus.INACTIVE.value
        )

        aeds = AEDService.get_nearby_aeds(
            db, latitude=31.2304, longitude=121.4737, radius=1000, only_active=True
        )

        assert len(aeds) == 1
        assert aeds[0]["resource_name"] == "可用AED"

    def test_get_aed_navigation_url(self):
        """测试获取导航链接"""
        nav_urls = AEDService.get_aed_navigation_url(
            from_lat=31.2304,
            from_lon=121.4737,
            to_lat=31.2314,
            to_lon=121.4747,
            nav_type="walking",
        )

        assert "amap" in nav_urls
        assert "baidu" in nav_urls
        assert "qqmap" in nav_urls
        assert "apple" in nav_urls
        assert "google" in nav_urls

        # 验证链接包含必要的参数
        assert "31.2304" in nav_urls["amap"]
        assert "121.4737" in nav_urls["amap"]

    def test_import_aeds_batch(self, db: Session):
        """测试批量导入AED"""
        aed_data = [
            {
                "name": "导入AED-1",
                "latitude": 31.2304,
                "longitude": 121.4737,
                "address": "地址1",
                "city": "上海市",
                "brand": "飞利浦",
                "model": "HS1",
            },
            {
                "name": "导入AED-2",
                "latitude": 31.2314,
                "longitude": 121.4747,
                "address": "地址2",
                "city": "上海市",
                "sn": "SN123456",
            },
            {
                # 缺少必填字段，应该失败
                "name": "导入AED-失败"
            },
        ]

        result = AEDService.import_aeds_batch(db, aed_data)

        assert result["total"] == 3
        assert result["success"] == 2
        assert result["failed"] == 1
        assert len(result["errors"]) == 1

    def test_get_aed_statistics(self, db: Session):
        """测试获取AED统计信息"""
        # 创建不同状态的AED
        self._create_test_aed(db, city="上海市", aed_status=AEDStatus.ACTIVE.value)
        self._create_test_aed(db, city="上海市", aed_status=AEDStatus.ACTIVE.value)
        self._create_test_aed(db, city="上海市", aed_status=AEDStatus.MAINTENANCE.value)
        self._create_test_aed(db, city="北京市", aed_status=AEDStatus.ACTIVE.value)

        stats = AEDService.get_aed_statistics(db)

        assert stats["total"] == 4
        assert stats["status_distribution"]["active"] == 3
        assert stats["status_distribution"]["maintenance"] == 1
        assert stats["active_rate"] == 75.0
        assert len(stats["city_distribution"]) > 0

    def test_get_aed_statistics_by_city(self, db: Session):
        """测试按城市统计AED"""
        self._create_test_aed(db, city="上海市")
        self._create_test_aed(db, city="上海市")
        self._create_test_aed(db, city="北京市")

        sh_stats = AEDService.get_aed_statistics(db, city="上海市")
        assert sh_stats["total"] == 2

        bj_stats = AEDService.get_aed_statistics(db, city="北京市")
        assert bj_stats["total"] == 1

    def test_update_aed_status(self, db: Session):
        """测试更新AED状态"""
        aed = self._create_test_aed(db, aed_status=AEDStatus.ACTIVE.value)

        updated = AEDService.update_aed_status(
            db,
            aed.id,
            AEDStatus.MAINTENANCE.value,
            inspection_data={
                "battery_expiry": datetime(2026, 12, 31),
                "pad_expiry": datetime(2026, 6, 30),
                "notes": "电池需要更换",
            },
        )

        assert updated is not None
        assert updated.aed_status == AEDStatus.MAINTENANCE.value
        assert updated.aed_battery_expiry.year == 2026
        assert updated.aed_pad_expiry.year == 2026
        assert updated.aed_last_inspection is not None

    def test_get_expiring_aeds(self, db: Session):
        """测试获取即将过期的AED"""
        now = datetime.utcnow()

        # 创建即将过期的AED
        self._create_test_aed(
            db,
            resource_name="电池即将过期",
            aed_battery_expiry=now + timedelta(days=15),
            aed_pad_expiry=now + timedelta(days=100),
        )

        # 创建电极片即将过期的AED
        self._create_test_aed(
            db,
            resource_name="电极片即将过期",
            aed_battery_expiry=now + timedelta(days=100),
            aed_pad_expiry=now + timedelta(days=20),
        )

        # 创建未过期的AED
        self._create_test_aed(
            db,
            resource_name="正常AED",
            aed_battery_expiry=now + timedelta(days=100),
            aed_pad_expiry=now + timedelta(days=100),
        )

        expiring = AEDService.get_expiring_aeds(db, days=30)

        assert len(expiring) == 2
        names = [a["resource_name"] for a in expiring]
        assert "电池即将过期" in names
        assert "电极片即将过期" in names

        # 验证过期项目信息
        for aed in expiring:
            assert "expiring_items" in aed
            assert len(aed["expiring_items"]) > 0
            assert "days_left" in aed["expiring_items"][0]

    def test_calculate_distance(self):
        """测试距离计算"""
        # 上海人民广场到外滩的距离约1.5公里
        distance = AEDService._calculate_distance(
            31.2304, 121.4737, 31.2397, 121.4998  # 人民广场  # 外滩
        )

        # 应该在1-3公里之间
        assert 1000 < distance < 3000

    def test_format_distance(self):
        """测试距离格式化"""
        assert AEDService._format_distance(500) == "500米"
        assert AEDService._format_distance(1500) == "1.5公里"
        assert AEDService._format_distance(10000) == "10.0公里"

    def test_format_duration(self):
        """测试时长格式化"""
        assert AEDService._format_duration(30) == "1分钟"
        assert AEDService._format_duration(300) == "5分钟"
        assert AEDService._format_duration(3600) == "1小时"
        assert AEDService._format_duration(3660) == "1小时1分钟"

    def test_aed_to_dict_includes_aed_fields(self, db: Session):
        """测试AED字典包含AED专用字段"""
        aed = self._create_test_aed(
            db,
            resource_name="完整信息AED",
            aed_brand="飞利浦",
            aed_model="HS1",
            aed_sn="SN12345678",
            aed_location_desc="一楼大厅电梯旁",
            aed_access_instructions="24小时开放，直接取用",
        )

        data = aed.to_dict()

        assert data["resource_type"] == "aed"
        assert data["aed_brand"] == "飞利浦"
        assert data["aed_model"] == "HS1"
        assert data["aed_sn"] == "SN12345678"
        assert data["aed_location_desc"] == "一楼大厅电梯旁"
        assert data["aed_access_instructions"] == "24小时开放，直接取用"

    def test_non_aed_to_dict_excludes_aed_fields(self, db: Session):
        """测试非AED资源字典不包含AED专用字段"""
        hospital = EmergencyResource(
            resource_type="hospital",
            resource_name="测试医院",
            latitude=31.2304,
            longitude=121.4737,
            city="上海市",
            is_active=1,
        )
        db.add(hospital)
        db.commit()

        data = hospital.to_dict()

        assert data["resource_type"] == "hospital"
        # 医院不应该包含AED专用字段
        assert "aed_brand" not in data
        assert "aed_model" not in data
