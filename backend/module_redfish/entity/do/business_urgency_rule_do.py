"""
业务硬件紧急度规则DO模型
"""
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, SmallInteger
from sqlalchemy.sql import func

from .base import Base


class BusinessHardwareUrgencyRulesDO(Base):
    """业务硬件紧急度规则表"""
    __tablename__ = 'business_hardware_urgency_rules'
    
    rule_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='规则ID')
    business_type = Column(String(50), nullable=False, comment='业务类型')
    hardware_type = Column(String(50), nullable=False, comment='硬件类型')
    urgency_level = Column(String(20), nullable=False, comment='紧急程度')
    description = Column(String(200), comment='规则描述')
    is_active = Column(SmallInteger, default=1, comment='是否启用')
    create_by = Column(String(64), default='', comment='创建者')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')
    update_by = Column(String(64), default='', comment='更新者')
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间') 