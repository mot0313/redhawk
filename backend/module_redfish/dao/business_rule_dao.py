"""
业务硬件紧急度规则DAO数据访问层
"""
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import select, func, and_, or_, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from module_redfish.models import BusinessHardwareUrgencyRules, BusinessTypeDict, HardwareTypeDict
from module_redfish.entity.vo.business_rule_vo import (
    BusinessRulePageQueryModel, AddBusinessRuleModel, EditBusinessRuleModel,
    BusinessTypeQueryModel, HardwareTypeQueryModel, UrgencyRuleQueryModel,
    AddBusinessTypeModel, EditBusinessTypeModel,
    AddHardwareTypeModel, EditHardwareTypeModel,
    AddUrgencyRuleModel, EditUrgencyRuleModel
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


class BusinessTypeDao:
    """业务类型DAO"""

    @staticmethod
    async def get_business_type_list(
        db: AsyncSession,
        query_object: BusinessTypeQueryModel,
        is_page: bool = False
    ) -> Tuple[List[BusinessTypeDict], int]:
        """获取业务类型列表"""
        conditions = []
        
        if query_object.type_code:
            conditions.append(BusinessTypeDict.type_code.like(f'%{query_object.type_code}%'))
        if query_object.type_name:
            conditions.append(BusinessTypeDict.type_name.like(f'%{query_object.type_name}%'))
        if query_object.is_active is not None:
            conditions.append(BusinessTypeDict.is_active == query_object.is_active)
        
        query = select(BusinessTypeDict)
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(BusinessTypeDict.sort_order.asc(), BusinessTypeDict.create_time.desc())
        
        count_query = select(func.count(BusinessTypeDict.type_id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0
        
        if is_page:
            offset = (query_object.page_num - 1) * query_object.page_size
            query = query.offset(offset).limit(query_object.page_size)
        
        result = await db.execute(query)
        business_types = result.scalars().all()
        
        return business_types, total
    
    @staticmethod
    async def get_business_type_by_id(db: AsyncSession, type_id: int) -> Optional[BusinessTypeDict]:
        """根据ID获取业务类型"""
        query = select(BusinessTypeDict).where(BusinessTypeDict.type_id == type_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_business_type_by_code(db: AsyncSession, type_code: str) -> Optional[BusinessTypeDict]:
        """根据编码获取业务类型"""
        query = select(BusinessTypeDict).where(BusinessTypeDict.type_code == type_code)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def add_business_type(db: AsyncSession, business_type: AddBusinessTypeModel) -> BusinessTypeDict:
        """新增业务类型"""
        new_business_type = BusinessTypeDict(
            type_code=business_type.type_code,
            type_name=business_type.type_name,
            type_description=business_type.type_description,
            sort_order=business_type.sort_order,
            is_active=business_type.is_active,
            create_by='admin',
            create_time=datetime.now()
        )
        
        db.add(new_business_type)
        await db.commit()
        await db.refresh(new_business_type)
        return new_business_type
    
    @staticmethod
    async def edit_business_type(db: AsyncSession, business_type: EditBusinessTypeModel) -> bool:
        """编辑业务类型"""
        query = select(BusinessTypeDict).where(BusinessTypeDict.type_id == business_type.type_id)
        result = await db.execute(query)
        existing_business_type = result.scalar_one_or_none()
        
        if not existing_business_type:
            return False
        
        existing_business_type.type_code = business_type.type_code
        existing_business_type.type_name = business_type.type_name
        existing_business_type.type_description = business_type.type_description
        existing_business_type.sort_order = business_type.sort_order
        existing_business_type.is_active = business_type.is_active
        existing_business_type.update_by = 'admin'
        existing_business_type.update_time = datetime.now()
        
        await db.commit()
        return True
    
    @staticmethod
    async def delete_business_type(db: AsyncSession, type_id: int) -> bool:
        """删除业务类型"""
        query = select(BusinessTypeDict).where(BusinessTypeDict.type_id == type_id)
        result = await db.execute(query)
        business_type = result.scalar_one_or_none()
        
        if not business_type:
            return False
        
        await db.delete(business_type)
        await db.commit()
        return True
    
    @staticmethod
    async def get_all_business_types(db: AsyncSession) -> List[BusinessTypeDict]:
        """获取所有启用的业务类型"""
        query = select(BusinessTypeDict).where(
            BusinessTypeDict.is_active == 1
        ).order_by(BusinessTypeDict.sort_order.asc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_business_type_detail(db: AsyncSession, type_id: int) -> Optional[BusinessTypeDict]:
        """获取业务类型详情"""
        return await BusinessTypeDao.get_business_type_by_id(db, type_id)
    
    @staticmethod
    async def check_business_type_exists(db: AsyncSession, type_code: str, exclude_id: Optional[int] = None) -> bool:
        """检查业务类型编码是否存在"""
        query = select(BusinessTypeDict).where(BusinessTypeDict.type_code == type_code)
        if exclude_id:
            query = query.where(BusinessTypeDict.type_id != exclude_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None
    
    @staticmethod
    async def delete_business_type(db: AsyncSession, type_ids: List[int]) -> bool:
        """批量删除业务类型"""
        try:
            query = select(BusinessTypeDict).where(BusinessTypeDict.type_id.in_(type_ids))
            result = await db.execute(query)
            business_types = result.scalars().all()
            
            for business_type in business_types:
                await db.delete(business_type)
            
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            return False
    
    @staticmethod
    async def get_business_type_options(db: AsyncSession) -> List[Dict[str, Any]]:
        """获取业务类型选项"""
        query = select(BusinessTypeDict).where(
            BusinessTypeDict.is_active == 1
        ).order_by(BusinessTypeDict.sort_order.asc())
        
        result = await db.execute(query)
        business_types = result.scalars().all()
        
        return [
            {
                'value': bt.type_code,
                'label': bt.type_name,
                'type_id': bt.type_id
            }
            for bt in business_types
        ]


class HardwareTypeDao:
    """硬件类型DAO"""

    @staticmethod
    async def get_hardware_type_list(
        db: AsyncSession,
        query_object: HardwareTypeQueryModel,
        is_page: bool = False
    ) -> Tuple[List[HardwareTypeDict], int]:
        """获取硬件类型列表"""
        conditions = []
        
        if query_object.type_code:
            conditions.append(HardwareTypeDict.type_code.like(f'%{query_object.type_code}%'))
        if query_object.type_name:
            conditions.append(HardwareTypeDict.type_name.like(f'%{query_object.type_name}%'))
        if query_object.category:
            conditions.append(HardwareTypeDict.category.like(f'%{query_object.category}%'))
        if query_object.is_active is not None:
            conditions.append(HardwareTypeDict.is_active == query_object.is_active)
        
        query = select(HardwareTypeDict)
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(HardwareTypeDict.sort_order.asc(), HardwareTypeDict.create_time.desc())
        
        count_query = select(func.count(HardwareTypeDict.type_id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0
        
        if is_page:
            offset = (query_object.page_num - 1) * query_object.page_size
            query = query.offset(offset).limit(query_object.page_size)
        
        result = await db.execute(query)
        hardware_types = result.scalars().all()
        
        return hardware_types, total
    
    @staticmethod
    async def get_hardware_type_by_id(db: AsyncSession, type_id: int) -> Optional[HardwareTypeDict]:
        """根据ID获取硬件类型"""
        query = select(HardwareTypeDict).where(HardwareTypeDict.type_id == type_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_hardware_type_by_code(db: AsyncSession, type_code: str) -> Optional[HardwareTypeDict]:
        """根据编码获取硬件类型"""
        query = select(HardwareTypeDict).where(HardwareTypeDict.type_code == type_code)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def add_hardware_type(db: AsyncSession, hardware_type: AddHardwareTypeModel) -> HardwareTypeDict:
        """新增硬件类型"""
        new_hardware_type = HardwareTypeDict(
            type_code=hardware_type.type_code,
            type_name=hardware_type.type_name,
            type_description=hardware_type.type_description,
            category=hardware_type.category,
            sort_order=hardware_type.sort_order,
            is_active=hardware_type.is_active,
            create_by='admin',
            create_time=datetime.now()
        )
        
        db.add(new_hardware_type)
        await db.commit()
        await db.refresh(new_hardware_type)
        return new_hardware_type
    
    @staticmethod
    async def edit_hardware_type(db: AsyncSession, hardware_type: EditHardwareTypeModel) -> bool:
        """编辑硬件类型"""
        query = select(HardwareTypeDict).where(HardwareTypeDict.type_id == hardware_type.type_id)
        result = await db.execute(query)
        existing_hardware_type = result.scalar_one_or_none()
        
        if not existing_hardware_type:
            return False
        
        existing_hardware_type.type_code = hardware_type.type_code
        existing_hardware_type.type_name = hardware_type.type_name
        existing_hardware_type.type_description = hardware_type.type_description
        existing_hardware_type.category = hardware_type.category
        existing_hardware_type.sort_order = hardware_type.sort_order
        existing_hardware_type.is_active = hardware_type.is_active
        existing_hardware_type.update_by = 'admin'
        existing_hardware_type.update_time = datetime.now()
        
        await db.commit()
        return True
    
    @staticmethod
    async def delete_hardware_type(db: AsyncSession, type_id: int) -> bool:
        """删除硬件类型"""
        query = select(HardwareTypeDict).where(HardwareTypeDict.type_id == type_id)
        result = await db.execute(query)
        hardware_type = result.scalar_one_or_none()
        
        if not hardware_type:
            return False
        
        await db.delete(hardware_type)
        await db.commit()
        return True
    
    @staticmethod
    async def get_all_hardware_types(db: AsyncSession) -> List[HardwareTypeDict]:
        """获取所有启用的硬件类型"""
        query = select(HardwareTypeDict).where(
            HardwareTypeDict.is_active == 1
        ).order_by(HardwareTypeDict.sort_order.asc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_hardware_categories(db: AsyncSession) -> List[str]:
        """获取所有硬件分类"""
        query = select(HardwareTypeDict.category).distinct().where(
            and_(
                HardwareTypeDict.category.is_not(None),
                HardwareTypeDict.is_active == 1
            )
        )
        
        result = await db.execute(query)
        categories = result.scalars().all()
        return [cat for cat in categories if cat]
    
    @staticmethod
    async def get_hardware_type_detail(db: AsyncSession, type_id: int) -> Optional[HardwareTypeDict]:
        """获取硬件类型详情"""
        return await HardwareTypeDao.get_hardware_type_by_id(db, type_id)
    
    @staticmethod
    async def check_hardware_type_exists(db: AsyncSession, type_code: str, exclude_id: Optional[int] = None) -> bool:
        """检查硬件类型编码是否存在"""
        query = select(HardwareTypeDict).where(HardwareTypeDict.type_code == type_code)
        if exclude_id:
            query = query.where(HardwareTypeDict.type_id != exclude_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None
    
    @staticmethod
    async def delete_hardware_type(db: AsyncSession, type_ids: List[int]) -> bool:
        """批量删除硬件类型"""
        try:
            query = select(HardwareTypeDict).where(HardwareTypeDict.type_id.in_(type_ids))
            result = await db.execute(query)
            hardware_types = result.scalars().all()
            
            for hardware_type in hardware_types:
                await db.delete(hardware_type)
            
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            return False
    
    @staticmethod
    async def get_hardware_type_options(db: AsyncSession) -> List[Dict[str, Any]]:
        """获取硬件类型选项"""
        query = select(HardwareTypeDict).where(
            HardwareTypeDict.is_active == 1
        ).order_by(HardwareTypeDict.sort_order.asc())
        
        result = await db.execute(query)
        hardware_types = result.scalars().all()
        
        return [
            {
                'value': ht.type_code,
                'label': ht.type_name,
                'type_id': ht.type_id,
                'category': ht.category
            }
            for ht in hardware_types
        ]


class UrgencyRuleDao:
    """紧急度规则DAO"""

    @staticmethod
    async def get_urgency_rule_list(
        db: AsyncSession,
        query_object: UrgencyRuleQueryModel,
        is_page: bool = False
    ) -> Tuple[List[Dict[str, Any]], int]:
        """获取紧急度规则列表（包含关联的业务类型和硬件类型名称）"""
        conditions = []
        
        if query_object.business_type:
            conditions.append(BusinessHardwareUrgencyRules.business_type.like(f'%{query_object.business_type}%'))
        if query_object.hardware_type:
            conditions.append(BusinessHardwareUrgencyRules.hardware_type.like(f'%{query_object.hardware_type}%'))
        if query_object.urgency_level:
            conditions.append(BusinessHardwareUrgencyRules.urgency_level == query_object.urgency_level)
        if query_object.is_active is not None:
            conditions.append(BusinessHardwareUrgencyRules.is_active == query_object.is_active)
        
        query = select(
            BusinessHardwareUrgencyRules,
            BusinessTypeDict.type_name.label('business_type_name'),
            HardwareTypeDict.type_name.label('hardware_type_name')
        ).outerjoin(
            BusinessTypeDict,
            BusinessHardwareUrgencyRules.business_type == BusinessTypeDict.type_code
        ).outerjoin(
            HardwareTypeDict,
            BusinessHardwareUrgencyRules.hardware_type == HardwareTypeDict.type_code
        )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(BusinessHardwareUrgencyRules.create_time.desc())
        
        count_query = select(func.count(BusinessHardwareUrgencyRules.rule_id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0
        
        if is_page:
            offset = (query_object.page_num - 1) * query_object.page_size
            query = query.offset(offset).limit(query_object.page_size)
        
        result = await db.execute(query)
        rows = result.all()
        
        rules = []
        for row in rows:
            rule = row[0]  # BusinessHardwareUrgencyRules 对象
            business_type_name = row[1]  # business_type_name
            hardware_type_name = row[2]  # hardware_type_name
            
            rule_dict = {
                'rule_id': rule.rule_id,
                'business_type': rule.business_type,
                'hardware_type': rule.hardware_type,
                'urgency_level': rule.urgency_level,
                'description': rule.description,
                'is_active': rule.is_active,
                'create_by': rule.create_by,
                'create_time': rule.create_time,
                'update_by': rule.update_by,
                'update_time': rule.update_time,
                'business_type_name': business_type_name,
                'hardware_type_name': hardware_type_name
            }
            rules.append(rule_dict)
        
        return rules, total
    
    @staticmethod
    async def get_urgency_rule_by_id(db: AsyncSession, rule_id: int) -> Optional[BusinessHardwareUrgencyRules]:
        """根据ID获取紧急度规则"""
        query = select(BusinessHardwareUrgencyRules).where(BusinessHardwareUrgencyRules.rule_id == rule_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_rule_by_type(
        db: AsyncSession, 
        business_type: str, 
        hardware_type: str
    ) -> Optional[BusinessHardwareUrgencyRules]:
        """根据业务类型和硬件类型获取规则"""
        query = select(BusinessHardwareUrgencyRules).where(
            and_(
                BusinessHardwareUrgencyRules.business_type == business_type,
                BusinessHardwareUrgencyRules.hardware_type == hardware_type,
                BusinessHardwareUrgencyRules.is_active == 1
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def add_urgency_rule(db: AsyncSession, rule: AddUrgencyRuleModel) -> BusinessHardwareUrgencyRules:
        """新增紧急度规则"""
        new_rule = BusinessHardwareUrgencyRules(
            business_type=rule.business_type,
            hardware_type=rule.hardware_type,
            urgency_level=rule.urgency_level,
            description=rule.description,
            is_active=rule.is_active,
            create_by='admin',
            create_time=datetime.now()
        )
        
        db.add(new_rule)
        await db.commit()
        await db.refresh(new_rule)
        return new_rule
    
    @staticmethod
    async def edit_urgency_rule(db: AsyncSession, rule: EditUrgencyRuleModel) -> bool:
        """编辑紧急度规则"""
        query = select(BusinessHardwareUrgencyRules).where(BusinessHardwareUrgencyRules.rule_id == rule.rule_id)
        result = await db.execute(query)
        existing_rule = result.scalar_one_or_none()
        
        if not existing_rule:
            return False
        
        existing_rule.business_type = rule.business_type
        existing_rule.hardware_type = rule.hardware_type
        existing_rule.urgency_level = rule.urgency_level
        existing_rule.description = rule.description
        existing_rule.is_active = rule.is_active
        existing_rule.update_by = 'admin'
        existing_rule.update_time = datetime.now()
        
        await db.commit()
        return True
    
    @staticmethod
    async def delete_urgency_rule(db: AsyncSession, rule_id: int) -> bool:
        """删除紧急度规则"""
        query = select(BusinessHardwareUrgencyRules).where(BusinessHardwareUrgencyRules.rule_id == rule_id)
        result = await db.execute(query)
        rule = result.scalar_one_or_none()
        
        if not rule:
            return False
        
        await db.delete(rule)
        await db.commit()
        return True
    
    @staticmethod
    async def get_urgency_rule_detail(db: AsyncSession, rule_id: int) -> Optional[BusinessHardwareUrgencyRules]:
        """获取紧急度规则详情"""
        return await UrgencyRuleDao.get_urgency_rule_by_id(db, rule_id)
    
    @staticmethod
    async def check_urgency_rule_exists(db: AsyncSession, business_type: str, hardware_type: str, exclude_id: Optional[int] = None) -> bool:
        """检查紧急度规则是否存在"""
        query = select(BusinessHardwareUrgencyRules).where(
            and_(
                BusinessHardwareUrgencyRules.business_type == business_type,
                BusinessHardwareUrgencyRules.hardware_type == hardware_type
            )
        )
        if exclude_id:
            query = query.where(BusinessHardwareUrgencyRules.rule_id != exclude_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None
    
    @staticmethod
    async def delete_urgency_rules(db: AsyncSession, rule_ids: List[int]) -> bool:
        """批量删除紧急度规则"""
        try:
            query = select(BusinessHardwareUrgencyRules).where(BusinessHardwareUrgencyRules.rule_id.in_(rule_ids))
            result = await db.execute(query)
            rules = result.scalars().all()
            
            for rule in rules:
                await db.delete(rule)
            
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            return False 