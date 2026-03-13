"""
API层依赖注入模块

提供通用的依赖注入函数，简化API路由的依赖管理
"""

from typing import Generator, TypeVar

from app.core.container import get_container
from app.core.database import get_db
from app.services.aed_service import AEDService
from app.services.alert_service import AlertService
from app.services.anomaly_service import AnomalyService
from app.services.checkin_service import CheckInService
from app.services.device_service import DeviceService
from app.services.emergency_center_service import EmergencyCenterService
from app.services.emergency_contact_service import EmergencyContactService
from app.services.emergency_resource_service import EmergencyResourceService
from app.services.health_record_service import HealthRecordService
from app.services.health_report_service import HealthReportService
from app.services.knowledge_service import KnowledgeBaseService
from app.services.medication_service import MedicationService
from app.services.notification import NotificationService
from app.services.sos_service import SOSService
from app.services.user_service import UserService
from fastapi import Depends
from sqlalchemy.orm import Session

# 类型变量用于泛型服务
cT = TypeVar("T")


# ========== 数据库会话依赖 ==========


def get_db_session() -> Generator[Session, None, None]:
    """
    获取数据库会话的生成器

    Yields:
        Session: 数据库会话
    """
    yield from get_db()


# ========== 服务依赖工厂函数 ==========


def get_user_service(db: Session = Depends(get_db_session)) -> UserService:
    """
    获取用户服务实例

    Args:
        db: 数据库会话

    Returns:
        UserService: 用户服务实例
    """
    return UserService(db)


def get_checkin_service(db: Session = Depends(get_db_session)) -> CheckInService:
    """
    获取签到服务实例

    Args:
        db: 数据库会话

    Returns:
        CheckInService: 签到服务实例
    """
    return CheckInService(db)


def get_sos_service(db: Session = Depends(get_db_session)) -> SOSService:
    """
    获取SOS服务实例

    Args:
        db: 数据库会话

    Returns:
        SOSService: SOS服务实例
    """
    return SOSService(db)


def get_emergency_contact_service(
    db: Session = Depends(get_db_session),
) -> EmergencyContactService:
    """
    获取紧急联系人服务实例

    Args:
        db: 数据库会话

    Returns:
        EmergencyContactService: 紧急联系人服务实例
    """
    return EmergencyContactService(db)


def get_emergency_resource_service(
    db: Session = Depends(get_db_session),
) -> EmergencyResourceService:
    """
    获取急救资源服务实例

    Args:
        db: 数据库会话

    Returns:
        EmergencyResourceService: 急救资源服务实例
    """
    return EmergencyResourceService(db)


def get_health_record_service(
    db: Session = Depends(get_db_session),
) -> HealthRecordService:
    """
    获取健康档案服务实例

    Args:
        db: 数据库会话

    Returns:
        HealthRecordService: 健康档案服务实例
    """
    return HealthRecordService(db)


def get_device_service(db: Session = Depends(get_db_session)) -> DeviceService:
    """
    获取设备服务实例

    Args:
        db: 数据库会话

    Returns:
        DeviceService: 设备服务实例
    """
    return DeviceService(db)


def get_alert_service(db: Session = Depends(get_db_session)) -> AlertService:
    """
    获取预警服务实例

    Args:
        db: 数据库会话

    Returns:
        AlertService: 预警服务实例
    """
    return AlertService(db)


def get_medication_service(
    db: Session = Depends(get_db_session),
) -> MedicationService:
    """
    获取用药服务实例

    Args:
        db: 数据库会话

    Returns:
        MedicationService: 用药服务实例
    """
    return MedicationService(db)


def get_medication_schedule_service(
    db: Session = Depends(get_db_session),
) -> "MedicationScheduleService":
    """
    获取用药计划服务实例

    Args:
        db: 数据库会话

    Returns:
        MedicationScheduleService: 用药计划服务实例
    """
    from app.services.medication_service import MedicationScheduleService

    return MedicationScheduleService(db)


def get_medication_reminder_service(
    db: Session = Depends(get_db_session),
) -> "MedicationReminderService":
    """
    获取用药提醒服务实例

    Args:
        db: 数据库会话

    Returns:
        MedicationReminderService: 用药提醒服务实例
    """
    from app.services.medication_service import MedicationReminderService

    return MedicationReminderService(db)


def get_medication_log_service(
    db: Session = Depends(get_db_session),
) -> "MedicationLogService":
    """
    获取服药记录服务实例

    Args:
        db: 数据库会话

    Returns:
        MedicationLogService: 服药记录服务实例
    """
    from app.services.medication_service import MedicationLogService

    return MedicationLogService(db)


def get_anomaly_service(db: Session = Depends(get_db_session)) -> AnomalyService:
    """
    获取异常检测服务实例

    Args:
        db: 数据库会话

    Returns:
        AnomalyService: 异常检测服务实例
    """
    return AnomalyService(db)


def get_aed_service(db: Session = Depends(get_db_session)) -> AEDService:
    """
    获取AED服务实例

    Args:
        db: 数据库会话

    Returns:
        AEDService: AED服务实例
    """
    return AEDService(db)


def get_emergency_center_service(
    db: Session = Depends(get_db_session),
) -> EmergencyCenterService:
    """
    获取急救中心服务实例

    Args:
        db: 数据库会话

    Returns:
        EmergencyCenterService: 急救中心服务实例
    """
    return EmergencyCenterService(db)


def get_knowledge_service(
    db: Session = Depends(get_db_session),
) -> KnowledgeBaseService:
    """
    获取知识库服务实例

    Args:
        db: 数据库会话

    Returns:
        KnowledgeBaseService: 知识库服务实例
    """
    return KnowledgeBaseService(db)


def get_health_report_service(
    db: Session = Depends(get_db_session),
) -> HealthReportService:
    """
    获取健康报告服务实例

    Args:
        db: 数据库会话

    Returns:
        HealthReportService: 健康报告服务实例
    """
    return HealthReportService(db)


def get_notification_service(
    db: Session = Depends(get_db_session),
) -> NotificationService:
    """
    获取通知服务实例

    Args:
        db: 数据库会话

    Returns:
        NotificationService: 通知服务实例
    """
    return NotificationService(db)


# ========== 从容器获取服务的便捷函数 ==========


def get_service_from_container(service_name: str):
    """
    从容器获取服务的通用函数

    Args:
        service_name: 服务名称（如 'user_service'）

    Returns:
        服务实例

    Example:
        >>> user_service = get_service_from_container('user_service')
    """
    container = get_container()
    return getattr(container, service_name)
