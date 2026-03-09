"""
紧急联系人服务

实现紧急联系人管理、通知等核心功能
"""

from datetime import datetime
from typing import List, Optional

from app.core.cache import cache_result, get_cached, invalidate_cache
from app.core.cache_config import CacheConfig
from app.models.emergency_contact import EmergencyContact
from app.models.user import User
from app.schemas.emergency_contact import EmergencyContactCreate, EmergencyContactUpdate
from app.services.base_service import BaseService
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session


class EmergencyContactService(BaseService[EmergencyContact]):
    """紧急联系人服务 - 继承BaseService"""

    model_class = EmergencyContact
    cache_prefix = CacheConfig.PREFIX_EMERGENCY_CONTACT
    cache_ttl = CacheConfig.TTL_EMERGENCY_CONTACT

    def create_emergency_contact(
        self, db: Session, contact_data: EmergencyContactCreate, user_id: str
    ) -> EmergencyContact:
        """创建紧急联系人"""
        contact = EmergencyContact(
            user_id=user_id,
            name=contact_data.contact_name,
            relationship=contact_data.relationship,
            phone=contact_data.phone,
            is_primary=1 if contact_data.is_primary else 0,
            priority=contact_data.priority,
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)

        # 失效联系人列表缓存
        invalidate_cache(
            CacheConfig.make_key(CacheConfig.PREFIX_EMERGENCY_CONTACTS, user_id)
        )

        return contact

    def get_emergency_contacts(
        self, db: Session, user_id: str
    ) -> List[EmergencyContact]:
        """获取用户紧急联系人列表"""
        # 尝试从缓存获取
        cache_key = CacheConfig.make_key(CacheConfig.PREFIX_EMERGENCY_CONTACTS, user_id)
        cached_contacts = get_cached(cache_key)
        if cached_contacts:
            return cached_contacts

        contacts = (
            db.query(EmergencyContact)
            .filter(EmergencyContact.user_id == user_id)
            .order_by(
                EmergencyContact.is_primary.desc(), EmergencyContact.created_at.desc()
            )
            .all()
        )

        # 缓存结果
        cache_result(cache_key, contacts, ttl=CacheConfig.TTL_EMERGENCY_CONTACTS_LIST)

        return contacts

    def get_emergency_contact(
        self, db: Session, contact_id: int, user_id: str
    ) -> Optional[EmergencyContact]:
        """获取紧急联系人详情"""
        # 尝试从缓存获取
        cache_key = CacheConfig.make_key(
            CacheConfig.PREFIX_EMERGENCY_CONTACT, contact_id, user_id
        )
        cached_contact = get_cached(cache_key)
        if cached_contact:
            return cached_contact

        contact = (
            db.query(EmergencyContact)
            .filter(
                and_(
                    EmergencyContact.id == contact_id,
                    EmergencyContact.user_id == user_id,
                )
            )
            .first()
        )

        if contact:
            # 缓存结果
            cache_result(cache_key, contact, ttl=CacheConfig.TTL_EMERGENCY_CONTACT)

        return contact

    def update_emergency_contact(
        self,
        db: Session,
        contact_id: int,
        update_data: EmergencyContactUpdate,
        user_id: str,
    ) -> Optional[EmergencyContact]:
        """更新紧急联系人"""
        contact = self.get_emergency_contact(db, contact_id, user_id)
        if not contact:
            return None

        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(contact, field, value)

        contact.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(contact)

        # 失效单个联系人和列表缓存
        invalidate_cache(
            CacheConfig.make_key(
                CacheConfig.PREFIX_EMERGENCY_CONTACT, contact_id, user_id
            )
        )
        invalidate_cache(
            CacheConfig.make_key(CacheConfig.PREFIX_EMERGENCY_CONTACTS, user_id)
        )

        return contact

    def delete_emergency_contact(
        self, db: Session, contact_id: int, user_id: str
    ) -> bool:
        """删除紧急联系人"""
        contact = self.get_emergency_contact(db, contact_id, user_id)
        if not contact:
            return False

        db.delete(contact)
        db.commit()

        # 失效单个联系人和列表缓存
        invalidate_cache(
            CacheConfig.make_key(
                CacheConfig.PREFIX_EMERGENCY_CONTACT, contact_id, user_id
            )
        )
        invalidate_cache(
            CacheConfig.make_key(CacheConfig.PREFIX_EMERGENCY_CONTACTS, user_id)
        )

        return True

    def set_primary_contact(
        self, db: Session, contact_id: int, user_id: str
    ) -> Optional[EmergencyContact]:
        """设置主要紧急联系人"""
        # 取消其他联系人主要状态
        db.query(EmergencyContact).filter(
            and_(
                EmergencyContact.user_id == user_id,
                EmergencyContact.is_primary.is_(True),
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

        # 失效列表缓存（主要联系人变化影响列表排序）
        invalidate_cache(
            CacheConfig.make_key(CacheConfig.PREFIX_EMERGENCY_CONTACTS, user_id)
        )

        return contact

    def get_primary_contact(
        self, db: Session, user_id: str
    ) -> Optional[EmergencyContact]:
        """获取主要紧急联系人"""
        return (
            db.query(EmergencyContact)
            .filter(
                and_(
                    EmergencyContact.user_id == user_id,
                    EmergencyContact.is_primary.is_(True),
                )
            )
            .first()
        )

    def get_enabled_contacts(self, db: Session, user_id: str) -> List[EmergencyContact]:
        """获取启用通知的紧急联系人"""
        return (
            db.query(EmergencyContact)
            .filter(
                and_(
                    EmergencyContact.user_id == user_id,
                    EmergencyContact.notification_enabled.is_(True),
                )
            )
            .order_by(EmergencyContact.is_primary.desc())
            .all()
        )
