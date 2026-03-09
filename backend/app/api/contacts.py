"""
紧急联系人API路由

使用 ApiResponseBuilder 统一构建响应
"""

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.core.response_builder import ApiResponseBuilder
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.emergency_contact import EmergencyContactCreate, EmergencyContactUpdate
from app.services.emergency_contact_service import EmergencyContactService
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(tags=["紧急联系人"])


@router.post("/", summary="创建紧急联系人")
async def create_emergency_contact(
    contact_data: EmergencyContactCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    创建紧急联系人

    - **contact_name**: 联系人姓名
    - **phone**: 联系电话
    - **relationship**: 关系
    - **is_primary**: 是否主要联系人
    - **priority**: 优先级
    - **notes**: 备注
    """
    # 验证用户ID匹配
    if contact_data.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权为其他用户创建联系人"
        )

    try:
        service = EmergencyContactService()
        contact = service.create_emergency_contact(
            db, contact_data, current_user.user_id
        )

        return ApiResponseBuilder.success(
            data={
                "id": contact.id,
                "contact_id": contact.contact_id,
                "name": contact.name,
                "phone": contact.phone,
                "relationship": contact.relationship,
                "is_primary": contact.is_primary,
                "priority": contact.priority,
                "created_at": (
                    contact.created_at.isoformat() if contact.created_at else None
                ),
            },
            message="创建紧急联系人成功",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建紧急联系人失败: {str(e)}",
        )


@router.get("/", summary="获取紧急联系人列表")
async def get_emergency_contacts(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """获取当前用户的紧急联系人列表"""
    service = EmergencyContactService()
    contacts = service.get_emergency_contacts(db, current_user.user_id)

    contact_list = [
        {
            "id": contact.id,
            "contact_id": contact.contact_id,
            "name": contact.name,
            "phone": contact.phone,
            "relationship": contact.relationship,
            "is_primary": contact.is_primary,
            "priority": contact.priority,
            "created_at": (
                contact.created_at.isoformat() if contact.created_at else None
            ),
        }
        for contact in contacts
    ]

    return ApiResponseBuilder.success(
        data={"total": len(contact_list), "contacts": contact_list},
        message="获取紧急联系人列表成功",
    )


@router.get("/{contact_id}", summary="获取紧急联系人详情")
async def get_emergency_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取紧急联系人详情"""
    service = EmergencyContactService()
    contact = service.get_emergency_contact(db, contact_id, current_user.user_id)

    if not contact:
        raise NotFoundException("紧急联系人不存在")

    return ApiResponseBuilder.success(
        data={
            "id": contact.id,
            "contact_id": contact.contact_id,
            "name": contact.name,
            "phone": contact.phone,
            "relationship": contact.relationship,
            "is_primary": contact.is_primary,
            "priority": contact.priority,
            "created_at": (
                contact.created_at.isoformat() if contact.created_at else None
            ),
            "updated_at": (
                contact.updated_at.isoformat() if contact.updated_at else None
            ),
        },
        message="获取紧急联系人详情成功",
    )


@router.put("/{contact_id}", summary="更新紧急联系人")
async def update_emergency_contact(
    contact_id: int,
    update_data: EmergencyContactUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    更新紧急联系人

    - **contact_name**: 联系人姓名
    - **phone**: 联系电话
    - **relationship**: 关系
    - **is_primary**: 是否主要联系人
    - **priority**: 优先级
    - **notes**: 备注
    """
    service = EmergencyContactService()
    contact = service.update_emergency_contact(
        db, contact_id, update_data, current_user.user_id
    )

    if not contact:
        raise NotFoundException("紧急联系人不存在")

    return ApiResponseBuilder.success(
        data={
            "id": contact.id,
            "contact_id": contact.contact_id,
            "name": contact.name,
            "phone": contact.phone,
            "relationship": contact.relationship,
            "is_primary": contact.is_primary,
            "priority": contact.priority,
        },
        message="更新紧急联系人成功",
    )


@router.delete("/{contact_id}", summary="删除紧急联系人")
async def delete_emergency_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除紧急联系人"""
    service = EmergencyContactService()
    success = service.delete_emergency_contact(db, contact_id, current_user.user_id)

    if not success:
        raise NotFoundException("紧急联系人不存在")

    return ApiResponseBuilder.success(message="删除紧急联系人成功")


@router.put("/{contact_id}/set-primary", summary="设置主要紧急联系人")
async def set_primary_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """设置指定联系人为主要紧急联系人"""
    service = EmergencyContactService()
    contact = service.set_primary_contact(db, contact_id, current_user.user_id)

    if not contact:
        raise NotFoundException("紧急联系人不存在")

    return ApiResponseBuilder.success(
        data={
            "id": contact.id,
            "contact_id": contact.contact_id,
            "name": contact.name,
            "phone": contact.phone,
            "is_primary": contact.is_primary,
        },
        message="设置主要紧急联系人成功",
    )
