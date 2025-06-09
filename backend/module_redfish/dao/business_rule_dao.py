"""
业务硬件紧急度规则DAO数据访问层
"""
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import select, func, and_, or_, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from module_redfish.models import BusinessHardwareUrgencyRules
from module_redfish.entity.vo.business_rule_vo import (
    BusinessRulePageQueryModel, AddBusinessRuleModel, EditBusinessRuleModel
)


class BusinessRuleDao:
    """业务硬件紧急度规则数据访问类"""
    
    @classmethod
    async def get_rule_list(
        cls,
        db: AsyncSession,
        query_object: BusinessRulePageQueryModel,
        is_page: bool = False
    ) -> Tuple[List[BusinessHardwareUrgencyRules], int]:
        """
        获取规则列表
        
        Args:
            db: 数据库会话
            query_object: 查询对象
            is_page: 是否分页
            
        Returns:
            Tuple[List[BusinessHardwareUrgencyRules], int]: 规则列表和总数
        """
        query = select(BusinessHardwareUrgencyRules)
        
        # 构建查询条件
        conditions = []
        
        if query_object.business_type:
            conditions.append(BusinessHardwareUrgencyRules.business_type.like(f'%{query_object.business_type}%'))
        
        if query_object.hardware_type:
            conditions.append(BusinessHardwareUrgencyRules.hardware_type.like(f'%{query_object.hardware_type}%'))
        
        if query_object.urgency_level:
            conditions.append(BusinessHardwareUrgencyRules.urgency_level == query_object.urgency_level)
        
        if query_object.is_active is not None:
            conditions.append(BusinessHardwareUrgencyRules.is_active == query_object.is_active)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 排序
        query = query.order_by(desc(BusinessHardwareUrgencyRules.create_time))
        
        # 分页
        if is_page:
            # 获取总数
            count_query = select(func.count(BusinessHardwareUrgencyRules.rule_id))
            if conditions:
                count_query = count_query.where(and_(*conditions))
            total_count = await db.scalar(count_query)
            
            # 分页查询
            query = query.offset((query_object.page_num - 1) * query_object.page_size).limit(query_object.page_size)
            result = await db.execute(query)
            rule_list = result.scalars().all()
            
            return rule_list, total_count
        else:
            result = await db.execute(query)
            rule_list = result.scalars().all()
            return rule_list, len(rule_list)
    
    @classmethod
    async def get_rule_by_id(cls, db: AsyncSession, rule_id: int) -> Optional[BusinessHardwareUrgencyRules]:
        """
        根据ID获取规则信息
        
        Args:
            db: 数据库会话
            rule_id: 规则ID
            
        Returns:
            Optional[BusinessHardwareUrgencyRules]: 规则信息
        """
        result = await db.execute(
            select(BusinessHardwareUrgencyRules).where(BusinessHardwareUrgencyRules.rule_id == rule_id)
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_rule_by_type(
        cls, 
        db: AsyncSession, 
        business_type: str, 
        hardware_type: str
    ) -> Optional[BusinessHardwareUrgencyRules]:
        """
        根据业务类型和硬件类型获取规则
        
        Args:
            db: 数据库会话
            business_type: 业务类型
            hardware_type: 硬件类型
            
        Returns:
            Optional[BusinessHardwareUrgencyRules]: 规则信息
        """
        result = await db.execute(
            select(BusinessHardwareUrgencyRules).where(
                and_(
                    BusinessHardwareUrgencyRules.business_type == business_type,
                    BusinessHardwareUrgencyRules.hardware_type == hardware_type,
                    BusinessHardwareUrgencyRules.is_active == 1
                )
            )
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def check_rule_exists(
        cls, 
        db: AsyncSession, 
        business_type: str, 
        hardware_type: str, 
        exclude_rule_id: Optional[int] = None
    ) -> bool:
        """
        检查规则是否已存在
        
        Args:
            db: 数据库会话
            business_type: 业务类型
            hardware_type: 硬件类型
            exclude_rule_id: 排除的规则ID（用于编辑时检查）
            
        Returns:
            bool: 是否存在
        """
        conditions = [
            BusinessHardwareUrgencyRules.business_type == business_type,
            BusinessHardwareUrgencyRules.hardware_type == hardware_type
        ]
        
        if exclude_rule_id:
            conditions.append(BusinessHardwareUrgencyRules.rule_id != exclude_rule_id)
        
        result = await db.execute(
            select(BusinessHardwareUrgencyRules).where(and_(*conditions))
        )
        return result.scalar_one_or_none() is not None
    
    @classmethod
    async def add_rule(cls, db: AsyncSession, rule: AddBusinessRuleModel) -> BusinessHardwareUrgencyRules:
        """
        添加规则
        
        Args:
            db: 数据库会话
            rule: 规则信息
            
        Returns:
            BusinessHardwareUrgencyRules: 新增的规则信息
        """
        db_rule = BusinessHardwareUrgencyRules(**rule.model_dump())
        db.add(db_rule)
        await db.commit()
        await db.refresh(db_rule)
        return db_rule
    
    @classmethod
    async def edit_rule(cls, db: AsyncSession, rule: EditBusinessRuleModel) -> bool:
        """
        编辑规则
        
        Args:
            db: 数据库会话
            rule: 规则信息
            
        Returns:
            bool: 是否成功
        """
        result = await db.execute(
            select(BusinessHardwareUrgencyRules).where(BusinessHardwareUrgencyRules.rule_id == rule.rule_id)
        )
        db_rule = result.scalar_one_or_none()
        
        if not db_rule:
            return False
        
        # 更新字段
        update_data = rule.model_dump(exclude={'rule_id'}, exclude_none=True)
        for field, value in update_data.items():
            setattr(db_rule, field, value)
        
        await db.commit()
        return True
    
    @classmethod
    async def delete_rule(cls, db: AsyncSession, rule_ids: List[int]) -> bool:
        """
        删除规则
        
        Args:
            db: 数据库会话
            rule_ids: 规则ID列表
            
        Returns:
            bool: 是否成功
        """
        await db.execute(
            delete(BusinessHardwareUrgencyRules).where(BusinessHardwareUrgencyRules.rule_id.in_(rule_ids))
        )
        await db.commit()
        return True
    
    @classmethod
    async def get_rule_statistics(cls, db: AsyncSession) -> Dict[str, Any]:
        """
        获取规则统计信息
        
        Args:
            db: 数据库会话
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        # 总规则数
        total_result = await db.execute(
            select(func.count(BusinessHardwareUrgencyRules.rule_id))
        )
        total_rules = total_result.scalar()
        
        # 启用规则数
        active_result = await db.execute(
            select(func.count(BusinessHardwareUrgencyRules.rule_id)).where(
                BusinessHardwareUrgencyRules.is_active == 1
            )
        )
        active_rules = active_result.scalar()
        
        # 紧急规则数
        urgent_result = await db.execute(
            select(func.count(BusinessHardwareUrgencyRules.rule_id)).where(
                and_(
                    BusinessHardwareUrgencyRules.urgency_level == 'urgent',
                    BusinessHardwareUrgencyRules.is_active == 1
                )
            )
        )
        urgent_rules = urgent_result.scalar()
        
        # 择期规则数
        scheduled_result = await db.execute(
            select(func.count(BusinessHardwareUrgencyRules.rule_id)).where(
                and_(
                    BusinessHardwareUrgencyRules.urgency_level == 'scheduled',
                    BusinessHardwareUrgencyRules.is_active == 1
                )
            )
        )
        scheduled_rules = scheduled_result.scalar()
        
        # 业务类型列表
        business_types_result = await db.execute(
            select(BusinessHardwareUrgencyRules.business_type).distinct()
        )
        business_types = [row[0] for row in business_types_result.fetchall()]
        
        # 硬件类型列表
        hardware_types_result = await db.execute(
            select(BusinessHardwareUrgencyRules.hardware_type).distinct()
        )
        hardware_types = [row[0] for row in hardware_types_result.fetchall()]
        
        return {
            'total_rules': total_rules,
            'active_rules': active_rules,
            'urgent_rules': urgent_rules,
            'scheduled_rules': scheduled_rules,
            'business_types': business_types,
            'hardware_types': hardware_types
        }
    
    @classmethod
    async def batch_update_status(cls, db: AsyncSession, rule_ids: List[int], is_active: int) -> bool:
        """
        批量更新规则状态
        
        Args:
            db: 数据库会话
            rule_ids: 规则ID列表
            is_active: 启用状态
            
        Returns:
            bool: 是否成功
        """
        result = await db.execute(
            select(BusinessHardwareUrgencyRules).where(
                BusinessHardwareUrgencyRules.rule_id.in_(rule_ids)
            )
        )
        rules = result.scalars().all()
        
        for rule in rules:
            rule.is_active = is_active
            rule.update_time = datetime.now()
        
        await db.commit()
        return True 