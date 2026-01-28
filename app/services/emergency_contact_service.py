"""
紧急联系人服务

实现紧急联系人管理、通知等核心功能
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from app.models.emergency_contact import EmergencyContact
from app.models.user import User
from app.schemas.emergency_contact import EmergencyContactCreate, EmergencyContactUpdate


class EmergencyContactService:
    """紧急联系人服务"""

    def create_emergency_contact(self, db: Session, contact_data: EmergencyContactCreate, user_id: str) -> EmergencyContact:
        """创建紧急联系人"""
        contact = EmergencyContact(
            user_id=user_id,
            contact_name=contact_data.contact_name,
            relationship=contact_data.relationship,
            phone=contact_data.phone,
            is_primary=contact_data.is_primary,
            notification_enabled=contact_data.notification_enabled
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact

    def get_emergency_contacts(self, db: Session, user_id: str) -> List[EmergencyContact]:
        """获取用户紧急联系人列表"""
        return db.query(EmergencyContact).filter(
            EmergencyContact.user_id == user_id
        ).order_by(EmergencyContact.is_primary.desc(), EmergencyContact.created_at.desc()).all()

    def get_emergency_contact(self, db: Session, contact_id: int, user_id: str) -> Optional[EmergencyContact]:
        """获取紧急联系人详情"""
        return db.query(EmergencyContact).filter(
            and_(
                EmergencyContact.id == contact_id,
                EmergencyContact.user_id == user_id
            )
        ).first()

    def update_emergency_contact(self, db: Session, contact_id: int, update_data: EmergencyContactUpdate, user_id: str) -> Optional[EmergencyContact]:
        """更新紧急联系人"""
        contact = self.get_emergency_contact(db, contact_id, user_id)
        if not contact:
            return None

        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(contact, field, value)

        contact.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(contact)
        return contact

    def delete_emergency_contact(self, db: Session, contact_id: int, user_id: str) -> bool:
        """删除紧急联系人"""
        contact = self.get_emergency_contact(db, contact_id, user_id)
        if not contact:
            return False

        db.delete(contact)
        db.commit()
        return True

    def set_primary_contact(self, db: Session, contact_id: int, user_id: str) -> Optional[EmergencyContact]:
        """设置主要紧急联系人"""
        # 取消其他联系人主要状态
        db.query(EmergencyContact).filter(
            and_(
                EmergencyContact.user_id == user_id,
                EmergencyContact.is_primary == True
            )
        ).update({EmergencyContact.is_primary: False})

        # 设置新的主要联系人
        contact = self.get_emergency_contact(db, contact_id, user_id)
        if not contact:
            return None

        contact.is_primary = True
        contact.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(contact)
        return contact

    def get_primary_contact(self, db: Session, user_id: str) -> Optional[EmergencyContact]:
        """获取主要紧急联系人"""
        return db.query(EmergencyContact).filter(
            and_(
                EmergencyContact.user_id == user_id,
                EmergencyContact.is_primary == True
            )
        ).first()

    def get_enabled_contacts(self, db: Session, user_id: str) -> List[EmergencyContact]:
        """获取启用通知的紧急联系人"""
        return db.query(EmergencyContact).filter(
            and_(
                EmergencyContact.user_id == user_id,
                EmergencyContact.notification_enabled == True
            )
        ).order_by(EmergencyContact.is_primary.desc()).all()
