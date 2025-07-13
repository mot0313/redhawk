"""
设备管理Controller层
"""
from datetime import datetime
from fastapi import APIRouter, Depends, Request, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, Optional, Literal
from pydantic_validation_decorator import ValidateFields
from config.get_db import get_db
from config.enums import BusinessType
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_redfish.entity.vo.device_vo import (
    DevicePageQueryModel, AddDeviceModel, EditDeviceModel, DeleteDeviceModel,
    DeviceDetailModel, DeviceTestConnectionModel, DevicePageResponseModel,
    DeviceStatsResponseModel
)
from module_redfish.service.device_service import DeviceService
from utils.response_util import ResponseUtil
from utils.page_util import PageResponseModel
from utils.log_util import logger
from utils.common_util import bytes2file_response


deviceController = APIRouter(prefix='/redfish/device', dependencies=[Depends(LoginService.get_current_user)])


@deviceController.get(
    '/list', 
    response_model=DevicePageResponseModel, 
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:device:list'))]
)
async def get_device_list(
    request: Request,
    device_page_query: DevicePageQueryModel = Depends(DevicePageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db)
):
    """获取设备列表"""
    try:
        device_page_query_result = await DeviceService.get_device_list_services(
            query_db, device_page_query, is_page=True
        )
        logger.info('获取设备列表成功')
        return ResponseUtil.success(model_content=device_page_query_result)
    except Exception as e:
        logger.error(f'获取设备列表失败: {str(e)}')
        return ResponseUtil.failure(msg='获取设备列表失败')


@deviceController.get('/statistics', response_model=DeviceStatsResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('redfish:device:list'))])
async def get_device_statistics(
    request: Request,
    query_db: AsyncSession = Depends(get_db)
):
    """获取设备统计信息"""
    try:
        statistics = await DeviceService.get_device_statistics_services(query_db)
        logger.info('获取设备统计信息成功')
        return ResponseUtil.success(model_content=statistics)
    except Exception as e:
        logger.error(f'获取设备统计信息失败: {str(e)}')
        return ResponseUtil.failure(msg='获取设备统计信息失败')


@deviceController.get(
    '/{device_id}',
    response_model=DeviceDetailModel,
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:device:query'))]
)
async def get_device_detail(
    request: Request,
    device_id: int,
    for_edit: bool = Query(default=False, alias='forEdit'),
    query_db: AsyncSession = Depends(get_db)
):
    """获取设备详情"""
    try:
        device_detail = await DeviceService.get_device_detail_services(query_db, device_id, for_edit=for_edit)
        logger.info(f'获取设备详情成功: {device_id}')
        return ResponseUtil.success(data=device_detail)
    except ValueError as e:
        logger.warning(f'获取设备详情失败: {str(e)}')
        return ResponseUtil.failure(msg=str(e))
    except Exception as e:
        logger.error(f'获取设备详情失败: {str(e)}')
        return ResponseUtil.failure(msg='获取设备详情失败')


@deviceController.post('', dependencies=[Depends(CheckUserInterfaceAuth('redfish:device:add'))])
@ValidateFields(validate_model='add_device')
@Log(title='设备管理', business_type=BusinessType.INSERT)
async def add_device(
    request: Request,
    add_device: AddDeviceModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """添加设备"""
    try:
        add_device.create_by = current_user.user.user_name
        add_device.create_time = datetime.now()
        
        add_device_result = await DeviceService.add_device_services(query_db, add_device)
        logger.info(f'添加设备: {add_device.hostname}')
        return add_device_result
    except Exception as e:
        logger.error(f'添加设备失败: {str(e)}')
        return ResponseUtil.failure(msg='添加设备失败')


@deviceController.put('', dependencies=[Depends(CheckUserInterfaceAuth('redfish:device:edit'))])
@ValidateFields(validate_model='edit_device')
@Log(title='设备管理', business_type=BusinessType.UPDATE)
async def edit_device(
    request: Request,
    edit_device: EditDeviceModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """编辑设备"""
    try:
        edit_device.update_by = current_user.user.user_name
        edit_device.update_time = datetime.now()
        
        edit_device_result = await DeviceService.edit_device_services(query_db, edit_device)
        logger.info(f'编辑设备: {edit_device.hostname}')
        return edit_device_result
    except Exception as e:
        logger.error(f'编辑设备失败: {str(e)}')
        return ResponseUtil.failure(msg='编辑设备失败')


@deviceController.delete('/{device_ids}', dependencies=[Depends(CheckUserInterfaceAuth('redfish:device:remove'))])
@Log(title='设备管理', business_type=BusinessType.DELETE)
async def delete_device(
    request: Request,
    device_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """删除设备"""
    try:
        if not device_ids:
            return ResponseUtil.failure(msg='请选择要删除的设备')
        
        delete_device = DeleteDeviceModel(
            device_ids=device_ids,
            update_by=current_user.user.user_name,
            update_time=datetime.now()
        )
        
        delete_device_result = await DeviceService.delete_device_services(query_db, delete_device)
        logger.info(f'删除设备: {device_ids}')
        return delete_device_result
    except Exception as e:
        logger.error(f'删除设备失败: {str(e)}')
        return ResponseUtil.failure(msg='删除设备失败')



@deviceController.post('/testConnectionById', dependencies=[Depends(CheckUserInterfaceAuth('redfish:device:test'))])
async def test_device_connection_by_id(
    request: Request,
    query_db: AsyncSession = Depends(get_db)
):
    """通过设备ID测试设备连接"""
    try:
        # 从请求体中获取设备ID
        request_data = await request.json()
        device_id = request_data.get('deviceId')
        
        if not device_id:
            return ResponseUtil.failure(msg='缺少设备ID参数')
        
        connection_result = await DeviceService.test_device_connection_by_id_services(query_db, device_id)
        logger.info(f'测试设备连接 (设备ID: {device_id})')
        
        if connection_result.success:
            return ResponseUtil.success(data=connection_result, msg='连接测试成功')
        else:
            return ResponseUtil.failure(data=connection_result, msg=connection_result.message)
    except Exception as e:
        logger.error(f'测试设备连接失败: {str(e)}')
        return ResponseUtil.failure(msg='测试设备连接失败')


@deviceController.get('/monitoring/list', dependencies=[Depends(CheckUserInterfaceAuth('redfish:device:list'))])
async def get_monitoring_devices(
    request: Request,
    query_db: AsyncSession = Depends(get_db)
):
    """获取启用监控的设备列表"""
    try:
        monitoring_devices = await DeviceService.get_monitoring_devices_services(query_db)
        logger.info('获取监控设备列表成功')
        return ResponseUtil.success(data=monitoring_devices)
    except Exception as e:
        logger.error(f'获取监控设备列表失败: {str(e)}')
        return ResponseUtil.failure(msg='获取监控设备列表失败')



@deviceController.put('/changeMonitoring', dependencies=[Depends(CheckUserInterfaceAuth('redfish:device:edit'))])
@Log(title='设备管理', business_type=BusinessType.UPDATE)
async def change_device_monitoring(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """修改设备监控状态"""
    try:
        # 从请求体中获取参数
        request_data = await request.json()
        device_id = request_data.get('deviceId')
        monitor_enabled = request_data.get('monitorEnabled')
        
        if device_id is None or monitor_enabled is None:
            return ResponseUtil.failure(msg='缺少必要参数')
        
        # 创建部分更新模型
        update_data = {
            "device_id": device_id,
            "monitor_enabled": 1 if monitor_enabled else 0,
            "update_by": current_user.user.user_name,
            "update_time": datetime.now()
        }
        edit_device = EditDeviceModel(**update_data)
        
        edit_device_result = await DeviceService.edit_device_services(query_db, edit_device)
        logger.info(f'修改设备监控状态: {device_id} -> {monitor_enabled}')
        return edit_device_result
    except Exception as e:
        logger.error(f'修改设备监控状态失败: {str(e)}')
        return ResponseUtil.failure(msg='修改设备监控状态失败')


@deviceController.post('/importData', dependencies=[Depends(CheckUserInterfaceAuth('redfish:device:import'))])
@Log(title='设备管理', business_type=BusinessType.IMPORT)
async def batch_import_device(
    request: Request,
    file: UploadFile = File(...),
    update_support: bool = Query(alias='updateSupport'),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """批量导入设备"""
    try:
        batch_import_result = await DeviceService.batch_import_device_services(
            request, query_db, file, update_support, current_user
        )
        logger.info(batch_import_result.message)
        return ResponseUtil.success(msg=batch_import_result.message)
    except Exception as e:
        logger.error(f'批量导入设备失败: {str(e)}')
        return ResponseUtil.failure(msg='批量导入设备失败')


@deviceController.post('/export', dependencies=[Depends(CheckUserInterfaceAuth('redfish:device:export'))])
@Log(title='设备管理', business_type=BusinessType.EXPORT)
async def export_device_list(
    request: Request,
    device_page_query: DevicePageQueryModel = Depends(DevicePageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db)
):
    """导出设备列表"""
    try:
        device_query_result = await DeviceService.get_device_list_services(
            query_db, device_page_query, is_page=False
        )
        device_export_result = await DeviceService.export_device_list_services(device_query_result)
        logger.info('导出设备列表成功')
        return ResponseUtil.streaming(data=bytes2file_response(device_export_result))
    except Exception as e:
        logger.error(f'导出设备列表失败: {str(e)}')
        return ResponseUtil.failure(msg='导出设备列表失败')


@deviceController.post('/importTemplate', dependencies=[Depends(CheckUserInterfaceAuth('redfish:device:import'))])
async def export_device_import_template(request: Request):
    """下载设备导入模板"""
    try:
        device_import_template_result = await DeviceService.get_device_import_template_services()
        logger.info('获取设备导入模板成功')
        return ResponseUtil.streaming(data=bytes2file_response(device_import_template_result))
    except Exception as e:
        logger.error(f'获取设备导入模板失败: {str(e)}')
        return ResponseUtil.failure(msg='获取设备导入模板失败') 