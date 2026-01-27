"""
Models包初始化文件
按依赖顺序导入所有模型，确保SQLAlchemy能正确解析关联关系
"""

# 基础模型（无外部依赖）
from .user import User

# 关联模型（依赖User）
from .emergency_contact import EmergencyContact
from .checkin import CheckIn
from .alert import Alert
from .sos_request import SOSRequest
from .device import Device
from .health_record import HealthRecord
# from .anomaly import Anomaly  # 暂时注释,等待修复外键引用

__all__ = [
    'User', 'EmergencyContact', 'CheckIn', 'Alert',
    'SOSRequest', 'Device', 'HealthRecord',  # 'Anomaly',
]
