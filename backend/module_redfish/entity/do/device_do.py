"""
设备信息DO模型
"""
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, SmallInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from .base import Base


class DeviceInfoDO(Base):
    """设备信息表"""
    __tablename__ = 'device_info'
    
    device_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='设备ID')
    hostname = Column(String(100), nullable=False, comment='主机名')
    business_ip = Column(String(45), comment='业务IP地址')
    oob_ip = Column(String(45), nullable=False, comment='带外IP地址（BMC IP）')
    oob_port = Column(Integer, default=443, comment='带外端口号')
    location = Column(String(200), nullable=False, comment='机房位置')
    operating_system = Column(String(100), comment='操作系统')
    serial_number = Column(String(100), comment='序列号')
    model = Column(String(100), comment='设备型号')
    manufacturer = Column(String(100), comment='厂商')
    technical_system = Column(String(100), comment='技术系统')
    system_owner = Column(String(100), comment='系统负责人')
    business_type = Column(String(50), comment='业务类型')
    redfish_username = Column(String(100), comment='Redfish用户名')
    redfish_password = Column(String(255), comment='Redfish密码（加密存储）')
    monitor_enabled = Column(SmallInteger, default=1, comment='是否启用监控')
    last_check_time = Column(DateTime, comment='最后检查时间')
    health_status = Column(String(20), default='unknown', comment='健康状态（ok正常/warning警告/unknown未知，critical已合并到warning）')
    create_by = Column(String(64), default='', comment='创建者')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')
    update_by = Column(String(64), default='', comment='更新者')
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    remark = Column(String(500), comment='备注')
    
    # 关联关系（注意：这里暂时用字符串引用，避免循环导入）
    alerts = relationship("AlertInfoDO", back_populates="device")
    logs = relationship("RedfishAlertLogDO", back_populates="device") 