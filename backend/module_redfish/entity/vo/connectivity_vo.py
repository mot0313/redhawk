"""
设备连通性VO模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from module_admin.annotation.pydantic_annotation import as_query


@as_query
class ConnectivityStatsQueryModel(BaseModel):
    """连通性统计查询参数模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    use_cache: bool = Field(default=True, description="是否使用缓存")
    cache_ttl_minutes: int = Field(default=5, ge=1, le=60, description="缓存时间（分钟）")


@as_query
class BatchCheckQueryModel(BaseModel):
    """批量检测查询参数模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    max_concurrent: int = Field(default=20, ge=1, le=50, description="最大并发数")


class ConnectivityResultModel(BaseModel):
    """连通性检测结果模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    device_id: Optional[int] = Field(default=None, description="设备ID")
    hostname: Optional[str] = Field(default=None, description="主机名")
    business_ip: Optional[str] = Field(default=None, description="业务IP")
    location: Optional[str] = Field(default=None, description="位置")
    online: bool = Field(..., description="是否在线")
    check_time: Optional[str] = Field(default=None, description="检测时间")
    check_details: Optional[Dict[str, Any]] = Field(default=None, description="检测详情")
    error_message: Optional[str] = Field(default=None, description="错误信息")


class ConnectivityStatsResponseModel(BaseModel):
    """连通性统计响应模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    total_devices: int = Field(..., description="总设备数")
    online_devices: int = Field(..., description="在线设备数")
    offline_devices: int = Field(..., description="离线设备数")
    check_duration_ms: float = Field(..., description="检测耗时（毫秒）")
    check_time: str = Field(..., description="检测时间")
    details: List[ConnectivityResultModel] = Field(default_factory=list, description="详细结果")
    error: Optional[str] = Field(default=None, description="错误信息")
    
    @classmethod
    def from_service_result(cls, service_result: Dict[str, Any]) -> "ConnectivityStatsResponseModel":
        """从服务层结果转换为响应模型"""
        details = []
        for detail in service_result.get("details", []):
            details.append(ConnectivityResultModel(
                device_id=detail.get("device_id"),
                hostname=detail.get("hostname"),
                business_ip=detail.get("business_ip"),
                location=detail.get("location"),
                online=detail.get("online", False),
                check_time=detail.get("check_time"),
                check_details=detail.get("check_details"),
                error_message=detail.get("error_message")
            ))
        
        return cls(
            total_devices=service_result.get("total_devices", 0),
            online_devices=service_result.get("online_devices", 0),
            offline_devices=service_result.get("offline_devices", 0),
            check_duration_ms=service_result.get("check_duration_ms", 0),
            check_time=service_result.get("check_time", ""),
            details=details,
            error=service_result.get("error")
        )


class SingleDeviceConnectivityResponseModel(BaseModel):
    """单设备连通性检测响应模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    device_id: Optional[int] = Field(default=None, description="设备ID")
    hostname: Optional[str] = Field(default=None, description="主机名")
    business_ip: Optional[str] = Field(default=None, description="业务IP")
    online: bool = Field(..., description="是否在线")
    check_time: str = Field(..., description="检测时间")
    check_details: Optional[Dict[str, Any]] = Field(default=None, description="检测详情")
    error: Optional[str] = Field(default=None, description="错误信息")
    
    @classmethod
    def from_service_result(cls, service_result: Dict[str, Any]) -> "SingleDeviceConnectivityResponseModel":
        """从服务层结果转换为响应模型"""
        return cls(
            device_id=service_result.get("device_id"),
            hostname=service_result.get("hostname"),
            business_ip=service_result.get("business_ip"),
            online=service_result.get("online", False),
            check_time=service_result.get("check_time", ""),
            check_details=service_result.get("check_details"),
            error=service_result.get("error")
        )


class IpConnectivityQueryModel(BaseModel):
    """IP连通性检测查询模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    business_ip: str = Field(..., description="业务IP地址") 