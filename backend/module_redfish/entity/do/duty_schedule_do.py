"""
值班排期DO模型
"""
from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class DutyScheduleDO(Base):
    """值班排期表"""
    __tablename__ = 'duty_schedule'
    
    schedule_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='排期ID')
    person_id = Column(BigInteger, ForeignKey('duty_person.person_id'), nullable=False, comment='人员ID')
    duty_date = Column(DateTime, nullable=False, comment='值班日期')
    duty_type = Column(String(20), default='primary', comment='值班类型：primary=主值班，backup=备值班，emergency=应急值班')
    shift_type = Column(String(20), nullable=False, comment='班次类型：day=白班，night=夜班，all=全天')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    remarks = Column(String(500), comment='备注')
    
    # 关联关系
    person = relationship("DutyPersonDO", back_populates="schedules") 