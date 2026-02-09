"""
健康数据报告服务

提供健康数据趋势分析、异常检测、统计报告等功能
"""

import json
from datetime import datetime, timedelta, date
from typing import List, Optional, Dict, Any, Tuple
from collections import defaultdict
from enum import Enum as PyEnum
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, extract

from app.services.base_service import BaseService
from app.models.device_data import DeviceData, DeviceThreshold
from app.models.health_record import HealthRecord


class ReportPeriod(str, PyEnum):
    """报告周期"""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class HealthMetricType(str, PyEnum):
    """健康指标类型"""
    HEART_RATE = "heart_rate"
    BLOOD_PRESSURE = "blood_pressure"
    BLOOD_OXYGEN = "blood_oxygen"
    BODY_TEMPERATURE = "body_temperature"
    STEPS = "steps"
    SLEEP = "sleep"
    CALORIES = "calories"


class HealthReportService(BaseService):
    """健康报告服务"""
    
    cache_prefix = "health_report"
    
    # 默认健康指标阈值
    DEFAULT_THRESHOLDS = {
        "heart_rate": {"min": 60, "max": 100, "unit": "bpm"},
        "blood_pressure_systolic": {"min": 90, "max": 140, "unit": "mmHg"},
        "blood_pressure_diastolic": {"min": 60, "max": 90, "unit": "mmHg"},
        "blood_oxygen": {"min": 95, "max": 100, "unit": "%"},
        "body_temperature": {"min": 36.0, "max": 37.3, "unit": "℃"},
        "steps": {"min": 6000, "max": 20000, "unit": "步"},
        "sleep_duration": {"min": 6, "max": 10, "unit": "小时"},
    }
    
    @classmethod
    def get_trend_analysis(
        cls,
        db: Session,
        user_id: str,
        metric_type: str,
        start_date: date,
        end_date: date,
        period: ReportPeriod = ReportPeriod.DAY
    ) -> Dict[str, Any]:
        """
        获取健康数据趋势分析
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            metric_type: 指标类型
            start_date: 开始日期
            end_date: 结束日期
            period: 统计周期
            
        Returns:
            趋势分析结果
        """
        # 获取数据
        data_points = cls._get_metric_data(db, user_id, metric_type, start_date, end_date)
        
        if not data_points:
            return {
                "metric_type": metric_type,
                "period": period.value,
                "data_points": [],
                "statistics": None,
                "trend": "no_data"
            }
        
        # 按周期聚合数据
        aggregated = cls._aggregate_by_period(data_points, period)
        
        # 计算统计值
        statistics = cls._calculate_statistics([d["value"] for d in data_points])
        
        # 分析趋势
        trend = cls._analyze_trend([d["value"] for d in data_points])
        
        # 获取阈值
        thresholds = cls._get_user_thresholds(db, user_id, metric_type)
        
        # 检测异常
        anomalies = cls._detect_anomalies(data_points, thresholds)
        
        return {
            "metric_type": metric_type,
            "period": period.value,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "data_points": aggregated,
            "statistics": statistics,
            "trend": trend,
            "thresholds": thresholds,
            "anomalies": anomalies,
            "total_readings": len(data_points)
        }
    
    @classmethod
    def get_comprehensive_report(
        cls,
        db: Session,
        user_id: str,
        report_date: date,
        period: ReportPeriod = ReportPeriod.WEEK
    ) -> Dict[str, Any]:
        """
        获取综合健康报告
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            report_date: 报告日期
            period: 报告周期
            
        Returns:
            综合健康报告
        """
        # 计算日期范围
        start_date, end_date = cls._get_period_range(report_date, period)
        
        # 获取各项指标数据
        metrics = {}
        overall_score = 0
        metric_count = 0
        
        for metric_type in ["heart_rate", "blood_pressure", "blood_oxygen", "steps", "sleep"]:
            try:
                trend = cls.get_trend_analysis(db, user_id, metric_type, start_date, end_date, period)
                metrics[metric_type] = trend
                
                if trend["statistics"]:
                    # 计算单项健康评分（简化算法）
                    score = cls._calculate_metric_score(trend)
                    metrics[metric_type]["health_score"] = score
                    overall_score += score
                    metric_count += 1
            except Exception as e:
                metrics[metric_type] = {"error": str(e)}
        
        # 计算综合健康评分
        avg_score = round(overall_score / metric_count, 1) if metric_count > 0 else 0
        
        # 生成健康建议
        suggestions = cls._generate_suggestions(metrics)
        
        # 获取健康档案基本信息
        health_record = db.query(HealthRecord).filter(
            HealthRecord.user_id == user_id
        ).first()
        
        return {
            "report_id": f"HR{user_id}{report_date.strftime('%Y%m%d')}",
            "user_id": user_id,
            "report_type": f"{period.value}_report",
            "report_date": report_date.isoformat(),
            "period": {
                "type": period.value,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "overall_health_score": avg_score,
            "health_level": cls._get_health_level(avg_score),
            "metrics": metrics,
            "suggestions": suggestions,
            "user_profile": {
                "has_health_record": health_record is not None,
                "record_updated_at": health_record.updated_at.isoformat() if health_record else None
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    @classmethod
    def get_anomaly_report(
        cls,
        db: Session,
        user_id: str,
        days: int = 7,
        severity: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取异常检测报告
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            days: 查询天数
            severity: 严重程度筛选（high/medium/low）
            
        Returns:
            异常检测报告
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        all_anomalies = []
        
        for metric_type in ["heart_rate", "blood_pressure", "blood_oxygen", "body_temperature"]:
            trend = cls.get_trend_analysis(
                db, user_id, metric_type, start_date, end_date, ReportPeriod.DAY
            )
            
            for anomaly in trend.get("anomalies", []):
                anomaly["metric_type"] = metric_type
                all_anomalies.append(anomaly)
        
        # 按严重程度排序
        severity_order = {"high": 0, "medium": 1, "low": 2}
        all_anomalies.sort(key=lambda x: severity_order.get(x.get("severity"), 3))
        
        # 筛选
        if severity:
            all_anomalies = [a for a in all_anomalies if a.get("severity") == severity]
        
        # 统计
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        for a in all_anomalies:
            severity_counts[a.get("severity", "low")] += 1
        
        return {
            "report_period": f"最近{days}天",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_anomalies": len(all_anomalies),
            "severity_distribution": severity_counts,
            "anomalies": all_anomalies[:50],  # 最多返回50条
            "summary": cls._generate_anomaly_summary(all_anomalies)
        }
    
    @classmethod
    def compare_periods(
        cls,
        db: Session,
        user_id: str,
        metric_type: str,
        current_start: date,
        current_end: date,
        previous_start: date,
        previous_end: date
    ) -> Dict[str, Any]:
        """
        对比两个时期的数据
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            metric_type: 指标类型
            current_start, current_end: 当前时期
            previous_start, previous_end: 对比时期
            
        Returns:
            对比分析结果
        """
        current_data = cls.get_trend_analysis(
            db, user_id, metric_type, current_start, current_end, ReportPeriod.DAY
        )
        
        previous_data = cls.get_trend_analysis(
            db, user_id, metric_type, previous_start, previous_end, ReportPeriod.DAY
        )
        
        current_stats = current_data.get("statistics", {})
        previous_stats = previous_data.get("statistics", {})
        
        comparison = {
            "metric_type": metric_type,
            "current_period": {
                "start": current_start.isoformat(),
                "end": current_end.isoformat(),
                "statistics": current_stats
            },
            "previous_period": {
                "start": previous_start.isoformat(),
                "end": previous_end.isoformat(),
                "statistics": previous_stats
            },
            "changes": {}
        }
        
        # 计算变化
        if current_stats and previous_stats:
            for key in ["mean", "median", "min", "max"]:
                curr_val = current_stats.get(key)
                prev_val = previous_stats.get(key)
                if curr_val is not None and prev_val is not None and prev_val != 0:
                    change_pct = round((curr_val - prev_val) / prev_val * 100, 2)
                    comparison["changes"][key] = {
                        "current": curr_val,
                        "previous": prev_val,
                        "change": round(curr_val - prev_val, 2),
                        "change_percent": change_pct
                    }
        
        return comparison
    
    @classmethod
    def get_daily_summary(
        cls,
        db: Session,
        user_id: str,
        summary_date: date
    ) -> Dict[str, Any]:
        """
        获取每日健康摘要
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            summary_date: 摘要日期
            
        Returns:
            每日健康摘要
        """
        next_day = summary_date + timedelta(days=1)
        
        summary = {
            "date": summary_date.isoformat(),
            "user_id": user_id,
            "metrics": {}
        }
        
        # 心率
        hr_data = cls._get_metric_data(db, user_id, "heart_rate", summary_date, next_day)
        if hr_data:
            summary["metrics"]["heart_rate"] = {
                "avg": round(sum(d["value"] for d in hr_data) / len(hr_data), 1),
                "min": min(d["value"] for d in hr_data),
                "max": max(d["value"] for d in hr_data),
                "readings": len(hr_data)
            }
        
        # 步数
        steps_data = cls._get_metric_data(db, user_id, "steps", summary_date, next_day)
        if steps_data:
            total_steps = sum(d["value"] for d in steps_data)
            summary["metrics"]["steps"] = {
                "total": total_steps,
                "goal": 10000,
                "goal_achieved": total_steps >= 10000,
                "completion_rate": round(min(total_steps / 10000 * 100, 100), 1)
            }
        
        # 血压
        bp_data = cls._get_metric_data(db, user_id, "blood_pressure", summary_date, next_day)
        if bp_data:
            summary["metrics"]["blood_pressure"] = {
                "systolic_avg": round(sum(d.get("systolic", 0) for d in bp_data) / len(bp_data), 1),
                "diastolic_avg": round(sum(d.get("diastolic", 0) for d in bp_data) / len(bp_data), 1),
                "readings": len(bp_data)
            }
        
        # 睡眠
        sleep_data = cls._get_metric_data(db, user_id, "sleep", summary_date, next_day)
        if sleep_data:
            total_sleep = sum(d["value"] for d in sleep_data)
            summary["metrics"]["sleep"] = {
                "total_hours": round(total_sleep, 1),
                "quality": cls._evaluate_sleep_quality(total_sleep)
            }
        
        # 计算今日健康评分
        summary["daily_score"] = cls._calculate_daily_score(summary["metrics"])
        summary["health_status"] = cls._get_health_level(summary["daily_score"])
        
        return summary
    
    @classmethod
    def _get_metric_data(
        cls,
        db: Session,
        user_id: str,
        metric_type: str,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """获取指标数据"""
        query = db.query(DeviceData).filter(
            DeviceData.user_id == user_id,
            DeviceData.data_timestamp >= datetime.combine(start_date, datetime.min.time()),
            DeviceData.data_timestamp < datetime.combine(end_date, datetime.min.time())
        )
        
        if metric_type == "heart_rate":
            query = query.filter(DeviceData.heart_rate.isnot(None))
            results = query.order_by(DeviceData.data_timestamp).all()
            return [
                {
                    "timestamp": r.data_timestamp.isoformat() if r.data_timestamp else r.created_at.isoformat(),
                    "value": r.heart_rate,
                    "datetime": r.data_timestamp or r.created_at
                }
                for r in results
            ]
        
        elif metric_type == "blood_pressure":
            query = query.filter(DeviceData.systolic_pressure.isnot(None))
            results = query.order_by(DeviceData.data_timestamp).all()
            return [
                {
                    "timestamp": r.data_timestamp.isoformat() if r.data_timestamp else r.created_at.isoformat(),
                    "value": (r.systolic_pressure + r.diastolic_pressure) / 2,
                    "systolic": r.systolic_pressure,
                    "diastolic": r.diastolic_pressure,
                    "datetime": r.data_timestamp or r.created_at
                }
                for r in results
            ]
        
        elif metric_type == "blood_oxygen":
            query = query.filter(DeviceData.blood_oxygen.isnot(None))
            results = query.order_by(DeviceData.data_timestamp).all()
            return [
                {
                    "timestamp": r.data_timestamp.isoformat() if r.data_timestamp else r.created_at.isoformat(),
                    "value": r.blood_oxygen,
                    "datetime": r.data_timestamp or r.created_at
                }
                for r in results
            ]
        
        elif metric_type == "body_temperature":
            query = query.filter(DeviceData.body_temperature.isnot(None))
            results = query.order_by(DeviceData.data_timestamp).all()
            return [
                {
                    "timestamp": r.data_timestamp.isoformat() if r.data_timestamp else r.created_at.isoformat(),
                    "value": r.body_temperature,
                    "datetime": r.data_timestamp or r.created_at
                }
                for r in results
            ]
        
        elif metric_type == "steps":
            query = query.filter(DeviceData.steps.isnot(None))
            results = query.order_by(DeviceData.data_timestamp).all()
            return [
                {
                    "timestamp": r.data_timestamp.isoformat() if r.data_timestamp else r.created_at.isoformat(),
                    "value": r.steps,
                    "datetime": r.data_timestamp or r.created_at
                }
                for r in results
            ]
        
        elif metric_type == "sleep":
            query = query.filter(DeviceData.sleep_duration.isnot(None))
            results = query.order_by(DeviceData.data_timestamp).all()
            return [
                {
                    "timestamp": r.data_timestamp.isoformat() if r.data_timestamp else r.created_at.isoformat(),
                    "value": r.sleep_duration,
                    "datetime": r.data_timestamp or r.created_at
                }
                for r in results
            ]
        
        return []
    
    @classmethod
    def _aggregate_by_period(
        cls,
        data_points: List[Dict],
        period: ReportPeriod
    ) -> List[Dict]:
        """按周期聚合数据"""
        if not data_points:
            return []
        
        if period == ReportPeriod.DAY:
            # 按天聚合
            daily = defaultdict(list)
            for dp in data_points:
                day = dp["datetime"].strftime("%Y-%m-%d")
                daily[day].append(dp["value"])
            
            return [
                {
                    "date": day,
                    "avg": round(sum(values) / len(values), 2),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values)
                }
                for day, values in sorted(daily.items())
            ]
        
        elif period == ReportPeriod.WEEK:
            # 按周聚合
            weekly = defaultdict(list)
            for dp in data_points:
                week = dp["datetime"].strftime("%Y-W%W")
                weekly[week].append(dp["value"])
            
            return [
                {
                    "week": week,
                    "avg": round(sum(values) / len(values), 2),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values)
                }
                for week, values in sorted(weekly.items())
            ]
        
        elif period == ReportPeriod.MONTH:
            # 按月聚合
            monthly = defaultdict(list)
            for dp in data_points:
                month = dp["datetime"].strftime("%Y-%m")
                monthly[month].append(dp["value"])
            
            return [
                {
                    "month": month,
                    "avg": round(sum(values) / len(values), 2),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values)
                }
                for month, values in sorted(monthly.items())
            ]
        
        return data_points
    
    @classmethod
    def _calculate_statistics(cls, values: List[float]) -> Dict[str, float]:
        """计算统计数据"""
        if not values:
            return None
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        mean = sum(values) / n
        
        # 中位数
        if n % 2 == 0:
            median = (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
        else:
            median = sorted_values[n//2]
        
        # 标准差
        variance = sum((x - mean) ** 2 for x in values) / n
        std_dev = variance ** 0.5
        
        return {
            "mean": round(mean, 2),
            "median": round(median, 2),
            "min": min(values),
            "max": max(values),
            "std_dev": round(std_dev, 2),
            "count": n
        }
    
    @classmethod
    def _analyze_trend(cls, values: List[float]) -> str:
        """分析趋势"""
        if len(values) < 3:
            return "insufficient_data"
        
        # 简单线性回归
        n = len(values)
        x = list(range(n))
        
        mean_x = sum(x) / n
        mean_y = sum(values) / n
        
        numerator = sum((x[i] - mean_x) * (values[i] - mean_y) for i in range(n))
        denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        # 根据斜率判断趋势
        avg_value = sum(values) / len(values)
        threshold = avg_value * 0.05  # 5%阈值
        
        if slope > threshold:
            return "increasing"
        elif slope < -threshold:
            return "decreasing"
        else:
            return "stable"
    
    @classmethod
    def _get_user_thresholds(
        cls,
        db: Session,
        user_id: str,
        metric_type: str
    ) -> Dict[str, Any]:
        """获取用户阈值设置"""
        threshold = db.query(DeviceThreshold).filter(
            DeviceThreshold.user_id == user_id,
            DeviceThreshold.enabled == 1
        ).first()
        
        if not threshold:
            return cls.DEFAULT_THRESHOLDS.get(metric_type, {})
        
        # 根据指标类型返回对应的阈值
        if metric_type == "heart_rate":
            return {
                "min": threshold.heart_rate_min or cls.DEFAULT_THRESHOLDS["heart_rate"]["min"],
                "max": threshold.heart_rate_max or cls.DEFAULT_THRESHOLDS["heart_rate"]["max"],
                "unit": "bpm"
            }
        elif metric_type == "blood_pressure":
            return {
                "systolic": {
                    "min": threshold.blood_pressure_systolic_min or cls.DEFAULT_THRESHOLDS["blood_pressure_systolic"]["min"],
                    "max": threshold.blood_pressure_systolic_max or cls.DEFAULT_THRESHOLDS["blood_pressure_systolic"]["max"]
                },
                "diastolic": {
                    "min": threshold.blood_pressure_diastolic_min or cls.DEFAULT_THRESHOLDS["blood_pressure_diastolic"]["min"],
                    "max": threshold.blood_pressure_diastolic_max or cls.DEFAULT_THRESHOLDS["blood_pressure_diastolic"]["max"]
                },
                "unit": "mmHg"
            }
        elif metric_type == "blood_oxygen":
            return {
                "min": threshold.blood_oxygen_min or cls.DEFAULT_THRESHOLDS["blood_oxygen"]["min"],
                "max": 100,
                "unit": "%"
            }
        elif metric_type == "body_temperature":
            return {
                "min": threshold.temperature_min or cls.DEFAULT_THRESHOLDS["body_temperature"]["min"],
                "max": threshold.temperature_max or cls.DEFAULT_THRESHOLDS["body_temperature"]["max"],
                "unit": "℃"
            }
        elif metric_type == "steps":
            return {
                "min": threshold.steps_min or cls.DEFAULT_THRESHOLDS["steps"]["min"],
                "max": threshold.steps_max or cls.DEFAULT_THRESHOLDS["steps"]["max"],
                "unit": "步"
            }
        elif metric_type == "sleep":
            return {
                "min": threshold.sleep_duration_min or cls.DEFAULT_THRESHOLDS["sleep_duration"]["min"],
                "max": cls.DEFAULT_THRESHOLDS["sleep_duration"]["max"],
                "unit": "小时"
            }
        
        return {}
    
    @classmethod
    def _detect_anomalies(
        cls,
        data_points: List[Dict],
        thresholds: Dict[str, Any]
    ) -> List[Dict]:
        """检测异常数据"""
        anomalies = []
        
        min_val = thresholds.get("min")
        max_val = thresholds.get("max")
        
        for dp in data_points:
            value = dp["value"]
            severity = None
            
            if min_val is not None and value < min_val:
                diff_percent = abs(value - min_val) / min_val * 100 if min_val > 0 else 0
                if diff_percent > 20:
                    severity = "high"
                elif diff_percent > 10:
                    severity = "medium"
                else:
                    severity = "low"
            
            if max_val is not None and value > max_val:
                diff_percent = (value - max_val) / max_val * 100 if max_val > 0 else 0
                if diff_percent > 20:
                    severity = "high"
                elif diff_percent > 10:
                    severity = "medium"
                else:
                    severity = "low"
            
            if severity:
                anomalies.append({
                    "timestamp": dp["timestamp"],
                    "value": value,
                    "threshold_min": min_val,
                    "threshold_max": max_val,
                    "severity": severity,
                    "type": "below_min" if (min_val and value < min_val) else "above_max"
                })
        
        return anomalies
    
    @classmethod
    def _get_period_range(cls, report_date: date, period: ReportPeriod) -> Tuple[date, date]:
        """获取报告周期日期范围"""
        end_date = report_date
        
        if period == ReportPeriod.DAY:
            start_date = end_date - timedelta(days=1)
        elif period == ReportPeriod.WEEK:
            start_date = end_date - timedelta(weeks=1)
        elif period == ReportPeriod.MONTH:
            start_date = end_date - timedelta(days=30)
        elif period == ReportPeriod.YEAR:
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=7)
        
        return start_date, end_date
    
    @classmethod
    def _calculate_metric_score(cls, trend_data: Dict) -> float:
        """计算单项健康评分（简化算法）"""
        stats = trend_data.get("statistics", {})
        if not stats:
            return 0
        
        anomalies = trend_data.get("anomalies", [])
        total = stats.get("count", 0)
        anomaly_count = len(anomalies)
        
        if total == 0:
            return 0
        
        # 基于异常率计算分数
        anomaly_rate = anomaly_count / total
        base_score = 100 - (anomaly_rate * 100)
        
        return round(max(0, min(100, base_score)), 1)
    
    @classmethod
    def _get_health_level(cls, score: float) -> str:
        """获取健康等级"""
        if score >= 90:
            return "excellent"
        elif score >= 80:
            return "good"
        elif score >= 60:
            return "fair"
        else:
            return "poor"
    
    @classmethod
    def _generate_suggestions(cls, metrics: Dict) -> List[str]:
        """生成健康建议"""
        suggestions = []
        
        for metric_type, data in metrics.items():
            if isinstance(data, dict) and "trend" in data:
                trend = data.get("trend")
                anomalies = data.get("anomalies", [])
                
                if trend == "increasing":
                    if metric_type == "heart_rate":
                        suggestions.append("心率呈上升趋势，建议注意休息，避免过度疲劳")
                    elif metric_type == "blood_pressure":
                        suggestions.append("血压呈上升趋势，建议控制饮食盐分，适当运动")
                
                if trend == "decreasing":
                    if metric_type == "steps":
                        suggestions.append("运动量减少，建议增加日常步行")
                    elif metric_type == "sleep":
                        suggestions.append("睡眠时间减少，建议保持规律作息")
                
                if anomalies:
                    high_count = sum(1 for a in anomalies if a.get("severity") == "high")
                    if high_count > 0:
                        suggestions.append(f"{metric_type}有{high_count}次严重异常，建议及时就医检查")
        
        return suggestions[:5]  # 最多返回5条建议
    
    @classmethod
    def _generate_anomaly_summary(cls, anomalies: List[Dict]) -> str:
        """生成异常摘要"""
        if not anomalies:
            return "最近未检测到明显异常"
        
        high_count = sum(1 for a in anomalies if a.get("severity") == "high")
        
        if high_count > 0:
            return f"检测到{high_count}次严重异常，建议及时关注"
        elif len(anomalies) > 5:
            return f"检测到{len(anomalies)}次轻度异常，建议关注健康趋势"
        else:
            return "有少量异常，但总体在可控范围内"
    
    @classmethod
    def _evaluate_sleep_quality(cls, total_hours: float) -> str:
        """评估睡眠质量"""
        if total_hours >= 7 and total_hours <= 9:
            return "good"
        elif total_hours >= 6 and total_hours < 7:
            return "fair"
        elif total_hours < 6:
            return "poor"
        else:
            return "excessive"
    
    @classmethod
    def _calculate_daily_score(cls, metrics: Dict) -> float:
        """计算每日健康评分"""
        score = 70  # 基础分
        
        # 步数评分
        if "steps" in metrics:
            steps_data = metrics["steps"]
            if steps_data.get("goal_achieved"):
                score += 15
            else:
                score += steps_data.get("completion_rate", 0) * 0.15
        
        # 睡眠评分
        if "sleep" in metrics:
            sleep_quality = metrics["sleep"].get("quality")
            if sleep_quality == "good":
                score += 15
            elif sleep_quality == "fair":
                score += 10
            elif sleep_quality == "poor":
                score += 5
        
        return round(min(100, score), 1)
