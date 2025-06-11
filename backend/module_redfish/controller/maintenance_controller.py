"""
硬件更换排期Controller（轻量化方案）
基于现有告警系统扩展，提供排期管理REST API
"""
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from utils.response_util import ResponseUtil
from utils.page_util import PageResponseModel  
from utils.log_util import logger
from config.get_db import get_db
from config.enums import BusinessType
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_redfish.service.maintenance_service import MaintenanceService
from module_redfish.entity.vo.maintenance_vo import (
    MaintenanceSchedulePageQueryModel,
    CreateMaintenanceScheduleModel,
    UpdateMaintenanceScheduleModel,
    BatchUpdateScheduleModel
)

maintenanceController = APIRouter(prefix='/redfish/maintenance', tags=['硬件更换排期管理'])


@maintenanceController.get(
    '/list',
    response_model=PageResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:maintenance:list'))]
)
@Log(title='硬件更换排期', business_type=BusinessType.OTHER)
async def get_maintenance_schedule_list(
    request: Request,
    maintenance_schedule_page_query: MaintenanceSchedulePageQueryModel = Depends(MaintenanceSchedulePageQueryModel.as_query),
    db: AsyncSession = Depends(get_db)
):
    """
    获取硬件更换排期列表
    
    Args:
        request: Request对象
        maintenance_schedule_page_query: 查询参数
        db: 数据库会话
        
    Returns:
        PageResponseModel: 排期列表数据
    """
    try:
        # 获取查询参数
        query_object = maintenance_schedule_page_query
        is_page = True
        
        # 调用service层获取数据
        maintenance_schedule_result = await MaintenanceService.get_maintenance_schedule_list_services(
            db, query_object, is_page
        )
        
        logger.info('获取硬件更换排期列表成功')
        return maintenance_schedule_result
        
    except Exception as e:
        logger.error(f'获取硬件更换排期列表失败: {str(e)}')
        return PageResponseModel(rows=[], page_num=1, page_size=10, total=0, has_next=False)


@maintenanceController.get(
    '/detail/{alert_id}',
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:maintenance:query'))]
)
@Log(title='硬件更换排期', business_type=BusinessType.OTHER)
async def get_maintenance_schedule_detail(
    request: Request,
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取硬件更换排期详情
    
    Args:
        request: Request对象
        alert_id: 告警ID
        db: 数据库会话
        
    Returns:
        响应结果
    """
    try:
        maintenance_schedule_detail = await MaintenanceService.get_maintenance_schedule_detail_services(
            db, alert_id
        )
        
        if maintenance_schedule_detail:
            logger.info(f'获取硬件更换排期详情成功: {alert_id}')
            return ResponseUtil.success(data=maintenance_schedule_detail)
        else:
            return ResponseUtil.failure(msg='排期不存在')
            
    except Exception as e:
        logger.error(f'获取硬件更换排期详情失败: {str(e)}')
        return ResponseUtil.failure(msg='获取排期详情失败')


@maintenanceController.post(
    '/add',
    response_model=CrudResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:maintenance:add'))]
)
@Log(title='硬件更换排期', business_type=BusinessType.INSERT)
async def add_maintenance_schedule(
    request: Request,
    add_maintenance_schedule: CreateMaintenanceScheduleModel,
    db: AsyncSession = Depends(get_db)
):
    """
    新增硬件更换排期
    
    Args:
        request: Request对象
        add_maintenance_schedule: 新增排期对象
        db: 数据库会话
        
    Returns:
        CrudResponseModel: 响应结果
    """
    try:
        add_maintenance_schedule_result = await MaintenanceService.create_maintenance_schedule_services(
            db, add_maintenance_schedule
        )
        
        logger.info(f'新增硬件更换排期: {add_maintenance_schedule.device_id}')
        return add_maintenance_schedule_result
        
    except Exception as e:
        logger.error(f'新增硬件更换排期失败: {str(e)}')
        return ResponseUtil.failure(msg='新增排期失败')


@maintenanceController.put(
    '/edit',
    response_model=CrudResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:maintenance:edit'))]
)
@Log(title='硬件更换排期', business_type=BusinessType.UPDATE)
async def edit_maintenance_schedule(
    request: Request,
    edit_maintenance_schedule: UpdateMaintenanceScheduleModel,
    db: AsyncSession = Depends(get_db)
):
    """
    修改硬件更换排期
    
    Args:
        request: Request对象
        edit_maintenance_schedule: 修改排期对象
        db: 数据库会话
        
    Returns:
        CrudResponseModel: 响应结果
    """
    try:
        edit_maintenance_schedule_result = await MaintenanceService.update_maintenance_schedule_services(
            db, edit_maintenance_schedule
        )
        
        logger.info(f'修改硬件更换排期: {edit_maintenance_schedule.alert_id}')
        return edit_maintenance_schedule_result
        
    except Exception as e:
        logger.error(f'修改硬件更换排期失败: {str(e)}')
        return ResponseUtil.failure(msg='修改排期失败')


@maintenanceController.delete(
    '/delete/{alert_id}',
    response_model=CrudResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:maintenance:remove'))]
)
@Log(title='硬件更换排期', business_type=BusinessType.DELETE)
async def delete_maintenance_schedule(
    request: Request,
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除硬件更换排期
    
    Args:
        request: Request对象
        alert_id: 告警ID
        db: 数据库会话
        
    Returns:
        CrudResponseModel: 响应结果
    """
    try:
        delete_maintenance_schedule_result = await MaintenanceService.delete_maintenance_schedule_services(
            db, alert_id
        )
        
        logger.info(f'删除硬件更换排期: {alert_id}')
        return delete_maintenance_schedule_result
        
    except Exception as e:
        logger.error(f'删除硬件更换排期失败: {str(e)}')
        return ResponseUtil.failure(msg='删除排期失败')


@maintenanceController.get(
    '/statistics',
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:maintenance:list'))]
)
@Log(title='硬件更换排期', business_type=BusinessType.OTHER)
async def get_maintenance_statistics(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    获取硬件更换排期统计信息
    
    Args:
        request: Request对象
        db: 数据库会话
        
    Returns:
        响应结果
    """
    try:
        statistics = await MaintenanceService.get_maintenance_statistics_services(db)
        
        logger.info('获取硬件更换排期统计信息成功')
        return ResponseUtil.success(data=statistics.model_dump())
        
    except Exception as e:
        logger.error(f'获取硬件更换排期统计信息失败: {str(e)}')
        return ResponseUtil.failure(msg='获取统计信息失败')


@maintenanceController.get(
    '/calendar',
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:maintenance:list'))]
)
@Log(title='硬件更换排期', business_type=BusinessType.OTHER)
async def get_maintenance_calendar(
    request: Request,
    year: int = Query(..., description="年份"),
    month: int = Query(..., description="月份", ge=1, le=12),
    db: AsyncSession = Depends(get_db)
):
    """
    获取硬件更换排期日历数据
    
    Args:
        request: Request对象
        year: 年份
        month: 月份
        db: 数据库会话
        
    Returns:
        响应结果
    """
    try:
        calendar_data = await MaintenanceService.get_maintenance_calendar_services(db, year, month)
        
        logger.info(f'获取硬件更换排期日历数据成功: {year}-{month}')
        return ResponseUtil.success(data=calendar_data)
        
    except Exception as e:
        logger.error(f'获取硬件更换排期日历数据失败: {str(e)}')
        return ResponseUtil.failure(msg='获取日历数据失败')


@maintenanceController.post(
    '/batch-update',
    response_model=CrudResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:maintenance:edit'))]
)
@Log(title='硬件更换排期', business_type=BusinessType.UPDATE)
async def batch_update_maintenance_schedules(
    request: Request,
    batch_update_data: BatchUpdateScheduleModel,
    db: AsyncSession = Depends(get_db)
):
    """
    批量更新硬件更换排期
    
    Args:
        request: Request对象
        batch_update_data: 批量更新数据
        db: 数据库会话
        
    Returns:
        CrudResponseModel: 响应结果
    """
    try:
        batch_update_result = await MaintenanceService.batch_update_schedules_services(
            db, batch_update_data
        )
        
        logger.info(f'批量更新硬件更换排期: {len(batch_update_data.alert_ids)}条')
        return batch_update_result
        
    except Exception as e:
        logger.error(f'批量更新硬件更换排期失败: {str(e)}')
        return ResponseUtil.failure(msg='批量更新失败')


@maintenanceController.get(
    '/urgency-options',
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:maintenance:list'))]
)
async def get_urgency_level_options(request: Request):
    """
    获取紧急程度选项列表
    
    Args:
        request: Request对象
        
    Returns:
        响应结果
    """
    try:
        options = await MaintenanceService.get_urgency_level_options_services()
        
        logger.info('获取紧急程度选项成功')
        return ResponseUtil.success(data=options)
        
    except Exception as e:
        logger.error(f'获取紧急程度选项失败: {str(e)}')
        return ResponseUtil.failure(msg='获取选项失败')


@maintenanceController.post(
    '/auto-create/{alert_id}',
    response_model=CrudResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:maintenance:add'))]
)
@Log(title='硬件更换排期', business_type=BusinessType.INSERT)
async def auto_create_schedule_from_alert(
    request: Request,
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    从告警自动创建硬件更换排期
    
    Args:
        request: Request对象
        alert_id: 告警ID
        db: 数据库会话
        
    Returns:
        CrudResponseModel: 响应结果
    """
    try:
        auto_create_result = await MaintenanceService.auto_create_schedule_from_alert_services(
            db, alert_id
        )
        
        logger.info(f'从告警自动创建排期: {alert_id}')
        return auto_create_result
        
    except Exception as e:
        logger.error(f'从告警自动创建排期失败: {str(e)}')
        return ResponseUtil.failure(msg='自动创建排期失败')


@maintenanceController.get(
    '/report',
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:maintenance:export'))]
)
@Log(title='硬件更换排期', business_type=BusinessType.OTHER)
async def generate_maintenance_report(
    request: Request,
    start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期 YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db)
):
    """
    生成硬件更换排期报告
    
    Args:
        request: Request对象
        start_date: 开始日期
        end_date: 结束日期
        db: 数据库会话
        
    Returns:
        响应结果
    """
    try:
        # 解析日期
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        
        report = await MaintenanceService.generate_maintenance_report_services(
            db, start_datetime, end_datetime
        )
        
        logger.info(f'生成硬件更换排期报告成功: {start_date} - {end_date}')
        return ResponseUtil.success(data=report.model_dump())
        
    except ValueError as e:
        logger.error(f'日期格式错误: {str(e)}')
        return ResponseUtil.failure(msg='日期格式错误，请使用YYYY-MM-DD格式')
    except Exception as e:
        logger.error(f'生成硬件更换排期报告失败: {str(e)}')
        return ResponseUtil.failure(msg='生成报告失败')


@maintenanceController.get(
    '/export',
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:maintenance:export'))]
)
@Log(title='硬件更换排期', business_type=BusinessType.EXPORT)
async def export_maintenance_schedules(
    request: Request,
    maintenance_schedule_query: MaintenanceSchedulePageQueryModel = Depends(MaintenanceSchedulePageQueryModel.as_query),
    db: AsyncSession = Depends(get_db)
):
    """
    导出硬件更换排期数据
    
    Args:
        request: Request对象
        maintenance_schedule_query: 查询参数
        db: 数据库会话
        
    Returns:
        响应结果
    """
    try:
        # 获取所有数据（不分页）
        export_result = await MaintenanceService.get_maintenance_schedule_list_services(
            db, maintenance_schedule_query, is_page=False
        )
        
        # 构造导出数据
        export_data = []
        for schedule in export_result.rows:
            export_data.append({
                '设备主机名': schedule.get('hostname', ''),
                '业务类型': schedule.get('business_type', ''),
                '组件类型': schedule.get('component_type', ''),
                '组件名称': schedule.get('component_name', ''),
                '紧急程度': schedule.get('urgency_level', ''),
                '计划时间': schedule.get('scheduled_date', ''),
                '负责人': schedule.get('responsible_person', ''),
                '状态': schedule.get('status', ''),
                '描述': schedule.get('description', ''),
                '首次发生时间': schedule.get('first_occurrence', '')
            })
        
        logger.info(f'导出硬件更换排期数据: {len(export_data)}条')
        return ResponseUtil.success(data={
            'export_data': export_data,
            'total_count': len(export_data),
            'export_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        logger.error(f'导出硬件更换排期数据失败: {str(e)}')
        return ResponseUtil.failure(msg='导出数据失败') 