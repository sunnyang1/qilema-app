"""
签到打卡数据模型

记录用户的每日签到记录,用于确认用户安全状态
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship as db_relationship
from ..core.database import Base


class CheckIn(Base):
    """签到记录表"""

    __tablename__ = "checkins"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    
    # 外键关联用户
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 签到时间戳
    checkin_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # 签到日期(用于快速查询某天的签到状态)
    checkin_date = Column(String(10), nullable=False, index=True)  # 格式: YYYY-MM-DD
    
    # 签到位置(可选)
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)
    
    # 签到方式: 'manual'手动签到, 'auto'自动签到(智能设备)
    checkin_method = Column(String(10), nullable=False, default='manual')
    
    # 备注信息
    notes = Column(String(200), nullable=True)

    # 关联用户
    user = db_relationship("User", back_populates="checkins")

    def __repr__(self):
        return f"<CheckIn(id={self.id}, user_id={self.user_id}, date={self.checkin_date})>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "checkin_time": self.checkin_time.isoformat() if self.checkin_time else None,
            "checkin_date": self.checkin_date,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "checkin_method": self.checkin_method,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建对象"""
        return cls(
            user_id=data.get("user_id"),
            checkin_time=datetime.fromisoformat(data["checkin_time"]) if data.get("checkin_time") else datetime.utcnow(),
            checkin_date=data.get("checkin_date"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            checkin_method=data.get("checkin_method", "manual"),
            notes=data.get("notes")
        )


# 复合索引: 用户ID + 签到日期(确保每天只能签到一次)
Index('ix_checkins_user_date', CheckIn.user_id, CheckIn.checkin_date, unique=True)
