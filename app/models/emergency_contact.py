"""
紧急联系人SQLAlchemy模型
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship as db_relationship
from app.core.database import Base


class EmergencyContact(Base):
    """紧急联系人模型"""
    __tablename__ = "emergency_contacts"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(String(36), nullable=False, unique=True, index=True, default=lambda: str(__import__('uuid').uuid4()))
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    name = Column(String(50), nullable=False, comment="联系人姓名")
    phone = Column(String(20), nullable=False, comment="联系人电话")
    relationship = Column(String(20), nullable=True, comment="与用户关系")
    is_primary = Column(Integer, nullable=False, default=0, comment="是否主要联系人: 0=否 1=是")
    priority = Column(Integer, nullable=False, default=1, comment="通知优先级")
    notify_channels = Column(JSON, nullable=True, comment="通知渠道")
    created_at = Column(DateTime, nullable=False, default=lambda: __import__('datetime').datetime.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=True, comment="更新时间")

    # 关系
    user = db_relationship("User", back_populates="emergency_contacts")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "contact_id": self.contact_id,
            "user_id": self.user_id,
            "name": self.name,
            "phone": self.phone,
            "relationship": self.relationship,
            "is_primary": self.is_primary,
            "priority": self.priority,
            "notify_channels": self.notify_channels,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
