"""
硬件类型字典DO模型
"""
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, SmallInteger
from sqlalchemy.sql import func

from .base import Base


class HardwareTypeDictDO(Base):
    """硬件类型字典表"""
    __tablename__ = 'hardware_type_dict'
    
    type_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='类型ID')
    type_code = Column(String(50), nullable=False, unique=True, comment='类型编码')
    type_name = Column(String(100), nullable=False, comment='类型名称')
    type_description = Column(String(200), comment='类型描述')
    category = Column(String(50), comment='硬件分类')
    sort_order = Column(Integer, default=0, comment='排序顺序')
    is_active = Column(SmallInteger, default=1, comment='是否启用')
    create_by = Column(String(64), default='', comment='创建者')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')
    update_by = Column(String(64), default='', comment='更新者')
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间') 