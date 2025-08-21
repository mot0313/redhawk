"""
设备可用性监控器
基于业务IP连通性检测设备是否宕机，生成相应告警
"""
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

from ..service.connectivity_service import ConnectivityService
from ..utils.component_type_mapper import to_hardware_code


class DeviceAvailabilityMonitor:
    """设备可用性监控器"""
    
    def __init__(self):
        """初始化监控器"""
        self.monitor_type = "availability"
        
    async def check_device_availability(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        检测单个设备的可用性状态
        
        Args:
            device_info: 设备信息字典，必须包含device_id和business_ip
            
        Returns:
            Dict: 可用性检测结果
        """
        device_id = device_info.get('device_id')
        hostname = device_info.get('hostname', f'Device-{device_id}')
        business_ip = device_info.get('business_ip')
        
        logger.info(f"开始检测设备可用性 | device_id={device_id} hostname={hostname} business_ip={business_ip}")
        
        # 检查业务IP是否存在
        if not business_ip:
            logger.warning(f"设备 {hostname} 无业务IP，跳过可用性检测")
            return {
                "success": True,
                "device_id": device_id,
                "hostname": hostname,
                "availability_status": "unknown",
                "message": "设备无业务IP配置",
                "components": [],
                "alerts": [],
                "check_time": datetime.now().isoformat()
            }
        
        try:
            # 执行连通性检测
            start_time = datetime.now()
            connectivity_result = await ConnectivityService.check_device_business_ip_connectivity(
                db=None,  # 不需要数据库会话，直接使用business_ip参数
                business_ip=business_ip
            )
            
            is_online = connectivity_result.get('online', False)
            check_time = datetime.now()
            response_time = (check_time - start_time).total_seconds()
            
            # 生成组件状态信息
            components = []
            alerts = []
            
            if is_online:
                # 设备在线，生成正常状态的组件
                availability_status = "online"
                health_status = "ok"
                message = f"设备在线 | 响应时间: {response_time:.2f}s"
                
                logger.info(f"设备可用性检测成功 | {hostname} 在线")
                
            else:
                # 设备离线，生成告警
                availability_status = "offline"
                health_status = "critical"
                error_msg = connectivity_result.get('error', '网络连接失败')
                message = f"设备宕机 | 错误: {error_msg}"
                
                logger.warning(f"设备宕机检测 | {hostname} 离线 | {error_msg}")
                
                # 生成告警信息
                alert = {
                    "device_id": device_id,
                    "alert_source": "availability_monitor",
                    "component_type": to_hardware_code("downtime", {}),
                    "component_name": "宕机检测",
                    "health_status": health_status,
                    "urgency_level": "critical",  # 宕机默认为critical，后续会根据业务规则调整
                    "alert_message": f"设备宕机告警: {error_msg}",
                    "first_occurrence": check_time,
                    "raw_data": json.dumps({
                        "business_ip": business_ip,
                        "connectivity_result": connectivity_result,
                        "check_time": check_time.isoformat()
                    })
                }
                alerts.append(alert)
            
            # 生成组件状态（无论在线离线都记录）
            component = {
                "component_type": to_hardware_code("downtime", {}),
                "component_name": "宕机检测",
                "health_status": health_status
            }
            components.append(component)
            
            return {
                "success": True,
                "device_id": device_id,
                "hostname": hostname,
                "availability_status": availability_status,
                "message": message,
                "components": components,
                "alerts": alerts,
                "check_time": check_time.isoformat(),
                "response_time_seconds": response_time,
                "raw_connectivity_result": connectivity_result
            }
            
        except Exception as e:
            logger.error(f"设备可用性检测失败 | {hostname} | 错误: {str(e)}")
            return {
                "success": False,
                "device_id": device_id,
                "hostname": hostname,
                "availability_status": "error",
                "message": f"可用性检测异常: {str(e)}",
                "components": [],
                "alerts": [],
                "check_time": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def batch_check_devices_availability(self, devices_info: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量检测多个设备的可用性状态
        
        Args:
            devices_info: 设备信息列表
            
        Returns:
            Dict: 批量检测结果汇总
        """
        logger.info(f"开始批量可用性检测 | 设备数量: {len(devices_info)}")
        
        start_time = datetime.now()
        
        # 并发执行所有设备的可用性检测
        tasks = [
            self.check_device_availability(device_info) 
            for device_info in devices_info
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 统计结果
        total_devices = len(devices_info)
        successful_checks = 0
        online_devices = 0
        offline_devices = 0
        error_devices = 0
        total_alerts = 0
        
        valid_results = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"设备 {devices_info[i].get('hostname', 'Unknown')} 检测异常: {str(result)}")
                error_devices += 1
                continue
                
            if not result.get('success', False):
                error_devices += 1
                continue
                
            valid_results.append(result)
            successful_checks += 1
            
            availability_status = result.get('availability_status', 'unknown')
            if availability_status == 'online':
                online_devices += 1
            elif availability_status == 'offline':
                offline_devices += 1
            else:
                error_devices += 1
                
            total_alerts += len(result.get('alerts', []))
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        summary = {
            "success": True,
            "batch_check_time": end_time.isoformat(),
            "duration_seconds": duration,
            "statistics": {
                "total_devices": total_devices,
                "successful_checks": successful_checks,
                "online_devices": online_devices,
                "offline_devices": offline_devices,
                "error_devices": error_devices,
                "total_alerts_generated": total_alerts
            },
            "results": valid_results
        }
        
        logger.info(
            f"批量可用性检测完成 | "
            f"总数: {total_devices} | 在线: {online_devices} | "
            f"离线: {offline_devices} | 异常: {error_devices} | "
            f"告警: {total_alerts} | 耗时: {duration:.2f}s"
        )
        
        return summary
    
    def get_monitor_info(self) -> Dict[str, str]:
        """获取监控器信息"""
        return {
            "monitor_type": self.monitor_type,
            "description": "设备可用性监控器 - 基于业务IP连通性检测设备宕机状态",
            "component_type": to_hardware_code("downtime", {}),
            "alert_source": "availability_monitor"
        }
