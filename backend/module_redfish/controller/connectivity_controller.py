"""
设备连通性检测Controller层
"""
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from config.get_db import get_db
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_redfish.service.connectivity_service import ConnectivityService
from module_redfish.entity.vo.connectivity_vo import (
    ConnectivityStatsQueryModel,
    BatchCheckQueryModel,
    IpConnectivityQueryModel,
    ConnectivityStatsResponseModel,
    SingleDeviceConnectivityResponseModel
)
from utils.response_util import ResponseUtil
from utils.log_util import logger


connectivityController = APIRouter(
    prefix='/redfish/connectivity', 
    dependencies=[Depends(LoginService.get_current_user)]
)


@connectivityController.post(
    '/check/{device_id}',
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:device:test'))]
)
async def check_single_device_connectivity(
    request: Request,
    device_id: int,
    query_db: AsyncSession = Depends(get_db)
):
    """检测单个设备的业务IP连通性"""
    try:
        service_result = await ConnectivityService.check_device_business_ip_connectivity(
            query_db, device_id=device_id
        )
        
        # 转换为响应模型（驼峰命名）
        response_model = SingleDeviceConnectivityResponseModel.from_service_result(service_result)
        
        if service_result.get("online", False):
            logger.info(f'设备 {device_id} 连通性检测成功: 在线')
            return ResponseUtil.success(
                model_content=response_model,
                msg='设备在线'
            )
        else:
            logger.info(f'设备 {device_id} 连通性检测完成: 离线')
            return ResponseUtil.success(
                model_content=response_model,
                msg='设备离线'
            )
            
    except Exception as e:
        logger.error(f'检测设备 {device_id} 连通性失败: {str(e)}')
        return ResponseUtil.failure(msg=f'连通性检测失败: {str(e)}')


@connectivityController.post(
    '/batch-check',
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:device:test'))]
)
async def batch_check_devices_connectivity(
    request: Request,
    query_params: BatchCheckQueryModel = Depends(BatchCheckQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db)
):
    """批量检测设备连通性"""
    try:
        device_ids = None
        
        # 尝试从请求体获取device_ids
        try:
            if request.headers.get("content-type", "").startswith("application/json"):
                request_data = await request.json()
                device_ids = request_data.get('deviceIds')
                logger.info(f"从请求体获取到device_ids: {device_ids}")
            else:
                logger.info("请求不包含JSON数据，将检测所有设备")
        except Exception as json_error:
            logger.warning(f"解析请求体JSON失败: {json_error}，将检测所有设备")
        
        # 验证device_ids格式
        if device_ids is not None:
            if not isinstance(device_ids, list):
                logger.error(f"device_ids必须是列表，但收到: {type(device_ids)}")
                return ResponseUtil.failure(msg='device_ids参数必须是列表格式')
            
            # 确保所有元素都是整数
            try:
                device_ids = [int(id) for id in device_ids]
            except (ValueError, TypeError) as e:
                logger.error(f"device_ids包含无效的设备ID: {e}")
                return ResponseUtil.failure(msg='device_ids必须包含有效的设备ID（整数）')
        
        logger.info(f"开始批量连通性检测，设备IDs: {device_ids}, 最大并发: {query_params.max_concurrent}")
        
        service_result = await ConnectivityService.batch_check_connectivity(
            query_db, device_ids=device_ids, max_concurrent=query_params.max_concurrent
        )
        
        # 转换为响应模型（驼峰命名）
        response_model = ConnectivityStatsResponseModel.from_service_result(service_result)
        
        logger.info(f'批量连通性检测完成: {service_result.get("online_devices", 0)} 在线, {service_result.get("offline_devices", 0)} 离线')
        return ResponseUtil.success(
            model_content=response_model,
            msg='批量连通性检测完成'
        )
        
    except Exception as e:
        logger.error(f'批量连通性检测失败: {str(e)}', exc_info=True)
        return ResponseUtil.failure(msg=f'批量检测失败: {str(e)}')


@connectivityController.get(
    '/statistics',
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:device:list'))]
)
async def get_connectivity_statistics(
    request: Request,
    query_params: ConnectivityStatsQueryModel = Depends(ConnectivityStatsQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db)
):
    """获取设备连通性统计"""
    try:
        logger.info(f'获取连通性统计请求: use_cache={query_params.use_cache}, cache_ttl_minutes={query_params.cache_ttl_minutes}')
        
        service_result = await ConnectivityService.get_connectivity_statistics(
            query_db, use_cache=query_params.use_cache, cache_ttl_minutes=query_params.cache_ttl_minutes
        )
        
        # 转换为响应模型（驼峰命名）
        response_model = ConnectivityStatsResponseModel.from_service_result(service_result)
        
        logger.info(f'获取连通性统计成功: {service_result.get("online_devices", 0)} 在线, {service_result.get("offline_devices", 0)} 离线')
        return ResponseUtil.success(
            model_content=response_model,
            msg='获取连通性统计成功'
        )
        
    except Exception as e:
        logger.error(f'获取连通性统计失败: {str(e)}')
        return ResponseUtil.failure(msg=f'获取统计失败: {str(e)}')


@connectivityController.post(
    '/refresh-cache',
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:device:test'))]
)
async def refresh_connectivity_cache(
    request: Request,
    query_db: AsyncSession = Depends(get_db)
):
    """刷新连通性统计缓存"""
    try:
        # 先清理旧缓存
        try:
            from module_admin.service.cache_service import CacheService
            await CacheService.delete_cache("connectivity_stats")
            logger.info("已清理旧的连通性统计缓存")
        except Exception as e:
            logger.warning(f"清理缓存失败: {e}")
        
        # 强制刷新（不使用缓存）
        service_result = await ConnectivityService.get_connectivity_statistics(
            query_db, use_cache=False
        )
        
        # 转换为响应模型（驼峰命名）
        response_model = ConnectivityStatsResponseModel.from_service_result(service_result)
        
        logger.info(f'连通性统计缓存已刷新: {service_result.get("online_devices", 0)} 在线, {service_result.get("offline_devices", 0)} 离线')
        return ResponseUtil.success(
            model_content=response_model,
            msg='缓存已刷新'
        )
        
    except Exception as e:
        logger.error(f'刷新连通性缓存失败: {str(e)}')
        return ResponseUtil.failure(msg=f'刷新缓存失败: {str(e)}')


@connectivityController.post(
    '/clear-cache',
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:device:test'))]
)
async def clear_connectivity_cache(
    request: Request
):
    """清理连通性统计缓存"""
    try:
        from module_admin.service.cache_service import CacheService
        await CacheService.delete_cache("connectivity_stats")
        logger.info("连通性统计缓存已清理")
        return ResponseUtil.success(msg='缓存已清理')
        
    except Exception as e:
        logger.error(f'清理连通性缓存失败: {str(e)}')
        return ResponseUtil.failure(msg=f'清理缓存失败: {str(e)}')


@connectivityController.post(
    '/check-ip',
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:device:test'))]
)
async def check_ip_connectivity(
    request: Request,
    query_db: AsyncSession = Depends(get_db)
):
    """检测指定IP的连通性（不需要在设备库中存在）"""
    try:
        request_data = await request.json()
        business_ip = request_data.get('businessIp')
        
        if not business_ip:
            return ResponseUtil.failure(msg='请提供业务IP地址')
        
        service_result = await ConnectivityService.check_device_business_ip_connectivity(
            query_db, business_ip=business_ip
        )
        
        # 转换为响应模型（驼峰命名）
        response_model = SingleDeviceConnectivityResponseModel.from_service_result(service_result)
        
        status = "在线" if service_result.get("online", False) else "离线"
        logger.info(f'IP {business_ip} 连通性检测完成: {status}')
        return ResponseUtil.success(
            model_content=response_model,
            msg=f'IP连通性检测完成: {status}'
        )
        
    except Exception as e:
        logger.error(f'IP连通性检测失败: {str(e)}')
        return ResponseUtil.failure(msg=f'IP检测失败: {str(e)}') 