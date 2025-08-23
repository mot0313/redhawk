"""
Redfish日志数据对象(DO)
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from module_redfish.entity.do.base import Base
import uuid


class RedfishLogDO(Base):
    """
    Redfish日志数据对象
    轻量版设计：只存储Critical和Warning级别的日志，保存30天
    """
    __tablename__ = 'redfish_log'
    
    # 主键
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment='日志ID')
    
    # 设备信息
    device_id = Column(Integer, nullable=False, comment='设备ID')
    device_ip = Column(String(45), nullable=False, comment='设备IP地址')
    
    # 日志基本信息
    entry_id = Column(String(100), comment='原始条目ID')
    entry_type = Column(String(50), comment='条目类型')
    log_source = Column(String(10), nullable=False, comment='日志来源(SEL/MEL)')
    
    # 严重程度 - 只存储Critical和Warning
    severity = Column(String(20), nullable=False, comment='严重程度(CRITICAL/WARNING)')
    
    # 时间信息
    created_time = Column(DateTime, nullable=False, comment='日志创建时间')
    collected_time = Column(DateTime, nullable=False, default=datetime.now, comment='日志收集时间')
    
    # 消息内容
    message = Column(Text, comment='日志消息')
    
    # 传感器信息字段已删除（不再使用）
    
    # 系统字段
    create_by = Column(String(50), comment='创建者')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_by = Column(String(50), comment='更新者')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(Text, comment='备注')
    
    # 创建索引以提高查询性能
    __table_args__ = (
        Index('idx_redfish_log_device_id', 'device_id'),
        Index('idx_redfish_log_device_ip', 'device_ip'),
        Index('idx_redfish_log_severity', 'severity'),
        Index('idx_redfish_log_created_time', 'created_time'),
        Index('idx_redfish_log_collected_time', 'collected_time'),
        Index('idx_redfish_log_source', 'log_source'),
        Index('idx_redfish_log_device_time', 'device_id', 'created_time'),
        {'comment': 'Redfish设备日志表'}
    )
    
    def __repr__(self):
        return f"<RedfishLogDO(log_id={self.log_id}, device_id={self.device_id}, severity={self.severity}, message={self.message[:50]}...)>"
