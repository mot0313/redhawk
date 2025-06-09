"""
告警管理Controller层
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
from module_redfish.entity.vo.alert_vo import (
    AlertPageQueryModel, AlertManualOverrideModel, AlertResolveModel, AlertIgnoreModel
)
from module_redfish.service.alert_service import AlertService
from utils.response_util import ResponseUtil
from utils.page_util import PageResponseModel
from utils.log_util import logger


alertController = APIRouter(prefix='/redfish/alert', dependencies=[Depends(LoginService.get_current_user)])


@alertController.get(
    '/list', 
    response_model=PageResponseModel, 
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:alert:list'))]
)
async def get_alert_list(
    request: Request,
    alert_page_query: AlertPageQueryModel = Depends(AlertPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db)
):
    """获取告警列表"""
    try:
        alert_page_query_result = await AlertService.get_alert_list_services(
            query_db, alert_page_query, is_page=True
        )
        logger.info('获取告警列表成功')
        return ResponseUtil.success(model_content=alert_page_query_result)
    except Exception as e:
        logger.error(f'获取告警列表失败: {str(e)}')
        return ResponseUtil.failure(msg='获取告警列表失败')


@alertController.get(
    '/{alert_id}',
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:alert:query'))]
)
async def get_alert_detail(
    request: Request,
    alert_id: int,
    query_db: AsyncSession = Depends(get_db)
):
    """获取告警详情"""
    try:
        alert_detail_result = await AlertService.get_alert_detail_services(query_db, alert_id)
        logger.info(f'获取告警详情成功: {alert_id}')
        return alert_detail_result
    except Exception as e:
        logger.error(f'获取告警详情失败: {str(e)}')
        return ResponseUtil.failure(msg='获取告警详情失败')


@alertController.put('/manualOverride', dependencies=[Depends(CheckUserInterfaceAuth('redfish:alert:override'))])
@ValidateFields(validate_model='manual_override_alert')
@Log(title='告警管理', business_type=BusinessType.UPDATE)
async def manual_override_alert(
    request: Request,
    override_alert: AlertManualOverrideModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """手动覆盖告警级别"""
    try:
        override_alert.manual_operator = current_user.user.user_name
        override_alert.manual_time = datetime.now()
        
        override_result = await AlertService.manual_override_alert_services(query_db, override_alert)
        logger.info(f'手动覆盖告警级别: {override_alert.alert_id}')
        return override_result
    except Exception as e:
        logger.error(f'手动覆盖告警级别失败: {str(e)}')
        return ResponseUtil.failure(msg='手动覆盖告警级别失败')


@alertController.put('/resolve', dependencies=[Depends(CheckUserInterfaceAuth('redfish:alert:resolve'))])
@ValidateFields(validate_model='resolve_alert')
@Log(title='告警管理', business_type=BusinessType.UPDATE)
async def resolve_alerts(
    request: Request,
    resolve_alert: AlertResolveModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """解决告警"""
    try:
        resolve_alert.resolved_by = current_user.user.user_name
        resolve_alert.resolved_time = datetime.now()
        
        resolve_result = await AlertService.resolve_alerts_services(query_db, resolve_alert)
        logger.info(f'解决告警: {resolve_alert.alert_ids}')
        return resolve_result
    except Exception as e:
        logger.error(f'解决告警失败: {str(e)}')
        return ResponseUtil.failure(msg='解决告警失败')


@alertController.put('/ignore', dependencies=[Depends(CheckUserInterfaceAuth('redfish:alert:ignore'))])
@ValidateFields(validate_model='ignore_alert')
@Log(title='告警管理', business_type=BusinessType.UPDATE)
async def ignore_alerts(
    request: Request,
    ignore_alert: AlertIgnoreModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """忽略告警"""
    try:
        ignore_alert.operator = current_user.user.user_name
        ignore_alert.operation_time = datetime.now()
        
        ignore_result = await AlertService.ignore_alerts_services(query_db, ignore_alert)
        logger.info(f'忽略告警: {ignore_alert.alert_ids}')
        return ignore_result
    except Exception as e:
        logger.error(f'忽略告警失败: {str(e)}')
        return ResponseUtil.failure(msg='忽略告警失败')


@alertController.get('/statistics', dependencies=[Depends(CheckUserInterfaceAuth('redfish:alert:list'))])
async def get_alert_statistics(
    request: Request,
    days: int = Query(default=7, description="统计天数"),
    query_db: AsyncSession = Depends(get_db)
):
    """获取告警统计信息"""
    try:
        statistics = await AlertService.get_alert_statistics_services(query_db, days)
        logger.info(f'获取告警统计信息成功: {days}天')
        return ResponseUtil.success(data=statistics)
    except Exception as e:
        logger.error(f'获取告警统计信息失败: {str(e)}')
        return ResponseUtil.failure(msg='获取告警统计信息失败')


@alertController.get('/trend', dependencies=[Depends(CheckUserInterfaceAuth('redfish:alert:list'))])
async def get_alert_trend(
    request: Request,
    days: int = Query(default=7, description="统计天数"),
    query_db: AsyncSession = Depends(get_db)
):
    """获取告警趋势数据"""
    try:
        trend_data = await AlertService.get_alert_trend_services(query_db, days)
        logger.info(f'获取告警趋势数据成功: {days}天')
        return ResponseUtil.success(data=trend_data)
    except Exception as e:
        logger.error(f'获取告警趋势数据失败: {str(e)}')
        return ResponseUtil.failure(msg='获取告警趋势数据失败')


@alertController.get('/realtime', dependencies=[Depends(CheckUserInterfaceAuth('redfish:alert:list'))])
async def get_realtime_alerts(
    request: Request,
    limit: int = Query(default=10, description="返回数量限制"),
    query_db: AsyncSession = Depends(get_db)
):
    """获取实时告警列表"""
    try:
        realtime_alerts = await AlertService.get_realtime_alerts_services(query_db, limit)
        logger.info('获取实时告警列表成功')
        return ResponseUtil.success(data=realtime_alerts)
    except Exception as e:
        logger.error(f'获取实时告警列表失败: {str(e)}')
        return ResponseUtil.failure(msg='获取实时告警列表失败')


@alertController.get('/scheduled', dependencies=[Depends(CheckUserInterfaceAuth('redfish:alert:list'))])
async def get_scheduled_alerts(
    request: Request,
    limit: int = Query(default=10, description="返回数量限制"),
    query_db: AsyncSession = Depends(get_db)
):
    """获取择期告警列表"""
    try:
        scheduled_alerts = await AlertService.get_scheduled_alerts_services(query_db, limit)
        logger.info('获取择期告警列表成功')
        return ResponseUtil.success(data=scheduled_alerts)
    except Exception as e:
        logger.error(f'获取择期告警列表失败: {str(e)}')
        return ResponseUtil.failure(msg='获取择期告警列表失败')


@alertController.get('/distribution', dependencies=[Depends(CheckUserInterfaceAuth('redfish:alert:list'))])
async def get_alert_distribution(
    request: Request,
    query_db: AsyncSession = Depends(get_db)
):
    """获取告警分布统计"""
    try:
        distribution = await AlertService.get_alert_distribution_services(query_db)
        logger.info('获取告警分布统计成功')
        return ResponseUtil.success(data=distribution)
    except Exception as e:
        logger.error(f'获取告警分布统计失败: {str(e)}')
        return ResponseUtil.failure(msg='获取告警分布统计失败')


@alertController.get('/device/{device_id}', dependencies=[Depends(CheckUserInterfaceAuth('redfish:alert:list'))])
async def get_device_alerts(
    request: Request,
    device_id: int,
    query_db: AsyncSession = Depends(get_db)
):
    """获取设备的所有活跃告警"""
    try:
        device_alerts = await AlertService.get_device_alerts_services(query_db, device_id)
        logger.info(f'获取设备告警列表成功: {device_id}')
        return ResponseUtil.success(data=device_alerts)
    except Exception as e:
        logger.error(f'获取设备告警列表失败: {str(e)}')
        return ResponseUtil.failure(msg='获取设备告警列表失败') 