"""
硬件更换排期DAO（轻量化方案）
基于现有告警系统扩展，主要操作AlertInfo表
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from module_redfish.models import AlertInfo, DeviceInfo, BusinessHardwareUrgencyRules
from module_redfish.entity.vo.maintenance_vo import (
    MaintenanceScheduleQueryModel,
    MaintenanceSchedulePageQueryModel,
    MaintenanceScheduleStatisticsModel,
    MaintenanceCalendarModel,
    MaintenanceStrategyConfigModel
)


class MaintenanceDao:
    """维护排期数据访问对象（轻量化方案）"""

    @staticmethod
    async def get_maintenance_schedule_list(
        db: AsyncSession,
        query_object: MaintenanceSchedulePageQueryModel,
        is_page: bool = False
    ) -> Tuple[List[AlertInfo], int]:
        """
        获取维护排期列表（基于告警信息）
        
        Args:
            db: 数据库会话
            query_object: 查询对象
            is_page: 是否分页
            
        Returns:
            Tuple[List[AlertInfo], int]: 排期列表和总数
        """
        # 构建查询条件
        conditions = []
        
        # 只查询有效的告警（未解决或需要排期的）
        conditions.append(AlertInfo.alert_status.in_(['active', 'acknowledged', 'scheduled']))
        
        if query_object.device_id:
            conditions.append(AlertInfo.device_id == query_object.device_id)
            
        if query_object.hostname:
            # 关联设备表查询主机名
            conditions.append(DeviceInfo.hostname.like(f'%{query_object.hostname}%'))
            
        if query_object.business_ip:
            # 关联设备表查询业务IP
            conditions.append(DeviceInfo.business_ip.like(f'%{query_object.business_ip}%'))
            
        if query_object.component_type:
            conditions.append(AlertInfo.component_type.like(f'%{query_object.component_type}%'))
            
        if query_object.urgency_level:
            conditions.append(AlertInfo.urgency_level == query_object.urgency_level)
            
        # 处理前端传来的maintenance_status，映射到alert_status
        if query_object.maintenance_status:
            conditions.append(AlertInfo.alert_status == query_object.maintenance_status)
        elif query_object.status:
            conditions.append(AlertInfo.alert_status == query_object.status)
            
        if query_object.responsible_person:
            # 在resolution_note中搜索负责人信息
            conditions.append(AlertInfo.resolution_note.like(f'%{query_object.responsible_person}%'))
            
        if query_object.scheduled_date_start:
            conditions.append(AlertInfo.resolved_time >= query_object.scheduled_date_start)
            
        if query_object.scheduled_date_end:
            conditions.append(AlertInfo.resolved_time <= query_object.scheduled_date_end)

        # 构建查询 - 需要显式JOIN设备表以支持设备字段的查询条件
        if query_object.hostname or query_object.business_ip:
            # 如果有设备相关的查询条件，显式JOIN设备表
            query = select(AlertInfo).options(
                joinedload(AlertInfo.device)
            ).join(DeviceInfo, AlertInfo.device_id == DeviceInfo.device_id).where(and_(*conditions))
            
            # 总数查询也需要JOIN
            count_query = select(func.count(AlertInfo.alert_id)).join(
                DeviceInfo, AlertInfo.device_id == DeviceInfo.device_id
            ).where(and_(*conditions))
        else:
            # 没有设备相关查询条件时，使用原有方式
            query = select(AlertInfo).options(
                joinedload(AlertInfo.device)
            ).where(and_(*conditions))
            
            count_query = select(func.count(AlertInfo.alert_id)).where(and_(*conditions))
        
        # 排序
        query = query.order_by(AlertInfo.first_occurrence.desc())
        
        # 获取总数
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页
        if is_page:
            offset = (query_object.page_num - 1) * query_object.page_size
            query = query.offset(offset).limit(query_object.page_size)
        
        # 执行查询
        result = await db.execute(query)
        maintenance_list = result.scalars().all()
        
        return maintenance_list, total

    @staticmethod
    async def get_maintenance_schedule_by_id(db: AsyncSession, alert_id: int) -> Optional[AlertInfo]:
        """
        根据告警ID获取维护排期详情
        
        Args:
            db: 数据库会话
            alert_id: 告警ID
            
        Returns:
            Optional[AlertInfo]: 排期详情
        """
        query = select(AlertInfo).options(
            joinedload(AlertInfo.device),
            selectinload(AlertInfo.logs)
        ).where(AlertInfo.alert_id == alert_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_maintenance_schedule(
        db: AsyncSession,
        device_id: int,
        component_type: str,
        component_name: Optional[str],
        urgency_level: str,
        responsible_person: str,
        description: Optional[str] = None,
        scheduled_date: Optional[datetime] = None
    ) -> AlertInfo:
        """
        创建维护排期（创建告警记录）
        
        Args:
            db: 数据库会话
            device_id: 设备ID
            component_type: 组件类型
            component_name: 组件名称
            urgency_level: 紧急程度
            responsible_person: 负责人
            description: 描述
            scheduled_date: 计划时间
            
        Returns:
            AlertInfo: 创建的告警记录
        """
        # 计算排期时间
        if not scheduled_date:
            scheduled_date = MaintenanceDao._calculate_scheduled_date(urgency_level)
        
        # 创建告警记录作为排期
        alert = AlertInfo(
            device_id=device_id,
            alert_source='maintenance',
            component_type=component_type,
            component_name=component_name or component_type,
            urgency_level=urgency_level,
            alert_type='maintenance',
            alert_message=description or f'{component_type}需要维护',
            alert_status='scheduled',
            first_occurrence=datetime.now(),
            last_occurrence=datetime.now(),
            resolved_time=scheduled_date,
            resolution_note=f'负责人: {responsible_person}'
        )
        
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        
        return alert

    @staticmethod
    async def update_maintenance_schedule(
        db: AsyncSession,
        alert_id: int,
        **kwargs
    ) -> bool:
        """
        更新维护排期
        
        Args:
            db: 数据库会话
            alert_id: 告警ID
            **kwargs: 更新字段
            
        Returns:
            bool: 是否更新成功
        """
        query = select(AlertInfo).where(AlertInfo.alert_id == alert_id)
        result = await db.execute(query)
        alert = result.scalar_one_or_none()
        
        if not alert:
            return False
        
        # 直接更新所有字段（已经在Service层做了映射）
        for key, value in kwargs.items():
            if value is not None and hasattr(alert, key):
                setattr(alert, key, value)
        
        alert.update_time = datetime.now()
        await db.commit()
        return True

    @staticmethod
    async def delete_maintenance_schedule(db: AsyncSession, alert_id: int) -> bool:
        """
        删除维护排期
        
        Args:
            db: 数据库会话
            alert_id: 告警ID
            
        Returns:
            bool: 是否删除成功
        """
        query = select(AlertInfo).where(AlertInfo.alert_id == alert_id)
        result = await db.execute(query)
        alert = result.scalar_one_or_none()
        
        if not alert:
            return False
        
        await db.delete(alert)
        await db.commit()
        return True

    @staticmethod
    async def get_maintenance_statistics(db: AsyncSession) -> Dict[str, Any]:
        """
        获取维护排期统计信息
        
        Args:
            db: 数据库会话
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        # 基础统计查询
        base_conditions = [
            AlertInfo.alert_status.in_(['active', 'acknowledged', 'scheduled', 'resolved'])
        ]
        
        # 总排期数
        total_query = select(func.count(AlertInfo.alert_id)).where(and_(*base_conditions))
        total_result = await db.execute(total_query)
        total_schedules = total_result.scalar() or 0
        
        # 按状态统计
        status_query = select(
            AlertInfo.alert_status,
            func.count(AlertInfo.alert_id).label('count')
        ).where(and_(*base_conditions)).group_by(AlertInfo.alert_status)
        
        status_result = await db.execute(status_query)
        status_stats = {row.alert_status: row.count for row in status_result}
        
        # 按紧急程度统计
        urgency_query = select(
            AlertInfo.urgency_level,
            func.count(AlertInfo.alert_id).label('count')
        ).where(and_(*base_conditions)).group_by(AlertInfo.urgency_level)
        
        urgency_result = await db.execute(urgency_query)
        urgency_stats = {row.urgency_level: row.count for row in urgency_result}
        
        # 逾期统计
        now = datetime.now()
        overdue_query = select(func.count(AlertInfo.alert_id)).where(
            and_(
                AlertInfo.alert_status.in_(['active', 'acknowledged', 'scheduled']),
                AlertInfo.resolved_time < now
            )
        )
        overdue_result = await db.execute(overdue_query)
        overdue_schedules = overdue_result.scalar() or 0
        
        return {
            'total_schedules': total_schedules,
            'pending_schedules': status_stats.get('active', 0) + status_stats.get('acknowledged', 0),
            'in_progress_schedules': status_stats.get('scheduled', 0),
            'completed_schedules': status_stats.get('resolved', 0),
            'immediate_schedules': urgency_stats.get('immediate', 0),
            'urgent_schedules': urgency_stats.get('urgent', 0),
            'scheduled_schedules': urgency_stats.get('scheduled', 0),
            'overdue_schedules': overdue_schedules
        }

    @staticmethod
    async def get_calendar_data(
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        获取维护日历数据
        
        Args:
            db: 数据库会话
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[Dict[str, Any]]: 日历数据
        """
        query = select(AlertInfo).options(
            joinedload(AlertInfo.device)
        ).where(
            and_(
                AlertInfo.alert_status.in_(['active', 'acknowledged', 'scheduled']),
                AlertInfo.resolved_time >= start_date,
                AlertInfo.resolved_time <= end_date
            )
        ).order_by(AlertInfo.resolved_time)
        
        result = await db.execute(query)
        schedules = result.scalars().all()
        
        # 按日期分组
        calendar_data = {}
        for schedule in schedules:
            if schedule.resolved_time:
                date_str = schedule.resolved_time.strftime('%Y-%m-%d')
                if date_str not in calendar_data:
                    calendar_data[date_str] = {
                        'date': date_str,
                        'schedules': [],
                        'total_count': 0,
                        'immediate_count': 0,
                        'urgent_count': 0,
                        'scheduled_count': 0
                    }
                
                schedule_data = {
                    'alert_id': schedule.alert_id,
                    'hostname': schedule.device.hostname if schedule.device else '',
                    'component_type': schedule.component_type,
                    'component_name': schedule.component_name,
                    'urgency_level': schedule.urgency_level,
                    'responsible_person': MaintenanceDao._extract_responsible_person(schedule.resolution_note),
                    'status': schedule.alert_status
                }
                
                calendar_data[date_str]['schedules'].append(schedule_data)
                calendar_data[date_str]['total_count'] += 1
                
                # 按紧急程度计数
                if schedule.urgency_level == 'immediate':
                    calendar_data[date_str]['immediate_count'] += 1
                elif schedule.urgency_level == 'urgent':
                    calendar_data[date_str]['urgent_count'] += 1
                elif schedule.urgency_level == 'scheduled':
                    calendar_data[date_str]['scheduled_count'] += 1
        
        return list(calendar_data.values())

    @staticmethod
    async def batch_update_schedules(
        db: AsyncSession,
        alert_ids: List[int],
        **kwargs
    ) -> int:
        """
        批量更新排期
        
        Args:
            db: 数据库会话
            alert_ids: 告警ID列表
            **kwargs: 更新字段
            
        Returns:
            int: 成功更新的数量
        """
        success_count = 0
        for alert_id in alert_ids:
            if await MaintenanceDao.update_maintenance_schedule(db, alert_id, **kwargs):
                success_count += 1
        
        return success_count

    @staticmethod
    def _calculate_scheduled_date(urgency_level: str) -> datetime:
        """
        根据紧急程度计算排期时间
        
        Args:
            urgency_level: 紧急程度
            
        Returns:
            datetime: 计算出的排期时间
        """
        now = datetime.now()
        
        if urgency_level == 'immediate':
            # 立即处理
            return now
        elif urgency_level == 'urgent':
            # 24小时内处理
            return now + timedelta(hours=24)
        else:  # scheduled
            # 择期处理，安排到下个周六凌晨2点
            days_until_saturday = (5 - now.weekday()) % 7
            if days_until_saturday == 0 and now.hour >= 6:
                # 如果今天是周六且已过维护窗口，安排到下周六
                days_until_saturday = 7
            
            next_saturday = now + timedelta(days=days_until_saturday)
            return next_saturday.replace(hour=2, minute=0, second=0, microsecond=0)

    @staticmethod
    def _extract_responsible_person(resolution_note: Optional[str]) -> Optional[str]:
        """
        从resolution_note中提取负责人信息
        
        Args:
            resolution_note: 解决说明
            
        Returns:
            Optional[str]: 负责人
        """
        if not resolution_note:
            return None
        
        if '负责人:' in resolution_note:
            parts = resolution_note.split('负责人:')
            if len(parts) > 1:
                return parts[1].split('\n')[0].strip()
        
        return None

    @staticmethod
    async def get_urgency_level_options() -> List[Dict[str, Any]]:
        """
        获取紧急程度选项列表
        
        Returns:
            List[Dict[str, Any]]: 紧急程度选项
        """
        return [
            {
                'value': 'immediate',
                'label': '立即修复',
                'description': '核心业务，立即处理',
                'duration_minutes': 0,
                'color': '#f56565'  # 红色
            },
            {
                'value': 'urgent',
                'label': '24小时内修复',
                'description': '重要业务，24小时内处理',
                'duration_minutes': 1440,
                'color': '#ed8936'  # 橙色
            },
            {
                'value': 'scheduled',
                'label': '择期修复',
                'description': '普通业务，安排维护窗口处理',
                'duration_minutes': 10080,  # 一周
                'color': '#38a169'  # 绿色
            }
        ] 