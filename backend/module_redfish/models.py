"""
Redfish模块数据库模型
"""
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, SmallInteger, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class DeviceInfo(Base):
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
    
    # 关联关系
    alerts = relationship("AlertInfo", back_populates="device")
    logs = relationship("RedfishAlertLog", back_populates="device")


class AlertInfo(Base):
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
    device = relationship("DeviceInfo", back_populates="alerts")
    logs = relationship("RedfishAlertLog", back_populates="alert")


class RedfishAlertLog(Base):
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
    device = relationship("DeviceInfo", back_populates="logs")
    alert = relationship("AlertInfo", back_populates="logs")


class BusinessHardwareUrgencyRules(Base):
    """业务硬件紧急度规则表"""
    __tablename__ = 'business_hardware_urgency_rules'
    
    rule_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='规则ID')
    business_type = Column(String(50), nullable=False, comment='业务类型')
    hardware_type = Column(String(50), nullable=False, comment='硬件类型')
    urgency_level = Column(String(20), nullable=False, comment='紧急程度')
    description = Column(String(200), comment='规则描述')
    is_active = Column(SmallInteger, default=1, comment='是否启用')
    create_by = Column(String(64), default='', comment='创建者')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')
    update_by = Column(String(64), default='', comment='更新者')
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')


class DutyPerson(Base):
    """值班人员表"""
    __tablename__ = 'duty_person'
    
    person_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='人员ID')
    person_name = Column(String(100), nullable=False, comment='姓名')
    department = Column(String(100), comment='部门')
    position = Column(String(100), comment='职位')
    phone = Column(String(20), comment='手机号')
    email = Column(String(100), comment='邮箱')
    status = Column(String(2), default='1', comment='状态：0=停用，1=正常')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    remarks = Column(String(500), comment='备注')
    
    # 关联关系
    schedules = relationship("DutySchedule", back_populates="person")


class DutySchedule(Base):
    """值班排期表"""
    __tablename__ = 'duty_schedule'
    
    schedule_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='排期ID')
    person_id = Column(BigInteger, ForeignKey('duty_person.person_id'), nullable=False, comment='人员ID')
    duty_date = Column(DateTime, nullable=False, comment='值班日期')
    duty_type = Column(String(20), default='primary', comment='值班类型：primary=主值班，backup=备值班，emergency=应急值班')
    shift_type = Column(String(20), nullable=False, comment='班次类型：day=白班，night=夜班，all=全天')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    remarks = Column(String(500), comment='备注')
    
    # 关联关系
    person = relationship("DutyPerson", back_populates="schedules")


class MaintenanceSchedule(Base):
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
    device = relationship("DeviceInfo")


class BusinessTypeDict(Base):
    """业务类型字典表"""
    __tablename__ = 'business_type_dict'
    
    type_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='类型ID')
    type_code = Column(String(50), nullable=False, unique=True, comment='类型编码')
    type_name = Column(String(100), nullable=False, comment='类型名称')
    type_description = Column(String(200), comment='类型描述')
    sort_order = Column(Integer, default=0, comment='排序顺序')
    is_active = Column(SmallInteger, default=1, comment='是否启用')
    create_by = Column(String(64), default='', comment='创建者')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')
    update_by = Column(String(64), default='', comment='更新者')
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')


class HardwareTypeDict(Base):
    """硬件类型字典表"""
    __tablename__ = 'hardware_type_dict'
    
    type_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='类型ID')
    type_code = Column(String(50), nullable=False, unique=True, comment='类型编码')
    type_name = Column(String(100), nullable=False, comment='类型名称')
    type_description = Column(String(200), comment='类型描述')
    category = Column(String(50), comment='硬件分类')
    sort_order = Column(Integer, default=0, comment='排序顺序')
    is_active = Column(SmallInteger, default=1, comment='是否启用')
    create_by = Column(String(64), default='', comment='创建者')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')
    update_by = Column(String(64), default='', comment='更新者')
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间') 