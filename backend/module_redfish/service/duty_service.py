"""
值班管理Service层
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from module_redfish.dao.duty_dao import DutyDao
from module_redfish.entity.vo.duty_vo import (
    DutyPersonPageQueryModel, DutyPersonModel, DutyPersonQueryModel,
    DutySchedulePageQueryModel, DutyScheduleModel, DutyScheduleQueryModel
)
from utils.response_util import ResponseUtil
from utils.page_util import PageResponseModel
# 移除CustomException导入，使用标准异常


class DutyService:
    """值班管理Service"""
    
    @classmethod
    async def get_duty_person_list_service(
        cls,
        query_object: DutyPersonPageQueryModel,
        db: AsyncSession,
        is_page: bool = False
    ):
        """
        获取值班人员列表
        
        Args:
            query_object: 查询对象
            db: 数据库会话
            is_page: 是否分页
            
        Returns:
            分页或非分页的人员列表
        """
        try:
            person_list, total = await DutyDao.get_duty_person_list(db, query_object, is_page)
            
            if is_page:
                # 转换为VO格式
                person_list_data = [
                    DutyPersonModel(
                        person_id=person.person_id,
                        person_name=person.person_name,
                        department=person.department,
                        position=person.position,
                        phone=person.phone,
                        email=person.email,
                        status=person.status,
                        status_dict={"1": "正常", "0": "停用"}.get(person.status, "未知"),
                        create_time=person.create_time,
                        update_time=person.update_time,
                        remarks=person.remarks
                    ) for person in person_list
                ]
                
                return ResponseUtil.success(
                    data=PageResponseModel(
                        rows=person_list_data,
                        total=total
                    )
                )
            else:
                person_list_data = [
                    DutyPersonQueryModel(
                        person_id=person.person_id,
                        person_name=person.person_name,
                        department=person.department,
                        position=person.position,
                        phone=person.phone,
                        email=person.email,
                        status=person.status
                    ) for person in person_list
                ]
                
                return ResponseUtil.success(data=person_list_data)
                
        except Exception as e:
            raise Exception(f"获取值班人员列表失败: {str(e)}")
    
    @classmethod
    async def get_duty_person_detail_service(cls, person_id: int, db: AsyncSession):
        """
        获取值班人员详情
        
        Args:
            person_id: 人员ID
            db: 数据库会话
            
        Returns:
            人员详情
        """
        try:
            person = await DutyDao.get_duty_person_by_id(db, person_id)
            if not person:
                return ResponseUtil.error(message="值班人员不存在")
            
            person_data = DutyPersonModel(
                person_id=person.person_id,
                person_name=person.person_name,
                department=person.department,
                position=person.position,
                phone=person.phone,
                email=person.email,
                status=person.status,
                status_dict={"1": "正常", "0": "停用"}.get(person.status, "未知"),
                create_time=person.create_time,
                update_time=person.update_time,
                remarks=person.remarks
            )
            
            return ResponseUtil.success(data=person_data)
            
        except Exception as e:
            raise Exception(f"获取值班人员详情失败: {str(e)}")
    
    @classmethod
    async def add_duty_person_service(cls, person_data: dict, db: AsyncSession):
        """
        添加值班人员
        
        Args:
            person_data: 人员数据
            db: 数据库会话
            
        Returns:
            新增结果
        """
        try:
            # 检查姓名是否重复
            existing_person = await DutyDao.get_duty_person_by_name(db, person_data['person_name'])
            if existing_person:
                return ResponseUtil.error(message="值班人员姓名已存在")
            
            # 添加创建时间
            person_data['create_time'] = datetime.now()
            person_data['update_time'] = datetime.now()
            
            new_person = await DutyDao.add_duty_person(db, person_data)
            
            return ResponseUtil.success(
                data={'person_id': new_person.person_id},
                message="值班人员添加成功"
            )
            
        except Exception as e:
            raise Exception(f"添加值班人员失败: {str(e)}")
    
    @classmethod
    async def edit_duty_person_service(cls, person_data: dict, db: AsyncSession):
        """
        编辑值班人员
        
        Args:
            person_data: 人员数据
            db: 数据库会话
            
        Returns:
            编辑结果
        """
        try:
            person_id = person_data['person_id']
            
            # 检查人员是否存在
            existing_person = await DutyDao.get_duty_person_by_id(db, person_id)
            if not existing_person:
                return ResponseUtil.error(message="值班人员不存在")
            
            # 检查姓名是否与其他人员重复
            person_with_same_name = await DutyDao.get_duty_person_by_name(db, person_data['person_name'])
            if person_with_same_name and person_with_same_name.person_id != person_id:
                return ResponseUtil.error(message="值班人员姓名已存在")
            
            # 添加更新时间
            person_data['update_time'] = datetime.now()
            
            await DutyDao.edit_duty_person(db, person_data)
            
            return ResponseUtil.success(message="值班人员编辑成功")
            
        except Exception as e:
            raise Exception(f"编辑值班人员失败: {str(e)}")
    
    @classmethod
    async def delete_duty_person_service(cls, person_ids: List[int], db: AsyncSession):
        """
        删除值班人员
        
        Args:
            person_ids: 人员ID列表
            db: 数据库会话
            
        Returns:
            删除结果
        """
        try:
            # 检查是否有关联的值班排期
            for person_id in person_ids:
                # 查询未来的值班排期
                future_schedules = await DutyDao.get_duty_schedule_by_date_range(
                    db, 
                    date.today(), 
                    date.today() + timedelta(days=365)
                )
                
                person_schedules = [s for s in future_schedules if s.person_id == person_id]
                if person_schedules:
                    person = await DutyDao.get_duty_person_by_id(db, person_id)
                    return ResponseUtil.error(
                        message=f"值班人员 {person.person_name if person else '未知'} 存在未来的值班排期，无法删除"
                    )
            
            await DutyDao.delete_duty_person(db, person_ids)
            
            return ResponseUtil.success(message="值班人员删除成功")
            
        except Exception as e:
            raise Exception(f"删除值班人员失败: {str(e)}")
    
    @classmethod
    async def get_duty_schedule_list_service(
        cls,
        query_object: DutySchedulePageQueryModel,
        db: AsyncSession,
        is_page: bool = False
    ):
        """
        获取值班排期列表
        
        Args:
            query_object: 查询对象
            db: 数据库会话
            is_page: 是否分页
            
        Returns:
            分页或非分页的排期列表
        """
        try:
            schedule_list, total = await DutyDao.get_duty_schedule_list(db, query_object, is_page)
            
            # 获取关联的人员信息
            person_ids = list(set([schedule.person_id for schedule in schedule_list]))
            persons = {}
            for person_id in person_ids:
                person = await DutyDao.get_duty_person_by_id(db, person_id)
                if person:
                    persons[person_id] = person
            
            if is_page:
                # 转换为VO格式
                schedule_list_data = [
                    DutyScheduleModel(
                        schedule_id=schedule.schedule_id,
                        person_id=schedule.person_id,
                        person_name=persons.get(schedule.person_id).person_name if persons.get(schedule.person_id) else "未知",
                        department=persons.get(schedule.person_id).department if persons.get(schedule.person_id) else "未知",
                        duty_date=schedule.duty_date,
                        duty_type=schedule.duty_type,
                        duty_type_dict={"primary": "主值班", "backup": "备值班", "emergency": "应急值班"}.get(schedule.duty_type, "未知"),
                        shift_type=schedule.shift_type,
                        shift_type_dict={"day": "白班", "night": "夜班", "all": "全天"}.get(schedule.shift_type, "未知"),
                        create_time=schedule.create_time,
                        update_time=schedule.update_time,
                        remarks=schedule.remarks
                    ) for schedule in schedule_list
                ]
                
                return ResponseUtil.success(
                    data=PageResponseModel(
                        rows=schedule_list_data,
                        total=total
                    )
                )
            else:
                schedule_list_data = [
                    DutyScheduleQueryModel(
                        schedule_id=schedule.schedule_id,
                        person_id=schedule.person_id,
                        person_name=persons.get(schedule.person_id).person_name if persons.get(schedule.person_id) else "未知",
                        duty_date=schedule.duty_date,
                        duty_type=schedule.duty_type,
                        shift_type=schedule.shift_type
                    ) for schedule in schedule_list
                ]
                
                return ResponseUtil.success(data=schedule_list_data)
                
        except Exception as e:
            raise Exception(f"获取值班排期列表失败: {str(e)}")
    
    @classmethod
    async def get_duty_schedule_detail_service(cls, schedule_id: int, db: AsyncSession):
        """
        获取值班排期详情
        
        Args:
            schedule_id: 排期ID
            db: 数据库会话
            
        Returns:
            排期详情
        """
        try:
            schedule = await DutyDao.get_duty_schedule_by_id(db, schedule_id)
            if not schedule:
                return ResponseUtil.error(message="值班排期不存在")
            
            person = await DutyDao.get_duty_person_by_id(db, schedule.person_id)
            
            schedule_data = DutyScheduleModel(
                schedule_id=schedule.schedule_id,
                person_id=schedule.person_id,
                person_name=person.person_name if person else "未知",
                department=person.department if person else "未知",
                duty_date=schedule.duty_date,
                duty_type=schedule.duty_type,
                duty_type_dict={"primary": "主值班", "backup": "备值班", "emergency": "应急值班"}.get(schedule.duty_type, "未知"),
                shift_type=schedule.shift_type,
                shift_type_dict={"day": "白班", "night": "夜班", "all": "全天"}.get(schedule.shift_type, "未知"),
                create_time=schedule.create_time,
                update_time=schedule.update_time,
                remarks=schedule.remarks
            )
            
            return ResponseUtil.success(data=schedule_data)
            
        except Exception as e:
            raise Exception(f"获取值班排期详情失败: {str(e)}")
    
    @classmethod
    async def add_duty_schedule_service(cls, schedule_data: dict, db: AsyncSession):
        """
        添加值班排期
        
        Args:
            schedule_data: 排期数据
            db: 数据库会话
            
        Returns:
            新增结果
        """
        try:
            # 检查人员是否存在
            person = await DutyDao.get_duty_person_by_id(db, schedule_data['person_id'])
            if not person:
                return ResponseUtil.error(message="值班人员不存在")
            
            if person.status != '1':
                return ResponseUtil.error(message="值班人员状态异常，无法安排值班")
            
            # 检查排期冲突
            conflicts = await DutyDao.get_duty_schedule_conflicts(
                db,
                schedule_data['person_id'],
                schedule_data['duty_date'],
                schedule_data['shift_type']
            )
            
            if conflicts:
                return ResponseUtil.error(message="该人员在此时间段已有值班安排")
            
            # 添加创建时间
            schedule_data['create_time'] = datetime.now()
            schedule_data['update_time'] = datetime.now()
            
            new_schedule = await DutyDao.add_duty_schedule(db, schedule_data)
            
            return ResponseUtil.success(
                data={'schedule_id': new_schedule.schedule_id},
                message="值班排期添加成功"
            )
            
        except Exception as e:
            raise Exception(f"添加值班排期失败: {str(e)}")
    
    @classmethod
    async def edit_duty_schedule_service(cls, schedule_data: dict, db: AsyncSession):
        """
        编辑值班排期
        
        Args:
            schedule_data: 排期数据
            db: 数据库会话
            
        Returns:
            编辑结果
        """
        try:
            schedule_id = schedule_data['schedule_id']
            
            # 检查排期是否存在
            existing_schedule = await DutyDao.get_duty_schedule_by_id(db, schedule_id)
            if not existing_schedule:
                return ResponseUtil.error(message="值班排期不存在")
            
            # 检查人员是否存在
            person = await DutyDao.get_duty_person_by_id(db, schedule_data['person_id'])
            if not person:
                return ResponseUtil.error(message="值班人员不存在")
            
            if person.status != '1':
                return ResponseUtil.error(message="值班人员状态异常，无法安排值班")
            
            # 检查排期冲突（排除当前编辑的排期）
            conflicts = await DutyDao.get_duty_schedule_conflicts(
                db,
                schedule_data['person_id'],
                schedule_data['duty_date'],
                schedule_data['shift_type'],
                exclude_schedule_id=schedule_id
            )
            
            if conflicts:
                return ResponseUtil.error(message="该人员在此时间段已有值班安排")
            
            # 添加更新时间
            schedule_data['update_time'] = datetime.now()
            
            await DutyDao.edit_duty_schedule(db, schedule_data)
            
            return ResponseUtil.success(message="值班排期编辑成功")
            
        except Exception as e:
            raise Exception(f"编辑值班排期失败: {str(e)}")
    
    @classmethod
    async def delete_duty_schedule_service(cls, schedule_ids: List[int], db: AsyncSession):
        """
        删除值班排期
        
        Args:
            schedule_ids: 排期ID列表
            db: 数据库会话
            
        Returns:
            删除结果
        """
        try:
            await DutyDao.delete_duty_schedule(db, schedule_ids)
            
            return ResponseUtil.success(message="值班排期删除成功")
            
        except Exception as e:
            raise Exception(f"删除值班排期失败: {str(e)}")
    
    @classmethod
    async def get_duty_calendar_service(
        cls,
        year: int,
        month: int,
        db: AsyncSession
    ):
        """
        获取值班日历数据
        
        Args:
            year: 年份
            month: 月份
            db: 数据库会话
            
        Returns:
            日历数据
        """
        try:
            # 获取当月的值班排期
            start_date = date(year, month, 1)
            
            # 获取当月最后一天
            if month == 12:
                next_month = date(year + 1, 1, 1)
            else:
                next_month = date(year, month + 1, 1)
            end_date = next_month - timedelta(days=1)
            
            schedules = await DutyDao.get_duty_schedule_by_date_range(db, start_date, end_date)
            
            # 获取人员信息
            person_ids = list(set([schedule.person_id for schedule in schedules]))
            persons = {}
            for person_id in person_ids:
                person = await DutyDao.get_duty_person_by_id(db, person_id)
                if person:
                    persons[person_id] = person
            
            # 按日期组织数据
            calendar_data = {}
            for schedule in schedules:
                date_str = schedule.duty_date.strftime('%Y-%m-%d')
                person = persons.get(schedule.person_id)
                
                if date_str not in calendar_data:
                    calendar_data[date_str] = []
                
                calendar_data[date_str].append({
                    'schedule_id': schedule.schedule_id,
                    'person_id': schedule.person_id,
                    'person_name': person.person_name if person else "未知",
                    'department': person.department if person else "未知",
                    'duty_type': schedule.duty_type,
                    'duty_type_name': {"primary": "主值班", "backup": "备值班", "emergency": "应急值班"}.get(schedule.duty_type, "未知"),
                    'shift_type': schedule.shift_type,
                    'shift_type_name': {"day": "白班", "night": "夜班", "all": "全天"}.get(schedule.shift_type, "未知"),
                    'remarks': schedule.remarks
                })
            
            return ResponseUtil.success(data=calendar_data)
            
        except Exception as e:
            raise Exception(f"获取值班日历失败: {str(e)}")
    
    @classmethod
    async def get_current_duty_person_service(cls, db: AsyncSession):
        """
        获取当前值班人员
        
        Args:
            db: 数据库会话
            
        Returns:
            当前值班人员信息
        """
        try:
            # 获取主值班人员
            primary_duty = await DutyDao.get_current_duty_person(db, "primary")
            
            # 获取备值班人员
            backup_duty = await DutyDao.get_current_duty_person(db, "backup")
            
            return ResponseUtil.success(data={
                'primary_duty': primary_duty,
                'backup_duty': backup_duty
            })
            
        except Exception as e:
            raise Exception(f"获取当前值班人员失败: {str(e)}")
    
    @classmethod
    async def get_duty_statistics_service(cls, db: AsyncSession):
        """
        获取值班统计信息
        
        Args:
            db: 数据库会话
            
        Returns:
            统计信息
        """
        try:
            stats = await DutyDao.get_duty_statistics(db)
            
            return ResponseUtil.success(data=stats)
            
        except Exception as e:
            raise Exception(f"获取值班统计信息失败: {str(e)}") 