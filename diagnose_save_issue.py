#!/usr/bin/env python3
"""
诊断设备健康状态保存问题
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from datetime import datetime
from sqlalchemy import text
from database.database import get_sync_db
from module_redfish.models import AlertInfo, DeviceInfo
from utils.log_util import logger

def check_database_table():
    """检查数据库表结构"""
    print("🔍 检查数据库表结构...")
    try:
        db = next(get_sync_db())
        
        # 检查alert_info表是否存在
        result = db.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_name = 'alert_info'
        """))
        exists = result.fetchone()
        
        if not exists:
            print("❌ alert_info表不存在！")
            print("💡 需要执行: backend/sql/create_alert_info_final.sql")
            return False
        
        print("✅ alert_info表存在")
        
        # 检查字段结构
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'alert_info' 
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        column_names = [col.column_name for col in columns]
        
        print(f"📋 当前字段: {column_names}")
        
        # 检查关键字段
        required_fields = ['health_status', 'urgency_level', 'component_type', 'component_name']
        missing_fields = [field for field in required_fields if field not in column_names]
        
        if missing_fields:
            print(f"❌ 缺少关键字段: {missing_fields}")
            print("💡 需要执行SQL更新脚本")
            return False
        
        print("✅ 表结构正确")
        return True
        
    except Exception as e:
        print(f"❌ 检查数据库失败: {e}")
        return False

def check_devices():
    """检查设备数据"""
    print("\n🔍 检查设备数据...")
    try:
        db = next(get_sync_db())
        
        # 检查设备数量
        device_count = db.query(DeviceInfo).count()
        print(f"📊 设备总数: {device_count}")
        
        if device_count == 0:
            print("❌ 没有设备数据！")
            return False
        
        # 检查启用监控的设备
        enabled_devices = db.query(DeviceInfo).filter(
            DeviceInfo.monitor_enabled == 1
        ).all()
        
        print(f"📊 启用监控的设备: {len(enabled_devices)}")
        
        if len(enabled_devices) == 0:
            print("❌ 没有启用监控的设备！")
            return False
        
        # 显示设备信息
        for device in enabled_devices[:3]:  # 只显示前3个
            print(f"  • 设备ID: {device.device_id}, 主机名: {device.hostname}")
            print(f"    IP: {device.oob_ip}, 状态: {device.health_status}")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查设备失败: {e}")
        return False

def check_alert_data():
    """检查告警数据"""
    print("\n🔍 检查告警数据...")
    try:
        db = next(get_sync_db())
        
        # 检查告警总数
        alert_count = db.query(AlertInfo).count()
        print(f"📊 告警总数: {alert_count}")
        
        # 检查最近的告警
        recent_alerts = db.query(AlertInfo).order_by(
            AlertInfo.create_time.desc()
        ).limit(5).all()
        
        print(f"📊 最近5条告警:")
        for alert in recent_alerts:
            print(f"  • ID: {alert.alert_id}, 设备: {alert.device_id}")
            print(f"    组件: {alert.component_type}/{alert.component_name}")
            print(f"    状态: {alert.health_status}, 级别: {alert.urgency_level}")
            print(f"    时间: {alert.create_time}")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查告警失败: {e}")
        return False

def test_save_function():
    """测试保存功能"""
    print("\n🔍 测试保存功能...")
    try:
        from module_redfish.celery_tasks import save_monitoring_result
        
        db = next(get_sync_db())
        
        # 获取第一个设备
        device = db.query(DeviceInfo).first()
        if not device:
            print("❌ 没有设备可测试")
            return False
        
        print(f"📋 使用设备: {device.hostname} (ID: {device.device_id})")
        
        # 模拟监控结果
        test_result = {
            'device_id': device.device_id,
            'overall_health': 'warning',
            'alerts': [
                {
                    'component_type': 'CPU',
                    'component_name': 'CPU-Test',
                    'urgency_level': 'critical',  # 映射到health_status
                    'alert_message': '测试告警'
                }
            ],
            'logs': []
        }
        
        device_info = {
            'hostname': device.hostname,
            'business_type': device.business_type or 'default'
        }
        
        print("📝 执行保存测试...")
        
        # 记录保存前的告警数量
        before_count = db.query(AlertInfo).filter(
            AlertInfo.device_id == device.device_id
        ).count()
        
        # 执行保存
        save_monitoring_result(test_result, device_info)
        
        # 检查保存后的数量
        after_count = db.query(AlertInfo).filter(
            AlertInfo.device_id == device.device_id
        ).count()
        
        print(f"📊 保存前告警数: {before_count}")
        print(f"📊 保存后告警数: {after_count}")
        
        if after_count > before_count:
            print("✅ 保存功能正常！")
            
            # 显示新保存的告警
            new_alert = db.query(AlertInfo).filter(
                AlertInfo.device_id == device.device_id,
                AlertInfo.component_type == 'CPU',
                AlertInfo.component_name == 'CPU-Test'
            ).first()
            
            if new_alert:
                print(f"📋 新告警详情:")
                print(f"  • ID: {new_alert.alert_id}")
                print(f"  • 组件: {new_alert.component_type}/{new_alert.component_name}")
                print(f"  • 健康状态: {new_alert.health_status}")
                print(f"  • 紧急程度: {new_alert.urgency_level}")
            
            return True
        else:
            print("❌ 保存功能异常，数据未增加")
            return False
        
    except Exception as e:
        print(f"❌ 测试保存功能失败: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        return False

def check_scheduled_tasks():
    """检查定时任务状态"""
    print("\n🔍 检查定时任务状态...")
    try:
        db = next(get_sync_db())
        
        # 检查sys_job表中的监控任务
        result = db.execute(text("""
            SELECT job_name, job_group, invoke_target, cron_expression, status
            FROM sys_job 
            WHERE invoke_target LIKE '%redfish%' OR invoke_target LIKE '%monitor%'
        """))
        
        jobs = result.fetchall()
        print(f"📊 找到 {len(jobs)} 个相关任务:")
        
        for job in jobs:
            status_text = "启用" if job.status == '0' else "禁用"
            print(f"  • {job.job_name}: {status_text}")
            print(f"    调用目标: {job.invoke_target}")
            print(f"    Cron: {job.cron_expression}")
        
        if len(jobs) == 0:
            print("❌ 没有找到监控任务！")
            print("💡 需要执行: python add_monitor_jobs.py")
            return False
        
        active_jobs = [job for job in jobs if job.status == '0']
        if len(active_jobs) == 0:
            print("❌ 没有启用的监控任务！")
            return False
        
        print(f"✅ 有 {len(active_jobs)} 个活跃的监控任务")
        return True
        
    except Exception as e:
        print(f"❌ 检查定时任务失败: {e}")
        return False

def main():
    """主诊断函数"""
    print("🚀 开始诊断设备健康状态保存问题...\n")
    
    issues = []
    
    # 1. 检查数据库表结构
    if not check_database_table():
        issues.append("数据库表结构问题")
    
    # 2. 检查设备数据
    if not check_devices():
        issues.append("设备数据问题")
    
    # 3. 检查告警数据
    if not check_alert_data():
        issues.append("告警数据问题")
    
    # 4. 测试保存功能
    if not test_save_function():
        issues.append("保存功能问题")
    
    # 5. 检查定时任务
    if not check_scheduled_tasks():
        issues.append("定时任务问题")
    
    print("\n" + "="*50)
    if issues:
        print("❌ 发现以下问题:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        
        print("\n💡 解决建议:")
        if "数据库表结构问题" in issues:
            print("  • 执行: psql -U username -d database -f backend/sql/create_alert_info_final.sql")
        if "定时任务问题" in issues:
            print("  • 执行: python add_monitor_jobs.py")
        if "设备数据问题" in issues:
            print("  • 检查设备配置和监控启用状态")
    else:
        print("✅ 所有检查都通过！")
        print("🔄 如果问题仍然存在，请检查:")
        print("  • Celery Worker是否运行")
        print("  • APScheduler是否启动")
        print("  • 网络连接是否正常")

if __name__ == "__main__":
    main() 