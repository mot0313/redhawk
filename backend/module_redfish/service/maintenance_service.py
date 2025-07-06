"""
硬件更换排期Service（轻量化方案）
基于现有告警系统扩展，提供排期管理业务逻辑
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from utils.response_util import ResponseUtil
from utils.page_util import PageResponseModel
from module_redfish.dao.maintenance_dao import MaintenanceDao
from module_redfish.dao.business_rule_dao import BusinessRuleDao
from module_redfish.entity.vo.maintenance_vo import (
    MaintenanceScheduleModel,
    MaintenanceSchedulePageQueryModel,
    CreateMaintenanceScheduleModel,
    UpdateMaintenanceScheduleModel,
    MaintenanceScheduleStatisticsModel,
    MaintenanceCalendarModel,
    BatchUpdateScheduleModel,
    MaintenanceReportModel,
    UrgencyLevelOption
)
from module_redfish.models import AlertInfo, DeviceInfo

logger = logging.getLogger(__name__)


class MaintenanceService:
    """维护排期服务类（轻量化方案）"""

    @classmethod
    async def get_maintenance_schedule_list_services(
        cls,
        db: AsyncSession,
        query_object: MaintenanceSchedulePageQueryModel,
        is_page: bool = False
    ) -> PageResponseModel:
        """
        获取维护排期列表
        
        Args:
            db: 数据库会话
            query_object: 查询对象
            is_page: 是否分页
            
        Returns:
            PageResponseModel: 分页响应数据
        """
        try:
            # 获取排期列表数据
            maintenance_list, total = await MaintenanceDao.get_maintenance_schedule_list(
                db, query_object, is_page
            )
            
            # 转换为响应模型
            maintenance_schedule_list = []
            for alert in maintenance_list:
                schedule_data = await cls._convert_alert_to_schedule_model(alert)
                maintenance_schedule_list.append(schedule_data)
            
            # 构造分页响应
            if is_page:
                page_response = PageResponseModel(
                    rows=maintenance_schedule_list,
                    page_num=query_object.page_num,
                    page_size=query_object.page_size,
                    total=total,
                    has_next=query_object.page_num * query_object.page_size < total
                )
            else:
                page_response = PageResponseModel(
                    rows=maintenance_schedule_list,
                    page_num=1,
                    page_size=len(maintenance_schedule_list),
                    total=total,
                    has_next=False
                )
            
            return page_response
            
        except Exception as e:
            logger.error(f"获取维护排期列表失败: {str(e)}")
            return PageResponseModel(rows=[], page_num=1, page_size=10, total=0, has_next=False)

    @classmethod
    async def get_maintenance_schedule_detail_services(
        cls,
        db: AsyncSession,
        alert_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        获取维护排期详情
        
        Args:
            db: 数据库会话
            alert_id: 告警ID
            
        Returns:
            Optional[Dict[str, Any]]: 排期详情
        """
        try:
            alert = await MaintenanceDao.get_maintenance_schedule_by_id(db, alert_id)
            if not alert:
                return None
            
            # 获取设备信息
            device_info = None
            if alert.device:
                device_info = {
                    'deviceId': alert.device.device_id,
                    'hostname': alert.device.hostname,
                    'businessIp': alert.device.business_ip,
                    'location': alert.device.location,
                    'businessType': alert.device.business_type
                }
            
            # 获取相关告警日志
            alert_logs = []
            if alert.logs:
                alert_logs = [
                    {
                        'logId': log.log_id,
                        'logMessage': log.log_message,
                        'occurrenceTime': log.occurrence_time,
                        'logLevel': log.log_level
                    }
                    for log in alert.logs
                ]
            
            # 转换为排期模型
            schedule_model = await cls._convert_alert_to_schedule_model(alert)
            
            # 直接返回包含设备信息的排期模型数据
            return schedule_model
            
        except Exception as e:
            logger.error(f"获取维护排期详情失败: {str(e)}")
            return None

    @classmethod
    async def create_maintenance_schedule_services(
        cls,
        db: AsyncSession,
        schedule_data: CreateMaintenanceScheduleModel
    ) -> ResponseUtil:
        """
        创建维护排期
        
        Args:
            db: 数据库会话
            schedule_data: 排期数据
            
        Returns:
            ResponseUtil: 响应结果
        """
        try:
            # 验证设备是否存在
            device = await cls._get_device_by_id(db, schedule_data.device_id)
            if not device:
                return ResponseUtil.failure(msg="设备不存在")
            
            # 如果没有指定负责人，使用设备的系统负责人
            responsible_person = schedule_data.responsible_person
            if not responsible_person and device.system_owner:
                responsible_person = device.system_owner
                logger.info(f"使用设备系统负责人: {responsible_person}")
            
            # 计算排期时间（如果未指定）
            scheduled_date = schedule_data.scheduled_date
            if not scheduled_date:
                scheduled_date = MaintenanceDao._calculate_scheduled_date(schedule_data.urgency_level)
            
            # 创建排期记录
            alert = await MaintenanceDao.create_maintenance_schedule(
                db=db,
                device_id=schedule_data.device_id,
                component_type=schedule_data.component_type,
                component_name=schedule_data.component_name,
                urgency_level=schedule_data.urgency_level,
                responsible_person=responsible_person,
                description=schedule_data.description,
                scheduled_date=scheduled_date
            )
            
            logger.info(f"成功创建维护排期: 设备ID={schedule_data.device_id}, 组件={schedule_data.component_type}, 负责人={responsible_person}")
            return ResponseUtil.success(
                data={'alertId': alert.alert_id},
                msg="创建维护排期成功"
            )
            
        except Exception as e:
            logger.error(f"创建维护排期失败: {str(e)}")
            return ResponseUtil.failure(msg="创建维护排期失败")

    @classmethod
    async def update_maintenance_schedule_services(
        cls,
        db: AsyncSession,
        update_data: UpdateMaintenanceScheduleModel
    ) -> ResponseUtil:
        """
        更新维护排期
        
        Args:
            db: 数据库会话
            update_data: 更新数据
            
        Returns:
            ResponseUtil: 响应结果
        """
        try:
            # 准备更新字段
            update_fields = {}
            
            # 如果更新了设备，需要获取新设备的信息
            device = None
            if update_data.device_id:
                device = await cls._get_device_by_id(db, update_data.device_id)
                if not device:
                    return ResponseUtil.failure(msg="设备不存在")
                update_fields['device_id'] = update_data.device_id
            
            if update_data.component_type:
                update_fields['component_type'] = update_data.component_type
            if update_data.component_name:
                update_fields['component_name'] = update_data.component_name
            if update_data.urgency_level:
                update_fields['urgency_level'] = update_data.urgency_level
            if update_data.scheduled_date:
                update_fields['resolved_time'] = update_data.scheduled_date  # 映射到resolved_time字段
            
            # 处理负责人更新逻辑
            responsible_person = update_data.responsible_person
            if update_data.device_id and device and device.system_owner and not responsible_person:
                # 如果更新了设备但没有指定负责人，使用新设备的系统负责人
                responsible_person = device.system_owner
                logger.info(f"设备更换，使用新设备系统负责人: {responsible_person}")
            
            if responsible_person:
                # 将负责人信息存储到resolution_note中
                current_note = f"负责人: {responsible_person}"
                if update_data.description:
                    current_note += f"\n描述: {update_data.description}"
                update_fields['resolution_note'] = current_note
            elif update_data.description:
                update_fields['alert_message'] = update_data.description
                
            if update_data.status:
                update_fields['alert_status'] = update_data.status  # 映射到alert_status字段
            
            # 执行更新
            success = await MaintenanceDao.update_maintenance_schedule(
                db, update_data.alert_id, **update_fields
            )
            
            if success:
                logger.info(f"成功更新维护排期: ID={update_data.alert_id}")
                return ResponseUtil.success(msg="更新维护排期成功")
            else:
                return ResponseUtil.failure(msg="维护排期不存在或更新失败")
                
        except Exception as e:
            logger.error(f"更新维护排期失败: {str(e)}")
            return ResponseUtil.failure(msg="更新维护排期失败")

    @classmethod
    async def delete_maintenance_schedule_services(
        cls,
        db: AsyncSession,
        alert_id: int
    ) -> ResponseUtil:
        """
        删除维护排期
        
        Args:
            db: 数据库会话
            alert_id: 告警ID
            
        Returns:
            ResponseUtil: 响应结果
        """
        try:
            success = await MaintenanceDao.delete_maintenance_schedule(db, alert_id)
            
            if success:
                logger.info(f"成功删除维护排期: ID={alert_id}")
                return ResponseUtil.success(msg="删除维护排期成功")
            else:
                return ResponseUtil.failure(msg="维护排期不存在或删除失败")
                
        except Exception as e:
            logger.error(f"删除维护排期失败: {str(e)}")
            return ResponseUtil.failure(msg="删除维护排期失败")

    @classmethod
    async def get_maintenance_statistics_services(cls, db: AsyncSession) -> MaintenanceScheduleStatisticsModel:
        """
        获取维护排期统计信息
        
        Args:
            db: 数据库会话
            
        Returns:
            MaintenanceScheduleStatisticsModel: 统计信息
        """
        try:
            stats = await MaintenanceDao.get_maintenance_statistics(db)
            
            return MaintenanceScheduleStatisticsModel(
                total_schedules=stats['total_schedules'],
                pending_schedules=stats['pending_schedules'],
                in_progress_schedules=stats['in_progress_schedules'],
                completed_schedules=stats['completed_schedules'],
                immediate_schedules=stats['immediate_schedules'],
                urgent_schedules=stats['urgent_schedules'],
                scheduled_schedules=stats['scheduled_schedules'],
                overdue_schedules=stats['overdue_schedules']
            )
            
        except Exception as e:
            logger.error(f"获取维护统计信息失败: {str(e)}")
            return MaintenanceScheduleStatisticsModel(
                total_schedules=0,
                pending_schedules=0,
                in_progress_schedules=0,
                completed_schedules=0,
                immediate_schedules=0,
                urgent_schedules=0,
                scheduled_schedules=0,
                overdue_schedules=0
            )

    @classmethod
    async def get_maintenance_calendar_services(
        cls,
        db: AsyncSession,
        year: int,
        month: int
    ) -> List[Dict[str, Any]]:
        """
        获取维护日历数据
        
        Args:
            db: 数据库会话
            year: 年份
            month: 月份
            
        Returns:
            List[Dict[str, Any]]: 日历数据
        """
        try:
            # 计算月份的开始和结束日期
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1) - timedelta(days=1)
            
            calendar_data = await MaintenanceDao.get_calendar_data(db, start_date, end_date)
            return calendar_data
            
        except Exception as e:
            logger.error(f"获取维护日历数据失败: {str(e)}")
            return []

    @classmethod
    async def batch_update_schedules_services(
        cls,
        db: AsyncSession,
        batch_data: BatchUpdateScheduleModel
    ) -> ResponseUtil:
        """
        批量更新排期
        
        Args:
            db: 数据库会话
            batch_data: 批量更新数据
            
        Returns:
            ResponseUtil: 响应结果
        """
        try:
            # 准备更新字段
            update_fields = {}
            if batch_data.responsible_person:
                update_fields['responsible_person'] = batch_data.responsible_person
            if batch_data.scheduled_date:
                update_fields['scheduled_date'] = batch_data.scheduled_date
            if batch_data.status:
                update_fields['status'] = batch_data.status
            
            # 执行批量更新
            success_count = await MaintenanceDao.batch_update_schedules(
                db, batch_data.alert_ids, **update_fields
            )
            
            logger.info(f"批量更新维护排期: 成功{success_count}/{len(batch_data.alert_ids)}条")
            return ResponseUtil.success(
                data={'successCount': success_count, 'totalCount': len(batch_data.alert_ids)},
                msg=f"批量更新成功：{success_count}/{len(batch_data.alert_ids)}条"
            )
            
        except Exception as e:
            logger.error(f"批量更新维护排期失败: {str(e)}")
            return ResponseUtil.failure(msg="批量更新维护排期失败")

    @classmethod
    async def get_urgency_level_options_services(cls) -> List[Dict[str, Any]]:
        """
        获取紧急程度选项
        
        Returns:
            List[Dict[str, Any]]: 紧急程度选项列表
        """
        return await MaintenanceDao.get_urgency_level_options()

    @classmethod
    async def auto_create_schedule_from_alert_services(
        cls,
        db: AsyncSession,
        alert_id: int
    ) -> ResponseUtil:
        """
        从告警自动创建排期
        
        Args:
            db: 数据库会话
            alert_id: 告警ID
            
        Returns:
            ResponseUtil: 响应结果
        """
        try:
            # 获取告警信息
            alert = await MaintenanceDao.get_maintenance_schedule_by_id(db, alert_id)
            if not alert or alert.alert_source == 'maintenance':
                return ResponseUtil.failure(msg="告警不存在或已是维护排期")
            
            # 获取设备信息
            device = alert.device
            if not device:
                return ResponseUtil.failure(msg="设备信息不存在")
            
            # 根据业务规则确定紧急程度
            urgency_result = await BusinessRuleDao.get_rule_by_type(
                db, device.business_type, alert.component_type
            )
            
            urgency_level = urgency_result.urgency_level if urgency_result else 'scheduled'
            
            # 更新告警为排期状态
            update_fields = {
                'alert_status': 'scheduled',
                'resolved_time': MaintenanceDao._calculate_scheduled_date(urgency_level),
                'resolution_note': f'负责人: {device.system_owner or "系统自动分配"}'
            }
            
            success = await MaintenanceDao.update_maintenance_schedule(
                db, alert_id, **update_fields
            )
            
            if success:
                logger.info(f"成功从告警创建排期: 告警ID={alert_id}, 紧急程度={urgency_level}")
                return ResponseUtil.success(msg="自动创建排期成功")
            else:
                return ResponseUtil.failure(msg="创建排期失败")
                
        except Exception as e:
            logger.error(f"从告警自动创建排期失败: {str(e)}")
            return ResponseUtil.failure(msg="自动创建排期失败")

    @classmethod
    async def generate_maintenance_report_services(
        cls,
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime
    ) -> MaintenanceReportModel:
        """
        生成维护报告
        
        Args:
            db: 数据库会话
            start_date: 开始时间
            end_date: 结束时间
            
        Returns:
            MaintenanceReportModel: 维护报告
        """
        try:
            # 获取统计数据
            stats = await MaintenanceDao.get_maintenance_statistics(db)
            
            # 计算完成率
            total_maintenance = stats['total_schedules']
            completed_maintenance = stats['completed_schedules']
            completion_rate = completed_maintenance / total_maintenance if total_maintenance > 0 else 0
            
            # 按紧急程度分组
            by_urgency = {
                'immediate': stats['immediate_schedules'],
                'urgent': stats['urgent_schedules'],
                'scheduled': stats['scheduled_schedules']
            }
            
            # 模拟按组件类型分组（可以进一步完善）
            by_component = {
                'cpu': 0,
                'memory': 0,
                'storage': 0,
                'power': 0,
                'fan': 0
            }
            
            return MaintenanceReportModel(
                period_start=start_date,
                period_end=end_date,
                total_maintenance=total_maintenance,
                completed_maintenance=completed_maintenance,
                completion_rate=completion_rate,
                avg_resolution_time=24.0,  # 默认24小时，可以根据实际数据计算
                by_urgency=by_urgency,
                by_component=by_component,
                overdue_count=stats['overdue_schedules']
            )
            
        except Exception as e:
            logger.error(f"生成维护报告失败: {str(e)}")
            return MaintenanceReportModel(
                period_start=start_date,
                period_end=end_date,
                total_maintenance=0,
                completed_maintenance=0,
                completion_rate=0.0,
                by_urgency={},
                by_component={},
                overdue_count=0
            )

    @classmethod
    async def _convert_alert_to_schedule_model(cls, alert: AlertInfo) -> Dict[str, Any]:
        """
        将AlertInfo转换为维护排期模型（驼峰格式）
        
        Args:
            alert: 告警信息
            
        Returns:
            Dict[str, Any]: 排期模型数据
        """
        return {
            'alertId': alert.alert_id,
            'deviceId': alert.device_id,
            'hostname': alert.device.hostname if alert.device else '',
            'businessIp': alert.device.business_ip if alert.device else '',
            'businessType': alert.device.business_type if alert.device else '',
            'componentType': alert.component_type,
            'componentName': alert.component_name,
            'urgencyLevel': alert.urgency_level,
            'scheduledDate': alert.resolved_time,
            'responsiblePerson': MaintenanceDao._extract_responsible_person(alert.resolution_note) or (alert.device.system_owner if alert.device else None),
            'maintenanceType': 'repair',  # 默认为维修
            'status': alert.alert_status,
            'description': alert.alert_message,
            'alertMessage': alert.alert_message,
            'firstOccurrence': alert.first_occurrence,
            'resolvedTime': alert.resolved_time,
            'resolutionNote': alert.resolution_note,
            'estimatedDuration': None  # 可以从resolution_note中解析
        }

    @classmethod
    async def _get_device_by_id(cls, db: AsyncSession, device_id: int) -> Optional[DeviceInfo]:
        """
        根据ID获取设备信息
        
        Args:
            db: 数据库会话
            device_id: 设备ID
            
        Returns:
            Optional[DeviceInfo]: 设备信息
        """
        from sqlalchemy import select
        query = select(DeviceInfo).where(DeviceInfo.device_id == device_id)
        result = await db.execute(query)
        return result.scalar_one_or_none() 