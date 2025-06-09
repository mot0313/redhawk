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


class DashboardService:
    """首页数据服务"""
    
    @classmethod
    async def get_dashboard_overview_services(
        cls,
        db: AsyncSession,
        query_model: DashboardQueryModel
    ) -> DashboardOverviewModel:
        """
        获取首页概览数据
        
        Args:
            db: 数据库会话
            query_model: 查询模型
            
        Returns:
            DashboardOverviewModel: 概览数据
        """
        # 获取设备统计
        device_stats = await DeviceDao.get_device_statistics(db)
        
        # 获取7天告警统计
        alert_stats_7d = await AlertDao.get_alert_statistics(db, 7)
        
        # 获取30天告警统计
        alert_stats_30d = await AlertDao.get_alert_statistics(db, 30)
        
        # 当前紧急告警数和择期告警数
        current_urgent_alerts = await cls._get_current_alert_count(db, 'urgent')
        current_scheduled_alerts = await cls._get_current_alert_count(db, 'scheduled')
        
        # 设备健康状态统计
        # 基于健康状态统计设备
        healthy_devices = device_stats['healthy_devices']
        unhealthy_devices = device_stats['unhealthy_devices']
        
        # 获取详细的健康状态分布
        health_distribution = await cls._get_device_health_distribution(db)
        
        return DashboardOverviewModel(
            total_devices=device_stats['total_devices'],
            online_devices=device_stats['healthy_devices'],  # 使用健康设备数表示在线
            offline_devices=unhealthy_devices,               # 使用不健康设备数表示离线
            healthy_devices=health_distribution['ok'],
            warning_devices=health_distribution['warning'],
            critical_devices=health_distribution['critical'],
            alerts_7days=alert_stats_7d['total_alerts'],
            urgent_alerts_7days=alert_stats_7d['urgent_alerts'],
            scheduled_alerts_7days=alert_stats_7d['scheduled_alerts'],
            alerts_30days=alert_stats_30d['total_alerts'],
            urgent_alerts_30days=alert_stats_30d['urgent_alerts'],
            scheduled_alerts_30days=alert_stats_30d['scheduled_alerts'],
            current_urgent_alerts=current_urgent_alerts,
            current_scheduled_alerts=current_scheduled_alerts,
            last_update_time=datetime.now()
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
            urgent_counts=urgent_counts,
            scheduled_counts=scheduled_counts,
            total_counts=total_counts
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
        warning_count = health_distribution['warning']
        critical_count = health_distribution['critical']
        offline_count = health_distribution['unknown']
        
        # 按组件类型统计健康状态
        component_health = {
            'Processor': {'healthy': 0, 'warning': 0, 'critical': 0},
            'Memory': {'healthy': 0, 'warning': 0, 'critical': 0},
            'Storage': {'healthy': 0, 'warning': 0, 'critical': 0},
            'Power': {'healthy': 0, 'warning': 0, 'critical': 0},
            'Thermal': {'healthy': 0, 'warning': 0, 'critical': 0}
        }
        
        return DeviceHealthChartModel(
            healthy_count=healthy_count,
            warning_count=warning_count,
            critical_count=critical_count,
            offline_count=offline_count,
            component_health=component_health
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
            duration = cls._calculate_duration(alert.first_occurrence)
            
            # 获取设备位置信息
            # TODO: 可以优化为一次查询获取所有设备信息
            from module_redfish.dao.device_dao import DeviceDao
            device = await DeviceDao.get_device_by_id(db, alert.device_id)
            location = device.location if device else "Unknown"
            
            result.append(RealtimeAlertListModel(
                device_id=alert.device_id,
                hostname=alert.hostname,
                business_ip=alert.business_ip,
                location=location,
                component_type=alert.component_type,
                component_name=alert.component_name,
                health_status=alert.health_status,
                alert_level=alert.alert_level,
                alert_message=alert.alert_message,
                last_occurrence=alert.last_occurrence,
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
            device = await DeviceDao.get_device_by_id(db, alert.device_id)
            location = device.location if device else "Unknown"
            
            # 计算优先级评分（基于发生次数和时间）
            priority_score = alert.occurrence_count * 10
            if alert.first_occurrence < datetime.now() - timedelta(days=7):
                priority_score += 50  # 超过7天的告警增加优先级
            
            result.append(ScheduledAlertListModel(
                device_id=alert.device_id,
                hostname=alert.hostname,
                business_ip=alert.business_ip,
                location=location,
                component_type=alert.component_type,
                component_name=alert.component_name,
                health_status=alert.health_status,
                alert_message=alert.alert_message,
                first_occurrence=alert.first_occurrence,
                occurrence_count=alert.occurrence_count,
                priority_score=priority_score
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
            # TODO: 实现真实的设备健康状态获取
            # 这里需要从最新的监控数据中获取设备的健康状态
            
            # 暂时使用模拟数据
            overall_health = "OK"
            power_state = "On"
            processor_health = "OK"
            memory_health = "OK"
            storage_health = "OK"
            thermal_health = "OK"
            power_health = "OK"
            
            # 获取设备的告警数量
            device_alerts = await AlertService.get_device_alerts_services(db, device.device_id)
            alert_count = len(device_alerts)
            
            # 设备连接状态
            connection_status = "Connected"  # 暂时硬编码
            
            result.append(DeviceHealthSummaryListModel(
                device_id=device.device_id,
                hostname=device.hostname,
                business_ip=device.business_ip,
                location=device.location or "Unknown",
                manufacturer=device.manufacturer or "Unknown",
                model=device.model or "Unknown",
                overall_health=overall_health,
                power_state=power_state,
                processor_health=processor_health,
                memory_health=memory_health,
                storage_health=storage_health,
                thermal_health=thermal_health,
                power_health=power_health,
                alert_count=alert_count,
                last_check_time=datetime.now(),  # 暂时使用当前时间
                connection_status=connection_status
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
        total_monitoring_points = device_stats['monitoring_devices'] * 5  # 假设每个设备5个监控点
        healthy_points = total_monitoring_points - alert_stats['active_alerts']
        warning_points = alert_stats['active_alerts']
        critical_points = 0  # 暂时没有严重告警的概念
        unavailable_points = device_stats['inactive_devices'] * 5
        
        health_percentage = (healthy_points / total_monitoring_points * 100) if total_monitoring_points > 0 else 100
        availability_percentage = ((total_monitoring_points - unavailable_points) / total_monitoring_points * 100) if total_monitoring_points > 0 else 100
        
        return SystemHealthMetricsModel(
            total_monitoring_points=total_monitoring_points,
            healthy_points=healthy_points,
            warning_points=warning_points,
            critical_points=critical_points,
            unavailable_points=unavailable_points,
            health_percentage=round(health_percentage, 2),
            availability_percentage=round(availability_percentage, 2),
            avg_response_time=1.5,  # 模拟数据
            monitoring_success_rate=98.5,  # 模拟数据
            last_calculation_time=datetime.now()
        )
    
    @classmethod
    async def get_complete_dashboard_data_services(
        cls,
        db: AsyncSession,
        query_model: DashboardQueryModel
    ) -> DashboardDataModel:
        """
        获取完整的首页数据
        
        Args:
            db: 数据库会话
            query_model: 查询模型
            
        Returns:
            DashboardDataModel: 完整的首页数据
        """
        # 解析时间范围
        days = 7
        if query_model.time_range == "30d":
            days = 30
        elif query_model.time_range == "90d":
            days = 90
        
        # 并行获取各种数据
        overview = await cls.get_dashboard_overview_services(db, query_model)
        alert_trend = await cls.get_alert_trend_chart_services(db, days)
        device_health_chart = await cls.get_device_health_chart_services(db)
        realtime_alerts = await cls.get_realtime_alert_list_services(db, 10)
        scheduled_alerts = await cls.get_scheduled_alert_list_services(db, 10)
        device_health_summary = await cls.get_device_health_summary_services(db, 20)
        alert_distribution = await AlertService.get_alert_distribution_services(db)
        system_metrics = await cls.get_system_health_metrics_services(db)
        
        return DashboardDataModel(
            overview=overview,
            alert_trend=alert_trend,
            device_health_chart=device_health_chart,
            realtime_alerts=realtime_alerts,
            scheduled_alerts=scheduled_alerts,
            device_health_summary=device_health_summary,
            alert_distribution=alert_distribution,
            system_metrics=system_metrics
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
        from module_redfish.models import DeviceInfo
        
        # 按健康状态分组统计
        result = await db.execute(
            select(
                DeviceInfo.health_status,
                func.count(DeviceInfo.device_id).label('count')
            ).group_by(DeviceInfo.health_status)
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
    async def _get_current_alert_count(cls, db: AsyncSession, alert_level: str) -> int:
        """
        获取当前指定级别的告警数量
        
        Args:
            db: 数据库会话
            alert_level: 告警级别
            
        Returns:
            int: 告警数量
        """
        from sqlalchemy import select, func, and_
        from module_redfish.models import AlertInfo
        
        result = await db.execute(
            select(func.count(AlertInfo.alert_id)).where(
                and_(
                    AlertInfo.alert_status == 'active',
                    AlertInfo.alert_level == alert_level
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