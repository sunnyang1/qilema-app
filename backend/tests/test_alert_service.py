"""预警服务层单元测试"""

from datetime import date, datetime, timedelta

import pytest
from app.core.database import Base
from app.models.alert import AlertSetting
from app.models.checkin import CheckIn
from app.models.emergency_contact import EmergencyContact
from app.models.user import User
from app.schemas.alert import AlertCreate, AlertResolveRequest, AlertSettingCreate
from app.services.alert_service import AlertService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 创建测试数据库
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db):
    """创建测试用户"""
    user = User(
        user_id="test-user-001",
        phone="13800138000",
        nickname="测试用户",
        password_hash="hashed_password",
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture
def test_contacts(db, test_user):
    """创建测试紧急联系人"""
    contact1 = EmergencyContact(
        user_id=test_user.user_id,
        name="紧急联系人1",
        phone="13900139000",
        relationship="家人",
        priority=1,
    )
    contact2 = EmergencyContact(
        user_id=test_user.user_id,
        name="紧急联系人2",
        phone="13900139001",
        relationship="朋友",
        priority=2,
    )
    db.add(contact1)
    db.add(contact2)
    db.commit()
    return [contact1, contact2]


class TestAlertSettingService:
    """测试预警配置服务"""

    def test_create_alert_setting(self, db, test_user):
        """测试创建预警配置"""
        setting_data = AlertSettingCreate(
            checkin_threshold_hours=24,
            enable_notification=True,
            notification_channels="push,sms",
            auto_resolve=True,
        )

        setting = AlertService.create_or_update_setting(
            db, test_user.user_id, setting_data
        )

        assert setting.user_id == test_user.user_id
        assert setting.checkin_threshold_hours == 24
        assert setting.enable_notification is True
        assert setting.notification_channels == "push,sms"
        assert setting.auto_resolve is True

    def test_update_alert_setting(self, db, test_user):
        """测试更新预警配置"""
        # 先创建配置
        setting_data = AlertSettingCreate(checkin_threshold_hours=24)
        AlertService.create_or_update_setting(db, test_user.user_id, setting_data)

        # 更新配置
        update_data = AlertSettingCreate(
            checkin_threshold_hours=48, enable_notification=False
        )
        setting = AlertService.create_or_update_setting(
            db, test_user.user_id, update_data
        )

        assert setting.checkin_threshold_hours == 48
        assert setting.enable_notification is False

    def test_get_alert_setting(self, db, test_user):
        """测试获取预警配置"""
        setting_data = AlertSettingCreate(checkin_threshold_hours=24)
        AlertService.create_or_update_setting(db, test_user.user_id, setting_data)

        setting = AlertService.get_setting(db, test_user.user_id)

        assert setting is not None
        assert setting.checkin_threshold_hours == 24

    def test_invalid_threshold(self):
        """测试无效的预警阈值"""
        with pytest.raises(ValueError, match="预警阈值必须是"):
            AlertSettingCreate(checkin_threshold_hours=5)

    def test_invalid_notification_channels(self):
        """测试无效的通知渠道"""
        with pytest.raises(ValueError, match="通知渠道必须是"):
            AlertSettingCreate(notification_channels="push,invalid")


class TestAlertCheckInService:
    """测试签到状态检查服务"""

    def test_check_user_never_checkin(self, db, test_user):
        """测试用户从未签到"""
        setting = AlertSetting(user_id=test_user.user_id, enable_notification=True)
        db.add(setting)
        db.commit()

        status = AlertService.check_user_checkin_status(db, test_user.user_id)

        assert status is not None
        assert status["trigger_alert"] is True
        assert status["last_checkin_time"] is None

    def test_check_user_checkin_today(self, db, test_user):
        """测试用户今天已签到"""
        setting = AlertSetting(
            user_id=test_user.user_id,
            enable_notification=True,
            checkin_threshold_hours=24,
        )
        db.add(setting)

        checkin = CheckIn(
            user_id=test_user.user_id,
            checkin_time=datetime.utcnow(),
            checkin_date=date.today().strftime("%Y-%m-%d"),
            checkin_method="manual",
        )
        db.add(checkin)
        db.commit()

        status = AlertService.check_user_checkin_status(db, test_user.user_id)

        assert status is not None
        assert status["trigger_alert"] is False
        assert status["missed_hours"] < 24

    def test_check_user_missed_2_days(self, db, test_user):
        """测试用户连续2天未签到"""
        setting = AlertSetting(
            user_id=test_user.user_id,
            enable_notification=True,
            checkin_threshold_hours=48,
        )
        db.add(setting)

        checkin = CheckIn(
            user_id=test_user.user_id,
            checkin_time=datetime.utcnow() - timedelta(days=2),
            checkin_date=(date.today() - timedelta(days=2)).strftime("%Y-%m-%d"),
            checkin_method="manual",
        )
        db.add(checkin)
        db.commit()

        status = AlertService.check_user_checkin_status(db, test_user.user_id)

        assert status is not None
        assert status["trigger_alert"] is True
        assert status["missed_days"] >= 2

    def test_check_user_notification_disabled(self, db, test_user):
        """测试通知已禁用"""
        setting = AlertSetting(user_id=test_user.user_id, enable_notification=False)
        db.add(setting)
        db.commit()

        status = AlertService.check_user_checkin_status(db, test_user.user_id)

        assert status is None


class TestAlertCreationService:
    """测试预警创建服务"""

    def test_create_alert(self, db, test_user):
        """测试创建预警记录"""
        alert_data = AlertCreate(
            user_id=test_user.user_id,
            alert_type="checkin_absent",
            severity="medium",
            trigger_reason="用户连续2天未签到",
            missed_days=2,
            threshold_hours=48,
        )

        alert = AlertService.create_alert(db, alert_data)

        assert alert.user_id == test_user.user_id
        assert alert.alert_type == "checkin_absent"
        assert alert.severity == "medium"
        assert alert.status == "active"

    def test_create_duplicate_alert(self, db, test_user):
        """测试不重复创建活动预警"""
        alert_data = AlertCreate(
            user_id=test_user.user_id,
            alert_type="checkin_absent",
            severity="medium",
            trigger_reason="用户连续2天未签到",
        )

        # 创建第一个预警
        alert1 = AlertService.create_alert(db, alert_data)

        # 尝试创建重复预警
        alert2 = AlertService.create_alert(db, alert_data)

        assert alert1.id == alert2.id  # 返回同一个预警

    def test_severity_calculation(self):
        """测试严重程度计算"""
        assert AlertService._calculate_severity(96) == "critical"
        assert AlertService._calculate_severity(60) == "high"
        assert AlertService._calculate_severity(30) == "medium"
        assert AlertService._calculate_severity(12) == "low"


class TestAlertResolveService:
    """测试预警解除服务"""

    def test_resolve_alert(self, db, test_user):
        """测试解除预警"""
        # 创建活动预警
        alert_data = AlertCreate(
            user_id=test_user.user_id,
            alert_type="checkin_absent",
            severity="medium",
            trigger_reason="测试预警",
        )
        alert = AlertService.create_alert(db, alert_data)

        # 解除预警
        resolve_request = AlertResolveRequest(resolved_reason="已联系用户确认安全")
        resolved_alert = AlertService.resolve_alert(
            db, alert.id, test_user.user_id, resolve_request
        )

        assert resolved_alert.status == "resolved"
        assert resolved_alert.resolved_by == "manual_dismiss"
        assert resolved_alert.resolved_reason == "已联系用户确认安全"
        assert resolved_alert.resolved_at is not None

    def test_auto_resolve_by_checkin(self, db, test_user):
        """测试签到后自动解除预警"""
        # 创建预警配置(启用自动解除)
        setting = AlertSetting(user_id=test_user.user_id, auto_resolve=True)
        db.add(setting)

        # 创建多个活动预警(使用不同类型避免重复检查)
        alert_data1 = AlertCreate(
            user_id=test_user.user_id,
            alert_type="checkin_absent",
            trigger_reason="预警1",
        )
        alert_data2 = AlertCreate(
            user_id=test_user.user_id, alert_type="sos_missed", trigger_reason="预警2"
        )
        AlertService.create_alert(db, alert_data1)
        AlertService.create_alert(db, alert_data2)
        db.commit()

        # 用户签到后自动解除
        count = AlertService.auto_resolve_by_checkin(db, test_user.user_id)

        assert count == 2

    def test_resolve_nonexistent_alert(self, db, test_user):
        """测试解除不存在的预警"""
        resolve_request = AlertResolveRequest()
        result = AlertService.resolve_alert(
            db, 9999, test_user.user_id, resolve_request
        )

        assert result is None


class TestAlertQueryService:
    """测试预警查询服务"""

    def test_get_alerts(self, db, test_user):
        """测试查询预警记录"""
        # 创建预警记录
        alert_data = AlertCreate(
            user_id=test_user.user_id,
            alert_type="checkin_absent",
            severity="medium",
            trigger_reason="测试预警",
        )
        AlertService.create_alert(db, alert_data)

        # 查询预警
        alerts, total = AlertService.get_alerts(db, test_user.user_id)

        assert total == 1
        assert len(alerts) == 1
        assert alerts[0].alert_type == "checkin_absent"

    def test_get_alerts_with_status_filter(self, db, test_user):
        """测试按状态查询预警"""
        # 创建预警记录
        alert_data = AlertCreate(
            user_id=test_user.user_id,
            alert_type="checkin_absent",
            trigger_reason="测试",
        )
        alert = AlertService.create_alert(db, alert_data)

        # 解除预警
        resolve_request = AlertResolveRequest(resolved_reason="测试解除")
        AlertService.resolve_alert(db, alert.id, test_user.user_id, resolve_request)

        # 查询活动预警
        active_alerts, _ = AlertService.get_alerts(
            db, test_user.user_id, status="active"
        )
        assert len(active_alerts) == 0

        # 查询已解除预警
        resolved_alerts, _ = AlertService.get_alerts(
            db, test_user.user_id, status="resolved"
        )
        assert len(resolved_alerts) == 1

    def test_get_alert_stats(self, db, test_user):
        """测试获取预警统计"""
        # 创建活动预警
        alert_data = AlertCreate(
            user_id=test_user.user_id,
            alert_type="checkin_absent",
            trigger_reason="预警1",
        )
        alert = AlertService.create_alert(db, alert_data)

        # 解除预警
        resolve_request = AlertResolveRequest(resolved_reason="测试")
        AlertService.resolve_alert(db, alert.id, test_user.user_id, resolve_request)

        # 获取统计
        stats = AlertService.get_alert_stats(db, test_user.user_id)

        assert stats["total_alerts"] == 1
        assert stats["resolved_alerts"] == 1
        assert stats["active_alerts"] == 0

    def test_get_contacts_for_notification(self, db, test_user, test_contacts):
        """测试获取通知联系人"""
        contacts = AlertService.get_contacts_for_notification(db, test_user.user_id)

        assert len(contacts) == 2
        assert contacts[0].priority == 1
        assert contacts[1].priority == 2

    def test_check_all_users_and_create_alerts(self, db, test_user, test_contacts):
        """测试检查所有用户并创建预警"""
        # 创建预警配置
        setting = AlertSetting(
            user_id=test_user.user_id,
            enable_notification=True,
            checkin_threshold_hours=24,
        )
        db.add(setting)

        # 创建2天前的签到记录
        checkin = CheckIn(
            user_id=test_user.user_id,
            checkin_time=datetime.utcnow() - timedelta(days=2),
            checkin_date=(date.today() - timedelta(days=2)).strftime("%Y-%m-%d"),
            checkin_method="manual",
        )
        db.add(checkin)
        db.commit()

        # 检查所有用户
        created_alerts = AlertService.check_all_users_and_create_alerts(db)

        assert len(created_alerts) == 1
        assert created_alerts[0].alert_type == "checkin_absent"
        assert created_alerts[0].severity == "high"
