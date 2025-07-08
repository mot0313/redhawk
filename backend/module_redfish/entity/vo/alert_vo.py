"""
告警管理VO模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from module_admin.annotation.pydantic_annotation import as_query


class AlertInfoModel(BaseModel):
    """精简版告警信息模型（专注首页展示）"""
    alert_id: Optional[int] = Field(default=None, description="告警ID")
    device_id: int = Field(..., description="设备ID")
    hostname: Optional[str] = Field(default=None, description="主机名（来自device_info表）")
    business_ip: Optional[str] = Field(default=None, description="业务IP（来自device_info表）")
    component_type: str = Field(..., description="组件类型（首页展示核心字段）")
    component_name: Optional[str] = Field(default=None, description="组件名称（首页展示）")
    health_status: str = Field(..., description="健康状态（ok/warning/critical）")
    urgency_level: str = Field(..., description="紧急程度（urgent/scheduled）")
    alert_status: str = Field(default="active", description="告警状态（active/resolved）")
    first_occurrence: datetime = Field(..., description="首次发生时间")
    last_occurrence: Optional[datetime] = Field(default=None, description="最后发生时间")
    resolved_by: Optional[str] = Field(default=None, description="解决人")
    resolved_time: Optional[datetime] = Field(default=None, description="解决时间")
    resolved_note: Optional[str] = Field(default=None, description="解决备注")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    
    # 维修时间相关字段
    scheduled_maintenance_time: Optional[datetime] = Field(default=None, description="计划维修时间")
    maintenance_description: Optional[str] = Field(default=None, description="维修描述")
    maintenance_status: Optional[str] = Field(default="none", description="维修状态（none/planned/in_progress/completed/cancelled）")
    maintenance_notes: Optional[str] = Field(default=None, description="维修备注")


class AlertQueryModel(BaseModel):
    """精简版告警查询模型"""
    model_config = ConfigDict(alias_generator=to_camel)
    
    device_id: Optional[int] = Field(default=None, description="设备ID")
    hostname: Optional[str] = Field(default=None, description="主机名")
    business_ip: Optional[str] = Field(default=None, description="业务IP")
    component_type: Optional[str] = Field(default=None, description="组件类型")
    urgency_level: Optional[str] = Field(default=None, description="紧急程度（urgent/scheduled）")
    health_status: Optional[str] = Field(default=None, description="健康状态（ok/warning/critical）")
    alert_status: Optional[str] = Field(default=None, description="告警状态（active/resolved）")
    start_time: Optional[datetime] = Field(default=None, description="开始时间")
    end_time: Optional[datetime] = Field(default=None, description="结束时间")


@as_query
class AlertPageQueryModel(AlertQueryModel):
    """告警分页查询模型"""
    page_num: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页记录数")


class AlertStatisticsModel(BaseModel):
    """告警统计模型"""
    total_alerts: int = Field(..., description="总告警数")
    urgent_alerts: int = Field(..., description="紧急告警数")
    scheduled_alerts: int = Field(..., description="择期告警数")
    active_alerts: int = Field(..., description="活跃告警数")
    resolved_alerts: int = Field(..., description="已解决告警数")
    ignored_alerts: int = Field(..., description="已忽略告警数")


class AlertTrendModel(BaseModel):
    """告警趋势模型"""
    date: str = Field(..., description="日期")
    urgent_count: int = Field(..., description="紧急告警数")
    scheduled_count: int = Field(..., description="择期告警数")
    total_count: int = Field(..., description="总告警数")


class DeviceHealthSummaryModel(BaseModel):
    """设备健康汇总模型"""
    device_id: int = Field(..., description="设备ID")
    hostname: str = Field(..., description="主机名")
    business_ip: str = Field(..., description="业务IP")
    overall_health: str = Field(..., description="整体健康状态")
    component_health: dict = Field(..., description="组件健康状态")
    alert_count: int = Field(..., description="告警数量")
    last_check_time: datetime = Field(..., description="最后检查时间")


class RealtimeAlertModel(BaseModel):
    """实时告警模型（紧急告警首页展示）"""
    device_id: int = Field(..., description="设备ID")
    hostname: str = Field(..., description="主机名")
    business_ip: Optional[str] = Field(default=None, description="业务IP")
    component_type: str = Field(..., description="组件类型")
    component_name: Optional[str] = Field(default=None, description="组件名称")
    health_status: str = Field(..., description="健康状态（ok/warning/critical）")
    urgency_level: str = Field(..., description="紧急程度（urgent）")
    first_occurrence: datetime = Field(..., description="首次发生时间")


class ScheduledAlertModel(BaseModel):
    """择期告警模型（择期告警首页展示）"""
    device_id: int = Field(..., description="设备ID")
    hostname: str = Field(..., description="主机名")
    business_ip: Optional[str] = Field(default=None, description="业务IP")
    component_type: str = Field(..., description="组件类型")
    component_name: Optional[str] = Field(default=None, description="组件名称")
    health_status: str = Field(..., description="健康状态（ok/warning/critical）")
    urgency_level: str = Field(..., description="紧急程度（scheduled）")
    first_occurrence: datetime = Field(..., description="首次发生时间")


class AlertDistributionModel(BaseModel):
    """告警分布模型"""
    byLevel: dict = Field(..., description="按级别分布")
    byComponent: dict = Field(..., description="按组件类型分布")
    byLocation: dict = Field(..., description="按位置分布")
    byManufacturer: dict = Field(..., description="按制造商分布")


class MaintenanceScheduleModel(BaseModel):
    """维修计划模型"""
    model_config = ConfigDict(alias_generator=to_camel)
    
    alert_id: int = Field(..., description="告警ID")
    scheduled_maintenance_time: datetime = Field(..., description="计划维修时间")
    maintenance_description: Optional[str] = Field(default=None, description="维修描述")
    maintenance_notes: Optional[str] = Field(default=None, description="维修备注")


class MaintenanceUpdateModel(BaseModel):
    """维修计划更新模型"""
    model_config = ConfigDict(alias_generator=to_camel)
    
    alert_id: int = Field(..., description="告警ID")
    scheduled_maintenance_time: Optional[datetime] = Field(default=None, description="计划维修时间")
    maintenance_description: Optional[str] = Field(default=None, description="维修描述")
    maintenance_status: Optional[str] = Field(default=None, description="维修状态（none/planned/in_progress/completed/cancelled）")
    maintenance_notes: Optional[str] = Field(default=None, description="维修备注")


class BatchMaintenanceUpdateModel(BaseModel):
    """批量维修计划更新模型"""
    model_config = ConfigDict(alias_generator=to_camel)
    
    alert_ids: List[int] = Field(..., description="告警ID列表")
    scheduled_maintenance_time: Optional[datetime] = Field(default=None, description="计划维修时间")
    maintenance_description: Optional[str] = Field(default=None, description="维修描述")
    maintenance_status: Optional[str] = Field(default=None, description="维修状态（none/planned/in_progress/completed/cancelled）")
    maintenance_notes: Optional[str] = Field(default=None, description="维修备注")


class MaintenanceQueryModel(BaseModel):
    """维修计划查询模型"""
    model_config = ConfigDict(alias_generator=to_camel)
    
    device_id: Optional[int] = Field(default=None, description="设备ID")
    maintenance_status: Optional[str] = Field(default=None, description="维修状态")
    scheduled_start_time: Optional[datetime] = Field(default=None, description="计划开始时间范围")
    scheduled_end_time: Optional[datetime] = Field(default=None, description="计划结束时间范围")


@as_query
class MaintenancePageQueryModel(MaintenanceQueryModel):
    """维修计划分页查询模型"""
    page_num: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页记录数")


 