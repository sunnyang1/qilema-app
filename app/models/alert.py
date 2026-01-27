"""
预警SQLAlchemy模型
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship as db_relationship
from app.core.database import Base


class Alert(Base):
    """预警模型"""
    __tablename__ = "alerts"
    
    alert_id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    alert_type = Column(Integer, nullable=False, comment="预警类型: 1-未签到, 2-生理异常")
    trigger_time = Column(DateTime, nullable=False, comment="触发时间")
    status = Column(Integer, nullable=False, default=0, comment="状态: 0-待处理, 1-已处理, 2-已解除")
    last_checkin_time = Column(DateTime, nullable=True, comment="最后签到时间")
    abnormal_data = Column(JSON, nullable=True, comment="异常数据")
    notification_sent = Column(JSON, nullable=True, comment="已发送的通知")
    resolved_at = Column(DateTime, nullable=True, comment="解决时间")
    created_at = Column(DateTime, nullable=False, comment="创建时间")
    
    # 关系
    user = db_relationship("User", back_populates="alerts")
