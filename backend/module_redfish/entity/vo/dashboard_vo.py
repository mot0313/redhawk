"""
首页数据VO模型
"""
from datetime import datetime, date
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class DashboardOverviewModel(BaseModel):
    """首页概览模型"""
    total_devices: int = Field(..., description="设备总数")
    online_devices: int = Field(..., description="在线设备数")
    offline_devices: int = Field(..., description="离线设备数")
    healthy_devices: int = Field(..., description="健康设备数")
    warning_devices: int = Field(..., description="告警设备数")
    critical_devices: int = Field(..., description="严重告警设备数")
    
    # 7天告警统计
    alerts_7days: int = Field(..., description="7天告警总数")
    urgent_alerts_7days: int = Field(..., description="7天紧急告警数")
    scheduled_alerts_7days: int = Field(..., description="7天择期告警数")
    
    # 30天告警统计
    alerts_30days: int = Field(..., description="30天告警总数")
    urgent_alerts_30days: int = Field(..., description="30天紧急告警数")
    scheduled_alerts_30days: int = Field(..., description="30天择期告警数")
    
    # 当前告警统计
    current_urgent_alerts: int = Field(..., description="当前紧急告警数")
    current_scheduled_alerts: int = Field(..., description="当前择期告警数")
    
    last_update_time: datetime = Field(..., description="最后更新时间")


class AlertTrendChartModel(BaseModel):
    """告警趋势图模型"""
    dates: List[str] = Field(..., description="日期列表")
    urgent_counts: List[int] = Field(..., description="紧急告警数量列表")
    scheduled_counts: List[int] = Field(..., description="择期告警数量列表")
    total_counts: List[int] = Field(..., description="总告警数量列表")


class DeviceHealthChartModel(BaseModel):
    """设备健康图模型"""
    healthy_count: int = Field(..., description="健康设备数")
    warning_count: int = Field(..., description="告警设备数")
    critical_count: int = Field(..., description="严重告警设备数")
    offline_count: int = Field(..., description="离线设备数")
    
    # 按组件类型统计
    component_health: Dict[str, Dict[str, int]] = Field(..., description="组件健康统计")


class RealtimeAlertListModel(BaseModel):
    """实时告警列表模型"""
    device_id: int = Field(..., description="设备ID")
    hostname: str = Field(..., description="主机名")
    business_ip: str = Field(..., description="业务IP")
    location: str = Field(..., description="位置")
    component_type: str = Field(..., description="组件类型")
    component_name: str = Field(..., description="组件名称")
    health_status: str = Field(..., description="健康状态")
    alert_level: str = Field(..., description="告警级别")
    alert_message: str = Field(..., description="告警消息")
    last_occurrence: datetime = Field(..., description="最后发生时间")
    duration: str = Field(..., description="持续时间")


class ScheduledAlertListModel(BaseModel):
    """择期告警列表模型"""
    device_id: int = Field(..., description="设备ID")
    hostname: str = Field(..., description="主机名")
    business_ip: str = Field(..., description="业务IP")
    location: str = Field(..., description="位置")
    component_type: str = Field(..., description="组件类型")
    component_name: str = Field(..., description="组件名称")
    health_status: str = Field(..., description="健康状态")
    alert_message: str = Field(..., description="告警消息")
    first_occurrence: datetime = Field(..., description="首次发生时间")
    occurrence_count: int = Field(..., description="发生次数")
    priority_score: int = Field(..., description="优先级评分")


class DeviceHealthSummaryListModel(BaseModel):
    """设备健康汇总列表模型"""
    device_id: int = Field(..., description="设备ID")
    hostname: str = Field(..., description="主机名")
    business_ip: str = Field(..., description="业务IP")
    location: str = Field(..., description="位置")
    manufacturer: str = Field(..., description="制造商")
    model: str = Field(..., description="型号")
    overall_health: str = Field(..., description="整体健康状态")
    power_state: str = Field(..., description="电源状态")
    
    # 组件健康状态
    processor_health: str = Field(..., description="处理器健康状态")
    memory_health: str = Field(..., description="内存健康状态")
    storage_health: str = Field(..., description="存储健康状态")
    thermal_health: str = Field(..., description="温度健康状态")
    power_health: str = Field(..., description="电源健康状态")
    
    alert_count: int = Field(..., description="告警数量")
    last_check_time: datetime = Field(..., description="最后检查时间")
    connection_status: str = Field(..., description="连接状态")


class AlertDistributionModel(BaseModel):
    """告警分布模型"""
    by_level: Dict[str, int] = Field(..., description="按级别分布")
    by_component: Dict[str, int] = Field(..., description="按组件分布")
    by_location: Dict[str, int] = Field(..., description="按位置分布")
    by_manufacturer: Dict[str, int] = Field(..., description="按制造商分布")


class SystemHealthMetricsModel(BaseModel):
    """系统健康指标模型"""
    total_monitoring_points: int = Field(..., description="总监控点数")
    healthy_points: int = Field(..., description="健康监控点数")
    warning_points: int = Field(..., description="告警监控点数")
    critical_points: int = Field(..., description="严重告警监控点数")
    unavailable_points: int = Field(..., description="不可用监控点数")
    
    health_percentage: float = Field(..., description="健康百分比")
    availability_percentage: float = Field(..., description="可用性百分比")
    
    # 性能指标
    avg_response_time: float = Field(..., description="平均响应时间(秒)")
    monitoring_success_rate: float = Field(..., description="监控成功率")
    
    last_calculation_time: datetime = Field(..., description="最后计算时间")


class DashboardQueryModel(BaseModel):
    """首页数据查询模型"""
    time_range: str = Field(default="7d", description="时间范围(7d/30d/90d)")
    include_resolved: bool = Field(default=False, description="是否包含已解决告警")
    location_filter: Optional[str] = Field(default=None, description="位置过滤")
    manufacturer_filter: Optional[str] = Field(default=None, description="制造商过滤")


class DashboardDataModel(BaseModel):
    """首页完整数据模型"""
    overview: DashboardOverviewModel = Field(..., description="概览数据")
    alert_trend: AlertTrendChartModel = Field(..., description="告警趋势图")
    device_health_chart: DeviceHealthChartModel = Field(..., description="设备健康图")
    realtime_alerts: List[RealtimeAlertListModel] = Field(..., description="实时告警列表")
    scheduled_alerts: List[ScheduledAlertListModel] = Field(..., description="择期告警列表")
    device_health_summary: List[DeviceHealthSummaryListModel] = Field(..., description="设备健康汇总")
    alert_distribution: AlertDistributionModel = Field(..., description="告警分布")
    system_metrics: SystemHealthMetricsModel = Field(..., description="系统健康指标") 