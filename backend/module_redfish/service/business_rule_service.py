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
    UrgencyRuleMatchModel, UrgencyRuleResultModel
)
from utils.response_util import ResponseUtil
from utils.page_util import PageResponseModel
from utils.log_util import logger


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
        from module_redfish.models import BusinessTypeDict
        
        try:
            result = await db.execute(
                select(BusinessTypeDict)
                .where(BusinessTypeDict.is_active == 1)
                .order_by(BusinessTypeDict.sort_order, BusinessTypeDict.type_code)
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
        from module_redfish.models import HardwareTypeDict
        
        try:
            result = await db.execute(
                select(HardwareTypeDict)
                .where(HardwareTypeDict.is_active == 1)
                .order_by(HardwareTypeDict.sort_order, HardwareTypeDict.type_code)
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