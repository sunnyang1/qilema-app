"""
智能设备服务层

实现设备绑定、数据管理、状态监控、异常检测等核心业务逻辑
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
import json

from app.models.device import Device
from app.models.device_data import DeviceData, DeviceThreshold
from app.schemas.device import (
    DeviceBind, DeviceUpdate, DeviceDataUpload, DeviceDataQuery,
    DeviceThresholdCreate, DeviceThresholdUpdate, DeviceStatusUpdate, DeviceAlert
)
from app.models.user import User


class DeviceService:
    """智能设备服务类"""
    
    def __init__(self):
        """初始化设备服务"""
        self.alert_cooldown_cache = {}  # 预警冷却缓存
    
    # ========== 设备绑定管理 ==========
    
    def bind_device(self, db: Session, user_id: int, device_data: DeviceBind) -> Device:
        """绑定设备"""
        # 检查设备是否已被绑定
        existing_device = db.query(Device).filter(
            Device.device_id == device_data.device_id,
            Device.is_active == True
        ).first()
        
        if existing_device:
            if existing_device.user_id == user_id:
                raise ValueError("该设备已绑定到当前用户")
            else:
                raise ValueError("该设备已被其他用户绑定")
        
        # 创建设备记录
        device = Device(
            user_id=user_id,
            device_id=device_data.device_id,
            device_name=device_data.device_name,
            device_type=device_data.device_type,
            device_model=device_data.device_model,
            firmware_version=device_data.firmware_version,
            status="active",
            is_active=True
        )
        
        db.add(device)
        db.commit()
        db.refresh(device)
        
        # 创建默认阈值设置
        self._create_default_threshold(db, device.id)
        
        return device
    
    def unbind_device(self, db: Session, device_id: int, user_id: int) -> bool:
        """解绑设备"""
        device = db.query(Device).filter(
            Device.id == device_id,
            Device.user_id == user_id,
            Device.is_active == True
        ).first()
        
        if not device:
            raise ValueError("设备不存在或未绑定")
        
        # 标记为已解绑
        device.is_active = False
        device.unbound_at = datetime.utcnow()
        
        db.commit()
        return True
    
    def get_user_devices(self, db: Session, user_id: int, include_inactive: bool = False) -> List[Device]:
        """获取用户设备列表"""
        query = db.query(Device).filter(Device.user_id == user_id)
        
        if not include_inactive:
            query = query.filter(Device.is_active == True)
        
        devices = query.order_by(desc(Device.bound_at)).all()
        return devices
    
    def get_device(self, db: Session, device_id: int, user_id: int) -> Optional[Device]:
        """获取设备详情"""
        device = db.query(Device).filter(
            Device.id == device_id,
            Device.user_id == user_id
        ).first()
        return device
    
    def update_device(self, db: Session, device_id: int, user_id: int, device_data: DeviceUpdate) -> Device:
        """更新设备信息"""
        device = db.query(Device).filter(
            Device.id == device_id,
            Device.user_id == user_id
        ).first()
        
        if not device:
            raise ValueError("设备不存在")
        
        # 更新设备信息
        if device_data.device_name is not None:
            device.device_name = device_data.device_name
        if device_data.notes is not None:
            device.notes = device_data.notes
        
        device.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(device)
        
        return device
    
    # ========== 设备数据管理 ==========
    
    def upload_device_data(self, db: Session, user_id: int, data: DeviceDataUpload) -> DeviceData:
        """上传设备数据"""
        # 查找设备
        device = db.query(Device).filter(
            Device.device_id == data.device_id,
            Device.user_id == user_id,
            Device.is_active == True
        ).first()
        
        if not device:
            raise ValueError("设备不存在或未绑定")
        
        # 检查是否至少有一个数据字段
        has_data = any([
            data.heart_rate is not None,
            data.steps is not None,
            data.calories is not None,
            data.distance is not None,
            data.sleep_duration is not None,
            data.deep_sleep_duration is not None,
            data.systolic_pressure is not None,
            data.diastolic_pressure is not None,
            data.blood_oxygen is not None,
            data.body_temperature is not None
        ])
        
        if not has_data:
            raise ValueError("至少需要提供一个生理数据字段")
        
        # 创建数据记录
        device_data = DeviceData(
            device_id=device.id,
            heart_rate=data.heart_rate,
            steps=data.steps,
            calories=data.calories,
            distance=data.distance,
            sleep_duration=data.sleep_duration,
            deep_sleep_duration=data.deep_sleep_duration,
            systolic_pressure=data.systolic_pressure,
            diastolic_pressure=data.diastolic_pressure,
            blood_oxygen=data.blood_oxygen,
            body_temperature=data.body_temperature,
            data_timestamp=data.data_timestamp,
            raw_data=data.raw_data
        )
        
        db.add(device_data)
        
        # 更新设备最后同步时间
        device.last_sync_at = datetime.utcnow()
        device.is_online = True
        
        db.commit()
        db.refresh(device_data)
        
        # 检查异常并触发预警
        alerts = self._check_abnormal_data(db, device, device_data)
        if alerts:
            self._send_alerts(db, alerts)
        
        return device_data
    
    def get_device_data(self, db: Session, user_id: int, query_params: DeviceDataQuery) -> List[DeviceData]:
        """获取设备数据"""
        # 构建基础查询
        query = db.query(DeviceData).join(Device).filter(Device.user_id == user_id)
        
        # 设备过滤
        if query_params.device_id:
            device = db.query(Device).filter(
                Device.device_id == query_params.device_id,
                Device.user_id == user_id
            ).first()
            if device:
                query = query.filter(DeviceData.device_id == device.id)
        
        # 时间范围过滤
        if query_params.start_time:
            query = query.filter(DeviceData.data_timestamp >= query_params.start_time)
        if query_params.end_time:
            query = query.filter(DeviceData.data_timestamp <= query_params.end_time)
        
        # 数据类型过滤
        if query_params.data_type:
            data_field_map = {
                'heart_rate': DeviceData.heart_rate,
                'steps': DeviceData.steps,
                'calories': DeviceData.calories,
                'distance': DeviceData.distance,
                'sleep_duration': DeviceData.sleep_duration,
                'blood_oxygen': DeviceData.blood_oxygen,
                'body_temperature': DeviceData.body_temperature
            }
            if query_params.data_type in data_field_map:
                query = query.filter(data_field_map[query_params.data_type].isnot(None))
        
        # 排序和分页
        query = query.order_by(desc(DeviceData.data_timestamp))
        query = query.limit(query_params.limit).offset(query_params.offset)
        
        return query.all()
    
    def get_device_statistics(self, db: Session, device_id: int, data_type: str, 
                             start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """获取设备数据统计"""
        # 映射数据类型到字段
        data_field_map = {
            'heart_rate': DeviceData.heart_rate,
            'steps': DeviceData.steps,
            'calories': DeviceData.calories,
            'distance': DeviceData.distance,
            'sleep_duration': DeviceData.sleep_duration,
            'blood_oxygen': DeviceData.blood_oxygen,
            'body_temperature': DeviceData.body_temperature
        }
        
        if data_type not in data_field_map:
            raise ValueError(f"不支持的数据类型: {data_type}")
        
        data_field = data_field_map[data_type]
        
        # 获取设备
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            raise ValueError("设备不存在")
        
        # 构建统计查询
        query = db.query(
            func.count(data_field).label('count'),
            func.avg(data_field).label('avg_value'),
            func.min(data_field).label('min_value'),
            func.max(data_field).label('max_value')
        ).filter(
            DeviceData.device_id == device_id,
            DeviceData.data_timestamp >= start_time,
            DeviceData.data_timestamp <= end_time,
            data_field.isnot(None)
        )
        
        result = query.first()
        
        # 计算趋势(与前一时间段对比)
        trend = self._calculate_trend(db, device_id, data_field, start_time, end_time)
        
        return {
            'device_id': device_id,
            'device_name': device.device_name,
            'data_type': data_type,
            'start_time': start_time,
            'end_time': end_time,
            'count': int(result.count) if result.count else 0,
            'avg_value': float(result.avg_value) if result.avg_value else None,
            'min_value': float(result.min_value) if result.min_value else None,
            'max_value': float(result.max_value) if result.max_value else None,
            'trend': trend
        }
    
    # ========== 设备状态管理 ==========
    
    def update_device_status(self, db: Session, device_id: int, user_id: int, 
                            status_data: DeviceStatusUpdate) -> Device:
        """更新设备状态"""
        device = db.query(Device).filter(
            Device.id == device_id,
            Device.user_id == user_id
        ).first()
        
        if not device:
            raise ValueError("设备不存在")
        
        # 更新状态
        if status_data.is_online is not None:
            device.is_online = status_data.is_online
        if status_data.battery_level is not None:
            device.battery_level = status_data.battery_level
        
        device.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(device)
        
        return device
    
    def check_offline_devices(self, db: Session, offline_threshold_minutes: int = 60) -> List[Device]:
        """检查离线设备"""
        threshold_time = datetime.utcnow() - timedelta(minutes=offline_threshold_minutes)
        
        offline_devices = db.query(Device).filter(
            Device.is_active == True,
            Device.is_online == True,
            or_(
                Device.last_sync_at < threshold_time,
                Device.last_sync_at.is_(None)
            )
        ).all()
        
        # 标记为离线
        for device in offline_devices:
            device.is_online = False
            device.updated_at = datetime.utcnow()
        
        db.commit()
        return offline_devices
    
    # ========== 阈值管理 ==========
    
    def create_threshold(self, db: Session, threshold_data: DeviceThresholdCreate) -> DeviceThreshold:
        """创建设备阈值"""
        # 检查设备是否存在
        device = db.query(Device).filter(Device.id == threshold_data.device_id).first()
        if not device:
            raise ValueError("设备不存在")
        
        # 检查是否已存在阈值配置
        existing = db.query(DeviceThreshold).filter(
            DeviceThreshold.device_id == threshold_data.device_id
        ).first()
        
        if existing:
            raise ValueError("该设备已存在阈值配置")
        
        # 创建阈值
        threshold = DeviceThreshold(
            device_id=threshold_data.device_id,
            heart_rate_min=threshold_data.heart_rate_min,
            heart_rate_max=threshold_data.heart_rate_max,
            systolic_pressure_max=threshold_data.systolic_pressure_max,
            diastolic_pressure_max=threshold_data.diastolic_pressure_max,
            blood_oxygen_min=threshold_data.blood_oxygen_min,
            body_temperature_min=threshold_data.body_temperature_min,
            body_temperature_max=threshold_data.body_temperature_max,
            steps_min_per_day=threshold_data.steps_min_per_day,
            alert_enabled=threshold_data.alert_enabled,
            alert_cooldown_minutes=threshold_data.alert_cooldown_minutes
        )
        
        db.add(threshold)
        db.commit()
        db.refresh(threshold)
        
        return threshold
    
    def get_threshold(self, db: Session, device_id: int) -> Optional[DeviceThreshold]:
        """获取设备阈值"""
        threshold = db.query(DeviceThreshold).filter(
            DeviceThreshold.device_id == device_id
        ).first()
        return threshold
    
    def update_threshold(self, db: Session, device_id: int, 
                        threshold_data: DeviceThresholdUpdate) -> DeviceThreshold:
        """更新设备阈值"""
        threshold = db.query(DeviceThreshold).filter(
            DeviceThreshold.device_id == device_id
        ).first()
        
        if not threshold:
            raise ValueError("阈值配置不存在")
        
        # 更新字段
        update_fields = [
            'heart_rate_min', 'heart_rate_max', 'systolic_pressure_max',
            'diastolic_pressure_max', 'blood_oxygen_min', 'body_temperature_min',
            'body_temperature_max', 'steps_min_per_day', 'alert_enabled',
            'alert_cooldown_minutes'
        ]
        
        for field in update_fields:
            value = getattr(threshold_data, field, None)
            if value is not None:
                setattr(threshold, field, value)
        
        threshold.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(threshold)
        
        return threshold
    
    # ========== 异常检测 ==========
    
    def _check_abnormal_data(self, db: Session, device: Device, 
                            device_data: DeviceData) -> List[DeviceAlert]:
        """检查异常数据"""
        alerts = []
        
        # 获取阈值配置
        threshold = self.get_threshold(db, device.id)
        if not threshold or not threshold.alert_enabled:
            return alerts
        
        # 检查预警冷却
        cache_key = f"{device.id}_{device_data.data_timestamp.strftime('%Y%m%d%H%M')}"
        if cache_key in self.alert_cooldown_cache:
            return alerts
        
        # 心率异常检测
        if device_data.heart_rate:
            if device_data.heart_rate > threshold.heart_rate_max:
                alerts.append(DeviceAlert(
                    device_id=device.id,
                    device_name=device.device_name,
                    alert_type="heart_rate_high",
                    alert_message=f"心率过高预警: {device_data.heart_rate}次/分",
                    alert_value=device_data.heart_rate,
                    threshold_value=threshold.heart_rate_max
                ))
            elif device_data.heart_rate < threshold.heart_rate_min:
                alerts.append(DeviceAlert(
                    device_id=device.id,
                    device_name=device.device_name,
                    alert_type="heart_rate_low",
                    alert_message=f"心率过低预警: {device_data.heart_rate}次/分",
                    alert_value=device_data.heart_rate,
                    threshold_value=threshold.heart_rate_min
                ))
        
        # 血压异常检测
        if device_data.systolic_pressure and device_data.diastolic_pressure:
            if device_data.systolic_pressure > threshold.systolic_pressure_max:
                alerts.append(DeviceAlert(
                    device_id=device.id,
                    device_name=device.device_name,
                    alert_type="blood_pressure_high",
                    alert_message=f"收缩压过高预警: {device_data.systolic_pressure}mmHg",
                    alert_value=device_data.systolic_pressure,
                    threshold_value=threshold.systolic_pressure_max
                ))
            if device_data.diastolic_pressure > threshold.diastolic_pressure_max:
                alerts.append(DeviceAlert(
                    device_id=device.id,
                    device_name=device.device_name,
                    alert_type="blood_pressure_high",
                    alert_message=f"舒张压过高预警: {device_data.diastolic_pressure}mmHg",
                    alert_value=device_data.diastolic_pressure,
                    threshold_value=threshold.diastolic_pressure_max
                ))
        
        # 血氧异常检测
        if device_data.blood_oxygen:
            if device_data.blood_oxygen < threshold.blood_oxygen_min:
                alerts.append(DeviceAlert(
                    device_id=device.id,
                    device_name=device.device_name,
                    alert_type="blood_oxygen_low",
                    alert_message=f"血氧过低预警: {device_data.blood_oxygen}%",
                    alert_value=device_data.blood_oxygen,
                    threshold_value=threshold.blood_oxygen_min
                ))
        
        # 体温异常检测
        if device_data.body_temperature:
            if device_data.body_temperature > threshold.body_temperature_max:
                alerts.append(DeviceAlert(
                    device_id=device.id,
                    device_name=device.device_name,
                    alert_type="temperature_high",
                    alert_message=f"体温过高预警: {device_data.body_temperature}°C",
                    alert_value=device_data.body_temperature,
                    threshold_value=threshold.body_temperature_max
                ))
            elif device_data.body_temperature < threshold.body_temperature_min:
                alerts.append(DeviceAlert(
                    device_id=device.id,
                    device_name=device.device_name,
                    alert_type="temperature_low",
                    alert_message=f"体温过低预警: {device_data.body_temperature}°C",
                    alert_value=device_data.body_temperature,
                    threshold_value=threshold.body_temperature_min
                ))
        
        # 记录预警冷却
        if alerts:
            self.alert_cooldown_cache[cache_key] = True
        
        return alerts
    
    def _send_alerts(self, db: Session, alerts: List[DeviceAlert]) -> bool:
        """发送预警通知"""
        # 这里可以集成短信、推送、邮件等通知服务
        # 目前仅记录到日志
        for alert in alerts:
            print(f"[设备预警] {alert.alert_message} - 设备ID: {alert.device_id}")
        
        return True
    
    def _calculate_trend(self, db: Session, device_id: int, data_field,
                        current_start: datetime, current_end: datetime) -> str:
        """计算数据趋势"""
        # 当前时间段
        current_query = db.query(func.avg(data_field)).filter(
            DeviceData.device_id == device_id,
            DeviceData.data_timestamp >= current_start,
            DeviceData.data_timestamp <= current_end
        )
        current_avg = current_query.scalar()
        
        if current_avg is None:
            return "unknown"
        
        # 前一时间段(相同长度)
        time_diff = current_end - current_start
        prev_start = current_start - time_diff
        prev_end = current_start
        
        prev_query = db.query(func.avg(data_field)).filter(
            DeviceData.device_id == device_id,
            DeviceData.data_timestamp >= prev_start,
            DeviceData.data_timestamp <= prev_end
        )
        prev_avg = prev_query.scalar()
        
        if prev_avg is None:
            return "unknown"
        
        # 计算变化率
        change_rate = (current_avg - prev_avg) / prev_avg if prev_avg > 0 else 0
        
        if abs(change_rate) < 0.05:  # 变化小于5%
            return "stable"
        elif change_rate > 0:
            return "up"
        else:
            return "down"
    
    def _create_default_threshold(self, db: Session, device_id: int) -> DeviceThreshold:
        """创建默认阈值配置"""
        # 需要获取user_id，从device关联获取
        device = db.query(Device).filter(Device.id == device_id).first()
        user_id = device.user_id if device else None

        threshold = DeviceThreshold(
            device_id=device_id,
            user_id=user_id,
            heart_rate_min=60,
            heart_rate_max=100,
            blood_pressure_systolic_max=140,
            blood_pressure_diastolic_max=90,
            blood_oxygen_min=95,
            temperature_min=36.0,
            temperature_max=37.5,
            steps_min=1000,
            enabled=1
        )

        db.add(threshold)
        db.commit()
        db.refresh(threshold)

        return threshold