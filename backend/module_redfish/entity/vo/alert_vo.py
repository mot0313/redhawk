"""
告警管理VO模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from module_admin.annotation.pydantic_annotation import as_query


class AlertInfoModel(BaseModel):
    """告警信息模型"""
    alert_id: Optional[int] = Field(default=None, description="告警ID")
    device_id: int = Field(..., description="设备ID")
    hostname: str = Field(..., description="主机名")
    business_ip: str = Field(..., description="业务IP")
    component_type: str = Field(..., description="组件类型")
    component_name: str = Field(..., description="组件名称")
    alert_level: str = Field(..., description="告警级别(urgent/scheduled)")
    health_status: str = Field(..., description="健康状态")
    alert_message: str = Field(..., description="告警消息")
    first_occurrence: datetime = Field(..., description="首次发生时间")
    last_occurrence: datetime = Field(..., description="最后发生时间")
    occurrence_count: int = Field(default=1, description="发生次数")
    is_manual_override: bool = Field(default=False, description="是否手动覆盖")
    manual_level: Optional[str] = Field(default=None, description="手动设置级别")
    manual_reason: Optional[str] = Field(default=None, description="手动设置原因")
    manual_operator: Optional[str] = Field(default=None, description="手动操作人")
    manual_time: Optional[datetime] = Field(default=None, description="手动操作时间")
    alert_status: str = Field(default="active", description="状态(active/resolved/ignored)")
    resolved_by: Optional[str] = Field(default=None, description="解决人")
    resolved_time: Optional[datetime] = Field(default=None, description="解决时间")
    resolved_note: Optional[str] = Field(default=None, description="解决备注")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")


class AlertQueryModel(BaseModel):
    """告警查询模型"""
    model_config = ConfigDict(alias_generator=to_camel)
    
    device_id: Optional[int] = Field(default=None, description="设备ID")
    hostname: Optional[str] = Field(default=None, description="主机名")
    business_ip: Optional[str] = Field(default=None, description="业务IP")
    component_type: Optional[str] = Field(default=None, description="组件类型")
    alert_level: Optional[str] = Field(default=None, description="告警级别")
    health_status: Optional[str] = Field(default=None, description="健康状态")
    alert_status: Optional[str] = Field(default=None, description="状态")
    start_time: Optional[datetime] = Field(default=None, description="开始时间")
    end_time: Optional[datetime] = Field(default=None, description="结束时间")


@as_query
class AlertPageQueryModel(AlertQueryModel):
    """告警分页查询模型"""
    page_num: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页记录数")


class AlertManualOverrideModel(BaseModel):
    """告警手动覆盖模型"""
    alert_id: int = Field(..., description="告警ID")
    manual_level: str = Field(..., description="手动设置级别(urgent/scheduled)")
    manual_reason: str = Field(..., description="手动设置原因")
    manual_operator: str = Field(..., description="手动操作人")
    manual_time: datetime = Field(..., description="手动操作时间")


class AlertResolveModel(BaseModel):
    """告警解决模型"""
    alert_ids: str = Field(..., description="告警ID列表，逗号分隔")
    resolved_by: str = Field(..., description="解决人")
    resolved_time: datetime = Field(..., description="解决时间")
    resolved_note: Optional[str] = Field(default=None, description="解决备注")


class AlertIgnoreModel(BaseModel):
    """告警忽略模型"""
    alert_ids: str = Field(..., description="告警ID列表，逗号分隔")
    operator: str = Field(..., description="操作人")
    operation_time: datetime = Field(..., description="操作时间")
    ignore_reason: Optional[str] = Field(default=None, description="忽略原因")


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
    """实时告警模型"""
    device_id: int = Field(..., description="设备ID")
    hostname: str = Field(..., description="主机名")
    business_ip: str = Field(..., description="业务IP")
    component_type: str = Field(..., description="组件类型")
    component_name: str = Field(..., description="组件名称")
    health_status: str = Field(..., description="健康状态")
    alert_level: str = Field(..., description="告警级别")
    last_occurrence: datetime = Field(..., description="最后发生时间")


class ScheduledAlertModel(BaseModel):
    """择期告警模型"""
    device_id: int = Field(..., description="设备ID")
    hostname: str = Field(..., description="主机名")
    business_ip: str = Field(..., description="业务IP")
    component_type: str = Field(..., description="组件类型")
    component_name: str = Field(..., description="组件名称")
    health_status: str = Field(..., description="健康状态")
    alert_message: str = Field(..., description="告警消息")
    first_occurrence: datetime = Field(..., description="首次发生时间")
    occurrence_count: int = Field(..., description="发生次数")


class AlertDistributionModel(BaseModel):
    """告警分布模型"""
    by_level: dict = Field(..., description="按级别分布")
    by_component: dict = Field(..., description="按组件类型分布")
    by_location: dict = Field(..., description="按位置分布")
    by_manufacturer: dict = Field(..., description="按制造商分布") 