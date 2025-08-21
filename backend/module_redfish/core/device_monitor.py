"""
设备监控逻辑模块
负责分析redfish数据并生成告警（已移除日志生成，专注告警分析）
"""
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from loguru import logger
from .redfish_client import RedfishClient, decrypt_password
from ..service.connectivity_service import ConnectivityService
from ..adapters import get_vendor_adaptor
from ..utils.component_type_mapper import to_hardware_code


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
            "fans": "fan",
            "connectivity": "downtime"
        }
    
    def _get_component_status(self, component_data: Dict[str, Any]) -> Tuple[str, str]:
        """
        健壮地从组件数据中获取健康状态和运行状态。
        处理状态信息可能在顶层或嵌套在 'Status' 键下的情况。
        
        Args:
            component_data: 单个组件的字典数据
            
        Returns:
            Tuple[str, str]: (health_status, state)
        """
        status_block = component_data.get('Status', {})
        
        health_status = component_data.get('health_status') or status_block.get('Health', 'Unknown')
        state = component_data.get('state') or status_block.get('State', 'Unknown')
        
        return health_status, state

    async def monitor_device(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        监控单个设备
        
        Args:
            device_info: 设备信息字典
            
        Returns:
            Dict: 监控结果（已移除日志生成）
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
            # 依据厂商适配并归一化组件结构
            system_info = status_data.get('system_info') or {}
            manufacturer = (system_info.get('manufacturer') or system_info.get('Manufacturer') or '').upper()
            adaptor = get_vendor_adaptor(manufacturer)
            # 归一化各组件
            normalized = {
                'system_info': adaptor.normalize_system(system_info) if system_info else {},
                'processors': adaptor.normalize_processors(status_data.get('processors', [])),
                'memory': adaptor.normalize_memory(status_data.get('memory', [])),
                'storage': adaptor.normalize_storage(status_data.get('storage', [])),
                'power': adaptor.normalize_power(status_data.get('power', [])),
            }
            temps, fans = adaptor.normalize_thermal(status_data.get('temperatures', []), status_data.get('fans', []))
            normalized['temperatures'] = temps
            normalized['fans'] = fans
            status_data = adaptor.postprocess(normalized)

            # 关键统计日志（帮助排查未落库/未识别问题）
            try:
                logger.info(
                    "Redfish normalized summary | host={} manufacturer={} proc={} mem={} storage={} power={} temp={} fan={}",
                    device_info.get('hostname') or device_info.get('oob_ip'),
                    manufacturer or 'Unknown',
                    len(status_data.get('processors', [])),
                    len(status_data.get('memory', [])),
                    len(status_data.get('storage', [])),
                    len(status_data.get('power', [])),
                    len(status_data.get('temperatures', [])),
                    len(status_data.get('fans', []))
                )
            except Exception:
                pass
            
            if not status_data:
                return {
                    "device_id": device_info['device_id'],
                    "success": False,
                    "error": "Failed to get device status",
                    "alerts": []
                }
            
            # 分析状态并生成告警（不再生成日志）
            alerts, all_components = await self._analyze_status(device_info, status_data)
            
            return {
                "device_id": device_info['device_id'],
                "success": True,
                "timestamp": datetime.now().isoformat(),
                 "overall_health": self._calculate_overall_health(status_data),
                "alerts": alerts,
                "all_components": all_components,
                "raw_data": status_data
            }
            
        except Exception as e:
            logger.error(f"Error monitoring device {device_info.get('hostname', 'Unknown')}: {str(e)}")
            return {
                "device_id": device_info['device_id'],
                "success": False,
                "error": str(e),
                "alerts": []
            }
    
    async def _analyze_status(self, device_info: Dict[str, Any], status_data: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
        """
        分析设备状态，生成告警，并返回所有组件的健康状态
        
        Args:
            device_info: 设备信息
            status_data: 状态数据
            
        Returns:
            Tuple[List[Dict], List[Dict]]: (告警列表, 所有组件状态列表)
        """
        alerts = []
        all_components = []
        
        # 检查业务IP连通性
        business_ip = device_info.get('business_ip')
        if business_ip:
            try:
                connectivity_result = await ConnectivityService.check_device_business_ip_connectivity(
                    db=None, business_ip=business_ip
                )
                
                # 根据连通性结果生成组件状态
                is_online = connectivity_result.get('online', False)
                health_status = 'OK' if is_online else 'Critical'
                
                component_status = {
                    "component_type": to_hardware_code("downtime", {}),
                    "component_name": "宕机",
                    "health_status": self._normalize_health_status(health_status)
                }
                all_components.append(component_status)
                
                # 如果离线，生成告警
                if not is_online:
                    alert_entry = {
                        "device_id": device_info['device_id'],
                        "alert_source": "downtime_detection",
                        "component_type": to_hardware_code("downtime", {}),
                        "component_name": "宕机",
                        "health_status": self._normalize_health_status(health_status),
                        "urgency_level": self._map_health_to_urgency_level(health_status),
                        "alert_message": f"设备宕机告警: 业务IP {business_ip} 无法连通 - {connectivity_result.get('error', '连接失败')}",
                        "first_occurrence": datetime.now(),
                        "raw_data": json.dumps(connectivity_result)
                    }
                    alerts.append(alert_entry)
                    
            except Exception as e:
                logger.error(f"Error checking business IP connectivity for {business_ip}: {str(e)}")
                # 连通性检查失败时，记录为未知状态
                component_status = {
                    "component_type": to_hardware_code("downtime", {}),
                    "component_name": "宕机",
                    "health_status": "unknown"
                }
                all_components.append(component_status)
        
        # 分析系统整体状态
        system_info = status_data.get('system_info', {})
        if system_info:
            component_status, alert = self._analyze_system_health(device_info, system_info)
            if component_status:
                component_status["component_type"] = to_hardware_code(component_status["component_type"], system_info)
                all_components.append(component_status)
            if alert:
                alerts.append(alert)
        
        # 分析处理器状态
        processors = status_data.get('processors', [])
        for processor in processors:
            component_status, alert = self._analyze_processor_health(device_info, processor)
            if component_status:
                component_status["component_type"] = to_hardware_code(component_status["component_type"], processor)
                all_components.append(component_status)
            if alert:
                alerts.append(alert)
        
        # 分析内存状态
        memory_modules = status_data.get('memory', [])
        try:
            # 采样前3条DIMM，记录名称与健康，便于对比check_redfish
            for idx, m in enumerate(memory_modules[:3]):
                hs, st = self._get_component_status(m)
                name = m.get('device_locator') or m.get('name') or m.get('id') or f"DIMM#{idx}"
                logger.info("Memory sample [{}] name={} health={} state={}", idx, name, hs, st)
        except Exception:
            pass
        for memory in memory_modules:
            component_status, alert = self._analyze_memory_health(device_info, memory)
            if component_status:
                component_status["component_type"] = to_hardware_code(component_status["component_type"], memory)
                all_components.append(component_status)
            if alert:
                alerts.append(alert)
        try:
            mem_comp = [c for c in all_components if c.get('component_type') == 'memory']
            mem_bad = [c for c in mem_comp if c.get('health_status') in ('warning', 'critical')]
            logger.info("Memory analyzed | components={} abnormal={}", len(mem_comp), len(mem_bad))
        except Exception:
            pass

        # MemorySummary 兜底（方案A）：若DIMM未触发异常且汇总健康为告警，则追加聚合内存告警（Fujitsu 例外）
        try:
            sys_info_norm = status_data.get('system_info', {}) or {}
            raw_pre = sys_info_norm.get('raw', {}) or {}
            # 兼容多种字段名
            manufacturer = (
                raw_pre.get('Manufacturer')
                or raw_pre.get('manufacturer')
                or sys_info_norm.get('manufacturer')
                or ''
            )
            is_fujitsu = isinstance(manufacturer, str) and 'FUJITSU' in manufacturer.upper()
            # DIMM 是否已有异常
            dimm_has_issue = any(
                (comp.get('component_type') in ('memory', 'MEMORY')) and (comp.get('health_status') in ('warning', 'critical'))
                for comp in all_components
            )
            if not dimm_has_issue and not is_fujitsu:
                # 优先使用系统原始原生数据中的 MemorySummary
                sys_raw_data = raw_pre.get('raw_data') or raw_pre
                # 也兼容已提取的 memory_summary 字段
                mem_summary = (sys_raw_data.get('MemorySummary')
                               or sys_info_norm.get('memory_summary')
                               or {})
                mem_status = (mem_summary.get('Status') or {})
                # HealthRollup 优先，其次 Health
                rollup = mem_status.get('HealthRollup') or mem_status.get('Health')
                if rollup in ('Warning', 'Critical'):
                    logger.info("MemorySummary fallback triggered | manufacturer={} rollup={}", manufacturer or 'Unknown', rollup)
                    summary_component = {
                        "component_type": to_hardware_code("memory", {}),
                        "component_name": "MemorySummary",
                        "health_status": self._normalize_health_status(rollup)
                    }
                    all_components.append(summary_component)
                    alerts.append({
                        "device_id": device_info['device_id'],
                        "alert_source": "redfish",
                        "component_type": summary_component["component_type"],
                        "component_name": "MemorySummary",
                        "health_status": summary_component["health_status"],
                        "urgency_level": self._map_health_to_urgency_level(rollup),
                        "alert_message": f"Memory summary health issue: {rollup}",
                        "first_occurrence": datetime.now(),
                        "raw_data": json.dumps({"MemorySummary": mem_summary})
                    })
        except Exception as e:
            logger.warning(f"MemorySummary fallback failed: {e}")
        
        # 分析存储状态
        storage_devices = status_data.get('storage', [])
        for storage in storage_devices:
            component_status, alert = self._analyze_storage_health(device_info, storage)
            if component_status:
                component_status["component_type"] = to_hardware_code(component_status["component_type"], storage)
                all_components.append(component_status)
            if alert:
                alerts.append(alert)
        
        # 分析电源状态
        power_supplies = status_data.get('power', [])
        for power in power_supplies:
            component_status, alert = self._analyze_power_health(device_info, power)
            if component_status:
                component_status["component_type"] = to_hardware_code(component_status["component_type"], power)
                all_components.append(component_status)
            if alert:
                alerts.append(alert)
        
        # 分析温度状态
        temperatures = status_data.get('temperatures', [])
        for temp in temperatures:
            component_status, alert = self._analyze_temperature_health(device_info, temp)
            if component_status:
                component_status["component_type"] = to_hardware_code(component_status["component_type"], temp)
                all_components.append(component_status)
            if alert:
                alerts.append(alert)
        
        # 分析风扇状态
        fans = status_data.get('fans', [])
        for fan in fans:
            component_status, alert = self._analyze_fan_health(device_info, fan)
            if component_status:
                component_status["component_type"] = to_hardware_code(component_status["component_type"], fan)
                all_components.append(component_status)
            if alert:
                alerts.append(alert)
        
        return alerts, all_components
    
    def _analyze_system_health(self, device_info: Dict[str, Any], system_info: Dict[str, Any]) -> Tuple[Optional[Dict], Optional[Dict]]:
        """分析系统健康状态，返回组件状态和告警"""
        health_status, state = self._get_component_status(system_info)
        
        component_status = {
            "component_type": "system",
            "component_name": "System",
            "health_status": self._normalize_health_status(health_status)
        }
        
        alert_entry = None
        if health_status in ['Warning', 'Critical']:
            alert_entry = {
                "device_id": device_info['device_id'],
                "alert_source": "redfish",
                "component_type": "system",
                "component_name": "System",
                "health_status": self._normalize_health_status(health_status),
                "urgency_level": self._map_health_to_urgency_level(health_status),
                "alert_message": f"System health issue: {health_status}, State: {state}",
                "first_occurrence": datetime.now(),
                "raw_data": json.dumps(system_info)
            }
        
        return component_status, alert_entry
    
    def _analyze_processor_health(self, device_info: Dict[str, Any], processor: Dict[str, Any]) -> Tuple[Optional[Dict], Optional[Dict]]:
        """分析处理器健康状态，返回组件状态和告警"""
        health_status, state = self._get_component_status(processor)
        processor_name = processor.get('socket', processor.get('id', 'Unknown'))
        
        if state == 'Absent':
            return None, None

        component_status = {
            "component_type": "processor",
            "component_name": processor_name,
            "health_status": self._normalize_health_status(health_status)
        }

        alert_entry = None
        if health_status in ['Warning', 'Critical']:
            alert_entry = {
                "device_id": device_info['device_id'],
                "alert_source": "redfish",
                "component_type": "processor",
                "component_name": processor_name,
                "health_status": self._normalize_health_status(health_status),
                "urgency_level": self._map_health_to_urgency_level(health_status),
                "alert_message": f"Processor {processor_name} health issue: {health_status}, State: {state}",
                "first_occurrence": datetime.now(),
                "raw_data": json.dumps(processor)
            }
        
        return component_status, alert_entry
    
    def _analyze_memory_health(self, device_info: Dict[str, Any], memory: Dict[str, Any]) -> Tuple[Optional[Dict], Optional[Dict]]:
        """分析内存健康状态，返回组件状态和告警"""
        health_status, state = self._get_component_status(memory)
        # 兼容适配器归一化后的字段（component_name），以及 Redfish 原生字段
        memory_name = (
            memory.get('component_name')
            or memory.get('device_locator')
            or memory.get('name')
            or memory.get('id')
            or 'Unknown'
        )
        
        if state == 'Absent':
            return None, None

        component_status = {
            "component_type": "memory",
            "component_name": memory_name,
            "health_status": self._normalize_health_status(health_status)
        }

        alert_entry = None
        if health_status in ['Warning', 'Critical']:
            alert_entry = {
                "device_id": device_info['device_id'],
                "alert_source": "redfish",
                "component_type": "memory",
                "component_name": memory_name,
                "health_status": self._normalize_health_status(health_status),
                "urgency_level": self._map_health_to_urgency_level(health_status),
                "alert_message": f"Memory {memory_name} health issue: {health_status}, State: {state}",
                "first_occurrence": datetime.now(),
                "raw_data": json.dumps(memory)
            }
        
        return component_status, alert_entry
    
    def _analyze_storage_health(self, device_info: Dict[str, Any], storage: Dict[str, Any]) -> Tuple[Optional[Dict], Optional[Dict]]:
        """分析存储健康状态，返回组件状态和告警"""
        health_status, state = self._get_component_status(storage)
        storage_name = storage.get('name', storage.get('id', 'Unknown'))
        
        if state == 'Absent':
            return None, None

        component_status = {
            "component_type": "storage",
            "component_name": storage_name,
            "health_status": self._normalize_health_status(health_status)
        }

        alert_entry = None
        if health_status in ['Warning', 'Critical']:
            alert_entry = {
                "device_id": device_info['device_id'],
                "alert_source": "redfish",
                "component_type": "storage",
                "component_name": storage_name,
                "health_status": self._normalize_health_status(health_status),
                "urgency_level": self._map_health_to_urgency_level(health_status),
                "alert_message": f"Storage {storage_name} health issue: {health_status}, State: {state}",
                "first_occurrence": datetime.now(),
                "raw_data": json.dumps(storage)
            }
        
        return component_status, alert_entry
    
    def _analyze_power_health(self, device_info: Dict[str, Any], power: Dict[str, Any]) -> Tuple[Optional[Dict], Optional[Dict]]:
        """分析电源健康状态，返回组件状态和告警"""
        health_status, state = self._get_component_status(power)
        power_name = power.get('name', power.get('id', 'Unknown'))
        
        if state == 'Absent':
            return None, None

        component_status = {
            "component_type": "power",
            "component_name": power_name,
            "health_status": self._normalize_health_status(health_status)
        }

        alert_entry = None
        if health_status in ['Warning', 'Critical']:
            alert_entry = {
                "device_id": device_info['device_id'],
                "alert_source": "redfish",
                "component_type": "power",
                "component_name": power_name,
                "health_status": self._normalize_health_status(health_status),
                "urgency_level": self._map_health_to_urgency_level(health_status),
                "alert_message": f"Power {power_name} health issue: {health_status}, State: {state}",
                "first_occurrence": datetime.now(),
                "raw_data": json.dumps(power)
            }
        
        return component_status, alert_entry
    
    def _analyze_temperature_health(self, device_info: Dict[str, Any], temperature: Dict[str, Any]) -> Tuple[Optional[Dict], Optional[Dict]]:
        """分析温度健康状态，返回组件状态和告警"""
        health_status, state = self._get_component_status(temperature)
        temp_name = temperature.get('name', temperature.get('id', 'Unknown'))
        reading = temperature.get('reading_celsius', 'N/A')
        
        if state == 'Absent':
            return None, None

        component_status = {
            "component_type": "temperature",
            "component_name": temp_name,
            "health_status": self._normalize_health_status(health_status)
        }

        alert_entry = None
        if health_status in ['Warning', 'Critical']:
            alert_entry = {
                "device_id": device_info['device_id'],
                "alert_source": "redfish",
                "component_type": "temperature",
                "component_name": temp_name,
                "health_status": self._normalize_health_status(health_status),
                "urgency_level": self._map_health_to_urgency_level(health_status),
                "alert_message": f"Temperature {temp_name} is {health_status} ({reading}°C)",
                "first_occurrence": datetime.now(),
                "raw_data": json.dumps(temperature)
            }
        
        return component_status, alert_entry
    
    def _analyze_fan_health(self, device_info: Dict[str, Any], fan: Dict[str, Any]) -> Tuple[Optional[Dict], Optional[Dict]]:
        """分析风扇健康状态，返回组件状态和告警"""
        health_status, state = self._get_component_status(fan)
        fan_name = fan.get('name', fan.get('id', 'Unknown'))
        reading = fan.get('reading', 'N/A')
        
        if state == 'Absent':
            return None, None

        component_status = {
            "component_type": "fan",
            "component_name": fan_name,
            "health_status": self._normalize_health_status(health_status)
        }

        alert_entry = None
        if health_status in ['Warning', 'Critical']:
            alert_entry = {
                "device_id": device_info['device_id'],
                "alert_source": "redfish",
                "component_type": "fan",
                "component_name": fan_name,
                "health_status": self._normalize_health_status(health_status),
                "urgency_level": self._map_health_to_urgency_level(health_status),
                "alert_message": f"Fan {fan_name} health issue: {health_status} (Reading: {reading} RPM)",
                "first_occurrence": datetime.now(),
                "raw_data": json.dumps(fan)
            }
        
        return component_status, alert_entry

    def _calculate_overall_health(self, status_data: Dict[str, Any]) -> str:
        """
        计算设备整体健康状态
        
        Args:
            status_data: 状态数据
            
        Returns:
            str: 整体健康状态
        """
        all_health_statuses = []
        
        # 提取所有组件的健康状态
        components_map = {
            'system_info': [status_data.get('system_info', {})],
            'processors': status_data.get('processors', []),
            'memory': status_data.get('memory', []),
            'storage': status_data.get('storage', []),
            'power': status_data.get('power', []),
            'temperatures': status_data.get('temperatures', []),
            'fans': status_data.get('fans', [])
        }
        
        for component_list in components_map.values():
            for component in component_list:
                if component: # 确保组件信息存在
                    health, state = self._get_component_status(component)
                    # 忽略状态为 'Absent' 的组件
                    if state != 'Absent':
                        # 只有明确的健康状态才参与计算
                        if health in ['OK', 'Warning', 'Critical']:
                            all_health_statuses.append(health)
        
        if not all_health_statuses:
            return "unknown"

        # 使用评分系统计算总体健康度
        # Critical=3, Warning=2, OK=1, Unknown=0
        scores = [self._health_to_score(h) for h in all_health_statuses]
        
        # 最高分决定最终状态
        max_score = max(scores) if scores else 0
        
        return self._score_to_health(max_score)
    
    def _health_to_score(self, health: str) -> int:
        return {"Critical": 3, "Warning": 2, "OK": 1, "Unknown": 0}.get(health, 0)
    
    def _score_to_health(self, score: int) -> str:
        return {3: "critical", 2: "warning", 1: "ok", 0: "unknown"}.get(score, "unknown")
    
    def _map_health_to_urgency_level(self, health_status: str) -> str:
        """根据健康状态初步映射一个临时的紧急程度"""
        if health_status == 'Critical':
            return 'urgent'
        return 'scheduled'
    
    def _normalize_health_status(self, health_status: str) -> str:
        return self.health_status_mapping.get(health_status, "unknown")
    
    def _map_health_to_log_level(self, health_status: str) -> str:
        """将健康状态映射为日志级别（保留方法以备将来使用）"""
        mapping = {
            'OK': 'info',
            'Warning': 'warning',
            'Critical': 'error',
            'Unknown': 'warning'
        }
        return mapping.get(health_status, 'info') 