"""
告警紧急度联动查询服务
实现设备业务类型与硬件类型的紧急度自动匹配
"""
from typing import Optional, Dict, Any
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from module_redfish.models import DeviceInfo, BusinessHardwareUrgencyRules, AlertInfo
from utils.log_util import logger


class AlertUrgencyService:
    """告警紧急度联动服务"""
    
    @classmethod
    async def get_alert_urgency_by_device_and_component(
        cls,
        db: AsyncSession,
        device_id: int,
        component_type: str
    ) -> Dict[str, Any]:
        """
        根据设备ID和组件类型获取告警紧急度
        
        Args:
            db: 数据库会话
            device_id: 设备ID
            component_type: 组件类型（硬件类型）
            
        Returns:
            Dict[str, Any]: 紧急度信息
        """
        try:
            # 1. 获取设备的业务类型
            device_result = await db.execute(
                select(DeviceInfo.business_type, DeviceInfo.hostname)
                .where(DeviceInfo.device_id == device_id)
            )
            device_info = device_result.first()
            
            if not device_info:
                logger.warning(f"设备不存在: {device_id}")
                return {
                    'urgency_level': 'scheduled',
                    'matched': False,
                    'reason': '设备不存在',
                    'rule_id': None
                }
            
            business_type = device_info.business_type
            hostname = device_info.hostname
            
            # 2. 根据业务类型和硬件类型查询紧急度规则（支持大小写不敏感匹配）
            rule_result = await db.execute(
                select(BusinessHardwareUrgencyRules)
                .where(
                    and_(
                        BusinessHardwareUrgencyRules.business_type == business_type,
                        BusinessHardwareUrgencyRules.hardware_type == component_type.upper(),
                        BusinessHardwareUrgencyRules.is_active == 1
                    )
                )
            )
            rule = rule_result.scalar_one_or_none()
            
            if rule:
                logger.info(f"匹配到紧急度规则: 设备[{hostname}] 业务类型[{business_type}] 硬件类型[{component_type}] -> {rule.urgency_level}")
                return {
                    'urgency_level': rule.urgency_level,
                    'matched': True,
                    'reason': f'匹配规则: {rule.description or ""}',
                    'rule_id': rule.rule_id,
                    'business_type': business_type,
                    'hardware_type': component_type,
                    'hostname': hostname
                }
            else:
                logger.info(f"未匹配到紧急度规则: 设备[{hostname}] 业务类型[{business_type}] 硬件类型[{component_type}] -> 默认择期")
                return {
                    'urgency_level': 'scheduled',
                    'matched': False,
                    'reason': f'未找到匹配规则: {business_type} + {component_type}',
                    'rule_id': None,
                    'business_type': business_type,
                    'hardware_type': component_type,
                    'hostname': hostname
                }
                
        except Exception as e:
            logger.error(f"查询告警紧急度失败: {str(e)}")
            return {
                'urgency_level': 'scheduled',
                'matched': False,
                'reason': f'查询异常: {str(e)}',
                'rule_id': None
            }
    
    @classmethod
    async def get_alert_urgency_by_alert_id(
        cls,
        db: AsyncSession,
        alert_id: int
    ) -> Dict[str, Any]:
        """
        根据告警ID获取告警紧急度
        
        Args:
            db: 数据库会话
            alert_id: 告警ID
            
        Returns:
            Dict[str, Any]: 紧急度信息
        """
        try:
            # 获取告警信息
            alert_result = await db.execute(
                select(AlertInfo.device_id, AlertInfo.component_type)
                .where(AlertInfo.alert_id == alert_id)
            )
            alert_info = alert_result.first()
            
            if not alert_info:
                logger.warning(f"告警不存在: {alert_id}")
                return {
                    'urgency_level': 'scheduled',
                    'matched': False,
                    'reason': '告警不存在',
                    'rule_id': None
                }
            
            # 调用设备和组件查询方法
            return await cls.get_alert_urgency_by_device_and_component(
                db, alert_info.device_id, alert_info.component_type
            )
            
        except Exception as e:
            logger.error(f"根据告警ID查询紧急度失败: {str(e)}")
            return {
                'urgency_level': 'scheduled',
                'matched': False,
                'reason': f'查询异常: {str(e)}',
                'rule_id': None
            }
    
    @classmethod
    async def batch_update_alert_urgency(
        cls,
        db: AsyncSession,
        alert_ids: list[int] = None,
        device_ids: list[int] = None
    ) -> Dict[str, Any]:
        """
        批量更新告警紧急度
        
        Args:
            db: 数据库会话
            alert_ids: 告警ID列表（可选）
            device_ids: 设备ID列表（可选）
            
        Returns:
            Dict[str, Any]: 更新结果统计
        """
        try:
            updated_count = 0
            urgent_count = 0
            scheduled_count = 0
            error_count = 0
            
            # 构建查询条件
            query = select(AlertInfo.alert_id, AlertInfo.device_id, AlertInfo.component_type)
            
            if alert_ids:
                query = query.where(AlertInfo.alert_id.in_(alert_ids))
            elif device_ids:
                query = query.where(AlertInfo.device_id.in_(device_ids))
            else:
                # 如果都没指定，更新所有活跃告警
                query = query.where(AlertInfo.alert_status == 'active')
            
            result = await db.execute(query)
            alerts = result.fetchall()
            
            for alert in alerts:
                try:
                    urgency_info = await cls.get_alert_urgency_by_device_and_component(
                        db, alert.device_id, alert.component_type
                    )
                    
                    # 更新告警的紧急度（这里需要在AlertInfo表中添加urgency_level字段）
                    # 或者可以通过alert_type字段来标识紧急度
                    urgency_level = urgency_info['urgency_level']
                    
                    # 统计
                    if urgency_level == 'urgent':
                        urgent_count += 1
                    else:
                        scheduled_count += 1
                    
                    updated_count += 1
                    
                except Exception as e:
                    logger.error(f"更新告警 {alert.alert_id} 紧急度失败: {str(e)}")
                    error_count += 1
            
            await db.commit()
            
            logger.info(f"批量更新告警紧急度完成: 总计{updated_count}, 紧急{urgent_count}, 择期{scheduled_count}, 错误{error_count}")
            
            return {
                'success': True,
                'total_count': len(alerts),
                'updated_count': updated_count,
                'urgent_count': urgent_count,
                'scheduled_count': scheduled_count,
                'error_count': error_count
            }
            
        except Exception as e:
            logger.error(f"批量更新告警紧急度失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    async def get_urgency_statistics_by_device(
        cls,
        db: AsyncSession,
        device_id: int
    ) -> Dict[str, Any]:
        """
        获取指定设备的紧急度统计
        
        Args:
            db: 数据库会话
            device_id: 设备ID
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            # 获取设备所有活跃告警
            alerts_result = await db.execute(
                select(AlertInfo.alert_id, AlertInfo.component_type)
                .where(
                    and_(
                        AlertInfo.device_id == device_id,
                        AlertInfo.alert_status == 'active'
                    )
                )
            )
            alerts = alerts_result.fetchall()
            
            urgent_alerts = []
            scheduled_alerts = []
            
            for alert in alerts:
                urgency_info = await cls.get_alert_urgency_by_device_and_component(
                    db, device_id, alert.component_type
                )
                
                alert_data = {
                    'alert_id': alert.alert_id,
                    'component_type': alert.component_type,
                    'urgency_level': urgency_info['urgency_level'],
                    'matched': urgency_info['matched'],
                    'rule_id': urgency_info['rule_id']
                }
                
                if urgency_info['urgency_level'] == 'urgent':
                    urgent_alerts.append(alert_data)
                else:
                    scheduled_alerts.append(alert_data)
            
            return {
                'device_id': device_id,
                'total_alerts': len(alerts),
                'urgent_count': len(urgent_alerts),
                'scheduled_count': len(scheduled_alerts),
                'urgent_alerts': urgent_alerts,
                'scheduled_alerts': scheduled_alerts
            }
            
        except Exception as e:
            logger.error(f"获取设备紧急度统计失败: {str(e)}")
            return {
                'device_id': device_id,
                'error': str(e)
            } 