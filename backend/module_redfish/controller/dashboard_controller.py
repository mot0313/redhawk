"""
首页数据Controller层
"""
from datetime import datetime
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, Optional, Literal
from config.get_db import get_db
from module_admin.service.login_service import LoginService
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_redfish.entity.vo.dashboard_vo import DashboardQueryModel
from module_redfish.service.dashboard_service import DashboardService
from utils.response_util import ResponseUtil
from utils.log_util import logger


dashboardController = APIRouter(prefix='/redfish/dashboard', dependencies=[Depends(LoginService.get_current_user)])


@dashboardController.get('/overview', dependencies=[Depends(CheckUserInterfaceAuth('redfish:dashboard:overview'))])
async def get_dashboard_overview(
    request: Request,
    time_range: str = Query(default="7d", description="时间范围: 7d/30d/90d"),
    query_db: AsyncSession = Depends(get_db)
):
    """获取首页概览数据"""
    try:
        query_model = DashboardQueryModel(time_range=time_range)
        overview_data = await DashboardService.get_dashboard_overview_services(query_db, query_model)
        logger.info('获取首页概览数据成功')
        return ResponseUtil.success(data=overview_data)
    except Exception as e:
        logger.error(f'获取首页概览数据失败: {str(e)}')
        return ResponseUtil.failure(msg='获取首页概览数据失败')


@dashboardController.get('/alert/trend', dependencies=[Depends(CheckUserInterfaceAuth('redfish:dashboard:alert'))])
async def get_alert_trend_chart(
    request: Request,
    days: int = Query(default=7, description="统计天数"),
    query_db: AsyncSession = Depends(get_db)
):
    """获取告警趋势图数据"""
    try:
        trend_data = await DashboardService.get_alert_trend_chart_services(query_db, days)
        logger.info(f'获取告警趋势图数据成功: {days}天')
        return ResponseUtil.success(data=trend_data)
    except Exception as e:
        logger.error(f'获取告警趋势图数据失败: {str(e)}')
        return ResponseUtil.failure(msg='获取告警趋势图数据失败')


@dashboardController.get('/device/health', dependencies=[Depends(CheckUserInterfaceAuth('redfish:dashboard:device'))])
async def get_device_health_chart(
    request: Request,
    query_db: AsyncSession = Depends(get_db)
):
    """获取设备健康图数据"""
    try:
        health_data = await DashboardService.get_device_health_chart_services(query_db)
        logger.info('获取设备健康图数据成功')
        return ResponseUtil.success(data=health_data)
    except Exception as e:
        logger.error(f'获取设备健康图数据失败: {str(e)}')
        return ResponseUtil.failure(msg='获取设备健康图数据失败')


@dashboardController.get('/alert/realtime', dependencies=[Depends(CheckUserInterfaceAuth('redfish:dashboard:alert'))])
async def get_realtime_alert_list(
    request: Request,
    limit: int = Query(default=10, description="返回数量限制"),
    query_db: AsyncSession = Depends(get_db)
):
    """获取实时告警列表"""
    try:
        realtime_alerts = await DashboardService.get_realtime_alert_list_services(query_db, limit)
        logger.info('获取实时告警列表成功')
        return ResponseUtil.success(data=realtime_alerts)
    except Exception as e:
        logger.error(f'获取实时告警列表失败: {str(e)}')
        return ResponseUtil.failure(msg='获取实时告警列表失败')


@dashboardController.get('/alert/scheduled', dependencies=[Depends(CheckUserInterfaceAuth('redfish:dashboard:alert'))])
async def get_scheduled_alert_list(
    request: Request,
    limit: int = Query(default=10, description="返回数量限制"),
    query_db: AsyncSession = Depends(get_db)
):
    """获取择期告警列表"""
    try:
        scheduled_alerts = await DashboardService.get_scheduled_alert_list_services(query_db, limit)
        logger.info('获取择期告警列表成功')
        return ResponseUtil.success(data=scheduled_alerts)
    except Exception as e:
        logger.error(f'获取择期告警列表失败: {str(e)}')
        return ResponseUtil.failure(msg='获取择期告警列表失败')


@dashboardController.get('/device/summary', dependencies=[Depends(CheckUserInterfaceAuth('redfish:dashboard:device'))])
async def get_device_health_summary(
    request: Request,
    limit: int = Query(default=20, description="返回数量限制"),
    query_db: AsyncSession = Depends(get_db)
):
    """获取设备健康汇总列表"""
    try:
        device_summary = await DashboardService.get_device_health_summary_services(query_db, limit)
        logger.info('获取设备健康汇总列表成功')
        return ResponseUtil.success(data=device_summary)
    except Exception as e:
        logger.error(f'获取设备健康汇总列表失败: {str(e)}')
        return ResponseUtil.failure(msg='获取设备健康汇总列表失败')


@dashboardController.get('/metrics', dependencies=[Depends(CheckUserInterfaceAuth('redfish:dashboard:metrics'))])
async def get_system_health_metrics(
    request: Request,
    query_db: AsyncSession = Depends(get_db)
):
    """获取系统健康指标"""
    try:
        metrics_data = await DashboardService.get_system_health_metrics_services(query_db)
        logger.info('获取系统健康指标成功')
        return ResponseUtil.success(data=metrics_data)
    except Exception as e:
        logger.error(f'获取系统健康指标失败: {str(e)}')
        return ResponseUtil.failure(msg='获取系统健康指标失败')


@dashboardController.get('/complete', dependencies=[Depends(CheckUserInterfaceAuth('redfish:dashboard:view'))])
async def get_complete_dashboard_data(
    request: Request,
    time_range: str = Query(default="7d", description="时间范围: 7d/30d/90d"),
    query_db: AsyncSession = Depends(get_db)
):
    """获取完整的首页数据（一次性获取所有数据）"""
    try:
        query_model = DashboardQueryModel(time_range=time_range)
        complete_data = await DashboardService.get_complete_dashboard_data_services(query_db, query_model)
        logger.info('获取完整首页数据成功')
        return ResponseUtil.success(data=complete_data)
    except Exception as e:
        logger.error(f'获取完整首页数据失败: {str(e)}')
        return ResponseUtil.failure(msg='获取完整首页数据失败')


@dashboardController.get('/refresh', dependencies=[Depends(CheckUserInterfaceAuth('redfish:dashboard:view'))])
async def refresh_dashboard_data(
    request: Request,
    component: str = Query(default="all", description="刷新组件: all/overview/alert/device/metrics"),
    time_range: str = Query(default="7d", description="时间范围: 7d/30d/90d"),
    query_db: AsyncSession = Depends(get_db)
):
    """刷新首页数据"""
    try:
        query_model = DashboardQueryModel(time_range=time_range)
        
        if component == "all":
            data = await DashboardService.get_complete_dashboard_data_services(query_db, query_model)
        elif component == "overview":
            data = await DashboardService.get_dashboard_overview_services(query_db, query_model)
        elif component == "alert":
            days = 7 if time_range == "7d" else 30 if time_range == "30d" else 90
            trend_data = await DashboardService.get_alert_trend_chart_services(query_db, days)
            realtime_alerts = await DashboardService.get_realtime_alert_list_services(query_db, 10)
            scheduled_alerts = await DashboardService.get_scheduled_alert_list_services(query_db, 10)
            data = {
                "trend": trend_data,
                "realtime": realtime_alerts,
                "scheduled": scheduled_alerts
            }
        elif component == "device":
            health_chart = await DashboardService.get_device_health_chart_services(query_db)
            health_summary = await DashboardService.get_device_health_summary_services(query_db, 20)
            data = {
                "health_chart": health_chart,
                "health_summary": health_summary
            }
        elif component == "metrics":
            data = await DashboardService.get_system_health_metrics_services(query_db)
        else:
            return ResponseUtil.failure(msg="无效的组件参数")
        
        logger.info(f'刷新首页数据成功: {component}')
        return ResponseUtil.success(data=data)
    except Exception as e:
        logger.error(f'刷新首页数据失败: {str(e)}')
        return ResponseUtil.failure(msg='刷新首页数据失败') 