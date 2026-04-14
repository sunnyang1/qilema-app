"""
签到打卡服务单元测试
"""

from datetime import date, datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.checkin import CheckIn
from app.models.emergency_contact import EmergencyContact
from app.models.user import User
from app.schemas.checkin import CheckInCreate, CheckInDateQuery
from app.services.checkin_service import CheckInService

# 测试数据库
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """创建测试数据库会话"""
    # 创建所有表
    from app.core.database import Base

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # 清理数据库
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db):
    """创建测试用户"""
    user = User(
        user_id="test-user-001",
        phone="13800138000",
        password_hash="$2b$12$test_hash_here",
        nickname="测试用户",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
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


class TestCheckInService:
    """签到服务测试"""

    def test_create_checkin_success(self, db, test_user):
        """测试成功创建签到记录"""
        checkin_data = CheckInCreate(
            latitude="39.9042",
            longitude="116.4074",
            checkin_method="manual",
            notes="早安",
        )

        checkin = CheckInService(db).create_checkin(test_user.user_id, checkin_data)

        assert checkin is not None
        assert checkin.user_id == test_user.user_id
        assert checkin.checkin_date == date.today().strftime("%Y-%m-%d")
        assert checkin.latitude == "39.9042"
        assert checkin.longitude == "116.4074"
        assert checkin.checkin_method == "manual"
        assert checkin.notes == "早安"
        assert checkin.checkin_time is not None

    def test_create_checkin_duplicate(self, db, test_user):
        """测试重复签到(同一天多次)"""
        checkin_data = CheckInCreate()

        # 第一次签到
        CheckInService(db).create_checkin(test_user.user_id, checkin_data)

        # 第二次签到应该失败
        with pytest.raises(ValueError, match="今天已经签到过了"):
            CheckInService(db).create_checkin(test_user.user_id, checkin_data)

    def test_create_checkin_without_location(self, db, test_user):
        """测试不带位置的签到"""
        checkin_data = CheckInCreate(checkin_method="manual")

        checkin = CheckInService(db).create_checkin(test_user.user_id, checkin_data)

        assert checkin is not None
        assert checkin.latitude is None
        assert checkin.longitude is None

    def test_get_user_checkins(self, db, test_user):
        """测试获取用户签到历史"""
        # 创建多个签到记录
        for i in range(5):
            checkin_date = (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
            checkin = CheckIn(
                user_id=test_user.user_id,
                checkin_time=datetime.utcnow() - timedelta(days=i),
                checkin_date=checkin_date,
                checkin_method="manual",
            )
            db.add(checkin)
        db.commit()

        # 获取签到历史
        checkins = CheckInService(db).get_user_checkins(test_user.user_id, days=10)

        assert len(checkins) == 5
        # 检查是否按日期降序排列
        for i in range(len(checkins) - 1):
            assert checkins[i].checkin_date >= checkins[i + 1].checkin_date

    def test_get_checkin_stats(self, db, test_user):
        """测试获取签到统计"""
        # 创建签到记录(连续签到3天)
        for i in range(3):
            checkin_date = (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
            checkin = CheckIn(
                user_id=test_user.user_id,
                checkin_time=datetime.utcnow() - timedelta(days=i),
                checkin_date=checkin_date,
                checkin_method="manual",
            )
            db.add(checkin)
        db.commit()

        # 获取统计信息
        stats = CheckInService(db).get_checkin_stats(test_user.user_id, days=10)

        assert stats.total_checkins == 3
        assert stats.current_streak == 3
        assert stats.longest_streak == 3
        assert 0 < stats.checkin_rate <= 100

    def test_get_checkin_stats_no_checkins(self, db, test_user):
        """测试无签到记录时的统计"""
        stats = CheckInService(db).get_checkin_stats(test_user.user_id, days=10)

        assert stats.total_checkins == 0
        assert stats.current_streak == 0
        assert stats.longest_streak == 0
        assert stats.checkin_rate == 0

    def test_get_checkin_status_today_checked(self, db, test_user):
        """测试今天的签到状态(已签到)"""
        # 创建今天的签到记录
        checkin = CheckIn(
            user_id=test_user.user_id,
            checkin_time=datetime.utcnow(),
            checkin_date=date.today().strftime("%Y-%m-%d"),
            checkin_method="manual",
        )
        db.add(checkin)
        db.commit()

        # 查询今天状态
        status = CheckInService(db).get_checkin_status(test_user.user_id)

        assert status.is_checked_in is True
        assert status.checkin_time is not None

    def test_get_checkin_status_today_unchecked(self, db, test_user):
        """测试今天的签到状态(未签到)"""
        # 查询今天状态(未签到)
        status = CheckInService(db).get_checkin_status(test_user.user_id)

        assert status.is_checked_in is False
        assert status.checkin_time is None

    def test_get_checkin_status_specific_date(self, db, test_user):
        """测试查询特定日期的签到状态"""
        # 创建昨天的签到记录
        yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        checkin = CheckIn(
            user_id=test_user.user_id,
            checkin_time=datetime.utcnow() - timedelta(days=1),
            checkin_date=yesterday,
            checkin_method="manual",
        )
        db.add(checkin)
        db.commit()

        # 查询昨天状态
        status = CheckInService(db).get_checkin_status(
            test_user.user_id, date.today() - timedelta(days=1)
        )

        assert status.is_checked_in is True
        assert status.checkin_time is not None

    def test_get_emergency_contacts_for_notification(
        self, db, test_user, test_contacts
    ):
        """测试获取紧急联系人(用于通知)"""
        contacts = CheckInService(db).get_emergency_contacts_for_notification(
            test_user.user_id
        )

        assert len(contacts) == 2
        # 检查是否按优先级排序
        assert contacts[0].priority == 1
        assert contacts[1].priority == 2

    def test_calculate_streak_continuous(self, db, test_user):
        """测试计算连续签到天数"""
        # 创建连续签到记录(7天)
        for i in range(7):
            checkin_date = (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
            checkin = CheckIn(
                user_id=test_user.user_id,
                checkin_time=datetime.utcnow() - timedelta(days=i),
                checkin_date=checkin_date,
                checkin_method="manual",
            )
            db.add(checkin)
        db.commit()

        # 计算连续签到天数
        streak = CheckInService(db)._calculate_streak(test_user.user_id, date.today())

        assert streak == 7

    def test_calculate_streak_broken(self, db, test_user):
        """测试计算被中断的连续签到"""
        # 创建签到记录: 今天和昨天签到,前天未签到
        for i in range(2):
            checkin_date = (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
            checkin = CheckIn(
                user_id=test_user.user_id,
                checkin_time=datetime.utcnow() - timedelta(days=i),
                checkin_date=checkin_date,
                checkin_method="manual",
            )
            db.add(checkin)
        db.commit()

        # 计算连续签到天数
        streak = CheckInService(db)._calculate_streak(test_user.user_id, date.today())

        assert streak == 2

    def test_calculate_longest_streak(self, db, test_user):
        """测试计算最长连续签到天数"""
        # 创建签到记录: 连续3天 -> 间隔1天 -> 连续5天
        for i in range(8):
            if i == 3:
                continue  # 跳过一天
            checkin_date = (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
            checkin = CheckIn(
                user_id=test_user.user_id,
                checkin_time=datetime.utcnow() - timedelta(days=i),
                checkin_date=checkin_date,
                checkin_method="manual",
            )
            db.add(checkin)
        db.commit()

        # 计算最长连续签到
        longest = CheckInService(db)._calculate_longest_streak(
            test_user.user_id, days=10
        )

        assert longest == 4  # 最长连续4天

    def test_checkin_date_validation(self):
        """测试日期格式验证"""
        # 有效的日期格式
        valid_query = CheckInDateQuery(date="2024-01-26")
        assert valid_query.date == "2024-01-26"

        # 无效的日期格式
        with pytest.raises(ValueError, match="日期格式必须是 YYYY-MM-DD"):
            CheckInDateQuery(date="2024/01/26")

    def test_checkin_method_validation(self):
        """测试签到方式验证"""
        # 有效的签到方式
        valid_data = CheckInCreate(checkin_method="manual")
        assert valid_data.checkin_method == "manual"

        valid_data = CheckInCreate(checkin_method="auto")
        assert valid_data.checkin_method == "auto"

        # 无效的签到方式
        with pytest.raises(ValueError, match="签到方式必须是 manual 或 auto"):
            CheckInCreate(checkin_method="invalid")

    def test_coordinates_validation(self):
        """测试经纬度验证"""
        # 有效的经纬度
        valid_data = CheckInCreate(latitude="39.9042", longitude="116.4074")
        assert valid_data.latitude == "39.9042"
        assert valid_data.longitude == "116.4074"

        # 无效的纬度
        with pytest.raises(ValueError, match="纬度必须在-90到90之间"):
            CheckInCreate(latitude="91.0")

        # 无效的经度
        with pytest.raises(ValueError, match="经度必须在-180到180之间"):
            CheckInCreate(longitude="181.0")

        # 无效的格式
        with pytest.raises(ValueError, match="经纬度必须是有效的数字"):
            CheckInCreate(latitude="invalid")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
