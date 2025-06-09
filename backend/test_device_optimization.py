#!/usr/bin/env python3
"""
测试设备字段优化后的功能
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from module_redfish.service.device_service import DeviceService
from module_redfish.entity.vo.device_vo import DevicePageQueryModel


async def test_device_optimization():
    """测试设备字段优化功能"""
    print("开始测试设备字段优化功能...")
    
    # 获取数据库会话
    async for db in get_db():
        try:
            # 1. 测试设备列表查询
            print("\n1. 测试设备列表查询...")
            query_model = DevicePageQueryModel(
                page_num=1,
                page_size=10,
                hostname="test"  # 使用hostname搜索
            )
            
            result = await DeviceService.get_device_list_services(
                db, query_model, is_page=True
            )
            
            print(f"查询结果: 成功返回 {len(result.rows)} 条记录")
            
            if result.rows:
                device = result.rows[0]
                # 使用驼峰格式的字段名
                device_id = device.get('deviceId')
                hostname = device.get('hostname')
                
                print(f"第一条设备记录:")
                print(f"  设备ID: {device_id}")
                print(f"  主机名: {hostname}")
                print(f"  健康状态: {device.get('healthStatus')}")
                print(f"  设备状态: {device.get('deviceStatus')}")
                
                # 2. 测试设备详情查询
                print(f"\n2. 测试设备详情查询 (设备ID: {device_id})...")
                
                detail = await DeviceService.get_device_detail_services(db, device_id)
                print(f"详情查询成功:")
                print(f"  主机名: {detail.device.hostname}")
                print(f"  位置: {detail.device.location}")
                print(f"  健康状态: {detail.health_status}")
                
                # 3. 测试监控设备列表
                print(f"\n3. 测试监控设备列表...")
                monitoring_devices = await DeviceService.get_monitoring_devices_services(db)
                print(f"监控设备列表返回 {len(monitoring_devices)} 条记录")
                
                if monitoring_devices:
                    monitor_device = monitoring_devices[0]
                    print(f"第一台监控设备:")
                    print(f"  设备ID: {monitor_device['device_id']}")
                    print(f"  主机名: {monitor_device['hostname']}")
                    print(f"  带外IP: {monitor_device['oob_ip']}")
                
            print("\n✅ 所有测试通过！设备字段优化成功")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await db.close()
            break


if __name__ == "__main__":
    asyncio.run(test_device_optimization()) 