"""
设备管理VO模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from module_admin.annotation.pydantic_annotation import as_query


class DeviceModel(BaseModel):
    """设备基础模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    device_id: Optional[int] = Field(default=None, description="设备ID")
    hostname: str = Field(..., description="主机名")
    business_ip: Optional[str] = Field(default=None, description="业务IP地址")
    oob_ip: str = Field(..., description="带外IP地址（BMC IP）")
    oob_port: int = Field(default=443, description="带外端口号")
    location: str = Field(..., description="机房位置")
    operating_system: Optional[str] = Field(default=None, description="操作系统")
    serial_number: Optional[str] = Field(default=None, description="序列号")
    model: Optional[str] = Field(default=None, description="设备型号")
    manufacturer: Optional[str] = Field(default=None, description="厂商")
    technical_system: Optional[str] = Field(default=None, description="技术系统")
    system_owner: Optional[str] = Field(default=None, description="系统负责人")
    business_type: Optional[str] = Field(default=None, description="业务类型")
    redfish_username: Optional[str] = Field(default=None, description="Redfish用户名")
    redfish_password: Optional[str] = Field(default=None, description="Redfish密码（加密存储）")
    monitor_enabled: int = Field(default=1, description="是否启用监控")
    last_check_time: Optional[datetime] = Field(default=None, description="最后检查时间")
    health_status: str = Field(default="unknown", description="健康状态")
    create_by: Optional[str] = Field(default="", description="创建者")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_by: Optional[str] = Field(default="", description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    remark: Optional[str] = Field(default=None, description="备注")


class AddDeviceModel(BaseModel):
    """添加设备模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    hostname: str = Field(..., description="主机名")
    business_ip: Optional[str] = Field(default=None, description="业务IP地址")
    oob_ip: str = Field(..., description="带外IP地址（BMC IP）")
    oob_port: int = Field(default=443, description="带外端口号")
    location: str = Field(..., description="机房位置")
    operating_system: Optional[str] = Field(default=None, description="操作系统")
    serial_number: Optional[str] = Field(default=None, description="序列号")
    model: Optional[str] = Field(default=None, description="设备型号")
    manufacturer: Optional[str] = Field(default=None, description="厂商")
    technical_system: Optional[str] = Field(default=None, description="技术系统")
    system_owner: Optional[str] = Field(default=None, description="系统负责人")
    business_type: Optional[str] = Field(default=None, description="业务类型")
    redfish_username: Optional[str] = Field(default=None, description="Redfish用户名")
    redfish_password: Optional[str] = Field(default=None, description="Redfish密码（加密存储）")
    monitor_enabled: int = Field(default=1, description="是否启用监控")
    health_status: str = Field(default="unknown", description="健康状态")
    remark: Optional[str] = Field(default=None, description="备注")
    create_by: Optional[str] = Field(default="", description="创建者")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")


class EditDeviceModel(BaseModel):
    """编辑设备模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    device_id: int = Field(..., description="设备ID")
    hostname: Optional[str] = Field(default=None, description="主机名")
    business_ip: Optional[str] = Field(default=None, description="业务IP地址")
    oob_ip: Optional[str] = Field(default=None, description="带外IP地址（BMC IP）")
    oob_port: Optional[int] = Field(default=None, description="带外端口号")
    location: Optional[str] = Field(default=None, description="机房位置")
    operating_system: Optional[str] = Field(default=None, description="操作系统")
    serial_number: Optional[str] = Field(default=None, description="序列号")
    model: Optional[str] = Field(default=None, description="设备型号")
    manufacturer: Optional[str] = Field(default=None, description="厂商")
    technical_system: Optional[str] = Field(default=None, description="技术系统")
    system_owner: Optional[str] = Field(default=None, description="系统负责人")
    business_type: Optional[str] = Field(default=None, description="业务类型")
    redfish_username: Optional[str] = Field(default=None, description="Redfish用户名")
    redfish_password: Optional[str] = Field(default=None, description="Redfish密码（加密存储）")
    monitor_enabled: Optional[int] = Field(default=None, description="是否启用监控")
    health_status: Optional[str] = Field(default=None, description="健康状态")
    remark: Optional[str] = Field(default=None, description="备注")
    update_by: Optional[str] = Field(default="", description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")


class DeleteDeviceModel(BaseModel):
    """删除设备模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    device_ids: str = Field(..., description="设备ID列表，逗号分隔")
    update_by: Optional[str] = Field(default="", description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")


class DeviceQueryModel(BaseModel):
    """设备查询模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    hostname: Optional[str] = Field(default=None, description="主机名")
    business_ip: Optional[str] = Field(default=None, description="业务IP地址")
    oob_ip: Optional[str] = Field(default=None, description="带外IP地址")
    location: Optional[str] = Field(default=None, description="机房位置")
    operating_system: Optional[str] = Field(default=None, description="操作系统")
    manufacturer: Optional[str] = Field(default=None, description="厂商")
    technical_system: Optional[str] = Field(default=None, description="技术系统")
    system_owner: Optional[str] = Field(default=None, description="系统负责人")
    business_type: Optional[str] = Field(default=None, description="业务类型")
    monitor_enabled: Optional[int] = Field(default=None, description="是否启用监控")
    health_status: Optional[str] = Field(default=None, description="健康状态")


@as_query
class DevicePageQueryModel(DeviceQueryModel):
    """设备分页查询模型"""
    page_num: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页记录数")


class DeviceDetailModel(BaseModel):
    """设备详情模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    device: DeviceModel
    health_status: Optional[str] = Field(default=None, description="健康状态")
    last_check_time: Optional[datetime] = Field(default=None, description="最后检查时间")
    connection_status: Optional[str] = Field(default=None, description="连接状态")


class DeviceHealthModel(BaseModel):
    """设备健康状态模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    device_id: int = Field(..., description="设备ID")
    hostname: str = Field(..., description="主机名")
    business_ip: Optional[str] = Field(default=None, description="业务IP地址")
    oob_ip: str = Field(..., description="带外IP地址")
    health_status: str = Field(..., description="健康状态")
    power_state: Optional[str] = Field(default=None, description="电源状态")
    processor_health: Optional[str] = Field(default=None, description="处理器健康状态")
    memory_health: Optional[str] = Field(default=None, description="内存健康状态")
    storage_health: Optional[str] = Field(default=None, description="存储健康状态")
    thermal_health: Optional[str] = Field(default=None, description="温度健康状态")
    power_health: Optional[str] = Field(default=None, description="电源健康状态")
    last_check_time: Optional[datetime] = Field(default=None, description="最后检查时间")


class DeviceTestConnectionModel(BaseModel):
    """设备连接测试模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    oob_ip: str = Field(..., description="带外IP地址")
    oob_port: int = Field(default=443, description="带外端口号")
    redfish_username: str = Field(..., description="Redfish用户名")
    redfish_password: str = Field(..., description="Redfish密码")


class DeviceConnectionResult(BaseModel):
    """设备连接测试结果"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    success: bool = Field(..., description="连接是否成功")
    message: str = Field(..., description="连接结果消息")
    system_info: Optional[dict] = Field(default=None, description="系统信息")


class DeviceResponseModel(BaseModel):
    """设备响应模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    device_id: int = Field(..., description="设备ID")
    hostname: str = Field(..., description="主机名")
    business_ip: Optional[str] = Field(default=None, description="业务IP地址")
    oob_ip: str = Field(..., description="带外IP地址")
    location: str = Field(..., description="机房位置")
    operating_system: Optional[str] = Field(default=None, description="操作系统")
    manufacturer: Optional[str] = Field(default=None, description="厂商")
    technical_system: Optional[str] = Field(default=None, description="技术系统")
    system_owner: Optional[str] = Field(default=None, description="系统负责人")
    business_type: Optional[str] = Field(default=None, description="业务类型")
    monitor_enabled: int = Field(..., description="是否启用监控")
    health_status: str = Field(..., description="健康状态")
    last_check_time: Optional[datetime] = Field(default=None, description="最后检查时间")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    remark: Optional[str] = Field(default=None, description="备注")