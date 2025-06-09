"""
值班管理VO模型
"""
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from datetime import datetime, date
from typing import Optional, List
from module_admin.annotation.pydantic_annotation import as_query
class DutyPersonQueryModel(BaseModel):
    """值班人员查询对象"""
    person_id: Optional[int] = Field(None, description="人员ID")
    person_name: Optional[str] = Field(None, description="姓名")
    department: Optional[str] = Field(None, description="部门")
    position: Optional[str] = Field(None, description="职位")
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    status: Optional[str] = Field(None, description="状态")


@as_query
class DutyPersonPageQueryModel(DutyPersonQueryModel):
    """值班人员分页查询对象"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    page_num: int = Field(1, description="页码", ge=1)
    page_size: int = Field(10, description="每页数量", ge=1, le=100)


class DutyPersonModel(BaseModel):
    """值班人员响应模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    person_id: Optional[int] = Field(None, description="人员ID")
    person_name: Optional[str] = Field(None, description="姓名")
    department: Optional[str] = Field(None, description="部门")
    position: Optional[str] = Field(None, description="职位")
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    status: Optional[str] = Field(None, description="状态")
    status_dict: Optional[str] = Field(None, description="状态描述")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_time: Optional[datetime] = Field(None, description="更新时间")
    remarks: Optional[str] = Field(None, description="备注")


class DutyPersonAddModel(BaseModel):
    """新增值班人员模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    person_name: str = Field(..., description="姓名")
    department: Optional[str] = Field(None, description="部门")
    position: Optional[str] = Field(None, description="职位")
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    status: Optional[str] = Field("1", description="状态")
    remarks: Optional[str] = Field(None, description="备注")


class DutyPersonEditModel(BaseModel):
    """编辑值班人员模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    person_id: int = Field(..., description="人员ID")
    person_name: str = Field(..., description="姓名")
    department: Optional[str] = Field(None, description="部门")
    position: Optional[str] = Field(None, description="职位")
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    status: Optional[str] = Field("1", description="状态")
    remarks: Optional[str] = Field(None, description="备注")


class DutyScheduleQueryModel(BaseModel):
    """值班排期查询对象"""
    schedule_id: Optional[int] = Field(None, description="排期ID")
    person_id: Optional[int] = Field(None, description="人员ID")
    person_name: Optional[str] = Field(None, description="人员姓名")
    duty_date: Optional[date] = Field(None, description="值班日期")
    duty_type: Optional[str] = Field(None, description="值班类型")
    shift_type: Optional[str] = Field(None, description="班次类型")


@as_query
class DutySchedulePageQueryModel(DutyScheduleQueryModel):
    """值班排期分页查询对象"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    page_num: int = Field(1, description="页码", ge=1)
    page_size: int = Field(10, description="每页数量", ge=1, le=100)
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    department: Optional[str] = Field(None, description="部门")


class DutyScheduleModel(BaseModel):
    """值班排期响应模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    schedule_id: Optional[int] = Field(None, description="排期ID")
    person_id: Optional[int] = Field(None, description="人员ID")
    person_name: Optional[str] = Field(None, description="人员姓名")
    department: Optional[str] = Field(None, description="部门")
    duty_date: Optional[date] = Field(None, description="值班日期")
    duty_type: Optional[str] = Field(None, description="值班类型")
    duty_type_dict: Optional[str] = Field(None, description="值班类型描述")
    shift_type: Optional[str] = Field(None, description="班次类型")
    shift_type_dict: Optional[str] = Field(None, description="班次类型描述")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_time: Optional[datetime] = Field(None, description="更新时间")
    remarks: Optional[str] = Field(None, description="备注")


class DutyScheduleAddModel(BaseModel):
    """新增值班排期模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    person_id: int = Field(..., description="人员ID")
    duty_date: date = Field(..., description="值班日期")
    duty_type: str = Field(..., description="值班类型")
    shift_type: str = Field(..., description="班次类型")
    remarks: Optional[str] = Field(None, description="备注")


class DutyScheduleEditModel(BaseModel):
    """编辑值班排期模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    schedule_id: int = Field(..., description="排期ID")
    person_id: int = Field(..., description="人员ID")
    duty_date: date = Field(..., description="值班日期")
    duty_type: str = Field(..., description="值班类型")
    shift_type: str = Field(..., description="班次类型")
    remarks: Optional[str] = Field(None, description="备注")


 