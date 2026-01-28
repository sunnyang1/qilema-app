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
    def create_alert(db: Session, alert_data: AlertCreate) -> Alert:
        """创建预警"""
        # 检查是否已存在相同类型的活动预警
        existing_alert = db.query(Alert).filter(
            Alert.user_id == alert_data.user_id,
            Alert.alert_type == alert_data.alert_type,
            Alert.status == "active"
        ).first()

        if existing_alert:
            return existing_alert

        alert = Alert(
            alert_id=str(uuid.uuid4()),
            user_id=alert_data.user_id,
            alert_type=alert_data.alert_type,
            severity=alert_data.severity,
            trigger_time=alert_data.trigger_time,
            trigger_reason=alert_data.trigger_reason,
            status="active",
            abnormal_data=alert_data.abnormal_data,
            created_at=datetime.now()
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    @staticmethod
    def resolve_alert(db: Session, alert_id: Union[str, int], user_id: str, resolve_request: AlertResolveRequest) -> Optional[Alert]:
        """解决预警"""
        # 支持 id 和 alert_id 两种查找方式
        if isinstance(alert_id, int):
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
        else:
            alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()

        if not alert:
            return None

        alert.status = "resolved"
        alert.resolved_at = datetime.now()
        alert.resolved_reason = resolve_request.resolved_reason if resolve_request.resolved_reason else resolve_request.resolve_note
        alert.resolved_by = "manual_dismiss"
        db.commit()
        db.refresh(alert)
        return alert

    @staticmethod
    def auto_resolve_by_checkin(db: Session, user_id: str) -> int:
        """签到后自动解除所有活动预警"""
        setting = AlertService.get_setting(db, user_id)
        if not setting or not setting.auto_resolve:
            return 0

        # 查找所有活动预警
        active_alerts = db.query(Alert).filter(
            Alert.user_id == user_id,
            Alert.status == "active"
        ).all()

        # 自动解除所有活动预警
        count = 0
        for alert in active_alerts:
            alert.status = "resolved"
            alert.resolved_at = datetime.now()
            alert.resolved_reason = "用户已签到"
            alert.resolved_by = "auto_checkin"
            count += 1

        db.commit()
        return count

    @staticmethod
    def get_alerts(db: Session, user_id: str, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> tuple[List[Alert], int]:
        """获取用户预警列表"""
        query = db.query(Alert).filter(Alert.user_id == user_id)
        if status:
            query = query.filter(Alert.status == status)
        total = query.count()
        alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
        return alerts, total

    @staticmethod
    def get_alert_stats(db: Session, user_id: str) -> dict:
        """获取预警统计"""
        total = db.query(Alert).filter(Alert.user_id == user_id).count()
        active = db.query(Alert).filter(Alert.user_id == user_id, Alert.status == "active").count()
        resolved = db.query(Alert).filter(Alert.user_id == user_id, Alert.status == "resolved").count()
        dismissed = db.query(Alert).filter(Alert.user_id == user_id, Alert.status == "dismissed").count()

        return {
            'total_alerts': total,
            'active_alerts': active,
            'resolved_alerts': resolved,
            'dismissed_alerts': dismissed
        }

    @staticmethod
    def get_contacts_for_notification(db: Session, user_id: str) -> List[EmergencyContact]:
        """获取用于通知的紧急联系人"""
        setting = AlertService.get_setting(db, user_id)
        if setting and not setting.emergency_contact_notify:
            return []

        return AlertService.get_user_emergency_contacts(db, user_id)

    @staticmethod
    def check_all_users_and_create_alerts(db: Session) -> List[Alert]:
        """检查所有用户并创建预警"""
        created_alerts = []

        # 获取所有启用了预警的用户配置
        settings = db.query(AlertSetting).filter(
            AlertSetting.checkin_enabled == True,
            AlertSetting.enable_notification == True
        ).all()

        for setting in settings:
            # 检查签到状态
            status = AlertService.check_user_checkin_status(db, setting.user_id)
            if status and status['trigger_alert']:
                # 计算严重程度
                severity = AlertService._calculate_severity(int(status['missed_hours']))

                # 创建预警
                alert_data = AlertCreate(
                    user_id=setting.user_id,
                    alert_type="checkin_absent",
                    severity=severity,
                    trigger_reason=f"用户连续{int(status['missed_days'])}天未签到",
                    missed_days=int(status['missed_days']),
                    threshold_hours=status['threshold_hours']
                )
                alert = AlertService.create_alert(db, alert_data)
                if alert:
                    created_alerts.append(alert)

        return created_alerts

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

    @staticmethod
    def _calculate_severity(missed_hours: int) -> str:
        """计算严重程度"""
        if missed_hours >= 96:
            return 'critical'
        elif missed_hours >= 48:
            return 'high'
        elif missed_hours >= 30:
            return 'medium'
        else:
            return 'low'

    @staticmethod
    def check_user_checkin_status(db: Session, user_id: str) -> Optional[dict]:
        """检查用户签到状态"""
        setting = AlertService.get_setting(db, user_id)
        if not setting or not setting.checkin_enabled or not setting.enable_notification:
            return None

        # 获取最后签到时间
        last_checkin = db.query(CheckIn).filter(CheckIn.user_id == user_id).order_by(CheckIn.checkin_time.desc()).first()

        if not last_checkin:
            # 从未签到过
            return {
                'trigger_alert': True,
                'last_checkin_time': None,
                'missed_hours': 999,
                'missed_days': 999,
                'reason': '从未签到'
            }

        # 计算未签到时间
        now = datetime.now()
        time_since_last_checkin = now - last_checkin.checkin_time
        missed_hours = time_since_last_checkin.total_seconds() / 3600
        missed_days = missed_hours / 24

        # 检查是否超过阈值
        trigger_alert = missed_hours >= setting.checkin_threshold_hours

        return {
            'trigger_alert': trigger_alert,
            'last_checkin_time': last_checkin.checkin_time,
            'missed_hours': missed_hours,
            'missed_days': missed_days,
            'threshold_hours': setting.checkin_threshold_hours
        }
