"""
预警服务层
"""
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import uuid

from app.models.alert import Alert, AlertSetting
from app.models.checkin import CheckIn
from app.models.emergency_contact import EmergencyContact
from app.schemas.alert import AlertSettingCreate, AlertSettingUpdate, AlertCreate


class AlertService:
    """预警服务类"""

    @staticmethod
    def create_or_update_setting(db: Session, user_id: str, setting_data: AlertSettingCreate) -> AlertSetting:
        """创建或更新预警配置"""
        # 查找现有配置
        setting = db.query(AlertSetting).filter(AlertSetting.user_id == user_id).first()

        # 转换notification_channels为字符串格式(用于测试兼容)
        notification_channels_str = None
        if setting_data.notification_channels:
            notification_channels_str = ','.join(setting_data.notification_channels)

        if setting:
            # 更新配置
            for field, value in setting_data.model_dump(exclude_unset=True).items():
                if field == 'notification_channels':
                    setattr(setting, field, notification_channels_str)
                else:
                    setattr(setting, field, value)
            setting.updated_at = datetime.now()
        else:
            # 创建新配置
            setting = AlertSetting(
                user_id=user_id,
                checkin_enabled=setting_data.checkin_enabled,
                checkin_threshold_hours=setting_data.checkin_threshold_hours,
                abnormal_enabled=setting_data.abnormal_enabled,
                enable_notification=setting_data.enable_notification,
                heart_rate_min=setting_data.heart_rate_min,
                heart_rate_max=setting_data.heart_rate_max,
                blood_pressure_systolic_min=setting_data.blood_pressure_systolic_min,
                blood_pressure_systolic_max=setting_data.blood_pressure_systolic_max,
                blood_pressure_diastolic_min=setting_data.blood_pressure_diastolic_min,
                blood_pressure_diastolic_max=setting_data.blood_pressure_diastolic_max,
                blood_oxygen_min=setting_data.blood_oxygen_min,
                notification_channels=notification_channels_str,
                emergency_contact_notify=setting_data.emergency_contact_notify,
                auto_resolve=setting_data.auto_resolve,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(setting)

        db.commit()
        db.refresh(setting)
        return setting

    @staticmethod
    def get_setting(db: Session, user_id: str) -> Optional[AlertSetting]:
        """获取预警配置"""
        return db.query(AlertSetting).filter(AlertSetting.user_id == user_id).first()

    @staticmethod
    def update_setting(db: Session, user_id: str, update_data: AlertSettingUpdate) -> Optional[AlertSetting]:
        """更新预警配置"""
        setting = db.query(AlertSetting).filter(AlertSetting.user_id == user_id).first()
        if not setting:
            return None
        
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(setting, field, value)
        setting.updated_at = datetime.now()
        
        db.commit()
        db.refresh(setting)
        return setting

    @staticmethod
    def create_alert(db: Session, user_id: str, alert_data: AlertCreate) -> Alert:
        """创建预警"""
        # 映射字符串类型到整数类型
        type_mapping = {
            "checkin_absent": 1,
            "physiological_abnormal": 2,
            "sos_missed": 3
        }
        alert_type_int = type_mapping.get(alert_data.alert_type, 1)  # 默认为1

        alert = Alert(
            alert_id=str(uuid.uuid4()),
            user_id=alert_data.user_id if alert_data.user_id else user_id,
            alert_type=alert_type_int,
            trigger_time=alert_data.trigger_time,
            status=0,
            abnormal_data=alert_data.abnormal_data,
            created_at=datetime.now()
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    @staticmethod
    def resolve_alert(db: Session, alert_id: str, resolve_note: Optional[str] = None) -> Optional[Alert]:
        """解决预警"""
        alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
        if not alert:
            return None
        
        alert.status = 1
        alert.resolved_at = datetime.now()
        db.commit()
        db.refresh(alert)
        return alert

    @staticmethod
    def get_alert(db: Session, alert_id: str) -> Optional[Alert]:
        """获取预警"""
        return db.query(Alert).filter(Alert.alert_id == alert_id).first()

    @staticmethod
    def get_user_alerts(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Alert]:
        """获取用户预警列表"""
        return db.query(Alert).filter(Alert.user_id == user_id).order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_pending_alerts(db: Session) -> List[Alert]:
        """获取待处理的预警"""
        return db.query(Alert).filter(Alert.status == 0).order_by(Alert.trigger_time).all()

    @staticmethod
    def check_missed_checkin(db: Session, user_id: str) -> Optional[Alert]:
        """检查是否未签到"""
        setting = AlertService.get_setting(db, user_id)
        if not setting or not setting.checkin_enabled:
            return None
        
        # 获取最后签到时间
        last_checkin = db.query(CheckIn).filter(CheckIn.user_id == user_id).order_by(Checkin.checkin_time.desc()).first()
        
        if not last_checkin:
            # 从未签到过
            return None
        
        # 检查是否超过阈值
        threshold = datetime.now() - timedelta(hours=setting.checkin_threshold_hours)
        if last_checkin.checkin_time < threshold:
            # 检查是否已有未解决的预警
            existing_alert = db.query(Alert).filter(
                Alert.user_id == user_id,
                Alert.alert_type == 1,
                Alert.status == 0
            ).first()
            
            if not existing_alert:
                # 创建新预警
                alert_data = AlertCreate(
                    alert_type=1,
                    trigger_time=datetime.now(),
                    abnormal_data={
                        "last_checkin_time": last_checkin.checkin_time.isoformat(),
                        "threshold_hours": setting.checkin_threshold_hours
                    }
                )
                return AlertService.create_alert(db, user_id, alert_data)
        
        return None

    @staticmethod
    def check_abnormal_data(db: Session, user_id: str, health_data: dict) -> Optional[Alert]:
        """检查生理数据异常"""
        setting = AlertService.get_setting(db, user_id)
        if not setting or not setting.abnormal_enabled:
            return None
        
        abnormal_info = {}
        
        # 检查心率
        heart_rate = health_data.get("heart_rate")
        if heart_rate:
            if setting.heart_rate_min and heart_rate < setting.heart_rate_min:
                abnormal_info["heart_rate_low"] = heart_rate
            if setting.heart_rate_max and heart_rate > setting.heart_rate_max:
                abnormal_info["heart_rate_high"] = heart_rate
        
        # 检查血压
        if "systolic" in health_data and "diastolic" in health_data:
            systolic = health_data["systolic"]
            diastolic = health_data["diastolic"]
            
            if setting.blood_pressure_systolic_min and systolic < setting.blood_pressure_systolic_min:
                abnormal_info["blood_pressure_systolic_low"] = systolic
            if setting.blood_pressure_systolic_max and systolic > setting.blood_pressure_systolic_max:
                abnormal_info["blood_pressure_systolic_high"] = systolic
            if setting.blood_pressure_diastolic_min and diastolic < setting.blood_pressure_diastolic_min:
                abnormal_info["blood_pressure_diastolic_low"] = diastolic
            if setting.blood_pressure_diastolic_max and diastolic > setting.blood_pressure_diastolic_max:
                abnormal_info["blood_pressure_diastolic_high"] = diastolic
        
        # 检查血氧
        blood_oxygen = health_data.get("blood_oxygen")
        if blood_oxygen and setting.blood_oxygen_min and blood_oxygen < setting.blood_oxygen_min:
            abnormal_info["blood_oxygen_low"] = blood_oxygen
        
        if abnormal_info:
            # 创建异常预警
            alert_data = AlertCreate(
                alert_type=2,
                trigger_time=datetime.now(),
                abnormal_data=abnormal_info
            )
            return AlertService.create_alert(db, user_id, alert_data)
        
        return None

    @staticmethod
    def get_user_emergency_contacts(db: Session, user_id: str) -> List[EmergencyContact]:
        """获取用户紧急联系人"""
        return db.query(EmergencyContact).filter(
            EmergencyContact.user_id == user_id
        ).order_by(EmergencyContact.priority).all()
