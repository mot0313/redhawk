"""
告警管理Service层
"""
import math
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from module_redfish.dao.alert_dao import AlertDao
from module_redfish.entity.vo.alert_vo import (
    AlertPageQueryModel, AlertManualOverrideModel, AlertResolveModel, AlertIgnoreModel,
    AlertStatisticsModel, AlertTrendModel, RealtimeAlertModel, ScheduledAlertModel,
    AlertDistributionModel
)
from utils.response_util import ResponseUtil
from utils.page_util import PageResponseModel, PageUtil
from utils.log_util import logger


class AlertService:
    """告警管理服务"""
    
    @classmethod
    async def get_alert_list_services(
        cls,
        db: AsyncSession,
        query_object: AlertPageQueryModel,
        is_page: bool = False
    ) -> PageResponseModel:
        """
        获取告警列表
        
        Args:
            db: 数据库会话
            query_object: 查询对象
            is_page: 是否分页
            
        Returns:
            PageResponseModel: 分页响应
        """
        alert_list, total = await AlertDao.get_alert_list(db, query_object, is_page)
        
        if is_page:
            # 使用现有的分页方法创建分页响应
            has_next = math.ceil(total / query_object.page_size) > query_object.page_num if total > 0 else False
            from utils.common_util import CamelCaseUtil
            return PageResponseModel(
                rows=CamelCaseUtil.transform_result(alert_list),
                pageNum=query_object.page_num,
                pageSize=query_object.page_size,
                total=total,
                hasNext=has_next
            )
        else:
            from utils.common_util import CamelCaseUtil
            return CamelCaseUtil.transform_result(alert_list)
    
    @classmethod
    async def get_alert_detail_services(cls, db: AsyncSession, alert_id: int) -> ResponseUtil:
        """
        获取告警详情
        
        Args:
            db: 数据库会话
            alert_id: 告警ID
            
        Returns:
            ResponseUtil: 响应结果
        """
        alert = await AlertDao.get_alert_by_id(db, alert_id)
        if not alert:
            return ResponseUtil.failure(msg="告警不存在")
        
        return ResponseUtil.success(data=alert)
    
    @classmethod
    async def manual_override_alert_services(
        cls,
        db: AsyncSession,
        override_model: AlertManualOverrideModel
    ) -> ResponseUtil:
        """
        手动覆盖告警级别
        
        Args:
            db: 数据库会话
            override_model: 覆盖模型
            
        Returns:
            ResponseUtil: 响应结果
        """
        try:
            success = await AlertDao.manual_override_alert(
                db,
                override_model.alert_id,
                override_model.manual_level,
                override_model.manual_reason,
                override_model.manual_operator
            )
            
            if success:
                logger.info(f"成功手动覆盖告警级别: {override_model.alert_id} -> {override_model.manual_level}")
                return ResponseUtil.success(msg="手动覆盖告警级别成功")
            else:
                return ResponseUtil.failure(msg="手动覆盖告警级别失败")
        except Exception as e:
            logger.error(f"手动覆盖告警级别失败: {str(e)}")
            return ResponseUtil.failure(msg="手动覆盖告警级别失败")
    
    @classmethod
    async def resolve_alerts_services(
        cls,
        db: AsyncSession,
        resolve_model: AlertResolveModel
    ) -> ResponseUtil:
        """
        解决告警
        
        Args:
            db: 数据库会话
            resolve_model: 解决模型
            
        Returns:
            ResponseUtil: 响应结果
        """
        alert_ids = [int(id_str) for id_str in resolve_model.alert_ids.split(',') if id_str]
        
        if not alert_ids:
            return ResponseUtil.failure(msg="请选择要解决的告警")
        
        try:
            success = await AlertDao.resolve_alerts(
                db,
                alert_ids,
                resolve_model.resolved_by,
                resolve_model.resolved_note
            )
            
            if success:
                logger.info(f"成功解决告警: {alert_ids}")
                return ResponseUtil.success(msg="解决告警成功")
            else:
                return ResponseUtil.failure(msg="解决告警失败")
        except Exception as e:
            logger.error(f"解决告警失败: {str(e)}")
            return ResponseUtil.failure(msg="解决告警失败")
    
    @classmethod
    async def ignore_alerts_services(
        cls,
        db: AsyncSession,
        ignore_model: AlertIgnoreModel
    ) -> ResponseUtil:
        """
        忽略告警
        
        Args:
            db: 数据库会话
            ignore_model: 忽略模型
            
        Returns:
            ResponseUtil: 响应结果
        """
        alert_ids = [int(id_str) for id_str in ignore_model.alert_ids.split(',') if id_str]
        
        if not alert_ids:
            return ResponseUtil.failure(msg="请选择要忽略的告警")
        
        try:
            success = await AlertDao.ignore_alerts(
                db,
                alert_ids,
                ignore_model.operator,
                ignore_model.ignore_reason
            )
            
            if success:
                logger.info(f"成功忽略告警: {alert_ids}")
                return ResponseUtil.success(msg="忽略告警成功")
            else:
                return ResponseUtil.failure(msg="忽略告警失败")
        except Exception as e:
            logger.error(f"忽略告警失败: {str(e)}")
            return ResponseUtil.failure(msg="忽略告警失败")
    
    @classmethod
    async def get_alert_statistics_services(cls, db: AsyncSession, days: int = 7) -> AlertStatisticsModel:
        """
        获取告警统计信息
        
        Args:
            db: 数据库会话
            days: 统计天数
            
        Returns:
            AlertStatisticsModel: 统计信息
        """
        stats = await AlertDao.get_alert_statistics(db, days)
        
        return AlertStatisticsModel(
            total_alerts=stats['total_alerts'],
            urgent_alerts=stats['urgent_alerts'],
            scheduled_alerts=stats['scheduled_alerts'],
            active_alerts=stats['active_alerts'],
            resolved_alerts=stats['resolved_alerts'],
            ignored_alerts=stats['ignored_alerts']
        )
    
    @classmethod
    async def get_alert_trend_services(cls, db: AsyncSession, days: int = 7) -> List[AlertTrendModel]:
        """
        获取告警趋势数据
        
        Args:
            db: 数据库会话
            days: 统计天数
            
        Returns:
            List[AlertTrendModel]: 趋势数据
        """
        trend_data = await AlertDao.get_alert_trend(db, days)
        
        return [
            AlertTrendModel(
                date=item['date'],
                urgent_count=item['urgent_count'],
                scheduled_count=item['scheduled_count'],
                total_count=item['total_count']
            )
            for item in trend_data
        ]
    
    @classmethod
    async def get_realtime_alerts_services(cls, db: AsyncSession, limit: int = 10) -> List[RealtimeAlertModel]:
        """
        获取实时告警列表
        
        Args:
            db: 数据库会话
            limit: 返回数量限制
            
        Returns:
            List[RealtimeAlertModel]: 实时告警列表
        """
        alerts = await AlertDao.get_realtime_alerts(db, limit)
        
        return [
            RealtimeAlertModel(
                device_id=alert.device_id,
                hostname=alert.hostname,
                business_ip=alert.business_ip,
                component_type=alert.component_type,
                component_name=alert.component_name,
                health_status=alert.health_status,
                alert_level=alert.alert_level,
                last_occurrence=alert.last_occurrence
            )
            for alert in alerts
        ]
    
    @classmethod
    async def get_scheduled_alerts_services(cls, db: AsyncSession, limit: int = 10) -> List[ScheduledAlertModel]:
        """
        获取择期告警列表
        
        Args:
            db: 数据库会话
            limit: 返回数量限制
            
        Returns:
            List[ScheduledAlertModel]: 择期告警列表
        """
        alerts = await AlertDao.get_scheduled_alerts(db, limit)
        
        return [
            ScheduledAlertModel(
                device_id=alert.device_id,
                hostname=alert.hostname,
                business_ip=alert.business_ip,
                component_type=alert.component_type,
                component_name=alert.component_name,
                health_status=alert.health_status,
                alert_message=alert.alert_message,
                first_occurrence=alert.first_occurrence,
                occurrence_count=alert.occurrence_count
            )
            for alert in alerts
        ]
    
    @classmethod
    async def get_alert_distribution_services(cls, db: AsyncSession) -> AlertDistributionModel:
        """
        获取告警分布统计
        
        Args:
            db: 数据库会话
            
        Returns:
            AlertDistributionModel: 分布统计
        """
        distribution = await AlertDao.get_alert_distribution(db)
        
        return AlertDistributionModel(
            by_level=distribution['by_level'],
            by_component=distribution['by_component'],
            by_location=distribution['by_location'],
            by_manufacturer=distribution['by_manufacturer']
        )
    
    @classmethod
    async def create_or_update_alert_services(
        cls,
        db: AsyncSession,
        device_id: int,
        component_type: str,
        component_name: str,
        health_status: str,
        alert_message: str,
        alert_level: str
    ) -> Optional[int]:
        """
        创建或更新告警（由监控系统调用）
        
        Args:
            db: 数据库会话
            device_id: 设备ID
            component_type: 组件类型
            component_name: 组件名称
            health_status: 健康状态
            alert_message: 告警消息
            alert_level: 告警级别
            
        Returns:
            Optional[int]: 告警ID
        """
        try:
            alert = await AlertDao.get_or_create_alert(
                db,
                device_id,
                component_type,
                component_name,
                health_status,
                alert_message,
                alert_level
            )
            return alert.alert_id
        except Exception as e:
            logger.error(f"创建或更新告警失败: {str(e)}")
            return None
    
    @classmethod
    async def get_device_alerts_services(cls, db: AsyncSession, device_id: int) -> List[Dict[str, Any]]:
        """
        获取设备的所有活跃告警
        
        Args:
            db: 数据库会话
            device_id: 设备ID
            
        Returns:
            List[Dict[str, Any]]: 告警列表
        """
        query_object = AlertPageQueryModel(
            device_id=device_id,
            status='active',
            page_num=0,
            page_size=1000
        )
        
        alerts, _ = await AlertDao.get_alert_list(db, query_object, is_page=False)
        
        return [
            {
                'alert_id': alert.alert_id,
                'component_type': alert.component_type,
                'component_name': alert.component_name,
                'health_status': alert.health_status,
                'alert_level': alert.alert_level,
                'alert_message': alert.alert_message,
                'first_occurrence': alert.first_occurrence,
                'last_occurrence': alert.last_occurrence,
                'occurrence_count': alert.occurrence_count
            }
            for alert in alerts
        ] 