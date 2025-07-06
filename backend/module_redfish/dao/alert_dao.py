"""
告警管理DAO层（优化版）
适配精简版alert_info表结构
"""
from sqlalchemy import and_, or_, func, desc, asc, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from module_redfish.models import AlertInfo, DeviceInfo
from module_redfish.entity.vo.alert_vo import AlertPageQueryModel
from utils.page_util import PageUtil
from utils.log_util import logger


class AlertDao:
    """告警管理DAO（优化版）"""
    
    @classmethod
    async def get_alert_list(
        cls,
        db: AsyncSession,
        query_object: AlertPageQueryModel,
        is_page: bool = False
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        获取告警列表（首页展示优化版）
        
        Args:
            db: 数据库会话
            query_object: 查询对象
            is_page: 是否分页
            
        Returns:
            Tuple[List[Dict[str, Any]], int]: 告警列表和总数
        """
        # 关联设备表查询，只选择必要字段提升性能
        query = select(
            AlertInfo.alert_id,
            AlertInfo.device_id,
            AlertInfo.component_type,
            AlertInfo.component_name,
            AlertInfo.health_status,
            AlertInfo.urgency_level,
            AlertInfo.alert_status,
            AlertInfo.first_occurrence,
            AlertInfo.last_occurrence,
            AlertInfo.resolved_time,
            DeviceInfo.hostname,
            DeviceInfo.business_ip,
            DeviceInfo.location
        ).join(DeviceInfo, AlertInfo.device_id == DeviceInfo.device_id)
        
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
        
        if query_object.urgency_level:
            conditions.append(AlertInfo.urgency_level == query_object.urgency_level)
        
        if query_object.health_status:
            conditions.append(AlertInfo.health_status == query_object.health_status)
        
        if query_object.alert_status:
            conditions.append(AlertInfo.alert_status == query_object.alert_status)
        
        if query_object.start_time:
            conditions.append(AlertInfo.first_occurrence >= query_object.start_time)
        
        if query_object.end_time:
            conditions.append(AlertInfo.first_occurrence <= query_object.end_time)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 排序：紧急告警优先，然后按首次发生时间倒序
        query = query.order_by(
            desc(AlertInfo.urgency_level == 'urgent'),
            desc(AlertInfo.first_occurrence)
        )
        
        # 分页
        if is_page:
            # 获取总数（优化的计数查询）
            count_query = select(func.count(AlertInfo.alert_id)).select_from(
                AlertInfo.__table__.join(DeviceInfo.__table__, AlertInfo.device_id == DeviceInfo.device_id)
            )
            if conditions:
                count_query = count_query.where(and_(*conditions))
            total_count = await db.scalar(count_query) or 0
            
            # 分页查询
            offset = (query_object.page_num - 1) * query_object.page_size
            query = query.offset(offset).limit(query_object.page_size)
            result = await db.execute(query)
            
            # 转换为字典列表
            alert_list = []
            for row in result.fetchall():
                # 生成基于组件状态的告警消息
                alert_message = f"{row.component_type} {row.component_name} 状态异常: {row.health_status}"
                
                alert_dict = {
                    'alert_id': row.alert_id,
                    'device_id': row.device_id,
                    'hostname': row.hostname,
                    'business_ip': row.business_ip,
                    'location': row.location,
                    'component_type': row.component_type,
                    'component_name': row.component_name,
                    'health_status': row.health_status,
                    'urgency_level': row.urgency_level,
                    'alert_status': row.alert_status,
                    'alert_message': alert_message,
                    'first_occurrence': row.first_occurrence,
                    'last_occurrence': row.last_occurrence,
                    'resolved_time': row.resolved_time
                }
                alert_list.append(alert_dict)
            
            return alert_list, total_count
        else:
            result = await db.execute(query)
            
            # 转换为字典列表
            alert_list = []
            for row in result.fetchall():
                # 生成基于组件状态的告警消息
                alert_message = f"{row.component_type} {row.component_name} 状态异常: {row.health_status}"
                
                alert_dict = {
                    'alert_id': row.alert_id,
                    'device_id': row.device_id,
                    'hostname': row.hostname,
                    'business_ip': row.business_ip,
                    'location': row.location,
                    'component_type': row.component_type,
                    'component_name': row.component_name,
                    'health_status': row.health_status,
                    'urgency_level': row.urgency_level,
                    'alert_status': row.alert_status,
                    'alert_message': alert_message,
                    'first_occurrence': row.first_occurrence,
                    'last_occurrence': row.last_occurrence,
                    'resolved_time': row.resolved_time
                }
                alert_list.append(alert_dict)
            
            return alert_list, len(alert_list)
    
    @classmethod
    async def get_alert_by_id(cls, db: AsyncSession, alert_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取告警详情
        
        Args:
            db: 数据库会话
            alert_id: 告警ID
            
        Returns:
            Optional[Dict[str, Any]]: 告警详情
        """
        query = select(
            AlertInfo.alert_id,
            AlertInfo.device_id,
            AlertInfo.component_type,
            AlertInfo.component_name,
            AlertInfo.health_status,
            AlertInfo.urgency_level,
            AlertInfo.alert_status,
            AlertInfo.first_occurrence,
            AlertInfo.last_occurrence,
            AlertInfo.resolved_time,
            AlertInfo.create_time,
            AlertInfo.update_time,
            DeviceInfo.hostname,
            DeviceInfo.business_ip,
            DeviceInfo.location,
            DeviceInfo.business_type,
            DeviceInfo.system_owner
        ).join(DeviceInfo, AlertInfo.device_id == DeviceInfo.device_id
        ).where(AlertInfo.alert_id == alert_id)
        
        result = await db.execute(query)
        row = result.first()
        
        if row:
            # 生成基于组件状态的告警消息
            alert_message = f"{row.component_type} {row.component_name} 状态异常: {row.health_status}"
            
            # 计算发生次数（精简版使用固定值1）
            occurrence_count = 1
            
            return {
                'alert_id': row.alert_id,
                'device_id': row.device_id,
                'hostname': row.hostname,
                'business_ip': row.business_ip,
                'location': row.location,
                'business_type': row.business_type,
                'system_owner': row.system_owner,
                'component_type': row.component_type,
                'component_name': row.component_name,
                'health_status': row.health_status,
                'urgency_level': row.urgency_level,
                'alert_status': row.alert_status,
                'alert_message': alert_message,
                'occurrence_count': occurrence_count,
                'first_occurrence': row.first_occurrence,
                'last_occurrence': row.last_occurrence,
                'resolved_time': row.resolved_time,
                'create_time': row.create_time,
                'update_time': row.update_time
            }
        return None
    
    @classmethod
    async def create_or_update_alert(
        cls,
        db: AsyncSession,
        device_id: int,
        component_type: str,
        component_name: str,
        health_status: str,
        urgency_level: str
    ) -> int:
        """
        创建或更新告警信息（精简版）
        
        Args:
            db: 数据库会话
            device_id: 设备ID
            component_type: 组件类型
            component_name: 组件名称
            health_status: 健康状态
            urgency_level: 紧急程度
            
        Returns:
            int: 告警ID
        """
        try:
            # 查找是否存在相同的活跃告警
            existing_alert_result = await db.execute(
                select(AlertInfo).where(
                    and_(
                        AlertInfo.device_id == device_id,
                        AlertInfo.component_type == component_type,
                        AlertInfo.component_name == component_name,
                        AlertInfo.alert_status == 'active'
                    )
                )
            )
            existing_alert = existing_alert_result.scalar_one_or_none()
            
            current_time = datetime.now()
            
            if existing_alert:
                # 更新现有告警
                existing_alert.health_status = health_status
                existing_alert.urgency_level = urgency_level
                existing_alert.last_occurrence = current_time
                existing_alert.update_time = current_time
                await db.commit()
                await db.refresh(existing_alert)
                logger.info(f"更新告警: device_id={device_id}, component={component_type}, alert_id={existing_alert.alert_id}")
                return existing_alert.alert_id
            else:
                # 创建新告警
                new_alert = AlertInfo(
                    device_id=device_id,
                    component_type=component_type,
                    component_name=component_name,
                    health_status=health_status,
                    urgency_level=urgency_level,
                    alert_status='active',
                    first_occurrence=current_time,
                    last_occurrence=current_time,
                    create_time=current_time,
                    update_time=current_time
                )
                db.add(new_alert)
                await db.commit()
                await db.refresh(new_alert)
                logger.info(f"创建新告警: device_id={device_id}, component={component_type}, alert_id={new_alert.alert_id}")
                return new_alert.alert_id
                
        except Exception as e:
            await db.rollback()
            logger.error(f"创建或更新告警失败: {str(e)}")
            raise
    
    @classmethod
    async def resolve_alerts(cls, db: AsyncSession, alert_ids: List[int], operator: str) -> bool:
        """
        解决告警（精简版）
        
        Args:
            db: 数据库会话
            alert_ids: 告警ID列表
            operator: 操作人
            
        Returns:
            bool: 是否成功
        """
        try:
            await db.execute(
                update(AlertInfo)
                .where(AlertInfo.alert_id.in_(alert_ids))
                .values(
                    alert_status='resolved',
                    resolved_time=datetime.now(),
                    update_time=datetime.now()
                )
            )
            await db.commit()
            logger.info(f"解决告警成功: {alert_ids}, 操作人: {operator}")
            return True
        except Exception as e:
            await db.rollback()
            logger.error(f"解决告警失败: {str(e)}")
            return False
    
    @classmethod
    async def get_alert_statistics(cls, db: AsyncSession, days: int = 7) -> Dict[str, int]:
        """
        获取告警统计信息（精简版）
        
        Args:
            db: 数据库会话
            days: 统计天数
            
        Returns:
            Dict[str, int]: 统计结果
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 总告警数
        total_result = await db.execute(
            select(func.count(AlertInfo.alert_id))
            .where(AlertInfo.first_occurrence >= start_date)
        )
        total_alerts = total_result.scalar() or 0
        
        # 紧急告警数
        urgent_result = await db.execute(
            select(func.count(AlertInfo.alert_id))
            .where(
                and_(
                    AlertInfo.first_occurrence >= start_date,
                    AlertInfo.urgency_level == 'urgent'
                )
            )
        )
        urgent_alerts = urgent_result.scalar() or 0
        
        # 择期告警数
        scheduled_result = await db.execute(
            select(func.count(AlertInfo.alert_id))
            .where(
                and_(
                    AlertInfo.first_occurrence >= start_date,
                    AlertInfo.urgency_level == 'scheduled'
                )
            )
        )
        scheduled_alerts = scheduled_result.scalar() or 0
        
        # 活跃告警数
        active_result = await db.execute(
            select(func.count(AlertInfo.alert_id))
            .where(AlertInfo.alert_status == 'active')
        )
        active_alerts = active_result.scalar() or 0
        
        # 已解决告警数
        resolved_result = await db.execute(
            select(func.count(AlertInfo.alert_id))
            .where(
                and_(
                    AlertInfo.first_occurrence >= start_date,
                    AlertInfo.alert_status == 'resolved'
                )
            )
        )
        resolved_alerts = resolved_result.scalar() or 0
        
        return {
            'total_alerts': total_alerts,
            'urgent_alerts': urgent_alerts,
            'scheduled_alerts': scheduled_alerts,
            'active_alerts': active_alerts,
            'resolved_alerts': resolved_alerts
        }
    
    @classmethod
    async def get_realtime_alerts(cls, db: AsyncSession, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取实时告警列表（紧急告警）
        
        Args:
            db: 数据库会话
            limit: 限制数量
            
        Returns:
            List[Dict[str, Any]]: 实时告警列表
        """
        query = select(
            AlertInfo.alert_id,
            AlertInfo.device_id,
            AlertInfo.component_type,
            AlertInfo.component_name,
            AlertInfo.health_status,
            AlertInfo.urgency_level,
            AlertInfo.first_occurrence,
            AlertInfo.last_occurrence,
            DeviceInfo.hostname,
            DeviceInfo.business_ip
        ).join(DeviceInfo, AlertInfo.device_id == DeviceInfo.device_id
        ).where(
            and_(
                AlertInfo.urgency_level == 'urgent',
                AlertInfo.alert_status == 'active'
            )
        ).order_by(desc(AlertInfo.first_occurrence)).limit(limit)
        
        result = await db.execute(query)
        
        alert_list = []
        for row in result.fetchall():
            alert_dict = {
                'alert_id': row.alert_id,
                'device_id': row.device_id,
                'hostname': row.hostname,
                'business_ip': row.business_ip,
                'component_type': row.component_type,
                'component_name': row.component_name,
                'health_status': row.health_status,
                'urgency_level': row.urgency_level,
                'first_occurrence': row.first_occurrence,
                'last_occurrence': row.last_occurrence
            }
            alert_list.append(alert_dict)
        
        return alert_list
    
    @classmethod
    async def get_scheduled_alerts(cls, db: AsyncSession, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取择期告警列表
        
        Args:
            db: 数据库会话
            limit: 限制数量
            
        Returns:
            List[Dict[str, Any]]: 择期告警列表
        """
        query = select(
            AlertInfo.alert_id,
            AlertInfo.device_id,
            AlertInfo.component_type,
            AlertInfo.component_name,
            AlertInfo.health_status,
            AlertInfo.urgency_level,
            AlertInfo.first_occurrence,
            AlertInfo.last_occurrence,
            DeviceInfo.hostname,
            DeviceInfo.business_ip
        ).join(DeviceInfo, AlertInfo.device_id == DeviceInfo.device_id
        ).where(
            and_(
                AlertInfo.urgency_level == 'scheduled',
                AlertInfo.alert_status == 'active'
            )
        ).order_by(desc(AlertInfo.first_occurrence)).limit(limit)
        
        result = await db.execute(query)
        
        alert_list = []
        for row in result.fetchall():
            alert_dict = {
                'alert_id': row.alert_id,
                'device_id': row.device_id,
                'hostname': row.hostname,
                'business_ip': row.business_ip,
                'component_type': row.component_type,
                'component_name': row.component_name,
                'health_status': row.health_status,
                'urgency_level': row.urgency_level,
                'first_occurrence': row.first_occurrence,
                'last_occurrence': row.last_occurrence
            }
            alert_list.append(alert_dict)
        
        return alert_list
    
    @classmethod
    async def get_alert_trend(cls, db: AsyncSession, days: int = 7) -> List[Dict[str, Any]]:
        """
        获取告警趋势数据（优化版）
        
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
                        AlertInfo.urgency_level == 'urgent'
                    )
                )
            )
            urgent_count = urgent_result.scalar() or 0
            
            # 当日择期告警数
            scheduled_result = await db.execute(
                select(func.count(AlertInfo.alert_id)).where(
                    and_(
                        AlertInfo.first_occurrence >= current_date,
                        AlertInfo.first_occurrence < next_date,
                        AlertInfo.urgency_level == 'scheduled'
                    )
                )
            )
            scheduled_count = scheduled_result.scalar() or 0
            
            trend_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'urgent_count': urgent_count,
                'scheduled_count': scheduled_count,
                'total_count': urgent_count + scheduled_count
            })
        
        return trend_data
    
    @classmethod
    async def get_alert_distribution(cls, db: AsyncSession) -> Dict[str, Dict[str, int]]:
        """
        获取告警分布统计（优化版）
        
        Args:
            db: 数据库会话
            
        Returns:
            Dict[str, Dict[str, int]]: 分布统计
        """
        # 按紧急程度分布
        level_result = await db.execute(
            select(AlertInfo.urgency_level, func.count(AlertInfo.alert_id))
            .where(AlertInfo.alert_status == 'active')
            .group_by(AlertInfo.urgency_level)
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
 