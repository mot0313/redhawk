"""
Redfish日志管理Controller层
"""
from datetime import datetime
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, Optional, Literal
from pydantic_validation_decorator import ValidateFields
from config.get_db import get_db
from config.enums import BusinessType
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_redfish.entity.vo.redfish_log_vo import (
    RedfishLogPageQueryModel, RedfishLogDetailModel, DeviceLogCollectModel,
    RedfishLogPageResponseModel, RedfishLogStatsModel, RedfishLogCollectResultModel,
    RedfishLogCleanupResultModel
)
from module_redfish.service.redfish_log_service import RedfishLogService
from utils.response_util import ResponseUtil
from utils.log_util import logger


redfishLogController = APIRouter(prefix='/redfish/log', dependencies=[Depends(LoginService.get_current_user)])


@redfishLogController.get(
    '/list', 
    response_model=RedfishLogPageResponseModel, 
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:log:list'))]
)
async def get_redfish_log_list(
    request: Request,
    query_model: RedfishLogPageQueryModel = Depends(RedfishLogPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db)
):
    """获取日志列表"""
    try:
        log_page_query_result = await RedfishLogService.get_redfish_log_list_services(
            query_db, query_model, is_page=True
        )
        logger.info('获取日志列表成功')
        return ResponseUtil.success(model_content=log_page_query_result)
    except Exception as e:
        logger.error(f'获取日志列表失败: {str(e)}')
        return ResponseUtil.failure(msg='获取日志列表失败')


@redfishLogController.get(
    '/statistics', 
    response_model=RedfishLogStatsModel, 
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:log:list'))]
)
async def get_redfish_log_statistics(
    request: Request,
    query_db: AsyncSession = Depends(get_db)
):
    """获取日志统计信息"""
    try:
        stats_result = await RedfishLogService.get_redfish_log_stats_services(query_db)
        logger.info('获取日志统计信息成功')
        return ResponseUtil.success(data=stats_result)
    except Exception as e:
        logger.error(f'获取日志统计信息失败: {str(e)}')
        return ResponseUtil.failure(msg='获取日志统计信息失败')


@redfishLogController.get(
    '/{log_id}',
    response_model=RedfishLogDetailModel,
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:log:query'))]
)
async def get_redfish_log_detail(
    request: Request,
    log_id: str,
    query_db: AsyncSession = Depends(get_db)
):
    """获取日志详情"""
    try:
        log_detail = await RedfishLogService.get_redfish_log_detail_services(query_db, log_id)
        logger.info(f'获取日志详情成功: {log_id}')
        return ResponseUtil.success(data=log_detail)
    except ValueError as e:
        logger.warning(f'获取日志详情失败: {str(e)}')
        return ResponseUtil.failure(msg=str(e))
    except Exception as e:
        logger.error(f'获取日志详情失败: {str(e)}')
        return ResponseUtil.failure(msg='获取日志详情失败')


@redfishLogController.post(
    '/collect', 
    response_model=RedfishLogCollectResultModel,
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:log:collect'))]
)
@Log(title='日志管理', business_type=BusinessType.OTHER)
async def collect_device_logs(
    request: Request,
    collect_request: DeviceLogCollectModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """收集设备日志"""
    try:
        collect_result = await RedfishLogService.collect_device_logs_services(
            query_db, collect_request, current_user.user.user_name
        )
        logger.info(f'日志收集任务完成: {collect_result.message}')
        return ResponseUtil.success(data=collect_result)
    except Exception as e:
        logger.error(f'收集设备日志失败: {str(e)}')
        return ResponseUtil.failure(msg='收集设备日志失败')


@redfishLogController.post(
    '/cleanup', 
    response_model=RedfishLogCleanupResultModel,
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:log:cleanup'))]
)
@Log(title='日志管理', business_type=BusinessType.CLEAN)
async def cleanup_old_logs(
    request: Request,
    days: int = Query(30, ge=1, le=365, description="保留天数"),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """清理旧日志"""
    try:
        cleanup_result = await RedfishLogService.cleanup_old_logs_services(query_db, days)
        logger.info(f'日志清理完成: {cleanup_result.message}')
        return ResponseUtil.success(data=cleanup_result)
    except Exception as e:
        logger.error(f'清理旧日志失败: {str(e)}')
        return ResponseUtil.failure(msg='清理旧日志失败')


@redfishLogController.delete(
    '/{log_id}', 
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:log:remove'))]
)
@Log(title='日志管理', business_type=BusinessType.DELETE)
async def delete_redfish_log(
    request: Request,
    log_id: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """删除日志"""
    try:
        delete_result = await RedfishLogService.delete_redfish_log_services(query_db, log_id)
        logger.info(f'删除日志: {log_id}')
        return delete_result
    except Exception as e:
        logger.error(f'删除日志失败: {str(e)}')
        return ResponseUtil.failure(msg='删除日志失败')


@redfishLogController.delete(
    '/device/{device_id}', 
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:log:remove'))]
)
@Log(title='日志管理', business_type=BusinessType.DELETE)
async def delete_device_logs(
    request: Request,
    device_id: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """删除指定设备的所有日志"""
    try:
        delete_result = await RedfishLogService.delete_device_logs_services(query_db, device_id)
        logger.info(f'删除设备日志: device_id={device_id}')
        return delete_result
    except Exception as e:
        logger.error(f'删除设备日志失败: {str(e)}')
        return ResponseUtil.failure(msg='删除设备日志失败')


@redfishLogController.get(
    '/export/data',
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:log:export'))]
)
async def export_logs_data(
    request: Request,
    device_id: Optional[int] = Query(None, description="设备ID"),
    log_source: Optional[str] = Query(None, description="日志来源"),
    severity: Optional[str] = Query(None, description="严重程度"),
    start_time: Optional[str] = Query(None, description="开始时间"),
    end_time: Optional[str] = Query(None, description="结束时间"),
    query_db: AsyncSession = Depends(get_db)
):
    """导出日志数据"""
    try:
        # 构建查询条件
        query_model = RedfishLogPageQueryModel.as_query(
            device_id=device_id,
            log_source=log_source,
            severity=severity,
            start_time=start_time,
            end_time=end_time,
            page_size=10000  # 导出时设置较大的页面大小
        )
        
        # 获取日志列表
        logs_list = await RedfishLogService.get_redfish_log_list_services(
            query_db, query_model, is_page=False
        )
        
        # 转换为导出格式
        export_data = []
        for log in logs_list:
            export_data.append({
                "日志ID": log.log_id,
                "设备ID": log.device_id,
                "设备IP": log.device_ip,
                "日志来源": log.log_source,
                "严重程度": log.severity,
                "创建时间": log.created_time.strftime("%Y-%m-%d %H:%M:%S") if log.created_time else "",
                "收集时间": log.collected_time.strftime("%Y-%m-%d %H:%M:%S") if log.collected_time else "",
                "消息内容": log.message or "",
                "传感器类型": log.sensor_type or "",
                "传感器编号": log.sensor_number or "",
                "备注": log.remark or ""
            })
        
        logger.info(f'导出日志数据成功，共 {len(export_data)} 条记录')
        return ResponseUtil.success(data=export_data, msg=f'导出成功，共 {len(export_data)} 条记录')
        
    except Exception as e:
        logger.error(f'导出日志数据失败: {str(e)}')
        return ResponseUtil.failure(msg='导出日志数据失败')
