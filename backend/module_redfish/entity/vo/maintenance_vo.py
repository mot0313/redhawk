"""
硬件更换排期VO模型（轻量化方案）
基于现有告警系统扩展，无需新建表
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from module_admin.annotation.pydantic_annotation import as_query


class MaintenanceScheduleModel(BaseModel):
    """维护排期基础模型（基于告警信息扩展）"""
    alert_id: Optional[int] = Field(default=None, description="告警ID")
    device_id: int = Field(..., description="设备ID")
    hostname: Optional[str] = Field(default=None, description="设备主机名")
    business_type: Optional[str] = Field(default=None, description="业务类型")
    component_type: str = Field(..., description="组件类型")
    component_name: Optional[str] = Field(default=None, description="组件名称")
    urgency_level: str = Field(..., description="紧急程度：immediate/urgent/scheduled")
    scheduled_date: Optional[datetime] = Field(default=None, description="计划处理时间")
    responsible_person: Optional[str] = Field(default=None, description="负责人")
    maintenance_type: str = Field(default="repair", description="维护类型：repair/replace/upgrade")
    status: str = Field(default="pending", description="状态：pending/in_progress/completed/cancelled")
    description: Optional[str] = Field(default=None, description="描述")
    alert_message: Optional[str] = Field(default=None, description="告警详细信息")
    first_occurrence: Optional[datetime] = Field(default=None, description="首次发生时间")
    resolved_time: Optional[datetime] = Field(default=None, description="解决时间")
    resolution_note: Optional[str] = Field(default=None, description="解决说明")
    estimated_duration: Optional[int] = Field(default=None, description="预计耗时（分钟）")


class MaintenanceScheduleQueryModel(BaseModel):
    """维护排期查询模型"""
    model_config = ConfigDict(alias_generator=to_camel)
    
    device_id: Optional[int] = Field(default=None, description="设备ID")
    hostname: Optional[str] = Field(default=None, description="主机名")
    business_ip: Optional[str] = Field(default=None, description="业务IP")
    business_type: Optional[str] = Field(default=None, description="业务类型")
    component_type: Optional[str] = Field(default=None, description="组件类型")
    urgency_level: Optional[str] = Field(default=None, description="紧急程度")
    status: Optional[str] = Field(default=None, description="状态")
    maintenance_status: Optional[str] = Field(default=None, description="维护状态（前端字段）")
    responsible_person: Optional[str] = Field(default=None, description="负责人")
    scheduled_date_start: Optional[datetime] = Field(default=None, description="计划开始时间")
    scheduled_date_end: Optional[datetime] = Field(default=None, description="计划结束时间")


@as_query
class MaintenanceSchedulePageQueryModel(MaintenanceScheduleQueryModel):
    """维护排期分页查询模型"""
    page_num: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页记录数")


class CreateMaintenanceScheduleModel(BaseModel):
    """创建维护排期模型"""
    model_config = ConfigDict(alias_generator=to_camel)
    
    device_id: int = Field(..., description="设备ID")
    component_type: str = Field(..., description="组件类型")
    component_name: Optional[str] = Field(default=None, description="组件名称")
    urgency_level: str = Field(..., description="紧急程度")
    scheduled_date: Optional[datetime] = Field(default=None, description="计划处理时间")
    responsible_person: str = Field(..., description="负责人")
    maintenance_type: str = Field(default="repair", description="维护类型")
    description: Optional[str] = Field(default=None, description="描述")
    estimated_duration: Optional[int] = Field(default=None, description="预计耗时（分钟）")


class UpdateMaintenanceScheduleModel(BaseModel):
    """更新维护排期模型"""
    model_config = ConfigDict(alias_generator=to_camel)
    
    alert_id: int = Field(..., description="告警ID")
    device_id: Optional[int] = Field(default=None, description="设备ID")
    component_type: Optional[str] = Field(default=None, description="组件类型")
    component_name: Optional[str] = Field(default=None, description="组件名称")
    urgency_level: Optional[str] = Field(default=None, description="紧急程度")
    scheduled_date: Optional[datetime] = Field(default=None, description="计划处理时间")
    responsible_person: Optional[str] = Field(default=None, description="负责人")
    status: Optional[str] = Field(default=None, description="状态")
    description: Optional[str] = Field(default=None, description="描述")
    resolution_note: Optional[str] = Field(default=None, description="处理说明")
    estimated_duration: Optional[int] = Field(default=None, description="预计耗时（分钟）")


class MaintenanceScheduleStatisticsModel(BaseModel):
    """维护排期统计模型"""
    total_schedules: int = Field(..., description="总排期数")
    pending_schedules: int = Field(..., description="待处理排期数")
    in_progress_schedules: int = Field(..., description="进行中排期数")
    completed_schedules: int = Field(..., description="已完成排期数")
    immediate_schedules: int = Field(..., description="立即处理排期数")
    urgent_schedules: int = Field(..., description="24小时内处理排期数")
    scheduled_schedules: int = Field(..., description="择期处理排期数")
    overdue_schedules: int = Field(..., description="逾期排期数")


class MaintenanceCalendarModel(BaseModel):
    """维护日历模型"""
    date: str = Field(..., description="日期（YYYY-MM-DD）")
    schedules: List[Dict[str, Any]] = Field(..., description="当天的排期列表")
    total_count: int = Field(..., description="当天排期总数")
    immediate_count: int = Field(default=0, description="立即处理数量")
    urgent_count: int = Field(default=0, description="24小时内处理数量")
    scheduled_count: int = Field(default=0, description="择期处理数量")


class MaintenanceStrategyConfigModel(BaseModel):
    """维护策略配置模型"""
    immediate_duration: int = Field(default=0, description="立即处理时长（分钟）")
    urgent_duration: int = Field(default=1440, description="24小时内处理时长（分钟）")
    maintenance_window_day: int = Field(default=6, description="维护窗口日期（0=周日，6=周六）")
    maintenance_window_start: str = Field(default="02:00", description="维护窗口开始时间")
    maintenance_window_end: str = Field(default="06:00", description="维护窗口结束时间")


class UrgencyLevelOption(BaseModel):
    """紧急程度选项模型"""
    value: str = Field(..., description="选项值")
    label: str = Field(..., description="显示标签")
    description: str = Field(..., description="描述")
    duration_minutes: int = Field(..., description="处理时长（分钟）")
    color: str = Field(..., description="显示颜色")


class MaintenanceScheduleDetailModel(BaseModel):
    """维护排期详情模型"""
    schedule: MaintenanceScheduleModel
    device_info: Optional[Dict[str, Any]] = Field(default=None, description="设备信息")
    alert_logs: Optional[List[Dict[str, Any]]] = Field(default=None, description="相关告警日志")
    maintenance_history: Optional[List[Dict[str, Any]]] = Field(default=None, description="维护历史")


class BatchUpdateScheduleModel(BaseModel):
    """批量更新排期模型"""
    model_config = ConfigDict(alias_generator=to_camel)
    
    alert_ids: List[int] = Field(..., description="告警ID列表")
    responsible_person: Optional[str] = Field(default=None, description="负责人")
    scheduled_date: Optional[datetime] = Field(default=None, description="计划处理时间")
    status: Optional[str] = Field(default=None, description="状态")


class MaintenanceReportModel(BaseModel):
    """维护报告模型"""
    period_start: datetime = Field(..., description="统计开始时间")
    period_end: datetime = Field(..., description="统计结束时间")
    total_maintenance: int = Field(..., description="总维护次数")
    completed_maintenance: int = Field(..., description="已完成维护次数")
    completion_rate: float = Field(..., description="完成率")
    avg_resolution_time: Optional[float] = Field(default=None, description="平均解决时间（小时）")
    by_urgency: Dict[str, int] = Field(..., description="按紧急程度分组统计")
    by_component: Dict[str, int] = Field(..., description="按组件类型分组统计")
    overdue_count: int = Field(..., description="逾期数量") 