"""健康档案API路由

使用 ApiResponseBuilder 统一构建响应
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.exceptions import ValidationException, NotFoundException, InternalServerException
from app.core.response_builder import ApiResponseBuilder
from app.services.health_record_service import HealthRecordService
from app.schemas.health_record import (
    HealthRecordCreate, HealthRecordUpdate, HealthRecordResponse, HealthRecordSummary,
    MedicalHistoryCreate, MedicalHistoryUpdate,
    MedicationCreate, MedicationUpdate,
    AllergyCreate, AllergyUpdate
)
from app.models.health_record import (
    HealthRecord, MedicalHistory, Medication, Allergy
)

router = APIRouter(prefix="/health-records", tags=["健康档案"])
health_service = HealthRecordService()


@router.post("/", summary="创建健康档案")
def create_health_record(
    data: HealthRecordCreate,
    db: Session = Depends(get_db)
):
    """
    创建健康档案

    - **user_id**: 用户ID
    - **real_name**: 真实姓名
    - **gender**: 性别(男/女/其他)
    - **blood_type**: 血型(A/B/O/AB/其他)
    - **height**: 身高(cm)
    - **weight**: 体重(kg)
    - **age**: 年龄
    - **emergency_contact_name**: 紧急医疗联系人姓名
    - **emergency_contact_phone**: 紧急医疗联系人电话
    - **emergency_contact_relation**: 紧急医疗联系人关系
    """
    try:
        health_record = health_service.create_health_record(db, data)
        return ApiResponseBuilder.success(data=health_record.to_dict(), message="健康档案创建成功")
    except ValueError as e:
        raise ValidationException(detail=str(e))
    except Exception as e:
        raise InternalServerException(detail=f"创建健康档案失败: {str(e)}")


@router.get("/{user_id}", summary="获取健康档案")
def get_health_record(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    获取用户的完整健康档案,包含基础信息、病史记录、用药信息、过敏史
    """
    try:
        health_record = health_service.get_health_record(db, user_id)
        if not health_record:
            raise NotFoundException("健康档案不存在")

        # 获取关联数据
        medical_histories = health_record.medical_histories.all()
        medications = health_record.medications.all()
        allergies = health_record.allergies.all()

        return ApiResponseBuilder.success(data={
            **health_record.to_dict(),
            "medical_histories": [mh.to_dict() for mh in medical_histories],
            "medications": [med.to_dict() for med in medications],
            "allergies": [allg.to_dict() for allg in allergies]
        }, message="获取健康档案成功")
    except (ValidationException, NotFoundException):
        raise
    except Exception as e:
        raise InternalServerException(detail=f"获取健康档案失败: {str(e)}")


@router.put("/{user_id}", summary="更新健康档案")
def update_health_record(
    user_id: str,
    data: HealthRecordUpdate,
    db: Session = Depends(get_db)
):
    """更新健康档案基础信息"""
    try:
        health_record = health_service.update_health_record(db, user_id, data)
        return ApiResponseBuilder.success(data=health_record.to_dict(), message="健康档案更新成功")
    except ValueError as e:
        raise ValidationException(detail=str(e))
    except Exception as e:
        raise InternalServerException(detail=f"更新健康档案失败: {str(e)}")


@router.post("/{user_id}/medical-histories", summary="添加病史记录")
def add_medical_history(
    user_id: str,
    data: MedicalHistoryCreate,
    db: Session = Depends(get_db)
):
    """
    添加病史记录

    - **disease_name**: 疾病名称
    - **diagnosis_date**: 诊断日期
    - **description**: 详细描述
    - **severity**: 严重程度(轻微/中等/严重)
    - **is_chronic**: 是否慢性病(0-否 1-是)
    """
    try:
        # 获取健康档案ID
        health_record = health_service.get_health_record(db, user_id)
        if not health_record:
            raise NotFoundException("健康档案不存在")

        data.health_record_id = health_record.id
        medical_history = health_service.add_medical_history(db, health_record.id, data)

        return ApiResponseBuilder.success(data=medical_history.to_dict(), message="病史记录添加成功")
    except (ValidationException, NotFoundException):
        raise
    except Exception as e:
        raise InternalServerException(detail=f"添加病史记录失败: {str(e)}")


@router.get("/{user_id}/medical-histories", summary="获取病史记录列表")
def get_medical_histories(
    user_id: str,
    db: Session = Depends(get_db)
):
    """获取用户的病史记录列表"""
    try:
        health_record = health_service.get_health_record(db, user_id)
        if not health_record:
            raise NotFoundException("健康档案不存在")

        medical_histories = health_service.get_medical_histories(db, health_record.id)

        return ApiResponseBuilder.success(data=[mh.to_dict() for mh in medical_histories], message="获取病史记录成功")
    except (ValidationException, NotFoundException):
        raise
    except Exception as e:
        raise InternalServerException(detail=f"获取病史记录失败: {str(e)}")


@router.put("/medical-histories/{history_id}", summary="更新病史记录")
def update_medical_history(
    history_id: int,
    data: MedicalHistoryUpdate,
    db: Session = Depends(get_db)
):
    """更新病史记录"""
    try:
        medical_history = health_service.update_medical_history(db, history_id, data)
        return ApiResponseBuilder.success(data=medical_history.to_dict(), message="病史记录更新成功")
    except ValueError as e:
        raise ValidationException(detail=str(e))
    except Exception as e:
        raise InternalServerException(detail=f"更新病史记录失败: {str(e)}")


@router.delete("/medical-histories/{history_id}", summary="删除病史记录")
def delete_medical_history(
    history_id: int,
    db: Session = Depends(get_db)
):
    """删除病史记录"""
    try:
        health_service.delete_medical_history(db, history_id)
        return ApiResponseBuilder.success(message="病史记录删除成功")
    except ValueError as e:
        raise ValidationException(detail=str(e))
    except Exception as e:
        raise InternalServerException(detail=f"删除病史记录失败: {str(e)}")


@router.post("/{user_id}/medications", summary="添加用药信息")
def add_medication(
    user_id: str,
    data: MedicationCreate,
    db: Session = Depends(get_db)
):
    """
    添加用药信息

    - **drug_name**: 药品名称
    - **dosage**: 剂量
    - **frequency**: 用药频率
    - **start_date**: 开始用药日期
    - **end_date**: 结束用药日期
    - **is_current**: 是否正在使用(0-否 1-是)
    - **notes**: 备注
    """
    try:
        health_record = health_service.get_health_record(db, user_id)
        if not health_record:
            raise NotFoundException("健康档案不存在")

        data.health_record_id = health_record.id
        medication = health_service.add_medication(db, health_record.id, data)

        return ApiResponseBuilder.success(data=medication.to_dict(), message="用药信息添加成功")
    except (ValidationException, NotFoundException):
        raise
    except Exception as e:
        raise InternalServerException(detail=f"添加用药信息失败: {str(e)}")


@router.get("/{user_id}/medications", summary="获取用药信息列表")
def get_medications(
    user_id: str,
    current_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    获取用户的用药信息列表

    - **current_only**: 是否只获取当前正在使用的药品
    """
    try:
        health_record = health_service.get_health_record(db, user_id)
        if not health_record:
            raise NotFoundException("健康档案不存在")

        medications = health_service.get_medications(db, health_record.id, current_only)

        return ApiResponseBuilder.success(data=[med.to_dict() for med in medications], message="获取用药信息成功")
    except (ValidationException, NotFoundException):
        raise
    except Exception as e:
        raise InternalServerException(detail=f"获取用药信息失败: {str(e)}")


@router.put("/medications/{medication_id}", summary="更新用药信息")
def update_medication(
    medication_id: int,
    data: MedicationUpdate,
    db: Session = Depends(get_db)
):
    """更新用药信息"""
    try:
        medication = health_service.update_medication(db, medication_id, data)
        return ApiResponseBuilder.success(data=medication.to_dict(), message="用药信息更新成功")
    except ValueError as e:
        raise ValidationException(detail=str(e))
    except Exception as e:
        raise InternalServerException(detail=f"更新用药信息失败: {str(e)}")


@router.delete("/medications/{medication_id}", summary="删除用药信息")
def delete_medication(
    medication_id: int,
    db: Session = Depends(get_db)
):
    """删除用药信息"""
    try:
        health_service.delete_medication(db, medication_id)
        return ApiResponseBuilder.success(message="用药信息删除成功")
    except ValueError as e:
        raise ValidationException(detail=str(e))
    except Exception as e:
        raise InternalServerException(detail=f"删除用药信息失败: {str(e)}")


@router.post("/{user_id}/allergies", summary="添加过敏史")
def add_allergy(
    user_id: str,
    data: AllergyCreate,
    db: Session = Depends(get_db)
):
    """
    添加过敏史

    - **allergen**: 过敏原
    - **allergic_reaction**: 过敏反应
    - **severity**: 严重程度(轻微/中等/严重)
    - **discovered_date**: 发现日期
    - **notes**: 备注
    """
    try:
        health_record = health_service.get_health_record(db, user_id)
        if not health_record:
            raise NotFoundException("健康档案不存在")

        data.health_record_id = health_record.id
        allergy = health_service.add_allergy(db, health_record.id, data)

        return ApiResponseBuilder.success(data=allergy.to_dict(), message="过敏史添加成功")
    except (ValidationException, NotFoundException):
        raise
    except Exception as e:
        raise InternalServerException(detail=f"添加过敏史失败: {str(e)}")


@router.get("/{user_id}/allergies", summary="获取过敏史列表")
def get_allergies(
    user_id: str,
    db: Session = Depends(get_db)
):
    """获取用户的过敏史列表"""
    try:
        health_record = health_service.get_health_record(db, user_id)
        if not health_record:
            raise NotFoundException("健康档案不存在")

        allergies = health_service.get_allergies(db, health_record.id)

        return ApiResponseBuilder.success(data=[allg.to_dict() for allg in allergies], message="获取过敏史成功")
    except (ValidationException, NotFoundException):
        raise
    except Exception as e:
        raise InternalServerException(detail=f"获取过敏史失败: {str(e)}")


@router.put("/allergies/{allergy_id}", summary="更新过敏史")
def update_allergy(
    allergy_id: int,
    data: AllergyUpdate,
    db: Session = Depends(get_db)
):
    """更新过敏史"""
    try:
        allergy = health_service.update_allergy(db, allergy_id, data)
        return ApiResponseBuilder.success(data=allergy.to_dict(), message="过敏史更新成功")
    except ValueError as e:
        raise ValidationException(detail=str(e))
    except Exception as e:
        raise InternalServerException(detail=f"更新过敏史失败: {str(e)}")


@router.delete("/allergies/{allergy_id}", summary="删除过敏史")
def delete_allergy(
    allergy_id: int,
    db: Session = Depends(get_db)
):
    """删除过敏史"""
    try:
        health_service.delete_allergy(db, allergy_id)
        return ApiResponseBuilder.success(message="过敏史删除成功")
    except ValueError as e:
        raise ValidationException(detail=str(e))
    except Exception as e:
        raise InternalServerException(detail=f"删除过敏史失败: {str(e)}")


@router.get("/{user_id}/summary", summary="生成健康档案摘要")
def generate_summary(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    生成健康档案摘要,用于快速分享给急救人员

    摘要包含:
    - 基本信息(姓名、性别、年龄、血型)
    - 慢性病列表
    - 当前用药
    - 严重过敏原
    - 紧急联系人信息
    """
    try:
        summary = health_service.generate_summary(db, user_id)

        return ApiResponseBuilder.success(data={
            **summary.dict(),
            "summary_text": summary.generate_summary_text()
        }, message="生成健康档案摘要成功")
    except ValueError as e:
        raise NotFoundException(detail=str(e))
    except Exception as e:
        raise InternalServerException(detail=f"生成健康档案摘要失败: {str(e)}")
