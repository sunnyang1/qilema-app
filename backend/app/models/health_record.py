"""健康档案数据模型"""

from datetime import datetime
from typing import List, Optional

from app.models.base_mixin import BaseModelMixin
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship as db_relationship

from ..core.database import Base


class HealthRecord(Base, BaseModelMixin):
    """健康档案主表"""

    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True, index=True, comment="健康档案ID")
    user_id = Column(
        String(36),
        ForeignKey("users.user_id"),
        index=True,
        nullable=False,
        comment="用户ID",
    )

    # 基础信息
    real_name = Column(String(50), nullable=False, comment="真实姓名")
    gender = Column(String(10), nullable=False, comment="性别:男/女/其他")
    blood_type = Column(String(5), comment="血型:A/B/O/AB/其他")
    height = Column(Float, comment="身高(cm)")
    weight = Column(Float, comment="体重(kg)")
    age = Column(Integer, comment="年龄")

    # 紧急医疗联系人
    emergency_contact_name = Column(String(50), comment="紧急医疗联系人姓名")
    emergency_contact_phone = Column(String(20), comment="紧急医疗联系人电话")
    emergency_contact_relation = Column(String(20), comment="紧急医疗联系人关系")

    # 加密存储标识
    is_encrypted = Column(Integer, default=0, comment="是否加密:0-否 1-是")

    # 健康档案数据（JSON字符串存储）
    chronic_diseases_json = Column("chronic_diseases", Text, comment="慢性病史，JSON数组字符串")
    allergies_json = Column("allergies", Text, comment="过敏史，JSON数组字符串")
    current_medications_json = Column(
        "current_medications", Text, comment="当前用药，JSON数组字符串"
    )
    surgeries_json = Column("surgeries", Text, comment="手术史，JSON数组字符串")
    blood_transfusion_history = Column(Integer, default=0, comment="输血史:0-否 1-是")
    organ_transplant_history = Column(Integer, default=0, comment="器官移植史:0-否 1-是")

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间"
    )

    # 关联关系
    user = db_relationship("User", back_populates="health_record")
    medical_histories = db_relationship(
        "MedicalHistory",
        back_populates="health_record",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    medications = db_relationship(
        "Medication",
        back_populates="health_record",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    allergies = db_relationship(
        "Allergy",
        back_populates="health_record",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def to_dict(
        self, exclude: Optional[List[str]] = None, include: Optional[List[str]] = None
    ) -> dict:
        """
        转换为字典

        Args:
            exclude: 要排除的字段列表
            include: 只包含的字段列表

        Returns:
            dict: 健康档案的字典表示
        """
        return super().to_dict(exclude=exclude, include=include)


class MedicalHistory(Base):
    """病史记录表"""

    __tablename__ = "medical_histories"

    id = Column(Integer, primary_key=True, index=True, comment="病史ID")
    health_record_id = Column(
        Integer,
        ForeignKey("health_records.id"),
        index=True,
        nullable=False,
        comment="健康档案ID",
    )

    disease_name = Column(String(100), nullable=False, comment="疾病名称")
    diagnosis_date = Column(DateTime, comment="诊断日期")
    description = Column(Text, comment="详细描述")
    severity = Column(String(20), comment="严重程度:轻微/中等/严重")
    is_chronic = Column(Integer, default=0, comment="是否慢性病:0-否 1-是")

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间"
    )

    # 关联关系
    health_record = db_relationship("HealthRecord", back_populates="medical_histories")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "health_record_id": self.health_record_id,
            "disease_name": self.disease_name,
            "diagnosis_date": (
                self.diagnosis_date.isoformat() if self.diagnosis_date else None
            ),
            "description": self.description,
            "severity": self.severity,
            "is_chronic": self.is_chronic,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Medication(Base):
    """用药信息表"""

    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True, comment="用药ID")
    health_record_id = Column(
        Integer,
        ForeignKey("health_records.id"),
        index=True,
        nullable=False,
        comment="健康档案ID",
    )

    drug_name = Column(String(100), nullable=False, comment="药品名称")
    dosage = Column(String(50), comment="剂量")
    frequency = Column(String(50), comment="用药频率")
    start_date = Column(DateTime, comment="开始用药日期")
    end_date = Column(DateTime, comment="结束用药日期")
    is_current = Column(Integer, default=1, comment="是否正在使用:0-否 1-是")
    notes = Column(Text, comment="备注")

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间"
    )

    # 关联关系
    health_record = db_relationship("HealthRecord", back_populates="medications")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "health_record_id": self.health_record_id,
            "drug_name": self.drug_name,
            "dosage": self.dosage,
            "frequency": self.frequency,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "is_current": self.is_current,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Allergy(Base):
    """过敏史表"""

    __tablename__ = "allergies"

    id = Column(Integer, primary_key=True, index=True, comment="过敏ID")
    health_record_id = Column(
        Integer,
        ForeignKey("health_records.id"),
        index=True,
        nullable=False,
        comment="健康档案ID",
    )

    allergen = Column(String(100), nullable=False, comment="过敏原")
    allergic_reaction = Column(String(200), comment="过敏反应")
    severity = Column(String(20), comment="严重程度:轻微/中等/严重")
    discovered_date = Column(DateTime, comment="发现日期")
    notes = Column(Text, comment="备注")

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间"
    )

    # 关联关系
    health_record = db_relationship("HealthRecord", back_populates="allergies")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "health_record_id": self.health_record_id,
            "allergen": self.allergen,
            "allergic_reaction": self.allergic_reaction,
            "severity": self.severity,
            "discovered_date": (
                self.discovered_date.isoformat() if self.discovered_date else None
            ),
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
