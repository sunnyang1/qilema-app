"""
用户登录记录SQLAlchemy模型
"""

from typing import List, Optional

from app.core.database import Base
from app.models.base_mixin import BaseModelMixin
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship as db_relationship


class LoginRecord(Base, BaseModelMixin):
    """用户登录记录模型"""

    __tablename__ = "login_records"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    user_id = Column(
        String(36),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True,
        comment="用户ID",
    )
    ip_address = Column(String(45), nullable=True, comment="IP地址")
    device_type = Column(String(50), nullable=True, comment="设备类型")
    device_model = Column(String(100), nullable=True, comment="设备型号")
    os_version = Column(String(50), nullable=True, comment="操作系统版本")
    app_version = Column(String(50), nullable=True, comment="App版本")
    location = Column(String(100), nullable=True, comment="位置")
    latitude = Column(Integer, nullable=True, comment="纬度")
    longitude = Column(Integer, nullable=True, comment="经度")
    login_status = Column(String(20), nullable=False, comment="登录状态: success/failure")
    failure_reason = Column(Text, nullable=True, comment="失败原因")
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: __import__("datetime").datetime.now(),
        comment="登录时间",
    )
    logged_out_at = Column(DateTime, nullable=True, comment="登出时间")

    # 关系
    user = db_relationship("User", back_populates="login_records")
