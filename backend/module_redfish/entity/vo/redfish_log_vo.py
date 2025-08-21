"""
Redfish日志视图对象(VO)
"""
from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field, validator
from utils.page_util import PageResponseModel


class RedfishLogQueryModel(BaseModel):
    """日志查询模型"""
    device_id: Optional[int] = Field(None, description="设备ID")
    device_ip: Optional[str] = Field(None, description="设备IP地址")
    log_source: Optional[str] = Field(None, description="日志来源(SEL/MEL/all)")
    severity: Optional[str] = Field(None, description="严重程度(CRITICAL/WARNING/all)")
    message_keyword: Optional[str] = Field(None, description="消息关键词")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    
    # 分页参数
    page_num: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")
    
    @validator('log_source')
    def validate_log_source(cls, v):
        if v and v not in ['SEL', 'MEL', 'all']:
            raise ValueError('日志来源必须是SEL、MEL或all')
        return v
    
    @validator('severity')
    def validate_severity(cls, v):
        if v:
            # 转换为大写并验证（除了'all'）
            if str(v).lower() == 'all':
                return 'all'
            v_upper = str(v).upper()
            if v_upper not in ['CRITICAL', 'WARNING']:
                raise ValueError('严重程度必须是CRITICAL、WARNING或all')
            return v_upper
        return v
    
    @classmethod
    def as_query(cls, 
                 device_id: Optional[int] = None,
                 device_ip: Optional[str] = None,
                 log_source: Optional[str] = None,
                 severity: Optional[str] = None,
                 message_keyword: Optional[str] = None,
                 start_time: Optional[str] = None,
                 end_time: Optional[str] = None,
                 page_num: int = 1,
                 page_size: int = 10):
        """作为查询参数使用"""
        # 转换时间字符串
        start_datetime = None
        end_datetime = None
        
        if start_time:
            try:
                start_datetime = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            except:
                pass
                
        if end_time:
            try:
                end_datetime = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            except:
                pass
        
        return cls(
            device_id=device_id,
            device_ip=device_ip,
            log_source=log_source,
            severity=severity,
            message_keyword=message_keyword,
            start_time=start_datetime,
            end_time=end_datetime,
            page_num=page_num,
            page_size=page_size
        )


class RedfishLogModel(BaseModel):
    """日志基本模型"""
    log_id: str = Field(..., description="日志ID")
    device_id: int = Field(..., description="设备ID")
    device_ip: str = Field(..., description="设备IP地址")
    entry_id: Optional[str] = Field(None, description="原始条目ID")
    entry_type: Optional[str] = Field(None, description="条目类型")
    log_source: str = Field(..., description="日志来源")
    severity: str = Field(..., description="严重程度")
    created_time: datetime = Field(..., description="日志创建时间")
    collected_time: datetime = Field(..., description="日志收集时间")
    message: Optional[str] = Field(None, description="日志消息")
    message_id: Optional[str] = Field(None, description="消息ID")
    sensor_type: Optional[str] = Field(None, description="传感器类型")
    sensor_number: Optional[int] = Field(None, description="传感器编号")
    remark: Optional[str] = Field(None, description="备注")


class RedfishLogDetailModel(RedfishLogModel):
    """日志详细信息模型"""
    create_by: Optional[str] = Field(None, description="创建者")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_by: Optional[str] = Field(None, description="更新者")
    update_time: Optional[datetime] = Field(None, description="更新时间")


class AddRedfishLogModel(BaseModel):
    """添加日志模型"""
    device_id: int = Field(..., description="设备ID")
    device_ip: str = Field(..., description="设备IP地址")
    entry_id: Optional[str] = Field(None, description="原始条目ID")
    entry_type: Optional[str] = Field(None, description="条目类型")
    log_source: str = Field(..., description="日志来源")
    severity: str = Field(..., description="严重程度")
    created_time: datetime = Field(..., description="日志创建时间")
    message: Optional[str] = Field(None, description="日志消息")
    message_id: Optional[str] = Field(None, description="消息ID")
    sensor_type: Optional[str] = Field(None, description="传感器类型")
    sensor_number: Optional[int] = Field(None, description="传感器编号")
    remark: Optional[str] = Field(None, description="备注")
    
    # 系统字段
    create_by: Optional[str] = Field(None, description="创建者")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    
    @validator('log_source')
    def validate_log_source(cls, v):
        if v not in ['SEL', 'MEL']:
            raise ValueError('日志来源必须是SEL或MEL')
        return v
    
    @validator('severity')
    def validate_severity(cls, v):
        if v:
            # 转换为大写并验证
            v_upper = str(v).upper()
            if v_upper not in ['CRITICAL', 'WARNING']:
                raise ValueError('严重程度必须是CRITICAL或WARNING')
            return v_upper
        return v


class RedfishLogStatsModel(BaseModel):
    """日志统计模型"""
    total_count: int = Field(0, description="总数量")
    critical_count: int = Field(0, description="严重错误数量")
    warning_count: int = Field(0, description="警告数量")
    sel_count: int = Field(0, description="SEL日志数量")
    mel_count: int = Field(0, description="MEL日志数量")
    today_count: int = Field(0, description="今日日志数量")
    recent_7days_count: int = Field(0, description="近7天日志数量")


class DeviceLogCollectModel(BaseModel):
    """设备日志收集模型"""
    device_id: Optional[int] = Field(None, description="设备ID，为空则收集所有设备")
    log_type: str = Field("all", description="日志类型(sel/mel/all)")
    max_entries: int = Field(100, ge=1, le=1000, description="最大条目数")
    force_refresh: bool = Field(False, description="是否强制刷新")
    
    @validator('log_type')
    def validate_log_type(cls, v):
        if v not in ['sel', 'mel', 'all']:
            raise ValueError('日志类型必须是sel、mel或all')
        return v


class RedfishLogPageQueryModel(RedfishLogQueryModel):
    """分页查询模型"""
    pass


class RedfishLogPageResponseModel(PageResponseModel):
    """日志分页响应模型"""
    rows: List[RedfishLogModel] = Field([], description="日志列表")


class RedfishLogCollectResultModel(BaseModel):
    """日志收集结果模型"""
    success: bool = Field(..., description="是否成功")
    device_count: int = Field(0, description="收集设备数量")
    total_collected: int = Field(0, description="总收集数量")
    critical_collected: int = Field(0, description="严重错误收集数量")
    warning_collected: int = Field(0, description="警告收集数量")
    failed_devices: List[str] = Field([], description="收集失败的设备IP")
    message: str = Field("", description="结果消息")


class RedfishLogCleanupResultModel(BaseModel):
    """日志清理结果模型"""
    success: bool = Field(..., description="是否成功")
    cleaned_count: int = Field(0, description="清理数量")
    before_date: datetime = Field(..., description="清理日期之前")
    message: str = Field("", description="结果消息")
