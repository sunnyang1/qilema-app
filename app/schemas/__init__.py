"""
Schema包初始化
"""
from app.schemas.user import UserRegister, UserLogin, UserResponse, UserUpdate
from app.schemas.token import Token, TokenData
from app.schemas.alert import (
    AlertSettingCreate, AlertSettingUpdate, AlertSettingResponse,
    AlertCreate, AlertResolveRequest, AlertResponse
)
from app.schemas.checkin import (
    CheckInCreate, CheckInResponse, CheckInDateQuery, CheckInStats,
    CheckInStatsResponse, CheckInStatusResponse
)
from app.schemas.device import (
    DeviceCreate, DeviceUpdate, DeviceResponse, DeviceDataCreate, DeviceDataQuery,
    DeviceBind, DeviceDataUpload, DeviceDataResponse,
    DeviceThresholdCreate, DeviceThresholdUpdate, DeviceThresholdResponse,
    DeviceStatusUpdate, DeviceStatistics, DeviceAlert
)
from app.schemas.health_record import (
    HealthRecordCreate, HealthRecordUpdate, HealthRecordResponse,
    MedicalHistoryCreate, MedicalHistoryResponse, MedicalHistoryUpdate,
    MedicationCreate, MedicationResponse, MedicationUpdate,
    AllergyCreate, AllergyResponse, AllergyUpdate
)
from app.schemas.emergency_contact import (
    EmergencyContactCreate, EmergencyContactUpdate, EmergencyContactResponse
)
from app.schemas.sos_request import SOSRequestCreate, SOSRequestUpdate, SOSRequestResponse

__all__ = [
    'UserRegister', 'UserLogin', 'UserResponse', 'UserUpdate',
    'Token', 'TokenData',
    'AlertSettingCreate', 'AlertSettingUpdate', 'AlertSettingResponse',
    'AlertCreate', 'AlertResolveRequest', 'AlertResponse',
    'CheckInCreate', 'CheckInResponse', 'CheckInDateQuery', 'CheckInStats',
    'CheckInStatsResponse', 'CheckInStatusResponse',
    'DeviceCreate', 'DeviceUpdate', 'DeviceResponse', 'DeviceDataCreate', 'DeviceDataQuery',
    'DeviceBind', 'DeviceDataUpload', 'DeviceDataResponse',
    'DeviceThresholdCreate', 'DeviceThresholdUpdate', 'DeviceThresholdResponse',
    'DeviceStatusUpdate', 'DeviceStatistics', 'DeviceAlert',
    'HealthRecordCreate', 'HealthRecordUpdate', 'HealthRecordResponse',
    'MedicalHistoryCreate', 'MedicalHistoryResponse', 'MedicalHistoryUpdate',
    'MedicationCreate', 'MedicationResponse', 'MedicationUpdate',
    'AllergyCreate', 'AllergyResponse', 'AllergyUpdate',
    'EmergencyContactCreate', 'EmergencyContactUpdate', 'EmergencyContactResponse',
    'SOSRequestCreate', 'SOSRequestUpdate', 'SOSRequestResponse',
]
