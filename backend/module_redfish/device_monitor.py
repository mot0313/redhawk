"""
设备监控逻辑模块
负责分析redfish数据并生成告警
"""
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from loguru import logger
from .redfish_client import RedfishClient, decrypt_password


class DeviceMonitor:
    """设备监控器"""
    
    def __init__(self):
        """初始化设备监控器"""
        self.health_status_mapping = {
            "OK": "ok",
            "Warning": "warning", 
            "Critical": "critical",
            "Unknown": "unknown"
        }
        
        self.component_type_mapping = {
            "processors": "cpu",
            "memory": "memory",
            "storage": "disk",
            "power": "power",
            "temperatures": "temperature",
            "fans": "fan"
        }
    
    async def monitor_device(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        监控单个设备
        
        Args:
            device_info: 设备信息字典
            
        Returns:
            Dict: 监控结果
        """
        try:
            # 解密密码
            password = decrypt_password(device_info.get('redfish_password', ''))
            
            # 创建redfish客户端
            client = RedfishClient(
                host=device_info['oob_ip'],
                username=device_info['redfish_username'],
                password=password,
                port=device_info.get('oob_port', 443),
                timeout=30
            )
            
            # 获取所有状态信息
            status_data = await client.get_all_status()
            
            if not status_data:
                return {
                    "device_id": device_info['device_id'],
                    "success": False,
                    "error": "Failed to get device status",
                    "alerts": [],
                    "logs": []
                }
            
            # 分析状态并生成告警
            alerts, logs = await self._analyze_status(device_info, status_data)
            
            return {
                "device_id": device_info['device_id'],
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "overall_health": self._calculate_overall_health(status_data),
                "alerts": alerts,
                "logs": logs,
                "raw_data": status_data
            }
            
        except Exception as e:
            logger.error(f"Error monitoring device {device_info.get('hostname', 'Unknown')}: {str(e)}")
            return {
                "device_id": device_info['device_id'],
                "success": False,
                "error": str(e),
                "alerts": [],
                "logs": []
            }
    
    async def _analyze_status(self, device_info: Dict[str, Any], status_data: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
        """
        分析设备状态并生成告警和日志
        
        Args:
            device_info: 设备信息
            status_data: 状态数据
            
        Returns:
            Tuple[List[Dict], List[Dict]]: (告警列表, 日志列表)
        """
        alerts = []
        logs = []
        
        # 分析系统整体状态
        system_info = status_data.get('system_info', {})
        if system_info:
            alert, log = self._analyze_system_health(device_info, system_info)
            if alert:
                alerts.append(alert)
            if log:
                logs.append(log)
        
        # 分析处理器状态
        processors = status_data.get('processors', [])
        for processor in processors:
            alert, log = self._analyze_processor_health(device_info, processor)
            if alert:
                alerts.append(alert)
            if log:
                logs.append(log)
        
        # 分析内存状态
        memory_modules = status_data.get('memory', [])
        for memory in memory_modules:
            alert, log = self._analyze_memory_health(device_info, memory)
            if alert:
                alerts.append(alert)
            if log:
                logs.append(log)
        
        # 分析存储状态
        storage_devices = status_data.get('storage', [])
        for storage in storage_devices:
            alert, log = self._analyze_storage_health(device_info, storage)
            if alert:
                alerts.append(alert)
            if log:
                logs.append(log)
        
        # 分析电源状态
        power_supplies = status_data.get('power', [])
        for power in power_supplies:
            alert, log = self._analyze_power_health(device_info, power)
            if alert:
                alerts.append(alert)
            if log:
                logs.append(log)
        
        # 分析温度状态
        temperatures = status_data.get('temperatures', [])
        for temp in temperatures:
            alert, log = self._analyze_temperature_health(device_info, temp)
            if alert:
                alerts.append(alert)
            if log:
                logs.append(log)
        
        # 分析风扇状态
        fans = status_data.get('fans', [])
        for fan in fans:
            alert, log = self._analyze_fan_health(device_info, fan)
            if alert:
                alerts.append(alert)
            if log:
                logs.append(log)
        
        return alerts, logs
    
    def _analyze_system_health(self, device_info: Dict[str, Any], system_info: Dict[str, Any]) -> Tuple[Optional[Dict], Optional[Dict]]:
        """分析系统整体健康状态"""
        health_status = system_info.get('health_status', 'Unknown')
        state = system_info.get('state', 'Unknown')
        
        # 创建日志记录
        log_entry = {
            "device_id": device_info['device_id'],
            "component_type": "system",
            "component_name": "System",
            "log_level": self._map_health_to_log_level(health_status),
            "log_message": f"System health: {health_status}, State: {state}",
            "raw_data": json.dumps(system_info),
            "occurrence_time": datetime.now()
        }
        
        # 如果状态不正常，生成告警
        alert_entry = None
        if health_status in ['Warning', 'Critical'] or state not in ['Enabled', 'StandbyOffline']:
            alert_entry = {
                "device_id": device_info['device_id'],
                "alert_source": "redfish",
                "component_type": "system",
                "component_name": "System",
                "alert_level": self._map_health_to_alert_level(health_status),
                "alert_message": f"System health issue: {health_status}, State: {state}",
                "first_occurrence": datetime.now(),
                "raw_data": json.dumps(system_info)
            }
        
        return alert_entry, log_entry
    
    def _analyze_processor_health(self, device_info: Dict[str, Any], processor: Dict[str, Any]) -> Tuple[Optional[Dict], Optional[Dict]]:
        """分析处理器健康状态"""
        health_status = processor.get('health_status', 'Unknown')
        state = processor.get('state', 'Unknown')
        processor_name = processor.get('name', processor.get('id', 'Unknown'))
        
        # 创建日志记录
        log_entry = {
            "device_id": device_info['device_id'],
            "component_type": "cpu",
            "component_name": processor_name,
            "log_level": self._map_health_to_log_level(health_status),
            "log_message": f"Processor {processor_name} health: {health_status}, State: {state}",
            "raw_data": json.dumps(processor),
            "occurrence_time": datetime.now()
        }
        
        # 如果状态不正常，生成告警
        alert_entry = None
        if health_status in ['Warning', 'Critical'] or state not in ['Enabled']:
            alert_entry = {
                "device_id": device_info['device_id'],
                "alert_source": "redfish",
                "component_type": "cpu",
                "component_name": processor_name,
                "alert_level": self._map_health_to_alert_level(health_status),
                "alert_message": f"Processor {processor_name} health issue: {health_status}",
                "first_occurrence": datetime.now(),
                "raw_data": json.dumps(processor)
            }
        
        return alert_entry, log_entry
    
    def _analyze_memory_health(self, device_info: Dict[str, Any], memory: Dict[str, Any]) -> Tuple[Optional[Dict], Optional[Dict]]:
        """分析内存健康状态"""
        health_status = memory.get('health_status', 'Unknown')
        state = memory.get('state', 'Unknown')
        memory_name = memory.get('device_locator', memory.get('name', memory.get('id', 'Unknown')))
        
        # 创建日志记录
        log_entry = {
            "device_id": device_info['device_id'],
            "component_type": "memory",
            "component_name": memory_name,
            "log_level": self._map_health_to_log_level(health_status),
            "log_message": f"Memory {memory_name} health: {health_status}, State: {state}",
            "raw_data": json.dumps(memory),
            "occurrence_time": datetime.now()
        }
        
        # 如果状态不正常，生成告警
        alert_entry = None
        if health_status in ['Warning', 'Critical'] or state not in ['Enabled']:
            alert_entry = {
                "device_id": device_info['device_id'],
                "alert_source": "redfish",
                "component_type": "memory",
                "component_name": memory_name,
                "alert_level": self._map_health_to_alert_level(health_status),
                "alert_message": f"Memory {memory_name} health issue: {health_status}",
                "first_occurrence": datetime.now(),
                "raw_data": json.dumps(memory)
            }
        
        return alert_entry, log_entry
    
    def _analyze_storage_health(self, device_info: Dict[str, Any], storage: Dict[str, Any]) -> Tuple[Optional[Dict], Optional[Dict]]:
        """分析存储健康状态"""
        health_status = storage.get('health_status', 'Unknown')
        state = storage.get('state', 'Unknown')
        storage_name = storage.get('name', storage.get('id', 'Unknown'))
        media_life_left = storage.get('predicted_media_life_left')
        
        # 创建日志记录
        log_message = f"Storage {storage_name} health: {health_status}, State: {state}"
        if media_life_left is not None:
            log_message += f", Media life left: {media_life_left}%"
        
        log_entry = {
            "device_id": device_info['device_id'],
            "component_type": "disk",
            "component_name": storage_name,
            "log_level": self._map_health_to_log_level(health_status),
            "log_message": log_message,
            "raw_data": json.dumps(storage),
            "occurrence_time": datetime.now()
        }
        
        # 如果状态不正常或媒体寿命过低，生成告警
        alert_entry = None
        alert_reasons = []
        
        if health_status in ['Warning', 'Critical']:
            alert_reasons.append(f"health status: {health_status}")
        
        if state not in ['Enabled', 'StandbyOffline']:
            alert_reasons.append(f"state: {state}")
        
        if media_life_left is not None and media_life_left < 10:  # 媒体寿命低于10%
            alert_reasons.append(f"media life left: {media_life_left}%")
        
        if alert_reasons:
            alert_entry = {
                "device_id": device_info['device_id'],
                "alert_source": "redfish",
                "component_type": "disk",
                "component_name": storage_name,
                "alert_level": self._map_health_to_alert_level(health_status),
                "alert_message": f"Storage {storage_name} issue: {', '.join(alert_reasons)}",
                "first_occurrence": datetime.now(),
                "raw_data": json.dumps(storage)
            }
        
        return alert_entry, log_entry
    
    def _analyze_power_health(self, device_info: Dict[str, Any], power: Dict[str, Any]) -> Tuple[Optional[Dict], Optional[Dict]]:
        """分析电源健康状态"""
        health_status = power.get('health_status', 'Unknown')
        state = power.get('state', 'Unknown')
        power_name = power.get('name', power.get('id', 'Unknown'))
        
        # 创建日志记录
        log_entry = {
            "device_id": device_info['device_id'],
            "component_type": "power",
            "component_name": power_name,
            "log_level": self._map_health_to_log_level(health_status),
            "log_message": f"Power supply {power_name} health: {health_status}, State: {state}",
            "raw_data": json.dumps(power),
            "occurrence_time": datetime.now()
        }
        
        # 如果状态不正常，生成告警
        alert_entry = None
        if health_status in ['Warning', 'Critical'] or state not in ['Enabled']:
            alert_entry = {
                "device_id": device_info['device_id'],
                "alert_source": "redfish",
                "component_type": "power",
                "component_name": power_name,
                "alert_level": self._map_health_to_alert_level(health_status),
                "alert_message": f"Power supply {power_name} health issue: {health_status}",
                "first_occurrence": datetime.now(),
                "raw_data": json.dumps(power)
            }
        
        return alert_entry, log_entry
    
    def _analyze_temperature_health(self, device_info: Dict[str, Any], temperature: Dict[str, Any]) -> Tuple[Optional[Dict], Optional[Dict]]:
        """分析温度健康状态"""
        health_status = temperature.get('health_status', 'Unknown')
        state = temperature.get('state', 'Unknown')
        temp_name = temperature.get('name', temperature.get('id', 'Unknown'))
        reading = temperature.get('reading_celsius', 0)
        critical_threshold = temperature.get('upper_threshold_critical')
        
        # 创建日志记录
        log_message = f"Temperature {temp_name} health: {health_status}, Reading: {reading}°C"
        if critical_threshold:
            log_message += f", Critical threshold: {critical_threshold}°C"
        
        log_entry = {
            "device_id": device_info['device_id'],
            "component_type": "temperature",
            "component_name": temp_name,
            "log_level": self._map_health_to_log_level(health_status),
            "log_message": log_message,
            "raw_data": json.dumps(temperature),
            "occurrence_time": datetime.now()
        }
        
        # 如果状态不正常或温度过高，生成告警
        alert_entry = None
        alert_reasons = []
        
        if health_status in ['Warning', 'Critical']:
            alert_reasons.append(f"health status: {health_status}")
        
        if critical_threshold and reading >= critical_threshold:
            alert_reasons.append(f"temperature {reading}°C exceeds critical threshold {critical_threshold}°C")
        
        if alert_reasons:
            alert_entry = {
                "device_id": device_info['device_id'],
                "alert_source": "redfish",
                "component_type": "temperature",
                "component_name": temp_name,
                "alert_level": "critical" if reading >= (critical_threshold or 100) else self._map_health_to_alert_level(health_status),
                "alert_message": f"Temperature {temp_name} issue: {', '.join(alert_reasons)}",
                "first_occurrence": datetime.now(),
                "raw_data": json.dumps(temperature)
            }
        
        return alert_entry, log_entry
    
    def _analyze_fan_health(self, device_info: Dict[str, Any], fan: Dict[str, Any]) -> Tuple[Optional[Dict], Optional[Dict]]:
        """分析风扇健康状态"""
        health_status = fan.get('health_status', 'Unknown')
        state = fan.get('state', 'Unknown')
        fan_name = fan.get('name', fan.get('id', 'Unknown'))
        reading_rpm = fan.get('reading_rpm', 0)
        
        # 创建日志记录
        log_entry = {
            "device_id": device_info['device_id'],
            "component_type": "fan",
            "component_name": fan_name,
            "log_level": self._map_health_to_log_level(health_status),
            "log_message": f"Fan {fan_name} health: {health_status}, Speed: {reading_rpm} RPM",
            "raw_data": json.dumps(fan),
            "occurrence_time": datetime.now()
        }
        
        # 如果状态不正常或风扇停转，生成告警
        alert_entry = None
        alert_reasons = []
        
        if health_status in ['Warning', 'Critical']:
            alert_reasons.append(f"health status: {health_status}")
        
        if state not in ['Enabled']:
            alert_reasons.append(f"state: {state}")
        
        if reading_rpm == 0:
            alert_reasons.append("fan stopped")
        
        if alert_reasons:
            alert_entry = {
                "device_id": device_info['device_id'],
                "alert_source": "redfish",
                "component_type": "fan",
                "component_name": fan_name,
                "alert_level": "critical" if reading_rpm == 0 else self._map_health_to_alert_level(health_status),
                "alert_message": f"Fan {fan_name} issue: {', '.join(alert_reasons)}",
                "first_occurrence": datetime.now(),
                "raw_data": json.dumps(fan)
            }
        
        return alert_entry, log_entry
    
    def _calculate_overall_health(self, status_data: Dict[str, Any]) -> str:
        """计算设备整体健康状态"""
        health_scores = []
        
        # 系统健康状态
        system_health = status_data.get('system_info', {}).get('health_status', 'Unknown')
        health_scores.append(self._health_to_score(system_health))
        
        # 各组件健康状态
        for component_type in ['processors', 'memory', 'storage', 'power', 'temperatures', 'fans']:
            components = status_data.get(component_type, [])
            for component in components:
                health = component.get('health_status', 'Unknown')
                health_scores.append(self._health_to_score(health))
        
        if not health_scores:
            return 'unknown'
        
        # 计算最差的健康状态
        min_score = min(health_scores)
        return self._score_to_health(min_score)
    
    def _health_to_score(self, health: str) -> int:
        """将健康状态转换为分数"""
        mapping = {
            'OK': 4,
            'Warning': 2,
            'Critical': 1,
            'Unknown': 0
        }
        return mapping.get(health, 0)
    
    def _score_to_health(self, score: int) -> str:
        """将分数转换为健康状态"""
        if score >= 4:
            return 'ok'
        elif score >= 2:
            return 'warning'
        elif score >= 1:
            return 'critical'
        else:
            return 'unknown'
    
    def _map_health_to_alert_level(self, health_status: str) -> str:
        """将健康状态映射为告警级别"""
        mapping = {
            'OK': 'info',
            'Warning': 'warning',
            'Critical': 'critical',
            'Unknown': 'warning'
        }
        return mapping.get(health_status, 'warning')
    
    def _map_health_to_log_level(self, health_status: str) -> str:
        """将健康状态映射为日志级别"""
        mapping = {
            'OK': 'info',
            'Warning': 'warning',
            'Critical': 'error',
            'Unknown': 'warning'
        }
        return mapping.get(health_status, 'info') 