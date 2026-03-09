"""
Models包初始化文件
按依赖顺序导入所有模型，确保SQLAlchemy能正确解析关联关系
"""

from .alert import Alert
from .anomaly import ActivityPattern, Anomaly, HealthTrend
from .checkin import CheckIn
from .device import Device
from .device_data import DeviceData, DeviceThreshold
from .emergency_center_model import (
    Ambulance,
    EmergencyCall,
    EmergencyCenter,
    RescueRecord,
)

# 关联模型（依赖User）
from .emergency_contact import EmergencyContact
from .emergency_resource_model import (
    EmergencyResource,
    NavigationRoute,
    ResourceDepartment,
    ResourceFacility,
    ResourceUsageLog,
)
from .health_record import HealthRecord
from .knowledge_base import KnowledgeArticle, KnowledgeCategory, KnowledgeTag
from .login_record import LoginRecord
from .medication import (
    MedicationReminderItem,
    MedicationReminderLog,
    MedicationReminderNotification,
    MedicationReminderSchedule,
)
from .notification_model import Notification
from .sos_request import SOSRequest

# 基础模型（无外部依赖）
from .user import User
from .user_setting_model import UserSetting

__all__ = [
    "User",
    "EmergencyCenter",
    "EmergencyResource",
    "EmergencyContact",
    "CheckIn",
    "Alert",
    "SOSRequest",
    "Device",
    "HealthRecord",
    "DeviceData",
    "DeviceThreshold",
    "LoginRecord",
    "UserSetting",
    "EmergencyCall",
    "Ambulance",
    "RescueRecord",
    "Notification",
    "ResourceFacility",
    "ResourceDepartment",
    "ResourceUsageLog",
    "NavigationRoute",
    "KnowledgeCategory",
    "KnowledgeTag",
    "KnowledgeArticle",
    "Anomaly",
    "HealthTrend",
    "ActivityPattern",
    "MedicationReminderItem",
    "MedicationReminderSchedule",
    "MedicationReminderNotification",
    "MedicationReminderLog",
]
