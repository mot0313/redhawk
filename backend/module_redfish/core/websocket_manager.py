"""
WebSocket连接管理器
用于管理WebSocket连接、房间订阅和消息广播
"""
import json
import asyncio
from typing import Dict, Set, List, Optional, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger
import redis.asyncio as aioredis
from config.env import RedisConfig


class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        """初始化连接管理器"""
        self.active_connections: Dict[str, WebSocket] = {}  # 用户ID -> WebSocket连接
        self.user_rooms: Dict[str, Set[str]] = {}  # 用户ID -> 订阅的房间集合
        self.room_users: Dict[str, Set[str]] = {}  # 房间 -> 用户ID集合
        self.redis_client: Optional[aioredis.Redis] = None
        
    async def init_redis(self):
        """初始化Redis连接"""
        try:
            self.redis_client = await aioredis.from_url(
                f"redis://{RedisConfig.redis_host}:{RedisConfig.redis_port}",
                username=RedisConfig.redis_username,
                password=RedisConfig.redis_password,
                db=RedisConfig.redis_database,
                decode_responses=True
            )
            logger.info("Redis connection initialized for WebSocket manager")
            
            # 启动Redis订阅任务
            asyncio.create_task(self._subscribe_redis_messages())
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis connection: {str(e)}")
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """
        接受WebSocket连接
        
        Args:
            websocket: WebSocket连接对象
            user_id: 用户ID
        """
        try:
            await websocket.accept()
            self.active_connections[user_id] = websocket
            self.user_rooms[user_id] = set()
            logger.info(f"WebSocket connected: user_id={user_id}")
            
            # 发送连接成功消息
            await self.send_to_user(user_id, {
                "type": "connection",
                "status": "connected",
                "message": "WebSocket连接成功",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error connecting WebSocket for user {user_id}: {str(e)}")
    
    async def disconnect(self, user_id: str):
        """
        断开WebSocket连接
        
        Args:
            user_id: 用户ID
        """
        try:
            # 从所有订阅的房间中移除用户
            if user_id in self.user_rooms:
                for room in self.user_rooms[user_id].copy():
                    await self.leave_room(user_id, room)
                del self.user_rooms[user_id]
            

            if user_id in self.active_connections:
                del self.active_connections[user_id]
            
            logger.info(f"WebSocket disconnected: user_id={user_id}")
            
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket for user {user_id}: {str(e)}")
    
    async def join_room(self, user_id: str, room: str):
        """
        加入房间
        
        Args:
            user_id: 用户ID
            room: 房间名称
        """
        try:
            if user_id not in self.user_rooms:
                self.user_rooms[user_id] = set()
            
            if room not in self.room_users:
                self.room_users[room] = set()
            
            self.user_rooms[user_id].add(room)
            self.room_users[room].add(user_id)
            
            logger.info(f"User {user_id} joined room {room}")
            
            # 通知用户加入房间成功
            await self.send_to_user(user_id, {
                "type": "room",
                "action": "joined",
                "room": room,
                "message": f"已加入房间: {room}",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error joining room {room} for user {user_id}: {str(e)}")
    
    async def leave_room(self, user_id: str, room: str):
        """
        离开房间
        
        Args:
            user_id: 用户ID
            room: 房间名称
        """
        try:
            if user_id in self.user_rooms and room in self.user_rooms[user_id]:
                self.user_rooms[user_id].remove(room)
            
            if room in self.room_users and user_id in self.room_users[room]:
                self.room_users[room].remove(user_id)
                
                # 如果房间没有用户了，删除房间
                if not self.room_users[room]:
                    del self.room_users[room]
            
            logger.info(f"User {user_id} left room {room}")
            
        except Exception as e:
            logger.error(f"Error leaving room {room} for user {user_id}: {str(e)}")
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """
        发送消息给特定用户
        
        Args:
            user_id: 用户ID
            message: 消息内容
        """
        try:
            if user_id in self.active_connections:
                websocket = self.active_connections[user_id]
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
                
        except WebSocketDisconnect:
            logger.warning(f"WebSocket disconnected when sending message to user {user_id}")
            await self.disconnect(user_id)
        except Exception as e:
            logger.error(f"Error sending message to user {user_id}: {str(e)}")
    
    async def broadcast_to_room(self, room: str, message: Dict[str, Any], exclude_user: Optional[str] = None):
        """
        向房间内所有用户广播消息
        
        Args:
            room: 房间名称
            message: 消息内容
            exclude_user: 排除的用户ID
        """
        try:
            if room not in self.room_users:
                return
            
            disconnected_users = []
            
            for user_id in self.room_users[room]:
                if exclude_user and user_id == exclude_user:
                    continue
                
                try:
                    await self.send_to_user(user_id, message)
                except Exception as e:
                    logger.error(f"Error sending broadcast to user {user_id}: {str(e)}")
                    disconnected_users.append(user_id)
            
            # 清理断开连接的用户
            for user_id in disconnected_users:
                await self.disconnect(user_id)
                
        except Exception as e:
            logger.error(f"Error broadcasting to room {room}: {str(e)}")
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """
        向所有连接的用户广播消息
        
        Args:
            message: 消息内容
        """
        try:
            disconnected_users = []
            
            for user_id in list(self.active_connections.keys()):
                try:
                    await self.send_to_user(user_id, message)
                except Exception as e:
                    logger.error(f"Error sending global broadcast to user {user_id}: {str(e)}")
                    disconnected_users.append(user_id)
            
            # 清理断开连接的用户
            for user_id in disconnected_users:
                await self.disconnect(user_id)
                
        except Exception as e:
            logger.error(f"Error broadcasting to all users: {str(e)}")
    
    async def publish_redis_message(self, channel: str, message: Dict[str, Any]):
        """
        向Redis发布消息（用于跨实例通信）
        
        Args:
            channel: Redis频道
            message: 消息内容
        """
        try:
            if self.redis_client:
                await self.redis_client.publish(channel, json.dumps(message, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Error publishing Redis message to channel {channel}: {str(e)}")
    
    async def _subscribe_redis_messages(self):
        """订阅Redis消息（用于跨进程通信）"""
        try:
            if not self.redis_client:
                logger.warning("Redis client not initialized, skipping subscription")
                return
            
            # 创建Redis订阅客户端
            pubsub = self.redis_client.pubsub()
            
            # 订阅WebSocket相关频道
            await pubsub.subscribe(
                "websocket:dashboard",
                "websocket:alerts", 
                "websocket:urgent_alerts",
                "websocket:device_monitoring",
                "websocket:broadcast"
            )
            
            logger.info("Started Redis subscription for WebSocket channels")
            
            # 监听消息
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        channel = message['channel']
                        data = json.loads(message['data'])
                        
                        logger.debug(f"Received Redis message on channel {channel}: {data}")
                        
                        # 根据频道转发消息
                        if channel == "websocket:broadcast":
                            await self.broadcast_to_all(data)
                        elif channel.startswith("websocket:"):
                            room = channel.replace("websocket:", "")
                            await self.broadcast_to_room(room, data)
                            
                    except Exception as e:
                        logger.error(f"Error processing Redis message: {str(e)}")
                        
        except Exception as e:
            logger.error(f"Error in Redis subscription: {str(e)}")
            # 重试订阅
            await asyncio.sleep(5)
            asyncio.create_task(self._subscribe_redis_messages())
    
    def get_room_users_count(self, room: str) -> int:
        """
        获取房间用户数量
        
        Args:
            room: 房间名称
            
        Returns:
            int: 用户数量
        """
        return len(self.room_users.get(room, set()))
    
    def get_active_connections_count(self) -> int:
        """
        获取活跃连接数量
        
        Returns:
            int: 连接数量
        """
        return len(self.active_connections)
    
    def get_user_rooms(self, user_id: str) -> List[str]:
        """
        获取用户订阅的房间列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[str]: 房间列表
        """
        return list(self.user_rooms.get(user_id, set()))


# 全局WebSocket管理器实例
websocket_manager = WebSocketManager()


async def init_websocket_manager():
    """初始化WebSocket管理器"""
    await websocket_manager.init_redis()


async def cleanup_websocket_manager():
    """清理WebSocket管理器"""
    if websocket_manager.redis_client:
        await websocket_manager.redis_client.close() 