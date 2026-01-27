from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship as db_relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum

class GenderEnum(str, enum.Enum):
    UNKNOWN = "0"
    MALE = "1"
    FEMALE = "2"

class BloodTypeEnum(str, enum.Enum):
    A = "A"
    B = "B"
    O = "O"
    AB = "AB"
    UNKNOWN = "UNKNOWN"

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    user_id = Column(String(36), primary_key=True, index=True, comment="用户唯一标识")
    phone = Column(String(11), unique=True, index=True, nullable=False, comment="手机号")
    password_hash = Column(String(255), nullable=False, comment="密码哈希值")
    nickname = Column(String(50), nullable=True, comment="昵称")
    gender = Column(SQLEnum(GenderEnum), default=GenderEnum.UNKNOWN, comment="性别")
    birth_date = Column(DateTime, nullable=True, comment="出生日期")
    blood_type = Column(SQLEnum(BloodTypeEnum), default=BloodTypeEnum.UNKNOWN, comment="血型")
    height = Column(Integer, nullable=True, comment="身高(cm)")
    weight = Column(Integer, nullable=True, comment="体重(kg)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="注册时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    last_sign_in = Column(DateTime(timezone=True), nullable=True, comment="最后登录时间")

    # 关联关系
    emergency_contacts = db_relationship("EmergencyContact", back_populates="user", cascade="all, delete-orphan")
    checkins = db_relationship("CheckIn", back_populates="user", cascade="all, delete-orphan")
    alerts = db_relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    alert_settings = db_relationship("AlertSetting", back_populates="user", cascade="all, delete-orphan", uselist=False)
    sos_requests = db_relationship("SOSRequest", back_populates="user", cascade="all, delete-orphan")
    devices = db_relationship("Device", back_populates="user", cascade="all, delete-orphan")
    # anomalies = db_relationship("Anomaly", back_populates="user", cascade="all, delete-orphan")  # 等待 Anomaly 模型修复
    # health_trends = db_relationship("HealthTrend", back_populates="user", cascade="all, delete-orphan")  # 等待 HealthTrend 模型实现
    # activity_patterns = db_relationship("ActivityPattern", back_populates="user", cascade="all, delete-orphan")  # 等待 ActivityPattern 模型实现
    # notifications = db_relationship("Notification", back_populates="user", cascade="all, delete-orphan")  # 等待 Notification 模型实现
    # notification_preference = db_relationship("NotificationPreference", back_populates="user", cascade="all, delete-orphan", uselist=False)  # 等待 NotificationPreference 模型实现
    # login_records = db_relationship("LoginRecord", back_populates="user", cascade="all, delete-orphan")  # 等待 LoginRecord 模型实现
    # user_setting = db_relationship("UserSetting", back_populates="user", cascade="all, delete-orphan", uselist=False)  # 等待 UserSetting 模型实现
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "phone": self.phone,
            "nickname": self.nickname,
            "gender": self.gender.value if self.gender else None,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "blood_type": self.blood_type.value if self.blood_type else None,
            "height": self.height,
            "weight": self.weight,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_sign_in": self.last_sign_in.isoformat() if self.last_sign_in else None
        }