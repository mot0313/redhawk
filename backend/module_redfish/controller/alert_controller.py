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
    AlertPageQueryModel, MaintenanceScheduleModel, 
    MaintenanceUpdateModel, BatchMaintenanceUpdateModel, MaintenancePageQueryModel,
    AlertPageResponseModel, AlertDetailResponseModel, AlertStatsResponseModel,
    CalendarMaintenanceResponseModel, AlertDeleteModel, AlertBatchDeleteModel,
    AlertDeleteResponseModel
)
from module_redfish.service.alert_service import AlertService
from utils.response_util import ResponseUtil
from utils.page_util import PageResponseModel
from utils.log_util import logger
from utils.common_util import bytes2file_response


alertController = APIRouter(prefix='/redfish/alert', dependencies=[Depends(LoginService.get_current_user)])


@alertController.get(
    '/list', 
    response_model=AlertPageResponseModel, 
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


@alertController.get('/calendar-maintenance', response_model=CalendarMaintenanceResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('redfish:alert:maintenance'))])
async def get_calendar_maintenance(
    request: Request,
    start_date: str = Query(description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(description="结束日期 YYYY-MM-DD"),
    query_db: AsyncSession = Depends(get_db)
):
    """获取日历视图的维修计划数据"""
    try:
        calendar_data = await AlertService.get_calendar_maintenance_services(query_db, start_date, end_date)
        logger.info(f'获取日历维修计划成功: {start_date} 到 {end_date}')
        return ResponseUtil.success(model_content=calendar_data)
    except Exception as e:
        logger.error(f'获取日历维修计划失败: {str(e)}')
        return ResponseUtil.failure(msg='获取日历维修计划失败')


@alertController.get(
    '/{alert_id}',
    response_model=AlertDetailResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:alert:list'))]
)
async def get_alert_detail(
    request: Request,
    alert_id: int,
    query_db: AsyncSession = Depends(get_db)
):
    """获取告警详情"""
    try:
        alert_detail_result = await AlertService.get_alert_detail_services(query_db, alert_id)
        if not alert_detail_result:
            return ResponseUtil.failure(msg='告警不存在')
        logger.info(f'获取告警详情成功: {alert_id}')
        return ResponseUtil.success(model_content=alert_detail_result)
    except Exception as e:
        logger.error(f'获取告警详情失败: {str(e)}')
        return ResponseUtil.failure(msg='获取告警详情失败')


@alertController.get('/statistics', response_model=AlertStatsResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('redfish:alert:list'))])
async def get_alert_statistics(
    request: Request,
    days: int = Query(default=7, description="统计天数"),
    query_db: AsyncSession = Depends(get_db)
):
    """获取告警统计信息"""
    try:
        statistics = await AlertService.get_alert_statistics_services(query_db, days)
        logger.info(f'获取告警统计信息成功: {days}天')
        return ResponseUtil.success(model_content=statistics)
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
        return ResponseUtil.success(model_content=trend_data)
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
        return ResponseUtil.success(model_content=realtime_alerts)
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
        return ResponseUtil.success(model_content=scheduled_alerts)
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
        return ResponseUtil.success(model_content=distribution)
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
        return ResponseUtil.success(model_content=device_alerts)
    except Exception as e:
        logger.error(f'获取设备告警列表失败: {str(e)}')
        return ResponseUtil.failure(msg='获取设备告警列表失败')


@alertController.post('/schedule-maintenance', dependencies=[Depends(CheckUserInterfaceAuth('redfish:alert:maintenance'))])
@ValidateFields(validate_model='schedule_maintenance')
@Log(title='告警维修计划', business_type=BusinessType.INSERT)
async def schedule_maintenance(
    request: Request,
    maintenance_schedule: MaintenanceScheduleModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """为告警安排维修时间"""
    try:
        result = await AlertService.schedule_maintenance_services(query_db, maintenance_schedule)
        logger.info(f'安排维修时间成功: alert_id={maintenance_schedule.alert_id}')
        return result
    except Exception as e:
        logger.error(f'安排维修时间失败: {str(e)}')
        return ResponseUtil.failure(msg='安排维修时间失败')


@alertController.put('/update-maintenance', dependencies=[Depends(CheckUserInterfaceAuth('redfish:alert:maintenance'))])
@ValidateFields(validate_model='update_maintenance')
@Log(title='告警维修计划', business_type=BusinessType.UPDATE)
async def update_maintenance(
    request: Request,
    maintenance_update: MaintenanceUpdateModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """更新告警维修计划"""
    try:
        result = await AlertService.update_maintenance_services(query_db, maintenance_update)
        logger.info(f'更新维修计划成功: alert_id={maintenance_update.alert_id}')
        return result
    except Exception as e:
        logger.error(f'更新维修计划失败: {str(e)}')
        return ResponseUtil.failure(msg='更新维修计划失败')


@alertController.put('/batch-schedule-maintenance', dependencies=[Depends(CheckUserInterfaceAuth('redfish:alert:maintenance'))])
@ValidateFields(validate_model='batch_schedule_maintenance')
@Log(title='告警维修计划', business_type=BusinessType.UPDATE)
async def batch_schedule_maintenance(
    request: Request,
    batch_maintenance: BatchMaintenanceUpdateModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """批量安排维修时间"""
    try:
        result = await AlertService.batch_schedule_maintenance_services(query_db, batch_maintenance)
        logger.info(f'批量安排维修时间成功: alert_ids={batch_maintenance.alert_ids}')
        return result
    except Exception as e:
        logger.error(f'批量安排维修时间失败: {str(e)}')
        return ResponseUtil.failure(msg='批量安排维修时间失败')


@alertController.get('/maintenance-schedule', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('redfish:alert:maintenance'))])
async def get_maintenance_schedule(
    request: Request,
    maintenance_query: MaintenancePageQueryModel = Depends(MaintenancePageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db)
):
    """获取维修计划列表"""
    try:
        maintenance_list = await AlertService.get_maintenance_schedule_services(query_db, maintenance_query)
        logger.info('获取维修计划列表成功')
        return ResponseUtil.success(model_content=maintenance_list)
    except Exception as e:
        logger.error(f'获取维修计划列表失败: {str(e)}')
        return ResponseUtil.failure(msg='获取维修计划列表失败')


@alertController.delete('/cancel-maintenance/{alert_id}', dependencies=[Depends(CheckUserInterfaceAuth('redfish:alert:maintenance'))])
@Log(title='告警维修计划', business_type=BusinessType.DELETE)
async def cancel_maintenance(
    request: Request,
    alert_id: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """取消告警维修计划"""
    try:
        result = await AlertService.cancel_maintenance_services(query_db, alert_id, current_user.user.user_name)
        logger.info(f'取消维修计划成功: alert_id={alert_id}')
        return result
    except Exception as e:
        logger.error(f'取消维修计划失败: {str(e)}')
        return ResponseUtil.failure(msg='取消维修计划失败') 


@alertController.delete('/remove/{alert_id}', response_model=AlertDeleteResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('redfish:alert:remove'))])
@Log(title='告警删除', business_type=BusinessType.DELETE)
async def delete_alert(
    request: Request,
    alert_id: int,
    delete_reason: Optional[str] = Query(default=None, description="删除原因"),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """删除告警"""
    try:
        result = await AlertService.delete_alert_services(query_db, alert_id, delete_reason)
        logger.info(f'删除告警成功: alert_id={alert_id}, user={current_user.user.user_name}')
        return ResponseUtil.success(model_content=result)
    except Exception as e:
        logger.error(f'删除告警失败: {str(e)}')
        return ResponseUtil.failure(msg='删除告警失败')


@alertController.delete('/batch-remove', response_model=AlertDeleteResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('redfish:alert:remove'))])
@Log(title='告警批量删除', business_type=BusinessType.DELETE)
async def batch_delete_alerts(
    request: Request,
    batch_delete: AlertBatchDeleteModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """批量删除告警"""
    try:
        result = await AlertService.batch_delete_alerts_services(
            query_db, batch_delete.alert_ids, batch_delete.delete_reason
        )
        logger.info(f'批量删除告警成功: 删除了{len(batch_delete.alert_ids)}个告警, user={current_user.user.user_name}')
        return ResponseUtil.success(model_content=result)
    except Exception as e:
        logger.error(f'批量删除告警失败: {str(e)}')
        return ResponseUtil.failure(msg='批量删除告警失败') 


@alertController.post('/export', dependencies=[Depends(CheckUserInterfaceAuth('redfish:alert:export'))])
@Log(title='告警管理', business_type=BusinessType.EXPORT)
async def export_alert_list(
    request: Request,
    alert_page_query: AlertPageQueryModel = Depends(AlertPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db)
):
    """导出告警列表"""
    try:
        alert_list = await AlertService.get_alert_list_services(
            query_db, alert_page_query, is_page=False
        )
        alert_export_result = await AlertService.export_alert_list_services(alert_list)
        logger.info('导出告警列表成功')
        return ResponseUtil.streaming(data=bytes2file_response(alert_export_result))
    except Exception as e:
        logger.error(f'导出告警列表失败: {str(e)}')
        return ResponseUtil.failure(msg='导出告警列表失败') 