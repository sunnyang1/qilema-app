"""
设备数据异常监测服务

实现生理数据异常检测、健康趋势分析、活动模式分析等核心功能
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
import json
import statistics

from app.models.anomaly import (
    Anomaly, AnomalyTypeEnum, SeverityLevel, AnomalyStatus,
    HealthTrend, ActivityPattern
)
from app.models.device import Device, DeviceData
from app.models.user import User
from app.models.sos_request import SOSRequest
from app.schemas.anomaly import (
    AnomalyCreate, AnomalyUpdate, AnomalyQuery, AnomalyStatistics,
    TrendAnalysisRequest, HealthTrendResponse,
    ActivityAnalysisRequest, ActivityPatternResponse,
    AnomalyDetectionConfig, HeartHealthAnalysis
)
from app.services.sos_service import SOSService
from app.services.notification_service import NotificationService


class AnomalyService:
    """异常监测服务"""
    
    def __init__(self):
        self.sos_service = SOSService()
        self.notification_service = NotificationService()
    
    # ========== 异常检测核心逻辑 ==========
    
    def detect_heart_rate_anomaly(
        self, 
        db: Session, 
        device_data: DeviceData,
        config: Optional[AnomalyDetectionConfig] = None
    ) -> Optional[Anomaly]:
        """
        检测心率异常
        
        检测条件:
        - 心率过低: 低于最低阈值
        - 心率过高: 超过最高阈值
        - 心率骤停: 心率骤降为0且持续时间超过阈值
        - 心率骤变: 心率在短时间内突然大幅变化
        """
        if not device_data.heart_rate:
            return None
        
        anomalies = []
        
        # 获取设备阈值配置
        if config:
            hr_min = config.heart_rate_min
            hr_max = config.heart_rate_max
            sudden_change_threshold = config.heart_rate_sudden_change_threshold
        else:
            # 默认阈值
            hr_min = 50
            hr_max = 110
            sudden_change_threshold = 30
        
        current_hr = device_data.heart_rate
        
        # 1. 心率过低检测
        if current_hr < hr_min:
            anomaly = Anomaly(
                user_id=device_data.device.user_id,
                device_id=device_data.device.id,
                device_data_id=device_data.id,
                anomaly_type=AnomalyTypeEnum.HEART_RATE_LOW,
                severity=SeverityLevel.MEDIUM,
                status=AnomalyStatus.PENDING,
                anomaly_value=current_hr,
                threshold_value=hr_min,
                deviation_ratio=(hr_min - current_hr) / hr_min * 100 if hr_min else 0,
                description=f"心率过低: {current_hr} bpm (阈值: {hr_min} bpm)",
                trigger_condition=f"heart_rate < {hr_min}",
                metadata=json.dumps({"condition": "heart_rate_low"})
            )
            anomalies.append(anomaly)
        
        # 2. 心率过高检测
        elif current_hr > hr_max:
            severity = SeverityLevel.HIGH if current_hr > 130 else SeverityLevel.MEDIUM
            anomaly = Anomaly(
                user_id=device_data.device.user_id,
                device_id=device_data.device.id,
                device_data_id=device_data.id,
                anomaly_type=AnomalyTypeEnum.HEART_RATE_HIGH,
                severity=severity,
                status=AnomalyStatus.PENDING,
                anomaly_value=current_hr,
                threshold_value=hr_max,
                deviation_ratio=(current_hr - hr_max) / hr_max * 100 if hr_max else 0,
                description=f"心率过高: {current_hr} bpm (阈值: {hr_max} bpm)",
                trigger_condition=f"heart_rate > {hr_max}",
                metadata=json.dumps({"condition": "heart_rate_high"})
            )
            anomalies.append(anomaly)
        
        # 3. 心率骤停检测(心率突变为0)
        if current_hr == 0:
            # 检查最近的数据,确认是否为骤停
            recent_data = db.query(DeviceData).filter(
                DeviceData.device_id == device_data.device_id,
                DeviceData.data_timestamp >= device_data.data_timestamp - timedelta(minutes=5)
            ).order_by(desc(DeviceData.data_timestamp)).limit(2).all()
            
            if recent_data and all(d.heart_rate and d.heart_rate > 0 for d in recent_data):
                # 确认为骤停
                anomaly = Anomaly(
                    user_id=device_data.device.user_id,
                    device_id=device_data.device.id,
                    device_data_id=device_data.id,
                    anomaly_type=AnomalyTypeEnum.HEART_RATE_STOP,
                    severity=SeverityLevel.CRITICAL,
                    status=AnomalyStatus.PENDING,
                    anomaly_value=0,
                    threshold_value=1,
                    deviation_ratio=100.0,
                    description="检测到心跳骤停,需要立即救援",
                    trigger_condition="heart_rate == 0 (之前有正常心跳)",
                    metadata=json.dumps({"condition": "heart_rate_stop", "previous_hr": recent_data[0].heart_rate})
                )
                anomalies.append(anomaly)
        
        # 4. 心率骤变检测
        if sudden_change_threshold and len(anomalies) == 0:
            # 获取最近的心率数据
            recent_data = db.query(DeviceData).filter(
                DeviceData.device_id == device_data.device_id,
                DeviceData.data_timestamp >= device_data.data_timestamp - timedelta(minutes=5),
                DeviceData.heart_rate.isnot(None)
            ).order_by(desc(DeviceData.data_timestamp)).limit(2).all()
            
            if len(recent_data) >= 2:
                previous_hr = recent_data[1].heart_rate
                change_ratio = abs(current_hr - previous_hr) / previous_hr * 100 if previous_hr else 0
                
                if change_ratio >= sudden_change_threshold:
                    severity = SeverityLevel.HIGH if change_ratio > 50 else SeverityLevel.MEDIUM
                    anomaly = Anomaly(
                        user_id=device_data.device.user_id,
                        device_id=device_data.device.id,
                        device_data_id=device_data.id,
                        anomaly_type=AnomalyTypeEnum.HEART_RATE_SUDDEN_CHANGE,
                        severity=severity,
                        status=AnomalyStatus.PENDING,
                        anomaly_value=current_hr,
                        threshold_value=previous_hr,
                        deviation_ratio=change_ratio,
                        description=f"心率骤变: 从 {previous_hr} bpm 变为 {current_hr} bpm (变化: {change_ratio:.1f}%)",
                        trigger_condition=f"|heart_rate_change| >= {sudden_change_threshold}%",
                        metadata=json.dumps({
                            "condition": "heart_rate_sudden_change",
                            "previous_hr": previous_hr,
                            "change_ratio": change_ratio
                        })
                    )
                    anomalies.append(anomaly)
        
        # 保存异常并返回
        for anomaly in anomalies:
            db.add(anomaly)
        
        if anomalies:
            db.commit()
            # 触发危机异常的SOS
            for anomaly in anomalies:
                if anomaly.severity == SeverityLevel.CRITICAL:
                    self._trigger_critical_anomaly_alert(db, anomaly)
        
        return anomalies[0] if anomalies else None
    
    def detect_blood_pressure_anomaly(
        self,
        db: Session,
        device_data: DeviceData,
        config: Optional[AnomalyDetectionConfig] = None
    ) -> Optional[Anomaly]:
        """
        检测血压异常
        
        检测收缩压和舒张压是否超出正常范围
        """
        if not device_data.systolic or not device_data.diastolic:
            return None
        
        # 默认阈值
        if config:
            sys_min = config.systolic_min or 90
            sys_max = config.systolic_max or 140
            dia_min = config.diastolic_min or 60
            dia_max = config.diastolic_max or 90
        else:
            sys_min, sys_max = 90, 140
            dia_min, dia_max = 60, 90
        
        systolic = device_data.systolic
        diastolic = device_data.diastolic
        
        # 检测收缩压异常
        if systolic < sys_min:
            anomaly = Anomaly(
                user_id=device_data.device.user_id,
                device_id=device_data.device.id,
                device_data_id=device_data.id,
                anomaly_type=AnomalyTypeEnum.BLOOD_PRESSURE_LOW,
                severity=SeverityLevel.MEDIUM,
                status=AnomalyStatus.PENDING,
                anomaly_value=float(systolic),
                threshold_value=float(sys_min),
                description=f"收缩压过低: {systolic} mmHg (阈值: {sys_min} mmHg)",
                trigger_condition=f"systolic < {sys_min}"
            )
            db.add(anomaly)
            db.commit()
            return anomaly
        
        elif systolic > sys_max:
            severity = SeverityLevel.HIGH if systolic > 160 else SeverityLevel.MEDIUM
            anomaly = Anomaly(
                user_id=device_data.device.user_id,
                device_id=device_data.device.id,
                device_data_id=device_data.id,
                anomaly_type=AnomalyTypeEnum.BLOOD_PRESSURE_HIGH,
                severity=severity,
                status=AnomalyStatus.PENDING,
                anomaly_value=float(systolic),
                threshold_value=float(sys_max),
                description=f"收缩压过高: {systolic} mmHg (阈值: {sys_max} mmHg)",
                trigger_condition=f"systolic > {sys_max}"
            )
            db.add(anomaly)
            db.commit()
            return anomaly
        
        # 检测舒张压异常
        if diastolic < dia_min or diastolic > dia_max:
            condition = f"diastolic < {dia_min}" if diastolic < dia_min else f"diastolic > {dia_max}"
            anomaly = Anomaly(
                user_id=device_data.device.user_id,
                device_id=device_data.device.id,
                device_data_id=device_data.id,
                anomaly_type=AnomalyTypeEnum.BLOOD_PRESSURE_HIGH if diastolic > dia_max else AnomalyTypeEnum.BLOOD_PRESSURE_LOW,
                severity=SeverityLevel.MEDIUM,
                status=AnomalyStatus.PENDING,
                anomaly_value=float(diastolic),
                threshold_value=float(dia_max if diastolic > dia_max else dia_min),
                description=f"舒张压异常: {diastolic} mmHg (正常范围: {dia_min}-{dia_max} mmHg)",
                trigger_condition=condition
            )
            db.add(anomaly)
            db.commit()
            return anomaly
        
        return None
    
    def detect_no_activity_anomaly(
        self,
        db: Session,
        user_id: str,
        device_id: int,
        config: Optional[AnomalyDetectionConfig] = None
    ) -> Optional[Anomaly]:
        """
        检测连续无活动异常
        
        检测用户在设定时间内没有任何活动数据
        """
        threshold_hours = config.no_activity_threshold if config else 12
        
        # 检查最近的活动数据
        cutoff_time = datetime.utcnow() - timedelta(hours=threshold_hours)
        recent_data = db.query(DeviceData).filter(
            DeviceData.device_id == device_id,
            DeviceData.data_timestamp >= cutoff_time,
            or_(
                DeviceData.steps.isnot(None),
                DeviceData.calories.isnot(None),
                DeviceData.distance.isnot(None)
            )
        ).first()
        
        if not recent_data:
            # 确认设备存在
            device = db.query(Device).filter(Device.id == device_id).first()
            if not device:
                return None
            
            anomaly = Anomaly(
                user_id=user_id,
                device_id=device_id,
                anomaly_type=AnomalyTypeEnum.NO_ACTIVITY,
                severity=SeverityLevel.MEDIUM,
                status=AnomalyStatus.PENDING,
                threshold_value=float(threshold_hours),
                description=f"连续{threshold_hours}小时无活动记录,请确认用户安全状态",
                trigger_condition=f"no_activity_hours >= {threshold_hours}",
                metadata=json.dumps({
                    "condition": "no_activity",
                    "threshold_hours": threshold_hours,
                    "last_activity_time": device.last_sync_at.isoformat() if device.last_sync_at else None
                })
            )
            db.add(anomaly)
            db.commit()
            return anomaly
        
        return None
    
    def analyze_health_trend(
        self,
        db: Session,
        request: TrendAnalysisRequest
    ) -> Optional[HealthTrendResponse]:
        """
        分析健康数据趋势
        
        计算指定时间段内某项指标的平均值、最大值、最小值、标准差和变化趋势
        """
        # 确定时间范围
        if not request.start_date:
            start_date = datetime.utcnow() - timedelta(days=7)
        else:
            start_date = request.start_date
        
        if not request.end_date:
            end_date = datetime.utcnow()
        else:
            end_date = request.end_date
        
        # 构建查询条件
        query_conditions = [
            DeviceData.data_timestamp >= start_date,
            DeviceData.data_timestamp <= end_date
        ]
        
        if request.device_id:
            query_conditions.append(DeviceData.device_id == request.device_id)
        
        # 根据指标类型选择数据字段
        metric_field = self._get_metric_field(request.metric_type)
        if not metric_field:
            raise ValueError(f"不支持的指标类型: {request.metric_type}")
        
        query_conditions.append(metric_field.isnot(None))
        
        # 查询数据
        device_data = db.query(DeviceData).join(Device).filter(
            Device.user_id == request.user_id,
            *query_conditions
        ).order_by(DeviceData.data_timestamp).all()
        
        if not device_data:
            return None
        
        # 提取数值
        values = [getattr(d, metric_field.name) for d in device_data if getattr(d, metric_field.name) is not None]
        
        if not values:
            return None
        
        # 计算统计数据
        avg_value = statistics.mean(values)
        min_value = min(values)
        max_value = max(values)
        
        std_deviation = statistics.stdev(values) if len(values) > 1 else 0
        
        # 分析趋势
        if len(values) >= 2:
            first_value = values[0]
            last_value = values[-1]
            trend_percentage = ((last_value - first_value) / first_value * 100) if first_value != 0 else 0
            
            if abs(trend_percentage) < 5:
                trend_direction = "stable"
            elif trend_percentage > 0:
                trend_direction = "up"
            else:
                trend_direction = "down"
        else:
            trend_direction = None
            trend_percentage = None
        
        # 创建或更新趋势记录
        existing_trend = db.query(HealthTrend).filter(
            HealthTrend.user_id == request.user_id,
            HealthTrend.metric_type == request.metric_type,
            HealthTrend.period_type == request.period_type,
            HealthTrend.start_date == start_date,
            HealthTrend.end_date == end_date
        ).first()
        
        if existing_trend:
            existing_trend.avg_value = avg_value
            existing_trend.min_value = min_value
            existing_trend.max_value = max_value
            existing_trend.std_deviation = std_deviation
            existing_trend.trend_direction = trend_direction
            existing_trend.trend_percentage = trend_percentage
            existing_trend.sample_count = len(values)
            existing_trend.quality_score = self._calculate_quality_score(len(values), len(device_data))
            trend = existing_trend
        else:
            trend = HealthTrend(
                user_id=request.user_id,
                device_id=request.device_id,
                metric_type=request.metric_type,
                period_type=request.period_type,
                start_date=start_date,
                end_date=end_date,
                avg_value=avg_value,
                min_value=min_value,
                max_value=max_value,
                std_deviation=std_deviation,
                trend_direction=trend_direction,
                trend_percentage=trend_percentage,
                sample_count=len(values),
                missing_count=len(device_data) - len(values),
                quality_score=self._calculate_quality_score(len(values), len(device_data))
            )
            db.add(trend)
        
        db.commit()
        return HealthTrendResponse.from_orm(trend)
    
    # ========== 异常记录管理 ==========
    
    def create_anomaly(self, db: Session, anomaly_data: AnomalyCreate) -> Anomaly:
        """创建异常记录"""
        anomaly = Anomaly(**anomaly_data.dict())
        db.add(anomaly)
        db.commit()
        db.refresh(anomaly)
        return anomaly
    
    def get_anomalies(self, db: Session, query_params: AnomalyQuery) -> List[Anomaly]:
        """查询异常记录"""
        query = db.query(Anomaly).filter(Anomaly.user_id == query_params.user_id)
        
        if query_params.anomaly_type:
            query = query.filter(Anomaly.anomaly_type == query_params.anomaly_type)
        
        if query_params.severity:
            query = query.filter(Anomaly.severity == query_params.severity)
        
        if query_params.status:
            query = query.filter(Anomaly.status == query_params.status)
        
        if query_params.start_date:
            query = query.filter(Anomaly.detected_at >= query_params.start_date)
        
        if query_params.end_date:
            query = query.filter(Anomaly.detected_at <= query_params.end_date)
        
        if query_params.device_id:
            query = query.filter(Anomaly.device_id == query_params.device_id)
        
        return query.order_by(desc(Anomaly.detected_at)).offset(query_params.offset).limit(query_params.limit).all()
    
    def update_anomaly(self, db: Session, anomaly_id: int, update_data: AnomalyUpdate) -> Optional[Anomaly]:
        """更新异常记录"""
        anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
        if not anomaly:
            return None
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(anomaly, field, value)
        
        db.commit()
        db.refresh(anomaly)
        return anomaly
    
    def get_anomaly_statistics(self, db: Session, user_id: str, start_date: datetime, end_date: datetime) -> AnomalyStatistics:
        """获取异常统计数据"""
        anomalies = db.query(Anomaly).filter(
            Anomaly.user_id == user_id,
            Anomaly.detected_at >= start_date,
            Anomaly.detected_at <= end_date
        ).all()
        
        # 按严重程度统计
        critical_count = sum(1 for a in anomalies if a.severity == SeverityLevel.CRITICAL)
        high_count = sum(1 for a in anomalies if a.severity == SeverityLevel.HIGH)
        medium_count = sum(1 for a in anomalies if a.severity == SeverityLevel.MEDIUM)
        low_count = sum(1 for a in anomalies if a.severity == SeverityLevel.LOW)
        
        # 按类型统计
        type_breakdown = {}
        for anomaly in anomalies:
            type_name = anomaly.anomaly_type.value
            type_breakdown[type_name] = type_breakdown.get(type_name, 0) + 1
        
        # 按状态统计
        resolved_count = sum(1 for a in anomalies if a.status == AnomalyStatus.RESOLVED)
        pending_count = sum(1 for a in anomalies if a.status == AnomalyStatus.PENDING)
        
        # 最常见的异常类型
        most_common_type = max(type_breakdown, key=type_breakdown.get) if type_breakdown else None
        
        return AnomalyStatistics(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            total_anomalies=len(anomalies),
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
            low_count=low_count,
            anomaly_type_breakdown=type_breakdown,
            resolved_count=resolved_count,
            pending_count=pending_count,
            most_common_type=most_common_type
        )
    
    # ========== 心脏健康分析 ==========
    
    def analyze_heart_health(self, db: Session, user_id: str, device_id: Optional[int] = None) -> HeartHealthAnalysis:
        """
        心脏健康分析
        
        基于心率数据进行心脏健康评估,包括静息心率、心率变异性、心律不齐检测等
        """
        # 获取最近7天的心率数据
        cutoff_time = datetime.utcnow() - timedelta(days=7)
        
        query = db.query(DeviceData).join(Device).filter(
            Device.user_id == user_id,
            DeviceData.data_timestamp >= cutoff_time,
            DeviceData.heart_rate.isnot(None)
        )
        
        if device_id:
            query = query.filter(DeviceData.id == device_id)
        
        device_data = query.order_by(DeviceData.data_timestamp).all()
        
        if not device_data:
            raise ValueError("没有找到心率数据")
        
        # 提取心率值
        heart_rates = [d.heart_rate for d in device_data if d.heart_rate is not None]
        
        if not heart_rates:
            raise ValueError("心率数据为空")
        
        # 基础统计
        avg_heart_rate = statistics.mean(heart_rates)
        max_heart_rate = max(heart_rates)
        min_heart_rate = min(heart_rates)
        
        # 估算静息心率(取凌晨2-4点的心率平均值)
        nighttime_rates = [
            d.heart_rate for d in device_data
            if d.heart_rate and 2 <= d.data_timestamp.hour < 4
        ]
        resting_heart_rate = statistics.mean(nighttime_rates) if nighttime_rates else None
        
        # 心率变异性(简化版:连续心跳间隔的标准差)
        hrv_value = statistics.stdev(heart_rates) if len(heart_rates) > 1 else None
        
        if hrv_value:
            if hrv_value > 50:
                hrv_status = "excellent"
            elif hrv_value > 30:
                hrv_status = "good"
            elif hrv_value > 20:
                hrv_status = "fair"
            else:
                hrv_status = "poor"
        else:
            hrv_status = None
        
        # 心律不齐检测(心率波动异常)
        if len(heart_rates) > 10:
            # 计算心率连续差分
            hr_diffs = [abs(heart_rates[i+1] - heart_rates[i]) for i in range(len(heart_rates)-1)]
            irregular_count = sum(1 for diff in hr_diffs if diff > 15)
            irregular_rhythm_detected = irregular_count > len(hr_diffs) * 0.2
        else:
            irregular_count = 0
            irregular_rhythm_detected = False
        
        # 心血管风险评估
        risk_factors = []
        if avg_heart_rate > 90:
            risk_factors.append("静息心率偏高")
        if min_heart_rate < 45:
            risk_factors.append("心率偏低")
        if irregular_rhythm_detected:
            risk_factors.append("心律不齐")
        if hrv_status == "poor":
            risk_factors.append("心率变异性低")
        
        if len(risk_factors) >= 3:
            cardiovascular_risk = "high"
        elif len(risk_factors) >= 2:
            cardiovascular_risk = "medium"
        elif len(risk_factors) >= 1:
            cardiovascular_risk = "low"
        else:
            cardiovascular_risk = "very_low"
        
        # 健康建议
        recommendations = []
        if avg_heart_rate > 90:
            recommendations.append("建议进行适度有氧运动降低静息心率")
        if irregular_rhythm_detected:
            recommendations.append("建议定期监测心率,必要时咨询医生")
        if hrv_status == "poor":
            recommendations.append("建议改善睡眠质量,增加运动")
        if resting_heart_rate and resting_heart_rate < 50:
            recommendations.append("如无其他不适,低静息心率可能表示心脏功能良好")
        
        return HeartHealthAnalysis(
            user_id=user_id,
            analysis_date=datetime.utcnow(),
            avg_heart_rate=round(avg_heart_rate, 1),
            resting_heart_rate=round(resting_heart_rate, 1) if resting_heart_rate else None,
            max_heart_rate=max_heart_rate,
            min_heart_rate=min_heart_rate,
            hrv_value=round(hrv_value, 1) if hrv_value else None,
            hrv_status=hrv_status,
            irregular_rhythm_detected=irregular_rhythm_detected,
            irregular_rhythm_count=irregular_count,
            cardiovascular_risk=cardiovascular_risk,
            risk_factors=risk_factors,
            health_recommendations=recommendations
        )
    
    # ========== 辅助方法 ==========
    
    def _trigger_critical_anomaly_alert(self, db: Session, anomaly: Anomaly):
        """触发危急异常警报"""
        # 发送通知
        self.notification_service.send_critical_anomaly_alert(
            db,
            anomaly.user_id,
            anomaly.anomaly_type.value,
            anomaly.description
        )
        
        # 自动触发SOS
        if anomaly.anomaly_type in [AnomalyTypeEnum.HEART_RATE_STOP, AnomalyTypeEnum.FALL_DETECTED]:
            sos_request = self.sos_service.create_sos_request(
                db,
                anomaly.user_id,
                f"系统自动触发: {anomaly.description}",
                auto_triggered=True
            )
            anomaly.sos_triggered = sos_request.id
            anomaly.action_taken = f"自动触发SOS #{sos_request.id}"
            db.commit()
    
    def _get_metric_field(self, metric_type: str):
        """根据指标类型获取数据库字段"""
        from sqlalchemy import case
        
        field_mapping = {
            "heart_rate": DeviceData.heart_rate,
            "steps": DeviceData.steps,
            "calories": DeviceData.calories,
            "distance": DeviceData.distance,
            "sleep_hours": DeviceData.sleep_hours,
            "blood_pressure_systolic": DeviceData.systolic,
            "blood_pressure_diastolic": DeviceData.diastolic,
            "blood_oxygen": DeviceData.blood_oxygen,
            "body_temperature": DeviceData.temperature
        }
        
        return field_mapping.get(metric_type)
    
    def _calculate_quality_score(self, valid_count: int, total_count: int) -> float:
        """计算数据质量分数"""
        if total_count == 0:
            return 0.0
        
        ratio = valid_count / total_count
        return round(ratio * 100, 2)