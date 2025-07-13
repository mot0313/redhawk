"""
Redfish告警日志DO模型
"""
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from .base import Base


class RedfishAlertLogDO(Base):
    """Redfish告警日志表（详细日志显示用）"""
    __tablename__ = 'redfish_alert_log'
    
    log_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='日志ID')
    device_id = Column(BigInteger, ForeignKey('device_info.device_id'), nullable=False, comment='设备ID')
    alert_id = Column(BigInteger, ForeignKey('alert_info.alert_id'), comment='关联的告警ID')
    log_source = Column(String(50), default='redfish', comment='日志来源')
    component_type = Column(String(50), comment='组件类型')
    component_name = Column(String(100), comment='组件名称')
    log_level = Column(String(20), comment='日志级别')
    log_message = Column(Text, comment='日志消息')
    raw_data = Column(Text, comment='原始JSON数据')
    processed_status = Column(String(20), default='unprocessed', comment='处理状态（unprocessed未处理/processed已处理/ignored已忽略）')
    redfish_log_id = Column(String(100), comment='Redfish原始日志ID')
    log_hash = Column(String(64), comment='日志内容哈希值（用于去重）')
    occurrence_time = Column(DateTime, nullable=False, comment='发生时间')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')
    
    # 关联关系
    device = relationship("DeviceInfoDO", back_populates="logs")
    alert = relationship("AlertInfoDO", back_populates="logs") 