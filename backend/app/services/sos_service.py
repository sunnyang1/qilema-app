"""
SOS求救服务

实现SOS求救请求的核心功能
"""

from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.sos_request import SOSRequest
from app.models.user import User
from app.schemas.sos_request import SOSRequestCreate, SOSRequestUpdate, SOSStatusUpdateRequest


class SOSService:
    """SOS求救服务"""

    def __init__(self):
        pass

    @staticmethod
    def create_sos_request(db: Session, user_id: str, sos_data: SOSRequestCreate) -> SOSRequest:
        """创建SOS求救请求

        Args:
            db: 数据库会话
            user_id: 用户ID（从认证获取，不可篡改）
            sos_data: SOS请求数据

        Returns:
            创建的SOS请求
        """
        from app.models.sos_request import SOSTypeEnum

        sos_type = sos_data.sos_type or sos_data.trigger_type or SOSTypeEnum.MANUAL.value

        sos = SOSRequest(
            user_id=user_id,  # 使用认证用户的ID，防止IDOR攻击
            sos_type=sos_type,
            latitude=sos_data.latitude,
            longitude=sos_data.longitude,
            address=sos_data.address or sos_data.location_description,
            location_accuracy=sos_data.location_accuracy,
            emergency_reason=sos_data.emergency_reason
        )
        db.add(sos)
        db.commit()
        db.refresh(sos)
        return sos

    @staticmethod
    def get_sos_requests(db: Session, user_id: str, limit: int = 20, offset: int = 0):
        """获取用户的SOS请求列表"""
        return db.query(SOSRequest).filter(
            SOSRequest.user_id == user_id
        ).order_by(desc(SOSRequest.trigger_time)).offset(offset).limit(limit).all()

    @staticmethod
    def get_sos_by_id(db: Session, sos_id: str, user_id: str) -> Optional[SOSRequest]:
        """根据ID获取SOS请求"""
        return db.query(SOSRequest).filter(
            SOSRequest.id == sos_id,
            SOSRequest.user_id == user_id
        ).first()

    @staticmethod
    def get_sos_request(db: Session, sos_id: str, user_id: str) -> Optional[SOSRequest]:
        """根据ID获取SOS请求"""
        return db.query(SOSRequest).filter(
            SOSRequest.id == sos_id,
            SOSRequest.user_id == user_id
        ).first()

    @staticmethod
    def get_active_sos(db: Session, user_id: str) -> Optional[SOSRequest]:
        """获取活动的SOS请求"""
        from app.models.sos_request import SOSStatusEnum
        return db.query(SOSRequest).filter(
            SOSRequest.user_id == user_id,
            SOSRequest.status == SOSStatusEnum.PENDING.value
        ).first()

    @staticmethod
    def update_sos_status(db: Session, sos_id: str, user_id: str, update_data: SOSStatusUpdateRequest) -> Optional[SOSRequest]:
        """更新SOS请求状态"""
        from app.models.sos_request import SOSStatusEnum
        from datetime import datetime

        sos = SOSService.get_sos_by_id(db, sos_id, user_id)
        if not sos:
            return None

        if update_data.status:
            sos.status = update_data.status
            # 如果状态变为救援中，设置救援开始时间
            if update_data.status == SOSStatusEnum.RESCUING.value:
                sos.rescue_start_time = datetime.utcnow()
            # 如果状态变为已解决或已取消，设置解决时间
            if update_data.status in [SOSStatusEnum.RESOLVED.value, SOSStatusEnum.CANCELLED.value]:
                sos.resolve_time = datetime.utcnow()

        if update_data.status_change_reason:
            sos.status_change_reason = update_data.status_change_reason
        if update_data.ambulance_contact:
            sos.ambulance_contact = update_data.ambulance_contact
        if update_data.ambulance_eta is not None:
            sos.ambulance_eta = update_data.ambulance_eta

        db.commit()
        db.refresh(sos)
        return sos

    @staticmethod
    def cancel_sos_request(db: Session, sos_id: int, user_id: str, cancel_data) -> Optional[SOSRequest]:
        """取消SOS请求"""
        from app.models.sos_request import SOSStatusEnum

        sos = SOSService.get_sos_by_id(db, sos_id, user_id)
        if not sos:
            return None

        # 只能取消待救援状态的SOS请求
        if sos.status != SOSStatusEnum.PENDING.value:
            raise ValueError("只能取消待救援状态的SOS请求")

        sos.status = SOSStatusEnum.CANCELLED.value
        sos.resolve_time = datetime.utcnow()

        if cancel_data.cancel_reason:
            sos.status_change_reason = cancel_data.cancel_reason

        db.commit()
        db.refresh(sos)
        return sos

    @staticmethod
    def add_location_history(db: Session, sos_id: int, user_id: str, location_data):
        """添加位置历史"""
        from app.models.sos_request import SOSLocationHistory

        location_history = SOSLocationHistory(
            sos_request_id=sos_id,
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            address=location_data.location_description,
            location_accuracy=location_data.location_accuracy
        )
        db.add(location_history)
        db.commit()
        db.refresh(location_history)
        return location_history

    @staticmethod
    def get_sos_history(db: Session, user_id: str, limit: int = 20, offset: int = 0):
        """获取SOS历史记录"""
        from app.models.sos_request import SOSRequest
        query = db.query(SOSRequest).filter(SOSRequest.user_id == user_id)
        total = query.count()
        sos_requests = query.order_by(desc(SOSRequest.trigger_time)).offset(offset).limit(limit).all()
        return sos_requests, total

    @staticmethod
    def get_emergency_contacts(db: Session, user_id: str):
        """获取紧急联系人列表"""
        from app.models.emergency_contact import EmergencyContact
        return db.query(EmergencyContact).filter(
            EmergencyContact.user_id == user_id
        ).order_by(EmergencyContact.priority.asc()).all()

    @staticmethod
    def get_sos_statistics(db: Session, user_id: str):
        """获取SOS统计信息"""
        from app.models.sos_request import SOSStatusEnum

        stats = {
            "total_sos": 0,
            "pending_sos": 0,
            "rescuing_sos": 0,
            "resolved_sos": 0,
            "cancelled_sos": 0
        }

        sos_list = db.query(SOSRequest).filter(SOSRequest.user_id == user_id).all()
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
