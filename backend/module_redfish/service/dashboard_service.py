"""
首页数据Service层
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from module_redfish.dao.device_dao import DeviceDao
from module_redfish.dao.alert_dao import AlertDao
from module_redfish.service.device_service import DeviceService
from module_redfish.service.alert_service import AlertService
from module_redfish.entity.vo.dashboard_vo import (
    DashboardOverviewModel, AlertTrendChartModel, DeviceHealthChartModel,
    RealtimeAlertListModel, ScheduledAlertListModel, DeviceHealthSummaryListModel,
    AlertDistributionModel, SystemHealthMetricsModel, DashboardDataModel,
    DashboardQueryModel
)
from utils.response_util import ResponseUtil
from utils.log_util import logger
from module_redfish.service.connectivity_service import ConnectivityService


class DashboardService:
    """首页数据服务"""
    
    @classmethod
    async def get_dashboard_overview_services(
        cls,
        db: AsyncSession,
        query_model: DashboardQueryModel,
        force_refresh: bool = False
    ) -> DashboardOverviewModel:
        """
        获取首页概览数据
        
        Args:
            db: 数据库会话
            query_model: 查询模型
            force_refresh: 是否强制刷新，跳过缓存
            
        Returns:
            DashboardOverviewModel: 首页概览数据
        """
        # 获取设备统计
        device_stats = await DeviceDao.get_device_statistics(db)
        
        # 获取设备健康状态分布
        health_distribution = await cls._get_device_health_distribution(db)
        
        # 将critical设备合并到warning中
        combined_warning_devices = health_distribution['warning'] + health_distribution['critical']
        
        # 获取基于业务IP的真实在线/离线设备统计
        # 如果force_refresh为True，则不使用缓存；否则使用3分钟缓存
        use_cache = not force_refresh
        cache_ttl = 3 if not force_refresh else 0
        
        connectivity_stats = await ConnectivityService.get_connectivity_statistics(
            db, use_cache=use_cache, cache_ttl_minutes=cache_ttl
        )
        online_devices = connectivity_stats.get('online_devices', 0)
        offline_devices = connectivity_stats.get('offline_devices', 0)
        
        # 获取7天告警统计
        alert_stats_7d = await AlertDao.get_alert_statistics(db, 7)
        
        # 获取30天告警统计
        alert_stats_30d = await AlertDao.get_alert_statistics(db, 30)
        
        # 获取当前告警统计
        current_urgent_alerts = await cls._get_current_alert_count(db, 'urgent')
        current_scheduled_alerts = await cls._get_current_alert_count(db, 'scheduled')

        
        return DashboardOverviewModel(
            totalDevices=device_stats['total_devices'],
            onlineDevices=online_devices,        # 基于业务IP连通性的在线设备数
            offlineDevices=offline_devices,      # 基于业务IP连通性的离线设备数
            healthyDevices=health_distribution['ok'],
            warningDevices=combined_warning_devices,
            criticalDevices=0,  # 不再使用critical分类，设为0
            alerts7Days=alert_stats_7d['total_alerts'],
            urgentAlerts7Days=alert_stats_7d['urgent_alerts'],
            scheduledAlerts7Days=alert_stats_7d['scheduled_alerts'],
            alerts30Days=alert_stats_30d['total_alerts'],
            urgentAlerts30Days=alert_stats_30d['urgent_alerts'],
            scheduledAlerts30Days=alert_stats_30d['scheduled_alerts'],
            currentUrgentAlerts=current_urgent_alerts,
            currentScheduledAlerts=current_scheduled_alerts,
            lastUpdateTime=datetime.now()
        )
    
    @classmethod
    async def get_alert_trend_chart_services(
        cls,
        db: AsyncSession,
        days: int = 7
    ) -> AlertTrendChartModel:
        """
        获取告警趋势图数据
        
        Args:
            db: 数据库会话
            days: 统计天数
            
        Returns:
            AlertTrendChartModel: 趋势图数据
        """
        trend_data = await AlertDao.get_alert_trend(db, days)
        
        dates = [item['date'] for item in trend_data]
        urgent_counts = [item['urgent_count'] for item in trend_data]
        scheduled_counts = [item['scheduled_count'] for item in trend_data]
        total_counts = [item['total_count'] for item in trend_data]
        
        return AlertTrendChartModel(
            dates=dates,
            urgentCounts=urgent_counts,
            scheduledCounts=scheduled_counts,
            totalCounts=total_counts
        )
    
    @classmethod
    async def get_device_health_chart_services(
        cls,
        db: AsyncSession
    ) -> DeviceHealthChartModel:
        """
        获取设备健康图数据
        
        Args:
            db: 数据库会话
            
        Returns:
            DeviceHealthChartModel: 设备健康图数据
        """
        # 获取详细的设备健康状态分布
        health_distribution = await cls._get_device_health_distribution(db)
        
        healthy_count = health_distribution['ok']
        # 将critical合并到warning中
        warning_count = health_distribution['warning'] + health_distribution['critical']
        offline_count = health_distribution['unknown']
        
        # 按组件类型统计健康状态（不再包含critical分类）
        component_health = {
            'Processor': {'healthy': 0, 'warning': 0},
            'Memory': {'healthy': 0, 'warning': 0},
            'Storage': {'healthy': 0, 'warning': 0},
            'Power': {'healthy': 0, 'warning': 0},
            'Thermal': {'healthy': 0, 'warning': 0}
        }
        
        return DeviceHealthChartModel(
            healthyCount=healthy_count,
            warningCount=warning_count,
            criticalCount=0,  # 不再使用critical分类，设为0
            offlineCount=offline_count,
            componentHealth=component_health
        )
    
    @classmethod
    async def get_realtime_alert_list_services(
        cls,
        db: AsyncSession,
        limit: int = 10
    ) -> List[RealtimeAlertListModel]:
        """
        获取实时告警列表数据
        
        Args:
            db: 数据库会话
            limit: 返回数量限制
            
        Returns:
            List[RealtimeAlertListModel]: 实时告警列表
        """
        alerts = await AlertDao.get_realtime_alerts(db, limit)
        
        result = []
        for alert in alerts:
            # 计算持续时间
            duration = cls._calculate_duration(alert['first_occurrence'])
            
            # 获取设备位置信息
            # TODO: 可以优化为一次查询获取所有设备信息
            from module_redfish.dao.device_dao import DeviceDao
            device = await DeviceDao.get_device_by_id(db, alert['device_id'])
            location = device.location if device else "Unknown"
            
            result.append(RealtimeAlertListModel(
                deviceId=alert['device_id'],
                hostname=alert['hostname'],
                businessIp=alert['business_ip'],
                location=location,
                componentType=alert['component_type'],
                componentName=alert['component_name'],
                healthStatus=alert['health_status'],
                urgencyLevel=alert['urgency_level'],
                alertMessage="",  # 优化版DAO中没有alert_message字段
                firstOccurrence=alert['first_occurrence'],
                lastOccurrence=alert['last_occurrence'],
                duration=duration
            ))
        
        return result
    
    @classmethod
    async def get_scheduled_alert_list_services(
        cls,
        db: AsyncSession,
        limit: int = 10
    ) -> List[ScheduledAlertListModel]:
        """
        获取择期告警列表数据
        
        Args:
            db: 数据库会话
            limit: 返回数量限制
            
        Returns:
            List[ScheduledAlertListModel]: 择期告警列表
        """
        alerts = await AlertDao.get_scheduled_alerts(db, limit)
        
        result = []
        for alert in alerts:
            # 获取设备位置信息
            from module_redfish.dao.device_dao import DeviceDao
            device = await DeviceDao.get_device_by_id(db, alert['device_id'])
            location = device.location if device else "Unknown"
            
            # 计算优先级评分（基于时间）
            priorityScore = 10  # 基础分数
            if alert['first_occurrence'] < datetime.now() - timedelta(days=7):
                priorityScore += 50  # 超过7天的告警增加优先级
            
            result.append(ScheduledAlertListModel(
                deviceId=alert['device_id'],
                hostname=alert['hostname'],
                businessIp=alert['business_ip'],
                location=location,
                componentType=alert['component_type'],
                componentName=alert['component_name'],
                healthStatus=alert['health_status'],
                urgencyLevel=alert['urgency_level'],
                firstOccurrence=alert['first_occurrence'],
                priorityScore=priorityScore
            ))
        
        return result
    
    @classmethod
    async def get_device_health_summary_services(
        cls,
        db: AsyncSession,
        limit: int = 20
    ) -> List[DeviceHealthSummaryListModel]:
        """
        获取设备健康汇总列表
        
        Args:
            db: 数据库会话
            limit: 返回数量限制
            
        Returns:
            List[DeviceHealthSummaryListModel]: 设备健康汇总列表
        """
        # 获取监控设备列表
        devices = await DeviceDao.get_monitoring_devices(db)
        
        result = []
        for device in devices[:limit]:
            # 读取真实的设备健康状态（来自 device_info 表与告警表）
            overallHealth = (device.health_status or "unknown").lower()
            # 组件健康：用最近活跃告警推断（有告警则标记 warning，否则 ok）
            deviceAlerts = await AlertService.get_device_alerts_services(db, device.device_id)
            alertCount = len(deviceAlerts)

            def comp_health(component: str) -> str:
                for a in deviceAlerts:
                    if a.component_type.lower() in component:
                        return a.health_status
                return "ok"

            processorHealth = comp_health("processor")
            memoryHealth = comp_health("memory")
            storageHealth = comp_health("storage")
            thermalHealth = "ok"  # 无专门热告警则视为ok
            powerHealth = comp_health("power")

            # 设备连接状态基于业务 IP 连通性缓存统计（简化：有业务IP则 Connected，否则 Unknown）
            connectionStatus = "Connected" if device.business_ip else "Unknown"

            result.append(DeviceHealthSummaryListModel(
                deviceId=device.device_id,
                hostname=device.hostname,
                businessIp=device.business_ip,
                location=device.location or "Unknown",
                manufacturer=device.manufacturer or "Unknown",
                model=device.model or "Unknown",
                overallHealth=overallHealth,
                powerState=device.operating_system or "On",
                processorHealth=processorHealth,
                memoryHealth=memoryHealth,
                storageHealth=storageHealth,
                thermalHealth=thermalHealth,
                powerHealth=powerHealth,
                alertCount=alertCount,
                lastCheckTime=device.last_check_time or datetime.now(),
                connectionStatus=connectionStatus
            ))
        
        return result
    
    @classmethod
    async def get_system_health_metrics_services(
        cls,
        db: AsyncSession
    ) -> SystemHealthMetricsModel:
        """
        获取系统健康指标
        
        Args:
            db: 数据库会话
            
        Returns:
            SystemHealthMetricsModel: 系统健康指标
        """
        device_stats = await DeviceDao.get_device_statistics(db)
        alert_stats = await AlertDao.get_alert_statistics(db, 1)  # 当天告警
        
        # TODO: 实现真实的系统健康指标计算
        totalMonitoringPoints = device_stats['monitoring_devices'] * 5  # 假设每个设备5个监控点
        healthyPoints = totalMonitoringPoints - alert_stats['active_alerts']
        warningPoints = alert_stats['active_alerts']
        criticalPoints = 0  # 暂时没有严重告警的概念
        unavailablePoints = device_stats['inactive_devices'] * 5
        
        healthPercentage = (healthyPoints / totalMonitoringPoints * 100) if totalMonitoringPoints > 0 else 100
        availabilityPercentage = ((totalMonitoringPoints - unavailablePoints) / totalMonitoringPoints * 100) if totalMonitoringPoints > 0 else 100
        
        return SystemHealthMetricsModel(
            totalMonitoringPoints=totalMonitoringPoints,
            healthyPoints=healthyPoints,
            warningPoints=warningPoints,
            criticalPoints=criticalPoints,
            unavailablePoints=unavailablePoints,
            healthPercentage=round(healthPercentage, 2),
            availabilityPercentage=round(availabilityPercentage, 2),
            avgResponseTime=1.5,  # 模拟数据
            monitoringSuccessRate=98.5,  # 模拟数据
            lastCalculationTime=datetime.now()
        )
    
    @classmethod
    async def get_complete_dashboard_data_services(
        cls,
        db: AsyncSession,
        query_model: DashboardQueryModel,
        force_refresh: bool = False
    ) -> DashboardDataModel:
        """
        获取完整的首页数据
        
        Args:
            db: 数据库会话
            query_model: 查询模型
            force_refresh: 是否强制刷新，跳过缓存
            
        Returns:
            DashboardDataModel: 完整的首页数据
        """
        # 解析时间范围
        days = 7
        if query_model.timeRange == "30d":
            days = 30
        elif query_model.timeRange == "90d":
            days = 90
        
        # 并行获取各种数据
        overview = await cls.get_dashboard_overview_services(db, query_model, force_refresh)
        alert_trend = await cls.get_alert_trend_chart_services(db, days)
        device_health_chart = await cls.get_device_health_chart_services(db)
        realtime_alerts = await cls.get_realtime_alert_list_services(db, 10)
        scheduled_alerts = await cls.get_scheduled_alert_list_services(db, 10)
        device_health_summary = await cls.get_device_health_summary_services(db, 20)
        alert_distribution = await AlertService.get_alert_distribution_services(db)
        system_metrics = await cls.get_system_health_metrics_services(db)
        
        return DashboardDataModel(
            overview=overview,
            alertTrend=alert_trend,
            deviceHealthChart=device_health_chart,
            realtimeAlerts=realtime_alerts,
            scheduledAlerts=scheduled_alerts,
            deviceHealthSummary=device_health_summary,
            alertDistribution=alert_distribution,
            systemMetrics=system_metrics
        )
    
    @classmethod
    async def _get_device_health_distribution(cls, db: AsyncSession) -> Dict[str, int]:
        """
        获取设备健康状态分布
        
        Args:
            db: 数据库会话
            
        Returns:
            Dict[str, int]: 健康状态分布
        """
        from sqlalchemy import select, func
        from module_redfish.entity.do.device_do import DeviceInfoDO
        
        # 按健康状态分组统计
        result = await db.execute(
            select(
                DeviceInfoDO.health_status,
                func.count(DeviceInfoDO.device_id).label('count')
            ).group_by(DeviceInfoDO.health_status)
        )
        
        status_counts = {}
        for row in result:
            status_counts[row.health_status] = row.count
        
        return {
            'ok': status_counts.get('ok', 0),
            'warning': status_counts.get('warning', 0),
            'critical': status_counts.get('critical', 0),
            'unknown': status_counts.get('unknown', 0)
        }

    @classmethod
    async def _get_current_alert_count(cls, db: AsyncSession, urgency_level: str) -> int:
        """
        获取当前指定紧急程度的告警数量
        
        Args:
            db: 数据库会话
            urgency_level: 紧急程度
            
        Returns:
            int: 告警数量
        """
        from sqlalchemy import select, func, and_
        from module_redfish.entity.do.alert_do import AlertInfoDO
        
        result = await db.execute(
            select(func.count(AlertInfoDO.alert_id)).where(
                and_(
                    AlertInfoDO.alert_status == 'active',
                    AlertInfoDO.urgency_level == urgency_level,
                    AlertInfoDO.del_flag == 0  # 添加del_flag条件，排除逻辑删除的告警
                )
            )
        )
        return result.scalar() or 0
    
    @classmethod
    def _calculate_duration(cls, start_time: datetime) -> str:
        """
        计算持续时间
        
        Args:
            start_time: 开始时间
            
        Returns:
            str: 持续时间字符串
        """
        duration = datetime.now() - start_time
        
        if duration.days > 0:
            return f"{duration.days}天"
        elif duration.seconds >= 3600:
            hours = duration.seconds // 3600
            return f"{hours}小时"
        elif duration.seconds >= 60:
            minutes = duration.seconds // 60
            return f"{minutes}分钟"
        else:
            return "刚刚" 