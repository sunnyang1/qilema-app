"""
消息通知SQLAlchemy模型
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship as db_relationship
from app.core.database import Base


class Notification(Base):
    """通知模型"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True, comment="用户ID")
    notification_type = Column(String(20), nullable=False, index=True, comment="通知类型: checkin/alert/sos/system/health/device/reminder")
    channel = Column(String(20), nullable=False, comment="通知渠道: push/sms/phone/email/wechat")
    priority = Column(String(20), nullable=False, default="normal", comment="优先级: low/normal/high/urgent")
    status = Column(String(20), nullable=False, default="pending", comment="状态: pending/sending/sent/delivered/read/failed")
    title = Column(String(200), nullable=False, comment="通知标题")
    content = Column(Text, nullable=True, comment="通知内容")
    data = Column(JSON, nullable=True, comment="附加数据")

    # 接收者信息
    recipient_type = Column(String(50), nullable=True, comment="接收者类型: user/contact/emergency_center")
    recipient_id = Column(String(36), nullable=True, comment="接收者ID")

    # 发送信息
    sent_at = Column(DateTime, nullable=True, comment="发送时间")
    delivered_at = Column(DateTime, nullable=True, comment="送达时间")
    read_at = Column(DateTime, nullable=True, comment="阅读时间")
    error_message = Column(Text, nullable=True, comment="错误信息")
    retry_count = Column(Integer, nullable=False, default=0, comment="重试次数")

    # 关联信息
    related_type = Column(String(50), nullable=True, comment="关联对象类型: alert/sos_request/checkin/device")
    related_id = Column(String(36), nullable=True, comment="关联对象ID")

    created_at = Column(DateTime, nullable=False, default=lambda: __import__('datetime').datetime.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=True, comment="更新时间")

    # 关系
    user = db_relationship("User", back_populates="notifications")
