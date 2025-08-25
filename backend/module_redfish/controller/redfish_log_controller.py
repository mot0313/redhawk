"""
Redfish日志管理Controller层
"""
from datetime import datetime
from fastapi import APIRouter, Depends, Request, Query, Form
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
    RedfishLogCleanupResultModel, RedfishLogTempCollectResultModel
)
from module_redfish.service.redfish_log_service import RedfishLogService
from utils.response_util import ResponseUtil
from utils.log_util import logger
from utils.excel_util import ExcelUtil
from utils.common_util import bytes2file_response


redfishLogController = APIRouter(prefix='/redfish/log', dependencies=[Depends(LoginService.get_current_user)])


@redfishLogController.get(
    '/list', 
    response_model=RedfishLogPageResponseModel, 
    dependencies=[Depends(CheckUserInterfaceAuth(['redfish:log:list', 'redfish:log:history']))]
)
async def get_redfish_log_list(
    request: Request,
    device_id: Optional[int] = Query(None, description="设备ID", alias="deviceId"),
    device_ip: Optional[str] = Query(None, description="设备IP地址", alias="deviceIp"),
    log_source: Optional[str] = Query(None, description="日志来源", alias="logSource"),
    severity: Optional[str] = Query(None, description="严重程度"),
    message_keyword: Optional[str] = Query(None, description="消息关键词", alias="messageKeyword"),
    start_time: Optional[str] = Query(None, description="开始时间", alias="startTime"),
    end_time: Optional[str] = Query(None, description="结束时间", alias="endTime"),
    page_num: int = Query(1, ge=1, description="页码", alias="pageNum"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量", alias="pageSize"),
    query_db: AsyncSession = Depends(get_db)
):
    """获取日志列表"""
    try:
        # 构建查询模型
        query_model = RedfishLogPageQueryModel.as_query(
            device_id=device_id,
            device_ip=device_ip,
            log_source=log_source,
            severity=severity,
            message_keyword=message_keyword,
            start_time=start_time,
            end_time=end_time,
            page_num=page_num,
            page_size=page_size
        )
        
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
    dependencies=[Depends(CheckUserInterfaceAuth(['redfish:log:collect', 'redfish:log:temp:collect', 'redfish:log:history:view']))]
)
async def collect_device_logs(
    request: Request,
    collect_request: DeviceLogCollectModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """收集设备日志"""
    try:
        # 临时收集模式不记录操作日志，直接处理
        if collect_request.no_storage:
            collect_result = await RedfishLogService.collect_device_logs_services(
                query_db, collect_request, current_user.user.user_name
            )
            logger.info(f'临时日志收集完成: {collect_result.message}')
            return ResponseUtil.success(data=collect_result)
        
        # 常规收集模式：手动记录操作日志，因为@Log装饰器会记录完整响应
        collect_result = await RedfishLogService.collect_device_logs_services(
            query_db, collect_request, current_user.user.user_name
        )
        logger.info(f'日志收集任务完成: {collect_result.message}')
        return ResponseUtil.success(data=collect_result)
    except Exception as e:
        logger.error(f'收集设备日志失败: {str(e)}')
        return ResponseUtil.failure(msg='收集设备日志失败')


@redfishLogController.get(
    '/device/list',
    dependencies=[Depends(CheckUserInterfaceAuth(['redfish:log:temp', 'redfish:log:history', 'redfish:log:collect']))]
)
async def get_devices_for_log(
    request: Request,
    query_db: AsyncSession = Depends(get_db)
):
    """获取设备列表（用于日志收集）"""
    try:
        from module_redfish.service.device_service import DeviceService
        from module_redfish.entity.vo.device_vo import DevicePageQueryModel
        
        # 创建查询对象，获取所有设备
        query_object = DevicePageQueryModel(page_size=1000)
        device_page_result = await DeviceService.get_device_list_services(
            query_db, query_object, is_page=True
        )
        
        logger.info('获取日志收集设备列表成功')
        return ResponseUtil.success(data=device_page_result)
    except Exception as e:
        logger.error(f'获取日志收集设备列表失败: {str(e)}')
        return ResponseUtil.failure(msg='获取设备列表失败')


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


@redfishLogController.post(
    '/export/data',
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:log:export'))]
)
@Log(title='日志管理', business_type=BusinessType.EXPORT)
async def export_logs_data(
    request: Request,
    log_page_query: RedfishLogPageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db)
):
    """导出日志数据"""
    try:
        # 获取全量数据
        logs_list = await RedfishLogService.get_redfish_log_list_services(
            query_db, log_page_query, is_page=False
        )
        
        # 调用导出服务
        export_result = await RedfishLogService.export_logs_data_services(logs_list)
        logger.info('导出成功')
        
        return ResponseUtil.streaming(data=bytes2file_response(export_result))
        
    except Exception as e:
        logger.error(f'导出日志数据失败: {str(e)}')
        return ResponseUtil.failure(msg='导出日志数据失败')
