"""
WebSocket控制器
处理WebSocket连接、认证和消息路由
"""
import json
from typing import Optional, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger
from datetime import datetime

from ..websocket_manager import websocket_manager
from module_task.redfish_monitor_tasks import RedfishSchedulerTasks, MonitorConfig
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from utils.log_util import logger as sys_logger


# JWT认证
security = HTTPBearer()


async def verify_websocket_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[str]:
    """
    验证WebSocket连接的JWT Token
    
    Args:
        credentials: HTTP认证凭据
        
    Returns:
        Optional[str]: 用户ID，如果认证失败返回None
    """
    try:
        if not credentials or not credentials.credentials:
            return None
        
        # 这里应该添加JWT token验证逻辑
        # 为了简化，暂时返回固定用户ID
        # 实际项目中应该解析JWT token获取用户信息
        token = credentials.credentials
        
        # TODO: 添加真实的JWT验证逻辑
        # decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        # user_id = decoded_token.get("user_id")
        
        # 临时使用token作为用户ID（仅用于演示）
        user_id = f"user_{hash(token) % 10000}"
        
        return user_id
        
    except Exception as e:
        logger.error(f"WebSocket token验证失败: {str(e)}")
        return None


class WebSocketController:
    """WebSocket控制器"""
    
    @staticmethod
    async def handle_websocket_connection(websocket: WebSocket, user_id: str = None):
        """
        处理WebSocket连接
        
        Args:
            websocket: WebSocket连接对象
            user_id: 用户ID（可选，如果为None则使用IP地址）
        """
        # 如果没有用户ID，使用客户端IP
        if not user_id:
            client_ip = websocket.client.host if websocket.client else "unknown"
            user_id = f"guest_{client_ip}_{int(datetime.now().timestamp())}"
        
        logger.info(f"处理WebSocket连接请求: user_id={user_id}")
        
        try:
            # 建立连接
            await websocket_manager.connect(websocket, user_id)
            
            # 自动加入dashboard房间
            await websocket_manager.join_room(user_id, "dashboard")
            
            # 发送初始状态信息
            await WebSocketController._send_initial_status(user_id)
            
            # 进入消息处理循环
            await WebSocketController._handle_messages(websocket, user_id)
            
        except WebSocketDisconnect:
            logger.info(f"WebSocket客户端断开连接: user_id={user_id}")
        except Exception as e:
            logger.error(f"WebSocket连接处理异常: user_id={user_id}, error={str(e)}")
        finally:
            # 清理连接
            await websocket_manager.disconnect(user_id)
    
    @staticmethod
    async def _send_initial_status(user_id: str):
        """
        发送初始状态信息
        
        Args:
            user_id: 用户ID
        """
        try:
            # 获取监控任务状态
            monitor_status = RedfishSchedulerTasks.get_monitor_task_status()
            
            # 获取监控配置
            monitor_config = MonitorConfig.get_config()
            
            # 发送初始状态
            await websocket_manager.send_to_user(user_id, {
                "type": "initial_status",
                "data": {
                    "monitor_status": monitor_status,
                    "monitor_config": monitor_config,
                    "connections_count": websocket_manager.get_active_connections_count()
                },
                "message": "已获取初始状态信息",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"发送初始状态信息失败: user_id={user_id}, error={str(e)}")
    
    @staticmethod
    async def _handle_messages(websocket: WebSocket, user_id: str):
        """
        处理WebSocket消息
        
        Args:
            websocket: WebSocket连接对象
            user_id: 用户ID
        """
        while True:
            try:
                # 接收消息
                data = await websocket.receive_text()
                message = json.loads(data)
                
                logger.debug(f"收到WebSocket消息: user_id={user_id}, message={message}")
                
                # 路由消息到相应的处理器
                await WebSocketController._route_message(user_id, message)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                logger.warning(f"收到无效JSON消息: user_id={user_id}")
                await websocket_manager.send_to_user(user_id, {
                    "type": "error",
                    "message": "消息格式错误，请发送有效的JSON格式",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"处理WebSocket消息异常: user_id={user_id}, error={str(e)}")
                await websocket_manager.send_to_user(user_id, {
                    "type": "error",
                    "message": f"处理消息时发生错误: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })
    
    @staticmethod
    async def _route_message(user_id: str, message: Dict[str, Any]):
        """
        路由消息到相应的处理器
        
        Args:
            user_id: 用户ID
            message: 消息内容
        """
        try:
            message_type = message.get("type")
            
            if message_type == "join_room":
                await WebSocketController._handle_join_room(user_id, message)
            elif message_type == "leave_room":
                await WebSocketController._handle_leave_room(user_id, message)
            elif message_type == "manual_monitor":
                await WebSocketController._handle_manual_monitor(user_id, message)
            elif message_type == "get_status":
                await WebSocketController._handle_get_status(user_id, message)
            elif message_type == "ping":
                await WebSocketController._handle_ping(user_id, message)
            else:
                await websocket_manager.send_to_user(user_id, {
                    "type": "error",
                    "message": f"未知消息类型: {message_type}",
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"路由消息失败: user_id={user_id}, error={str(e)}")
    
    @staticmethod
    async def _handle_join_room(user_id: str, message: Dict[str, Any]):
        """处理加入房间请求"""
        room = message.get("room")
        if room:
            await websocket_manager.join_room(user_id, room)
        else:
            await websocket_manager.send_to_user(user_id, {
                "type": "error",
                "message": "缺少房间参数",
                "timestamp": datetime.now().isoformat()
            })
    
    @staticmethod
    async def _handle_leave_room(user_id: str, message: Dict[str, Any]):
        """处理离开房间请求"""
        room = message.get("room")
        if room:
            await websocket_manager.leave_room(user_id, room)
        else:
            await websocket_manager.send_to_user(user_id, {
                "type": "error",
                "message": "缺少房间参数",
                "timestamp": datetime.now().isoformat()
            })
    
    @staticmethod
    async def _handle_manual_monitor(user_id: str, message: Dict[str, Any]):
        """处理手动触发监控请求"""
        result = await RedfishSchedulerTasks.manual_trigger_monitor(user_id)
        
        await websocket_manager.send_to_user(user_id, {
            "type": "manual_monitor_result",
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
    
    @staticmethod
    async def _handle_get_status(user_id: str, message: Dict[str, Any]):
        """处理获取状态请求"""
        await WebSocketController._send_initial_status(user_id)
    
    @staticmethod
    async def _handle_ping(user_id: str, message: Dict[str, Any]):
        """处理心跳请求"""
        await websocket_manager.send_to_user(user_id, {
            "type": "pong",
            "message": "pong",
            "timestamp": datetime.now().isoformat()
        })


# WebSocket消息广播工具函数
class WebSocketBroadcaster:
    """WebSocket消息广播器"""
    
    @staticmethod
    async def broadcast_alert_update(alert_data: Dict[str, Any]):
        """
        广播告警更新
        
        Args:
            alert_data: 告警数据
        """
        try:
            message = {
                "type": "alert_update",
                "data": alert_data,
                "message": "收到新的告警信息",
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket_manager.broadcast_to_room("dashboard", message)
            
        except Exception as e:
            logger.error(f"广播告警更新失败: {str(e)}")
    
    @staticmethod
    async def broadcast_device_status_update(device_data: Dict[str, Any]):
        """
        广播设备状态更新
        
        Args:
            device_data: 设备状态数据
        """
        try:
            message = {
                "type": "device_status_update",
                "data": device_data,
                "message": "设备状态已更新",
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket_manager.broadcast_to_room("dashboard", message)
            
        except Exception as e:
            logger.error(f"广播设备状态更新失败: {str(e)}")
    
    @staticmethod
    async def broadcast_monitor_result(monitor_result: Dict[str, Any]):
        """
        广播监控结果
        
        Args:
            monitor_result: 监控结果数据
        """
        try:
            message = {
                "type": "monitor_result",
                "data": monitor_result,
                "message": "设备监控任务已完成",
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket_manager.broadcast_to_room("dashboard", message)
            
        except Exception as e:
            logger.error(f"广播监控结果失败: {str(e)}") 