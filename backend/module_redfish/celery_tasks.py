"""
Celery异步任务模块
用于处理大规模设备监控任务
"""
import asyncio
from typing import Dict, List, Any
from datetime import datetime, timedelta
from celery import Celery, group
from celery.result import GroupResult
from loguru import logger
from sqlalchemy.orm import Session

from .device_monitor import DeviceMonitor
from ..module_admin.database import get_db
from .models import DeviceInfo, AlertInfo, RedfishAlertLog, BusinessHardwareUrgencyRules


# Celery应用配置
celery_app = Celery(
    'redfish_monitor',
    broker='redis://localhost:6379/1',  # 使用Redis作为消息代理
    backend='redis://localhost:6379/2'  # 使用Redis作为结果后端
)

# Celery配置
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5分钟超时
    task_soft_time_limit=240,  # 4分钟软超时
    worker_prefetch_multiplier=1,  # 防止任务堆积
    worker_max_tasks_per_child=1000,  # 防止内存泄漏
    result_expires=3600,  # 结果保存1小时
)


@celery_app.task(bind=True, name='monitor_single_device')
def monitor_single_device(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    监控单个设备的异步任务
    
    Args:
        device_info: 设备信息字典
        
    Returns:
        Dict: 监控结果
    """
    try:
        logger.info(f"Starting monitoring task for device: {device_info.get('hostname', 'Unknown')}")
        
        # 创建设备监控器
        monitor = DeviceMonitor()
        
        # 执行异步监控（在同步任务中运行异步代码）
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(monitor.monitor_device(device_info))
        finally:
            loop.close()
        
        # 保存监控结果到数据库
        if result['success']:
            save_monitoring_result(result, device_info)
        
        logger.info(f"Completed monitoring task for device: {device_info.get('hostname', 'Unknown')}")
        return result
        
    except Exception as e:
        logger.error(f"Error in monitoring task for device {device_info.get('hostname', 'Unknown')}: {str(e)}")
        self.retry(countdown=60, max_retries=3)  # 1分钟后重试，最多3次


@celery_app.task(name='monitor_all_devices')
def monitor_all_devices() -> Dict[str, Any]:
    """
    监控所有启用的设备
    
    Returns:
        Dict: 批量监控结果
    """
    try:
        logger.info("Starting batch monitoring task for all devices")
        
        # 获取数据库会话
        db = next(get_db())
        
        # 查询所有启用监控的设备
        devices = db.query(DeviceInfo).filter(
            DeviceInfo.monitor_enabled == 1
        ).all()
        
        if not devices:
            logger.warning("No devices found for monitoring")
            return {
                "success": True,
                "message": "No devices to monitor",
                "total_devices": 0,
                "results": []
            }
        
        logger.info(f"Found {len(devices)} devices to monitor")
        
        # 将设备信息转换为字典格式
        device_list = []
        for device in devices:
            device_dict = {
                "device_id": device.device_id,
                "hostname": device.hostname,
                "business_ip": device.business_ip,
                "oob_ip": device.oob_ip,
                "oob_port": device.oob_port,
                "business_type": device.business_type,
                "redfish_username": device.redfish_username,
                "redfish_password": device.redfish_password,
                "manufacturer": device.manufacturer,
                "model": device.model
            }
            device_list.append(device_dict)
        
        # 创建并发任务组
        job = group(monitor_single_device.s(device) for device in device_list)
        result = job.apply_async()
        
        # 等待所有任务完成（设置超时时间）
        results = result.get(timeout=600)  # 10分钟超时
        
        # 统计结果
        success_count = sum(1 for r in results if r.get('success', False))
        failed_count = len(results) - success_count
        
        logger.info(f"Batch monitoring completed: {success_count} success, {failed_count} failed")
        
        return {
            "success": True,
            "message": f"Monitoring completed for {len(devices)} devices",
            "total_devices": len(devices),
            "success_count": success_count,
            "failed_count": failed_count,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in batch monitoring task: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@celery_app.task(name='cleanup_old_logs')
def cleanup_old_logs(days: int = 30) -> Dict[str, Any]:
    """
    清理旧的日志记录
    
    Args:
        days: 保留天数，默认30天
        
    Returns:
        Dict: 清理结果
    """
    try:
        logger.info(f"Starting cleanup task for logs older than {days} days")
        
        # 获取数据库会话
        db = next(get_db())
        
        # 计算截止时间
        cutoff_time = datetime.now() - timedelta(days=days)
        
        # 删除旧的日志记录
        deleted_logs = db.query(RedfishAlertLog).filter(
            RedfishAlertLog.occurrence_time < cutoff_time
        ).delete()
        
        # 删除已解决的旧告警记录
        deleted_alerts = db.query(AlertInfo).filter(
            AlertInfo.resolved_time < cutoff_time,
            AlertInfo.alert_status.in_(['resolved', 'closed'])
        ).delete()
        
        db.commit()
        
        logger.info(f"Cleanup completed: {deleted_logs} logs, {deleted_alerts} alerts deleted")
        
        return {
            "success": True,
            "deleted_logs": deleted_logs,
            "deleted_alerts": deleted_alerts,
            "cutoff_time": cutoff_time.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup task: {str(e)}")
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }


def save_monitoring_result(result: Dict[str, Any], device_info: Dict[str, Any]):
    """
    保存监控结果到数据库
    
    Args:
        result: 监控结果
        device_info: 设备信息
    """
    try:
        # 获取数据库会话
        db = next(get_db())
        
        device_id = result['device_id']
        
        # 更新设备状态
        device = db.query(DeviceInfo).filter(DeviceInfo.device_id == device_id).first()
        if device:
            device.last_check_time = datetime.now()
            device.health_status = result.get('overall_health', 'unknown')
        
        # 保存告警信息
        for alert in result.get('alerts', []):
            # 检查是否已存在相同的活跃告警
            existing_alert = db.query(AlertInfo).filter(
                AlertInfo.device_id == device_id,
                AlertInfo.component_type == alert['component_type'],
                AlertInfo.component_name == alert['component_name'],
                AlertInfo.alert_status == 'active'
            ).first()
            
            if existing_alert:
                # 更新现有告警
                existing_alert.last_occurrence = datetime.now()
                existing_alert.occurrence_count += 1
                existing_alert.raw_data = alert['raw_data']
            else:
                # 创建新告警
                # 根据业务规则确定告警类型
                alert_type = determine_alert_type(db, device_info['business_type'], alert['component_type'])
                
                new_alert = AlertInfo(
                    device_id=device_id,
                    alert_source=alert['alert_source'],
                    component_type=alert['component_type'],
                    component_name=alert['component_name'],
                    alert_level=alert['alert_level'],
                    alert_type=alert_type,
                    alert_type_original=alert_type,
                    alert_message=alert['alert_message'],
                    first_occurrence=alert['first_occurrence'],
                    last_occurrence=alert['first_occurrence'],
                    raw_data=alert['raw_data']
                )
                db.add(new_alert)
        
        # 保存日志记录
        for log in result.get('logs', []):
            new_log = RedfishAlertLog(
                device_id=device_id,
                log_source='redfish',
                component_type=log['component_type'],
                component_name=log['component_name'],
                log_level=log['log_level'],
                log_message=log['log_message'],
                raw_data=log['raw_data'],
                occurrence_time=log['occurrence_time']
            )
            db.add(new_log)
        
        db.commit()
        logger.info(f"Saved monitoring result for device {device_id}")
        
    except Exception as e:
        logger.error(f"Error saving monitoring result: {str(e)}")
        db.rollback()


def determine_alert_type(db: Session, business_type: str, hardware_type: str) -> str:
    """
    根据业务规则确定告警类型
    
    Args:
        db: 数据库会话
        business_type: 业务类型
        hardware_type: 硬件类型
        
    Returns:
        str: 告警类型（urgent/scheduled）
    """
    try:
        # 查询匹配的规则
        rule = db.query(BusinessHardwareUrgencyRules).filter(
            BusinessHardwareUrgencyRules.business_type == business_type,
            BusinessHardwareUrgencyRules.hardware_type == hardware_type.upper(),
            BusinessHardwareUrgencyRules.is_active == 1
        ).first()
        
        if rule:
            return rule.urgency_level
        
        # 如果没有找到具体规则，使用默认规则
        # CPU和内存故障通常比较紧急
        if hardware_type in ['cpu', 'memory']:
            return 'urgent'
        else:
            return 'scheduled'
            
    except Exception as e:
        logger.error(f"Error determining alert type: {str(e)}")
        return 'scheduled'  # 默认返回择期


# Celery定时任务配置
celery_app.conf.beat_schedule = {
    # 每5分钟执行一次全设备监控
    'monitor-all-devices': {
        'task': 'monitor_all_devices',
        'schedule': 300.0,  # 5分钟
    },
    # 每天凌晨2点清理旧日志
    'cleanup-old-logs': {
        'task': 'cleanup_old_logs',
        'schedule': 7200.0,  # 2小时执行一次清理检查
        'kwargs': {'days': 30}
    },
} 