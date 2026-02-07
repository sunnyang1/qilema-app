"""
120急救中心对接服务

实现一键拨打120、位置发送、健康档案摘要、救护车追踪等核心功能
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
import json
import requests

from app.models.emergency_center_model import (
    EmergencyCenter, EmergencyCall, Ambulance, RescueRecord,
    EmergencyCallStatus, AmbulanceStatus
)
from app.models.user import User
from app.models.sos_request import SOSRequest
from app.models.emergency_contact import EmergencyContact
from app.models.health_record import HealthRecord
from app.models.device_data import DeviceData
from app.models.device import Device
from app.models.anomaly import Anomaly
from app.schemas.emergency_center import (
    EmergencyCenterCreate, EmergencyCenterUpdate,
    EmergencyCallCreate, EmergencyCallUpdate,
    AmbulanceCreate, AmbulanceUpdate, AmbulanceLocation,
    RescueRecordCreate, RescueRecordUpdate,
    Call120Request, Call120Response,
    HealthSummary, AmbulanceTracking
)
from app.services.location_service import LocationService
from app.services.health_record_service import HealthRecordService


class EmergencyCenterService:
    """120急救中心对接服务"""
    
    def __init__(self):
        self.location_service = LocationService()
        self.health_record_service = HealthRecordService()
    
    # ========== 120一键拨打 ==========
    
    def call_120(self, db: Session, request: Call120Request) -> Call120Response:
        """
        一键拨打120
        
        创建急救呼叫记录,拨打120电话,发送位置和健康档案
        """
        # 查找用户所在城市的急救中心
        emergency_center = self._find_nearest_emergency_center(db, request.caller_location)
        
        # 创建急救呼叫记录
        call_data = EmergencyCallCreate(
            user_id=request.user_id,
            sos_request_id=request.sos_request_id,
            emergency_center_id=emergency_center.id if emergency_center else None,
            caller_location=request.caller_location
        )
        
        call = EmergencyCall(**call_data.dict())
        db.add(call)
        db.commit()
        db.refresh(call)
        
        # 发送位置信息
        location_sent = self._send_location_to_120(db, call, emergency_center)
        
        # 发送健康档案摘要
        health_summary_sent = False
        if request.send_health_summary:
            health_summary_sent = self._send_health_summary_to_120(db, call, request.user_id)
        
        # 模拟拨打120电话
        is_successful = self._dial_120_phone(db, call, emergency_center)
        
        db.commit()
        db.refresh(call)
        
        return Call120Response(
            call_id=call.id,
            call_status=call.call_status,
            dialed_at=call.dialed_at,
            emergency_center_id=call.emergency_center_id,
            emergency_center_name=emergency_center.center_name if emergency_center else None,
            emergency_phone=emergency_center.emergency_phone if emergency_center else "120",
            location_sent=location_sent,
            health_summary_sent=health_summary_sent,
            ambulance_dispatched=None  # 需要从急救中心查询
        )
    
    def _find_nearest_emergency_center(self, db: Session, location: str) -> Optional[EmergencyCenter]:
        """
        查找最近的急救中心
        
        基于用户位置查找附近的急救中心
        """
        # 解析位置
        try:
            lat, lon = map(float, location.split(','))
        except:
            return None
        
        # 查询所有启用的急救中心
        centers = db.query(EmergencyCenter).filter(
            EmergencyCenter.is_active == True
        ).all()
        
        # 计算距离并找出最近的
        nearest_center = None
        min_distance = float('inf')
        
        for center in centers:
            # 这里应该有坐标字段,简化处理,直接返回第一个
            nearest_center = center
            break
        
        return nearest_center
    
    def _dial_120_phone(self, db: Session, call: EmergencyCall, emergency_center: Optional[EmergencyCenter]) -> bool:
        """
        模拟拨打120电话
        
        实际应该通过VoIP或调用第三方拨号服务
        """
        # 模拟拨打成功
        call.call_status = EmergencyCallStatus.CONNECTED
        call.connected_at = datetime.utcnow()
        call.is_successful = True
        
        # 记录通话时长(模拟)
        call.duration_seconds = 120  # 2分钟
        
        return True
    
    def _send_location_to_120(self, db: Session, call: EmergencyCall, emergency_center: Optional[EmergencyCenter]) -> bool:
        """
        发送位置信息到120
        
        解析坐标并发送给急救中心
        """
        try:
            lat, lon = map(float, call.caller_location.split(','))
            
            # 逆向地理编码获取地址
            address = self.location_service.reverse_geocode(lat, lon)
            
            # 更新呼叫记录
            call.address_sent = address
            call.location_sent_at = datetime.utcnow()
            
            # 如果急救中心支持API,实际应该调用接口
            # self._call_emergency_center_api(emergency_center, "send_location", {...})
            
            return True
        except:
            return False
    
    def _send_health_summary_to_120(self, db: Session, call: EmergencyCall, user_id: str) -> bool:
        """
        发送健康档案摘要到120

        生成用户健康档案摘要并发送给急救中心
        """
        try:
            # 生成健康档案摘要
            health_summary = self.generate_health_summary(db, user_id)

            # 更新呼叫记录
            call.health_summary_sent = 1
            call.health_summary_content = json.dumps(health_summary.model_dump(mode='json'), ensure_ascii=False)
            call.health_summary_sent_at = datetime.utcnow()

            # 如果急救中心支持API,实际应该调用接口
            # self._call_emergency_center_api(emergency_center, "send_health_summary", {...})

            return True
        except Exception as e:
            print(f"发送健康档案摘要失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_health_summary(self, db: Session, user_id: str) -> HealthSummary:
        """
        生成健康档案摘要
        
        汇总用户基本信息、健康档案、设备数据、异常记录等
        """
        # 获取用户信息
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        # 计算年龄
        age = None
        if user.birth_date:
            age = (datetime.utcnow().date() - user.birth_date.date()).days // 365
        
        # 获取健康档案
        health_record = db.query(HealthRecord).filter(
            HealthRecord.user_id == user_id
        ).first()
        
        # 获取紧急联系人
        emergency_contacts = db.query(EmergencyContact).filter(
            EmergencyContact.user_id == user_id
        ).all()
        
        # 获取最新的设备数据
        latest_device_data = db.query(DeviceData).join(Device).filter(
            Device.user_id == user_id
        ).order_by(DeviceData.data_timestamp.desc()).first()
        
        # 获取最近的异常记录
        recent_anomalies = db.query(Anomaly).filter(
            Anomaly.user_id == user_id,
            Anomaly.detected_at >= datetime.utcnow() - timedelta(days=7)
        ).order_by(desc(Anomaly.detected_at)).limit(5).all()
        
        # 构建健康档案摘要
        summary = HealthSummary(
            user_id=user_id,
            user_name=user.nickname,
            age=age,
            blood_type=user.blood_type.value if user.blood_type else None,
            chronic_diseases=json.loads(health_record.chronic_diseases_json) if health_record and health_record.chronic_diseases_json else None,
            allergies=json.loads(health_record.allergies_json) if health_record and health_record.allergies_json else None,
            current_medications=json.loads(health_record.current_medications_json) if health_record and health_record.current_medications_json else None,
            latest_heart_rate=latest_device_data.heart_rate if latest_device_data else None,
            latest_blood_pressure=f"{latest_device_data.systolic_pressure}/{latest_device_data.diastolic_pressure}" if latest_device_data and latest_device_data.systolic_pressure else None,
            latest_blood_oxygen=latest_device_data.blood_oxygen if latest_device_data else None,
            emergency_contacts=[ec.to_dict() for ec in emergency_contacts],
            recent_anomalies=[a.to_dict() for a in recent_anomalies],
            generated_at=datetime.utcnow()
        )
        
        return summary
    
    # ========== 救护车管理 ==========
    
    def dispatch_ambulance(self, db: Session, emergency_call_id: int) -> Ambulance:
        """
        派出救护车
        
        创建救护车记录并标记为已派出
        """
        call = db.query(EmergencyCall).filter(EmergencyCall.id == emergency_call_id).first()
        if not call:
            raise ValueError("急救呼叫记录不存在")
        
        # 创建救护车记录
        ambulance_data = AmbulanceCreate(
            emergency_call_id=emergency_call_id,
            ambulance_number=f"AMB-{emergency_call_id:06d}",
            ambulance_type="急救型"
        )
        
        ambulance = Ambulance(**ambulance_data.dict())
        ambulance.status = AmbulanceStatus.ON_ROUTE
        ambulance.dispatched_at = datetime.utcnow()
        ambulance.eta_minutes = 15  # 默认15分钟
        
        db.add(ambulance)
        db.commit()
        db.refresh(ambulance)
        
        return ambulance
    
    def update_ambulance_location(self, db: Session, location_data: AmbulanceLocation) -> Ambulance:
        """
        更新救护车位置
        
        接收救护车位置更新并保存
        """
        ambulance = db.query(Ambulance).filter(Ambulance.id == location_data.ambulance_id).first()
        if not ambulance:
            raise ValueError("救护车不存在")
        
        # 更新位置
        ambulance.current_latitude = location_data.latitude
        ambulance.current_longitude = location_data.longitude
        ambulance.current_address = location_data.address
        ambulance.location_updated_at = location_data.timestamp
        
        db.commit()
        db.refresh(ambulance)
        
        return ambulance
    
    def track_ambulance(self, db: Session, emergency_call_id: int) -> AmbulanceTracking:
        """
        追踪救护车
        
        获取救护车的实时位置和状态
        """
        ambulance = db.query(Ambulance).filter(
            Ambulance.emergency_call_id == emergency_call_id
        ).first()
        
        if not ambulance:
            raise ValueError("救护车不存在")
        
        # 计算距离(简化处理)
        # 实际应该根据起点和终点计算
        
        return AmbulanceTracking(
            ambulance_id=ambulance.id,
            ambulance_number=ambulance.ambulance_number,
            status=ambulance.status,
            current_location={
                "latitude": ambulance.current_latitude,
                "longitude": ambulance.current_longitude
            },
            current_address=ambulance.current_address,
            eta_minutes=ambulance.eta_minutes,
            contact_phone=ambulance.contact_phone,
            location_updated_at=ambulance.location_updated_at
        )
    
    # ========== 救援记录管理 ==========
    
    def create_rescue_record(self, db: Session, record_data: RescueRecordCreate) -> RescueRecord:
        """创建救援记录"""
        record = RescueRecord(**record_data.dict())
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    def update_rescue_record(self, db: Session, record_id: int, update_data: RescueRecordUpdate) -> Optional[RescueRecord]:
        """更新救援记录"""
        record = db.query(RescueRecord).filter(RescueRecord.id == record_id).first()
        if not record:
            return None
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(record, field, value)
        
        # 计算响应时间
        if update_data.arrival_time and record.alarm_time:
            record.response_time_minutes = int((update_data.arrival_time - record.alarm_time).total_seconds() / 60)
        
        # 计算总时长
        if update_data.completion_time and record.incident_time:
            record.overall_duration_minutes = int((update_data.completion_time - record.incident_time).total_seconds() / 60)
        
        db.commit()
        db.refresh(record)
        return record
    
    # ========== 急救中心管理 ==========
    
    def create_emergency_center(self, db: Session, center_data: EmergencyCenterCreate) -> EmergencyCenter:
        """创建急救中心"""
        center = EmergencyCenter(**center_data.dict())
        db.add(center)
        db.commit()
        db.refresh(center)
        return center
    
    def get_emergency_centers(self, db: Session, active_only: bool = True) -> List[EmergencyCenter]:
        """获取急救中心列表"""
        query = db.query(EmergencyCenter)
        
        if active_only:
            query = query.filter(EmergencyCenter.is_active == True)
        
        return query.order_by(EmergencyCenter.created_at.desc()).all()
    
    def get_emergency_call(self, db: Session, call_id: int) -> Optional[EmergencyCall]:
        """获取急救呼叫记录"""
        return db.query(EmergencyCall).filter(EmergencyCall.id == call_id).first()
    
    def get_user_emergency_calls(self, db: Session, user_id: str, limit: int = 10) -> List[EmergencyCall]:
        """获取用户的急救呼叫记录"""
        return db.query(EmergencyCall).filter(
            EmergencyCall.user_id == user_id
        ).order_by(desc(EmergencyCall.dialed_at)).limit(limit).all()
    
    # ========== 辅助方法 ==========
    
    def _call_emergency_center_api(self, emergency_center: EmergencyCenter, method: str, data: dict):
        """
        调用急救中心API
        
        实际应该调用急救中心提供的API接口
        """
        # 示例实现
        if not emergency_center.api_endpoint or not emergency_center.api_key:
            return None
        
        url = f"{emergency_center.api_endpoint}/{method}"
        headers = {
            "Authorization": f"Bearer {emergency_center.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=10)
            return response.json()
        except:
            return None