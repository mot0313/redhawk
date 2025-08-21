"""
实时推送服务模块
提供统一的WebSocket推送接口和消息管理功能
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from loguru import logger

from .websocket_manager import websocket_manager


class RealtimePushService:
    """实时推送服务"""
    
    @staticmethod
    async def _ensure_redis_connection():
        """确保Redis连接已初始化（用于独立进程）"""
        if not websocket_manager.redis_client:
            await websocket_manager.init_redis()
    
    @staticmethod
    async def push_dashboard_update(data: Dict[str, Any], action: str = "data_refresh"):
        """
        推送Dashboard更新数据
        
        Args:
            data: 更新数据
            action: 操作类型（默认为data_refresh）
        """
        try:
            # 确保Redis连接
            await RealtimePushService._ensure_redis_connection()
            
            message = {
                "type": "dashboard_update",
                "action": action,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            
            # 首先尝试直接广播
            await websocket_manager.broadcast_to_room("dashboard", message)
            
            # 然后通过Redis发布，确保跨进程通信
            await websocket_manager.publish_redis_message("websocket:dashboard", message)
            
            logger.info(f"Pushed dashboard update with action: {action}")
            
        except Exception as e:
            logger.error(f"Error pushing dashboard update: {str(e)}")
    
    @staticmethod
    async def push_device_status_change(device_id: str, old_status: str, new_status: str, device_info: Dict[str, Any]):
        """
        推送设备状态变化
        
        Args:
            device_id: 设备ID
            old_status: 旧状态
            new_status: 新状态
            device_info: 设备信息
        """
        try:
            # 确保Redis连接
            await RealtimePushService._ensure_redis_connection()
            
            message = {
                "type": "device_status_change",
                "action": "status_updated",
                "device_id": device_id,
                "hostname": device_info.get('hostname'),
                "old_status": old_status,
                "new_status": new_status,
                "device_info": device_info,
                "timestamp": datetime.now().isoformat()
            }
            
            # 推送到多个相关房间
            await websocket_manager.broadcast_to_room("dashboard", message)
            await websocket_manager.broadcast_to_room("device_monitoring", message)
            await websocket_manager.broadcast_to_room(f"device_{device_id}", message)
            
            # Redis发布
            await websocket_manager.publish_redis_message("websocket:dashboard", message)
            await websocket_manager.publish_redis_message("websocket:device_monitoring", message)
            
            logger.info(f"Pushed device status change: {device_id} {old_status} -> {new_status}")
            
        except Exception as e:
            logger.error(f"Error pushing device status change: {str(e)}")
    
    @staticmethod
    async def push_alert_statistics_update(statistics: Dict[str, Any]):
        """
        推送告警统计更新
        
        Args:
            statistics: 统计数据
        """
        try:
            # 确保Redis连接
            await RealtimePushService._ensure_redis_connection()
            
            message = {
                "type": "alert_statistics_update",
                "action": "statistics_updated",
                "statistics": statistics,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket_manager.broadcast_to_room("dashboard", message)
            await websocket_manager.broadcast_to_room("alerts", message)
            
            # Redis发布
            await websocket_manager.publish_redis_message("websocket:dashboard", message)
            await websocket_manager.publish_redis_message("websocket:alerts", message)
            
            logger.info("Pushed alert statistics update")
            
        except Exception as e:
            logger.error(f"Error pushing alert statistics: {str(e)}")
    
    @staticmethod
    async def push_system_notification(notification_type: str, title: str, message: str, level: str = "info"):
        """
        推送系统通知
        
        Args:
            notification_type: 通知类型
            title: 标题
            message: 消息内容
            level: 级别（info, warning, error, success）
        """
        try:
            # 确保Redis连接
            await RealtimePushService._ensure_redis_connection()
            
            notification = {
                "type": "system_notification",
                "action": "notification",
                "notification_type": notification_type,
                "title": title,
                "message": message,
                "level": level,
                "timestamp": datetime.now().isoformat()
            }
            
            # 根据级别选择推送范围
            if level == "error":
                # 错误通知推送给所有用户
                await websocket_manager.broadcast_to_all(notification)
                await websocket_manager.publish_redis_message("websocket:broadcast", notification)
            else:
                # 其他通知只推送到dashboard
                await websocket_manager.broadcast_to_room("dashboard", notification)
                await websocket_manager.publish_redis_message("websocket:dashboard", notification)
            
            logger.info(f"Pushed system notification: {title}")
            
        except Exception as e:
            logger.error(f"Error pushing system notification: {str(e)}")
    
    @staticmethod
    async def push_monitoring_task_status(task_id: str, status: str, progress: Optional[Dict[str, Any]] = None):
        """
        推送监控任务状态更新
        
        Args:
            task_id: 任务ID
            status: 任务状态
            progress: 进度信息
        """
        try:
            message = {
                "type": "monitoring_task_status",
                "action": "status_updated",
                "task_id": task_id,
                "status": status,
                "progress": progress,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket_manager.broadcast_to_room("dashboard", message)
            await websocket_manager.broadcast_to_room("device_monitoring", message)
            
            logger.info(f"Pushed monitoring task status: {task_id} - {status}")
            
        except Exception as e:
            logger.error(f"Error pushing monitoring task status: {str(e)}")


class AlertPushService:
    """告警推送服务"""
    
    @staticmethod
    async def push_new_alert(alert_data: Dict[str, Any]):
        """
        推送新告警
        
        Args:
            alert_data: 告警数据
        """
        try:
            message = {
                "type": "new_alert",
                "action": "alert_created",
                "alert": alert_data,
                "timestamp": datetime.now().isoformat()
            }
            
            # 根据告警类型推送到不同房间
            alert_type = alert_data.get('alert_type', 'scheduled')
            
            if alert_type == 'urgent':
                # 紧急告警：推送到所有相关房间
                await websocket_manager.broadcast_to_room("dashboard", message)
                await websocket_manager.broadcast_to_room("alerts", message)
                await websocket_manager.broadcast_to_room("urgent_alerts", message)
                
                # 发送紧急告警特殊通知
                urgent_notification = {
                    "type": "urgent_alert_notification",
                    "action": "urgent_alert",
                    "alert": alert_data,
                    "notification_type": "urgent",
                    "title": "紧急告警",
                    "message": f"设备 {alert_data.get('hostname')} 出现紧急告警",
                    "timestamp": datetime.now().isoformat()
                }
                await websocket_manager.broadcast_to_all(urgent_notification)
                
            else:
                # 择期告警：推送到普通房间
                await websocket_manager.broadcast_to_room("dashboard", message)
                await websocket_manager.broadcast_to_room("alerts", message)
            
            logger.info(f"Pushed new alert: {alert_type} - {alert_data.get('alert_message')}")
            
        except Exception as e:
            logger.error(f"Error pushing new alert: {str(e)}")
    
    @staticmethod
    async def push_alert_resolved(alert_data: Dict[str, Any]):
        """
        推送告警解决通知
        
        Args:
            alert_data: 告警数据
        """
        try:
            message = {
                "type": "alert_resolved",
                "action": "alert_resolved",
                "alert": alert_data,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket_manager.broadcast_to_room("dashboard", message)
            await websocket_manager.broadcast_to_room("alerts", message)
            
            logger.info(f"Pushed alert resolved: {alert_data.get('alert_id')}")
            
        except Exception as e:
            logger.error(f"Error pushing alert resolved: {str(e)}")


class DashboardPushService:
    """Dashboard数据推送服务"""
    
    @staticmethod
    async def push_real_time_statistics():
        """推送实时统计数据"""
        try:
            # 这里应该从数据库获取实时统计数据
            # 暂时使用示例数据
            statistics = {
                "device_count": 0,
                "online_devices": 0,
                "alert_counts": {
                    "urgent": 0,
                    "scheduled": 0,
                    "total": 0
                },
                "health_status": {
                    "healthy": 0,
                    "warning": 0,
                    "critical": 0
                },
                "last_update": datetime.now().isoformat()
            }
            
            message = {
                "type": "dashboard_statistics",
                "action": "real_time_update",
                "statistics": statistics,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket_manager.broadcast_to_room("dashboard", message)
            logger.info("Pushed real-time dashboard statistics")
            
        except Exception as e:
            logger.error(f"Error pushing dashboard statistics: {str(e)}")
    
    @staticmethod
    async def push_device_health_summary(devices_health: List[Dict[str, Any]]):
        """
        推送设备健康状态汇总
        
        Args:
            devices_health: 设备健康状态列表
        """
        try:
            message = {
                "type": "device_health_summary",
                "action": "health_updated",
                "devices": devices_health,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket_manager.broadcast_to_room("dashboard", message)
            logger.info(f"Pushed device health summary for {len(devices_health)} devices")
            
        except Exception as e:
            logger.error(f"Error pushing device health summary: {str(e)}")


class MonitoringPushService:
    """监控推送服务"""
    
    @staticmethod
    async def push_monitoring_started(total_devices: int):
        """
        推送监控开始通知
        
        Args:
            total_devices: 总设备数
        """
        try:
            message = {
                "type": "monitoring_started",
                "action": "monitoring_started",
                "total_devices": total_devices,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket_manager.broadcast_to_room("dashboard", message)
            await websocket_manager.broadcast_to_room("device_monitoring", message)
            
            logger.info(f"Pushed monitoring started for {total_devices} devices")
            
        except Exception as e:
            logger.error(f"Error pushing monitoring started: {str(e)}")
    
    @staticmethod
    async def push_monitoring_progress(completed: int, total: int, current_device: Optional[str] = None):
        """
        推送监控进度更新
        
        Args:
            completed: 已完成数量
            total: 总数量
            current_device: 当前设备
        """
        try:
            progress = round((completed / total) * 100, 2) if total > 0 else 0
            
            message = {
                "type": "monitoring_progress",
                "action": "progress_update",
                "completed": completed,
                "total": total,
                "progress": progress,
                "current_device": current_device,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket_manager.broadcast_to_room("dashboard", message)
            await websocket_manager.broadcast_to_room("device_monitoring", message)
            
            logger.debug(f"Pushed monitoring progress: {completed}/{total} ({progress}%)")
            
        except Exception as e:
            logger.error(f"Error pushing monitoring progress: {str(e)}")
    
    @staticmethod
    async def push_monitoring_completed(results: Dict[str, Any]):
        """
        推送监控完成通知
        
        Args:
            results: 监控结果
        """
        try:
            message = {
                "type": "monitoring_completed",
                "action": "monitoring_completed",
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket_manager.broadcast_to_room("dashboard", message)
            await websocket_manager.broadcast_to_room("device_monitoring", message)
            
            logger.info(f"Pushed monitoring completed: {results.get('total_devices')} devices")
            
        except Exception as e:
            logger.error(f"Error pushing monitoring completed: {str(e)}")


# 统一的推送服务入口
class PushServiceManager:
    """推送服务管理器"""
    
    realtime = RealtimePushService()
    alert = AlertPushService()
    dashboard = DashboardPushService()
    monitoring = MonitoringPushService()
    
    @classmethod
    async def initialize(cls):
        """初始化推送服务"""
        try:
            logger.info("Initializing push service manager...")
            # 这里可以添加初始化逻辑
            logger.info("Push service manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing push service manager: {str(e)}")
    
    @classmethod
    async def cleanup(cls):
        """清理推送服务"""
        try:
            logger.info("Cleaning up push service manager...")
            # 这里可以添加清理逻辑
            logger.info("Push service manager cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Error cleaning up push service manager: {str(e)}")


# 导出推送服务实例
push_service = PushServiceManager() 