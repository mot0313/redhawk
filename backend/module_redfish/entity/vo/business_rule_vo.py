"""
业务硬件紧急度规则VO模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from module_admin.annotation.pydantic_annotation import as_query


class BusinessRuleModel(BaseModel):
    """业务规则基础模型"""
    rule_id: Optional[int] = Field(default=None, description="规则ID")
    business_type: str = Field(..., description="业务类型")
    hardware_type: str = Field(..., description="硬件类型")
    urgency_level: str = Field(..., description="紧急程度")
    description: Optional[str] = Field(default=None, description="规则描述")
    is_active: int = Field(default=1, description="是否启用")
    create_by: Optional[str] = Field(default="", description="创建者")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_by: Optional[str] = Field(default="", description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")


class AddBusinessRuleModel(BaseModel):
    """添加业务规则模型"""
    business_type: str = Field(..., description="业务类型")
    hardware_type: str = Field(..., description="硬件类型")
    urgency_level: str = Field(..., description="紧急程度")
    description: Optional[str] = Field(default=None, description="规则描述")
    is_active: int = Field(default=1, description="是否启用")
    create_by: Optional[str] = Field(default="", description="创建者")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")


class EditBusinessRuleModel(BaseModel):
    """编辑业务规则模型"""
    rule_id: int = Field(..., description="规则ID")
    business_type: Optional[str] = Field(default=None, description="业务类型")
    hardware_type: Optional[str] = Field(default=None, description="硬件类型")
    urgency_level: Optional[str] = Field(default=None, description="紧急程度")
    description: Optional[str] = Field(default=None, description="规则描述")
    is_active: Optional[int] = Field(default=None, description="是否启用")
    update_by: Optional[str] = Field(default="", description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")


class DeleteBusinessRuleModel(BaseModel):
    """删除业务规则模型"""
    rule_ids: str = Field(..., description="规则ID列表，逗号分隔")
    update_by: Optional[str] = Field(default="", description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")


class BusinessRuleQueryModel(BaseModel):
    """业务规则查询模型"""
    model_config = ConfigDict(alias_generator=to_camel)
    
    business_type: Optional[str] = Field(default=None, description="业务类型")
    hardware_type: Optional[str] = Field(default=None, description="硬件类型")
    urgency_level: Optional[str] = Field(default=None, description="紧急程度")
    is_active: Optional[int] = Field(default=None, description="是否启用")


@as_query
class BusinessRulePageQueryModel(BusinessRuleQueryModel):
    """业务规则分页查询模型"""
    page_num: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页记录数")


class BusinessRuleStatisticsModel(BaseModel):
    """业务规则统计信息模型"""
    total_rules: int = Field(..., description="总规则数")
    active_rules: int = Field(..., description="启用规则数")
    urgent_rules: int = Field(..., description="紧急规则数")
    scheduled_rules: int = Field(..., description="择期规则数")
    business_types: List[str] = Field(..., description="业务类型列表")
    hardware_types: List[str] = Field(..., description="硬件类型列表")


class BusinessRuleDetailModel(BaseModel):
    """业务规则详情模型"""
    rule: BusinessRuleModel
    related_devices_count: Optional[int] = Field(default=0, description="关联设备数量")
    related_alerts_count: Optional[int] = Field(default=0, description="关联告警数量")


class UrgencyRuleMatchModel(BaseModel):
    """紧急度规则匹配模型"""
    business_type: str = Field(..., description="业务类型")
    hardware_type: str = Field(..., description="硬件类型")


class UrgencyRuleResultModel(BaseModel):
    """紧急度规则匹配结果模型"""
    matched: bool = Field(..., description="是否匹配到规则")
    urgency_level: Optional[str] = Field(default=None, description="紧急程度")
    description: Optional[str] = Field(default=None, description="规则描述")
    rule_id: Optional[int] = Field(default=None, description="规则ID") 


class BusinessTypeQueryModel(BaseModel):
    """业务类型查询模型"""
    model_config = ConfigDict(alias_generator=lambda x: x)
    
    page_num: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页大小")
    type_code: Optional[str] = Field(None, description="类型编码")
    type_name: Optional[str] = Field(None, description="类型名称")
    is_active: Optional[int] = Field(None, description="是否启用")

    @classmethod
    def as_query(cls, 
                page_num: int = 1, 
                page_size: int = 10,
                type_code: Optional[str] = None,
                type_name: Optional[str] = None,
                is_active: Optional[int] = None):
        return cls(
            page_num=page_num,
            page_size=page_size,
            type_code=type_code,
            type_name=type_name,
            is_active=is_active
        )


class AddBusinessTypeModel(BaseModel):
    """新增业务类型模型"""
    model_config = ConfigDict(alias_generator=lambda x: x)
    
    type_code: str = Field(..., description="类型编码")
    type_name: str = Field(..., description="类型名称")
    type_description: Optional[str] = Field(None, description="类型描述")
    sort_order: int = Field(0, description="排序顺序")
    is_active: int = Field(1, description="是否启用")


class EditBusinessTypeModel(BaseModel):
    """编辑业务类型模型"""
    model_config = ConfigDict(alias_generator=to_camel)
    
    type_id: int = Field(..., description="类型ID")
    type_code: str = Field(..., description="类型编码")
    type_name: str = Field(..., description="类型名称")
    type_description: Optional[str] = Field(None, description="类型描述")
    sort_order: int = Field(0, description="排序顺序")
    is_active: int = Field(1, description="是否启用")


class HardwareTypeQueryModel(BaseModel):
    """硬件类型查询模型"""
    model_config = ConfigDict(alias_generator=lambda x: x)
    
    page_num: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页大小")
    type_code: Optional[str] = Field(None, description="类型编码")
    type_name: Optional[str] = Field(None, description="类型名称")
    category: Optional[str] = Field(None, description="硬件分类")
    is_active: Optional[int] = Field(None, description="是否启用")

    @classmethod
    def as_query(cls, 
                page_num: int = 1, 
                page_size: int = 10,
                type_code: Optional[str] = None,
                type_name: Optional[str] = None,
                category: Optional[str] = None,
                is_active: Optional[int] = None):
        return cls(
            page_num=page_num,
            page_size=page_size,
            type_code=type_code,
            type_name=type_name,
            category=category,
            is_active=is_active
        )


class AddHardwareTypeModel(BaseModel):
    """新增硬件类型模型"""
    model_config = ConfigDict(alias_generator=lambda x: x)
    
    type_code: str = Field(..., description="类型编码")
    type_name: str = Field(..., description="类型名称")
    type_description: Optional[str] = Field(None, description="类型描述")
    category: Optional[str] = Field(None, description="硬件分类")
    sort_order: int = Field(0, description="排序顺序")
    is_active: int = Field(1, description="是否启用")


class EditHardwareTypeModel(BaseModel):
    """编辑硬件类型模型"""
    model_config = ConfigDict(alias_generator=to_camel)
    
    type_id: int = Field(..., description="类型ID")
    type_code: str = Field(..., description="类型编码")
    type_name: str = Field(..., description="类型名称")
    type_description: Optional[str] = Field(None, description="类型描述")
    category: Optional[str] = Field(None, description="硬件分类")
    sort_order: int = Field(0, description="排序顺序")
    is_active: int = Field(1, description="是否启用")


class UrgencyRuleQueryModel(BaseModel):
    """紧急度规则查询模型"""
    model_config = ConfigDict(alias_generator=lambda x: x)
    
    page_num: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页大小")
    business_type: Optional[str] = Field(None, description="业务类型")
    hardware_type: Optional[str] = Field(None, description="硬件类型")
    urgency_level: Optional[str] = Field(None, description="紧急程度")
    is_active: Optional[int] = Field(None, description="是否启用")

    @classmethod
    def as_query(cls, 
                page_num: int = 1, 
                page_size: int = 10,
                business_type: Optional[str] = None,
                hardware_type: Optional[str] = None,
                urgency_level: Optional[str] = None,
                is_active: Optional[int] = None):
        return cls(
            page_num=page_num,
            page_size=page_size,
            business_type=business_type,
            hardware_type=hardware_type,
            urgency_level=urgency_level,
            is_active=is_active
        )


class AddUrgencyRuleModel(BaseModel):
    """新增紧急度规则模型"""
    model_config = ConfigDict(alias_generator=lambda x: x)
    
    business_type: str = Field(..., description="业务类型")
    hardware_type: str = Field(..., description="硬件类型")
    urgency_level: str = Field(..., description="紧急程度")
    description: Optional[str] = Field(None, description="规则描述")
    is_active: int = Field(1, description="是否启用")


class EditUrgencyRuleModel(BaseModel):
    """编辑紧急度规则模型"""
    model_config = ConfigDict(alias_generator=to_camel)
    
    rule_id: int = Field(..., description="规则ID")
    business_type: str = Field(..., description="业务类型")
    hardware_type: str = Field(..., description="硬件类型")
    urgency_level: str = Field(..., description="紧急程度")
    description: Optional[str] = Field(None, description="规则描述")
    is_active: int = Field(1, description="是否启用")


class BusinessTypeModel(BaseModel):
    """业务类型模型"""
    model_config = ConfigDict(alias_generator=lambda x: x)
    
    type_id: int = Field(..., description="类型ID")
    type_code: str = Field(..., description="类型编码")
    type_name: str = Field(..., description="类型名称")
    type_description: Optional[str] = Field(None, description="类型描述")
    sort_order: int = Field(0, description="排序顺序")
    is_active: int = Field(1, description="是否启用")
    create_by: Optional[str] = Field(None, description="创建者")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_by: Optional[str] = Field(None, description="更新者")
    update_time: Optional[datetime] = Field(None, description="更新时间")


class HardwareTypeModel(BaseModel):
    """硬件类型模型"""
    model_config = ConfigDict(alias_generator=lambda x: x)
    
    type_id: int = Field(..., description="类型ID")
    type_code: str = Field(..., description="类型编码")
    type_name: str = Field(..., description="类型名称")
    type_description: Optional[str] = Field(None, description="类型描述")
    category: Optional[str] = Field(None, description="硬件分类")
    sort_order: int = Field(0, description="排序顺序")
    is_active: int = Field(1, description="是否启用")
    create_by: Optional[str] = Field(None, description="创建者")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_by: Optional[str] = Field(None, description="更新者")
    update_time: Optional[datetime] = Field(None, description="更新时间")


class UrgencyRuleModel(BaseModel):
    """紧急度规则模型"""
    model_config = ConfigDict(alias_generator=lambda x: x)
    
    rule_id: int = Field(..., description="规则ID")
    business_type: str = Field(..., description="业务类型")
    hardware_type: str = Field(..., description="硬件类型")
    urgency_level: str = Field(..., description="紧急程度")
    description: Optional[str] = Field(None, description="规则描述")
    is_active: int = Field(1, description="是否启用")
    create_by: Optional[str] = Field(None, description="创建者")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_by: Optional[str] = Field(None, description="更新者")
    update_time: Optional[datetime] = Field(None, description="更新时间")
    
    # 关联字段
    business_type_name: Optional[str] = Field(None, description="业务类型名称")
    hardware_type_name: Optional[str] = Field(None, description="硬件类型名称") 