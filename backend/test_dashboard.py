#!/usr/bin/env python3
"""
Dashboard功能测试脚本
"""
import asyncio
import sys
sys.path.append('.')

from config.database import AsyncSessionLocal
from module_redfish.service.dashboard_service import DashboardService
from module_redfish.entity.vo.dashboard_vo import DashboardQueryModel


async def test_dashboard():
    """测试dashboard功能"""
    print("开始测试Dashboard功能...")
    
    async with AsyncSessionLocal() as db:
        try:
            # 1. 测试概览数据
            print("\n1. 测试概览数据...")
            query_model = DashboardQueryModel(time_range='7d')
            overview = await DashboardService.get_dashboard_overview_services(db, query_model)
            print(f"概览数据: {overview.dict()}")
            
            # 2. 测试告警趋势图
            print("\n2. 测试告警趋势图...")
            trend = await DashboardService.get_alert_trend_chart_services(db, 7)
            print(f"趋势图数据: {trend.dict()}")
            
            # 3. 测试设备健康图
            print("\n3. 测试设备健康图...")
            health = await DashboardService.get_device_health_chart_services(db)
            print(f"设备健康图数据: {health.dict()}")
            
            # 4. 测试实时告警列表
            print("\n4. 测试实时告警列表...")
            realtime = await DashboardService.get_realtime_alert_list_services(db, 5)
            print(f"实时告警列表: {len(realtime)} 条记录")
            
            # 5. 测试择期告警列表
            print("\n5. 测试择期告警列表...")
            scheduled = await DashboardService.get_scheduled_alert_list_services(db, 5)
            print(f"择期告警列表: {len(scheduled)} 条记录")
            
            print("\n✅ Dashboard功能测试完成！")
            
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_dashboard()) 