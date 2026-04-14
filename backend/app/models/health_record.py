"""健康档案数据模型 (SQLAlchemy 2.x)"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_mixin import BaseModelMixin

from ..core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class HealthRecord(Base, BaseModelMixin):
    """健康档案主表 (SQLAlchemy 2.x)"""

    __tablename__ = "health_records"

    __table_args__ = (
        Index("idx_health_records_user_id", "user_id"),  # For user health record lookup
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, comment="健康档案ID"
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.user_id"),
        index=True,
        nullable=False,
        comment="用户ID",
    )

    # 基础信息
    real_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="真实姓名")
    gender: Mapped[str] = mapped_column(String(10), nullable=False, comment="性别:男/女/其他")
    blood_type: Mapped[Optional[str]] = mapped_column(String(5), comment="血型")
    height: Mapped[Optional[float]] = mapped_column(Float, comment="身高(cm)")
    weight: Mapped[Optional[float]] = mapped_column(Float, comment="体重(kg)")
    age: Mapped[Optional[int]] = mapped_column(Integer, comment="年龄")

    # 紧急医疗联系人
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(
        String(50), comment="紧急医疗联系人姓名"
    )
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(
        String(20), comment="紧急医疗联系人电话"
    )
    emergency_contact_relation: Mapped[Optional[str]] = mapped_column(
        String(20), comment="紧急医疗联系人关系"
    )

    # 加密存储标识
    is_encrypted: Mapped[int] = mapped_column(
        Integer, default=0, comment="是否加密:0-否 1-是"
    )

    # 健康档案数据（JSON字符串存储）
    chronic_diseases_json: Mapped[Optional[str]] = mapped_column(
        "chronic_diseases", Text, comment="慢性病史，JSON数组字符串"
    )
    allergies_json: Mapped[Optional[str]] = mapped_column(
        "allergies", Text, comment="过敏史，JSON数组字符串"
    )
    current_medications_json: Mapped[Optional[str]] = mapped_column(
        "current_medications", Text, comment="当前用药，JSON数组字符串"
    )
    surgeries_json: Mapped[Optional[str]] = mapped_column(
        "surgeries", Text, comment="手术史，JSON数组字符串"
    )
    blood_transfusion_history: Mapped[int] = mapped_column(
        Integer, default=0, comment="输血史:0-否 1-是"
    )
    organ_transplant_history: Mapped[int] = mapped_column(
        Integer, default=0, comment="器官移植史:0-否 1-是"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间",
    )

    # 关联关系
    # One-to-one with User - HealthRecord always needs user info
    user: Mapped["User"] = relationship(
        "User", back_populates="health_record", lazy="joined"
    )
    # Medical histories, medications, allergies - medium frequency
    medical_histories: Mapped[List["MedicalHistory"]] = relationship(
        "MedicalHistory",
        back_populates="health_record",
        cascade="all, delete-orphan",
        lazy="select",
    )
    medications: Mapped[List["Medication"]] = relationship(
        "Medication",
        back_populates="health_record",
        cascade="all, delete-orphan",
        lazy="select",
    )
    allergies: Mapped[List["Allergy"]] = relationship(
        "Allergy",
        back_populates="health_record",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def to_dict(
        self, exclude: Optional[List[str]] = None, include: Optional[List[str]] = None
    ) -> dict:
        """转换为字典"""
        return super().to_dict(exclude=exclude, include=include)


class MedicalHistory(Base):
    """病史记录表 (SQLAlchemy 2.x)"""

    __tablename__ = "medical_histories"

    __table_args__ = (
        Index(
            "idx_medical_histories_health_record_id", "health_record_id"
        ),  # For health record lookup
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, comment="病史ID"
    )
    health_record_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("health_records.id"),
        index=True,
        nullable=False,
        comment="健康档案ID",
    )

    disease_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="疾病名称"
    )
    diagnosis_date: Mapped[Optional[datetime]] = mapped_column(DateTime, comment="诊断日期")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="详细描述")
    severity: Mapped[Optional[str]] = mapped_column(String(20), comment="严重程度")
    is_chronic: Mapped[int] = mapped_column(Integer, default=0, comment="是否慢性病")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间",
    )

    # 关联关系
    health_record: Mapped["HealthRecord"] = relationship(
        "HealthRecord", back_populates="medical_histories"
    )

    def to_dict(self) -> dict:
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
    """用药信息表 (SQLAlchemy 2.x)"""

    __tablename__ = "medications"

    __table_args__ = (
        Index(
            "idx_medications_health_record_id", "health_record_id"
        ),  # For health record lookup
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, comment="用药ID"
    )
    health_record_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("health_records.id"),
        index=True,
        nullable=False,
        comment="健康档案ID",
    )

    drug_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="药品名称")
    dosage: Mapped[Optional[str]] = mapped_column(String(50), comment="剂量")
    frequency: Mapped[Optional[str]] = mapped_column(String(50), comment="用药频率")
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, comment="开始用药日期")
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, comment="结束用药日期")
    is_current: Mapped[int] = mapped_column(Integer, default=1, comment="是否正在使用")
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间",
    )

    # 关联关系
    health_record: Mapped["HealthRecord"] = relationship(
        "HealthRecord", back_populates="medications"
    )

    def to_dict(self) -> dict:
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
    """过敏史表 (SQLAlchemy 2.x)"""

    __tablename__ = "allergies"

    __table_args__ = (
        Index(
            "idx_allergies_health_record_id", "health_record_id"
        ),  # For health record lookup
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, comment="过敏ID"
    )
    health_record_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("health_records.id"),
        index=True,
        nullable=False,
        comment="健康档案ID",
    )

    allergen: Mapped[str] = mapped_column(String(100), nullable=False, comment="过敏原")
    allergic_reaction: Mapped[Optional[str]] = mapped_column(
        String(200), comment="过敏反应"
    )
    severity: Mapped[Optional[str]] = mapped_column(String(20), comment="严重程度")
    discovered_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="发现日期"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间",
    )

    # 关联关系
    health_record: Mapped["HealthRecord"] = relationship(
        "HealthRecord", back_populates="allergies"
    )

    def to_dict(self) -> dict:
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
