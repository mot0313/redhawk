"""
告警信息DO模型
"""
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, SmallInteger, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from .base import Base


class AlertInfoDO(Base):
    """精简版告警信息表（专注首页展示）"""
    __tablename__ = 'alert_info'
    
    alert_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='告警ID（主键）')
    device_id = Column(BigInteger, ForeignKey('device_info.device_id'), nullable=False, comment='设备ID（外键关联device_info）')
    component_type = Column(String(50), nullable=False, comment='组件类型（如：CPU/Memory/Storage/Fan/Power/Temperature）')
    component_name = Column(String(100), comment='组件名称（如：CPU1/Memory_DIMM_A1/Fan1）')
    health_status = Column(String(20), nullable=False, comment='健康状态（ok正常/warning警告/unknown未知，critical已合并到warning）')
    urgency_level = Column(String(20), nullable=False, comment='紧急程度（urgent紧急告警/scheduled择期告警）')
    alert_status = Column(String(20), default='active', comment='告警状态（active活跃告警/resolved已解决告警）')
    first_occurrence = Column(DateTime, nullable=False, comment='首次发生时间')
    last_occurrence = Column(DateTime, comment='最后发生时间')
    resolved_time = Column(DateTime, comment='解决时间')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    # 维修时间相关字段
    scheduled_maintenance_time = Column(DateTime, comment='计划维修时间')
    maintenance_description = Column(Text, comment='维修描述')
    maintenance_status = Column(String(20), default='none', comment='维修状态（none/planned/in_progress/completed/cancelled）')
    maintenance_notes = Column(Text, comment='维修备注')

    # 定义索引
    __table_args__ = (
        Index('ix_alert_info_lifecycle', 'device_id', 'component_type', 'component_name', 'alert_status'),
        Index('ix_alert_info_display', 'alert_status', 'urgency_level', 'last_occurrence'),
        Index('ix_alert_info_first_occurrence', 'first_occurrence'),
    )
    
    # 向后兼容的字段映射（为了兼容现有代码）
    @property
    def alert_level(self):
        """向后兼容：映射health_status到alert_level"""
        return self.health_status
    
    @alert_level.setter
    def alert_level(self, value):
        """向后兼容：设置alert_level时更新health_status"""
        self.health_status = value
    
    @property
    def alert_type(self):
        """向后兼容：映射urgency_level到alert_type"""
        return self.urgency_level
    
    @alert_type.setter
    def alert_type(self, value):
        """向后兼容：设置alert_type时更新urgency_level"""
        self.urgency_level = value
    
    # 关联关系
    device = relationship("DeviceInfoDO", back_populates="alerts") 