"""
设备数据异常监测服务

实现生理数据异常检测、健康趋势分析、活动模式分析等核心功能
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from app.models.anomaly import (
    Anomaly,
    AnomalyStatus,
    AnomalyTypeEnum,
    HealthTrend,
    SeverityLevel,
)
from app.models.device import Device
from app.models.device_data import DeviceData
from app.schemas.anomaly import (
    AnomalyCreate,
    AnomalyDetectionConfig,
    AnomalyQuery,
    AnomalyStatistics,
    AnomalyUpdate,
    HealthTrendResponse,
    HeartHealthAnalysis,
    TrendAnalysisRequest,
)
from app.services.notification_service import NotificationService
from app.services.sos_service import SOSService
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session


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
        config: Optional[AnomalyDetectionConfig] = None,
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

        # 获取设备阈值配置
        hr_min, hr_max, sudden_change_threshold = self._get_heart_rate_thresholds(
            config
        )

        anomalies = []
        current_hr = device_data.heart_rate

        # 检测各种心率异常
        anomalies.extend(self._check_heart_rate_low(device_data, current_hr, hr_min))
        anomalies.extend(self._check_heart_rate_high(device_data, current_hr, hr_max))
        anomalies.extend(self._check_heart_rate_stop(db, device_data, current_hr))
        anomalies.extend(
            self._check_heart_rate_sudden_change(
                db, device_data, current_hr, sudden_change_threshold, anomalies
            )
        )

        # 保存异常并返回第一个
        return self._save_and_trigger_alerts(db, anomalies)

    def _get_heart_rate_thresholds(
        self, config: Optional[AnomalyDetectionConfig]
    ) -> tuple:
        """获取心率阈值配置

        Returns:
            tuple: (hr_min, hr_max, sudden_change_threshold)
        """
        if config:
            return (
                config.heart_rate_min,
                config.heart_rate_max,
                config.heart_rate_sudden_change_threshold,
            )
        else:
            # 默认阈值
            return (50, 110, 30)

    def _check_heart_rate_low(
        self, device_data: DeviceData, current_hr: float, hr_min: float
    ) -> list:
        """检测心率过低异常"""
        if current_hr >= hr_min:
            return []

        return [
            Anomaly(
                user_id=device_data.device.user_id,
                device_id=device_data.device.device_id,
                device_data_id=device_data.id,
                anomaly_type=AnomalyTypeEnum.HEART_RATE_LOW,
                severity=SeverityLevel.MEDIUM,
                status=AnomalyStatus.PENDING,
                anomaly_value=current_hr,
                threshold_value=hr_min,
                deviation_ratio=(hr_min - current_hr) / hr_min * 100 if hr_min else 0,
                description=f"心率过低: {current_hr} bpm (阈值: {hr_min} bpm)",
                trigger_condition=f"heart_rate < {hr_min}",
                metadata=json.dumps({"condition": "heart_rate_low"}),
            )
        ]

    def _check_heart_rate_high(
        self, device_data: DeviceData, current_hr: float, hr_max: float
    ) -> list:
        """检测心率过高异常"""
        if current_hr <= hr_max:
            return []

        severity = SeverityLevel.HIGH if current_hr > 130 else SeverityLevel.MEDIUM
        return [
            Anomaly(
                user_id=device_data.device.user_id,
                device_id=device_data.device.device_id,
                device_data_id=device_data.id,
                anomaly_type=AnomalyTypeEnum.HEART_RATE_HIGH,
                severity=severity,
                status=AnomalyStatus.PENDING,
                anomaly_value=current_hr,
                threshold_value=hr_max,
                deviation_ratio=(current_hr - hr_max) / hr_max * 100 if hr_max else 0,
                description=f"心率过高: {current_hr} bpm (阈值: {hr_max} bpm)",
                trigger_condition=f"heart_rate > {hr_max}",
                metadata=json.dumps({"condition": "heart_rate_high"}),
            )
        ]

    def _check_heart_rate_stop(
        self, db: Session, device_data: DeviceData, current_hr: float
    ) -> list:
        """检测心率骤停异常"""
        if current_hr != 0:
            return []

        # 检查最近的数据,确认是否为骤停
        recent_data = (
            db.query(DeviceData)
            .filter(
                DeviceData.device_id == device_data.device_id,
                DeviceData.data_timestamp
                >= device_data.data_timestamp - timedelta(minutes=5),
            )
            .order_by(desc(DeviceData.data_timestamp))
            .limit(2)
            .all()
        )

        if not recent_data or not all(
            d.heart_rate and d.heart_rate > 0 for d in recent_data
        ):
            return []

        return [
            Anomaly(
                user_id=device_data.device.user_id,
                device_id=device_data.device.device_id,
                device_data_id=device_data.id,
                anomaly_type=AnomalyTypeEnum.HEART_RATE_STOP,
                severity=SeverityLevel.CRITICAL,
                status=AnomalyStatus.PENDING,
                anomaly_value=0,
                threshold_value=1,
                deviation_ratio=100.0,
                description="检测到心跳骤停,需要立即救援",
                trigger_condition="heart_rate == 0 (之前有正常心跳)",
                metadata=json.dumps(
                    {
                        "condition": "heart_rate_stop",
                        "previous_hr": recent_data[0].heart_rate,
                    }
                ),
            )
        ]

    def _check_heart_rate_sudden_change(
        self,
        db: Session,
        device_data: DeviceData,
        current_hr: float,
        threshold: float,
        existing_anomalies: list,
    ) -> list:
        """检测心率骤变异常"""
        if not threshold or existing_anomalies or current_hr == 0:
            return []

        # 获取最近的心率数据
        recent_data = (
            db.query(DeviceData)
            .filter(
                DeviceData.device_id == device_data.device_id,
                DeviceData.data_timestamp
                >= device_data.data_timestamp - timedelta(minutes=5),
                DeviceData.heart_rate.isnot(None),
            )
            .order_by(desc(DeviceData.data_timestamp))
            .limit(2)
            .all()
        )

        if len(recent_data) < 2:
            return []

        previous_hr = recent_data[1].heart_rate
        change_ratio = (
            abs(current_hr - previous_hr) / previous_hr * 100 if previous_hr else 0
        )

        if change_ratio < threshold:
            return []

        severity = SeverityLevel.HIGH if change_ratio > 50 else SeverityLevel.MEDIUM
        return [
            Anomaly(
                user_id=device_data.device.user_id,
                device_id=device_data.device.device_id,
                device_data_id=device_data.id,
                anomaly_type=AnomalyTypeEnum.HEART_RATE_SUDDEN_CHANGE,
                severity=severity,
                status=AnomalyStatus.PENDING,
                anomaly_value=current_hr,
                threshold_value=previous_hr,
                deviation_ratio=change_ratio,
                description=f"心率骤变: 从 {previous_hr} bpm 变为 {current_hr} bpm (变化: {change_ratio:.1f}%)",
                trigger_condition=f"|heart_rate_change| >= {threshold}%",
                metadata=json.dumps(
                    {
                        "condition": "heart_rate_sudden_change",
                        "previous_hr": previous_hr,
                        "change_ratio": change_ratio,
                    }
                ),
            )
        ]

    def _save_and_trigger_alerts(
        self, db: Session, anomalies: list
    ) -> Optional[Anomaly]:
        """保存异常并触发危急警报"""
        if not anomalies:
            return None

        # 保存所有异常
        for anomaly in anomalies:
            db.add(anomaly)

        db.commit()

        # 触发危机异常的SOS
        for anomaly in anomalies:
            if anomaly.severity == SeverityLevel.CRITICAL:
                self._trigger_critical_anomaly_alert(db, anomaly)

        return anomalies[0]

    def detect_blood_pressure_anomaly(
        self,
        db: Session,
        device_data: DeviceData,
        config: Optional[AnomalyDetectionConfig] = None,
    ) -> Optional[Anomaly]:
        """
        检测血压异常

        检测收缩压和舒张压是否超出正常范围
        """
        if not device_data.systolic or not device_data.diastolic:
            return None

        thresholds = self._get_bp_thresholds(config)

        if anomaly := self._check_systolic_anomaly(device_data, thresholds):
            return self._save_anomaly(db, anomaly)

        if anomaly := self._check_diastolic_anomaly(device_data, thresholds):
            return self._save_anomaly(db, anomaly)

        return None

    def _get_bp_thresholds(self, config: Optional[AnomalyDetectionConfig]) -> Dict:
        """获取血压阈值"""
        if config:
            return {
                "sys_min": config.systolic_min or 90,
                "sys_max": config.systolic_max or 140,
                "dia_min": config.diastolic_min or 60,
                "dia_max": config.diastolic_max or 90,
            }
        else:
            return {"sys_min": 90, "sys_max": 140, "dia_min": 60, "dia_max": 90}

    def _check_systolic_anomaly(
        self, device_data: DeviceData, thresholds: Dict
    ) -> Optional[Anomaly]:
        """检测收缩压异常"""
        systolic = device_data.systolic
        sys_min = thresholds["sys_min"]
        sys_max = thresholds["sys_max"]

        if systolic < sys_min:
            return self._create_bp_anomaly(
                device_data,
                AnomalyTypeEnum.BLOOD_PRESSURE_LOW,
                SeverityLevel.MEDIUM,
                systolic,
                sys_min,
                "收缩压过低",
            )
        elif systolic > sys_max:
            severity = SeverityLevel.HIGH if systolic > 160 else SeverityLevel.MEDIUM
            return self._create_bp_anomaly(
                device_data,
                AnomalyTypeEnum.BLOOD_PRESSURE_HIGH,
                severity,
                systolic,
                sys_max,
                "收缩压过高",
            )

        return None

    def _check_diastolic_anomaly(
        self, device_data: DeviceData, thresholds: Dict
    ) -> Optional[Anomaly]:
        """检测舒张压异常"""
        diastolic = device_data.diastolic
        dia_min = thresholds["dia_min"]
        dia_max = thresholds["dia_max"]

        if diastolic < dia_min:
            return self._create_bp_anomaly(
                device_data,
                AnomalyTypeEnum.BLOOD_PRESSURE_LOW,
                SeverityLevel.MEDIUM,
                diastolic,
                dia_min,
                "舒张压过低",
            )
        elif diastolic > dia_max:
            return self._create_bp_anomaly(
                device_data,
                AnomalyTypeEnum.BLOOD_PRESSURE_HIGH,
                SeverityLevel.MEDIUM,
                diastolic,
                dia_max,
                "舒张压过高",
            )

        return None

    def _create_bp_anomaly(
        self,
        device_data: DeviceData,
        anomaly_type: AnomalyTypeEnum,
        severity: SeverityLevel,
        value: float,
        threshold: float,
        description_prefix: str,
    ) -> Anomaly:
        """创建血压异常对象"""
        threshold_name = "收缩压" if "收缩" in description_prefix else "舒张压"
        condition_operator = "<" if "低" in description_prefix else ">"

        return Anomaly(
            user_id=device_data.device.user_id,
            device_id=device_data.device.device_id,
            device_data_id=device_data.id,
            anomaly_type=anomaly_type,
            severity=severity,
            status=AnomalyStatus.PENDING,
            anomaly_value=float(value),
            threshold_value=float(threshold),
            description=f"{description_prefix}: {value} mmHg (阈值: {threshold} mmHg)",
            trigger_condition=f"{threshold_name} {condition_operator} {threshold}",
        )

    def _save_anomaly(self, db: Session, anomaly: Anomaly) -> Anomaly:
        """保存异常记录"""
        db.add(anomaly)
        db.commit()
        return anomaly

    def detect_no_activity_anomaly(
        self,
        db: Session,
        user_id: str,
        device_id: int,
        config: Optional[AnomalyDetectionConfig] = None,
    ) -> Optional[Anomaly]:
        """
        检测连续无活动异常

        检测用户在设定时间内没有任何活动数据
        """
        threshold_hours = config.no_activity_threshold if config else 12

        # 检查最近的活动数据
        cutoff_time = datetime.utcnow() - timedelta(hours=threshold_hours)
        recent_data = (
            db.query(DeviceData)
            .filter(
                DeviceData.device_id == device_id,
                DeviceData.data_timestamp >= cutoff_time,
                or_(
                    DeviceData.steps.isnot(None),
                    DeviceData.calories.isnot(None),
                    DeviceData.distance.isnot(None),
                ),
            )
            .first()
        )

        if not recent_data:
            # 确认设备存在
            device = db.query(Device).filter(Device.device_id == device_id).first()
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
                metadata=json.dumps(
                    {
                        "condition": "no_activity",
                        "threshold_hours": threshold_hours,
                        "last_activity_time": (
                            device.last_sync_at.isoformat()
                            if device.last_sync_at
                            else None
                        ),
                    }
                ),
            )
            db.add(anomaly)
            db.commit()
            return anomaly

        return None

    def analyze_health_trend(
        self, db: Session, request: TrendAnalysisRequest
    ) -> Optional[HealthTrendResponse]:
        """
        分析健康数据趋势

        计算指定时间段内某项指标的平均值、最大值、最小值、标准差和变化趋势
        """
        date_range = self._determine_date_range(request.start_date, request.end_date)
        metric_field = self._validate_metric_field(request.metric_type)
        device_data = self._query_device_data(db, request, date_range, metric_field)

        if not device_data:
            return None

        values = self._extract_values(device_data, metric_field)
        if not values:
            return None

        statistics_data = self._calculate_statistics(values)
        trend = self._analyze_trend(values)
        trend_record = self._save_or_update_trend(
            db,
            request,
            date_range,
            statistics_data,
            trend,
            len(device_data),
            len(values),
        )

        return HealthTrendResponse.from_orm(trend_record)

    def _determine_date_range(
        self, start_date: Optional[datetime], end_date: Optional[datetime]
    ) -> Tuple[datetime, datetime]:
        """确定时间范围"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=7)
        if not end_date:
            end_date = datetime.utcnow()
        return (start_date, end_date)

    def _validate_metric_field(self, metric_type: str):
        """验证指标类型并返回对应的数据库字段"""
        metric_field = self._get_metric_field(metric_type)
        if not metric_field:
            raise ValueError(f"不支持的指标类型: {metric_type}")
        return metric_field

    def _query_device_data(
        self,
        db: Session,
        request: TrendAnalysisRequest,
        date_range: Tuple[datetime, datetime],
        metric_field,
    ) -> List[DeviceData]:
        """查询设备数据"""
        start_date, end_date = date_range

        query_conditions = [
            DeviceData.data_timestamp >= start_date,
            DeviceData.data_timestamp <= end_date,
            metric_field.isnot(None),
        ]

        if request.device_id:
            query_conditions.append(DeviceData.device_id == request.device_id)

        return (
            db.query(DeviceData)
            .join(Device)
            .filter(Device.user_id == request.user_id, *query_conditions)
            .order_by(DeviceData.data_timestamp)
            .all()
        )

    def _extract_values(
        self, device_data: List[DeviceData], metric_field
    ) -> List[float]:
        """从设备数据中提取数值"""
        return [
            getattr(d, metric_field.name)
            for d in device_data
            if getattr(d, metric_field.name) is not None
        ]

    def _calculate_statistics(self, values: List[float]) -> Dict:
        """计算统计数据"""
        return {
            "avg": statistics.mean(values),
            "min": min(values),
            "max": max(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0,
        }

    def _analyze_trend(self, values: List[float]) -> Dict:
        """分析趋势"""
        if len(values) < 2:
            return {"direction": None, "percentage": None}

        first_value = values[0]
        last_value = values[-1]
        trend_percentage = (
            ((last_value - first_value) / first_value * 100) if first_value != 0 else 0
        )

        if abs(trend_percentage) < 5:
            trend_direction = "stable"
        elif trend_percentage > 0:
            trend_direction = "up"
        else:
            trend_direction = "down"

        return {"direction": trend_direction, "percentage": trend_percentage}

    def _save_or_update_trend(
        self,
        db: Session,
        request: TrendAnalysisRequest,
        date_range: Tuple[datetime, datetime],
        statistics_data: Dict,
        trend: Dict,
        total_count: int,
        valid_count: int,
    ) -> HealthTrend:
        """创建或更新趋势记录"""
        start_date, end_date = date_range

        existing_trend = (
            db.query(HealthTrend)
            .filter(
                HealthTrend.user_id == request.user_id,
                HealthTrend.metric_type == request.metric_type,
                HealthTrend.period_type == request.period_type,
                HealthTrend.start_date == start_date,
                HealthTrend.end_date == end_date,
            )
            .first()
        )

        if existing_trend:
            self._update_trend_record(
                existing_trend, statistics_data, trend, valid_count, total_count
            )
            return existing_trend
        else:
            return self._create_trend_record(
                db,
                request,
                date_range,
                statistics_data,
                trend,
                valid_count,
                total_count,
            )

    def _update_trend_record(
        self,
        trend_record: HealthTrend,
        statistics_data: Dict,
        trend: Dict,
        valid_count: int,
        total_count: int,
    ):
        """更新趋势记录"""
        trend_record.avg_value = statistics_data["avg"]
        trend_record.min_value = statistics_data["min"]
        trend_record.max_value = statistics_data["max"]
        trend_record.std_deviation = statistics_data["std"]
        trend_record.trend_direction = trend["direction"]
        trend_record.trend_percentage = trend["percentage"]
        trend_record.sample_count = valid_count
        trend_record.quality_score = self._calculate_quality_score(
            valid_count, total_count
        )

    def _create_trend_record(
        self,
        db: Session,
        request: TrendAnalysisRequest,
        date_range: Tuple[datetime, datetime],
        statistics_data: Dict,
        trend: Dict,
        valid_count: int,
        total_count: int,
    ) -> HealthTrend:
        """创建趋势记录"""
        start_date, end_date = date_range

        trend_record = HealthTrend(
            user_id=request.user_id,
            device_id=request.device_id,
            metric_type=request.metric_type,
            period_type=request.period_type,
            start_date=start_date,
            end_date=end_date,
            avg_value=statistics_data["avg"],
            min_value=statistics_data["min"],
            max_value=statistics_data["max"],
            std_deviation=statistics_data["std"],
            trend_direction=trend["direction"],
            trend_percentage=trend["percentage"],
            sample_count=valid_count,
            missing_count=total_count - valid_count,
            quality_score=self._calculate_quality_score(valid_count, total_count),
        )
        db.add(trend_record)
        db.commit()
        return trend_record

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

        return (
            query.order_by(desc(Anomaly.detected_at))
            .offset(query_params.offset)
            .limit(query_params.limit)
            .all()
        )

    def update_anomaly(
        self, db: Session, anomaly_id: int, update_data: AnomalyUpdate
    ) -> Optional[Anomaly]:
        """更新异常记录"""
        anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
        if not anomaly:
            return None

        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(anomaly, field, value)

        db.commit()
        db.refresh(anomaly)
        return anomaly

    def get_anomaly_statistics(
        self, db: Session, user_id: str, start_date: datetime, end_date: datetime
    ) -> AnomalyStatistics:
        """获取异常统计数据"""
        anomalies = (
            db.query(Anomaly)
            .filter(
                Anomaly.user_id == user_id,
                Anomaly.detected_at >= start_date,
                Anomaly.detected_at <= end_date,
            )
            .all()
        )

        # 按严重程度统计
        critical_count = sum(
            1 for a in anomalies if a.severity == SeverityLevel.CRITICAL
        )
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
        most_common_type = (
            max(type_breakdown, key=type_breakdown.get) if type_breakdown else None
        )

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
            most_common_type=most_common_type,
        )

    # ========== 心脏健康分析 ==========

    def analyze_heart_health(
        self, db: Session, user_id: str, device_id: Optional[int] = None
    ) -> HeartHealthAnalysis:
        """
        心脏健康分析

        基于心率数据进行心脏健康评估,包括静息心率、心率变异性、心律不齐检测等
        """
        heart_rate_data = self._get_heart_rate_data(db, user_id, device_id)
        heart_rates = heart_rate_data["rates"]
        device_data = heart_rate_data["device_data"]

        stats = self._calculate_basic_stats(heart_rates)
        resting_heart_rate = self._estimate_resting_heart_rate(device_data)
        hrv_analysis = self._analyze_hrv(heart_rates)
        rhythm_analysis = self._analyze_heart_rhythm(heart_rates)
        risk_assessment = self._assess_cardiovascular_risk(
            stats, hrv_analysis, rhythm_analysis
        )
        recommendations = self._generate_recommendations(
            stats, hrv_analysis, rhythm_analysis, resting_heart_rate
        )

        return self._build_heart_health_response(
            user_id,
            stats,
            resting_heart_rate,
            hrv_analysis,
            rhythm_analysis,
            risk_assessment,
            recommendations,
        )

    def _get_heart_rate_data(
        self, db: Session, user_id: str, device_id: Optional[int] = None
    ) -> Dict:
        """获取最近7天的心率数据"""
        cutoff_time = datetime.utcnow() - timedelta(days=7)

        query = (
            db.query(DeviceData)
            .join(Device)
            .filter(
                Device.user_id == user_id,
                DeviceData.data_timestamp >= cutoff_time,
                DeviceData.heart_rate.isnot(None),
            )
        )

        if device_id:
            query = query.filter(DeviceData.id == device_id)

        device_data = query.order_by(DeviceData.data_timestamp).all()

        if not device_data:
            raise ValueError("没有找到心率数据")

        heart_rates = [d.heart_rate for d in device_data if d.heart_rate is not None]

        if not heart_rates:
            raise ValueError("心率数据为空")

        return {"rates": heart_rates, "device_data": device_data}

    def _calculate_basic_stats(self, heart_rates: List[float]) -> Dict:
        """计算基础统计数据"""
        return {
            "avg": statistics.mean(heart_rates),
            "max": max(heart_rates),
            "min": min(heart_rates),
        }

    def _estimate_resting_heart_rate(self, device_data: List) -> Optional[float]:
        """估算静息心率(取凌晨2-4点的心率平均值)"""
        if not device_data:
            return None

        nighttime_rates = [
            d.heart_rate
            for d in device_data
            if d.heart_rate and 2 <= d.data_timestamp.hour < 4
        ]

        return statistics.mean(nighttime_rates) if nighttime_rates else None

    def _analyze_hrv(self, heart_rates: List[float]) -> Dict:
        """分析心率变异性"""
        if len(heart_rates) <= 1:
            return {"value": None, "status": None}

        hrv_value = statistics.stdev(heart_rates)

        if hrv_value > 50:
            hrv_status = "excellent"
        elif hrv_value > 30:
            hrv_status = "good"
        elif hrv_value > 20:
            hrv_status = "fair"
        else:
            hrv_status = "poor"

        return {"value": hrv_value, "status": hrv_status}

    def _analyze_heart_rhythm(self, heart_rates: List[float]) -> Dict:
        """分析心律不齐"""
        if len(heart_rates) <= 10:
            return {"detected": False, "count": 0}

        # 计算心率连续差分
        hr_diffs = [
            abs(heart_rates[i + 1] - heart_rates[i])
            for i in range(len(heart_rates) - 1)
        ]
        irregular_count = sum(1 for diff in hr_diffs if diff > 15)
        irregular_rhythm_detected = irregular_count > len(hr_diffs) * 0.2

        return {"detected": irregular_rhythm_detected, "count": irregular_count}

    def _assess_cardiovascular_risk(
        self, stats: Dict, hrv_analysis: Dict, rhythm_analysis: Dict
    ) -> str:
        """评估心血管风险"""
        risk_factors = []

        if stats["avg"] > 90:
            risk_factors.append("静息心率偏高")
        if stats["min"] < 45:
            risk_factors.append("心率偏低")
        if rhythm_analysis["detected"]:
            risk_factors.append("心律不齐")
        if hrv_analysis["status"] == "poor":
            risk_factors.append("心率变异性低")

        if len(risk_factors) >= 3:
            return "high"
        elif len(risk_factors) >= 2:
            return "medium"
        elif len(risk_factors) >= 1:
            return "low"
        else:
            return "very_low"

    def _generate_recommendations(
        self,
        stats: Dict,
        hrv_analysis: Dict,
        rhythm_analysis: Dict,
        resting_heart_rate: Optional[float],
    ) -> List[str]:
        """生成健康建议"""
        recommendations = []

        if stats["avg"] > 90:
            recommendations.append("建议进行适度有氧运动降低静息心率")
        if rhythm_analysis["detected"]:
            recommendations.append("建议定期监测心率,必要时咨询医生")
        if hrv_analysis["status"] == "poor":
            recommendations.append("建议改善睡眠质量,增加运动")
        if resting_heart_rate and resting_heart_rate < 50:
            recommendations.append("如无其他不适,低静息心率可能表示心脏功能良好")

        return recommendations

    def _build_heart_health_response(
        self,
        user_id: str,
        stats: Dict,
        resting_heart_rate: Optional[float],
        hrv_analysis: Dict,
        rhythm_analysis: Dict,
        risk_assessment: str,
        recommendations: List[str],
    ) -> HeartHealthAnalysis:
        """构建心脏健康分析响应"""
        # 重新计算风险因子列表
        risk_factors = []
        if stats["avg"] > 90:
            risk_factors.append("静息心率偏高")
        if stats["min"] < 45:
            risk_factors.append("心率偏低")
        if rhythm_analysis["detected"]:
            risk_factors.append("心律不齐")
        if hrv_analysis["status"] == "poor":
            risk_factors.append("心率变异性低")

        return HeartHealthAnalysis(
            user_id=user_id,
            analysis_date=datetime.utcnow(),
            avg_heart_rate=round(stats["avg"], 1),
            resting_heart_rate=(
                round(resting_heart_rate, 1) if resting_heart_rate else None
            ),
            max_heart_rate=stats["max"],
            min_heart_rate=stats["min"],
            hrv_value=(
                round(hrv_analysis["value"], 1) if hrv_analysis["value"] else None
            ),
            hrv_status=hrv_analysis["status"],
            irregular_rhythm_detected=rhythm_analysis["detected"],
            irregular_rhythm_count=rhythm_analysis["count"],
            cardiovascular_risk=risk_assessment,
            risk_factors=risk_factors,
            health_recommendations=recommendations,
        )

    # ========== 辅助方法 ==========

    def _trigger_critical_anomaly_alert(self, db: Session, anomaly: Anomaly):
        """触发危急异常警报"""
        # 发送通知
        self.notification_service.send_critical_anomaly_alert(
            db, anomaly.user_id, anomaly.anomaly_type.value, anomaly.description
        )

        # 自动触发SOS
        if anomaly.anomaly_type in [
            AnomalyTypeEnum.HEART_RATE_STOP,
            AnomalyTypeEnum.FALL_DETECTED,
        ]:
            from app.schemas.sos_request import SOSRequestCreate

            # 创建 SOS 请求数据
            sos_data = SOSRequestCreate(
                user_id=anomaly.user_id,  # 使用认证用户的 ID
                sos_type="auto",
                trigger_type="health",
                emergency_reason=f"系统自动触发: {anomaly.description}",
                severity="critical",
            )

            # 使用修复后的 API（user_id 参数从认证获取，不可篡改）
            sos_request = self.sos_service.create_sos_request(
                db, anomaly.user_id, sos_data  # 用户 ID 从认证获取  # SOS 数据
            )

            anomaly.sos_triggered = sos_request.id
            anomaly.action_taken = f"自动触发SOS #{sos_request.id}"
            db.commit()

    def _get_metric_field(self, metric_type: str):
        """根据指标类型获取数据库字段"""

        field_mapping = {
            "heart_rate": DeviceData.heart_rate,
            "steps": DeviceData.steps,
            "calories": DeviceData.calories,
            "distance": DeviceData.distance,
            "sleep_hours": DeviceData.sleep_hours,
            "blood_pressure_systolic": DeviceData.systolic,
            "blood_pressure_diastolic": DeviceData.diastolic,
            "blood_oxygen": DeviceData.blood_oxygen,
            "body_temperature": DeviceData.temperature,
        }

        return field_mapping.get(metric_type)

    def _calculate_quality_score(self, valid_count: int, total_count: int) -> float:
        """计算数据质量分数"""
        if total_count == 0:
            return 0.0

        ratio = valid_count / total_count
        return round(ratio * 100, 2)
