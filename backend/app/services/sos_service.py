"""
SOS求救服务

实现SOS求救请求的核心功能
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.models.emergency_contact import EmergencyContact
from app.models.sos_request import (
    SOSLocationHistory,
    SOSRequest,
    SOSStatusEnum,
    SOSTypeEnum,
)
from app.schemas.sos_request import SOSRequestCreate, SOSStatusUpdateRequest
from sqlalchemy import desc
from sqlalchemy.orm import Session


class SOSService:
    """
    SOS求救服务 - 实例方法模式

    提供SOS求救请求的核心功能

    Attributes:
        db: 数据库会话
    """

    def __init__(self, db: Session):
        """
        初始化SOS服务

        Args:
            db: 数据库会话
        """
        self.db = db

    # ========== 创建方法 ==========

    def create(self, user_id: str, sos_data: SOSRequestCreate) -> SOSRequest:
        """
        创建SOS求救请求

        Args:
            user_id: 用户ID（从认证获取，不可篡改）
            sos_data: SOS请求数据

        Returns:
            创建的SOS请求
        """
        sos_type = (
            sos_data.sos_type or sos_data.trigger_type or SOSTypeEnum.MANUAL.value
        )

        sos = SOSRequest(
            user_id=user_id,  # 使用认证用户的ID，防止IDOR攻击
            sos_type=sos_type,
            latitude=sos_data.latitude,
            longitude=sos_data.longitude,
            address=sos_data.address or sos_data.location_description,
            location_accuracy=sos_data.location_accuracy,
            emergency_reason=sos_data.emergency_reason,
        )
        self.db.add(sos)
        self.db.commit()
        self.db.refresh(sos)
        return sos

    # ========== 查询方法 ==========

    def get_by_id(self, sos_id: str, user_id: str) -> Optional[SOSRequest]:
        """
        根据ID获取SOS请求

        Args:
            sos_id: SOS请求ID
            user_id: 用户ID

        Returns:
            SOS请求对象或None
        """
        return (
            self.db.query(SOSRequest)
            .filter(SOSRequest.id == sos_id, SOSRequest.user_id == user_id)
            .first()
        )

    def list(self, user_id: str, limit: int = 20, offset: int = 0) -> List[SOSRequest]:
        """
        获取用户的SOS请求列表

        Args:
            user_id: 用户ID
            limit: 限制数量
            offset: 偏移量

        Returns:
            SOS请求列表
        """
        return (
            self.db.query(SOSRequest)
            .filter(SOSRequest.user_id == user_id)
            .order_by(desc(SOSRequest.trigger_time))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_active(self, user_id: str) -> Optional[SOSRequest]:
        """
        获取活动的SOS请求

        Args:
            user_id: 用户ID

        Returns:
            活动的SOS请求或None
        """
        return (
            self.db.query(SOSRequest)
            .filter(
                SOSRequest.user_id == user_id,
                SOSRequest.status == SOSStatusEnum.PENDING.value,
            )
            .first()
        )

    # ========== 更新方法 ==========

    def update_status(
        self, sos_id: str, user_id: str, update_data: SOSStatusUpdateRequest
    ) -> Optional[SOSRequest]:
        """
        更新SOS请求状态

        Args:
            sos_id: SOS请求ID
            user_id: 用户ID
            update_data: 更新数据

        Returns:
            更新后的SOS请求或None
        """
        sos = self.get_by_id(sos_id, user_id)
        if not sos:
            return None

        if update_data.status:
            sos.status = update_data.status
            # 如果状态变为救援中，设置救援开始时间
            if update_data.status == SOSStatusEnum.RESCUING.value:
                sos.rescue_start_time = datetime.utcnow()
            # 如果状态变为已解决或已取消，设置解决时间
            if update_data.status in [
                SOSStatusEnum.RESOLVED.value,
                SOSStatusEnum.CANCELLED.value,
            ]:
                sos.resolve_time = datetime.utcnow()

        if update_data.status_change_reason:
            sos.status_change_reason = update_data.status_change_reason
        if update_data.ambulance_contact:
            sos.ambulance_contact = update_data.ambulance_contact
        if update_data.ambulance_eta is not None:
            sos.ambulance_eta = update_data.ambulance_eta

        self.db.commit()
        self.db.refresh(sos)
        return sos

    def cancel(self, sos_id: int, user_id: str, cancel_data) -> Optional[SOSRequest]:
        """
        取消SOS请求

        Args:
            sos_id: SOS请求ID
            user_id: 用户ID
            cancel_data: 取消数据

        Returns:
            取消后的SOS请求或None

        Raises:
            ValueError: 只能取消待救援状态的SOS请求
        """
        sos = self.get_by_id(sos_id, user_id)
        if not sos:
            return None

        # 只能取消待救援状态的SOS请求
        if sos.status != SOSStatusEnum.PENDING.value:
            raise ValueError("只能取消待救援状态的SOS请求")

        sos.status = SOSStatusEnum.CANCELLED.value
        sos.resolve_time = datetime.utcnow()

        if cancel_data.cancel_reason:
            sos.status_change_reason = cancel_data.cancel_reason

        self.db.commit()
        self.db.refresh(sos)
        return sos

    # ========== 位置历史 ==========

    def add_location_history(self, sos_id: int, location_data) -> SOSLocationHistory:
        """
        添加位置历史

        Args:
            sos_id: SOS请求ID
            location_data: 位置数据

        Returns:
            位置历史记录
        """
        location_history = SOSLocationHistory(
            sos_request_id=sos_id,
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            address=location_data.location_description,
            location_accuracy=location_data.location_accuracy,
        )
        self.db.add(location_history)
        self.db.commit()
        self.db.refresh(location_history)
        return location_history

    # ========== 历史记录 ==========

    def get_history(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> Tuple[List[SOSRequest], int]:
        """
        获取SOS历史记录

        Args:
            user_id: 用户ID
            limit: 限制数量
            offset: 偏移量

        Returns:
            (SOS请求列表, 总数)
        """
        query = self.db.query(SOSRequest).filter(SOSRequest.user_id == user_id)
        total = query.count()
        sos_requests = (
            query.order_by(desc(SOSRequest.trigger_time))
            .offset(offset)
            .limit(limit)
            .all()
        )
        return sos_requests, total

    # ========== 紧急联系人 ==========

    def get_emergency_contacts(self, user_id: str) -> List[EmergencyContact]:
        """
        获取紧急联系人列表

        Args:
            user_id: 用户ID

        Returns:
            紧急联系人列表
        """
        return (
            self.db.query(EmergencyContact)
            .filter(EmergencyContact.user_id == user_id)
            .order_by(EmergencyContact.priority.asc())
            .all()
        )

    # ========== 统计 ==========

    def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        获取SOS统计信息

        Args:
            user_id: 用户ID

        Returns:
            统计信息字典
        """
        stats = {
            "total_sos": 0,
            "pending_sos": 0,
            "rescuing_sos": 0,
            "resolved_sos": 0,
            "cancelled_sos": 0,
        }

        sos_list = self.db.query(SOSRequest).filter(SOSRequest.user_id == user_id).all()
        stats["total_sos"] = len(sos_list)

        for sos in sos_list:
            if sos.status == SOSStatusEnum.PENDING.value:
                stats["pending_sos"] += 1
            elif sos.status == SOSStatusEnum.RESCUING.value:
                stats["rescuing_sos"] += 1
            elif sos.status == SOSStatusEnum.RESOLVED.value:
                stats["resolved_sos"] += 1
            elif sos.status == SOSStatusEnum.CANCELLED.value:
                stats["cancelled_sos"] += 1

        return stats

    # ========== 向后兼容的适配器方法 ==========

    def create_sos_request(
        self, user_id: str, sos_data: SOSRequestCreate
    ) -> SOSRequest:
        """向后兼容：创建SOS请求"""
        return self.create(user_id, sos_data)

    def get_sos_requests(self, user_id: str, limit: int = 20, offset: int = 0):
        """向后兼容：获取SOS请求列表"""
        return self.list(user_id, limit, offset)

    def get_sos_by_id(self, sos_id: str, user_id: str) -> Optional[SOSRequest]:
        """向后兼容：根据ID获取SOS请求"""
        return self.get_by_id(sos_id, user_id)

    def get_sos_request(self, sos_id: str, user_id: str) -> Optional[SOSRequest]:
        """向后兼容：根据ID获取SOS请求"""
        return self.get_by_id(sos_id, user_id)

    def get_active_sos(self, user_id: str) -> Optional[SOSRequest]:
        """向后兼容：获取活动的SOS请求"""
        return self.get_active(user_id)

    def update_sos_status(
        self, sos_id: str, user_id: str, update_data: SOSStatusUpdateRequest
    ) -> Optional[SOSRequest]:
        """向后兼容：更新SOS请求状态"""
        return self.update_status(sos_id, user_id, update_data)

    def cancel_sos_request(
        self, sos_id: int, user_id: str, cancel_data
    ) -> Optional[SOSRequest]:
        """向后兼容：取消SOS请求"""
        return self.cancel(sos_id, user_id, cancel_data)

    def get_sos_history(self, user_id: str, limit: int = 20, offset: int = 0):
        """向后兼容：获取SOS历史记录"""
        return self.get_history(user_id, limit, offset)

    def get_sos_statistics(self, user_id: str):
        """向后兼容：获取SOS统计信息"""
        return self.get_statistics(user_id)
