"""
值班管理Controller层
"""
from fastapi import APIRouter, Depends, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date
from config.get_db import get_db
from module_redfish.service.duty_service import DutyService
from module_redfish.entity.vo.duty_vo import (
    DutyPersonPageQueryModel, DutyPersonModel, DutyPersonQueryModel,
    DutySchedulePageQueryModel, DutyScheduleModel, DutyScheduleQueryModel,
    DutyPersonAddModel, DutyPersonEditModel,
    DutyScheduleAddModel, DutyScheduleEditModel
)
from utils.response_util import ResponseUtil
from utils.log_util import logger
from module_admin.service.login_service import LoginService

# 创建路由
duty_controller = APIRouter(prefix="/redfish/duty", dependencies=[Depends(LoginService.get_current_user)])

@duty_controller.get("/person/list", summary="获取值班人员列表")
async def get_duty_person_list(
    request_param: DutyPersonPageQueryModel = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    获取值班人员列表
    
    Args:
        request_param: 分页查询参数
        db: 数据库会话
        
    Returns:
        人员列表
    """
    try:
        logger.info(f"获取值班人员列表 - 查询参数: {request_param}")
        
        # 计算偏移量
        request_param.page_num = (request_param.page_num - 1) * request_param.page_size
        
        result = await DutyService.get_duty_person_list_service(
            query_object=request_param,
            db=db,
            is_page=True
        )
        
        logger.info("获取值班人员列表成功")
        return result
        
    except Exception as e:
        logger.error(f"获取值班人员列表失败: {str(e)}")
        return ResponseUtil.error(message=f"获取值班人员列表失败: {str(e)}")


@duty_controller.get("/person/all", summary="获取所有值班人员")
async def get_all_duty_persons(
    person_name: Optional[str] = Query(None, description="人员姓名"),
    department: Optional[str] = Query(None, description="部门"),
    status: Optional[str] = Query("1", description="状态"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有值班人员（不分页）
    
    Args:
        person_name: 人员姓名
        department: 部门
        status: 状态
        db: 数据库会话
        
    Returns:
        人员列表
    """
    try:
        logger.info("获取所有值班人员")
        
        request_param = DutyPersonPageQueryModel(
            person_name=person_name,
            department=department,
            status=status,
            page_num=1,
            page_size=1000
        )
        
        result = await DutyService.get_duty_person_list_service(
            query_object=request_param,
            db=db,
            is_page=False
        )
        
        logger.info("获取所有值班人员成功")
        return result
        
    except Exception as e:
        logger.error(f"获取所有值班人员失败: {str(e)}")
        return ResponseUtil.error(message=f"获取所有值班人员失败: {str(e)}")


@duty_controller.get("/person/{person_id}", summary="获取值班人员详情")
async def get_duty_person_detail(
    person_id: int = Path(..., description="人员ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取值班人员详情
    
    Args:
        person_id: 人员ID
        db: 数据库会话
        
    Returns:
        人员详情
    """
    try:
        logger.info(f"获取值班人员详情 - ID: {person_id}")
        
        result = await DutyService.get_duty_person_detail_service(
            person_id=person_id,
            db=db
        )
        
        logger.info("获取值班人员详情成功")
        return result
        
    except Exception as e:
        logger.error(f"获取值班人员详情失败: {str(e)}")
        return ResponseUtil.error(message=f"获取值班人员详情失败: {str(e)}")


@duty_controller.post("/person", summary="添加值班人员")
async def add_duty_person(
    person_data: DutyPersonAddModel = Body(..., description="人员信息"),
    db: AsyncSession = Depends(get_db)
):
    """
    添加值班人员
    
    Args:
        person_data: 人员信息
        db: 数据库会话
        
    Returns:
        添加结果
    """
    try:
        logger.info(f"添加值班人员 - 姓名: {person_data.person_name}")
        
        result = await DutyService.add_duty_person_service(
            person_data=person_data.model_dump(),
            db=db
        )
        
        logger.info("添加值班人员成功")
        return result
        
    except Exception as e:
        logger.error(f"添加值班人员失败: {str(e)}")
        return ResponseUtil.error(message=f"添加值班人员失败: {str(e)}")


@duty_controller.put("/person", summary="编辑值班人员")
async def edit_duty_person(
    person_data: DutyPersonEditModel = Body(..., description="人员信息"),
    db: AsyncSession = Depends(get_db)
):
    """
    编辑值班人员
    
    Args:
        person_data: 人员信息
        db: 数据库会话
        
    Returns:
        编辑结果
    """
    try:
        logger.info(f"编辑值班人员 - ID: {person_data.person_id}")
        
        result = await DutyService.edit_duty_person_service(
            person_data=person_data.model_dump(),
            db=db
        )
        
        logger.info("编辑值班人员成功")
        return result
        
    except Exception as e:
        logger.error(f"编辑值班人员失败: {str(e)}")
        return ResponseUtil.error(message=f"编辑值班人员失败: {str(e)}")


@duty_controller.delete("/person/{person_ids}", summary="删除值班人员")
async def delete_duty_person(
    person_ids: str = Path(..., description="人员ID列表，逗号分隔"),
    db: AsyncSession = Depends(get_db)
):
    """
    删除值班人员
    
    Args:
        person_ids: 人员ID列表，逗号分隔
        db: 数据库会话
        
    Returns:
        删除结果
    """
    try:
        person_id_list = [int(x.strip()) for x in person_ids.split(',') if x.strip().isdigit()]
        logger.info(f"删除值班人员 - IDs: {person_id_list}")
        
        result = await DutyService.delete_duty_person_service(
            person_ids=person_id_list,
            db=db
        )
        
        logger.info("删除值班人员成功")
        return result
        
    except Exception as e:
        logger.error(f"删除值班人员失败: {str(e)}")
        return ResponseUtil.error(message=f"删除值班人员失败: {str(e)}")


@duty_controller.get("/schedule/list", summary="获取值班排期列表")
async def get_duty_schedule_list(
    request_param: DutySchedulePageQueryModel = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    获取值班排期列表
    
    Args:
        request_param: 分页查询参数
        db: 数据库会话
        
    Returns:
        排期列表
    """
    try:
        logger.info(f"获取值班排期列表 - 查询参数: {request_param}")
        
        # 计算偏移量
        request_param.page_num = (request_param.page_num - 1) * request_param.page_size
        
        result = await DutyService.get_duty_schedule_list_service(
            query_object=request_param,
            db=db,
            is_page=True
        )
        
        logger.info("获取值班排期列表成功")
        return result
        
    except Exception as e:
        logger.error(f"获取值班排期列表失败: {str(e)}")
        return ResponseUtil.error(message=f"获取值班排期列表失败: {str(e)}")


@duty_controller.get("/schedule/{schedule_id}", summary="获取值班排期详情")
async def get_duty_schedule_detail(
    schedule_id: int = Path(..., description="排期ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取值班排期详情
    
    Args:
        schedule_id: 排期ID
        db: 数据库会话
        
    Returns:
        排期详情
    """
    try:
        logger.info(f"获取值班排期详情 - ID: {schedule_id}")
        
        result = await DutyService.get_duty_schedule_detail_service(
            schedule_id=schedule_id,
            db=db
        )
        
        logger.info("获取值班排期详情成功")
        return result
        
    except Exception as e:
        logger.error(f"获取值班排期详情失败: {str(e)}")
        return ResponseUtil.error(message=f"获取值班排期详情失败: {str(e)}")


@duty_controller.post("/schedule", summary="添加值班排期")
async def add_duty_schedule(
    schedule_data: DutyScheduleAddModel = Body(..., description="排期信息"),
    db: AsyncSession = Depends(get_db)
):
    """
    添加值班排期
    
    Args:
        schedule_data: 排期信息
        db: 数据库会话
        
    Returns:
        添加结果
    """
    try:
        logger.info(f"添加值班排期 - 人员ID: {schedule_data.person_id}, 日期: {schedule_data.duty_date}")
        
        result = await DutyService.add_duty_schedule_service(
            schedule_data=schedule_data.model_dump(),
            db=db
        )
        
        logger.info("添加值班排期成功")
        return result
        
    except Exception as e:
        logger.error(f"添加值班排期失败: {str(e)}")
        return ResponseUtil.error(message=f"添加值班排期失败: {str(e)}")


@duty_controller.put("/schedule", summary="编辑值班排期")
async def edit_duty_schedule(
    schedule_data: DutyScheduleEditModel = Body(..., description="排期信息"),
    db: AsyncSession = Depends(get_db)
):
    """
    编辑值班排期
    
    Args:
        schedule_data: 排期信息
        db: 数据库会话
        
    Returns:
        编辑结果
    """
    try:
        logger.info(f"编辑值班排期 - ID: {schedule_data.schedule_id}")
        
        result = await DutyService.edit_duty_schedule_service(
            schedule_data=schedule_data.model_dump(),
            db=db
        )
        
        logger.info("编辑值班排期成功")
        return result
        
    except Exception as e:
        logger.error(f"编辑值班排期失败: {str(e)}")
        return ResponseUtil.error(message=f"编辑值班排期失败: {str(e)}")


@duty_controller.delete("/schedule/{schedule_ids}", summary="删除值班排期")
async def delete_duty_schedule(
    schedule_ids: str = Path(..., description="排期ID列表，逗号分隔"),
    db: AsyncSession = Depends(get_db)
):
    """
    删除值班排期
    
    Args:
        schedule_ids: 排期ID列表，逗号分隔
        db: 数据库会话
        
    Returns:
        删除结果
    """
    try:
        schedule_id_list = [int(x.strip()) for x in schedule_ids.split(',') if x.strip().isdigit()]
        logger.info(f"删除值班排期 - IDs: {schedule_id_list}")
        
        result = await DutyService.delete_duty_schedule_service(
            schedule_ids=schedule_id_list,
            db=db
        )
        
        logger.info("删除值班排期成功")
        return result
        
    except Exception as e:
        logger.error(f"删除值班排期失败: {str(e)}")
        return ResponseUtil.error(message=f"删除值班排期失败: {str(e)}")


@duty_controller.get("/calendar/{year}/{month}", summary="获取值班日历")
async def get_duty_calendar(
    year: int = Path(..., description="年份"),
    month: int = Path(..., description="月份", ge=1, le=12),
    db: AsyncSession = Depends(get_db)
):
    """
    获取值班日历
    
    Args:
        year: 年份
        month: 月份
        db: 数据库会话
        
    Returns:
        日历数据
    """
    try:
        logger.info(f"获取值班日历 - {year}年{month}月")
        
        result = await DutyService.get_duty_calendar_service(
            year=year,
            month=month,
            db=db
        )
        
        logger.info("获取值班日历成功")
        return result
        
    except Exception as e:
        logger.error(f"获取值班日历失败: {str(e)}")
        return ResponseUtil.error(message=f"获取值班日历失败: {str(e)}")


@duty_controller.get("/current", summary="获取当前值班人员")
async def get_current_duty_person(
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前值班人员
    
    Args:
        db: 数据库会话
        
    Returns:
        当前值班人员信息
    """
    try:
        logger.info("获取当前值班人员")
        
        result = await DutyService.get_current_duty_person_service(db=db)
        
        logger.info("获取当前值班人员成功")
        return result
        
    except Exception as e:
        logger.error(f"获取当前值班人员失败: {str(e)}")
        return ResponseUtil.error(message=f"获取当前值班人员失败: {str(e)}")


@duty_controller.get("/statistics", summary="获取值班统计信息")
async def get_duty_statistics(
    db: AsyncSession = Depends(get_db)
):
    """
    获取值班统计信息
    
    Args:
        db: 数据库会话
        
    Returns:
        统计信息
    """
    try:
        logger.info("获取值班统计信息")
        
        result = await DutyService.get_duty_statistics_service(db=db)
        
        logger.info("获取值班统计信息成功")
        return result
        
    except Exception as e:
        logger.error(f"获取值班统计信息失败: {str(e)}")
        return ResponseUtil.error(message=f"获取值班统计信息失败: {str(e)}") 