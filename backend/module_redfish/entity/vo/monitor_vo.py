"""
监控任务管理VO模型
"""
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class MonitorTaskModel(BaseModel):
    """监控任务模型"""
    task_id: str = Field(..., description="任务ID")
    task_name: str = Field(..., description="任务名称")
    task_type: str = Field(..., description="任务类型(device_monitor/batch_monitor)")
    device_id: Optional[int] = Field(default=None, description="设备ID(单设备监控)")
    device_count: Optional[int] = Field(default=None, description="设备数量(批量监控)")
    status: str = Field(..., description="任务状态(pending/running/success/failure/revoked)")
    progress: int = Field(default=0, description="进度百分比")
    start_time: Optional[datetime] = Field(default=None, description="开始时间")
    end_time: Optional[datetime] = Field(default=None, description="结束时间")
    duration: Optional[float] = Field(default=None, description="执行时长(秒)")
    result: Optional[dict] = Field(default=None, description="执行结果")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    created_by: str = Field(..., description="创建者")
    created_time: datetime = Field(..., description="创建时间")


class MonitorTaskQueryModel(BaseModel):
    """监控任务查询模型"""
    task_type: Optional[str] = Field(default=None, description="任务类型")
    status: Optional[str] = Field(default=None, description="任务状态")
    device_id: Optional[int] = Field(default=None, description="设备ID")
    created_by: Optional[str] = Field(default=None, description="创建者")
    start_date: Optional[datetime] = Field(default=None, description="开始日期")
    end_date: Optional[datetime] = Field(default=None, description="结束日期")
    limit: int = Field(default=50, description="返回数量限制")


class TriggerMonitorModel(BaseModel):
    """触发监控模型"""
    device_ids: Optional[List[int]] = Field(default=None, description="设备ID列表(为空则监控所有设备)")
    force_refresh: bool = Field(default=False, description="是否强制刷新")
    priority: str = Field(default="normal", description="优先级(low/normal/high)")
    created_by: str = Field(..., description="创建者")


class MonitorResultModel(BaseModel):
    """监控结果模型"""
    device_id: int = Field(..., description="设备ID")
    hostname: str = Field(..., description="主机名")
    business_ip: str = Field(..., description="业务IP")
    connection_success: bool = Field(..., description="连接是否成功")
    monitoring_success: bool = Field(..., description="监控是否成功")
    health_status: str = Field(..., description="健康状态")
    component_results: Dict[str, dict] = Field(..., description="组件监控结果")
    alerts_generated: int = Field(..., description="生成的告警数")
    execution_time: float = Field(..., description="执行时间(秒)")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    check_time: datetime = Field(..., description="检查时间")


class MonitorStatisticsModel(BaseModel):
    """监控统计模型"""
    total_tasks: int = Field(..., description="总任务数")
    running_tasks: int = Field(..., description="运行中任务数")
    pending_tasks: int = Field(..., description="等待中任务数")
    success_tasks: int = Field(..., description="成功任务数")
    failed_tasks: int = Field(..., description="失败任务数")
    
    total_devices: int = Field(..., description="总设备数")
    monitored_devices: int = Field(..., description="已监控设备数")
    failed_devices: int = Field(..., description="监控失败设备数")
    
    avg_execution_time: float = Field(..., description="平均执行时间(秒)")
    success_rate: float = Field(..., description="成功率")
    
    last_batch_time: Optional[datetime] = Field(default=None, description="最后批量监控时间")
    next_scheduled_time: Optional[datetime] = Field(default=None, description="下次计划监控时间")


class CeleryWorkerModel(BaseModel):
    """Celery工作节点模型"""
    worker_name: str = Field(..., description="工作节点名称")
    status: str = Field(..., description="状态(online/offline)")
    active_tasks: int = Field(..., description="活跃任务数")
    processed_tasks: int = Field(..., description="已处理任务数")
    load_average: List[float] = Field(..., description="负载平均值")
    last_heartbeat: datetime = Field(..., description="最后心跳时间")


class CeleryQueueModel(BaseModel):
    """Celery队列模型"""
    queue_name: str = Field(..., description="队列名称")
    pending_tasks: int = Field(..., description="等待任务数")
    active_tasks: int = Field(..., description="活跃任务数")
    reserved_tasks: int = Field(..., description="保留任务数")


class MonitorSystemStatusModel(BaseModel):
    """监控系统状态模型"""
    celery_status: str = Field(..., description="Celery状态(running/stopped/error)")
    redis_status: str = Field(..., description="Redis状态(connected/disconnected)")
    database_status: str = Field(..., description="数据库状态(connected/disconnected)")
    
    workers: List[CeleryWorkerModel] = Field(..., description="工作节点列表")
    queues: List[CeleryQueueModel] = Field(..., description="队列列表")
    
    system_load: Dict[str, float] = Field(..., description="系统负载")
    memory_usage: Dict[str, float] = Field(..., description="内存使用情况")
    
    last_check_time: datetime = Field(..., description="最后检查时间")


class MonitorConfigModel(BaseModel):
    """监控配置模型"""
    global_monitoring_enabled: bool = Field(..., description="全局监控是否启用")
    default_monitoring_interval: int = Field(..., description="默认监控间隔(秒)")
    batch_size: int = Field(..., description="批量监控批次大小")
    max_concurrent_tasks: int = Field(..., description="最大并发任务数")
    task_timeout: int = Field(..., description="任务超时时间(秒)")
    retry_attempts: int = Field(..., description="重试次数")
    alert_threshold: Dict[str, int] = Field(..., description="告警阈值配置")
    
    # 调度配置
    scheduled_monitoring_enabled: bool = Field(..., description="计划监控是否启用")
    schedule_cron: str = Field(..., description="调度Cron表达式")
    
    last_updated_by: str = Field(..., description="最后更新者")
    last_updated_time: datetime = Field(..., description="最后更新时间")


class UpdateMonitorConfigModel(BaseModel):
    """更新监控配置模型"""
    global_monitoring_enabled: Optional[bool] = Field(default=None, description="全局监控是否启用")
    default_monitoring_interval: Optional[int] = Field(default=None, description="默认监控间隔(秒)")
    batch_size: Optional[int] = Field(default=None, description="批量监控批次大小")
    max_concurrent_tasks: Optional[int] = Field(default=None, description="最大并发任务数")
    task_timeout: Optional[int] = Field(default=None, description="任务超时时间(秒)")
    retry_attempts: Optional[int] = Field(default=None, description="重试次数")
    alert_threshold: Optional[Dict[str, int]] = Field(default=None, description="告警阈值配置")
    
    scheduled_monitoring_enabled: Optional[bool] = Field(default=None, description="计划监控是否启用")
    schedule_cron: Optional[str] = Field(default=None, description="调度Cron表达式")
    
    updated_by: str = Field(..., description="更新者")


class TaskOperationModel(BaseModel):
    """任务操作模型"""
    task_ids: List[str] = Field(..., description="任务ID列表")
    operation: str = Field(..., description="操作类型(cancel/retry/delete)")
    operator: str = Field(..., description="操作者")
    reason: Optional[str] = Field(default=None, description="操作原因") 