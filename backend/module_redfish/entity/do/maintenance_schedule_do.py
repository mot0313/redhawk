"""
硬件更换排期DO模型
"""
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class MaintenanceScheduleDO(Base):
    """硬件更换排期表"""
    __tablename__ = 'maintenance_schedule'
    
    schedule_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='排期ID')
    device_id = Column(BigInteger, ForeignKey('device_info.device_id'), nullable=False, comment='设备ID')
    component_type = Column(String(50), nullable=False, comment='组件类型')
    component_name = Column(String(100), comment='组件名称')
    component_serial = Column(String(100), comment='组件序列号')
    maintenance_type = Column(String(20), nullable=False, comment='维护类型：replace=更换，repair=维修，upgrade=升级')
    priority_level = Column(String(20), nullable=False, comment='优先级：urgent=紧急，normal=正常，deferred=择期')
    scheduled_date = Column(DateTime, nullable=False, comment='计划日期')
    estimated_duration = Column(Integer, comment='预计耗时（分钟）')
    responsible_person = Column(String(100), nullable=False, comment='负责人')
    contact_phone = Column(String(20), comment='联系电话')
    status = Column(String(20), default='pending', comment='状态：pending=待执行，in_progress=执行中，completed=已完成，cancelled=已取消')
    description = Column(Text, comment='描述')
    pre_check_result = Column(Text, comment='预检结果')
    maintenance_result = Column(Text, comment='维护结果')
    actual_start_time = Column(DateTime, comment='实际开始时间')
    actual_end_time = Column(DateTime, comment='实际结束时间')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    remarks = Column(String(500), comment='备注')
    
    # 关联关系
    device = relationship("DeviceInfoDO") 