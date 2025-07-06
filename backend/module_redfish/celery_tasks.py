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

from .device_monitor import DeviceMonitor
from config.get_db import get_sync_db
from .models import DeviceInfo, AlertInfo, RedfishAlertLog, BusinessHardwareUrgencyRules
from .realtime_service import PushServiceManager

# 导入统一的Celery配置
from .celery_config import celery_app

# 确保推送服务正确初始化
push_service = PushServiceManager()

# Redis配置，用于同步发布消息
from config.env import RedisConfig


# ===============================================================
# 同步的Redis消息发布工具
# ===============================================================
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
        
        batch_result = {
            "success": True,
            "message": f"Monitoring completed for {len(devices)} devices",
            "total_devices": len(devices),
            "success_count": success_count,
            "failed_count": failed_count,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        # 推送批量监控完成通知
        # TODO: 需要实现监控完成推送方法
        logger.info("Batch monitoring completed, TODO: implement push notification")
        
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
    清理旧的日志记录
    
    Args:
        days: 保留天数，默认30天
        
    Returns:
        Dict: 清理结果
    """
    try:
        logger.info(f"Starting cleanup task for logs older than {days} days")
        
        # 获取数据库会话
        db = next(get_sync_db())
        
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
        active_alerts_query = db.query(AlertInfo).filter(
            AlertInfo.device_id == device_id,
            AlertInfo.alert_status == 'active'
        ).all()
        active_alerts_map = {(alert.component_type, alert.component_name): alert for alert in active_alerts_query}
        
        # 获取所有紧急度规则
        rules_query = db.query(BusinessHardwareUrgencyRules).filter(BusinessHardwareUrgencyRules.is_active == 1).all()
        urgency_rules_map = {(rule.business_type, rule.hardware_type.lower()): rule.urgency_level for rule in rules_query}

        # 获取设备当前状态
        device = db.query(DeviceInfo).filter(DeviceInfo.device_id == device_id).first()
        if not device:
            logger.error(f"Device with id {device_id} not found in database.")
            return
            
            old_health_status = device.health_status
            device.last_check_time = datetime.now()
            device.health_status = result.get('overall_health', 'unknown')
            new_health_status = device.health_status

        # 2. 状态对比与逻辑处理
        all_monitored_components = result.get('all_components', [])
        monitored_components_map = {(comp['component_type'], comp['component_name']): comp for comp in all_monitored_components}
        
        alerts_to_create = []
        alerts_to_resolve = []
        
        # 遍历当前监控到的所有组件
        for (component_type, component_name), component_data in monitored_components_map.items():
            health_status = component_data['health_status']
            alert_key = (component_type, component_name)
            
            existing_alert = active_alerts_map.get(alert_key)
            
            if health_status != 'ok':
                # 组件状态异常
                if not existing_alert:
                    # 情况1: 新告警
                    urgency_level = urgency_rules_map.get((business_type, component_type), 'scheduled')
                    
                    new_alert = AlertInfo(
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
        device = db.query(DeviceInfo).filter(DeviceInfo.device_id == device_id).first()
        if not device:
            logger.warning(f"Recalculation task skipped: Device with id {device_id} not found.")
            return

        business_type = device.business_type
        
        # 2. 获取该设备所有活跃的告警
        active_alerts = db.query(AlertInfo).filter(
            AlertInfo.device_id == device_id,
            AlertInfo.alert_status == 'active'
        ).all()

        if not active_alerts:
            logger.info(f"No active alerts found for device {device_id}. Nothing to do.")
            return
            
        # 3. 获取所有紧急度规则并存入map
        rules_query = db.query(BusinessHardwareUrgencyRules).filter(BusinessHardwareUrgencyRules.is_active == 1).all()
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
        devices = db.query(DeviceInfo.device_id).filter(DeviceInfo.business_type == business_type).all()
        device_ids = [device.device_id for device in devices]

        if not device_ids:
            logger.info(f"No devices found with business_type '{business_type}'. Nothing to do.")
            return

        # 2. 获取所有紧急度规则并存入map
        rules_query = db.query(BusinessHardwareUrgencyRules).filter(BusinessHardwareUrgencyRules.is_active == 1).all()
        urgency_rules_map = {(rule.business_type, rule.hardware_type.lower()): rule.urgency_level for rule in rules_query}

        # 3. 查找所有匹配设备和硬件类型的活跃告警
        alerts_to_update = db.query(AlertInfo).filter(
            AlertInfo.device_id.in_(device_ids),
            AlertInfo.component_type.ilike(hardware_type),
            AlertInfo.alert_status == 'active'
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


# Celery Beat 启动命令（示例）：
# celery -A module_redfish.celery_tasks.celery_app beat -l info 