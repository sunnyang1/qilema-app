"""
紧急联系人SQLAlchemy模型
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship as db_relationship
from app.core.database import Base


class EmergencyContact(Base):
    """紧急联系人模型"""
    __tablename__ = "emergency_contacts"
    
    contact_id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    name = Column(String(50), nullable=False, comment="联系人姓名")
    phone = Column(String(20), nullable=False, comment="联系人电话")
    relationship = Column(String(20), nullable=True, comment="与用户关系")
    priority = Column(Integer, nullable=False, default=1, comment="通知优先级")
    notify_channels = Column(JSON, nullable=True, comment="通知渠道")
    created_at = Column(DateTime, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, nullable=True, comment="更新时间")
    
    # 关系
    user = db_relationship("User", back_populates="emergency_contacts")
