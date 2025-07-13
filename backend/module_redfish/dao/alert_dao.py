"""
告警管理DAO层（优化版）
适配精简版alert_info表结构
"""
from sqlalchemy import and_, or_, func, desc, asc, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from module_redfish.entity.do import AlertInfoDO, DeviceInfoDO
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
            AlertInfoDO.alert_id,
            AlertInfoDO.device_id,
            AlertInfoDO.component_type,
            AlertInfoDO.component_name,
            AlertInfoDO.health_status,
            AlertInfoDO.urgency_level,
            AlertInfoDO.alert_status,
            AlertInfoDO.first_occurrence,
            AlertInfoDO.last_occurrence,
            AlertInfoDO.resolved_time,
            AlertInfoDO.scheduled_maintenance_time,
            AlertInfoDO.maintenance_description,
            AlertInfoDO.maintenance_status,
            AlertInfoDO.maintenance_notes,
            AlertInfoDO.create_time,
            AlertInfoDO.update_time,
            DeviceInfoDO.hostname,
            DeviceInfoDO.business_ip,
            DeviceInfoDO.location
        ).join(DeviceInfoDO, AlertInfoDO.device_id == DeviceInfoDO.device_id)
        
        # 构建查询条件
        conditions = [
            AlertInfoDO.alert_status != 'deleted'  # 排除已删除的告警
        ]
        
        if query_object.device_id:
            conditions.append(AlertInfoDO.device_id == query_object.device_id)
        
        if query_object.hostname:
            conditions.append(DeviceInfoDO.hostname.like(f'%{query_object.hostname}%'))
        
        if query_object.business_ip:
            conditions.append(DeviceInfoDO.business_ip.like(f'%{query_object.business_ip}%'))
        
        if query_object.component_type:
            conditions.append(AlertInfoDO.component_type == query_object.component_type)
        
        if query_object.urgency_level:
            conditions.append(AlertInfoDO.urgency_level == query_object.urgency_level)
        
        if query_object.health_status:
            conditions.append(AlertInfoDO.health_status == query_object.health_status)
        
        if query_object.alert_status:
            conditions.append(AlertInfoDO.alert_status == query_object.alert_status)
        
        if query_object.start_time:
            conditions.append(AlertInfoDO.first_occurrence >= query_object.start_time)
        
        if query_object.end_time:
            conditions.append(AlertInfoDO.first_occurrence <= query_object.end_time)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 排序：紧急告警优先，然后按首次发生时间倒序
        query = query.order_by(
            desc(AlertInfoDO.urgency_level == 'urgent'),
            desc(AlertInfoDO.first_occurrence)
        )
        
        # 分页
        if is_page:
            # 获取总数（优化的计数查询）
            count_query = select(func.count(AlertInfoDO.alert_id)).select_from(
                AlertInfoDO.__table__.join(DeviceInfoDO.__table__, AlertInfoDO.device_id == DeviceInfoDO.device_id)
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
                    'resolved_time': row.resolved_time,
                    'scheduled_maintenance_time': row.scheduled_maintenance_time,
                    'maintenance_description': row.maintenance_description,
                    'maintenance_status': row.maintenance_status or 'none',
                    'maintenance_notes': row.maintenance_notes,
                    'create_time': row.create_time,
                    'update_time': row.update_time
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
                    'resolved_time': row.resolved_time,
                    'scheduled_maintenance_time': row.scheduled_maintenance_time,
                    'maintenance_description': row.maintenance_description,
                    'maintenance_status': row.maintenance_status or 'none',
                    'maintenance_notes': row.maintenance_notes,
                    'create_time': row.create_time,
                    'update_time': row.update_time
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
            AlertInfoDO.alert_id,
            AlertInfoDO.device_id,
            AlertInfoDO.component_type,
            AlertInfoDO.component_name,
            AlertInfoDO.health_status,
            AlertInfoDO.urgency_level,
            AlertInfoDO.alert_status,
            AlertInfoDO.first_occurrence,
            AlertInfoDO.last_occurrence,
            AlertInfoDO.resolved_time,
            AlertInfoDO.create_time,
            AlertInfoDO.update_time,
            DeviceInfoDO.hostname,
            DeviceInfoDO.business_ip,
            DeviceInfoDO.location,
            DeviceInfoDO.business_type,
            DeviceInfoDO.system_owner
        ).join(DeviceInfoDO, AlertInfoDO.device_id == DeviceInfoDO.device_id
        ).where(
            AlertInfoDO.alert_id == alert_id,
            AlertInfoDO.alert_status != 'deleted'  # 排除已删除的告警
        )
        
        result = await db.execute(query)
        row = result.first()
        
        if row:
            # 生成基于组件状态的告警消息
            alert_message = f"{row.component_type} {row.component_name} 状态异常: {row.health_status}"
            
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
                select(AlertInfoDO).where(
                    and_(
                        AlertInfoDO.device_id == device_id,
                        AlertInfoDO.component_type == component_type,
                        AlertInfoDO.component_name == component_name,
                        AlertInfoDO.alert_status == 'active'
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
                new_alert = AlertInfoDO(
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
    
    # 精简版移除手动解决告警功能，告警状态由监控系统自动管理
    
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
            select(func.count(AlertInfoDO.alert_id))
            .where(AlertInfoDO.first_occurrence >= start_date)
        )
        total_alerts = total_result.scalar() or 0
        
        # 紧急告警数
        urgent_result = await db.execute(
            select(func.count(AlertInfoDO.alert_id))
            .where(
                and_(
                    AlertInfoDO.first_occurrence >= start_date,
                    AlertInfoDO.urgency_level == 'urgent'
                )
            )
        )
        urgent_alerts = urgent_result.scalar() or 0
        
        # 择期告警数
        scheduled_result = await db.execute(
            select(func.count(AlertInfoDO.alert_id))
            .where(
                and_(
                    AlertInfoDO.first_occurrence >= start_date,
                    AlertInfoDO.urgency_level == 'scheduled'
                )
            )
        )
        scheduled_alerts = scheduled_result.scalar() or 0
        
        # 活跃告警数
        active_result = await db.execute(
            select(func.count(AlertInfoDO.alert_id))
            .where(AlertInfoDO.alert_status == 'active')
        )
        active_alerts = active_result.scalar() or 0
        
        # 已解决告警数
        resolved_result = await db.execute(
            select(func.count(AlertInfoDO.alert_id))
            .where(
                and_(
                    AlertInfoDO.first_occurrence >= start_date,
                    AlertInfoDO.alert_status == 'resolved'
                )
            )
        )
        resolved_alerts = resolved_result.scalar() or 0
        
        return {
            'total_alerts': total_alerts,
            'urgent_alerts': urgent_alerts,
            'scheduled_alerts': scheduled_alerts,
            'active_alerts': active_alerts,
            'resolved_alerts': resolved_alerts,
            'ignored_alerts': 0  # 精简版移除忽略功能，设为0
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
            AlertInfoDO.alert_id,
            AlertInfoDO.device_id,
            AlertInfoDO.component_type,
            AlertInfoDO.component_name,
            AlertInfoDO.health_status,
            AlertInfoDO.urgency_level,
            AlertInfoDO.first_occurrence,
            AlertInfoDO.last_occurrence,
            DeviceInfoDO.hostname,
            DeviceInfoDO.business_ip
        ).join(DeviceInfoDO, AlertInfoDO.device_id == DeviceInfoDO.device_id
        ).where(
            and_(
                AlertInfoDO.urgency_level == 'urgent',
                AlertInfoDO.alert_status == 'active'
            )
        ).order_by(desc(AlertInfoDO.first_occurrence)).limit(limit)
        
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
            AlertInfoDO.alert_id,
            AlertInfoDO.device_id,
            AlertInfoDO.component_type,
            AlertInfoDO.component_name,
            AlertInfoDO.health_status,
            AlertInfoDO.urgency_level,
            AlertInfoDO.first_occurrence,
            AlertInfoDO.last_occurrence,
            DeviceInfoDO.hostname,
            DeviceInfoDO.business_ip
        ).join(DeviceInfoDO, AlertInfoDO.device_id == DeviceInfoDO.device_id
        ).where(
            and_(
                AlertInfoDO.urgency_level == 'scheduled',
                AlertInfoDO.alert_status == 'active'
            )
        ).order_by(desc(AlertInfoDO.first_occurrence)).limit(limit)
        
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
                select(func.count(AlertInfoDO.alert_id)).where(
                    and_(
                        AlertInfoDO.first_occurrence >= current_date,
                        AlertInfoDO.first_occurrence < next_date,
                        AlertInfoDO.urgency_level == 'urgent'
                    )
                )
            )
            urgent_count = urgent_result.scalar() or 0
            
            # 当日择期告警数
            scheduled_result = await db.execute(
                select(func.count(AlertInfoDO.alert_id)).where(
                    and_(
                        AlertInfoDO.first_occurrence >= current_date,
                        AlertInfoDO.first_occurrence < next_date,
                        AlertInfoDO.urgency_level == 'scheduled'
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
            select(AlertInfoDO.urgency_level, func.count(AlertInfoDO.alert_id))
            .where(AlertInfoDO.alert_status == 'active')
            .group_by(AlertInfoDO.urgency_level)
        )
        by_level = {row[0]: row[1] for row in level_result.fetchall()}
        
        # 按组件类型分布
        component_result = await db.execute(
            select(AlertInfoDO.component_type, func.count(AlertInfoDO.alert_id))
            .where(AlertInfoDO.alert_status == 'active')
            .group_by(AlertInfoDO.component_type)
        )
        by_component = {row[0]: row[1] for row in component_result.fetchall()}
        
        # 按位置分布（通过关联设备表）
        location_result = await db.execute(
            select(DeviceInfoDO.location, func.count(AlertInfoDO.alert_id))
            .select_from(AlertInfoDO.__table__.join(DeviceInfoDO.__table__, AlertInfoDO.device_id == DeviceInfoDO.device_id))
            .where(AlertInfoDO.alert_status == 'active')
            .group_by(DeviceInfoDO.location)
        )
        by_location = {row[0]: row[1] for row in location_result.fetchall()}
        
        # 按制造商分布（通过关联设备表）
        manufacturer_result = await db.execute(
            select(DeviceInfoDO.manufacturer, func.count(AlertInfoDO.alert_id))
            .select_from(AlertInfoDO.__table__.join(DeviceInfoDO.__table__, AlertInfoDO.device_id == DeviceInfoDO.device_id))
            .where(AlertInfoDO.alert_status == 'active')
            .group_by(DeviceInfoDO.manufacturer)
        )
        by_manufacturer = {row[0]: row[1] for row in manufacturer_result.fetchall()}
        
        return {
            'by_level': by_level,
            'by_component': by_component,
            'by_location': by_location,
            'by_manufacturer': by_manufacturer
        }

    @classmethod
    async def schedule_maintenance(
        cls, 
        db: AsyncSession, 
        alert_id: int, 
        maintenance_data: Dict[str, Any]
    ) -> bool:
        """
        为告警安排维修时间
        
        Args:
            db: 数据库会话
            alert_id: 告警ID
            maintenance_data: 维修数据
            
        Returns:
            bool: 是否成功
        """
        try:
            # 更新告警的维修信息
            update_stmt = update(AlertInfoDO).where(
                AlertInfoDO.alert_id == alert_id
            ).values(
                scheduled_maintenance_time=maintenance_data.get('scheduled_maintenance_time'),
                maintenance_description=maintenance_data.get('maintenance_description'),
                maintenance_status='planned',
                maintenance_notes=maintenance_data.get('maintenance_notes')
            )
            
            result = await db.execute(update_stmt)
            if result.rowcount > 0:
                await db.commit()
                logger.info(f"为告警 {alert_id} 安排维修时间成功")
                return True
            else:
                logger.warning(f"未找到告警 {alert_id}")
                return False
                
        except Exception as e:
            await db.rollback()
            logger.error(f"为告警 {alert_id} 安排维修时间失败: {str(e)}")
            return False

    @classmethod
    async def update_maintenance(
        cls, 
        db: AsyncSession, 
        alert_id: int, 
        maintenance_data: Dict[str, Any],
        updated_by: str
    ) -> bool:
        """
        更新告警的维修计划
        
        Args:
            db: 数据库会话
            alert_id: 告警ID
            maintenance_data: 维修数据
            updated_by: 更新人
            
        Returns:
            bool: 是否成功
        """
        try:
            # 构建更新字段
            update_values = {}
            
            # 只更新非None的字段
            for key, value in maintenance_data.items():
                if value is not None:
                    update_values[key] = value
            
            update_stmt = update(AlertInfoDO).where(
                AlertInfoDO.alert_id == alert_id
            ).values(**update_values)
            
            result = await db.execute(update_stmt)
            if result.rowcount > 0:
                await db.commit()
                logger.info(f"更新告警 {alert_id} 维修计划成功")
                return True
            else:
                logger.warning(f"未找到告警 {alert_id}")
                return False
                
        except Exception as e:
            await db.rollback()
            logger.error(f"更新告警 {alert_id} 维修计划失败: {str(e)}")
            return False

    @classmethod
    async def batch_schedule_maintenance(
        cls, 
        db: AsyncSession, 
        alert_ids: List[int], 
        maintenance_data: Dict[str, Any]
    ) -> int:
        """
        批量安排维修时间
        
        Args:
            db: 数据库会话
            alert_ids: 告警ID列表
            maintenance_data: 维修数据
            
        Returns:
            int: 成功更新的记录数
        """
        try:
            update_stmt = update(AlertInfoDO).where(
                AlertInfoDO.alert_id.in_(alert_ids)
            ).values(
                scheduled_maintenance_time=maintenance_data.get('scheduled_maintenance_time'),
                maintenance_description=maintenance_data.get('maintenance_description'),
                maintenance_status=maintenance_data.get('maintenance_status', 'planned'),
                maintenance_notes=maintenance_data.get('maintenance_notes')
            )
            
            result = await db.execute(update_stmt)
            updated_count = result.rowcount
            
            if updated_count > 0:
                await db.commit()
                logger.info(f"批量安排维修时间成功，更新了 {updated_count} 条记录")
            
            return updated_count
                
        except Exception as e:
            await db.rollback()
            logger.error(f"批量安排维修时间失败: {str(e)}")
            return 0

    @classmethod
    async def get_maintenance_schedule(
        cls, 
        db: AsyncSession, 
        query_object: Optional[Dict[str, Any]] = None,
        page_num: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        获取维修计划列表
        
        Args:
            db: 数据库会话
            query_object: 查询条件
            page_num: 页码
            page_size: 页大小
            
        Returns:
            Tuple[List[Dict[str, Any]], int]: 维修计划列表和总数
        """
        query = select(
            AlertInfoDO.alert_id,
            AlertInfoDO.device_id,
            AlertInfoDO.component_type,
            AlertInfoDO.component_name,
            AlertInfoDO.health_status,
            AlertInfoDO.urgency_level,
            AlertInfoDO.scheduled_maintenance_time,
            AlertInfoDO.maintenance_description,
            AlertInfoDO.maintenance_status,
            AlertInfoDO.maintenance_notes,
            DeviceInfoDO.hostname,
            DeviceInfoDO.business_ip,
            DeviceInfoDO.location
        ).join(DeviceInfoDO, AlertInfoDO.device_id == DeviceInfoDO.device_id
        ).where(AlertInfoDO.maintenance_status != 'none')
        
        # 构建查询条件
        conditions = []
        if query_object:
            if query_object.get('device_id'):
                conditions.append(AlertInfoDO.device_id == query_object['device_id'])
            if query_object.get('maintenance_status'):
                conditions.append(AlertInfoDO.maintenance_status == query_object['maintenance_status'])
            if query_object.get('scheduled_start_time'):
                conditions.append(AlertInfoDO.scheduled_maintenance_time >= query_object['scheduled_start_time'])
            if query_object.get('scheduled_end_time'):
                conditions.append(AlertInfoDO.scheduled_maintenance_time <= query_object['scheduled_end_time'])
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 排序：按计划维修时间排序
        query = query.order_by(asc(AlertInfoDO.scheduled_maintenance_time))
        
        # 获取总数
        count_query = select(func.count(AlertInfoDO.alert_id)).select_from(
            AlertInfoDO.__table__.join(DeviceInfoDO.__table__, AlertInfoDO.device_id == DeviceInfoDO.device_id)
        ).where(AlertInfoDO.maintenance_status != 'none')
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_count = await db.scalar(count_query) or 0
        
        # 分页
        offset = (page_num - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await db.execute(query)
        
        # 转换为字典列表
        maintenance_list = []
        for row in result.fetchall():
            maintenance_dict = {
                'alert_id': row.alert_id,
                'device_id': row.device_id,
                'hostname': row.hostname,
                'business_ip': row.business_ip,
                'location': row.location,
                'component_type': row.component_type,
                'component_name': row.component_name,
                'health_status': row.health_status,
                'urgency_level': row.urgency_level,
                'scheduled_maintenance_time': row.scheduled_maintenance_time,
                'maintenance_description': row.maintenance_description,
                'maintenance_status': row.maintenance_status,
                'maintenance_notes': row.maintenance_notes
            }
            maintenance_list.append(maintenance_dict)
        
        return maintenance_list, total_count

    @classmethod
    async def get_calendar_maintenance(
        cls, 
        db: AsyncSession, 
        start_date: str,
        end_date: str
    ) -> List:
        """
        获取日历视图的维修计划数据
        
        Args:
            db: 数据库会话
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List: 维修计划查询结果
        """
        try:
            # 转换日期格式为datetime对象
            from datetime import datetime
            start_datetime = datetime.strptime(f"{start_date} 00:00:00", "%Y-%m-%d %H:%M:%S")
            end_datetime = datetime.strptime(f"{end_date} 23:59:59", "%Y-%m-%d %H:%M:%S")
            
            query = select(
                AlertInfoDO.alert_id,
                AlertInfoDO.device_id,
                AlertInfoDO.component_type,
                AlertInfoDO.component_name,
                AlertInfoDO.health_status,
                AlertInfoDO.urgency_level,
                AlertInfoDO.alert_status,
                AlertInfoDO.scheduled_maintenance_time,
                AlertInfoDO.maintenance_description,
                AlertInfoDO.maintenance_status,
                AlertInfoDO.maintenance_notes,
                AlertInfoDO.first_occurrence,
                AlertInfoDO.last_occurrence,
                DeviceInfoDO.hostname,
                DeviceInfoDO.business_ip
            ).join(
                DeviceInfoDO, AlertInfoDO.device_id == DeviceInfoDO.device_id
            ).where(
                and_(
                    AlertInfoDO.scheduled_maintenance_time.isnot(None),
                    AlertInfoDO.scheduled_maintenance_time >= start_datetime,
                    AlertInfoDO.scheduled_maintenance_time <= end_datetime
                )
            ).order_by(asc(AlertInfoDO.scheduled_maintenance_time))
            
            result = await db.execute(query)
            return result.fetchall()
            
        except Exception as e:
            logger.error(f"获取日历维修计划失败: {str(e)}")
            raise
 
    @classmethod
    async def delete_alert(
        cls,
        db: AsyncSession,
        alert_id: int,
        delete_reason: Optional[str] = None
    ) -> bool:
        """
        删除告警（逻辑删除）
        
        Args:
            db: 数据库会话
            alert_id: 告警ID
            delete_reason: 删除原因
            
        Returns:
            bool: 是否成功
        """
        try:
            # 逻辑删除：修改状态为deleted
            stmt = update(AlertInfoDO).where(
                AlertInfoDO.alert_id == alert_id,
                AlertInfoDO.alert_status != 'deleted'  # 防止重复删除
            ).values(
                alert_status='deleted',
                resolved_time=datetime.now(),
                maintenance_notes=delete_reason or '手动删除',
                update_time=datetime.now()
            )
            
            result = await db.execute(stmt)
            await db.commit()
            
            return result.rowcount > 0
            
        except Exception as e:
            await db.rollback()
            logger.error(f"删除告警失败: {str(e)}")
            return False
    
    @classmethod
    async def batch_delete_alerts(
        cls,
        db: AsyncSession,
        alert_ids: List[int],
        delete_reason: Optional[str] = None
    ) -> int:
        """
        批量删除告警（逻辑删除）
        
        Args:
            db: 数据库会话
            alert_ids: 告警ID列表
            delete_reason: 删除原因
            
        Returns:
            int: 成功删除的数量
        """
        try:
            # 逻辑删除：修改状态为deleted
            stmt = update(AlertInfoDO).where(
                AlertInfoDO.alert_id.in_(alert_ids),
                AlertInfoDO.alert_status != 'deleted'  # 防止重复删除
            ).values(
                alert_status='deleted',
                resolved_time=datetime.now(),
                maintenance_notes=delete_reason or '批量删除',
                update_time=datetime.now()
            )
            
            result = await db.execute(stmt)
            await db.commit()
            
            return result.rowcount
            
        except Exception as e:
            await db.rollback()
            logger.error(f"批量删除告警失败: {str(e)}")
            return 0
    
    @classmethod
    async def get_alert_info_by_id(cls, db: AsyncSession, alert_id: int) -> Optional[AlertInfoDO]:
        """
        根据ID获取告警信息（返回SQLAlchemy对象）
        
        Args:
            db: 数据库会话
            alert_id: 告警ID
            
        Returns:
            Optional[AlertInfoDO]: 告警信息
        """
        try:
            stmt = select(AlertInfoDO).where(
                AlertInfoDO.alert_id == alert_id,
                AlertInfoDO.alert_status != 'deleted'  # 排除已删除的告警
            )
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"获取告警信息失败: {str(e)}")
            return None 