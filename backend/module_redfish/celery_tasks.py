"""
Celery异步任务模块
用于处理大规模设备监控任务，支持WebSocket实时推送
"""
import asyncio
from typing import Dict, List, Any
from datetime import datetime, timedelta
from celery import Celery, group
from celery.result import GroupResult
from loguru import logger
from celery.schedules import crontab
# from sqlalchemy.orm import Session  # 不再需要，使用config.get_db中的session
import redis
import json

from .core.device_monitor import DeviceMonitor
from .core.availability_monitor import DeviceAvailabilityMonitor
from config.get_db import get_sync_db
from .entity.do import DeviceInfoDO, AlertInfoDO, BusinessHardwareUrgencyRulesDO
from .core.realtime_service import PushServiceManager
from .utils.component_type_mapper import to_hardware_code

# 导入统一的Celery配置
from .celery_config import celery_app

# 确保推送服务正确初始化
push_service = PushServiceManager()

# Redis配置，用于同步发布消息
from config.env import RedisConfig


# ===============================================================
# 同步的Redis消息发布工具
# ===============================================================
def check_batch_completion(batch_id: str, task_success: bool = True):
    """
    检查批次任务是否全部完成
    
    Args:
        batch_id: 批次ID
        task_success: 当前任务是否成功
    """
    try:
        from config.get_redis import get_redis
        redis_client = get_redis()
        
        counter_key = f"monitoring_batch:{batch_id}:counter"
        total_key = f"monitoring_batch:{batch_id}:total"
        success_key = f"monitoring_batch:{batch_id}:success"
        failed_key = f"monitoring_batch:{batch_id}:failed"
        
        # 原子性增加计数器
        current_count = redis_client.incr(counter_key)
        total_count = int(redis_client.get(total_key) or 0)
        
        # 更新成功/失败计数器
        if task_success:
            redis_client.incr(success_key)
        else:
            redis_client.incr(failed_key)
        
        logger.info(f"Batch {batch_id}: {current_count}/{total_count} tasks completed")
        
        # 推送监控进度更新（每次任务完成都推送）
        if current_count < total_count:
            progress_percentage = round((current_count / total_count) * 100, 2) if total_count > 0 else 0
            progress_message = {
                "type": "monitoring_progress",
                "action": "progress_update",
                "completed": current_count,
                "total": total_count,
                "progress": progress_percentage,
                "current_device": f"已完成 {current_count} 台设备",
                "timestamp": datetime.now().isoformat()
            }
            
            # 推送进度更新
            publish_sync_redis_message("websocket:dashboard", progress_message)
            logger.debug(f"Pushed monitoring progress: {current_count}/{total_count} ({progress_percentage}%)")
        
        # 如果所有任务都完成了，发送完成通知
        if current_count >= total_count:
            logger.info(f"All monitoring tasks completed for batch {batch_id}")
            
            # 先推送100%进度
            final_progress_message = {
                "type": "monitoring_progress",
                "action": "progress_update",
                "completed": total_count,
                "total": total_count,
                "progress": 100.0,
                "current_device": f"所有 {total_count} 台设备监控完成",
                "timestamp": datetime.now().isoformat()
            }
            
            publish_sync_redis_message("websocket:dashboard", final_progress_message)
            logger.debug(f"Pushed final monitoring progress: {total_count}/{total_count} (100%)")
            
            # 获取成功和失败统计
            successful_devices = int(redis_client.get(success_key) or 0)
            failed_devices = int(redis_client.get(failed_key) or 0)
            
            # 推送监控完成通知
            message = {
                "type": "monitoring_completed",
                "action": "monitoring_completed",
                "results": {
                    "success": True,
                    "message": f"Monitoring completed for {total_count} devices",
                    "total_devices": total_count,
                    "successful_devices": successful_devices,
                    "failed_devices": failed_devices,
                    "batch_id": batch_id,
                    "timestamp": datetime.now().isoformat()
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # 使用同步Redis发布（只发送到dashboard频道，避免重复）
            publish_sync_redis_message("websocket:dashboard", message)
            
            logger.info(f"Pushed monitoring completed notification: {total_count} devices ({successful_devices} success, {failed_devices} failed)")
            
            # 监控完成后清除设备状态缓存，确保下次请求获取最新数据
            try:
                from module_admin.service.cache_service import CacheService
                import asyncio
                
                # 在同步任务中运行异步代码
                async def clear_cache():
                    await CacheService.delete_cache("connectivity_stats")
                    logger.info("Monitoring completed: device status cache cleared")
                
                # 运行异步缓存清理
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(clear_cache())
                finally:
                    loop.close()
                    
            except Exception as e:
                logger.warning(f"Failed to clear device status cache after monitoring: {str(e)}")
            
            # 清理Redis计数器
            redis_client.delete(counter_key, total_key, success_key, failed_key)
            
    except Exception as e:
        logger.error(f"Error checking batch completion for {batch_id}: {str(e)}")


def publish_sync_redis_message(channel: str, message: dict):
    """
    一个同步的函数，用于从Celery任务中向Redis发布消息。
    """
    try:
        r = redis.Redis(
            host=RedisConfig.redis_host,
            port=RedisConfig.redis_port,
            username=RedisConfig.redis_username,
            password=RedisConfig.redis_password,
            db=RedisConfig.redis_database,
            decode_responses=True
        )
        r.publish(channel, json.dumps(message, ensure_ascii=False))
        logger.info(f"Successfully published message to Redis channel '{channel}'")
        r.close()
    except Exception as e:
        logger.error(f"Failed to publish message to Redis channel '{channel}': {e}")


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
            
            # 推送监控结果到WebSocket客户端
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(push_service.realtime.push_device_status_change(
                    device_id=result.get('device_id'),
                    old_status='unknown',
                    new_status=result.get('overall_health', 'unknown'),
                    device_info=device_info
                ))
            except RuntimeError:
                # 如果没有运行的事件循环，跳过推送
                logger.warning("No event loop running, skipping WebSocket push")
        
        logger.info(f"Completed monitoring task for device: {device_info.get('hostname', 'Unknown')}")
        
        # 检查是否是批次任务，如果是则更新计数器
        batch_id = device_info.get('batch_id')
        if batch_id:
            check_batch_completion(batch_id, result['success'])
        
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
        db = next(get_sync_db())
        
        # 查询所有启用监控的设备
        devices = db.query(DeviceInfoDO).filter(
            DeviceInfoDO.monitor_enabled == 1
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
        
        # 生成批次ID
        import uuid
        batch_id = str(uuid.uuid4())
        
        # 在Redis中设置计数器，用于跟踪任务完成情况
        from config.get_redis import get_redis
        redis_client = get_redis()
        counter_key = f"monitoring_batch:{batch_id}:counter"
        total_key = f"monitoring_batch:{batch_id}:total"
        success_key = f"monitoring_batch:{batch_id}:success"
        failed_key = f"monitoring_batch:{batch_id}:failed"
        
        # 设置总任务数和当前完成数
        redis_client.set(total_key, len(devices), ex=3600)  # 1小时过期
        redis_client.set(counter_key, 0, ex=3600)
        redis_client.set(success_key, 0, ex=3600)
        redis_client.set(failed_key, 0, ex=3600)
        
        # 创建任务组，为每个任务传递batch_id
        enhanced_device_list = []
        for device in device_list:
            enhanced_device = device.copy()
            enhanced_device['batch_id'] = batch_id
            enhanced_device_list.append(enhanced_device)
        
        job = group(monitor_single_device.s(device) for device in enhanced_device_list)
        result = job.apply_async()
        
        logger.info(f"Submitted {len(devices)} monitoring tasks, batch ID: {batch_id}")
        
        # 创建任务提交的结果
        batch_result = {
            "success": True,
            "message": f"Monitoring tasks submitted for {len(devices)} devices",
            "total_devices": len(devices),
            "batch_id": batch_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # 推送批量监控开始通知
        try:
            # 发送WebSocket通知，通知前端监控已开始
            message = {
                "type": "monitoring_started",
                "action": "monitoring_started", 
                "results": batch_result,
                "timestamp": datetime.now().isoformat()
            }
            
            # 使用同步Redis发布，因为这是在同步任务中（只发送到dashboard频道，避免重复）
            publish_sync_redis_message("websocket:dashboard", message)
            
            logger.info(f"Pushed monitoring started notification: {len(devices)} devices")
            
            # 推送初始进度状态（0%）
            initial_progress_message = {
                "type": "monitoring_progress",
                "action": "progress_update",
                "completed": 0,
                "total": len(devices),
                "progress": 0.0,
                "current_device": "开始监控...",
                "timestamp": datetime.now().isoformat()
            }
            
            publish_sync_redis_message("websocket:dashboard", initial_progress_message)
            logger.debug(f"Pushed initial monitoring progress: 0/{len(devices)} (0%)")
            
        except Exception as e:
            logger.error(f"Error pushing monitoring started notification: {str(e)}")
        
        return batch_result
        
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
    清理旧的日志和告警记录
    
    Args:
        days (int): 清理多少天前的记录，默认30天
        
    Returns:
        Dict: 清理结果
    """
    try:
        logger.info(f"Starting cleanup task for records older than {days} days")
        db = next(get_sync_db())
        
        cutoff_time = datetime.now() - timedelta(days=days)
        
        # 1. 清理已解决的告警 (alert_info)
        # 只删除在截止日期前已解决（status='resolved'）且更新时间早于截止时间的告警
        deleted_alerts_count = db.query(AlertInfoDO).filter(
            AlertInfoDO.status == 'resolved',
            AlertInfoDO.update_time < cutoff_time
        ).delete(synchronize_session=False)
        
        db.commit()
        
        logger.info(f"Successfully deleted {deleted_alerts_count} resolved alerts older than {cutoff_time}")
        
        return {
            "success": True,
            "message": "Cleanup task completed successfully",
            "deleted_alerts": deleted_alerts_count,
        }
        
    except Exception as e:
        logger.error(f"Error during cleanup task: {str(e)}")
        db.rollback()
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "deleted_alerts": 0,
        }
    finally:
        db.close()


def save_monitoring_result(result: Dict[str, Any], device_info: Dict[str, Any]):
    """
    保存监控结果到数据库，并实现告警生命周期管理
    
    Args:
        result: 监控结果，包含 'alerts' 和 'all_components'
        device_info: 设备信息
    """
    db = next(get_sync_db())
    try:
        device_id = result['device_id']
        business_type = device_info.get('business_type', '')
        
        # 1. 批量获取数据
        # 获取此设备所有现有 active 告警
        active_alerts_query = db.query(AlertInfoDO).filter(
            AlertInfoDO.device_id == device_id,
            AlertInfoDO.alert_status == 'active'
        ).all()
        active_alerts_map = {(alert.component_type, alert.component_name): alert for alert in active_alerts_query}
        
        # 获取所有紧急度规则
        rules_query = db.query(BusinessHardwareUrgencyRulesDO).filter(BusinessHardwareUrgencyRulesDO.is_active == 1).all()
        urgency_rules_map = {(rule.business_type, rule.hardware_type.lower()): rule.urgency_level for rule in rules_query}

        # 获取设备当前状态
        device = db.query(DeviceInfoDO).filter(DeviceInfoDO.device_id == device_id).first()
        if not device:
            logger.error(f"Device with id {device_id} not found in database.")
            return
            
        old_health_status = device.health_status
        device.last_check_time = datetime.now()
        device.health_status = result.get('overall_health', 'unknown')
        new_health_status = device.health_status

        # 2. 状态对比与逻辑处理
        all_monitored_components = result.get('all_components', [])
        # 统一将内部 component_type 转为硬件字典码（小写）
        normalized_components = []
        for comp in all_monitored_components:
            ct = to_hardware_code(comp.get('component_type'), comp)
            nc = comp.copy()
            nc['component_type'] = ct
            normalized_components.append(nc)
        monitored_components_map = {(comp['component_type'], comp['component_name']): comp for comp in normalized_components}

        # 监控统计日志：记录各类型异常数量（帮助定位如memory未入库问题）
        try:
            type_bad_counts = {}
            for c in normalized_components:
                if c.get('health_status') != 'ok':
                    key = c.get('component_type') or 'unknown'
                    type_bad_counts[key] = type_bad_counts.get(key, 0) + 1
            logger.info(f"Monitored abnormal components by type: {type_bad_counts}")
        except Exception:
            pass
        
        alerts_to_create = []
        alerts_to_resolve = []
        
        # 遍历当前监控到的所有组件
        for (component_type, component_name), component_data in monitored_components_map.items():
            health_status = component_data['health_status']
            alert_key = (component_type, component_name)
            
            existing_alert = active_alerts_map.get(alert_key)
            
            if health_status != 'ok':
                try:
                    logger.info(f"Evaluating alert create/update | type={component_type} name={component_name} health={health_status}")
                except Exception:
                    pass
                # 组件状态异常
                if not existing_alert:
                    # 情况1: 新告警
                    urgency_level = urgency_rules_map.get((business_type, component_type.lower()), 'scheduled')
                    
                    new_alert = AlertInfoDO(
                    device_id=device_id,
                    component_type=component_type,
                    component_name=component_name,
                    health_status=health_status,
                    urgency_level=urgency_level,
                    alert_status='active',
                        first_occurrence=datetime.now(),
                        last_occurrence=datetime.now()
                    )
                    alerts_to_create.append(new_alert)
                    logger.info(f"New alert for device {device_id}: {component_type}/{component_name} -> {health_status}, Urgency: {urgency_level}")
                else:
                    # 情况2: 持续的告警，更新最后发生时间
                    existing_alert.last_occurrence = datetime.now()
                    # 从map中移除，代表已处理
                    active_alerts_map.pop(alert_key)
            else:
                # 组件状态正常
                if existing_alert:
                    # 情况3: 已恢复的告警
                    existing_alert.alert_status = 'resolved'
                    existing_alert.resolved_time = datetime.now()
                    alerts_to_resolve.append(existing_alert)
                    logger.info(f"Alert resolved for device {device_id}: {component_type}/{component_name}")
                    # 从map中移除，代表已处理
                    active_alerts_map.pop(alert_key)

        # 3. 处理未在本次监控中出现的旧告警（可能由于组件被移除等原因）
        # for (component_type, component_name), alert in active_alerts_map.items():
        #     # 这些是数据库里有，但本次监控没返回的告警，也标记为解决
        #     alert.alert_status = 'resolved'
        #     alert.resolved_time = datetime.now()
        #     alerts_to_resolve.append(alert)
        #     logger.warning(f"Stale alert resolved for device {device_id}: {component_type}/{component_name} was not reported in this cycle.")

        # 4. 批量数据库操作
        if alerts_to_create:
            db.add_all(alerts_to_create)
        
        # 所有变更（包括 alets_to_resolve 和持续告警的更新）将通过一次 commit 完成
        db.commit()
        
        # 5. 准备并推送通知 (此部分可以进一步细化)
        # 此处简化处理，只对新告警和已解决告警推送
        new_alerts_data = [
            {
                "device_id": alert.device_id, "hostname": device.hostname, "component_type": alert.component_type,
                "component_name": alert.component_name, "health_status": alert.health_status, "urgency_level": alert.urgency_level,
                "action": "created"
            } for alert in alerts_to_create
        ]
        resolved_alerts_data = [
            {
                "device_id": alert.device_id, "hostname": device.hostname, "component_type": alert.component_type,
                "component_name": alert.component_name, "health_status": "ok", "urgency_level": alert.urgency_level,
                "action": "resolved"
            } for alert in alerts_to_resolve
        ]
        
        all_changes = new_alerts_data + resolved_alerts_data
        
        if old_health_status != new_health_status or all_changes:
            _schedule_push_notifications(device_info, old_health_status, new_health_status, all_changes)

        logger.info(f"Saved monitoring result for device {device_id}: {len(alerts_to_create)} new, {len(alerts_to_resolve)} resolved.")
        
    except Exception as e:
        logger.error(f"Error saving monitoring result for device {device_info.get('id', 'N/A')}: {str(e)}")
        if 'db' in locals():
            db.rollback()
    finally:
        db.close()


def _schedule_push_notifications(device_info: Dict[str, Any], old_health_status: str, new_health_status: str, all_alert_changes: List[Dict]):
    """
    调度推送通知（优化版）
    
    Args:
        device_info: 设备信息
        old_health_status: 旧健康状态
        new_health_status: 新健康状态
        all_alert_changes: 所有告警变化列表（新建和解决的告警）
    """
    import threading
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    
    # 推送前条件检查
    has_health_change = old_health_status != new_health_status
    has_alert_changes = len(all_alert_changes) > 0
    
    # 如果既没有健康状态变化，也没有告警变化，则跳过推送
    if not has_health_change and not has_alert_changes:
        logger.debug(f"Device {device_info['device_id']} has no changes, skip push")
        return
    
    # 记录推送决策
    logger.info(f"Push triggered for device {device_info['device_id']}: health_change={has_health_change}, alert_changes={len(all_alert_changes)}")
    
    def push_notifications():
        """在新线程中运行推送通知"""
        try:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def async_push_notifications():
                try:
                    push_count = 0
                    
                    # 1. 设备健康状态变化处理（静默更新健康图）
                    if has_health_change:
                        await push_service.realtime.push_dashboard_update({
                            "device_id": device_info['device_id'],
                            "hostname": device_info.get('hostname'),
                            "old_health_status": old_health_status,
                            "new_health_status": new_health_status,
                            "update_type": "health_chart_only"
                        }, "health_status_silent_update")
                        push_count += 1
                        logger.info(f"Silent health status update: {device_info['device_id']} {old_health_status} -> {new_health_status}")
                    
                    # 2. 推送告警变化
                    if has_alert_changes:
                        for alert_data in all_alert_changes:
                            if alert_data.get('action') == 'created':
                                await push_service.alert.push_new_alert(alert_data)
                            elif alert_data.get('action') == 'resolved':
                                await push_service.alert.push_resolved_alert(alert_data)
                            push_count += 1
                        
                        # 推送告警列表刷新事件
                        alert_refresh_message = {
                            "device_id": device_info['device_id'],
                            "hostname": device_info.get('hostname'),
                            "alert_changes": len(all_alert_changes),
                            "new_alerts": len([a for a in all_alert_changes if a.get('action') == 'created']),
                            "resolved_alerts": len([a for a in all_alert_changes if a.get('action') == 'resolved'])
                        }
                        
                        await push_service.realtime.push_dashboard_update(alert_refresh_message, "alert_list_refresh")
                        push_count += 1
                        logger.info(f"Alert list refresh: {device_info['device_id']} ({len(all_alert_changes)} changes)")
                    
                    # 3. 推送Dashboard数据更新通知
                    if has_health_change or has_alert_changes:
                        await push_service.realtime.push_dashboard_update({
                            "device_id": device_info['device_id'],
                            "hostname": device_info.get('hostname'),
                            "health_status": new_health_status,
                            "alert_count": len(all_alert_changes),
                            "has_health_change": has_health_change,
                            "has_alert_changes": has_alert_changes
                        }, "device_updated")
                        push_count += 1
                    
                    logger.info(f"Push completed for device {device_info['device_id']}: {push_count} messages sent")
                        
                except Exception as e:
                    logger.error(f"Error in async push notifications: {str(e)}")
            
            # 运行异步推送
            loop.run_until_complete(async_push_notifications())
            
        except Exception as e:
            logger.error(f"Error in push notifications thread: {str(e)}")
        finally:
            # 清理事件循环
            try:
                loop.close()
            except:
                pass
    
    # 使用线程池执行推送任务
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(push_notifications)
    except Exception as e:
        logger.error(f"Error scheduling push notifications: {str(e)}")


def determine_alert_type(db, business_type: str, hardware_type: str) -> str:
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
        rule = db.query(BusinessHardwareUrgencyRulesDO).filter(
            BusinessHardwareUrgencyRulesDO.business_type == business_type,
            BusinessHardwareUrgencyRulesDO.hardware_type == hardware_type.upper(),
            BusinessHardwareUrgencyRulesDO.is_active == 1
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
celery_app.conf.beat_schedule = {}


@celery_app.task(name='recalculate_urgency_for_device')
def recalculate_urgency_for_device(device_id: int):
    """
    当设备业务类型变更时，重新计算该设备所有活跃告警的紧急程度
    
    Args:
        device_id: 设备ID
    """
    db = next(get_sync_db())
    try:
        logger.info(f"Starting urgency recalculation for device_id: {device_id}")
        
        # 1. 获取设备最新的业务类型
        device = db.query(DeviceInfoDO).filter(DeviceInfoDO.device_id == device_id).first()
        if not device:
            logger.warning(f"Recalculation task skipped: Device with id {device_id} not found.")
            return

        business_type = device.business_type
        
        # 2. 获取该设备所有活跃的告警
        active_alerts = db.query(AlertInfoDO).filter(
            AlertInfoDO.device_id == device_id,
            AlertInfoDO.alert_status == 'active'
        ).all()

        if not active_alerts:
            logger.info(f"No active alerts found for device {device_id}. Nothing to do.")
            return
            
        # 3. 获取所有紧急度规则并存入map
        rules_query = db.query(BusinessHardwareUrgencyRulesDO).filter(BusinessHardwareUrgencyRulesDO.is_active == 1).all()
        urgency_rules_map = {(rule.business_type, rule.hardware_type.lower()): rule.urgency_level for rule in rules_query}
        
        updated_count = 0
        updated_alert_ids = []
        # 4. 遍历告警，重新计算紧急度
        for alert in active_alerts:
            old_urgency = alert.urgency_level
            new_urgency = urgency_rules_map.get((business_type, alert.component_type.lower()), 'scheduled')
            
            if old_urgency != new_urgency:
                alert.urgency_level = new_urgency
                alert.update_time = datetime.now()
                updated_count += 1
                updated_alert_ids.append(alert.alert_id)
                logger.info(f"Updating urgency for alert_id {alert.alert_id}: {old_urgency} -> {new_urgency}")

        if updated_count > 0:
            db.commit()
            logger.info(f"Urgency recalculation completed for device {device_id}. {updated_count} alerts updated.")
            
            # 发送WebSocket通知
            message = {
                "type": "urgency_recalculation_completed",
                "data": {
                    "updated_alert_ids": updated_alert_ids,
                    "affected_device_ids": [device_id]
                },
                "message": f"设备 {device.hostname or device_id} 的告警紧急度已更新",
                "timestamp": datetime.now().isoformat()
            }
            publish_sync_redis_message("websocket:alerts", message)

        else:
            logger.info(f"Urgency recalculation completed for device {device_id}. No changes needed.")

    except Exception as e:
        logger.error(f"Error during urgency recalculation for device {device_id}: {e}")
        db.rollback()
    finally:
        db.close()


@celery_app.task(name='recalculate_urgency_for_rule_change')
def recalculate_urgency_for_rule_change(business_type: str, hardware_type: str):
    """
    当紧急度规则变更时，重新计算所有受影响的活跃告警的紧急程度
    
    Args:
        business_type: 规则中的业务类型
        hardware_type: 规则中的硬件类型
    """
    db = next(get_sync_db())
    try:
        logger.info(f"Starting urgency recalculation for rule change: business_type='{business_type}', hardware_type='{hardware_type}'")
        
        # 1. 查找所有匹配该业务类型的设备
        devices = db.query(DeviceInfoDO.device_id).filter(DeviceInfoDO.business_type == business_type).all()
        device_ids = [device.device_id for device in devices]

        if not device_ids:
            logger.info(f"No devices found with business_type '{business_type}'. Nothing to do.")
            return

        # 2. 获取所有紧急度规则并存入map
        rules_query = db.query(BusinessHardwareUrgencyRulesDO).filter(BusinessHardwareUrgencyRulesDO.is_active == 1).all()
        urgency_rules_map = {(rule.business_type, rule.hardware_type.lower()): rule.urgency_level for rule in rules_query}

        # 3. 查找所有匹配设备和硬件类型的活跃告警（等值小写）
        alerts_to_update = db.query(AlertInfoDO).filter(
            AlertInfoDO.device_id.in_(device_ids),
            AlertInfoDO.component_type == hardware_type.lower(),
            AlertInfoDO.alert_status == 'active'
        ).all()

        if not alerts_to_update:
            logger.info(f"No active alerts found for hardware_type '{hardware_type}' on affected devices. Nothing to do.")
            return
        
        updated_count = 0
        updated_alert_ids = []
        affected_device_ids = list(set(alert.device_id for alert in alerts_to_update))
        # 4. 遍历告警，重新计算紧急度
        for alert in alerts_to_update:
            old_urgency = alert.urgency_level
            # 重新从map中根据告警的业务类型和组件类型获取最新紧急度
            # 注意：告警的业务类型是其所属设备的业务类型
            new_urgency = urgency_rules_map.get((business_type, alert.component_type.lower()), 'scheduled')
            
            if old_urgency != new_urgency:
                alert.urgency_level = new_urgency
                alert.update_time = datetime.now()
                updated_count += 1
                updated_alert_ids.append(alert.alert_id)
                logger.info(f"Updating urgency for alert_id {alert.alert_id}: {old_urgency} -> {new_urgency}")

        if updated_count > 0:
            db.commit()
            logger.info(f"Urgency recalculation for rule change completed. {updated_count} alerts updated.")
            
            # 发送WebSocket通知
            message = {
                "type": "urgency_recalculation_completed",
                "data": {
                    "updated_alert_ids": updated_alert_ids,
                    "affected_device_ids": affected_device_ids
                },
                "message": f"因规则变更， {updated_count}条告警的紧急度已更新",
                "timestamp": datetime.now().isoformat()
            }
            publish_sync_redis_message("websocket:alerts", message)

        else:
            logger.info(f"Urgency recalculation for rule change completed. No changes needed.")

    except Exception as e:
        logger.error(f"Error during urgency recalculation for rule change: {e}")
        db.rollback()
    finally:
        db.close()


# ===============================================================
# 设备可用性检测任务（基于业务IP连通性）
# ===============================================================

@celery_app.task(bind=True, name='check_device_availability')
def check_device_availability(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    检测单个设备的可用性状态（基于业务IP连通性）
    
    Args:
        device_info: 设备信息字典
        
    Returns:
        Dict: 可用性检测结果
    """
    try:
        logger.info(f"开始可用性检测任务 | 设备: {device_info.get('hostname', 'Unknown')}")
        
        # 创建可用性监控器
        availability_monitor = DeviceAvailabilityMonitor()
        
        # 执行异步可用性检测（在同步任务中运行异步代码）
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(availability_monitor.check_device_availability(device_info))
        finally:
            loop.close()
        
        # 保存检测结果到数据库
        if result.get('success', False):
            save_availability_result(result, device_info)
            
            # 推送可用性状态变化到WebSocket客户端
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(push_service.realtime.push_device_availability_change(
                    device_id=result.get('device_id'),
                    availability_status=result.get('availability_status', 'unknown'),
                    device_info=device_info
                ))
            except RuntimeError:
                # 如果没有运行的事件循环，跳过推送
                logger.warning("No event loop running, skipping availability WebSocket push")
        
        logger.info(f"完成可用性检测任务 | 设备: {device_info.get('hostname', 'Unknown')}")
        
        # 检查是否是批次任务，如果是则更新计数器
        batch_id = device_info.get('batch_id')
        if batch_id:
            check_batch_completion(batch_id, result.get('success', False))
        
        return result
        
    except Exception as e:
        logger.error(f"可用性检测任务异常 | 设备 {device_info.get('hostname', 'Unknown')}: {str(e)}")
        self.retry(countdown=60, max_retries=3)  # 1分钟后重试，最多3次


@celery_app.task(name='check_all_devices_availability')
def check_all_devices_availability() -> Dict[str, Any]:
    """
    检测所有启用监控的设备的可用性状态
    
    Returns:
        Dict: 批量可用性检测结果
    """
    try:
        logger.info("开始批量设备可用性检测任务")
        
        # 获取数据库会话
        db = next(get_sync_db())
        
        # 查询所有启用监控且有业务IP的设备
        devices = db.query(DeviceInfoDO).filter(
            DeviceInfoDO.monitor_enabled == 1,
            DeviceInfoDO.business_ip.is_not(None),
            DeviceInfoDO.business_ip != ''
        ).all()
        
        if not devices:
            logger.warning("未找到需要进行可用性检测的设备")
            return {
                "success": True,
                "message": "No devices to check availability",
                "total_devices": 0,
                "results": []
            }
        
        logger.info(f"找到 {len(devices)} 个设备需要进行可用性检测")
        
        # 将设备信息转换为字典格式
        device_list = []
        for device in devices:
            device_dict = {
                "device_id": device.device_id,
                "hostname": device.hostname,
                "business_ip": device.business_ip,
                "oob_ip": device.oob_ip,
                "business_type": device.business_type,
                "manufacturer": device.manufacturer,
                "model": device.model
            }
            device_list.append(device_dict)
        
        # 生成批次ID
        import uuid
        batch_id = str(uuid.uuid4())
        
        # 在Redis中设置计数器，用于跟踪任务完成情况
        from config.get_redis import get_redis
        redis_client = get_redis()
        counter_key = f"availability_batch:{batch_id}:counter"
        total_key = f"availability_batch:{batch_id}:total"
        success_key = f"availability_batch:{batch_id}:success"
        failed_key = f"availability_batch:{batch_id}:failed"
        
        redis_client.set(counter_key, 0, ex=3600)  # 1小时过期
        redis_client.set(total_key, len(device_list), ex=3600)
        redis_client.set(success_key, 0, ex=3600)
        redis_client.set(failed_key, 0, ex=3600)
        
        # 为每个设备添加batch_id
        for device_dict in device_list:
            device_dict['batch_id'] = batch_id
        
        # 创建并分发可用性检测任务到任务队列
        task_signatures = [
            check_device_availability.s(device_dict) 
            for device_dict in device_list
        ]
        
        # 并行执行所有任务
        job = group(task_signatures)
        result = job.apply_async()
        
        # 推送批次开始通知
        batch_start_message = {
            "type": "availability_batch_started",
            "data": {
                "batch_id": batch_id,
                "total_devices": len(device_list),
                "device_count_by_status": {
                    "pending": len(device_list),
                    "completed": 0,
                    "failed": 0
                }
            },
            "message": f"开始批量可用性检测 - {len(device_list)} 个设备",
            "timestamp": datetime.now().isoformat()
        }
        publish_sync_redis_message("websocket:availability", batch_start_message)
        
        logger.info(f"已分发 {len(device_list)} 个可用性检测任务，批次ID: {batch_id}")
        
        return {
            "success": True,
            "batch_id": batch_id,
            "total_devices": len(device_list),
            "message": f"Availability check tasks dispatched for {len(device_list)} devices",
            "task_group_id": result.id if result else None
        }
        
    except Exception as e:
        logger.error(f"批量可用性检测任务失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Batch availability check failed"
        }
    finally:
        if 'db' in locals():
            db.close()


def save_availability_result(result: Dict[str, Any], device_info: Dict[str, Any]):
    """
    保存设备可用性检测结果，并根据业务规则生成告警
    
    Args:
        result: 可用性检测结果
        device_info: 设备信息
    """
    db = next(get_sync_db())
    try:
        device_id = device_info['device_id']
        business_type = device_info.get('business_type', '')
        
        logger.info(f"保存设备可用性结果 | device_id={device_id}")
        
        # 1. 更新设备最后检查时间
        device = db.query(DeviceInfoDO).filter(DeviceInfoDO.device_id == device_id).first()
        if device:
            device.last_check_time = datetime.now()
            
            # 根据可用性状态更新设备健康状态
            availability_status = result.get('availability_status', 'unknown')
            if availability_status == 'online':
                # 可用性正常，不影响现有健康状态（除非之前是因为宕机导致的critical）
                if device.health_status == 'critical':
                    # 检查是否还有其他critical告警
                    other_critical_alerts = db.query(AlertInfoDO).filter(
                        AlertInfoDO.device_id == device_id,
                        AlertInfoDO.alert_status == 'active',
                        AlertInfoDO.component_type != 'downtime',
                        AlertInfoDO.health_status == 'critical'
                    ).count()
                    
                    if other_critical_alerts == 0:
                        # 如果没有其他critical告警，将设备状态改为warning或ok
                        warning_alerts = db.query(AlertInfoDO).filter(
                            AlertInfoDO.device_id == device_id,
                            AlertInfoDO.alert_status == 'active',
                            AlertInfoDO.health_status == 'warning'
                        ).count()
                        device.health_status = 'warning' if warning_alerts > 0 else 'ok'
                        
            elif availability_status == 'offline':
                # 设备宕机，健康状态设为critical
                device.health_status = 'critical'
        
        # 2. 获取所有紧急度规则
        rules_query = db.query(BusinessHardwareUrgencyRulesDO).filter(
            BusinessHardwareUrgencyRulesDO.is_active == 1
        ).all()
        urgency_rules_map = {
            (rule.business_type, rule.hardware_type.lower()): rule.urgency_level 
            for rule in rules_query
        }
        
        # 3. 处理可用性告警
        alerts = result.get('alerts', [])
        
        if alerts:
            logger.info(f"处理可用性告警 | device_id={device_id} | 告警数量: {len(alerts)}")
            
            # 获取现有的downtime类型活跃告警
            existing_downtime_alerts = db.query(AlertInfoDO).filter(
                AlertInfoDO.device_id == device_id,
                AlertInfoDO.component_type == 'downtime',
                AlertInfoDO.alert_status == 'active'
            ).all()
            
            # 为每个告警应用业务规则确定紧急程度
            for alert_data in alerts:
                component_type = alert_data.get('component_type', 'downtime')
                
                # 应用业务规则确定紧急程度
                urgency_level = urgency_rules_map.get(
                    (business_type, component_type), 
                    'urgent'  # 宕机默认为紧急
                )
                alert_data['urgency_level'] = urgency_level
                
                # 创建新告警
                new_alert = AlertInfoDO(
                    device_id=device_id,
                    component_type=component_type,
                    component_name=alert_data.get('component_name', '宕机检测'),
                    health_status=alert_data.get('health_status', 'critical'),
                    urgency_level=urgency_level,
                    alert_status='active',
                    alert_message=alert_data.get('alert_message', '设备宕机告警'),
                    first_occurrence=datetime.now(),
                    last_occurrence=datetime.now(),
                    raw_data=alert_data.get('raw_data', '{}')
                )
                db.add(new_alert)
                
                logger.info(f"新建可用性告警 | device_id={device_id} | 紧急程度: {urgency_level}")
            
            # 如果有现有的downtime告警，将其标记为已解决（因为现在有新的状态）
            for old_alert in existing_downtime_alerts:
                old_alert.alert_status = 'resolved'
                old_alert.resolved_time = datetime.now()
                
        else:
            # 没有新告警，检查是否需要解决现有的downtime告警
            existing_downtime_alerts = db.query(AlertInfoDO).filter(
                AlertInfoDO.device_id == device_id,
                AlertInfoDO.component_type == 'downtime',
                AlertInfoDO.alert_status == 'active'
            ).all()
            
            for old_alert in existing_downtime_alerts:
                old_alert.alert_status = 'resolved'
                old_alert.resolved_time = datetime.now()
                logger.info(f"解决可用性告警 | device_id={device_id} | 设备已恢复在线")
        
        db.commit()
        logger.info(f"设备可用性结果保存完成 | device_id={device_id}")
        
    except Exception as e:
        logger.error(f"保存设备可用性结果失败 | device_id={device_info.get('device_id', 'N/A')}: {str(e)}")
        db.rollback()
    finally:
        db.close()


# Celery Beat 启动命令（示例）：
# celery -A module_redfish.celery_tasks.celery_app beat -l info 