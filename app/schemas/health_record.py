"""
健康档案相关的Schema验证
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class HealthRecordCreate(BaseModel):
    """创建健康档案"""
    user_id: str = Field(..., description="用户ID")
    real_name: str = Field(..., min_length=1, max_length=50, description="真实姓名")
    gender: str = Field(..., description="性别: 男/女/其他")
    blood_type: Optional[str] = Field(None, description="血型: A/B/O/AB/其他")
    height: Optional[float] = Field(None, gt=0, le=300, description="身高(cm)")
    weight: Optional[float] = Field(None, gt=0, le=500, description="体重(kg)")
    age: Optional[int] = Field(None, gt=0, le=150, description="年龄")
    emergency_contact_name: Optional[str] = Field(None, max_length=50, description="紧急医疗联系人姓名")
    emergency_contact_phone: Optional[str] = Field(None, max_length=20, description="紧急医疗联系人电话")
    emergency_contact_relation: Optional[str] = Field(None, max_length=20, description="紧急医疗联系人关系")


class HealthRecordUpdate(BaseModel):
    """更新健康档案"""
    real_name: Optional[str] = Field(None, min_length=1, max_length=50)
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    height: Optional[float] = Field(None, gt=0, le=300)
    weight: Optional[float] = Field(None, gt=0, le=500)
    age: Optional[int] = Field(None, gt=0, le=150)
    emergency_contact_name: Optional[str] = Field(None, max_length=50)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relation: Optional[str] = Field(None, max_length=20)


class HealthRecordResponse(BaseModel):
    """健康档案响应"""
    id: int
    user_id: str
    real_name: str
    gender: str
    blood_type: Optional[str]
    height: Optional[float]
    weight: Optional[float]
    age: Optional[int]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    emergency_contact_relation: Optional[str]
    is_encrypted: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class MedicalHistoryCreate(BaseModel):
    """创建病史"""
    health_record_id: int = Field(..., description="健康档案ID")
    disease_name: str = Field(..., min_length=1, max_length=100, description="疾病名称")
    diagnosis_date: Optional[datetime] = Field(None, description="诊断日期")
    description: Optional[str] = Field(None, description="详细描述")
    severity: Optional[str] = Field(None, description="严重程度: 轻微/中等/严重")
    is_chronic: bool = Field(False, description="是否慢性病")


class MedicalHistoryResponse(BaseModel):
    """病史响应"""
    id: int
    health_record_id: int
    disease_name: str
    diagnosis_date: Optional[datetime]
    description: Optional[str]
    severity: Optional[str]
    is_chronic: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class MedicalHistoryUpdate(BaseModel):
    """更新病史"""
    disease_name: Optional[str] = Field(None, min_length=1, max_length=100)
    diagnosis_date: Optional[datetime] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    is_chronic: Optional[bool] = None


class MedicationCreate(BaseModel):
    """创建用药信息"""
    health_record_id: int = Field(..., description="健康档案ID")
    drug_name: str = Field(..., min_length=1, max_length=100, description="药品名称")
    dosage: Optional[str] = Field(None, max_length=50, description="剂量")
    frequency: Optional[str] = Field(None, max_length=50, description="用药频率")
    start_date: Optional[datetime] = Field(None, description="开始用药日期")
    end_date: Optional[datetime] = Field(None, description="结束用药日期")
    is_current: bool = Field(True, description="是否正在使用")
    notes: Optional[str] = Field(None, description="备注")


class MedicationResponse(BaseModel):
    """用药信息响应"""
    id: int
    health_record_id: int
    drug_name: str
    dosage: Optional[str]
    frequency: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    is_current: int
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class MedicationUpdate(BaseModel):
    """更新用药信息"""
    drug_name: Optional[str] = Field(None, min_length=1, max_length=100)
    dosage: Optional[str] = Field(None, max_length=50)
    frequency: Optional[str] = Field(None, max_length=50)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_current: Optional[bool] = None
    notes: Optional[str] = None


class AllergyCreate(BaseModel):
    """创建过敏史"""
    health_record_id: int = Field(..., description="健康档案ID")
    allergen: str = Field(..., min_length=1, max_length=100, description="过敏原")
    allergic_reaction: Optional[str] = Field(None, max_length=200, description="过敏反应")
    severity: Optional[str] = Field(None, description="严重程度: 轻微/中等/严重")
    discovered_date: Optional[datetime] = Field(None, description="发现日期")
    notes: Optional[str] = Field(None, description="备注")


class AllergyResponse(BaseModel):
    """过敏史响应"""
    id: int
    health_record_id: int
    allergen: str
    allergic_reaction: Optional[str]
    severity: Optional[str]
    discovered_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class AllergyUpdate(BaseModel):
    """更新过敏史"""
    allergen: Optional[str] = Field(None, min_length=1, max_length=100)
    allergic_reaction: Optional[str] = Field(None, max_length=200)
    severity: Optional[str] = None
    discovered_date: Optional[datetime] = None
    notes: Optional[str] = None


class HealthRecordSummary(BaseModel):
    """健康档案摘要"""
    real_name: str
    gender: str
    blood_type: Optional[str]
    age: Optional[int]
    height: Optional[float]
    weight: Optional[float]

    # 慢性病史
    chronic_diseases: Optional[list[str]] = None
    current_medications: Optional[list[str]] = None
    allergies: Optional[list[str]] = None

    # 最新健康数据
    latest_heart_rate: Optional[float] = None
    latest_blood_pressure: Optional[str] = None
    latest_blood_oxygen: Optional[float] = None

    # 紧急联系人
    emergency_contacts: Optional[list[dict]] = None

    # 最近设备异常
    recent_anomalies: Optional[list[dict]] = None

