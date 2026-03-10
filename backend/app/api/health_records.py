"""健康档案API路由

使用 ApiResponseBuilder 统一构建响应
"""

from app.api.dependencies import get_health_record_service
from app.core.exceptions import (
    InternalServerException,
    NotFoundException,
    ValidationException,
)
from app.core.response_builder import ApiResponseBuilder
from app.schemas.health_record import (
    AllergyCreate,
    AllergyResponse,
    AllergyUpdate,
    HealthRecordCreate,
    HealthRecordResponse,
    HealthRecordUpdate,
    MedicalHistoryCreate,
    MedicalHistoryResponse,
    MedicalHistoryUpdate,
    MedicationCreate,
    MedicationResponse,
    MedicationUpdate,
)
from app.services.health_record_service import HealthRecordService
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/health-records", tags=["健康档案"])


@router.post("/", summary="创建健康档案")
def create_health_record(
    data: HealthRecordCreate,
    service: HealthRecordService = Depends(get_health_record_service),
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
        health_record = service.create_health_record(data)
        return ApiResponseBuilder.success(
            data=HealthRecordResponse.model_validate(health_record).model_dump(),
            message="健康档案创建成功",
        )
    except ValueError as e:
        raise ValidationException(detail=str(e))
    except Exception as e:
        raise InternalServerException(detail=f"创建健康档案失败: {str(e)}")


@router.get("/{user_id}", summary="获取健康档案")
def get_health_record(
    user_id: str,
    service: HealthRecordService = Depends(get_health_record_service),
):
    """
    获取用户的完整健康档案,包含基础信息、病史记录、用药信息、过敏史
    """
    try:
        health_record = service.get_health_record(user_id)
        if not health_record:
            raise NotFoundException("健康档案不存在")

        # 获取关联数据（lazy="dynamic" 关系需要使用 .all()）
        medical_histories = [
            MedicalHistoryResponse.model_validate(mh)
            for mh in health_record.medical_histories.all()
        ]
        medications = [
            MedicationResponse.model_validate(med)
            for med in health_record.medications.all()
        ]
        allergies = [
            AllergyResponse.model_validate(allg)
            for allg in health_record.allergies.all()
        ]

        # 使用 Pydantic 模型序列化健康档案，并添加关联数据
        health_record_data = HealthRecordResponse.model_validate(
            health_record
        ).model_dump()
        health_record_data.update(
            {
                "chronic_diseases": health_record.chronic_diseases_json,
                "allergies_json": health_record.allergies_json,
                "current_medications": health_record.current_medications_json,
                "surgeries": health_record.surgeries_json,
                "blood_transfusion_history": health_record.blood_transfusion_history,
                "organ_transplant_history": health_record.organ_transplant_history,
                "medical_histories": [mh.model_dump() for mh in medical_histories],
                "medications": [med.model_dump() for med in medications],
                "allergies": [allg.model_dump() for allg in allergies],
            }
        )

        return ApiResponseBuilder.success(data=health_record_data, message="获取健康档案成功")
    except (ValidationException, NotFoundException):
        raise
    except Exception as e:
        raise InternalServerException(detail=f"获取健康档案失败: {str(e)}")


@router.put("/{user_id}", summary="更新健康档案")
def update_health_record(
    user_id: str,
    data: HealthRecordUpdate,
    service: HealthRecordService = Depends(get_health_record_service),
):
    """更新健康档案基础信息"""
    try:
        health_record = service.update_health_record(user_id, data)
        return ApiResponseBuilder.success(
            data=HealthRecordResponse.model_validate(health_record).model_dump(),
            message="健康档案更新成功",
        )
    except ValueError as e:
        raise ValidationException(detail=str(e))
    except Exception as e:
        raise InternalServerException(detail=f"更新健康档案失败: {str(e)}")


@router.post("/{user_id}/medical-histories", summary="添加病史记录")
def add_medical_history(
    user_id: str,
    data: MedicalHistoryCreate,
    service: HealthRecordService = Depends(get_health_record_service),
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
        health_record = service.get_health_record(user_id)
        if not health_record:
            raise NotFoundException("健康档案不存在")

        data.health_record_id = health_record.id
        medical_history = service.add_medical_history(health_record.id, data)

        # 使用 Pydantic 模型序列化
        return ApiResponseBuilder.success(
            data=MedicalHistoryResponse.model_validate(medical_history).model_dump(),
            message="病史记录添加成功",
        )
    except (ValidationException, NotFoundException):
        raise
    except Exception as e:
        raise InternalServerException(detail=f"添加病史记录失败: {str(e)}")


@router.get("/{user_id}/medical-histories", summary="获取病史记录列表")
def get_medical_histories(
    user_id: str,
    service: HealthRecordService = Depends(get_health_record_service),
):
    """获取用户的病史记录列表"""
    try:
        health_record = service.get_health_record(user_id)
        if not health_record:
            raise NotFoundException("健康档案不存在")

        medical_histories = service.get_medical_histories(health_record.id)

        # 使用 Pydantic 模型序列化
        return ApiResponseBuilder.success(
            data=[
                MedicalHistoryResponse.model_validate(mh).model_dump()
                for mh in medical_histories
            ],
            message="获取病史记录成功",
        )
    except (ValidationException, NotFoundException):
        raise
    except Exception as e:
        raise InternalServerException(detail=f"获取病史记录失败: {str(e)}")


@router.put("/medical-histories/{history_id}", summary="更新病史记录")
def update_medical_history(
    history_id: int,
    data: MedicalHistoryUpdate,
    service: HealthRecordService = Depends(get_health_record_service),
):
    """更新病史记录"""
    try:
        medical_history = service.update_medical_history(history_id, data)
        # 使用 Pydantic 模型序列化
        return ApiResponseBuilder.success(
            data=MedicalHistoryResponse.model_validate(medical_history).model_dump(),
            message="病史记录更新成功",
        )
    except ValueError as e:
        raise ValidationException(detail=str(e))
    except Exception as e:
        raise InternalServerException(detail=f"更新病史记录失败: {str(e)}")


@router.delete("/medical-histories/{history_id}", summary="删除病史记录")
def delete_medical_history(
    history_id: int,
    service: HealthRecordService = Depends(get_health_record_service),
):
    """删除病史记录"""
    try:
        service.delete_medical_history(history_id)
        return ApiResponseBuilder.success(message="病史记录删除成功")
    except ValueError as e:
        raise ValidationException(detail=str(e))
    except Exception as e:
        raise InternalServerException(detail=f"删除病史记录失败: {str(e)}")


@router.post("/{user_id}/medications", summary="添加用药信息")
def add_medication(
    user_id: str,
    data: MedicationCreate,
    service: HealthRecordService = Depends(get_health_record_service),
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
        health_record = service.get_health_record(user_id)
        if not health_record:
            raise NotFoundException("健康档案不存在")

        data.health_record_id = health_record.id
        medication = service.add_medication(health_record.id, data)

        # 使用 Pydantic 模型序列化
        return ApiResponseBuilder.success(
            data=MedicationResponse.model_validate(medication).model_dump(),
            message="用药信息添加成功",
        )
    except (ValidationException, NotFoundException):
        raise
    except Exception as e:
        raise InternalServerException(detail=f"添加用药信息失败: {str(e)}")


@router.get("/{user_id}/medications", summary="获取用药信息列表")
def get_medications(
    user_id: str,
    current_only: bool = False,
    service: HealthRecordService = Depends(get_health_record_service),
):
    """
    获取用户的用药信息列表

    - **current_only**: 是否只获取当前正在使用的药品
    """
    try:
        health_record = service.get_health_record(user_id)
        if not health_record:
            raise NotFoundException("健康档案不存在")

        medications = service.get_medications(health_record.id, current_only)

        # 使用 Pydantic 模型序列化
        return ApiResponseBuilder.success(
            data=[
                MedicationResponse.model_validate(med).model_dump()
                for med in medications
            ],
            message="获取用药信息成功",
        )
    except (ValidationException, NotFoundException):
        raise
    except Exception as e:
        raise InternalServerException(detail=f"获取用药信息失败: {str(e)}")


@router.put("/medications/{medication_id}", summary="更新用药信息")
def update_medication(
    medication_id: int,
    data: MedicationUpdate,
    service: HealthRecordService = Depends(get_health_record_service),
):
    """更新用药信息"""
    try:
        medication = service.update_medication(medication_id, data)
        return ApiResponseBuilder.success(
            data={
                "id": medication.id,
                "health_record_id": medication.health_record_id,
                "drug_name": medication.drug_name,
                "dosage": medication.dosage,
                "frequency": medication.frequency,
                "start_date": (
                    medication.start_date.isoformat() if medication.start_date else None
                ),
                "end_date": (
                    medication.end_date.isoformat() if medication.end_date else None
                ),
                "is_current": medication.is_current,
                "notes": medication.notes,
                "created_at": (
                    medication.created_at.isoformat() if medication.created_at else None
                ),
                "updated_at": (
                    medication.updated_at.isoformat() if medication.updated_at else None
                ),
            },
            message="用药信息更新成功",
        )
    except ValueError as e:
        raise ValidationException(detail=str(e))
    except Exception as e:
        raise InternalServerException(detail=f"更新用药信息失败: {str(e)}")


@router.delete("/medications/{medication_id}", summary="删除用药信息")
def delete_medication(
    medication_id: int,
    service: HealthRecordService = Depends(get_health_record_service),
):
    """删除用药信息"""
    try:
        service.delete_medication(medication_id)
        return ApiResponseBuilder.success(message="用药信息删除成功")
    except ValueError as e:
        raise ValidationException(detail=str(e))
    except Exception as e:
        raise InternalServerException(detail=f"删除用药信息失败: {str(e)}")


@router.post("/{user_id}/allergies", summary="添加过敏史")
def add_allergy(
    user_id: str,
    data: AllergyCreate,
    service: HealthRecordService = Depends(get_health_record_service),
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
        health_record = service.get_health_record(user_id)
        if not health_record:
            raise NotFoundException("健康档案不存在")

        data.health_record_id = health_record.id
        allergy = service.add_allergy(health_record.id, data)

        # 使用 Pydantic 模型序列化
        return ApiResponseBuilder.success(
            data=AllergyResponse.model_validate(allergy).model_dump(),
            message="过敏史添加成功",
        )
    except (ValidationException, NotFoundException):
        raise
    except Exception as e:
        raise InternalServerException(detail=f"添加过敏史失败: {str(e)}")


@router.get("/{user_id}/allergies", summary="获取过敏史列表")
def get_allergies(
    user_id: str,
    service: HealthRecordService = Depends(get_health_record_service),
):
    """获取用户的过敏史列表"""
    try:
        health_record = service.get_health_record(user_id)
        if not health_record:
            raise NotFoundException("健康档案不存在")

        allergies = service.get_allergies(health_record.id)

        # 使用 Pydantic 模型序列化
        return ApiResponseBuilder.success(
            data=[
                AllergyResponse.model_validate(allg).model_dump() for allg in allergies
            ],
            message="获取过敏史成功",
        )
    except (ValidationException, NotFoundException):
        raise
    except Exception as e:
        raise InternalServerException(detail=f"获取过敏史失败: {str(e)}")


@router.put("/allergies/{allergy_id}", summary="更新过敏史")
def update_allergy(
    allergy_id: int,
    data: AllergyUpdate,
    service: HealthRecordService = Depends(get_health_record_service),
):
    """更新过敏史"""
    try:
        allergy = service.update_allergy(allergy_id, data)
        # 使用 Pydantic 模型序列化
        return ApiResponseBuilder.success(
            data=AllergyResponse.model_validate(allergy).model_dump(),
            message="过敏史更新成功",
        )
    except ValueError as e:
        raise ValidationException(detail=str(e))
    except Exception as e:
        raise InternalServerException(detail=f"更新过敏史失败: {str(e)}")


@router.delete("/allergies/{allergy_id}", summary="删除过敏史")
def delete_allergy(
    allergy_id: int,
    service: HealthRecordService = Depends(get_health_record_service),
):
    """删除过敏史"""
    try:
        service.delete_allergy(allergy_id)
        return ApiResponseBuilder.success(message="过敏史删除成功")
    except ValueError as e:
        raise ValidationException(detail=str(e))
    except Exception as e:
        raise InternalServerException(detail=f"删除过敏史失败: {str(e)}")


@router.get("/{user_id}/summary", summary="生成健康档案摘要")
def generate_summary(
    user_id: str,
    service: HealthRecordService = Depends(get_health_record_service),
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
        summary = service.generate_summary(user_id)

        return ApiResponseBuilder.success(
            data={**summary.dict(), "summary_text": summary.generate_summary_text()},
            message="生成健康档案摘要成功",
        )
    except ValueError as e:
        raise NotFoundException(detail=str(e))
    except Exception as e:
        raise InternalServerException(detail=f"生成健康档案摘要失败: {str(e)}")
