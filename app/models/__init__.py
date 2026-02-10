"""
Models包初始化文件
按依赖顺序导入所有模型，确保SQLAlchemy能正确解析关联关系
"""

# 基础模型（无外部依赖）
from .user import User
from .emergency_center_model import EmergencyCenter
from .emergency_resource_model import EmergencyResource, ResourceFacility, ResourceDepartment, ResourceUsageLog, NavigationRoute
from .knowledge_base import KnowledgeCategory, KnowledgeTag, KnowledgeArticle

# 关联模型（依赖User）
from .emergency_contact import EmergencyContact
from .checkin import CheckIn
from .alert import Alert
from .sos_request import SOSRequest
from .device import Device
from .health_record import HealthRecord
from .device_data import DeviceData, DeviceThreshold
from .login_record import LoginRecord
from .user_setting_model import UserSetting
from .emergency_center_model import EmergencyCall, Ambulance, RescueRecord
from .notification_model import Notification
from .anomaly import Anomaly, HealthTrend, ActivityPattern
from .medication import (
    MedicationReminderItem, MedicationReminderSchedule,
    MedicationReminderNotification, MedicationReminderLog
)

__all__ = [
    'User', 'EmergencyCenter', 'EmergencyResource', 'EmergencyContact', 'CheckIn', 'Alert',
    'SOSRequest', 'Device', 'HealthRecord',
    'DeviceData', 'DeviceThreshold', 'LoginRecord', 'UserSetting',
    'EmergencyCall', 'Ambulance', 'RescueRecord', 'Notification',
    'ResourceFacility', 'ResourceDepartment', 'ResourceUsageLog', 'NavigationRoute',
    'KnowledgeCategory', 'KnowledgeTag', 'KnowledgeArticle',
    'Anomaly', 'HealthTrend', 'ActivityPattern',
    'MedicationReminderItem', 'MedicationReminderSchedule',
    'MedicationReminderNotification', 'MedicationReminderLog',
]
