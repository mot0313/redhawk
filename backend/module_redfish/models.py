"""
Redfish模块数据库模型
"""
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, SmallInteger, ForeignKey
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
    health_status = Column(String(20), default='unknown', comment='健康状态')
    create_by = Column(String(64), default='', comment='创建者')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')
    update_by = Column(String(64), default='', comment='更新者')
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    remark = Column(String(500), comment='备注')
    
    # 关联关系
    alerts = relationship("AlertInfo", back_populates="device")
    logs = relationship("RedfishAlertLog", back_populates="device")


class AlertInfo(Base):
    """告警信息表（首页显示用）"""
    __tablename__ = 'alert_info'
    
    alert_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='告警ID')
    device_id = Column(BigInteger, ForeignKey('device_info.device_id'), nullable=False, comment='设备ID')
    alert_source = Column(String(50), nullable=False, comment='告警来源')
    component_type = Column(String(50), nullable=False, comment='组件类型')
    component_name = Column(String(100), comment='组件名称')
    alert_level = Column(String(20), nullable=False, comment='告警级别')
    alert_type = Column(String(20), nullable=False, comment='告警类型')
    alert_type_original = Column(String(20), comment='原始告警类型')
    alert_message = Column(Text, comment='告警详细信息')
    alert_status = Column(String(20), default='active', comment='告警状态')
    first_occurrence = Column(DateTime, nullable=False, comment='首次发生时间')
    last_occurrence = Column(DateTime, comment='最后发生时间')
    occurrence_count = Column(Integer, default=1, comment='发生次数')
    acknowledged_time = Column(DateTime, comment='确认时间')
    resolved_time = Column(DateTime, comment='解决时间')
    resolution_note = Column(Text, comment='解决说明')
    auto_resolved = Column(SmallInteger, default=0, comment='是否自动解决')
    notification_sent = Column(SmallInteger, default=0, comment='是否已发送通知')
    is_manual_override = Column(SmallInteger, default=0, comment='是否手动覆盖')
    override_reason = Column(String(500), comment='覆盖原因')
    override_by = Column(String(64), comment='覆盖操作人')
    override_time = Column(DateTime, comment='覆盖时间')
    raw_data = Column(Text, comment='原始数据')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
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