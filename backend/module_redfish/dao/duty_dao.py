"""
值班管理DAO层
"""
from sqlalchemy import and_, or_, func, desc, asc, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timedelta, date
from module_redfish.entity.do import DutyScheduleDO, DutyPersonDO
from module_redfish.entity.vo.duty_vo import DutySchedulePageQueryModel, DutyPersonPageQueryModel
from utils.page_util import PageUtil


class DutyDao:
    """值班管理DAO"""
    
    @classmethod
    async def get_duty_person_list(
        cls,
        db: AsyncSession,
        query_object: DutyPersonPageQueryModel,
        is_page: bool = False
    ) -> Tuple[List[DutyPersonDO], int]:
        """
        获取值班人员列表
        
        Args:
            db: 数据库会话
            query_object: 查询对象
            is_page: 是否分页
            
        Returns:
            Tuple[List[DutyPersonDO], int]: 值班人员列表和总数
        """
        query = select(DutyPersonDO)
        
        # 构建查询条件
        conditions = []
        
        if query_object.person_name:
            conditions.append(DutyPersonDO.person_name.like(f'%{query_object.person_name}%'))
        
        if query_object.department:
            conditions.append(DutyPersonDO.department.like(f'%{query_object.department}%'))
        
        if query_object.position:
            conditions.append(DutyPersonDO.position.like(f'%{query_object.position}%'))
        
        if query_object.phone:
            conditions.append(DutyPersonDO.phone.like(f'%{query_object.phone}%'))
        
        if query_object.email:
            conditions.append(DutyPersonDO.email.like(f'%{query_object.email}%'))
        
        if query_object.status:
            conditions.append(DutyPersonDO.status == query_object.status)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 按创建时间倒序排列
        query = query.order_by(desc(DutyPersonDO.create_time))
        
        # 分页
        if is_page:
            # 获取总数
            count_query = select(func.count(DutyPersonDO.person_id))
            if conditions:
                count_query = count_query.where(and_(*conditions))
            total_count = await db.scalar(count_query)
            
            # 分页查询
            query = query.offset(query_object.page_num).limit(query_object.page_size)
            result = await db.execute(query)
            person_list = result.scalars().all()
            
            return person_list, total_count
        else:
            result = await db.execute(query)
            person_list = result.scalars().all()
            return person_list, len(person_list)
    
    @classmethod
    async def get_duty_person_by_id(cls, db: AsyncSession, person_id: int) -> Optional[DutyPersonDO]:
        """
        根据ID获取值班人员信息
        
        Args:
            db: 数据库会话
            person_id: 人员ID
            
        Returns:
            Optional[DutyPersonDO]: 值班人员信息
        """
        result = await db.execute(
            select(DutyPersonDO).where(DutyPersonDO.person_id == person_id)
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_duty_person_by_name(cls, db: AsyncSession, person_name: str) -> Optional[DutyPersonDO]:
        """
        根据姓名获取值班人员信息
        
        Args:
            db: 数据库会话
            person_name: 人员姓名
            
        Returns:
            Optional[DutyPersonDO]: 值班人员信息
        """
        result = await db.execute(
            select(DutyPersonDO).where(DutyPersonDO.person_name == person_name)
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def add_duty_person(cls, db: AsyncSession, person_data: dict) -> DutyPersonDO:
        """
        添加值班人员
        
        Args:
            db: 数据库会话
            person_data: 人员数据
            
        Returns:
            DutyPersonDO: 新增的值班人员
        """
        new_person = DutyPersonDO(**person_data)
        db.add(new_person)
        await db.commit()
        await db.refresh(new_person)
        return new_person
    
    @classmethod
    async def edit_duty_person(cls, db: AsyncSession, person_data: dict) -> bool:
        """
        编辑值班人员
        
        Args:
            db: 数据库会话
            person_data: 人员数据
            
        Returns:
            bool: 是否成功
        """
        person_id = person_data.pop('person_id')
        await db.execute(
            update(DutyPersonDO).where(DutyPersonDO.person_id == person_id).values(**person_data)
        )
        await db.commit()
        return True
    
    @classmethod
    async def delete_duty_person(cls, db: AsyncSession, person_ids: List[int]) -> bool:
        """
        删除值班人员
        
        Args:
            db: 数据库会话
            person_ids: 人员ID列表
            
        Returns:
            bool: 是否成功
        """
        await db.execute(
            delete(DutyPersonDO).where(DutyPersonDO.person_id.in_(person_ids))
        )
        await db.commit()
        return True
    
    @classmethod
    async def get_duty_schedule_list(
        cls,
        db: AsyncSession,
        query_object: DutySchedulePageQueryModel,
        is_page: bool = False
    ) -> Tuple[List[DutyScheduleDO], int]:
        """
        获取值班排期列表
        
        Args:
            db: 数据库会话
            query_object: 查询对象
            is_page: 是否分页
            
        Returns:
            Tuple[List[DutyScheduleDO], int]: 值班排期列表和总数
        """
        # 关联值班人员表查询
        query = select(DutyScheduleDO).join(DutyPersonDO, DutyScheduleDO.person_id == DutyPersonDO.person_id)
        
        # 构建查询条件
        conditions = []
        
        if query_object.person_id:
            conditions.append(DutyScheduleDO.person_id == query_object.person_id)
        
        if query_object.person_name:
            conditions.append(DutyPersonDO.person_name.like(f'%{query_object.person_name}%'))
        
        if query_object.duty_type:
            conditions.append(DutyScheduleDO.duty_type == query_object.duty_type)
        
        if query_object.shift_type:
            conditions.append(DutyScheduleDO.shift_type == query_object.shift_type)
        
        if query_object.start_date:
            conditions.append(DutyScheduleDO.duty_date >= query_object.start_date)
        
        if query_object.end_date:
            conditions.append(DutyScheduleDO.duty_date <= query_object.end_date)
        
        if query_object.department:
            conditions.append(DutyPersonDO.department == query_object.department)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 按值班日期倒序排列
        query = query.order_by(desc(DutyScheduleDO.duty_date), asc(DutyScheduleDO.shift_type))
        
        # 分页
        if is_page:
            # 获取总数
            count_query = select(func.count(DutyScheduleDO.schedule_id)).select_from(
                DutyScheduleDO.__table__.join(DutyPersonDO.__table__, DutyScheduleDO.person_id == DutyPersonDO.person_id)
            )
            if conditions:
                count_query = count_query.where(and_(*conditions))
            total_count = await db.scalar(count_query)
            
            # 分页查询
            query = query.offset(query_object.page_num).limit(query_object.page_size)
            result = await db.execute(query)
            schedule_list = result.scalars().all()
            
            return schedule_list, total_count
        else:
            result = await db.execute(query)
            schedule_list = result.scalars().all()
            return schedule_list, len(schedule_list)
    
    @classmethod
    async def get_duty_schedule_by_id(cls, db: AsyncSession, schedule_id: int) -> Optional[DutyScheduleDO]:
        """
        根据ID获取值班排期信息
        
        Args:
            db: 数据库会话
            schedule_id: 排期ID
            
        Returns:
            Optional[DutyScheduleDO]: 值班排期信息
        """
        result = await db.execute(
            select(DutyScheduleDO).where(DutyScheduleDO.schedule_id == schedule_id)
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_duty_schedule_by_date_range(
        cls,
        db: AsyncSession,
        start_date: date,
        end_date: date
    ) -> List[DutyScheduleDO]:
        """
        根据日期范围获取值班排期
        
        Args:
            db: 数据库会话
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[DutyScheduleDO]: 值班排期列表
        """
        result = await db.execute(
            select(DutyScheduleDO).where(
                and_(
                    DutyScheduleDO.duty_date >= start_date,
                    DutyScheduleDO.duty_date <= end_date
                )
            ).order_by(DutyScheduleDO.duty_date, DutyScheduleDO.shift_type)
        )
        return result.scalars().all()
    
    @classmethod
    async def get_duty_schedule_conflicts(
        cls,
        db: AsyncSession,
        person_id: int,
        duty_date: date,
        shift_type: str,
        exclude_schedule_id: Optional[int] = None
    ) -> List[DutyScheduleDO]:
        """
        检查值班排期冲突
        
        Args:
            db: 数据库会话
            person_id: 人员ID
            duty_date: 值班日期
            shift_type: 班次类型
            exclude_schedule_id: 排除的排期ID（用于编辑时）
            
        Returns:
            List[DutyScheduleDO]: 冲突的值班排期
        """
        conditions = [
            DutyScheduleDO.person_id == person_id,
            DutyScheduleDO.duty_date == duty_date,
            DutyScheduleDO.shift_type == shift_type
        ]
        
        if exclude_schedule_id:
            conditions.append(DutyScheduleDO.schedule_id != exclude_schedule_id)
        
        result = await db.execute(
            select(DutyScheduleDO).where(and_(*conditions))
        )
        return result.scalars().all()
    
    @classmethod
    async def add_duty_schedule(cls, db: AsyncSession, schedule_data: dict) -> DutyScheduleDO:
        """
        添加值班排期
        
        Args:
            db: 数据库会话
            schedule_data: 排期数据
            
        Returns:
            DutyScheduleDO: 新增的值班排期
        """
        new_schedule = DutyScheduleDO(**schedule_data)
        db.add(new_schedule)
        await db.commit()
        await db.refresh(new_schedule)
        return new_schedule
    
    @classmethod
    async def edit_duty_schedule(cls, db: AsyncSession, schedule_data: dict) -> bool:
        """
        编辑值班排期
        
        Args:
            db: 数据库会话
            schedule_data: 排期数据
            
        Returns:
            bool: 是否成功
        """
        schedule_id = schedule_data.pop('schedule_id')
        await db.execute(
            update(DutyScheduleDO).where(DutyScheduleDO.schedule_id == schedule_id).values(**schedule_data)
        )
        await db.commit()
        return True
    
    @classmethod
    async def delete_duty_schedule(cls, db: AsyncSession, schedule_ids: List[int]) -> bool:
        """
        删除值班排期
        
        Args:
            db: 数据库会话
            schedule_ids: 排期ID列表
            
        Returns:
            bool: 是否成功
        """
        await db.execute(
            delete(DutyScheduleDO).where(DutyScheduleDO.schedule_id.in_(schedule_ids))
        )
        await db.commit()
        return True
    
    @classmethod
    async def get_current_duty_person(cls, db: AsyncSession, duty_type: str = "primary") -> Optional[Dict[str, Any]]:
        """
        获取当前值班人员
        
        Args:
            db: 数据库会话
            duty_type: 值班类型
            
        Returns:
            Optional[Dict[str, Any]]: 当前值班人员信息
        """
        today = date.today()
        current_hour = datetime.now().hour
        
        # 根据时间判断班次
        if 8 <= current_hour < 20:
            shift_type = "day"
        else:
            shift_type = "night"
        
        result = await db.execute(
            select(DutyScheduleDO, DutyPersonDO).join(
                DutyPersonDO, DutyScheduleDO.person_id == DutyPersonDO.person_id
            ).where(
                and_(
                    DutyScheduleDO.duty_date == today,
                    DutyScheduleDO.duty_type == duty_type,
                    DutyScheduleDO.shift_type == shift_type
                )
            )
        )
        
        row = result.first()
        if row:
            schedule, person = row
            return {
                "schedule_id": schedule.schedule_id,
                "person_id": person.person_id,
                "person_name": person.person_name,
                "department": person.department,
                "position": person.position,
                "phone": person.phone,
                "email": person.email,
                "duty_date": schedule.duty_date,
                "duty_type": schedule.duty_type,
                "shift_type": schedule.shift_type,
                "remarks": schedule.remarks
            }
        
        return None
    
    @classmethod
    async def get_duty_statistics(cls, db: AsyncSession, days: int = 30) -> Dict[str, Any]:
        """
        获取值班统计信息
        
        Args:
            db: 数据库会话
            days: 统计天数
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        start_date = date.today() - timedelta(days=days)
        end_date = date.today()
        
        # 总值班人员数
        total_persons_result = await db.execute(
            select(func.count(DutyPersonDO.person_id)).where(DutyPersonDO.status == '1')
        )
        total_persons = total_persons_result.scalar()
        
        # 已安排值班数
        scheduled_count_result = await db.execute(
            select(func.count(DutyScheduleDO.schedule_id)).where(
                and_(
                    DutyScheduleDO.duty_date >= start_date,
                    DutyScheduleDO.duty_date <= end_date
                )
            )
        )
        scheduled_count = scheduled_count_result.scalar()
        
        # 按部门统计值班人员
        dept_stats_result = await db.execute(
            select(DutyPersonDO.department, func.count(DutyPersonDO.person_id))
            .where(DutyPersonDO.status == '1')
            .group_by(DutyPersonDO.department)
        )
        dept_stats = {row[0]: row[1] for row in dept_stats_result.fetchall()}
        
        # 按值班类型统计
        duty_type_stats_result = await db.execute(
            select(DutyScheduleDO.duty_type, func.count(DutyScheduleDO.schedule_id))
            .where(
                and_(
                    DutyScheduleDO.duty_date >= start_date,
                    DutyScheduleDO.duty_date <= end_date
                )
            )
            .group_by(DutyScheduleDO.duty_type)
        )
        duty_type_stats = {row[0]: row[1] for row in duty_type_stats_result.fetchall()}
        
        return {
            'total_persons': total_persons,
            'scheduled_count': scheduled_count,
            'period_days': days,
            'dept_distribution': dept_stats,
            'duty_type_distribution': duty_type_stats
        } 