"""
健康报告服务测试

测试健康数据趋势分析、综合报告、异常检测等功能
"""

import pytest
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from app.models.device_data import DeviceData
from app.services.health_report_service import HealthReportService, ReportPeriod


class TestHealthReportService:
    """测试健康报告服务"""

    def _create_device_data(self, db: Session, user_id: str, **kwargs):
        """创建设备数据"""
        defaults = {
            "data_id": f"DD{datetime.utcnow().timestamp()}",
            "device_id": "device123",
            "user_id": user_id,
            "data_type": "heart_rate",
            "data_value": {},
            "upload_time": datetime.utcnow(),
            "data_timestamp": datetime.utcnow()
        }
        defaults.update(kwargs)
        
        data = DeviceData(**defaults)
        db.add(data)
        db.commit()
        return data

    def test_get_trend_analysis_heart_rate(self, db: Session):
        """测试心率趋势分析"""
        user_id = "user123"
        base_date = date.today() - timedelta(days=7)
        
        # 创建7天的心率数据
        for i in range(7):
            for j in range(3):  # 每天3条数据
                self._create_device_data(
                    db,
                    user_id=user_id,
                    data_type="heart_rate",
                    heart_rate=70 + i + j,  # 递增趋势
                    data_timestamp=datetime.combine(
                        base_date + timedelta(days=i),
                        datetime.min.time()
                    ) + timedelta(hours=j*8)
                )
        
        result = HealthReportService.get_trend_analysis(
            db,
            user_id=user_id,
            metric_type="heart_rate",
            start_date=base_date,
            end_date=date.today(),
            period=ReportPeriod.DAY
        )
        
        assert result["metric_type"] == "heart_rate"
        assert result["period"] == "day"
        assert len(result["data_points"]) == 7  # 7天
        assert result["statistics"] is not None
        assert result["statistics"]["count"] == 21  # 21条数据
        assert "mean" in result["statistics"]
        assert "trend" in result

    def test_get_trend_analysis_steps(self, db: Session):
        """测试步数趋势分析"""
        user_id = "user123"
        base_date = date.today() - timedelta(days=5)
        
        # 创建5天的步数数据
        for i in range(5):
            self._create_device_data(
                db,
                user_id=user_id,
                data_type="steps",
                steps=8000 + i * 500,
                data_timestamp=datetime.combine(
                    base_date + timedelta(days=i),
                    datetime.min.time()
                )
            )
        
        result = HealthReportService.get_trend_analysis(
            db,
            user_id=user_id,
            metric_type="steps",
            start_date=base_date,
            end_date=base_date + timedelta(days=5),
            period=ReportPeriod.DAY
        )
        
        assert result["metric_type"] == "steps"
        assert len(result["data_points"]) == 5

    def test_get_trend_analysis_no_data(self, db: Session):
        """测试无数据时的趋势分析"""
        result = HealthReportService.get_trend_analysis(
            db,
            user_id="no_data_user",
            metric_type="heart_rate",
            start_date=date.today() - timedelta(days=7),
            end_date=date.today(),
            period=ReportPeriod.DAY
        )
        
        assert result["metric_type"] == "heart_rate"
        assert len(result["data_points"]) == 0
        assert result["statistics"] is None
        assert result["trend"] == "no_data"

    def test_get_comprehensive_report(self, db: Session):
        """测试综合健康报告"""
        user_id = "user123"
        
        # 创建一些测试数据
        base_date = date.today() - timedelta(days=3)
        for i in range(3):
            self._create_device_data(
                db,
                user_id=user_id,
                data_type="heart_rate",
                heart_rate=75,
                data_timestamp=datetime.combine(base_date + timedelta(days=i), datetime.min.time())
            )
            self._create_device_data(
                db,
                user_id=user_id,
                data_type="steps",
                steps=10000,
                data_timestamp=datetime.combine(base_date + timedelta(days=i), datetime.min.time())
            )
        
        result = HealthReportService.get_comprehensive_report(
            db,
            user_id=user_id,
            report_date=date.today(),
            period=ReportPeriod.WEEK
        )
        
        assert "report_id" in result
        assert result["user_id"] == user_id
        assert "overall_health_score" in result
        assert "health_level" in result
        assert "metrics" in result
        assert "suggestions" in result

    def test_get_anomaly_report(self, db: Session):
        """测试异常检测报告"""
        user_id = "user123"
        base_date = date.today() - timedelta(days=3)
        
        # 创建正常和异常的心率数据
        for i in range(3):
            # 正常心率
            self._create_device_data(
                db,
                user_id=user_id,
                data_type="heart_rate",
                heart_rate=75,
                data_timestamp=datetime.combine(base_date + timedelta(days=i), datetime.min.time())
            )
        
        # 异常高心率
        self._create_device_data(
            db,
            user_id=user_id,
            data_type="heart_rate",
            heart_rate=150,  # 异常高
            data_timestamp=datetime.utcnow()
        )
        
        result = HealthReportService.get_anomaly_report(
            db,
            user_id=user_id,
            days=7
        )
        
        assert "total_anomalies" in result
        assert "severity_distribution" in result
        assert "anomalies" in result
        assert "summary" in result

    def test_compare_periods(self, db: Session):
        """测试时期对比"""
        user_id = "user123"
        
        # 当前时期数据
        current_start = date.today() - timedelta(days=7)
        current_end = date.today()
        for i in range(7):
            self._create_device_data(
                db,
                user_id=user_id,
                data_type="heart_rate",
                heart_rate=80,
                data_timestamp=datetime.combine(current_start + timedelta(days=i), datetime.min.time())
            )
        
        # 上一时期数据
        previous_start = date.today() - timedelta(days=14)
        previous_end = date.today() - timedelta(days=7)
        for i in range(7):
            self._create_device_data(
                db,
                user_id=user_id,
                data_type="heart_rate",
                heart_rate=70,
                data_timestamp=datetime.combine(previous_start + timedelta(days=i), datetime.min.time())
            )
        
        result = HealthReportService.compare_periods(
            db,
            user_id=user_id,
            metric_type="heart_rate",
            current_start=current_start,
            current_end=current_end,
            previous_start=previous_start,
            previous_end=previous_end
        )
        
        assert result["metric_type"] == "heart_rate"
        assert "current_period" in result
        assert "previous_period" in result
        assert "changes" in result

    def test_get_daily_summary(self, db: Session):
        """测试每日健康摘要"""
        user_id = "user123"
        summary_date = date.today()
        
        # 创建一天的数据
        self._create_device_data(
            db,
            user_id=user_id,
            data_type="heart_rate",
            heart_rate=72,
            data_timestamp=datetime.combine(summary_date, datetime.min.time()) + timedelta(hours=8)
        )
        
        self._create_device_data(
            db,
            user_id=user_id,
            data_type="steps",
            steps=12000,
            data_timestamp=datetime.combine(summary_date, datetime.min.time())
        )
        
        result = HealthReportService.get_daily_summary(
            db,
            user_id=user_id,
            summary_date=summary_date
        )
        
        assert result["date"] == summary_date.isoformat()
        assert result["user_id"] == user_id
        assert "metrics" in result
        assert "daily_score" in result
        assert "health_status" in result

    def test_calculate_statistics(self):
        """测试统计计算"""
        values = [70, 72, 75, 73, 71, 74, 76]
        
        stats = HealthReportService._calculate_statistics(values)
        
        assert stats["mean"] == 73
        assert stats["median"] == 73
        assert stats["min"] == 70
        assert stats["max"] == 76
        assert stats["count"] == 7
        assert "std_dev" in stats

    def test_calculate_statistics_empty(self):
        """测试空数据统计"""
        stats = HealthReportService._calculate_statistics([])
        assert stats is None

    def test_analyze_trend_increasing(self):
        """测试上升趋势分析"""
        # 使用明显的上升趋势数据（超过5%阈值）
        values = [60, 65, 70, 75, 80, 85, 90]  # 50%增长
        trend = HealthReportService._analyze_trend(values)
        assert trend == "increasing"

    def test_analyze_trend_decreasing(self):
        """测试下降趋势分析"""
        # 使用明显的下降趋势数据
        values = [90, 85, 80, 75, 70, 65, 60]  # 33%下降
        trend = HealthReportService._analyze_trend(values)
        assert trend == "decreasing"

    def test_analyze_trend_stable(self):
        """测试稳定趋势分析"""
        values = [75, 76, 74, 75, 76, 75, 74]
        trend = HealthReportService._analyze_trend(values)
        assert trend == "stable"

    def test_detect_anomalies(self):
        """测试异常检测"""
        data_points = [
            {"timestamp": "2024-01-01T08:00:00", "value": 75, "datetime": datetime(2024, 1, 1, 8, 0)},
            {"timestamp": "2024-01-01T09:00:00", "value": 120, "datetime": datetime(2024, 1, 1, 9, 0)},  # 异常高
            {"timestamp": "2024-01-01T10:00:00", "value": 50, "datetime": datetime(2024, 1, 1, 10, 0)},  # 异常低
        ]
        thresholds = {"min": 60, "max": 100, "unit": "bpm"}
        
        anomalies = HealthReportService._detect_anomalies(data_points, thresholds)
        
        assert len(anomalies) == 2
        assert any(a["value"] == 120 for a in anomalies)
        assert any(a["value"] == 50 for a in anomalies)

    def test_get_period_range(self):
        """测试获取周期范围"""
        report_date = date(2024, 1, 31)
        
        # 日报告
        start, end = HealthReportService._get_period_range(report_date, ReportPeriod.DAY)
        assert (end - start).days == 1
        
        # 周报告
        start, end = HealthReportService._get_period_range(report_date, ReportPeriod.WEEK)
        assert (end - start).days == 7
        
        # 月报告
        start, end = HealthReportService._get_period_range(report_date, ReportPeriod.MONTH)
        assert (end - start).days == 30

    def test_get_health_level(self):
        """测试健康等级判断"""
        assert HealthReportService._get_health_level(95) == "excellent"
        assert HealthReportService._get_health_level(85) == "good"
        assert HealthReportService._get_health_level(70) == "fair"
        assert HealthReportService._get_health_level(50) == "poor"

    def test_evaluate_sleep_quality(self):
        """测试睡眠质量评估"""
        assert HealthReportService._evaluate_sleep_quality(8) == "good"
        assert HealthReportService._evaluate_sleep_quality(6.5) == "fair"
        assert HealthReportService._evaluate_sleep_quality(5) == "poor"
        assert HealthReportService._evaluate_sleep_quality(10.5) == "excessive"

    def test_aggregate_by_period_day(self):
        """测试按天聚合数据"""
        from datetime import datetime
        data_points = [
            {"value": 70, "datetime": datetime(2024, 1, 1, 8, 0)},
            {"value": 72, "datetime": datetime(2024, 1, 1, 12, 0)},
            {"value": 75, "datetime": datetime(2024, 1, 2, 8, 0)},
            {"value": 73, "datetime": datetime(2024, 1, 2, 12, 0)},
        ]
        
        aggregated = HealthReportService._aggregate_by_period(data_points, ReportPeriod.DAY)
        
        assert len(aggregated) == 2
        assert aggregated[0]["date"] == "2024-01-01"
        assert aggregated[0]["avg"] == 71  # (70+72)/2
        assert aggregated[0]["count"] == 2

    def test_aggregate_by_period_month(self):
        """测试按月聚合数据"""
        from datetime import datetime
        data_points = [
            {"value": 70, "datetime": datetime(2024, 1, 15)},
            {"value": 72, "datetime": datetime(2024, 1, 20)},
            {"value": 75, "datetime": datetime(2024, 2, 15)},
        ]
        
        aggregated = HealthReportService._aggregate_by_period(data_points, ReportPeriod.MONTH)
        
        assert len(aggregated) == 2
        assert aggregated[0]["month"] == "2024-01"
