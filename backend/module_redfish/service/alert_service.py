"""
告警管理Service层
"""
import math
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from module_redfish.dao.alert_dao import AlertDao
from module_redfish.entity.vo.alert_vo import (
    AlertPageQueryModel,
    AlertStatisticsModel, AlertTrendModel, RealtimeAlertModel, ScheduledAlertModel,
    AlertDistributionModel, MaintenanceScheduleModel, MaintenanceUpdateModel, 
    BatchMaintenanceUpdateModel, MaintenancePageQueryModel
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
        
        # 转换为驼峰命名
        from utils.common_util import CamelCaseUtil
        alert_camel = CamelCaseUtil.transform_result([alert])[0] if alert else alert
        
        return ResponseUtil.success(data=alert_camel)
    
    # 精简版移除手动解决和忽略告警功能，告警状态由监控系统自动管理
    
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
                device_id=alert['device_id'],
                hostname=alert['hostname'],
                business_ip=alert['business_ip'],
                component_type=alert['component_type'],
                component_name=alert['component_name'],
                health_status=alert['health_status'],
                urgency_level=alert['urgency_level'],
                last_occurrence=alert['last_occurrence']
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
                device_id=alert['device_id'],
                hostname=alert['hostname'],
                business_ip=alert['business_ip'],
                component_type=alert['component_type'],
                component_name=alert['component_name'],
                health_status=alert['health_status'],
                alert_message="",  # 优化版DAO中没有alert_message字段
                first_occurrence=alert['first_occurrence'],
                occurrence_count=1  # 优化版DAO中没有occurrence_count字段，使用默认值
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
            byLevel=distribution['by_level'],
            byComponent=distribution['by_component'],
            byLocation=distribution['by_location'],
            byManufacturer=distribution['by_manufacturer']
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
        urgency_level: str
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
            urgency_level: 紧急程度
            
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
                'urgency_level': alert.urgency_level,
                'alert_message': alert.alert_message,
                'first_occurrence': alert.first_occurrence,
                'last_occurrence': alert.last_occurrence,
                'occurrence_count': alert.occurrence_count
            }
            for alert in alerts
        ]

    @classmethod
    async def schedule_maintenance_services(
        cls,
        db: AsyncSession,
        maintenance_schedule: MaintenanceScheduleModel
    ) -> ResponseUtil:
        """
        为告警安排维修时间
        
        Args:
            db: 数据库会话
            maintenance_schedule: 维修计划模型
            
        Returns:
            ResponseUtil: 响应结果
        """
        try:
            maintenance_data = {
                'scheduled_maintenance_time': maintenance_schedule.scheduled_maintenance_time,
                'maintenance_description': maintenance_schedule.maintenance_description,
                'maintenance_notes': maintenance_schedule.maintenance_notes
            }
            
            success = await AlertDao.schedule_maintenance(
                db, 
                maintenance_schedule.alert_id, 
                maintenance_data
            )
            
            if success:
                logger.info(f"成功为告警 {maintenance_schedule.alert_id} 安排维修时间")
                return ResponseUtil.success(msg="安排维修时间成功")
            else:
                return ResponseUtil.failure(msg="告警不存在或安排维修时间失败")
                
        except Exception as e:
            logger.error(f"安排维修时间失败: {str(e)}")
            return ResponseUtil.failure(msg="安排维修时间失败")

    @classmethod
    async def update_maintenance_services(
        cls,
        db: AsyncSession,
        maintenance_update: MaintenanceUpdateModel
    ) -> ResponseUtil:
        """
        更新告警维修计划
        
        Args:
            db: 数据库会话
            maintenance_update: 维修更新模型
            
        Returns:
            ResponseUtil: 响应结果
        """
        try:
            maintenance_data = {}
            
            # 只包含非None的字段
            if maintenance_update.scheduled_maintenance_time is not None:
                maintenance_data['scheduled_maintenance_time'] = maintenance_update.scheduled_maintenance_time
            if maintenance_update.maintenance_description is not None:
                maintenance_data['maintenance_description'] = maintenance_update.maintenance_description
            if maintenance_update.maintenance_status is not None:
                maintenance_data['maintenance_status'] = maintenance_update.maintenance_status
            if maintenance_update.maintenance_notes is not None:
                maintenance_data['maintenance_notes'] = maintenance_update.maintenance_notes
            
            success = await AlertDao.update_maintenance(
                db, 
                maintenance_update.alert_id, 
                maintenance_data,
                'system'  # 占位符，实际不使用
            )
            
            if success:
                logger.info(f"成功更新告警 {maintenance_update.alert_id} 的维修计划")
                return ResponseUtil.success(msg="更新维修计划成功")
            else:
                return ResponseUtil.failure(msg="告警不存在或更新维修计划失败")
                
        except Exception as e:
            logger.error(f"更新维修计划失败: {str(e)}")
            return ResponseUtil.failure(msg="更新维修计划失败")

    @classmethod
    async def batch_schedule_maintenance_services(
        cls,
        db: AsyncSession,
        batch_maintenance: BatchMaintenanceUpdateModel
    ) -> ResponseUtil:
        """
        批量安排维修时间
        
        Args:
            db: 数据库会话
            batch_maintenance: 批量维修模型
            
        Returns:
            ResponseUtil: 响应结果
        """
        try:
            maintenance_data = {}
            
            # 只包含非None的字段
            if batch_maintenance.scheduled_maintenance_time is not None:
                maintenance_data['scheduled_maintenance_time'] = batch_maintenance.scheduled_maintenance_time
            if batch_maintenance.maintenance_description is not None:
                maintenance_data['maintenance_description'] = batch_maintenance.maintenance_description
            if batch_maintenance.maintenance_status is not None:
                maintenance_data['maintenance_status'] = batch_maintenance.maintenance_status
            if batch_maintenance.maintenance_notes is not None:
                maintenance_data['maintenance_notes'] = batch_maintenance.maintenance_notes
            
            # 移除audit字段，直接调用DAO方法
            updated_count = await AlertDao.batch_schedule_maintenance(
                db, 
                batch_maintenance.alert_ids, 
                maintenance_data
            )
            
            if updated_count > 0:
                logger.info(f"成功批量安排维修时间，更新了 {updated_count} 条记录")
                return ResponseUtil.success(msg=f"批量安排维修时间成功，更新了 {updated_count} 条记录")
            else:
                return ResponseUtil.failure(msg="没有找到符合条件的告警记录")
                
        except Exception as e:
            logger.error(f"批量安排维修时间失败: {str(e)}")
            return ResponseUtil.failure(msg="批量安排维修时间失败")

    @classmethod
    async def get_maintenance_schedule_services(
        cls,
        db: AsyncSession,
        query_object: MaintenancePageQueryModel
    ) -> PageResponseModel:
        """
        获取维修计划列表
        
        Args:
            db: 数据库会话
            query_object: 查询对象
            
        Returns:
            PageResponseModel: 分页响应
        """
        try:
            query_dict = {}
            if query_object.device_id:
                query_dict['device_id'] = query_object.device_id
            if query_object.maintenance_status:
                query_dict['maintenance_status'] = query_object.maintenance_status
            if query_object.scheduled_start_time:
                query_dict['scheduled_start_time'] = query_object.scheduled_start_time
            if query_object.scheduled_end_time:
                query_dict['scheduled_end_time'] = query_object.scheduled_end_time
            
            maintenance_list, total = await AlertDao.get_maintenance_schedule(
                db, 
                query_dict,
                query_object.page_num,
                query_object.page_size
            )
            
            # 使用现有的分页方法创建分页响应
            has_next = math.ceil(total / query_object.page_size) > query_object.page_num if total > 0 else False
            from utils.common_util import CamelCaseUtil
            return PageResponseModel(
                rows=CamelCaseUtil.transform_result(maintenance_list),
                pageNum=query_object.page_num,
                pageSize=query_object.page_size,
                total=total,
                hasNext=has_next
            )
            
        except Exception as e:
            logger.error(f"获取维修计划列表失败: {str(e)}")
            raise

    @classmethod
    async def cancel_maintenance_services(
        cls,
        db: AsyncSession,
        alert_id: int,
        operator: str
    ) -> ResponseUtil:
        """
        取消告警维修计划
        
        Args:
            db: 数据库会话
            alert_id: 告警ID
            operator: 操作人
            
        Returns:
            ResponseUtil: 响应结果
        """
        try:
            maintenance_data = {
                'maintenance_status': 'cancelled'
            }
            
            success = await AlertDao.update_maintenance(
                db, 
                alert_id, 
                maintenance_data,
                operator
            )
            
            if success:
                logger.info(f"成功取消告警 {alert_id} 的维修计划")
                return ResponseUtil.success(msg="取消维修计划成功")
            else:
                return ResponseUtil.failure(msg="告警不存在或取消维修计划失败")
                
        except Exception as e:
            logger.error(f"取消维修计划失败: {str(e)}")
            return ResponseUtil.failure(msg="取消维修计划失败")

    @classmethod
    async def get_calendar_maintenance_services(
        cls,
        db: AsyncSession,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        获取日历视图的维修计划数据
        
        Args:
            db: 数据库会话
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[Dict[str, Any]]: 维修计划列表
        """
        try:
            # 获取指定时间范围内的维修计划
            maintenance_list = await AlertDao.get_calendar_maintenance(db, start_date, end_date)
            
            # 转换为前端需要的格式
            result = []
            for maintenance in maintenance_list:
                result.append({
                    'alert_id': maintenance.alert_id,
                    'hostname': maintenance.hostname,
                    'business_ip': maintenance.business_ip,
                    'component_type': maintenance.component_type,
                    'component_name': maintenance.component_name,
                    'urgency_level': maintenance.urgency_level,
                    'health_status': maintenance.health_status,
                    'alert_status': maintenance.alert_status,
                    'alert_message': f"{maintenance.component_type} 组件健康状态异常",  # 生成默认告警消息
                    'scheduled_maintenance_time': maintenance.scheduled_maintenance_time.isoformat() if maintenance.scheduled_maintenance_time else None,
                    'maintenance_status': maintenance.maintenance_status,
                    'maintenance_description': maintenance.maintenance_description,
                    'maintenance_notes': maintenance.maintenance_notes,
                    'first_occurrence': maintenance.first_occurrence.isoformat() if maintenance.first_occurrence else None,
                    'last_occurrence': maintenance.last_occurrence.isoformat() if maintenance.last_occurrence else None,
                    'occurrence_count': 1  # 由于AlertInfo表没有此字段，设为默认值
                })
            
            # 应用字段名转换（下划线转驼峰）
            from utils.common_util import CamelCaseUtil
            return CamelCaseUtil.transform_result(result)
            
        except Exception as e:
            logger.error(f"获取日历维修计划失败: {str(e)}")
            raise 