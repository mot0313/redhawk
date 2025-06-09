"""
告警管理DAO层
"""
from sqlalchemy import and_, or_, func, desc, asc, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from module_redfish.models import AlertInfo, DeviceInfo
from module_redfish.entity.vo.alert_vo import AlertPageQueryModel
from utils.page_util import PageUtil


class AlertDao:
    """告警管理DAO"""
    
    @classmethod
    async def get_alert_list(
        cls,
        db: AsyncSession,
        query_object: AlertPageQueryModel,
        is_page: bool = False
    ) -> Tuple[List[AlertInfo], int]:
        """
        获取告警列表
        
        Args:
            db: 数据库会话
            query_object: 查询对象
            is_page: 是否分页
            
        Returns:
            Tuple[List[AlertInfo], int]: 告警列表和总数
        """
        # 关联设备表查询
        query = select(AlertInfo).join(DeviceInfo, AlertInfo.device_id == DeviceInfo.device_id)
        
        # 构建查询条件
        conditions = []
        
        if query_object.device_id:
            conditions.append(AlertInfo.device_id == query_object.device_id)
        
        if query_object.hostname:
            conditions.append(DeviceInfo.hostname.like(f'%{query_object.hostname}%'))
        
        if query_object.business_ip:
            conditions.append(DeviceInfo.business_ip.like(f'%{query_object.business_ip}%'))
        
        if query_object.component_type:
            conditions.append(AlertInfo.component_type == query_object.component_type)
        
        if query_object.alert_level:
            conditions.append(AlertInfo.alert_level == query_object.alert_level)
        
        if query_object.health_status:
            conditions.append(AlertInfo.health_status == query_object.health_status)
        
        if query_object.alert_status:
            conditions.append(AlertInfo.alert_status == query_object.alert_status)
        
        if query_object.start_time:
            conditions.append(AlertInfo.first_occurrence >= query_object.start_time)
        
        if query_object.end_time:
            conditions.append(AlertInfo.last_occurrence <= query_object.end_time)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 排序：紧急告警优先，然后按最后发生时间倒序
        query = query.order_by(
            desc(AlertInfo.alert_level == 'urgent'),
            desc(AlertInfo.last_occurrence)
        )
        
        # 分页
        if is_page:
            # 获取总数
            count_query = select(func.count(AlertInfo.alert_id)).select_from(
                AlertInfo.__table__.join(DeviceInfo.__table__, AlertInfo.device_id == DeviceInfo.device_id)
            )
            if conditions:
                count_query = count_query.where(and_(*conditions))
            total_count = await db.scalar(count_query)
            
            # 分页查询
            query = query.offset(query_object.page_num).limit(query_object.page_size)
            result = await db.execute(query)
            alert_list = result.scalars().all()
            
            return alert_list, total_count
        else:
            result = await db.execute(query)
            alert_list = result.scalars().all()
            return alert_list, len(alert_list)
    
    @classmethod
    async def get_alert_by_id(cls, db: AsyncSession, alert_id: int) -> Optional[AlertInfo]:
        """
        根据ID获取告警信息
        
        Args:
            db: 数据库会话
            alert_id: 告警ID
            
        Returns:
            Optional[AlertInfo]: 告警信息
        """
        result = await db.execute(
            select(AlertInfo).where(AlertInfo.alert_id == alert_id)
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_or_create_alert(
        cls,
        db: AsyncSession,
        device_id: int,
        component_type: str,
        component_name: str,
        health_status: str,
        alert_message: str,
        alert_level: str
    ) -> AlertInfo:
        """
        获取或创建告警信息
        
        Args:
            db: 数据库会话
            device_id: 设备ID
            component_type: 组件类型
            component_name: 组件名称
            health_status: 健康状态
            alert_message: 告警消息
            alert_level: 告警级别
            
        Returns:
            AlertInfo: 告警信息
        """
        # 查找是否存在相同的活跃告警
        existing_alert = await db.execute(
            select(AlertInfo).where(
                and_(
                    AlertInfo.device_id == device_id,
                    AlertInfo.component_type == component_type,
                    AlertInfo.component_name == component_name,
                    AlertInfo.alert_status == 'active'
                )
            )
        )
        existing_alert = existing_alert.scalar_one_or_none()
        
        if existing_alert:
            # 更新现有告警
            existing_alert.health_status = health_status
            existing_alert.alert_message = alert_message
            existing_alert.alert_level = alert_level
            existing_alert.last_occurrence = datetime.now()
            existing_alert.occurrence_count += 1
            existing_alert.update_time = datetime.now()
            await db.commit()
            return existing_alert
        else:
            # 创建新告警
            # 获取设备信息
            device_result = await db.execute(
                select(DeviceInfo).where(DeviceInfo.device_id == device_id)
            )
            device = device_result.scalar_one()
            
            new_alert = AlertInfo(
                device_id=device_id,
                hostname=device.hostname,
                business_ip=device.business_ip,
                component_type=component_type,
                component_name=component_name,
                alert_level=alert_level,
                health_status=health_status,
                alert_message=alert_message,
                first_occurrence=datetime.now(),
                last_occurrence=datetime.now(),
                occurrence_count=1,
                alert_status='active',
                create_time=datetime.now(),
                update_time=datetime.now()
            )
            db.add(new_alert)
            await db.commit()
            await db.refresh(new_alert)
            return new_alert
    
    @classmethod
    async def resolve_alerts(cls, db: AsyncSession, alert_ids: List[int], resolved_by: str, resolved_note: str = None) -> bool:
        """
        解决告警
        
        Args:
            db: 数据库会话
            alert_ids: 告警ID列表
            resolved_by: 解决人
            resolved_note: 解决备注
            
        Returns:
            bool: 是否成功
        """
        await db.execute(
            update(AlertInfo).where(AlertInfo.alert_id.in_(alert_ids)).values(
                alert_status='resolved',
                resolved_by=resolved_by,
                resolved_time=datetime.now(),
                resolved_note=resolved_note,
                update_time=datetime.now()
            )
        )
        await db.commit()
        return True
    
    @classmethod
    async def ignore_alerts(cls, db: AsyncSession, alert_ids: List[int], operator: str, ignore_reason: str = None) -> bool:
        """
        忽略告警
        
        Args:
            db: 数据库会话
            alert_ids: 告警ID列表
            operator: 操作人
            ignore_reason: 忽略原因
            
        Returns:
            bool: 是否成功
        """
        await db.execute(
            update(AlertInfo).where(AlertInfo.alert_id.in_(alert_ids)).values(
                alert_status='ignored',
                resolved_by=operator,
                resolved_time=datetime.now(),
                resolved_note=ignore_reason,
                update_time=datetime.now()
            )
        )
        await db.commit()
        return True
    
    @classmethod
    async def manual_override_alert(
        cls,
        db: AsyncSession,
        alert_id: int,
        manual_level: str,
        manual_reason: str,
        manual_operator: str
    ) -> bool:
        """
        手动覆盖告警级别
        
        Args:
            db: 数据库会话
            alert_id: 告警ID
            manual_level: 手动设置级别
            manual_reason: 手动设置原因
            manual_operator: 手动操作人
            
        Returns:
            bool: 是否成功
        """
        await db.execute(
            update(AlertInfo).where(AlertInfo.alert_id == alert_id).values(
                is_manual_override=True,
                manual_level=manual_level,
                manual_reason=manual_reason,
                manual_operator=manual_operator,
                manual_time=datetime.now(),
                update_time=datetime.now()
            )
        )
        await db.commit()
        return True
    
    @classmethod
    async def get_alert_statistics(cls, db: AsyncSession, days: int = 7) -> Dict[str, int]:
        """
        获取告警统计信息
        
        Args:
            db: 数据库会话
            days: 统计天数
            
        Returns:
            Dict[str, int]: 统计信息
        """
        start_time = datetime.now() - timedelta(days=days)
        
        # 总告警数（指定天数内）
        total_result = await db.execute(
            select(func.count(AlertInfo.alert_id)).where(AlertInfo.first_occurrence >= start_time)
        )
        total_alerts = total_result.scalar()
        
        # 紧急告警数（指定天数内）
        urgent_result = await db.execute(
            select(func.count(AlertInfo.alert_id)).where(
                and_(
                    AlertInfo.first_occurrence >= start_time,
                    AlertInfo.alert_level == 'urgent'
                )
            )
        )
        urgent_alerts = urgent_result.scalar()
        
        # 择期告警数（指定天数内）
        scheduled_result = await db.execute(
            select(func.count(AlertInfo.alert_id)).where(
                and_(
                    AlertInfo.first_occurrence >= start_time,
                    AlertInfo.alert_level == 'scheduled'
                )
            )
        )
        scheduled_alerts = scheduled_result.scalar()
        
        # 当前活跃告警数
        active_result = await db.execute(
            select(func.count(AlertInfo.alert_id)).where(AlertInfo.alert_status == 'active')
        )
        active_alerts = active_result.scalar()
        
        # 已解决告警数
        resolved_result = await db.execute(
            select(func.count(AlertInfo.alert_id)).where(AlertInfo.alert_status == 'resolved')
        )
        resolved_alerts = resolved_result.scalar()
        
        # 已忽略告警数
        ignored_result = await db.execute(
            select(func.count(AlertInfo.alert_id)).where(AlertInfo.alert_status == 'ignored')
        )
        ignored_alerts = ignored_result.scalar()
        
        return {
            'total_alerts': total_alerts,
            'urgent_alerts': urgent_alerts,
            'scheduled_alerts': scheduled_alerts,
            'active_alerts': active_alerts,
            'resolved_alerts': resolved_alerts,
            'ignored_alerts': ignored_alerts
        }
    
    @classmethod
    async def get_alert_trend(cls, db: AsyncSession, days: int = 7) -> List[Dict[str, Any]]:
        """
        获取告警趋势数据
        
        Args:
            db: 数据库会话
            days: 统计天数
            
        Returns:
            List[Dict[str, Any]]: 趋势数据
        """
        start_date = datetime.now().date() - timedelta(days=days-1)
        
        trend_data = []
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            next_date = current_date + timedelta(days=1)
            
            # 当日紧急告警数
            urgent_result = await db.execute(
                select(func.count(AlertInfo.alert_id)).where(
                    and_(
                        AlertInfo.first_occurrence >= current_date,
                        AlertInfo.first_occurrence < next_date,
                        AlertInfo.alert_level == 'urgent'
                    )
                )
            )
            urgent_count = urgent_result.scalar()
            
            # 当日择期告警数
            scheduled_result = await db.execute(
                select(func.count(AlertInfo.alert_id)).where(
                    and_(
                        AlertInfo.first_occurrence >= current_date,
                        AlertInfo.first_occurrence < next_date,
                        AlertInfo.alert_level == 'scheduled'
                    )
                )
            )
            scheduled_count = scheduled_result.scalar()
            
            trend_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'urgent_count': urgent_count,
                'scheduled_count': scheduled_count,
                'total_count': urgent_count + scheduled_count
            })
        
        return trend_data
    
    @classmethod
    async def get_realtime_alerts(cls, db: AsyncSession, limit: int = 10) -> List[AlertInfo]:
        """
        获取实时告警列表
        
        Args:
            db: 数据库会话
            limit: 返回数量限制
            
        Returns:
            List[AlertInfo]: 实时告警列表
        """
        result = await db.execute(
            select(AlertInfo).where(
                and_(
                    AlertInfo.alert_status == 'active',
                    AlertInfo.alert_level == 'urgent'
                )
            ).order_by(desc(AlertInfo.last_occurrence)).limit(limit)
        )
        return result.scalars().all()
    
    @classmethod
    async def get_scheduled_alerts(cls, db: AsyncSession, limit: int = 10) -> List[AlertInfo]:
        """
        获取择期告警列表
        
        Args:
            db: 数据库会话
            limit: 返回数量限制
            
        Returns:
            List[AlertInfo]: 择期告警列表
        """
        result = await db.execute(
            select(AlertInfo).where(
                and_(
                    AlertInfo.alert_status == 'active',
                    AlertInfo.alert_level == 'scheduled'
                )
            ).order_by(desc(AlertInfo.occurrence_count), desc(AlertInfo.first_occurrence)).limit(limit)
        )
        return result.scalars().all()
    
    @classmethod
    async def get_alert_distribution(cls, db: AsyncSession) -> Dict[str, Dict[str, int]]:
        """
        获取告警分布统计
        
        Args:
            db: 数据库会话
            
        Returns:
            Dict[str, Dict[str, int]]: 分布统计
        """
        # 按级别分布
        level_result = await db.execute(
            select(AlertInfo.alert_level, func.count(AlertInfo.alert_id))
            .where(AlertInfo.alert_status == 'active')
            .group_by(AlertInfo.alert_level)
        )
        by_level = {row[0]: row[1] for row in level_result.fetchall()}
        
        # 按组件类型分布
        component_result = await db.execute(
            select(AlertInfo.component_type, func.count(AlertInfo.alert_id))
            .where(AlertInfo.alert_status == 'active')
            .group_by(AlertInfo.component_type)
        )
        by_component = {row[0]: row[1] for row in component_result.fetchall()}
        
        # 按位置分布（通过关联设备表）
        location_result = await db.execute(
            select(DeviceInfo.location, func.count(AlertInfo.alert_id))
            .select_from(AlertInfo.__table__.join(DeviceInfo.__table__, AlertInfo.device_id == DeviceInfo.device_id))
            .where(AlertInfo.alert_status == 'active')
            .group_by(DeviceInfo.location)
        )
        by_location = {row[0]: row[1] for row in location_result.fetchall()}
        
        # 按制造商分布（通过关联设备表）
        manufacturer_result = await db.execute(
            select(DeviceInfo.manufacturer, func.count(AlertInfo.alert_id))
            .select_from(AlertInfo.__table__.join(DeviceInfo.__table__, AlertInfo.device_id == DeviceInfo.device_id))
            .where(AlertInfo.alert_status == 'active')
            .group_by(DeviceInfo.manufacturer)
        )
        by_manufacturer = {row[0]: row[1] for row in manufacturer_result.fetchall()}
        
        return {
            'by_level': by_level,
            'by_component': by_component,
            'by_location': by_location,
            'by_manufacturer': by_manufacturer
        } 