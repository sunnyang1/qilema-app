"""健康档案服务层"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
import os

from app.models.health_record import (
    HealthRecord, MedicalHistory, Medication, Allergy
)
from app.schemas.health_record import (
    HealthRecordCreate, HealthRecordUpdate,
    MedicalHistoryCreate, MedicalHistoryUpdate,
    MedicationCreate, MedicationUpdate,
    AllergyCreate, AllergyUpdate,
    HealthRecordSummary
)
from app.models.user import User


class EncryptionService:
    """加密服务"""
    
    def __init__(self):
        # 从环境变量获取加密密钥,如果没有则生成新密钥
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            # 在生产环境中应该从安全的地方获取密钥
            key = Fernet.generate_key()
        self.cipher = Fernet(key)
    
    def encrypt(self, text: str) -> str:
        """加密文本"""
        if not text:
            return text
        return self.cipher.encrypt(text.encode()).decode()
    
    def decrypt(self, encrypted_text: str) -> str:
        """解密文本"""
        if not encrypted_text:
            return encrypted_text
        return self.cipher.decrypt(encrypted_text.encode()).decode()


class HealthRecordService:
    """健康档案服务"""
    
    def __init__(self):
        self.encryption_service = EncryptionService()
    
    def create_health_record(self, db: Session, data: HealthRecordCreate, encrypt: bool = True) -> HealthRecord:
        """创建健康档案"""
        # 检查用户是否已有健康档案
        existing = db.query(HealthRecord).filter(HealthRecord.user_id == data.user_id).first()
        if existing:
            raise ValueError("该用户已存在健康档案")
        
        # 创建健康档案
        health_record = HealthRecord(
            user_id=data.user_id,
            real_name=self._encrypt_field(data.real_name, encrypt),
            gender=data.gender,
            blood_type=data.blood_type,
            height=data.height,
            weight=data.weight,
            age=data.age,
            emergency_contact_name=self._encrypt_field(data.emergency_contact_name, encrypt),
            emergency_contact_phone=self._encrypt_field(data.emergency_contact_phone, encrypt),
            emergency_contact_relation=data.emergency_contact_relation,
            is_encrypted=1 if encrypt else 0
        )
        
        db.add(health_record)
        db.commit()
        db.refresh(health_record)
        
        return self._decrypt_record(health_record, encrypt)
    
    def get_health_record(self, db: Session, user_id: str) -> Optional[HealthRecord]:
        """获取健康档案"""
        health_record = db.query(HealthRecord).filter(HealthRecord.user_id == user_id).first()
        if not health_record:
            return None
        
        return self._decrypt_record(health_record, health_record.is_encrypted == 1)
    
    def update_health_record(self, db: Session, user_id: str, data: HealthRecordUpdate) -> HealthRecord:
        """更新健康档案"""
        health_record = db.query(HealthRecord).filter(HealthRecord.user_id == user_id).first()
        if not health_record:
            raise ValueError("健康档案不存在")
        
        is_encrypted = health_record.is_encrypted == 1
        
        # 更新字段
        if data.real_name is not None:
            health_record.real_name = self._encrypt_field(data.real_name, is_encrypted)
        if data.gender is not None:
            health_record.gender = data.gender
        if data.blood_type is not None:
            health_record.blood_type = data.blood_type
        if data.height is not None:
            health_record.height = data.height
        if data.weight is not None:
            health_record.weight = data.weight
        if data.age is not None:
            health_record.age = data.age
        if data.emergency_contact_name is not None:
            health_record.emergency_contact_name = self._encrypt_field(data.emergency_contact_name, is_encrypted)
        if data.emergency_contact_phone is not None:
            health_record.emergency_contact_phone = self._encrypt_field(data.emergency_contact_phone, is_encrypted)
        if data.emergency_contact_relation is not None:
            health_record.emergency_contact_relation = data.emergency_contact_relation
        
        health_record.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(health_record)
        
        return self._decrypt_record(health_record, is_encrypted)
    
    def add_medical_history(self, db: Session, health_record_id: int, data: MedicalHistoryCreate) -> MedicalHistory:
        """添加病史记录"""
        health_record = db.query(HealthRecord).filter(HealthRecord.id == health_record_id).first()
        if not health_record:
            raise ValueError("健康档案不存在")
        
        medical_history = MedicalHistory(
            health_record_id=health_record_id,
            disease_name=data.disease_name,
            diagnosis_date=data.diagnosis_date,
            description=data.description,
            severity=data.severity,
            is_chronic=data.is_chronic or 0
        )
        
        db.add(medical_history)
        db.commit()
        db.refresh(medical_history)
        
        return medical_history
    
    def get_medical_histories(self, db: Session, health_record_id: int) -> List[MedicalHistory]:
        """获取病史记录列表"""
        return db.query(MedicalHistory).filter(
            MedicalHistory.health_record_id == health_record_id
        ).order_by(MedicalHistory.diagnosis_date.desc()).all()
    
    def update_medical_history(self, db: Session, history_id: int, data: MedicalHistoryUpdate) -> MedicalHistory:
        """更新病史记录"""
        medical_history = db.query(MedicalHistory).filter(MedicalHistory.id == history_id).first()
        if not medical_history:
            raise ValueError("病史记录不存在")
        
        if data.disease_name is not None:
            medical_history.disease_name = data.disease_name
        if data.diagnosis_date is not None:
            medical_history.diagnosis_date = data.diagnosis_date
        if data.description is not None:
            medical_history.description = data.description
        if data.severity is not None:
            medical_history.severity = data.severity
        if data.is_chronic is not None:
            medical_history.is_chronic = data.is_chronic
        
        medical_history.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(medical_history)
        
        return medical_history
    
    def delete_medical_history(self, db: Session, history_id: int) -> bool:
        """删除病史记录"""
        medical_history = db.query(MedicalHistory).filter(MedicalHistory.id == history_id).first()
        if not medical_history:
            raise ValueError("病史记录不存在")
        
        db.delete(medical_history)
        db.commit()
        return True
    
    def add_medication(self, db: Session, health_record_id: int, data: MedicationCreate) -> Medication:
        """添加用药信息"""
        health_record = db.query(HealthRecord).filter(HealthRecord.id == health_record_id).first()
        if not health_record:
            raise ValueError("健康档案不存在")
        
        medication = Medication(
            health_record_id=health_record_id,
            drug_name=data.drug_name,
            dosage=data.dosage,
            frequency=data.frequency,
            start_date=data.start_date,
            end_date=data.end_date,
            is_current=1 if data.is_current else 0,
            notes=data.notes
        )
        
        db.add(medication)
        db.commit()
        db.refresh(medication)
        
        return medication
    
    def get_medications(self, db: Session, health_record_id: int, current_only: bool = False) -> List[Medication]:
        """获取用药信息列表"""
        query = db.query(Medication).filter(Medication.health_record_id == health_record_id)
        
        if current_only:
            # 使用精确的整型比较确保过滤准确
            query = query.filter(Medication.is_current == 1)
        
        medications = query.order_by(Medication.created_at.desc()).all()
        
        # 双重确保过滤 - 在Python层面再次验证
        if current_only:
            medications = [m for m in medications if m.is_current == 1]
        
        return medications
    
    def update_medication(self, db: Session, medication_id: int, data: MedicationUpdate) -> Medication:
        """更新用药信息"""
        medication = db.query(Medication).filter(Medication.id == medication_id).first()
        if not medication:
            raise ValueError("用药信息不存在")
        
        if data.drug_name is not None:
            medication.drug_name = data.drug_name
        if data.dosage is not None:
            medication.dosage = data.dosage
        if data.frequency is not None:
            medication.frequency = data.frequency
        if data.start_date is not None:
            medication.start_date = data.start_date
        if data.end_date is not None:
            medication.end_date = data.end_date
        if data.is_current is not None:
            medication.is_current = 1 if data.is_current else 0
        if data.notes is not None:
            medication.notes = data.notes
        
        medication.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(medication)
        
        return medication
    
    def delete_medication(self, db: Session, medication_id: int) -> bool:
        """删除用药信息"""
        medication = db.query(Medication).filter(Medication.id == medication_id).first()
        if not medication:
            raise ValueError("用药信息不存在")
        
        db.delete(medication)
        db.commit()
        return True
    
    def add_allergy(self, db: Session, health_record_id: int, data: AllergyCreate) -> Allergy:
        """添加过敏史"""
        health_record = db.query(HealthRecord).filter(HealthRecord.id == health_record_id).first()
        if not health_record:
            raise ValueError("健康档案不存在")
        
        allergy = Allergy(
            health_record_id=health_record_id,
            allergen=data.allergen,
            allergic_reaction=data.allergic_reaction,
            severity=data.severity,
            discovered_date=data.discovered_date,
            notes=data.notes
        )
        
        db.add(allergy)
        db.commit()
        db.refresh(allergy)
        
        return allergy
    
    def get_allergies(self, db: Session, health_record_id: int) -> List[Allergy]:
        """获取过敏史列表"""
        return db.query(Allergy).filter(
            Allergy.health_record_id == health_record_id
        ).order_by(Allergy.discovered_date.desc()).all()
    
    def update_allergy(self, db: Session, allergy_id: int, data: AllergyUpdate) -> Allergy:
        """更新过敏史"""
        allergy = db.query(Allergy).filter(Allergy.id == allergy_id).first()
        if not allergy:
            raise ValueError("过敏史不存在")
        
        if data.allergen is not None:
            allergy.allergen = data.allergen
        if data.allergic_reaction is not None:
            allergy.allergic_reaction = data.allergic_reaction
        if data.severity is not None:
            allergy.severity = data.severity
        if data.discovered_date is not None:
            allergy.discovered_date = data.discovered_date
        if data.notes is not None:
            allergy.notes = data.notes
        
        allergy.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(allergy)
        
        return allergy
    
    def delete_allergy(self, db: Session, allergy_id: int) -> bool:
        """删除过敏史"""
        allergy = db.query(Allergy).filter(Allergy.id == allergy_id).first()
        if not allergy:
            raise ValueError("过敏史不存在")
        
        db.delete(allergy)
        db.commit()
        return True
    
    def generate_summary(self, db: Session, user_id: str) -> HealthRecordSummary:
        """生成健康档案摘要"""
        health_record = self.get_health_record(db, user_id)
        if not health_record:
            raise ValueError("健康档案不存在")
        
        # 获取慢性病
        chronic_diseases = [
            mh.disease_name 
            for mh in health_record.medical_histories 
            if mh.is_chronic == 1
        ]
        
        # 获取当前用药
        current_medications = [
            med.drug_name 
            for med in health_record.medications 
            if med.is_current == 1
        ]
        
        # 获取严重过敏
        severe_allergies = [
            allg.allergen 
            for allg in health_record.allergies 
            if allg.severity == '严重'
        ]
        
        # 构建紧急联系人列表
        emergency_contacts = []
        if health_record.emergency_contact_name and health_record.emergency_contact_phone:
            emergency_contacts.append({
                "name": health_record.emergency_contact_name,
                "phone": health_record.emergency_contact_phone,
                "relation": health_record.emergency_contact_relation or ""
            })
        
        summary = HealthRecordSummary(
            real_name=health_record.real_name,
            gender=health_record.gender,
            age=health_record.age,
            blood_type=health_record.blood_type,
            height=health_record.height,
            weight=health_record.weight,
            chronic_diseases=chronic_diseases,
            current_medications=current_medications,
            allergies=severe_allergies,  # 只包含严重过敏
            emergency_contacts=emergency_contacts,
            recent_anomalies=None  # 暂时留空
        )
        
        return summary
    
    def _encrypt_field(self, field: Optional[str], encrypt: bool) -> Optional[str]:
        """加密字段"""
        if not encrypt or not field:
            return field
        return self.encryption_service.encrypt(field)
    
    def _decrypt_field(self, field: Optional[str], decrypt: bool) -> Optional[str]:
        """解密字段"""
        if not decrypt or not field:
            return field
        try:
            return self.encryption_service.decrypt(field)
        except Exception:
            # 如果解密失败,返回原值
            return field
    
    def _decrypt_record(self, record: HealthRecord, decrypt: bool) -> HealthRecord:
        """解密健康档案"""
        if decrypt:
            record.real_name = self._decrypt_field(record.real_name, True)
            record.emergency_contact_name = self._decrypt_field(record.emergency_contact_name, True)
            record.emergency_contact_phone = self._decrypt_field(record.emergency_contact_phone, True)
        return record
