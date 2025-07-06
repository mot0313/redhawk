"""
首页数据VO模型
"""
from datetime import datetime, date
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class DashboardOverviewModel(BaseModel):
    """首页概览模型"""
    totalDevices: int = Field(..., description="设备总数")
    onlineDevices: int = Field(..., description="在线设备数")
    offlineDevices: int = Field(..., description="离线设备数")
    healthyDevices: int = Field(..., description="健康设备数")
    warningDevices: int = Field(..., description="告警设备数")
    criticalDevices: int = Field(..., description="已废弃字段(critical已合并到warning)")
    
    # 7天告警统计
    alerts7Days: int = Field(..., description="7天告警总数")
    urgentAlerts7Days: int = Field(..., description="7天紧急告警数")
    scheduledAlerts7Days: int = Field(..., description="7天择期告警数")
    
    # 30天告警统计
    alerts30Days: int = Field(..., description="30天告警总数")
    urgentAlerts30Days: int = Field(..., description="30天紧急告警数")
    scheduledAlerts30Days: int = Field(..., description="30天择期告警数")
    
    # 当前告警统计
    currentUrgentAlerts: int = Field(..., description="当前紧急告警数")
    currentScheduledAlerts: int = Field(..., description="当前择期告警数")
    
    lastUpdateTime: datetime = Field(..., description="最后更新时间")


class AlertTrendChartModel(BaseModel):
    """告警趋势图模型"""
    dates: List[str] = Field(..., description="日期列表")
    urgentCounts: List[int] = Field(..., description="紧急告警数量列表")
    scheduledCounts: List[int] = Field(..., description="择期告警数量列表")
    totalCounts: List[int] = Field(..., description="总告警数量列表")


class DeviceHealthChartModel(BaseModel):
    """设备健康图模型"""
    healthyCount: int = Field(..., description="健康设备数")
    warningCount: int = Field(..., description="告警设备数")
    criticalCount: int = Field(..., description="已废弃字段(critical已合并到warning)")
    offlineCount: int = Field(..., description="离线设备数")
    
    # 按组件类型统计
    componentHealth: Dict[str, Dict[str, int]] = Field(..., description="组件健康统计")


class RealtimeAlertListModel(BaseModel):
    """实时告警列表模型"""
    deviceId: int = Field(..., description="设备ID")
    hostname: str = Field(..., description="主机名")
    businessIp: str = Field(..., description="业务IP")
    location: str = Field(..., description="位置")
    componentType: str = Field(..., description="组件类型")
    componentName: str = Field(..., description="组件名称")
    healthStatus: str = Field(..., description="健康状态")
    urgencyLevel: str = Field(..., description="紧急程度")
    alertMessage: str = Field(..., description="告警消息")
    firstOccurrence: datetime = Field(..., description="首次发生时间")
    lastOccurrence: datetime = Field(..., description="最后发生时间")
    duration: str = Field(..., description="持续时间")


class ScheduledAlertListModel(BaseModel):
    """择期告警列表模型"""
    deviceId: int = Field(..., description="设备ID")
    hostname: str = Field(..., description="主机名")
    businessIp: str = Field(..., description="业务IP")
    location: str = Field(..., description="位置")
    componentType: str = Field(..., description="组件类型")
    componentName: str = Field(..., description="组件名称")
    healthStatus: str = Field(..., description="健康状态")
    urgencyLevel: str = Field(..., description="紧急程度")
    firstOccurrence: datetime = Field(..., description="首次发生时间")
    priorityScore: int = Field(..., description="优先级评分")


class DeviceHealthSummaryListModel(BaseModel):
    """设备健康汇总列表模型"""
    deviceId: int = Field(..., description="设备ID")
    hostname: str = Field(..., description="主机名")
    businessIp: str = Field(..., description="业务IP")
    location: str = Field(..., description="位置")
    manufacturer: str = Field(..., description="制造商")
    model: str = Field(..., description="型号")
    overallHealth: str = Field(..., description="整体健康状态")
    powerState: str = Field(..., description="电源状态")
    
    # 组件健康状态
    processorHealth: str = Field(..., description="处理器健康状态")
    memoryHealth: str = Field(..., description="内存健康状态")
    storageHealth: str = Field(..., description="存储健康状态")
    thermalHealth: str = Field(..., description="温度健康状态")
    powerHealth: str = Field(..., description="电源健康状态")
    
    alertCount: int = Field(..., description="告警数量")
    lastCheckTime: datetime = Field(..., description="最后检查时间")
    connectionStatus: str = Field(..., description="连接状态")


class AlertDistributionModel(BaseModel):
    """告警分布模型"""
    byLevel: Dict[str, int] = Field(..., description="按级别分布")
    byComponent: Dict[str, int] = Field(..., description="按组件分布")
    byLocation: Dict[str, int] = Field(..., description="按位置分布")
    byManufacturer: Dict[str, int] = Field(..., description="按制造商分布")


class SystemHealthMetricsModel(BaseModel):
    """系统健康指标模型"""
    totalMonitoringPoints: int = Field(..., description="总监控点数")
    healthyPoints: int = Field(..., description="健康监控点数")
    warningPoints: int = Field(..., description="告警监控点数")
    criticalPoints: int = Field(..., description="已废弃字段(critical已合并到warning)")
    unavailablePoints: int = Field(..., description="不可用监控点数")
    
    healthPercentage: float = Field(..., description="健康百分比")
    availabilityPercentage: float = Field(..., description="可用性百分比")
    
    # 性能指标
    avgResponseTime: float = Field(..., description="平均响应时间(秒)")
    monitoringSuccessRate: float = Field(..., description="监控成功率")
    
    lastCalculationTime: datetime = Field(..., description="最后计算时间")


class DashboardQueryModel(BaseModel):
    """首页数据查询模型"""
    timeRange: str = Field(default="7d", description="时间范围(7d/30d/90d)")
    includeResolved: bool = Field(default=False, description="是否包含已解决告警")
    locationFilter: Optional[str] = Field(default=None, description="位置过滤")
    manufacturerFilter: Optional[str] = Field(default=None, description="制造商过滤")


class DashboardDataModel(BaseModel):
    """首页完整数据模型"""
    overview: DashboardOverviewModel = Field(..., description="概览数据")
    alertTrend: AlertTrendChartModel = Field(..., description="告警趋势图")
    deviceHealthChart: DeviceHealthChartModel = Field(..., description="设备健康图")
    realtimeAlerts: List[RealtimeAlertListModel] = Field(..., description="实时告警列表")
    scheduledAlerts: List[ScheduledAlertListModel] = Field(..., description="择期告警列表")
    deviceHealthSummary: List[DeviceHealthSummaryListModel] = Field(..., description="设备健康汇总")
    alertDistribution: AlertDistributionModel = Field(..., description="告警分布")
    systemMetrics: SystemHealthMetricsModel = Field(..., description="系统健康指标") 