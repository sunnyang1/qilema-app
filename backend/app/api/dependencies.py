"""
API层依赖注入模块

提供通用的依赖注入函数，简化API路由的依赖管理

遵循 FastAPI 0.135.x 规范，使用 Annotated[..., Depends(...)] 模式
参考: https://fastapi.tiangolo.com/tutorial/dependencies/
"""

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

from typing import TYPE_CHECKING, TypeVar

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.async_database import get_async_db
from app.core.container import get_container
from app.core.database import get_db
from app.core.security import (
    get_current_active_user,
    get_current_admin,
    get_current_user,
)
from app.models.user import User
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

if TYPE_CHECKING:
    from app.services.medication_service import (
        MedicationLogService,
        MedicationReminderService,
        MedicationScheduleService,
    )

# 类型变量用于泛型服务
cT = TypeVar("T")

# ========== 数据库会话依赖 ==========


def get_db_session() -> Session:
    """
    获取数据库会话的生成器

    Yields:
        Session: 数据库会话
    """
    # 使用 next() 从生成器获取值
    return next(get_db())


# 标准数据库会话依赖，使用 Annotated 模式
DbSession = Annotated[Session, Depends(get_db)]

# 异步数据库会话依赖（Phase 2 新增）
AsyncDbSession = Annotated[AsyncSession, Depends(get_async_db)]


# ========== 服务依赖工厂函数 ==========


def get_user_service(db: DbSession) -> UserService:
    """
    获取用户服务实例

    Args:
        db: 数据库会话

    Returns:
        UserService: 用户服务实例
    """
    return UserService(db)


# 使用 Annotated 模式的用户服务依赖
UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_checkin_service(db: DbSession) -> CheckInService:
    """
    获取签到服务实例

    Args:
        db: 数据库会话

    Returns:
        CheckInService: 签到服务实例
    """
    return CheckInService(db)


# 使用 Annotated 模式的签到服务依赖
CheckInServiceDep = Annotated[CheckInService, Depends(get_checkin_service)]


def get_sos_service(db: DbSession) -> SOSService:
    """
    获取SOS服务实例

    Args:
        db: 数据库会话

    Returns:
        SOSService: SOS服务实例
    """
    return SOSService(db)


# 使用 Annotated 模式的SOS服务依赖
SOSServiceDep = Annotated[SOSService, Depends(get_sos_service)]


def get_emergency_contact_service(
    db: DbSession,
) -> EmergencyContactService:
    """
    获取紧急联系人服务实例

    Args:
        db: 数据库会话

    Returns:
        EmergencyContactService: 紧急联系人服务实例
    """
    return EmergencyContactService(db)


# 使用 Annotated 模式的紧急联系人服务依赖
EmergencyContactServiceDep = Annotated[
    EmergencyContactService, Depends(get_emergency_contact_service)
]


def get_emergency_resource_service(
    db: DbSession,
) -> EmergencyResourceService:
    """
    获取急救资源服务实例

    Args:
        db: 数据库会话

    Returns:
        EmergencyResourceService: 急救资源服务实例
    """
    return EmergencyResourceService(db)


# 使用 Annotated 模式的急救资源服务依赖
EmergencyResourceServiceDep = Annotated[
    EmergencyResourceService, Depends(get_emergency_resource_service)
]


def get_health_record_service(
    db: DbSession,
) -> HealthRecordService:
    """
    获取健康档案服务实例

    Args:
        db: 数据库会话

    Returns:
        HealthRecordService: 健康档案服务实例
    """
    return HealthRecordService(db)


# 使用 Annotated 模式的健康档案服务依赖
HealthRecordServiceDep = Annotated[
    HealthRecordService, Depends(get_health_record_service)
]


def get_device_service(db: DbSession) -> DeviceService:
    """
    获取设备服务实例

    Args:
        db: 数据库会话

    Returns:
        DeviceService: 设备服务实例
    """
    return DeviceService(db)


# 使用 Annotated 模式的设备服务依赖
DeviceServiceDep = Annotated[DeviceService, Depends(get_device_service)]


def get_alert_service(db: DbSession) -> AlertService:
    """
    获取预警服务实例

    Args:
        db: 数据库会话

    Returns:
        AlertService: 预警服务实例
    """
    return AlertService(db)


# 使用 Annotated 模式的预警服务依赖
AlertServiceDep = Annotated[AlertService, Depends(get_alert_service)]


def get_medication_service(
    db: DbSession,
) -> MedicationService:
    """
    获取用药服务实例

    Args:
        db: 数据库会话

    Returns:
        MedicationService: 用药服务实例
    """
    return MedicationService(db)


# 使用 Annotated 模式的用药服务依赖
MedicationServiceDep = Annotated[MedicationService, Depends(get_medication_service)]


def get_medication_schedule_service(
    db: DbSession,
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


# 使用 Annotated 模式的用药计划服务依赖
MedicationScheduleServiceDep = Annotated[
    "MedicationScheduleService", Depends(get_medication_schedule_service)
]


def get_medication_reminder_service(
    db: DbSession,
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


# 使用 Annotated 模式的用药提醒服务依赖
MedicationReminderServiceDep = Annotated[
    "MedicationReminderService", Depends(get_medication_reminder_service)
]


def get_medication_log_service(
    db: DbSession,
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


# 使用 Annotated 模式的服药记录服务依赖
MedicationLogServiceDep = Annotated[
    "MedicationLogService", Depends(get_medication_log_service)
]


def get_anomaly_service(db: DbSession) -> AnomalyService:
    """
    获取异常检测服务实例

    Args:
        db: 数据库会话

    Returns:
        AnomalyService: 异常检测服务实例
    """
    return AnomalyService(db)


# 使用 Annotated 模式的异常检测服务依赖
AnomalyServiceDep = Annotated[AnomalyService, Depends(get_anomaly_service)]


def get_aed_service(db: DbSession) -> AEDService:
    """
    获取AED服务实例

    Args:
        db: 数据库会话

    Returns:
        AEDService: AED服务实例
    """
    return AEDService(db)


# 使用 Annotated 模式的AED服务依赖
AEDServiceDep = Annotated[AEDService, Depends(get_aed_service)]


def get_emergency_center_service(
    db: DbSession,
) -> EmergencyCenterService:
    """
    获取急救中心服务实例

    Args:
        db: 数据库会话

    Returns:
        EmergencyCenterService: 急救中心服务实例
    """
    return EmergencyCenterService(db)


# 使用 Annotated 模式的急救中心服务依赖
EmergencyCenterServiceDep = Annotated[
    EmergencyCenterService, Depends(get_emergency_center_service)
]


def get_knowledge_service(
    db: DbSession,
) -> KnowledgeBaseService:
    """
    获取知识库服务实例

    Args:
        db: 数据库会话

    Returns:
        KnowledgeBaseService: 知识库服务实例
    """
    return KnowledgeBaseService(db)


# 使用 Annotated 模式的知识库服务依赖
KnowledgeBaseServiceDep = Annotated[
    KnowledgeBaseService, Depends(get_knowledge_service)
]


def get_health_report_service(
    db: DbSession,
) -> HealthReportService:
    """
    获取健康报告服务实例

    Args:
        db: 数据库会话

    Returns:
        HealthReportService: 健康报告服务实例
    """
    return HealthReportService(db)


# 使用 Annotated 模式的健康报告服务依赖
HealthReportServiceDep = Annotated[
    HealthReportService, Depends(get_health_report_service)
]


def get_notification_service(
    db: DbSession,
) -> NotificationService:
    """
    获取通知服务实例

    Args:
        db: 数据库会话

    Returns:
        NotificationService: 通知服务实例
    """
    return NotificationService(db)


# 使用 Annotated 模式的通知服务依赖
NotificationServiceDep = Annotated[
    NotificationService, Depends(get_notification_service)
]


# ========== 当前用户依赖 ==========

# 使用 Annotated 模式的当前用户依赖
CurrentUserDep = Annotated[User, Depends(get_current_user)]

# 使用 Annotated 模式的当前活跃用户依赖（验证账号状态）
CurrentActiveUserDep = Annotated[User, Depends(get_current_active_user)]

# 使用 Annotated 模式的管理员用户依赖
CurrentAdminDep = Annotated[User, Depends(get_current_admin)]


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
