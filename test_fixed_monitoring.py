#!/usr/bin/env python3
"""
测试修复后的监控数据保存功能
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from datetime import datetime
from sqlalchemy import text
from database.database import get_sync_db
from module_redfish.models import AlertInfo, DeviceInfo
from module_redfish.celery_tasks import save_monitoring_result
from utils.log_util import logger

def test_database_schema():
    """测试数据库表结构是否正确"""
    try:
        db = next(get_sync_db())
        
        # 检查alert_info表结构
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'alert_info' 
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        logger.info("=== alert_info表结构 ===")
        for column in columns:
            logger.info(f"  {column.column_name}: {column.data_type} ({'nullable' if column.is_nullable == 'YES' else 'not null'})")
        
        # 检查关键字段是否存在
        required_fields = ['health_status', 'urgency_level', 'component_type', 'component_name']
        existing_fields = [col.column_name for col in columns]
        
        for field in required_fields:
            if field in existing_fields:
                logger.info(f"✅ 字段 {field} 存在")
            else:
                logger.error(f"❌ 字段 {field} 不存在")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"检查数据库表结构失败: {str(e)}")
        return False

def test_model_creation():
    """测试AlertInfo模型创建"""
    try:
        # 测试使用新字段创建AlertInfo对象
        alert = AlertInfo(
            device_id=1,
            component_type="CPU",
            component_name="CPU1", 
            health_status="critical",
            urgency_level="urgent",
            alert_status="active",
            first_occurrence=datetime.now()
        )
        
        logger.info("✅ AlertInfo模型创建成功")
        logger.info(f"  component_type: {alert.component_type}")
        logger.info(f"  health_status: {alert.health_status}")
        logger.info(f"  urgency_level: {alert.urgency_level}")
        
        # 测试向后兼容的property
        logger.info(f"  alert_level (兼容): {alert.alert_level}")
        logger.info(f"  alert_type (兼容): {alert.alert_type}")
        
        return True
        
    except Exception as e:
        logger.error(f"AlertInfo模型测试失败: {str(e)}")
        return False

def test_save_monitoring_result():
    """测试保存监控结果"""
    try:
        db = next(get_sync_db())
        
        # 确保存在测试设备
        device = db.query(DeviceInfo).first()
        if not device:
            logger.error("❌ 没有找到测试设备")
            return False
        
        # 模拟监控结果
        test_result = {
            'device_id': device.device_id,
            'overall_health': 'warning',
            'alerts': [
                {
                    'component_type': 'CPU',
                    'component_name': 'CPU1',
                    'urgency_level': 'critical',  # 这会映射到health_status
                    'alert_message': 'CPU温度过高'
                }
            ],
            'logs': [
                {
                    'component_type': 'CPU',
                    'component_name': 'CPU1',
                    'log_level': 'warning',
                    'log_message': 'CPU温度监控日志',
                    'raw_data': '{"temperature": 85}',
                    'occurrence_time': datetime.now()
                }
            ]
        }
        
        device_info = {
            'hostname': device.hostname,
            'business_type': device.business_type or 'default'
        }
        
        # 执行保存
        save_monitoring_result(test_result, device_info)
        
        # 验证保存结果
        alert = db.query(AlertInfo).filter(
            AlertInfo.device_id == device.device_id,
            AlertInfo.component_type == 'CPU',
            AlertInfo.component_name == 'CPU1'
        ).first()
        
        if alert:
            logger.info("✅ 告警数据保存成功")
            logger.info(f"  alert_id: {alert.alert_id}")
            logger.info(f"  device_id: {alert.device_id}")
            logger.info(f"  component_type: {alert.component_type}")
            logger.info(f"  health_status: {alert.health_status}")
            logger.info(f"  urgency_level: {alert.urgency_level}")
            return True
        else:
            logger.error("❌ 告警数据未保存成功")
            return False
            
    except Exception as e:
        logger.error(f"保存监控结果测试失败: {str(e)}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        return False

def main():
    """主测试函数"""
    logger.info("🔍 开始测试修复后的监控数据保存功能...")
    
    # 1. 测试数据库表结构
    logger.info("\n1. 测试数据库表结构")
    if not test_database_schema():
        logger.error("💥 数据库表结构测试失败！请先执行 sql/create_alert_info_final.sql")
        return False
    
    # 2. 测试模型创建
    logger.info("\n2. 测试AlertInfo模型")
    if not test_model_creation():
        logger.error("💥 AlertInfo模型测试失败！")
        return False
    
    # 3. 测试保存功能
    logger.info("\n3. 测试保存监控结果")
    if not test_save_monitoring_result():
        logger.error("💥 保存监控结果测试失败！")
        return False
    
    logger.info("\n🎉 所有测试通过！修复成功！")
    return True

if __name__ == "__main__":
    main() 