"""
值班人员DO模型
"""
from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class DutyPersonDO(Base):
    """值班人员表"""
    __tablename__ = 'duty_person'
    
    person_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='人员ID')
    person_name = Column(String(100), nullable=False, comment='姓名')
    department = Column(String(100), comment='部门')
    position = Column(String(100), comment='职位')
    phone = Column(String(20), comment='手机号')
    email = Column(String(100), comment='邮箱')
    status = Column(String(2), default='1', comment='状态：0=停用，1=正常')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    remarks = Column(String(500), comment='备注')
    
    # 关联关系
    schedules = relationship("DutyScheduleDO", back_populates="person") 