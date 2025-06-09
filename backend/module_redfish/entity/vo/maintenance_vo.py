"""
硬件更换排期VO模型
"""
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from datetime import datetime, date
from typing import Optional
from fastapi_pagination import PageSize, Page
from module_admin.annotation.pydantic_annotation import as_query


class MaintenanceScheduleQueryModel(BaseModel):
    """硬件更换排期查询对象"""
    schedule_id: Optional[int] = Field(None, description="排期ID")
    device_id: Optional[int] = Field(None, description="设备ID")
    hostname: Optional[str] = Field(None, description="主机名")
    component_type: Optional[str] = Field(None, description="组件类型")
    maintenance_type: Optional[str] = Field(None, description="维护类型")
    priority_level: Optional[str] = Field(None, description="优先级")
    status: Optional[str] = Field(None, description="状态")
    scheduled_date: Optional[date] = Field(None, description="计划日期")


@as_query
class MaintenanceSchedulePageQueryModel(MaintenanceScheduleQueryModel):
    """硬件更换排期分页查询对象"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    page_num: int = Field(1, description="页码", ge=1)
    page_size: int = Field(10, description="每页数量", ge=1, le=100)
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    department: Optional[str] = Field(None, description="部门")


class MaintenanceScheduleModel(BaseModel):
    """硬件更换排期响应模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    schedule_id: Optional[int] = Field(None, description="排期ID")
    device_id: Optional[int] = Field(None, description="设备ID")
    hostname: Optional[str] = Field(None, description="主机名")
    device_ip: Optional[str] = Field(None, description="设备IP")
    location: Optional[str] = Field(None, description="设备位置")
    component_type: Optional[str] = Field(None, description="组件类型")
    component_name: Optional[str] = Field(None, description="组件名称")
    component_serial: Optional[str] = Field(None, description="组件序列号")
    maintenance_type: Optional[str] = Field(None, description="维护类型")
    maintenance_type_dict: Optional[str] = Field(None, description="维护类型描述")
    priority_level: Optional[str] = Field(None, description="优先级")
    priority_level_dict: Optional[str] = Field(None, description="优先级描述")
    scheduled_date: Optional[date] = Field(None, description="计划日期")
    estimated_duration: Optional[int] = Field(None, description="预计耗时（分钟）")
    responsible_person: Optional[str] = Field(None, description="负责人")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    status: Optional[str] = Field(None, description="状态")
    status_dict: Optional[str] = Field(None, description="状态描述")
    description: Optional[str] = Field(None, description="描述")
    pre_check_result: Optional[str] = Field(None, description="预检结果")
    maintenance_result: Optional[str] = Field(None, description="维护结果")
    actual_start_time: Optional[datetime] = Field(None, description="实际开始时间")
    actual_end_time: Optional[datetime] = Field(None, description="实际结束时间")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_time: Optional[datetime] = Field(None, description="更新时间")
    remarks: Optional[str] = Field(None, description="备注")


class MaintenanceScheduleAddModel(BaseModel):
    """新增硬件更换排期模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    device_id: int = Field(..., description="设备ID")
    component_type: str = Field(..., description="组件类型")
    component_name: Optional[str] = Field(None, description="组件名称")
    component_serial: Optional[str] = Field(None, description="组件序列号")
    maintenance_type: str = Field(..., description="维护类型")
    priority_level: str = Field(..., description="优先级")
    scheduled_date: date = Field(..., description="计划日期")
    estimated_duration: Optional[int] = Field(None, description="预计耗时（分钟）")
    responsible_person: str = Field(..., description="负责人")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    description: Optional[str] = Field(None, description="描述")
    remarks: Optional[str] = Field(None, description="备注")


class MaintenanceScheduleEditModel(BaseModel):
    """编辑硬件更换排期模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    schedule_id: int = Field(..., description="排期ID")
    device_id: int = Field(..., description="设备ID")
    component_type: str = Field(..., description="组件类型")
    component_name: Optional[str] = Field(None, description="组件名称")
    component_serial: Optional[str] = Field(None, description="组件序列号")
    maintenance_type: str = Field(..., description="维护类型")
    priority_level: str = Field(..., description="优先级")
    scheduled_date: date = Field(..., description="计划日期")
    estimated_duration: Optional[int] = Field(None, description="预计耗时（分钟）")
    responsible_person: str = Field(..., description="负责人")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    status: Optional[str] = Field(None, description="状态")
    description: Optional[str] = Field(None, description="描述")
    pre_check_result: Optional[str] = Field(None, description="预检结果")
    maintenance_result: Optional[str] = Field(None, description="维护结果")
    actual_start_time: Optional[datetime] = Field(None, description="实际开始时间")
    actual_end_time: Optional[datetime] = Field(None, description="实际结束时间")
    remarks: Optional[str] = Field(None, description="备注")


class MaintenanceTaskModel(BaseModel):
    """维护任务模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    schedule_id: int = Field(..., description="排期ID")
    task_name: str = Field(..., description="任务名称")
    hostname: str = Field(..., description="主机名")
    component_type: str = Field(..., description="组件类型")
    priority_level: str = Field(..., description="优先级")
    scheduled_date: date = Field(..., description="计划日期")
    responsible_person: str = Field(..., description="负责人")
    status: str = Field(..., description="状态")


class MaintenanceStatisticsModel(BaseModel):
    """维护统计模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    total_schedules: int = Field(0, description="总排期数")
    pending_count: int = Field(0, description="待执行数")
    in_progress_count: int = Field(0, description="执行中数")
    completed_count: int = Field(0, description="已完成数")
    cancelled_count: int = Field(0, description="已取消数")
    urgent_count: int = Field(0, description="紧急排期数")
    delayed_count: int = Field(0, description="延期排期数")
    component_type_stats: dict = Field(default_factory=dict, description="组件类型统计")
    priority_level_stats: dict = Field(default_factory=dict, description="优先级统计")
    monthly_trend: list = Field(default_factory=list, description="月度趋势")


class MaintenanceCalendarModel(BaseModel):
    """维护日历模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    date: str = Field(..., description="日期")
    schedules: list[MaintenanceTaskModel] = Field(default_factory=list, description="当日排期")
    total_count: int = Field(0, description="当日总数")
    urgent_count: int = Field(0, description="紧急排期数") 