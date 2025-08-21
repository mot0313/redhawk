"""
Redfish日志数据访问对象(DAO)
"""
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import and_, or_, func, text, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from module_redfish.entity.do.redfish_log_do import RedfishLogDO
from module_redfish.entity.vo.redfish_log_vo import RedfishLogQueryModel, AddRedfishLogModel
from utils.page_util import PageUtil


class RedfishLogDao:
    """Redfish日志数据访问类"""
    
    @classmethod
    async def get_redfish_log_list(cls, db: AsyncSession, query_object: RedfishLogQueryModel, is_page: bool = False):
        """
        获取日志列表
        
        Args:
            db: 数据库会话
            query_object: 查询对象
            is_page: 是否分页
            
        Returns:
            分页结果或列表
        """
        query = select(RedfishLogDO)
        
        # 构建查询条件
        query = cls._build_query_conditions(query, query_object)
        
        # 排序：按创建时间降序
        query = query.order_by(desc(RedfishLogDO.created_time))
        
        if is_page:
            # 获取总数
            count_query = select(func.count(RedfishLogDO.log_id))
            conditions = []
            
            # 重复构建查询条件用于计数
            if query_object.device_id:
                conditions.append(RedfishLogDO.device_id == query_object.device_id)
            if query_object.device_ip:
                conditions.append(RedfishLogDO.device_ip.like(f'%{query_object.device_ip}%'))
            if query_object.log_source and query_object.log_source != 'all':
                conditions.append(RedfishLogDO.log_source == query_object.log_source)
            if query_object.severity and query_object.severity != 'all':
                conditions.append(RedfishLogDO.severity == query_object.severity)
            if query_object.message_keyword:
                conditions.append(
                    or_(
                        RedfishLogDO.message.like(f'%{query_object.message_keyword}%'),
                        RedfishLogDO.message_id.like(f'%{query_object.message_keyword}%')
                    )
                )
            if query_object.start_time:
                conditions.append(RedfishLogDO.created_time >= query_object.start_time)
            if query_object.end_time:
                conditions.append(RedfishLogDO.created_time <= query_object.end_time)
            
            if conditions:
                count_query = count_query.where(and_(*conditions))
            total_count = await db.scalar(count_query)
            
            # 分页查询
            query = query.offset((query_object.page_num - 1) * query_object.page_size).limit(query_object.page_size)
            result = await db.execute(query)
            log_list = result.scalars().all()
            
            return log_list, total_count
        else:
            # 普通查询
            result = await db.execute(query)
            log_list = result.scalars().all()
            return log_list, len(log_list)
    
    @classmethod
    def _build_query_conditions(cls, query, query_object: RedfishLogQueryModel):
        """构建查询条件"""
        conditions = []
        
        # 设备ID筛选
        if query_object.device_id:
            conditions.append(RedfishLogDO.device_id == query_object.device_id)
        
        # 设备IP筛选
        if query_object.device_ip:
            conditions.append(RedfishLogDO.device_ip.like(f'%{query_object.device_ip}%'))
        
        # 日志来源筛选
        if query_object.log_source and query_object.log_source != 'all':
            conditions.append(RedfishLogDO.log_source == query_object.log_source)
        
        # 严重程度筛选
        if query_object.severity and query_object.severity != 'all':
            conditions.append(RedfishLogDO.severity == query_object.severity)
        
        # 消息关键词搜索
        if query_object.message_keyword:
            conditions.append(
                or_(
                    RedfishLogDO.message.like(f'%{query_object.message_keyword}%'),
                    RedfishLogDO.message_id.like(f'%{query_object.message_keyword}%')
                )
            )
        
        # 时间范围筛选
        if query_object.start_time:
            conditions.append(RedfishLogDO.created_time >= query_object.start_time)
        
        if query_object.end_time:
            conditions.append(RedfishLogDO.created_time <= query_object.end_time)
        
        # 应用所有条件
        if conditions:
            query = query.where(and_(*conditions))
        
        return query
    
    @classmethod
    async def get_redfish_log_detail(cls, db: AsyncSession, log_id: str) -> Optional[RedfishLogDO]:
        """
        获取日志详情
        
        Args:
            db: 数据库会话
            log_id: 日志ID
            
        Returns:
            日志详情或None
        """
        query = select(RedfishLogDO).where(RedfishLogDO.log_id == log_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @classmethod
    async def add_redfish_log(cls, db: AsyncSession, log_data: AddRedfishLogModel) -> RedfishLogDO:
        """
        添加日志
        
        Args:
            db: 数据库会话
            log_data: 日志数据
            
        Returns:
            新增的日志对象
        """
        log_obj = RedfishLogDO(**log_data.dict())
        db.add(log_obj)
        await db.flush()
        await db.refresh(log_obj)
        return log_obj
    
    @classmethod
    async def add_redfish_logs_batch(cls, db: AsyncSession, logs_data: List[AddRedfishLogModel]) -> List[RedfishLogDO]:
        """
        批量添加日志
        
        Args:
            db: 数据库会话
            logs_data: 日志数据列表
            
        Returns:
            新增的日志对象列表
        """
        log_objects = []
        for log_data in logs_data:
            log_obj = RedfishLogDO(**log_data.dict())
            log_objects.append(log_obj)
        
        db.add_all(log_objects)
        await db.flush()
        
        # 刷新所有对象
        for log_obj in log_objects:
            await db.refresh(log_obj)
        
        return log_objects
    
    @classmethod
    async def delete_redfish_log(cls, db: AsyncSession, log_id: str) -> bool:
        """
        删除日志
        
        Args:
            db: 数据库会话
            log_id: 日志ID
            
        Returns:
            是否删除成功
        """
        query = select(RedfishLogDO).where(RedfishLogDO.log_id == log_id)
        result = await db.execute(query)
        log_obj = result.scalar_one_or_none()
        
        if log_obj:
            await db.delete(log_obj)
            await db.flush()
            return True
        return False
    
    @classmethod
    async def delete_redfish_logs_by_device(cls, db: AsyncSession, device_id: int) -> int:
        """
        删除指定设备的所有日志
        
        Args:
            db: 数据库会话
            device_id: 设备ID
            
        Returns:
            删除的日志数量
        """
        query = select(RedfishLogDO).where(RedfishLogDO.device_id == device_id)
        result = await db.execute(query)
        logs = result.scalars().all()
        
        count = len(logs)
        for log_obj in logs:
            await db.delete(log_obj)
        
        await db.flush()
        return count
    
    @classmethod
    async def cleanup_old_logs(cls, db: AsyncSession, before_date: datetime) -> int:
        """
        清理指定日期之前的日志
        
        Args:
            db: 数据库会话
            before_date: 清理此日期之前的日志
            
        Returns:
            清理的日志数量
        """
        # 查询要删除的日志
        query = select(RedfishLogDO).where(RedfishLogDO.created_time < before_date)
        result = await db.execute(query)
        logs_to_delete = result.scalars().all()
        
        count = len(logs_to_delete)
        
        # 批量删除
        for log_obj in logs_to_delete:
            await db.delete(log_obj)
        
        await db.flush()
        return count
    
    @classmethod
    async def get_redfish_log_stats(cls, db: AsyncSession) -> Dict[str, int]:
        """
        获取日志统计信息
        
        Args:
            db: 数据库会话
            
        Returns:
            统计信息字典
        """
        # 总数量
        total_query = select(func.count(RedfishLogDO.log_id))
        total_result = await db.execute(total_query)
        total_count = total_result.scalar() or 0
        
        # 按严重程度统计
        critical_query = select(func.count(RedfishLogDO.log_id)).where(RedfishLogDO.severity == 'CRITICAL')
        critical_result = await db.execute(critical_query)
        critical_count = critical_result.scalar() or 0
        
        warning_query = select(func.count(RedfishLogDO.log_id)).where(RedfishLogDO.severity == 'WARNING')
        warning_result = await db.execute(warning_query)
        warning_count = warning_result.scalar() or 0
        
        # 按日志来源统计
        sel_query = select(func.count(RedfishLogDO.log_id)).where(RedfishLogDO.log_source == 'SEL')
        sel_result = await db.execute(sel_query)
        sel_count = sel_result.scalar() or 0
        
        mel_query = select(func.count(RedfishLogDO.log_id)).where(RedfishLogDO.log_source == 'MEL')
        mel_result = await db.execute(mel_query)
        mel_count = mel_result.scalar() or 0
        
        # 今日日志数量
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        today_query = select(func.count(RedfishLogDO.log_id)).where(
            and_(
                RedfishLogDO.created_time >= today_start,
                RedfishLogDO.created_time <= today_end
            )
        )
        today_result = await db.execute(today_query)
        today_count = today_result.scalar() or 0
        
        # 近7天日志数量
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_query = select(func.count(RedfishLogDO.log_id)).where(
            RedfishLogDO.created_time >= seven_days_ago
        )
        recent_result = await db.execute(recent_query)
        recent_7days_count = recent_result.scalar() or 0
        
        return {
            'total_count': total_count,
            'critical_count': critical_count,
            'warning_count': warning_count,
            'sel_count': sel_count,
            'mel_count': mel_count,
            'today_count': today_count,
            'recent_7days_count': recent_7days_count
        }
    
    @classmethod
    async def get_device_log_count(cls, db: AsyncSession, device_id: int) -> int:
        """
        获取指定设备的日志数量
        
        Args:
            db: 数据库会话
            device_id: 设备ID
            
        Returns:
            日志数量
        """
        query = select(func.count(RedfishLogDO.log_id)).where(RedfishLogDO.device_id == device_id)
        result = await db.execute(query)
        return result.scalar() or 0
    
    @classmethod
    async def check_log_exists(cls, db: AsyncSession, device_id: int, entry_id: str, created_time: datetime) -> bool:
        """
        检查日志是否已存在（避免重复收集）
        
        Args:
            db: 数据库会话
            device_id: 设备ID
            entry_id: 原始条目ID
            created_time: 创建时间
            
        Returns:
            是否存在
        """
        query = select(RedfishLogDO).where(
            and_(
                RedfishLogDO.device_id == device_id,
                RedfishLogDO.entry_id == entry_id,
                RedfishLogDO.created_time == created_time
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None
    
    @classmethod
    async def get_latest_log_time(cls, db: AsyncSession, device_id: int) -> Optional[datetime]:
        """
        获取指定设备的最新日志时间
        
        Args:
            db: 数据库会话
            device_id: 设备ID
            
        Returns:
            最新日志时间或None
        """
        query = select(func.max(RedfishLogDO.created_time)).where(RedfishLogDO.device_id == device_id)
        result = await db.execute(query)
        return result.scalar()
