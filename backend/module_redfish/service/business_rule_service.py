"""
业务硬件紧急度规则Service业务逻辑层
"""
import math
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from module_redfish.dao.business_rule_dao import BusinessRuleDao
from module_redfish.entity.vo.business_rule_vo import (
    BusinessRulePageQueryModel, AddBusinessRuleModel, EditBusinessRuleModel, DeleteBusinessRuleModel,
    BusinessRuleDetailModel, BusinessRuleModel, BusinessRuleStatisticsModel,
    UrgencyRuleMatchModel, UrgencyRuleResultModel,
    BusinessTypeQueryModel, HardwareTypeQueryModel, UrgencyRuleQueryModel,
    AddBusinessTypeModel, EditBusinessTypeModel,
    AddHardwareTypeModel, EditHardwareTypeModel,
    AddUrgencyRuleModel, EditUrgencyRuleModel
)
from utils.response_util import ResponseUtil
from utils.page_util import PageResponseModel
from utils.log_util import logger
from module_redfish.celery_tasks import recalculate_urgency_for_rule_change


class BusinessRuleService:
    """业务硬件紧急度规则服务"""
    
    @classmethod
    async def get_rule_list_services(
        cls,
        db: AsyncSession,
        query_object: BusinessRulePageQueryModel,
        is_page: bool = False
    ) -> PageResponseModel:
        """
        获取规则列表
        
        Args:
            db: 数据库会话
            query_object: 查询对象
            is_page: 是否分页
            
        Returns:
            PageResponseModel: 分页响应
        """
        rule_list, total = await BusinessRuleDao.get_rule_list(db, query_object, is_page)
        
        if is_page:
            # 创建分页响应
            has_next = math.ceil(total / query_object.page_size) > query_object.page_num if total > 0 else False
            from utils.common_util import CamelCaseUtil
            return PageResponseModel(
                rows=CamelCaseUtil.transform_result(rule_list),
                pageNum=query_object.page_num,
                pageSize=query_object.page_size,
                total=total,
                hasNext=has_next
            )
        else:
            from utils.common_util import CamelCaseUtil
            return CamelCaseUtil.transform_result(rule_list)
    
    @classmethod
    async def get_rule_detail_services(cls, db: AsyncSession, rule_id: int) -> BusinessRuleDetailModel:
        """
        获取规则详情
        
        Args:
            db: 数据库会话
            rule_id: 规则ID
            
        Returns:
            BusinessRuleDetailModel: 规则详情
        """
        rule = await BusinessRuleDao.get_rule_by_id(db, rule_id)
        if not rule:
            raise ValueError("规则不存在")
        
        # 将数据库对象转换为VO模型
        rule_model = BusinessRuleModel(
            rule_id=rule.rule_id,
            business_type=rule.business_type,
            hardware_type=rule.hardware_type,
            urgency_level=rule.urgency_level,
            description=rule.description,
            is_active=rule.is_active,
            create_by=rule.create_by,
            create_time=rule.create_time,
            update_by=rule.update_by,
            update_time=rule.update_time
        )
        
        # TODO: 获取关联设备数量和告警数量
        related_devices_count = 0
        related_alerts_count = 0
        
        return BusinessRuleDetailModel(
            rule=rule_model,
            related_devices_count=related_devices_count,
            related_alerts_count=related_alerts_count
        )
    
    @classmethod
    async def add_rule_services(cls, db: AsyncSession, rule: AddBusinessRuleModel) -> ResponseUtil:
        """
        添加规则
        
        Args:
            db: 数据库会话
            rule: 规则信息
            
        Returns:
            ResponseUtil: 响应结果
        """
        # 检查规则是否已存在
        if await BusinessRuleDao.check_rule_exists(db, rule.business_type, rule.hardware_type):
            return ResponseUtil.failure(msg="该业务类型和硬件类型的规则已存在")
        
        try:
            new_rule = await BusinessRuleDao.add_rule(db, rule)
            logger.info(f"成功添加规则: {rule.business_type} - {rule.hardware_type}")
            return ResponseUtil.success(msg="添加规则成功")
        except Exception as e:
            logger.error(f"添加规则失败: {str(e)}")
            return ResponseUtil.failure(msg="添加规则失败")
    
    @classmethod
    async def edit_rule_services(cls, db: AsyncSession, rule: EditBusinessRuleModel) -> ResponseUtil:
        """
        编辑规则
        
        Args:
            db: 数据库会话
            rule: 规则信息
            
        Returns:
            ResponseUtil: 响应结果
        """
        # 检查规则是否存在
        existing_rule = await BusinessRuleDao.get_rule_by_id(db, rule.rule_id)
        if not existing_rule:
            return ResponseUtil.failure(msg="规则不存在")
        
        # 如果修改了业务类型或硬件类型，检查是否与其他规则冲突
        if rule.business_type or rule.hardware_type:
            business_type = rule.business_type or existing_rule.business_type
            hardware_type = rule.hardware_type or existing_rule.hardware_type
            
            if await BusinessRuleDao.check_rule_exists(db, business_type, hardware_type, rule.rule_id):
                return ResponseUtil.failure(msg="该业务类型和硬件类型的规则已存在")
        
        try:
            success = await BusinessRuleDao.edit_rule(db, rule)
            if success:
                logger.info(f"成功编辑规则: {rule.rule_id}")
                return ResponseUtil.success(msg="编辑规则成功")
            else:
                return ResponseUtil.failure(msg="编辑规则失败")
        except Exception as e:
            logger.error(f"编辑规则失败: {str(e)}")
            return ResponseUtil.failure(msg="编辑规则失败")
    
    @classmethod
    async def delete_rule_services(cls, db: AsyncSession, delete_rule: DeleteBusinessRuleModel) -> ResponseUtil:
        """
        删除规则
        
        Args:
            db: 数据库会话
            delete_rule: 删除规则信息
            
        Returns:
            ResponseUtil: 响应结果
        """
        rule_ids = [int(id_str) for id_str in delete_rule.rule_ids.split(',') if id_str]
        
        if not rule_ids:
            return ResponseUtil.failure(msg="请选择要删除的规则")
        
        try:
            success = await BusinessRuleDao.delete_rule(db, rule_ids)
            if success:
                logger.info(f"成功删除规则: {rule_ids}")
                return ResponseUtil.success(msg="删除规则成功")
            else:
                return ResponseUtil.failure(msg="删除规则失败")
        except Exception as e:
            logger.error(f"删除规则失败: {str(e)}")
            return ResponseUtil.failure(msg="删除规则失败")
    
    @classmethod
    async def get_rule_statistics_services(cls, db: AsyncSession) -> BusinessRuleStatisticsModel:
        """
        获取规则统计信息
        
        Args:
            db: 数据库会话
            
        Returns:
            BusinessRuleStatisticsModel: 统计信息
        """
        stats = await BusinessRuleDao.get_rule_statistics(db)
        
        return BusinessRuleStatisticsModel(
            total_rules=stats['total_rules'],
            active_rules=stats['active_rules'],
            urgent_rules=stats['urgent_rules'],
            scheduled_rules=stats['scheduled_rules'],
            business_types=stats['business_types'],
            hardware_types=stats['hardware_types']
        )
    
    @classmethod
    async def match_urgency_rule_services(
        cls, 
        db: AsyncSession, 
        match_request: UrgencyRuleMatchModel
    ) -> UrgencyRuleResultModel:
        """
        匹配紧急度规则
        
        Args:
            db: 数据库会话
            match_request: 匹配请求
            
        Returns:
            UrgencyRuleResultModel: 匹配结果
        """
        try:
            rule = await BusinessRuleDao.get_rule_by_type(
                db, 
                match_request.business_type, 
                match_request.hardware_type
            )
            
            if rule:
                return UrgencyRuleResultModel(
                    matched=True,
                    urgency_level=rule.urgency_level,
                    description=rule.description,
                    rule_id=rule.rule_id
                )
            else:
                # 没有匹配到规则，返回默认择期
                return UrgencyRuleResultModel(
                    matched=False,
                    urgency_level="scheduled",
                    description="未匹配到规则，默认为择期",
                    rule_id=None
                )
        except Exception as e:
            logger.error(f"匹配紧急度规则失败: {str(e)}")
            return UrgencyRuleResultModel(
                matched=False,
                urgency_level="scheduled",
                description="规则匹配异常，默认为择期",
                rule_id=None
            )
    
    @classmethod
    async def batch_update_status_services(
        cls, 
        db: AsyncSession, 
        rule_ids: List[int], 
        is_active: int
    ) -> ResponseUtil:
        """
        批量更新规则状态
        
        Args:
            db: 数据库会话
            rule_ids: 规则ID列表
            is_active: 启用状态
            
        Returns:
            ResponseUtil: 响应结果
        """
        try:
            success = await BusinessRuleDao.batch_update_status(db, rule_ids, is_active)
            if success:
                status_text = "启用" if is_active else "禁用"
                logger.info(f"成功批量{status_text}规则: {rule_ids}")
                return ResponseUtil.success(msg=f"批量{status_text}规则成功")
            else:
                return ResponseUtil.failure(msg="批量更新规则状态失败")
        except Exception as e:
            logger.error(f"批量更新规则状态失败: {str(e)}")
            return ResponseUtil.failure(msg="批量更新规则状态失败")
    
    @classmethod
    async def get_business_types_services(cls, db: AsyncSession) -> List[Dict[str, Any]]:
        """
        获取所有业务类型（从字典表）
        
        Args:
            db: 数据库会话
            
        Returns:
            List[Dict[str, Any]]: 业务类型列表
        """
        from sqlalchemy import select
        from module_redfish.entity.do.business_type_dict_do import BusinessTypeDictDO
        
        try:
            result = await db.execute(
                select(BusinessTypeDictDO)
                .where(BusinessTypeDictDO.is_active == 1)
                .order_by(BusinessTypeDictDO.sort_order, BusinessTypeDictDO.type_code)
            )
            business_types = result.scalars().all()
            
            return [
                {
                    'typeId': bt.type_id,
                    'typeCode': bt.type_code,
                    'typeName': bt.type_name,
                    'description': bt.type_description,
                    'sortOrder': bt.sort_order
                }
                for bt in business_types
            ]
        except Exception as e:
            logger.warning(f"从字典表获取业务类型失败，降级到规则表获取: {str(e)}")
            # 降级方案：从现有规则中获取
            stats = await BusinessRuleDao.get_rule_statistics(db)
            return [{'typeCode': bt, 'typeName': bt} for bt in stats['business_types']]
    
    @classmethod
    async def get_hardware_types_services(cls, db: AsyncSession) -> List[Dict[str, Any]]:
        """
        获取所有硬件类型（从字典表）
        
        Args:
            db: 数据库会话
            
        Returns:
            List[Dict[str, Any]]: 硬件类型列表
        """
        from sqlalchemy import select
        from module_redfish.entity.do.hardware_type_dict_do import HardwareTypeDictDO
        
        try:
            result = await db.execute(
                select(HardwareTypeDictDO)
                .where(HardwareTypeDictDO.is_active == 1)
                .order_by(HardwareTypeDictDO.sort_order, HardwareTypeDictDO.type_code)
            )
            hardware_types = result.scalars().all()
            
            return [
                {
                    'typeId': ht.type_id,
                    'typeCode': ht.type_code,
                    'typeName': ht.type_name,
                    'description': ht.type_description,
                    'category': ht.category,
                    'sortOrder': ht.sort_order
                }
                for ht in hardware_types
            ]
        except Exception as e:
            logger.warning(f"从字典表获取硬件类型失败，降级到规则表获取: {str(e)}")
            # 降级方案：从现有规则中获取
            stats = await BusinessRuleDao.get_rule_statistics(db)
            return [{'typeCode': ht, 'typeName': ht} for ht in stats['hardware_types']]
    
    @classmethod
    async def get_hardware_types_by_category_services(cls, db: AsyncSession) -> Dict[str, List[Dict[str, Any]]]:
        """
        按分类获取硬件类型
        
        Args:
            db: 数据库会话
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 按分类分组的硬件类型
        """
        hardware_types = await cls.get_hardware_types_services(db)
        
        # 按分类分组
        categorized = {}
        for ht in hardware_types:
            category = ht.get('category', 'other')
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(ht)
        
        return categorized 

    # ==================== 业务类型管理方法 ====================
    
    @classmethod
    async def get_business_type_list_services(
        cls,
        db: AsyncSession,
        query_object: BusinessTypeQueryModel,
        is_page: bool = False
    ):
        """获取业务类型列表"""
        try:
            from module_redfish.dao.business_rule_dao import BusinessTypeDao
            from utils.common_util import CamelCaseUtil
            business_types, total = await BusinessTypeDao.get_business_type_list(db, query_object, is_page)
            
            # 参考device service的转换方式
            business_type_dicts = [bt.__dict__.copy() for bt in business_types]
            for bt_dict in business_type_dicts:
                bt_dict.pop('_sa_instance_state', None)
            
            if is_page:
                has_next = math.ceil(total / query_object.page_size) > query_object.page_num if total > 0 else False
                return PageResponseModel(
                    rows=CamelCaseUtil.transform_result(business_type_dicts),
                    pageNum=query_object.page_num,
                    pageSize=query_object.page_size,
                    total=total,
                    hasNext=has_next
                )
            else:
                return CamelCaseUtil.transform_result(business_type_dicts)
        except Exception as e:
            logger.error(f"获取业务类型列表失败: {str(e)}")
            raise

    @classmethod
    async def get_business_type_detail_services(cls, db: AsyncSession, type_id: int) -> ResponseUtil:
        """获取业务类型详情"""
        try:
            from module_redfish.dao.business_rule_dao import BusinessTypeDao
            from utils.common_util import CamelCaseUtil
            business_type = await BusinessTypeDao.get_business_type_detail(db, type_id)
            if business_type:
                # 参考device service的转换方式
                business_type_dict = business_type.__dict__.copy()
                business_type_dict.pop('_sa_instance_state', None)
                return ResponseUtil.success(data=CamelCaseUtil.transform_result(business_type_dict))
            else:
                return ResponseUtil.failure(msg="业务类型不存在")
        except Exception as e:
            logger.error(f"获取业务类型详情失败: {str(e)}")
            return ResponseUtil.failure(msg="获取业务类型详情失败")

    @classmethod
    async def add_business_type_services(cls, db: AsyncSession, business_type: AddBusinessTypeModel) -> ResponseUtil:
        """新增业务类型"""
        try:
            from module_redfish.dao.business_rule_dao import BusinessTypeDao
            # 检查类型编码是否已存在
            if await BusinessTypeDao.check_business_type_exists(db, business_type.type_code):
                return ResponseUtil.failure(msg="业务类型编码已存在")
            
            success = await BusinessTypeDao.add_business_type(db, business_type)
            if success:
                logger.info(f"成功添加业务类型: {business_type.type_code}")
                return ResponseUtil.success(msg="添加业务类型成功")
            else:
                return ResponseUtil.failure(msg="添加业务类型失败")
        except Exception as e:
            logger.error(f"添加业务类型失败: {str(e)}")
            return ResponseUtil.failure(msg="添加业务类型失败")

    @classmethod
    async def edit_business_type_services(cls, db: AsyncSession, business_type: EditBusinessTypeModel) -> ResponseUtil:
        """编辑业务类型"""
        try:
            from module_redfish.dao.business_rule_dao import BusinessTypeDao
            # 检查业务类型是否存在
            existing = await BusinessTypeDao.get_business_type_detail(db, business_type.type_id)
            if not existing:
                return ResponseUtil.failure(msg="业务类型不存在")
            
            # 如果修改了类型编码，检查是否与其他记录冲突
            if business_type.type_code and business_type.type_code != existing.type_code:
                if await BusinessTypeDao.check_business_type_exists(db, business_type.type_code, business_type.type_id):
                    return ResponseUtil.failure(msg="业务类型编码已存在")
            
            success = await BusinessTypeDao.edit_business_type(db, business_type)
            if success:
                logger.info(f"成功编辑业务类型: {business_type.type_id}")
                return ResponseUtil.success(msg="编辑业务类型成功")
            else:
                return ResponseUtil.failure(msg="编辑业务类型失败")
        except Exception as e:
            logger.error(f"编辑业务类型失败: {str(e)}")
            return ResponseUtil.failure(msg="编辑业务类型失败")

    @classmethod
    async def delete_business_type_services(cls, db: AsyncSession, type_ids: List[int]) -> ResponseUtil:
        """删除业务类型"""
        try:
            from module_redfish.dao.business_rule_dao import BusinessTypeDao
            if not type_ids:
                return ResponseUtil.failure(msg="请选择要删除的业务类型")
            
            success = await BusinessTypeDao.delete_business_type(db, type_ids)
            if success:
                logger.info(f"成功删除业务类型: {type_ids}")
                return ResponseUtil.success(msg="删除业务类型成功")
            else:
                return ResponseUtil.failure(msg="删除业务类型失败")
        except Exception as e:
            logger.error(f"删除业务类型失败: {str(e)}")
            return ResponseUtil.failure(msg="删除业务类型失败")

    @classmethod
    async def get_business_type_options_services(cls, db: AsyncSession) -> ResponseUtil:
        """获取业务类型选项"""
        try:
            from module_redfish.dao.business_rule_dao import BusinessTypeDao
            from utils.common_util import CamelCaseUtil
            options = await BusinessTypeDao.get_business_type_options(db)
            return ResponseUtil.success(data=CamelCaseUtil.transform_result(options))
        except Exception as e:
            logger.error(f"获取业务类型选项失败: {str(e)}")
            return ResponseUtil.failure(msg="获取业务类型选项失败")

    # ==================== 硬件类型管理方法 ====================
    
    @classmethod
    async def get_hardware_type_list_services(
        cls,
        db: AsyncSession,
        query_object: HardwareTypeQueryModel,
        is_page: bool = False
    ):
        """获取硬件类型列表"""
        try:
            from module_redfish.dao.business_rule_dao import HardwareTypeDao
            from utils.common_util import CamelCaseUtil
            hardware_types, total = await HardwareTypeDao.get_hardware_type_list(db, query_object, is_page)
            
            # 参考device service的转换方式
            hardware_type_dicts = [ht.__dict__.copy() for ht in hardware_types]
            for ht_dict in hardware_type_dicts:
                ht_dict.pop('_sa_instance_state', None)
            
            if is_page:
                has_next = math.ceil(total / query_object.page_size) > query_object.page_num if total > 0 else False
                return PageResponseModel(
                    rows=CamelCaseUtil.transform_result(hardware_type_dicts),
                    pageNum=query_object.page_num,
                    pageSize=query_object.page_size,
                    total=total,
                    hasNext=has_next
                )
            else:
                return CamelCaseUtil.transform_result(hardware_type_dicts)
        except Exception as e:
            logger.error(f"获取硬件类型列表失败: {str(e)}")
            raise

    @classmethod
    async def get_hardware_type_detail_services(cls, db: AsyncSession, type_id: int) -> ResponseUtil:
        """获取硬件类型详情"""
        try:
            from module_redfish.dao.business_rule_dao import HardwareTypeDao
            from utils.common_util import CamelCaseUtil
            hardware_type = await HardwareTypeDao.get_hardware_type_detail(db, type_id)
            if hardware_type:
                # 参考device service的转换方式
                hardware_type_dict = hardware_type.__dict__.copy()
                hardware_type_dict.pop('_sa_instance_state', None)
                return ResponseUtil.success(data=CamelCaseUtil.transform_result(hardware_type_dict))
            else:
                return ResponseUtil.failure(msg="硬件类型不存在")
        except Exception as e:
            logger.error(f"获取硬件类型详情失败: {str(e)}")
            return ResponseUtil.failure(msg="获取硬件类型详情失败")

    @classmethod
    async def add_hardware_type_services(cls, db: AsyncSession, hardware_type: AddHardwareTypeModel) -> ResponseUtil:
        """新增硬件类型"""
        try:
            from module_redfish.dao.business_rule_dao import HardwareTypeDao
            # 检查类型编码是否已存在
            if await HardwareTypeDao.check_hardware_type_exists(db, hardware_type.type_code):
                return ResponseUtil.failure(msg="硬件类型编码已存在")
            
            success = await HardwareTypeDao.add_hardware_type(db, hardware_type)
            if success:
                logger.info(f"成功添加硬件类型: {hardware_type.type_code}")
                return ResponseUtil.success(msg="添加硬件类型成功")
            else:
                return ResponseUtil.failure(msg="添加硬件类型失败")
        except Exception as e:
            logger.error(f"添加硬件类型失败: {str(e)}")
            return ResponseUtil.failure(msg="添加硬件类型失败")

    @classmethod
    async def edit_hardware_type_services(cls, db: AsyncSession, hardware_type: EditHardwareTypeModel) -> ResponseUtil:
        """编辑硬件类型"""
        try:
            from module_redfish.dao.business_rule_dao import HardwareTypeDao
            # 检查硬件类型是否存在
            existing = await HardwareTypeDao.get_hardware_type_detail(db, hardware_type.type_id)
            if not existing:
                return ResponseUtil.failure(msg="硬件类型不存在")
            
            # 如果修改了类型编码，检查是否与其他记录冲突
            if hardware_type.type_code and hardware_type.type_code != existing.type_code:
                if await HardwareTypeDao.check_hardware_type_exists(db, hardware_type.type_code, hardware_type.type_id):
                    return ResponseUtil.failure(msg="硬件类型编码已存在")
            
            success = await HardwareTypeDao.edit_hardware_type(db, hardware_type)
            if success:
                logger.info(f"成功编辑硬件类型: {hardware_type.type_id}")
                return ResponseUtil.success(msg="编辑硬件类型成功")
            else:
                return ResponseUtil.failure(msg="编辑硬件类型失败")
        except Exception as e:
            logger.error(f"编辑硬件类型失败: {str(e)}")
            return ResponseUtil.failure(msg="编辑硬件类型失败")

    @classmethod
    async def delete_hardware_type_services(cls, db: AsyncSession, type_ids: List[int]) -> ResponseUtil:
        """删除硬件类型"""
        try:
            from module_redfish.dao.business_rule_dao import HardwareTypeDao
            if not type_ids:
                return ResponseUtil.failure(msg="请选择要删除的硬件类型")
            
            success = await HardwareTypeDao.delete_hardware_type(db, type_ids)
            if success:
                logger.info(f"成功删除硬件类型: {type_ids}")
                return ResponseUtil.success(msg="删除硬件类型成功")
            else:
                return ResponseUtil.failure(msg="删除硬件类型失败")
        except Exception as e:
            logger.error(f"删除硬件类型失败: {str(e)}")
            return ResponseUtil.failure(msg="删除硬件类型失败")

    @classmethod
    async def get_hardware_type_options_services(cls, db: AsyncSession) -> ResponseUtil:
        """获取硬件类型选项"""
        try:
            from module_redfish.dao.business_rule_dao import HardwareTypeDao
            from utils.common_util import CamelCaseUtil
            options = await HardwareTypeDao.get_hardware_type_options(db)
            return ResponseUtil.success(data=CamelCaseUtil.transform_result(options))
        except Exception as e:
            logger.error(f"获取硬件类型选项失败: {str(e)}")
            return ResponseUtil.failure(msg="获取硬件类型选项失败")

    @classmethod
    async def get_hardware_categories_services(cls, db: AsyncSession) -> ResponseUtil:
        """获取硬件分类选项"""
        try:
            from module_redfish.dao.business_rule_dao import HardwareTypeDao
            from utils.common_util import CamelCaseUtil
            categories = await HardwareTypeDao.get_hardware_categories(db)
            # 转换为前端期望的格式
            category_options = [
                {
                    'value': category,
                    'label': category
                }
                for category in categories
            ]
            return ResponseUtil.success(data=CamelCaseUtil.transform_result(category_options))
        except Exception as e:
            logger.error(f"获取硬件分类选项失败: {str(e)}")
            return ResponseUtil.failure(msg="获取硬件分类选项失败")

    # ==================== 紧急度规则管理方法 ====================
    
    @classmethod
    async def get_urgency_rule_list_services(
        cls,
        db: AsyncSession,
        query_object: UrgencyRuleQueryModel,
        is_page: bool = False
    ):
        """获取紧急度规则列表"""
        try:
            from module_redfish.dao.business_rule_dao import UrgencyRuleDao
            from utils.common_util import CamelCaseUtil
            rules, total = await UrgencyRuleDao.get_urgency_rule_list(db, query_object, is_page)
            
            # UrgencyRuleDao.get_urgency_rule_list 已经返回字典列表，无需转换
            if is_page:
                has_next = math.ceil(total / query_object.page_size) > query_object.page_num if total > 0 else False
                return PageResponseModel(
                    rows=CamelCaseUtil.transform_result(rules),
                    pageNum=query_object.page_num,
                    pageSize=query_object.page_size,
                    total=total,
                    hasNext=has_next
                )
            else:
                return CamelCaseUtil.transform_result(rules)
        except Exception as e:
            logger.error(f"获取紧急度规则列表失败: {str(e)}")
            raise

    @classmethod
    async def get_urgency_rule_detail_services(cls, db: AsyncSession, rule_id: int) -> ResponseUtil:
        """获取紧急度规则详情"""
        try:
            from module_redfish.dao.business_rule_dao import UrgencyRuleDao
            from utils.common_util import CamelCaseUtil
            rule = await UrgencyRuleDao.get_urgency_rule_detail(db, rule_id)
            if rule:
                # 参考device service的转换方式
                rule_dict = rule.__dict__.copy()
                rule_dict.pop('_sa_instance_state', None)
                return ResponseUtil.success(data=CamelCaseUtil.transform_result(rule_dict))
            else:
                return ResponseUtil.failure(msg="紧急度规则不存在")
        except Exception as e:
            logger.error(f"获取紧急度规则详情失败: {str(e)}")
            return ResponseUtil.failure(msg="获取紧急度规则详情失败")

    @classmethod
    async def add_urgency_rule_services(cls, db: AsyncSession, rule: AddUrgencyRuleModel) -> ResponseUtil:
        """新增紧急度规则"""
        try:
            from module_redfish.dao.business_rule_dao import UrgencyRuleDao
            # 检查规则是否已存在
            if await UrgencyRuleDao.check_urgency_rule_exists(db, rule.business_type, rule.hardware_type):
                return ResponseUtil.failure(msg="该业务类型和硬件类型的规则已存在")
            
            success = await UrgencyRuleDao.add_urgency_rule(db, rule)
            if success:
                logger.info(f"成功添加紧急度规则: {rule.business_type} - {rule.hardware_type}")

                # 触发后台任务
                recalculate_urgency_for_rule_change.delay(rule.business_type, rule.hardware_type)
                logger.info(f"为规则 {rule.business_type}-{rule.hardware_type} 触发紧急度重新计算任务")

                return ResponseUtil.success(msg="添加规则成功")
            else:
                return ResponseUtil.failure(msg="添加紧急度规则失败")
        except Exception as e:
            logger.error(f"添加紧急度规则失败: {str(e)}")
            return ResponseUtil.failure(msg="添加紧急度规则失败")

    @classmethod
    async def edit_urgency_rule_services(cls, db: AsyncSession, rule: EditUrgencyRuleModel) -> ResponseUtil:
        """编辑紧急度规则"""
        existing_rule = await BusinessRuleDao.get_urgency_rule_by_id(db, rule.rule_id)
        if not existing_rule:
            return ResponseUtil.failure(msg="规则不存在")
            
        # 检查是否与其他规则冲突
        business_type = rule.business_type or existing_rule.business_type
        hardware_type = rule.hardware_type or existing_rule.hardware_type
        if await BusinessRuleDao.check_urgency_rule_exists(db, business_type, hardware_type, rule.rule_id):
                    return ResponseUtil.failure(msg="该业务类型和硬件类型的规则已存在")
            
        # 记录旧的规则信息，用于触发任务
        old_business_type = existing_rule.business_type
        old_hardware_type = existing_rule.hardware_type

        try:
            success = await BusinessRuleDao.edit_urgency_rule(db, rule)
            if success:
                logger.info(f"成功编辑紧急度规则: {rule.rule_id}")
                
                # 触发旧规则相关告警的更新
                recalculate_urgency_for_rule_change.delay(old_business_type, old_hardware_type)
                logger.info(f"为旧规则 {old_business_type}-{old_hardware_type} 触发紧急度重新计算任务")
                # 如果业务或硬件类型被更改，还需要触发新规则相关告警的更新
                if business_type != old_business_type or hardware_type != old_hardware_type:
                    recalculate_urgency_for_rule_change.delay(business_type, hardware_type)
                    logger.info(f"为新规则 {business_type}-{hardware_type} 触发紧急度重新计算任务")

                return ResponseUtil.success(msg="编辑规则成功")
            else:
                return ResponseUtil.failure(msg="编辑规则失败")
        except Exception as e:
            logger.error(f"编辑紧急度规则失败: {str(e)}")
            return ResponseUtil.failure(msg="编辑规则失败")

    @classmethod
    async def delete_urgency_rule_services(cls, db: AsyncSession, rule_ids: List[int]) -> ResponseUtil:
        """删除紧急度规则"""
        if not rule_ids:
            return ResponseUtil.failure(msg="请选择要删除的规则")
            
        # 在删除前获取规则信息
        rules_to_delete = await BusinessRuleDao.get_urgency_rules_by_ids(db, rule_ids)
        if not rules_to_delete:
            return ResponseUtil.failure(msg="规则不存在或已被删除")

        try:
            success = await BusinessRuleDao.delete_urgency_rule(db, rule_ids)
            if success:
                logger.info(f"成功删除紧急度规则: {rule_ids}")

                # 为每条被删除的规则触发后台任务
                for rule in rules_to_delete:
                    recalculate_urgency_for_rule_change.delay(rule.business_type, rule.hardware_type)
                    logger.info(f"为已删除的规则 {rule.business_type}-{rule.hardware_type} 触发紧急度重新计算任务")

                return ResponseUtil.success(msg="删除规则成功")
            else:
                return ResponseUtil.failure(msg="删除规则失败")
        except Exception as e:
            logger.error(f"删除紧急度规则失败: {str(e)}")
            return ResponseUtil.failure(msg="删除规则失败") 