"""
业务硬件紧急度规则Controller控制层
"""
from datetime import datetime
from typing import Union, Optional, List
from fastapi import APIRouter, Depends, Request, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from pydantic_validation_decorator import ValidateFields
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.service.login_service import LoginService
from module_admin.entity.vo.user_vo import CurrentUserModel

from module_redfish.service.business_rule_service import BusinessRuleService
from module_redfish.service.alert_urgency_service import AlertUrgencyService
from module_redfish.entity.vo.business_rule_vo import (
    BusinessRulePageQueryModel, AddBusinessRuleModel, EditBusinessRuleModel, DeleteBusinessRuleModel,
    BusinessRuleDetailModel, BusinessRuleStatisticsModel, UrgencyRuleMatchModel, UrgencyRuleResultModel,
    BusinessTypeQueryModel, HardwareTypeQueryModel, UrgencyRuleQueryModel,
    AddBusinessTypeModel, EditBusinessTypeModel,
    AddHardwareTypeModel, EditHardwareTypeModel,
    AddUrgencyRuleModel, EditUrgencyRuleModel
)
from utils.response_util import ResponseUtil
from utils.page_util import PageResponseModel
from utils.log_util import logger
from utils.common_util import CamelCaseUtil
from config.get_db import get_db
from config.enums import BusinessType

businessRuleController = APIRouter(prefix='/redfish/businessRule', dependencies=[Depends(LoginService.get_current_user)])


@businessRuleController.get(
    '/list', 
    response_model=PageResponseModel, 
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:businessRule:list'))]
)
async def get_rule_list(
    request: Request,
    rule_page_query: BusinessRulePageQueryModel = Depends(BusinessRulePageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db)
):
    """获取规则列表"""
    try:
        rule_list_result = await BusinessRuleService.get_rule_list_services(
            query_db, rule_page_query, is_page=True
        )
        logger.info('获取规则列表成功')
        return ResponseUtil.success(data=rule_list_result)
    except Exception as e:
        logger.error(f'获取规则列表失败: {str(e)}')
        return ResponseUtil.failure(msg='获取规则列表失败')


@businessRuleController.get('/statistics', dependencies=[Depends(CheckUserInterfaceAuth('redfish:businessRule:list'))])
async def get_rule_statistics(
    request: Request,
    query_db: AsyncSession = Depends(get_db)
):
    """获取规则统计信息"""
    try:
        statistics = await BusinessRuleService.get_rule_statistics_services(query_db)
        logger.info('获取规则统计信息成功')
        return ResponseUtil.success(data=statistics)
    except Exception as e:
        logger.error(f'获取规则统计信息失败: {str(e)}')
        return ResponseUtil.failure(msg='获取规则统计信息失败')


@businessRuleController.post('', dependencies=[Depends(CheckUserInterfaceAuth('redfish:businessRule:add'))])
@ValidateFields(validate_model='add_business_rule')
@Log(title='规则管理', business_type=BusinessType.INSERT)
async def add_rule(
    request: Request,
    add_rule: AddBusinessRuleModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """添加规则"""
    try:
        add_rule.create_by = current_user.user.user_name
        add_rule.create_time = datetime.now()
        
        add_rule_result = await BusinessRuleService.add_rule_services(query_db, add_rule)
        logger.info(f'添加规则: {add_rule.business_type} - {add_rule.hardware_type}')
        return add_rule_result
    except Exception as e:
        logger.error(f'添加规则失败: {str(e)}')
        return ResponseUtil.failure(msg='添加规则失败')


@businessRuleController.put('', dependencies=[Depends(CheckUserInterfaceAuth('redfish:businessRule:edit'))])
@ValidateFields(validate_model='edit_business_rule')
@Log(title='规则管理', business_type=BusinessType.UPDATE)
async def edit_rule(
    request: Request,
    edit_rule: EditBusinessRuleModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """编辑规则"""
    try:
        edit_rule.update_by = current_user.user.user_name
        edit_rule.update_time = datetime.now()
        
        edit_rule_result = await BusinessRuleService.edit_rule_services(query_db, edit_rule)
        logger.info(f'编辑规则: {edit_rule.rule_id}')
        return edit_rule_result
    except Exception as e:
        logger.error(f'编辑规则失败: {str(e)}')
        return ResponseUtil.failure(msg='编辑规则失败')


@businessRuleController.delete('/{rule_ids}', dependencies=[Depends(CheckUserInterfaceAuth('redfish:businessRule:remove'))])
@Log(title='规则管理', business_type=BusinessType.DELETE)
async def delete_rule(
    request: Request,
    rule_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """删除规则"""
    try:
        if not rule_ids:
            return ResponseUtil.failure(msg='请选择要删除的规则')
        
        delete_rule = DeleteBusinessRuleModel(
            rule_ids=rule_ids,
            update_by=current_user.user.user_name,
            update_time=datetime.now()
        )
        
        delete_rule_result = await BusinessRuleService.delete_rule_services(query_db, delete_rule)
        logger.info(f'删除规则: {rule_ids}')
        return delete_rule_result
    except Exception as e:
        logger.error(f'删除规则失败: {str(e)}')
        return ResponseUtil.failure(msg='删除规则失败')


@businessRuleController.post('/match', dependencies=[Depends(CheckUserInterfaceAuth('redfish:businessRule:query'))])
async def match_urgency_rule(
    request: Request,
    match_request: UrgencyRuleMatchModel,
    query_db: AsyncSession = Depends(get_db)
):
    """匹配紧急度规则"""
    try:
        match_result = await BusinessRuleService.match_urgency_rule_services(query_db, match_request)
        logger.info(f'匹配紧急度规则: {match_request.business_type} - {match_request.hardware_type}')
        return ResponseUtil.success(data=match_result)
    except Exception as e:
        logger.error(f'匹配紧急度规则失败: {str(e)}')
        return ResponseUtil.failure(msg='匹配紧急度规则失败')


@businessRuleController.put('/changeStatus', dependencies=[Depends(CheckUserInterfaceAuth('redfish:businessRule:edit'))])
@Log(title='规则管理', business_type=BusinessType.UPDATE)
async def change_rule_status(
    request: Request,
    rule_id: int,
    is_active: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """修改规则状态"""
    try:
        # 创建部分更新模型
        update_data = {
            "rule_id": rule_id,
            "is_active": is_active,
            "update_by": current_user.user.user_name,
            "update_time": datetime.now()
        }
        edit_rule = EditBusinessRuleModel(**update_data)
        
        edit_rule_result = await BusinessRuleService.edit_rule_services(query_db, edit_rule)
        logger.info(f'修改规则状态: {rule_id} -> {is_active}')
        return edit_rule_result
    except Exception as e:
        logger.error(f'修改规则状态失败: {str(e)}')
        return ResponseUtil.failure(msg='修改规则状态失败')


@businessRuleController.put('/batchStatus', dependencies=[Depends(CheckUserInterfaceAuth('redfish:businessRule:edit'))])
@Log(title='规则管理', business_type=BusinessType.UPDATE)
async def batch_update_rule_status(
    request: Request,
    rule_ids: str,
    is_active: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """批量更新规则状态"""
    try:
        rule_id_list = [int(id_str) for id_str in rule_ids.split(',') if id_str]
        
        if not rule_id_list:
            return ResponseUtil.failure(msg='请选择要更新的规则')
        
        batch_result = await BusinessRuleService.batch_update_status_services(
            query_db, rule_id_list, is_active
        )
        logger.info(f'批量更新规则状态: {rule_ids} -> {is_active}')
        return batch_result
    except Exception as e:
        logger.error(f'批量更新规则状态失败: {str(e)}')
        return ResponseUtil.failure(msg='批量更新规则状态失败')


@businessRuleController.get('/types/business', dependencies=[Depends(CheckUserInterfaceAuth('redfish:businessRule:list'))])
async def get_business_types(
    request: Request,
    query_db: AsyncSession = Depends(get_db)
):
    """获取所有业务类型"""
    try:
        business_types = await BusinessRuleService.get_business_types_services(query_db)
        logger.info('获取业务类型列表成功')
        return ResponseUtil.success(data=business_types)
    except Exception as e:
        logger.error(f'获取业务类型列表失败: {str(e)}')
        return ResponseUtil.failure(msg='获取业务类型列表失败')


@businessRuleController.get('/types/hardware', dependencies=[Depends(CheckUserInterfaceAuth('redfish:businessRule:list'))])
async def get_hardware_types(
    request: Request,
    query_db: AsyncSession = Depends(get_db)
):
    """获取所有硬件类型"""
    try:
        hardware_types = await BusinessRuleService.get_hardware_types_services(query_db)
        logger.info('获取硬件类型列表成功')
        return ResponseUtil.success(data=hardware_types)
    except Exception as e:
        logger.error(f'获取硬件类型列表失败: {str(e)}')
        return ResponseUtil.failure(msg='获取硬件类型列表失败')


@businessRuleController.get('/types/hardware/categories', dependencies=[Depends(CheckUserInterfaceAuth('redfish:businessRule:list'))])
async def get_hardware_types_by_category(
    request: Request,
    query_db: AsyncSession = Depends(get_db)
):
    """按分类获取硬件类型"""
    try:
        categorized_types = await BusinessRuleService.get_hardware_types_by_category_services(query_db)
        logger.info('获取分类硬件类型成功')
        return ResponseUtil.success(data=categorized_types)
    except Exception as e:
        logger.error(f'获取分类硬件类型失败: {str(e)}')
        return ResponseUtil.failure(msg='获取分类硬件类型失败')


@businessRuleController.get('/urgency/device/{device_id}/component/{component_type}', dependencies=[Depends(CheckUserInterfaceAuth('redfish:businessRule:query'))])
async def get_urgency_by_device_component(
    request: Request,
    device_id: int,
    component_type: str,
    query_db: AsyncSession = Depends(get_db)
):
    """根据设备ID和组件类型获取紧急度"""
    try:
        urgency_info = await AlertUrgencyService.get_alert_urgency_by_device_and_component(
            query_db, device_id, component_type
        )
        logger.info(f'查询设备组件紧急度成功: 设备{device_id} 组件{component_type}')
        return ResponseUtil.success(data=urgency_info)
    except Exception as e:
        logger.error(f'查询设备组件紧急度失败: {str(e)}')
        return ResponseUtil.failure(msg='查询设备组件紧急度失败')


@businessRuleController.get('/urgency/alert/{alert_id}', dependencies=[Depends(CheckUserInterfaceAuth('redfish:businessRule:query'))])
async def get_urgency_by_alert(
    request: Request,
    alert_id: int,
    query_db: AsyncSession = Depends(get_db)
):
    """根据告警ID获取紧急度"""
    try:
        urgency_info = await AlertUrgencyService.get_alert_urgency_by_alert_id(query_db, alert_id)
        logger.info(f'查询告警紧急度成功: 告警{alert_id}')
        return ResponseUtil.success(data=urgency_info)
    except Exception as e:
        logger.error(f'查询告警紧急度失败: {str(e)}')
        return ResponseUtil.failure(msg='查询告警紧急度失败')


@businessRuleController.get('/urgency/statistics/device/{device_id}', dependencies=[Depends(CheckUserInterfaceAuth('redfish:businessRule:query'))])
async def get_urgency_statistics_by_device(
    request: Request,
    device_id: int,
    query_db: AsyncSession = Depends(get_db)
):
    """获取设备紧急度统计"""
    try:
        statistics = await AlertUrgencyService.get_urgency_statistics_by_device(query_db, device_id)
        logger.info(f'获取设备紧急度统计成功: 设备{device_id}')
        return ResponseUtil.success(data=statistics)
    except Exception as e:
        logger.error(f'获取设备紧急度统计失败: {str(e)}')
        return ResponseUtil.failure(msg='获取设备紧急度统计失败')


@businessRuleController.post('/urgency/batch/update', dependencies=[Depends(CheckUserInterfaceAuth('redfish:businessRule:edit'))])
@Log(title='规则管理', business_type=BusinessType.UPDATE)
async def batch_update_alert_urgency(
    request: Request,
    alert_ids: Optional[List[int]] = None,
    device_ids: Optional[List[int]] = None,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """批量更新告警紧急度"""
    try:
        result = await AlertUrgencyService.batch_update_alert_urgency(
            query_db, alert_ids, device_ids
        )
        logger.info(f'批量更新告警紧急度: 告警{alert_ids} 设备{device_ids}')
        return ResponseUtil.success(data=result, msg='批量更新告警紧急度成功')
    except Exception as e:
        logger.error(f'批量更新告警紧急度失败: {str(e)}')
        return ResponseUtil.failure(msg='批量更新告警紧急度失败') 


# ==================== 业务类型管理 ====================

@businessRuleController.get("/business-types", summary="获取业务类型列表")
async def get_business_type_list(
    pageNum: int = Query(1, alias="pageNum", description="页码"),
    pageSize: int = Query(10, alias="pageSize", description="每页大小"),
    typeCode: str = Query(None, alias="typeCode", description="类型编码"),
    typeName: str = Query(None, alias="typeName", description="类型名称"),
    isActive: int = Query(None, alias="isActive", description="是否启用"),
    db: AsyncSession = Depends(get_db)
):
    """获取业务类型分页列表"""
    query_object = BusinessTypeQueryModel.as_query(
        page_num=pageNum,
        page_size=pageSize,
        type_code=typeCode,
        type_name=typeName,
        is_active=isActive
    )
    return await BusinessRuleService.get_business_type_list_services(db, query_object, is_page=True)


@businessRuleController.get("/business-types/all", summary="获取所有业务类型")
async def get_all_business_types(db: AsyncSession = Depends(get_db)):
    """获取所有业务类型（不分页，用于下拉框）"""
    query_object = BusinessTypeQueryModel()
    result = await BusinessRuleService.get_business_type_list_services(db, query_object, is_page=False)
    return ResponseUtil.success(data=result)


@businessRuleController.get("/business-types/options", summary="获取业务类型选项")
async def get_business_type_options(db: AsyncSession = Depends(get_db)):
    """获取业务类型选项（用于下拉框）"""
    return await BusinessRuleService.get_business_type_options_services(db)


@businessRuleController.get("/business-types/{type_id}", summary="获取业务类型详情")
async def get_business_type_detail(
    type_id: int = Path(..., description="业务类型ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取业务类型详情"""
    result = await BusinessRuleService.get_business_type_detail_services(db, type_id)
    return result


@businessRuleController.post("/business-types", summary="新增业务类型")
async def add_business_type(
    business_type: AddBusinessTypeModel,
    db: AsyncSession = Depends(get_db)
):
    """新增业务类型"""
    return await BusinessRuleService.add_business_type_services(db, business_type)


@businessRuleController.put("/business-types", summary="编辑业务类型")
async def edit_business_type(
    business_type: EditBusinessTypeModel,
    db: AsyncSession = Depends(get_db)
):
    """编辑业务类型"""
    return await BusinessRuleService.edit_business_type_services(db, business_type)


@businessRuleController.delete("/business-types/{type_ids}", summary="删除业务类型")
async def delete_business_type(
    type_ids: str = Path(..., description="业务类型ID列表，逗号分隔"),
    db: AsyncSession = Depends(get_db)
):
    """删除业务类型"""
    id_list = [int(id.strip()) for id in type_ids.split(',') if id.strip()]
    return await BusinessRuleService.delete_business_type_services(db, id_list)


# ==================== 硬件类型管理 ====================

@businessRuleController.get("/hardware-types", summary="获取硬件类型列表")
async def get_hardware_type_list(
    pageNum: int = Query(1, alias="pageNum", description="页码"),
    pageSize: int = Query(10, alias="pageSize", description="每页大小"),
    typeCode: str = Query(None, alias="typeCode", description="类型编码"),
    typeName: str = Query(None, alias="typeName", description="类型名称"),
    category: str = Query(None, alias="category", description="硬件分类"),
    isActive: int = Query(None, alias="isActive", description="是否启用"),
    db: AsyncSession = Depends(get_db)
):
    """获取硬件类型分页列表"""
    query_object = HardwareTypeQueryModel.as_query(
        page_num=pageNum,
        page_size=pageSize,
        type_code=typeCode,
        type_name=typeName,
        category=category,
        is_active=isActive
    )
    return await BusinessRuleService.get_hardware_type_list_services(db, query_object, is_page=True)


@businessRuleController.get("/hardware-types/all", summary="获取所有硬件类型")
async def get_all_hardware_types(db: AsyncSession = Depends(get_db)):
    """获取所有硬件类型（不分页，用于下拉框）"""
    query_object = HardwareTypeQueryModel()
    result = await BusinessRuleService.get_hardware_type_list_services(db, query_object, is_page=False)
    return ResponseUtil.success(data=result)


@businessRuleController.get("/hardware-types/options", summary="获取硬件类型选项")
async def get_hardware_type_options(db: AsyncSession = Depends(get_db)):
    """获取硬件类型选项（用于下拉框）"""
    return await BusinessRuleService.get_hardware_type_options_services(db)


@businessRuleController.get("/hardware-types/categories", summary="获取硬件分类选项")
async def get_hardware_categories(db: AsyncSession = Depends(get_db)):
    """获取硬件分类选项"""
    return await BusinessRuleService.get_hardware_categories_services(db)


@businessRuleController.get("/hardware-types/{type_id}", summary="获取硬件类型详情")
async def get_hardware_type_detail(
    type_id: int = Path(..., description="硬件类型ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取硬件类型详情"""
    result = await BusinessRuleService.get_hardware_type_detail_services(db, type_id)
    return result


@businessRuleController.post("/hardware-types", summary="新增硬件类型")
async def add_hardware_type(
    hardware_type: AddHardwareTypeModel,
    db: AsyncSession = Depends(get_db)
):
    """新增硬件类型"""
    return await BusinessRuleService.add_hardware_type_services(db, hardware_type)


@businessRuleController.put("/hardware-types", summary="编辑硬件类型")
async def edit_hardware_type(
    hardware_type: EditHardwareTypeModel,
    db: AsyncSession = Depends(get_db)
):
    """编辑硬件类型"""
    return await BusinessRuleService.edit_hardware_type_services(db, hardware_type)


@businessRuleController.delete("/hardware-types/{type_ids}", summary="删除硬件类型")
async def delete_hardware_type(
    type_ids: str = Path(..., description="硬件类型ID列表，逗号分隔"),
    db: AsyncSession = Depends(get_db)
):
    """删除硬件类型"""
    id_list = [int(id.strip()) for id in type_ids.split(',') if id.strip()]
    return await BusinessRuleService.delete_hardware_type_services(db, id_list)


# ==================== 紧急度规则管理 ====================

@businessRuleController.get("/urgency-rules", summary="获取紧急度规则列表")
async def get_urgency_rule_list(
    pageNum: int = Query(1, alias="pageNum", description="页码"),
    pageSize: int = Query(10, alias="pageSize", description="每页大小"),
    businessType: str = Query(None, alias="businessType", description="业务类型"),
    hardwareType: str = Query(None, alias="hardwareType", description="硬件类型"),
    urgencyLevel: str = Query(None, alias="urgencyLevel", description="紧急程度"),
    isActive: int = Query(None, alias="isActive", description="是否启用"),
    db: AsyncSession = Depends(get_db)
):
    """获取紧急度规则分页列表"""
    query_object = UrgencyRuleQueryModel.as_query(
        page_num=pageNum,
        page_size=pageSize,
        business_type=businessType,
        hardware_type=hardwareType,
        urgency_level=urgencyLevel,
        is_active=isActive
    )
    return await BusinessRuleService.get_urgency_rule_list_services(db, query_object, is_page=True)


@businessRuleController.get("/urgency-rules/all", summary="获取所有紧急度规则")
async def get_all_urgency_rules(db: AsyncSession = Depends(get_db)):
    """获取所有紧急度规则（不分页）"""
    query_object = UrgencyRuleQueryModel()
    result = await BusinessRuleService.get_urgency_rule_list_services(db, query_object, is_page=False)
    return ResponseUtil.success(data=result)


@businessRuleController.get("/urgency-rules/{rule_id}", summary="获取紧急度规则详情")
async def get_urgency_rule_detail(
    rule_id: int = Path(..., description="规则ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取紧急度规则详情"""
    result = await BusinessRuleService.get_urgency_rule_detail_services(db, rule_id)
    return result


@businessRuleController.post("/urgency-rules", summary="新增紧急度规则")
async def add_urgency_rule(
    rule: AddUrgencyRuleModel,
    db: AsyncSession = Depends(get_db)
):
    """新增紧急度规则"""
    return await BusinessRuleService.add_urgency_rule_services(db, rule)


@businessRuleController.put("/urgency-rules", summary="编辑紧急度规则")
async def edit_urgency_rule(
    rule: EditUrgencyRuleModel,
    db: AsyncSession = Depends(get_db)
):
    """编辑紧急度规则"""
    return await BusinessRuleService.edit_urgency_rule_services(db, rule)


@businessRuleController.delete("/urgency-rules/{rule_ids}", summary="删除紧急度规则")
async def delete_urgency_rule(
    rule_ids: str = Path(..., description="规则ID列表，逗号分隔"),
    db: AsyncSession = Depends(get_db)
):
    """删除紧急度规则"""
    id_list = [int(id.strip()) for id in rule_ids.split(',') if id.strip()]
    return await BusinessRuleService.delete_urgency_rule_services(db, id_list)


# ==================== 通用路由（必须放在最后） ====================

@businessRuleController.get(
    '/{rule_id}',
    response_model=BusinessRuleDetailModel,
    dependencies=[Depends(CheckUserInterfaceAuth('redfish:businessRule:query'))]
)
async def get_rule_detail(
    request: Request,
    rule_id: int,
    query_db: AsyncSession = Depends(get_db)
):
    """获取规则详情"""
    try:
        rule_detail = await BusinessRuleService.get_rule_detail_services(query_db, rule_id)
        logger.info(f'获取规则详情成功: {rule_id}')
        return ResponseUtil.success(data=rule_detail)
    except ValueError as e:
        logger.warning(f'获取规则详情失败: {str(e)}')
        return ResponseUtil.failure(msg=str(e))
    except Exception as e:
        logger.error(f'获取规则详情失败: {str(e)}')
        return ResponseUtil.failure(msg='获取规则详情失败') 