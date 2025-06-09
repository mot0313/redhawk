#!/usr/bin/env python3
"""
优化设备字段设计的脚本
移除重复的device_name字段，统一使用hostname
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text
from config.get_db import get_db
from module_redfish.models import DeviceInfo


async def optimize_device_fields():
    """优化设备字段设计"""
    print("开始优化设备字段设计...")
    
    # 获取数据库会话
    async for db in get_db():
        try:
            # 1. 首先检查当前数据情况
            result = await db.execute(
                select(DeviceInfo.device_id, DeviceInfo.device_name, DeviceInfo.hostname)
                .order_by(DeviceInfo.device_id)
            )
            devices = result.all()
            
            print(f"\n当前有 {len(devices)} 台设备:")
            print("-" * 80)
            print(f"{'ID':<5} {'设备名称':<20} {'主机名':<20}")
            print("-" * 80)
            
            for device in devices:
                print(f"{device.device_id:<5} {device.device_name or 'None':<20} {device.hostname or 'None':<20}")
            
            # 2. 数据迁移：如果hostname为空，使用device_name填充
            print("\n开始数据迁移...")
            
            # 查找hostname为空但device_name不为空的记录
            empty_hostname_devices = await db.execute(
                select(DeviceInfo)
                .where(DeviceInfo.hostname.is_(None))
                .where(DeviceInfo.device_name.isnot(None))
            )
            
            devices_to_migrate = empty_hostname_devices.all()
            
            if devices_to_migrate:
                print(f"发现 {len(devices_to_migrate)} 台设备需要迁移hostname...")
                
                for device in devices_to_migrate:
                    await db.execute(
                        update(DeviceInfo)
                        .where(DeviceInfo.device_id == device.device_id)
                        .values(hostname=device.device_name)
                    )
                    print(f"  设备 {device.device_id}: hostname 设置为 '{device.device_name}'")
            
            await db.commit()
            
            # 3. 生成删除device_name字段的SQL
            print("\n生成删除device_name字段的SQL:")
            print("-- 执行以下SQL来删除device_name字段:")
            print("ALTER TABLE device_info DROP COLUMN IF EXISTS device_name;")
            
            print("\n✅ 数据迁移完成!")
            print("⚠️  请手动执行上述SQL来删除device_name字段")
            
        except Exception as e:
            print(f"优化失败: {e}")
            await db.rollback()
        finally:
            await db.close()
            break


if __name__ == "__main__":
    asyncio.run(optimize_device_fields()) 