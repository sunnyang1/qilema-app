"""
紧急联系人服务

实现紧急联系人管理、通知等核心功能
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.cache import cache_result, get_cached, invalidate_cache
from app.core.cache_config import CacheConfig
from app.models.emergency_contact import EmergencyContact
from app.schemas.emergency_contact import EmergencyContactCreate, EmergencyContactUpdate
from app.services.base_service import BaseService


class EmergencyContactService(BaseService[EmergencyContact]):
    """
    紧急联系人服务 - 实例方法模式

    提供紧急联系人的CRUD操作和通知管理

    Attributes:
        db: 数据库会话
        model_class: 紧急联系人模型类
    """

    model_class = EmergencyContact
    cache_prefix = CacheConfig.PREFIX_EMERGENCY_CONTACT
    cache_ttl = CacheConfig.TTL_EMERGENCY_CONTACT

    def __init__(self, db: Session):
        """
        初始化紧急联系人服务

        Args:
            db: 数据库会话
        """
        self.db = db

    # ========== 创建方法 ==========

    def create(
        self, contact_data: EmergencyContactCreate, user_id: str
    ) -> EmergencyContact:
        """
        创建紧急联系人

        Args:
            contact_data: 联系人数据
            user_id: 用户ID

        Returns:
            创建的紧急联系人
        """
        contact = EmergencyContact(
            user_id=user_id,
            name=contact_data.contact_name,
            relationship=contact_data.relationship,
            phone=contact_data.phone,
            is_primary=1 if contact_data.is_primary else 0,
            priority=contact_data.priority,
        )
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)

        # 失效联系人列表缓存
        invalidate_cache(
            CacheConfig.make_key(CacheConfig.PREFIX_EMERGENCY_CONTACTS, user_id)
        )

        return contact

    # ========== 查询方法 ==========

    def list(self, user_id: str) -> List[EmergencyContact]:
        """
        获取用户紧急联系人列表

        Args:
            user_id: 用户ID

        Returns:
            紧急联系人列表
        """
        # 尝试从缓存获取
        cache_key = CacheConfig.make_key(CacheConfig.PREFIX_EMERGENCY_CONTACTS, user_id)
        cached_contacts = get_cached(cache_key)
        if cached_contacts:
            return cached_contacts

        contacts = (
            self.db.query(EmergencyContact)
            .filter(EmergencyContact.user_id == user_id)
            .order_by(
                EmergencyContact.is_primary.desc(), EmergencyContact.created_at.desc()
            )
            .all()
        )

        # 缓存结果
        cache_result(cache_key, contacts, ttl=CacheConfig.TTL_EMERGENCY_CONTACTS_LIST)

        return contacts

    def get_by_id(self, contact_id: int, user_id: str) -> Optional[EmergencyContact]:
        """
        获取紧急联系人详情

        Args:
            contact_id: 联系人ID
            user_id: 用户ID

        Returns:
            紧急联系人或None
        """
        # 尝试从缓存获取
        cache_key = CacheConfig.make_key(
            CacheConfig.PREFIX_EMERGENCY_CONTACT, contact_id, user_id
        )
        cached_contact = get_cached(cache_key)
        if cached_contact:
            return cached_contact

        contact = (
            self.db.query(EmergencyContact)
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

    def get_primary(self, user_id: str) -> Optional[EmergencyContact]:
        """
        获取主要紧急联系人

        Args:
            user_id: 用户ID

        Returns:
            主要紧急联系人或None
        """
        return (
            self.db.query(EmergencyContact)
            .filter(
                and_(
                    EmergencyContact.user_id == user_id,
                    EmergencyContact.is_primary.is_(True),
                )
            )
            .first()
        )

    def get_enabled(self, user_id: str) -> List[EmergencyContact]:
        """
        获取启用通知的紧急联系人

        Args:
            user_id: 用户ID

        Returns:
            启用的紧急联系人列表
        """
        return (
            self.db.query(EmergencyContact)
            .filter(
                and_(
                    EmergencyContact.user_id == user_id,
                    EmergencyContact.notification_enabled.is_(True),
                )
            )
            .order_by(EmergencyContact.is_primary.desc())
            .all()
        )

    # ========== 更新方法 ==========

    def update(
        self,
        contact_id: int,
        update_data: EmergencyContactUpdate,
        user_id: str,
    ) -> Optional[EmergencyContact]:
        """
        更新紧急联系人

        Args:
            contact_id: 联系人ID
            update_data: 更新数据
            user_id: 用户ID

        Returns:
            更新后的联系人或None
        """
        contact = self.get_by_id(contact_id, user_id)
        if not contact:
            return None

        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(contact, field, value)

        contact.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(contact)

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

    def set_primary(self, contact_id: int, user_id: str) -> Optional[EmergencyContact]:
        """
        设置主要紧急联系人

        Args:
            contact_id: 联系人ID
            user_id: 用户ID

        Returns:
            设置后的联系人或None
        """
        # 取消其他联系人主要状态
        self.db.query(EmergencyContact).filter(
            and_(
                EmergencyContact.user_id == user_id,
                EmergencyContact.is_primary.is_(True),
            )
        ).update({EmergencyContact.is_primary: False})

        # 设置新的主要联系人
        contact = self.get_by_id(contact_id, user_id)
        if not contact:
            return None

        contact.is_primary = True
        contact.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(contact)

        # 失效列表缓存（主要联系人变化影响列表排序）
        invalidate_cache(
            CacheConfig.make_key(CacheConfig.PREFIX_EMERGENCY_CONTACTS, user_id)
        )

        return contact

    # ========== 删除方法 ==========

    def delete(self, contact_id: int, user_id: str) -> bool:
        """
        删除紧急联系人

        Args:
            contact_id: 联系人ID
            user_id: 用户ID

        Returns:
            是否成功删除
        """
        contact = self.get_by_id(contact_id, user_id)
        if not contact:
            return False

        self.db.delete(contact)
        self.db.commit()

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

    # ========== 向后兼容的适配器方法 ==========

    def create_emergency_contact(
        self, contact_data: EmergencyContactCreate, user_id: str
    ) -> EmergencyContact:
        """向后兼容：创建紧急联系人"""
        return self.create(contact_data, user_id)

    def get_emergency_contacts(self, user_id: str) -> List[EmergencyContact]:
        """向后兼容：获取用户紧急联系人列表"""
        return self.list(user_id)

    def get_emergency_contact(
        self, contact_id: int, user_id: str
    ) -> Optional[EmergencyContact]:
        """向后兼容：获取紧急联系人详情"""
        return self.get_by_id(contact_id, user_id)

    def update_emergency_contact(
        self,
        contact_id: int,
        update_data: EmergencyContactUpdate,
        user_id: str,
    ) -> Optional[EmergencyContact]:
        """向后兼容：更新紧急联系人"""
        return self.update(contact_id, update_data, user_id)

    def delete_emergency_contact(self, contact_id: int, user_id: str) -> bool:
        """向后兼容：删除紧急联系人"""
        return self.delete(contact_id, user_id)

    def set_primary_contact(
        self, contact_id: int, user_id: str
    ) -> Optional[EmergencyContact]:
        """向后兼容：设置主要紧急联系人"""
        return self.set_primary(contact_id, user_id)

    def get_primary_contact(self, user_id: str) -> Optional[EmergencyContact]:
        """向后兼容：获取主要紧急联系人"""
        return self.get_primary(user_id)

    def get_enabled_contacts(self, user_id: str) -> List[EmergencyContact]:
        """向后兼容：获取启用通知的紧急联系人"""
        return self.get_enabled(user_id)
