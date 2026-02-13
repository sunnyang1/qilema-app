"""
服务接口抽象定义

定义业务服务的接口契约，确保服务实现遵循统一的规范
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any
from datetime import datetime, date
from sqlalchemy.orm import Session


class ICheckInService(ABC):
    """签到服务接口"""

    @abstractmethod
    def create_checkin(self, db: Session, user_id: str, checkin_data: Any) -> Any:
        """创建签到记录"""
        pass

    @abstractmethod
    def get_user_checkins(self, db: Session, user_id: str, offset: int = 0, limit: int = 20) -> List[Any]:
        """获取用户签到记录"""
        pass

    @abstractmethod
    def get_checkin_stats(self, db: Session, user_id: str) -> Any:
        """获取签到统计"""
        pass

    @abstractmethod
    def get_checkin_status(self, db: Session, user_id: str) -> Any:
        """获取签到状态"""
        pass

    @abstractmethod
    def check_today_checked_in(self, db: Session, user_id: str) -> bool:
        """检查今天是否已签到"""
        pass


class IUserService(ABC):
    """用户服务接口"""

    @abstractmethod
    def create_user(self, db: Session, user_data: Any) -> Any:
        """创建用户"""
        pass

    @abstractmethod
    def get_user_by_id(self, db: Session, user_id: str) -> Any:
        """根据ID获取用户"""
        pass

    @abstractmethod
    def get_user_by_phone(self, db: Session, phone: str) -> Any:
        """根据手机号获取用户"""
        pass

    @abstractmethod
    def update_user(self, db: Session, user_id: str, update_data: Any) -> Any:
        """更新用户信息"""
        pass

    @abstractmethod
    def authenticate(self, db: Session, phone: str, password: str) -> Any:
        """用户认证"""
        pass

    @abstractmethod
    def delete_user(self, db: Session, user_id: str) -> bool:
        """删除用户"""
        pass

    @abstractmethod
    def get_all_users(self, db: Session, offset: int = 0, limit: int = 20) -> Any:
        """获取所有用户"""
        pass


class IEmergencyContactService(ABC):
    """紧急联系人服务接口"""

    @abstractmethod
    def create_emergency_contact(self, db: Session, contact_data: Any) -> Any:
        """创建紧急联系人"""
        pass

    @abstractmethod
    def get_emergency_contacts(self, db: Session, user_id: str) -> List[Any]:
        """获取用户的紧急联系人列表"""
        pass

    @abstractmethod
    def get_emergency_contact_by_id(self, db: Session, contact_id: int) -> Any:
        """根据ID获取紧急联系人"""
        pass

    @abstractmethod
    def update_emergency_contact(self, db: Session, contact_id: int, update_data: Any) -> Any:
        """更新紧急联系人信息"""
        pass

    @abstractmethod
    def delete_emergency_contact(self, db: Session, contact_id: int) -> bool:
        """删除紧急联系人"""
        pass

    @abstractmethod
    def delete_user_emergency_contacts(self, db: Session, user_id: str) -> int:
        """删除用户的所有紧急联系人"""
        pass


class ISosService(ABC):
    """SOS服务接口"""

    @abstractmethod
    def create_sos_request(self, db: Session, sos_data: Any) -> Any:
        """创建SOS求助请求"""
        pass

    @abstractmethod
    def get_sos_request(self, db: Session, request_id: int) -> Any:
        """获取SOS请求详情"""
        pass

    @abstractmethod
    def get_user_sos_requests(self, db: Session, user_id: str, offset: int = 0, limit: int = 20) -> List[Any]:
        """获取用户的SOS请求列表"""
        pass

    @abstractmethod
    def cancel_sos_request(self, db: Session, request_id: int) -> bool:
        """取消SOS请求"""
        pass

    @abstractmethod
    def update_sos_status(self, db: Session, request_id: int, status: str) -> bool:
        """更新SOS请求状态"""
        pass

    @abstractmethod
    def get_active_sos_requests(self, db: Session) -> List[Any]:
        """获取所有活跃的SOS请求"""
        pass


class IHealthRecordService(ABC):
    """健康记录服务接口"""

    @abstractmethod
    def create_health_record(self, db: Session, record_data: Any) -> Any:
        """创建健康记录"""
        pass

    @abstractmethod
    def get_health_records(self, db: Session, user_id: str, offset: int = 0, limit: int = 20) -> List[Any]:
        """获取用户的健康记录"""
        pass

    @abstractmethod
    def get_health_record_by_id(self, db: Session, record_id: int) -> Any:
        """根据ID获取健康记录"""
        pass

    @abstractmethod
    def update_health_record(self, db: Session, record_id: int, update_data: Any) -> Any:
        """更新健康记录"""
        pass

    @abstractmethod
    def delete_health_record(self, db: Session, record_id: int) -> bool:
        """删除健康记录"""
        pass

    @abstractmethod
    def get_latest_records(self, db: Session, user_id: str, limit: int = 10) -> List[Any]:
        """获取最新健康记录"""
        pass


class INotificationService(ABC):
    """通知服务接口"""

    @abstractmethod
    def send_notification(self, db: Session, notification_data: Any) -> Any:
        """发送通知"""
        pass

    @abstractmethod
    def get_user_notifications(self, db: Session, user_id: str, offset: int = 0, limit: int = 20) -> List[Any]:
        """获取用户通知"""
        pass

    @abstractmethod
    def mark_as_read(self, db: Session, notification_id: int) -> bool:
        """标记通知为已读"""
        pass

    @abstractmethod
    def mark_all_as_read(self, db: Session, user_id: str) -> int:
        """标记所有通知为已读"""
        pass

    @abstractmethod
    def delete_notification(self, db: Session, notification_id: int) -> bool:
        """删除通知"""
        pass


class IDeviceService(ABC):
    """设备服务接口"""

    @abstractmethod
    def register_device(self, db: Session, device_data: Any) -> Any:
        """注册设备"""
        pass

    @abstractmethod
    def get_user_devices(self, db: Session, user_id: str) -> List[Any]:
        """获取用户设备"""
        pass

    @abstractmethod
    def update_device(self, db: Session, device_id: int, update_data: Any) -> Any:
        """更新设备信息"""
        pass

    @abstractmethod
    def delete_device(self, db: Session, device_id: int) -> bool:
        """删除设备"""
        pass

    @abstractmethod
    def update_device_status(self, db: Session, device_id: int, status: str) -> bool:
        """更新设备状态"""
        pass


class IAlertService(ABC):
    """告警服务接口"""

    @abstractmethod
    def create_alert(self, db: Session, alert_data: Any) -> Any:
        """创建告警"""
        pass

    @abstractmethod
    def get_alerts(self, db: Session, user_id: Optional[str] = None, status: Optional[str] = None, offset: int = 0, limit: int = 20) -> List[Any]:
        """获取告警列表"""
        pass

    @abstractmethod
    def get_alert_by_id(self, db: Session, alert_id: int) -> Any:
        """获取告警详情"""
        pass

    @abstractmethod
    def update_alert_status(self, db: Session, alert_id: int, status: str) -> bool:
        """更新告警状态"""
        pass

    @abstractmethod
    def get_active_alerts(self, db: Session) -> List[Any]:
        """获取活跃告警"""
        pass
