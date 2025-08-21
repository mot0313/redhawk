#!/usr/bin/env python3
"""
检查WebSocket管理器状态
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from module_redfish.core.websocket_manager import websocket_manager


async def check_websocket_status():
    """检查WebSocket状态"""
    try:
        print("=== WebSocket管理器状态检查 ===")
        
        # 初始化Redis（如果需要）
        await websocket_manager.init_redis()
        
        # 获取连接状态
        active_connections = websocket_manager.get_active_connections_count()
        print(f"📊 活跃连接数: {active_connections}")
        
        # 获取房间信息
        dashboard_users = websocket_manager.get_room_users_count('dashboard')
        alerts_users = websocket_manager.get_room_users_count('alerts')
        urgent_alerts_users = websocket_manager.get_room_users_count('urgent_alerts')
        device_monitoring_users = websocket_manager.get_room_users_count('device_monitoring')
        
        print(f"🏠 房间用户统计:")
        print(f"  - dashboard: {dashboard_users} 用户")
        print(f"  - alerts: {alerts_users} 用户") 
        print(f"  - urgent_alerts: {urgent_alerts_users} 用户")
        print(f"  - device_monitoring: {device_monitoring_users} 用户")
        
        # 显示详细的连接信息
        print(f"\n🔗 详细连接信息:")
        print(f"  - 连接字典: {list(websocket_manager.active_connections.keys())}")
        print(f"  - 用户房间: {websocket_manager.user_rooms}")
        print(f"  - 房间用户: {websocket_manager.room_users}")
        
        return active_connections > 0
        
    except Exception as e:
        print(f"❌ 检查状态失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(check_websocket_status())
    
    if success:
        print("\n✅ WebSocket连接正常！")
    else:
        print("\n❌ WebSocket连接异常！") 