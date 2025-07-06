"""
Redfish客户端模块
参考check_redfish项目实现
"""
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import redfish
from redfish.rest.v1 import ServerDownOrUnreachableError
from loguru import logger
from cryptography.fernet import Fernet
import os
from config.env import RedfishConfig


class RedfishClient:
    """Redfish客户端类"""
    
    def __init__(self, host: str, username: str, password: str, port: int = 443, timeout: int = 30):
        """
        初始化Redfish客户端
        
        Args:
            host: BMC IP地址
            username: 用户名
            password: 密码
            port: 端口号，默认443
            timeout: 超时时间，默认30秒
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self.client = None
        self.session_active = False
        
    async def connect(self) -> bool:
        """
        连接到Redfish服务
        
        Returns:
            bool: 连接是否成功
        """
        try:
            # 构建连接URL
            base_url = f"https://{self.host}:{self.port}"
            
            # 创建redfish客户端
            self.client = redfish.redfish_client(
                base_url=base_url,
                username=self.username,
                password=self.password,
                timeout=self.timeout,
                max_retry=3
            )
            
            # 登录
            self.client.login(auth="session")
            self.session_active = True
            
            logger.info(f"Successfully connected to Redfish service at {self.host}")
            return True
            
        except ServerDownOrUnreachableError:
            logger.error(f"Server {self.host} is down or unreachable")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to {self.host}: {str(e)}")
            return False
    
    async def disconnect(self):
        """断开连接"""
        try:
            if self.client and self.session_active:
                self.client.logout()
                self.session_active = False
                logger.info(f"Disconnected from {self.host}")
        except Exception as e:
            logger.error(f"Error disconnecting from {self.host}: {str(e)}")
    
    async def get_system_info(self) -> Optional[Dict[str, Any]]:
        """
        获取系统基本信息
        
        Returns:
            Dict: 系统信息字典
        """
        try:
            if not self.session_active:
                await self.connect()
            
            # 获取系统信息
            systems_uri = "/redfish/v1/Systems"
            response = self.client.get(systems_uri)
            
            if response.status != 200:
                logger.error(f"Failed to get systems info from {self.host}: {response.status}")
                return None
            
            systems_data = response.dict
            if not systems_data.get("Members"):
                return None
            
            # 获取第一个系统的详细信息
            system_uri = systems_data["Members"][0]["@odata.id"]
            system_response = self.client.get(system_uri)
            
            if system_response.status != 200:
                return None
            
            system_data = system_response.dict
            
            return {
                "manufacturer": system_data.get("Manufacturer", ""),
                "model": system_data.get("Model", ""),
                "serial_number": system_data.get("SerialNumber", ""),
                "hostname": system_data.get("HostName", ""),
                "power_state": system_data.get("PowerState", ""),
                "health_status": system_data.get("Status", {}).get("Health", "Unknown"),
                "state": system_data.get("Status", {}).get("State", "Unknown"),
                "bios_version": system_data.get("BiosVersion", ""),
                "processor_summary": system_data.get("ProcessorSummary", {}),
                "memory_summary": system_data.get("MemorySummary", {}),
                "raw_data": system_data
            }
            
        except Exception as e:
            logger.error(f"Error getting system info from {self.host}: {str(e)}")
            return None
    
    async def get_processor_status(self) -> List[Dict[str, Any]]:
        """
        获取处理器状态
        
        Returns:
            List[Dict]: 处理器状态列表
        """
        try:
            if not self.session_active:
                await self.connect()
            
            processors = []
            
            # 获取系统URI
            systems_response = self.client.get("/redfish/v1/Systems")
            if systems_response.status != 200:
                return processors
            
            system_uri = systems_response.dict["Members"][0]["@odata.id"]
            
            # 获取处理器集合
            processors_uri = f"{system_uri}/Processors"
            processors_response = self.client.get(processors_uri)
            
            if processors_response.status != 200:
                return processors
            
            # 遍历每个处理器
            for member in processors_response.dict.get("Members", []):
                processor_uri = member["@odata.id"]
                processor_response = self.client.get(processor_uri)
                
                if processor_response.status == 200:
                    processor_data = processor_response.dict
                    processors.append({
                        "id": processor_data.get("Id", ""),
                        "name": processor_data.get("Name", ""),
                        "model": processor_data.get("Model", ""),
                        "manufacturer": processor_data.get("Manufacturer", ""),
                        "socket": processor_data.get("Socket", ""),
                        "cores": processor_data.get("TotalCores", 0),
                        "threads": processor_data.get("TotalThreads", 0),
                        "health_status": processor_data.get("Status", {}).get("Health", "Unknown"),
                        "state": processor_data.get("Status", {}).get("State", "Unknown"),
                        "temperature": processor_data.get("Temperature", {}),
                        "raw_data": processor_data
                    })
            
            return processors
            
        except Exception as e:
            logger.error(f"Error getting processor status from {self.host}: {str(e)}")
            return []
    
    async def get_memory_status(self) -> List[Dict[str, Any]]:
        """
        获取内存状态
        
        Returns:
            List[Dict]: 内存状态列表
        """
        try:
            if not self.session_active:
                await self.connect()
            
            memory_modules = []
            
            # 获取系统URI
            systems_response = self.client.get("/redfish/v1/Systems")
            if systems_response.status != 200:
                return memory_modules
            
            system_uri = systems_response.dict["Members"][0]["@odata.id"]
            
            # 获取内存集合
            memory_uri = f"{system_uri}/Memory"
            memory_response = self.client.get(memory_uri)
            
            if memory_response.status != 200:
                return memory_modules
            
            # 遍历每个内存模块
            for member in memory_response.dict.get("Members", []):
                memory_module_uri = member["@odata.id"]
                module_response = self.client.get(memory_module_uri)
                
                if module_response.status == 200:
                    module_data = module_response.dict
                    memory_modules.append({
                        "id": module_data.get("Id", ""),
                        "name": module_data.get("Name", ""),
                        "manufacturer": module_data.get("Manufacturer", ""),
                        "part_number": module_data.get("PartNumber", ""),
                        "serial_number": module_data.get("SerialNumber", ""),
                        "capacity_mb": module_data.get("CapacityMiB", 0),
                        "speed_mhz": module_data.get("OperatingSpeedMhz", 0),
                        "memory_type": module_data.get("MemoryType", ""),
                        "device_locator": module_data.get("DeviceLocator", ""),
                        "health_status": module_data.get("Status", {}).get("Health", "Unknown"),
                        "state": module_data.get("Status", {}).get("State", "Unknown"),
                        "raw_data": module_data
                    })
            
            return memory_modules
            
        except Exception as e:
            logger.error(f"Error getting memory status from {self.host}: {str(e)}")
            return []
    
    async def get_storage_status(self) -> List[Dict[str, Any]]:
        """
        获取存储状态
        
        Returns:
            List[Dict]: 存储状态列表
        """
        try:
            if not self.session_active:
                await self.connect()
            
            storage_devices = []
            
            # 获取系统URI
            systems_response = self.client.get("/redfish/v1/Systems")
            if systems_response.status != 200:
                return storage_devices
            
            system_uri = systems_response.dict["Members"][0]["@odata.id"]
            
            # 获取存储集合
            storage_uri = f"{system_uri}/Storage"
            storage_response = self.client.get(storage_uri)
            
            if storage_response.status != 200:
                return storage_devices
            
            # 遍历每个存储控制器
            for member in storage_response.dict.get("Members", []):
                storage_controller_uri = member["@odata.id"]
                controller_response = self.client.get(storage_controller_uri)
                
                if controller_response.status == 200:
                    controller_data = controller_response.dict
                    
                    # 获取驱动器信息
                    for drive_ref in controller_data.get("Drives", []):
                        drive_uri = drive_ref["@odata.id"]
                        drive_response = self.client.get(drive_uri)
                        
                        if drive_response.status == 200:
                            drive_data = drive_response.dict
                            storage_devices.append({
                                "id": drive_data.get("Id", ""),
                                "name": drive_data.get("Name", ""),
                                "manufacturer": drive_data.get("Manufacturer", ""),
                                "model": drive_data.get("Model", ""),
                                "serial_number": drive_data.get("SerialNumber", ""),
                                "capacity_gb": drive_data.get("CapacityBytes", 0) // (1024**3),
                                "media_type": drive_data.get("MediaType", ""),
                                "protocol": drive_data.get("Protocol", ""),
                                "health_status": drive_data.get("Status", {}).get("Health", "Unknown"),
                                "state": drive_data.get("Status", {}).get("State", "Unknown"),
                                "predicted_media_life_left": drive_data.get("PredictedMediaLifeLeftPercent", None),
                                "raw_data": drive_data
                            })
            
            return storage_devices
            
        except Exception as e:
            logger.error(f"Error getting storage status from {self.host}: {str(e)}")
            return []
    
    async def get_power_status(self) -> List[Dict[str, Any]]:
        """
        获取电源状态
        
        Returns:
            List[Dict]: 电源状态列表
        """
        try:
            if not self.session_active:
                await self.connect()
            
            power_supplies = []
            
            # 获取机箱信息
            chassis_response = self.client.get("/redfish/v1/Chassis")
            if chassis_response.status != 200:
                return power_supplies
            
            # 遍历每个机箱
            for chassis_member in chassis_response.dict.get("Members", []):
                chassis_uri = chassis_member["@odata.id"]
                
                # 获取电源信息
                power_uri = f"{chassis_uri}/Power"
                power_response = self.client.get(power_uri)
                
                if power_response.status == 200:
                    power_data = power_response.dict
                    
                    # 获取电源供应器信息
                    for ps in power_data.get("PowerSupplies", []):
                        power_supplies.append({
                            "id": ps.get("MemberId", ""),
                            "name": ps.get("Name", ""),
                            "manufacturer": ps.get("Manufacturer", ""),
                            "model": ps.get("Model", ""),
                            "serial_number": ps.get("SerialNumber", ""),
                            "part_number": ps.get("PartNumber", ""),
                            "power_capacity_watts": ps.get("PowerCapacityWatts", 0),
                            "power_input_watts": ps.get("PowerInputWatts", 0),
                            "power_output_watts": ps.get("PowerOutputWatts", 0),
                            "efficiency_percent": ps.get("EfficiencyPercent", 0),
                            "health_status": ps.get("Status", {}).get("Health", "Unknown"),
                            "state": ps.get("Status", {}).get("State", "Unknown"),
                            "raw_data": ps
                        })
            
            return power_supplies
            
        except Exception as e:
            logger.error(f"Error getting power status from {self.host}: {str(e)}")
            return []
    
    async def get_thermal_status(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取温度和风扇状态
        
        Returns:
            Dict: 包含温度和风扇状态的字典
        """
        try:
            if not self.session_active:
                await self.connect()
            
            temperatures = []
            fans = []
            
            # 获取机箱信息
            chassis_response = self.client.get("/redfish/v1/Chassis")
            if chassis_response.status != 200:
                return {"temperatures": temperatures, "fans": fans}
            
            # 遍历每个机箱
            for chassis_member in chassis_response.dict.get("Members", []):
                chassis_uri = chassis_member["@odata.id"]
                
                # 获取热管理信息
                thermal_uri = f"{chassis_uri}/Thermal"
                thermal_response = self.client.get(thermal_uri)
                
                if thermal_response.status == 200:
                    thermal_data = thermal_response.dict
                    
                    # 获取温度传感器信息
                    for temp in thermal_data.get("Temperatures", []):
                        temperatures.append({
                            "id": temp.get("MemberId", ""),
                            "name": temp.get("Name", ""),
                            "sensor_number": temp.get("SensorNumber", 0),
                            "reading_celsius": temp.get("ReadingCelsius", 0),
                            "upper_threshold_critical": temp.get("UpperThresholdCritical", None),
                            "upper_threshold_fatal": temp.get("UpperThresholdFatal", None),
                            "lower_threshold_critical": temp.get("LowerThresholdCritical", None),
                            "health_status": temp.get("Status", {}).get("Health", "Unknown"),
                            "state": temp.get("Status", {}).get("State", "Unknown"),
                            "raw_data": temp
                        })
                    
                    # 获取风扇信息
                    for fan in thermal_data.get("Fans", []):
                        fans.append({
                            "id": fan.get("MemberId", ""),
                            "name": fan.get("Name", ""),
                            "reading_rpm": fan.get("Reading", 0),
                            "reading_units": fan.get("ReadingUnits", ""),
                            "lower_threshold_critical": fan.get("LowerThresholdCritical", None),
                            "lower_threshold_fatal": fan.get("LowerThresholdFatal", None),
                            "health_status": fan.get("Status", {}).get("Health", "Unknown"),
                            "state": fan.get("Status", {}).get("State", "Unknown"),
                            "raw_data": fan
                        })
            
            return {"temperatures": temperatures, "fans": fans}
            
        except Exception as e:
            logger.error(f"Error getting thermal status from {self.host}: {str(e)}")
            return {"temperatures": [], "fans": []}
    
    async def get_all_status(self) -> Dict[str, Any]:
        """
        获取所有组件状态
        
        Returns:
            Dict: 包含所有组件状态的字典
        """
        try:
            if not await self.connect():
                return {}
            
            # 并发获取所有状态信息
            system_info_task = self.get_system_info()
            processor_task = self.get_processor_status()
            memory_task = self.get_memory_status()
            storage_task = self.get_storage_status()
            power_task = self.get_power_status()
            thermal_task = self.get_thermal_status()
            
            # 等待所有任务完成
            system_info, processors, memory, storage, power, thermal = await asyncio.gather(
                system_info_task,
                processor_task,
                memory_task,
                storage_task,
                power_task,
                thermal_task,
                return_exceptions=True
            )
            
            # 处理异常结果
            if isinstance(system_info, Exception):
                system_info = {}
            if isinstance(processors, Exception):
                processors = []
            if isinstance(memory, Exception):
                memory = []
            if isinstance(storage, Exception):
                storage = []
            if isinstance(power, Exception):
                power = []
            if isinstance(thermal, Exception):
                thermal = {"temperatures": [], "fans": []}
            
            return {
                "timestamp": datetime.now().isoformat(),
                "host": self.host,
                "system_info": system_info,
                "processors": processors,
                "memory": memory,
                "storage": storage,
                "power": power,
                "temperatures": thermal.get("temperatures", []),
                "fans": thermal.get("fans", [])
            }
            
        except Exception as e:
            logger.error(f"Error getting all status from {self.host}: {str(e)}")
            return {}
        finally:
            await self.disconnect()
    
    async def discover_log_services(self) -> Dict[str, List[str]]:
        """
        发现可用的日志服务（参考check_redfish的自动发现机制）
        
        Returns:
            Dict: 发现的日志服务 {"managers": [...], "systems": [...]}
        """
        try:
            if not self.session_active:
                await self.connect()
            
            discovered_services = {"managers": [], "systems": []}
            
            # 1. 发现Manager LogServices
            managers_response = self.client.get("/redfish/v1/Managers")
            if managers_response.status == 200:
                managers_data = managers_response.dict
                for manager_member in managers_data.get("Members", []):
                    manager_uri = manager_member["@odata.id"]
                    log_services_uri = f"{manager_uri}/LogServices"
                    
                    log_services_response = self.client.get(log_services_uri)
                    if log_services_response.status == 200:
                        log_services_data = log_services_response.dict
                        for service_member in log_services_data.get("Members", []):
                            service_uri = service_member["@odata.id"]
                            discovered_services["managers"].append(service_uri)
            
            # 2. 发现System LogServices
            systems_response = self.client.get("/redfish/v1/Systems")
            if systems_response.status == 200:
                systems_data = systems_response.dict
                for system_member in systems_data.get("Members", []):
                    system_uri = system_member["@odata.id"]
                    log_services_uri = f"{system_uri}/LogServices"
                    
                    log_services_response = self.client.get(log_services_uri)
                    if log_services_response.status == 200:
                        log_services_data = log_services_response.dict
                        for service_member in log_services_data.get("Members", []):
                            service_uri = service_member["@odata.id"]
                            discovered_services["systems"].append(service_uri)
            
            return discovered_services
            
        except Exception as e:
            logger.error(f"Error discovering log services from {self.host}: {str(e)}")
            return {"managers": [], "systems": []}
    
    async def get_log_service_entries(self, service_uri: str, max_entries: int = 50,
                                     since_entry_id: Optional[str] = None,
                                     since_timestamp: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        获取指定日志服务的条目（支持增量获取，优化大量获取）
        
        Args:
            service_uri: 日志服务URI
            max_entries: 最大返回条目数
            since_entry_id: 起始条目ID（用于增量获取）
            since_timestamp: 起始时间戳（用于增量获取）
            
        Returns:
            List[Dict]: 日志条目列表
        """
        try:
            if not self.session_active:
                await self.connect()
            
            logs = []
            
            # 获取日志服务详情
            service_response = self.client.get(service_uri)
            if service_response.status != 200:
                return logs
            
            service_data = service_response.dict
            service_id = service_data.get("Id", "").upper()
            service_name = service_data.get("Name", "")
            
            # 获取日志条目
            entries_uri = f"{service_uri}/Entries"
            entries_response = self.client.get(entries_uri)
            
            if entries_response.status != 200:
                logger.warning(f"Cannot access entries for {service_uri}: {entries_response.status}")
                return logs
            
            entries_data = entries_response.dict
            members = entries_data.get("Members", [])
            total_entries = len(members)
            
            if total_entries == 0:
                logger.info(f"No entries found for {service_uri}")
                return logs
            
            logger.info(f"开始处理 {service_uri}，总条目数: {total_entries}，预期获取: {min(max_entries, total_entries)}")
            
            # 处理日志条目（优化大量获取）
            found_start_point = since_entry_id is None  # 如果没有指定起始ID，则从头开始
            processed_count = 0
            failed_count = 0
            last_progress_log = 0
            
            for i, entry_member in enumerate(members):
                # 检查是否达到最大条目数
                if len(logs) >= max_entries:
                    logger.info(f"达到最大条目数限制: {max_entries}")
                    break
                
                # 进度显示（每处理50条或到达10%进度时显示一次）
                progress_percentage = (i + 1) / total_entries * 100
                if (processed_count > 0 and processed_count % 50 == 0) or \
                   (progress_percentage >= last_progress_log + 10):
                    logger.info(f"处理进度: {i+1}/{total_entries} ({progress_percentage:.1f}%), "
                               f"成功: {len(logs)}, 失败: {failed_count}")
                    last_progress_log = int(progress_percentage / 10) * 10
                
                entry_uri = entry_member["@odata.id"]
                
                # 获取条目详情（增加重试机制）
                entry_data = None
                retry_count = 0
                max_retries = 3
                
                while retry_count < max_retries and entry_data is None:
                    try:
                        entry_response = self.client.get(entry_uri)
                        
                        if entry_response.status == 200:
                            entry_data = entry_response.dict
                        else:
                            logger.warning(f"获取条目失败 {entry_uri}: HTTP {entry_response.status}")
                            if retry_count < max_retries - 1:
                                await asyncio.sleep(0.5)  # 重试前等待
                    
                    except Exception as e:
                        logger.warning(f"获取条目异常 {entry_uri}: {str(e)}")
                        if retry_count < max_retries - 1:
                            await asyncio.sleep(0.5)  # 重试前等待
                    
                    retry_count += 1
                
                processed_count += 1
                
                # 如果重试后仍然失败，记录并继续处理下一个
                if entry_data is None:
                    failed_count += 1
                    logger.warning(f"跳过无法获取的条目: {entry_uri}")
                    continue
                
                entry_id = entry_data.get("Id", "")
                entry_created = entry_data.get("Created", "")
                
                # 增量获取逻辑：跳过已处理的条目
                if not found_start_point and since_entry_id:
                    if entry_id == since_entry_id:
                        found_start_point = True
                        logger.info(f"找到起始点: {since_entry_id}")
                    continue
                
                # 时间戳过滤
                if since_timestamp and entry_created:
                    try:
                        from dateutil.parser import parse
                        entry_time = parse(entry_created)
                        if entry_time <= since_timestamp:
                            continue
                    except Exception:
                        pass  # 如果时间解析失败，则保留该条目
                
                # 修复UnboundLocalError：必须先定义repaired
                repaired = self._get_property(entry_data, 'Repaired')
                if repaired is None:
                    repaired = False

                severity_str = self._get_property(entry_data, 'Severity')
                severity = severity_str.upper() if isinstance(severity_str, str) else ""

                # 最终版逻辑：只过滤，不转换业务级别
                if repaired is True or severity == "OK":
                    logger.debug(f"跳过日志: ID {entry_data.get('Id', '')}, Repaired: {repaired}, Severity: {severity}")
                else:
                    # 对于所有未修复且非OK的日志，进行记录
                    # 回归纯粹：只提供原始数据，键名也使用原始的，让下游服务去处理
                    log_entry = {
                        "Id": entry_data.get("Id", ""),
                        "Message": self._get_property(entry_data, 'Message'),
                        "Severity": severity,
                        "Created": entry_data.get("Created"),
                        "Repaired": repaired,
                        "SensorType": self._get_property(entry_data, 'SensorType'),
                        "RawData": entry_data, # 保留最原始的数据
                    }
                    
                    logger.debug(f"记录日志: ID {log_entry['Id']}, "
                               f"Severity: {log_entry['Severity']}, "
                               f"Message: {log_entry['Message']}")
                    
                    logs.append(log_entry)

            # 最终日志记录
            logger.info(f"完成处理 {service_uri}: 总条目{total_entries}, "
                       f"处理{processed_count}, 成功{len(logs)}, 失败{failed_count}")
            
            if failed_count > 0:
                logger.warning(f"获取过程中有 {failed_count} 个条目失败，这可能是网络问题或设备限制导致的")
            
            return logs
            
        except Exception as e:
            logger.error(f"Error getting log entries from {service_uri}: {str(e)}")
            return []
    
    async def get_event_logs(self, log_type: str = "all", max_entries: int = 100,
                           since_entry_id: Optional[str] = None,
                           since_timestamp: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        获取Redfish事件日志（增强版，支持多厂商和自动发现，支持增量获取）
        
        Args:
            log_type: 日志类型 ("sel", "mel", "all")
            max_entries: 最大返回条目数
            since_entry_id: 起始条目ID（用于增量获取）
            since_timestamp: 起始时间戳（用于增量获取）
            
        Returns:
            List[Dict]: 事件日志列表
        """
        try:
            if not self.session_active:
                await self.connect()
            
            all_logs = []
            
            # 自动发现日志服务
            discovered_services = await self.discover_log_services()
            
            # 定义服务ID映射（支持多厂商）
            sel_service_ids = ["sel", "systemlog", "systemlogservice", "iml"]  # 系统日志
            mel_service_ids = ["mel", "managementlog", "iel", "managereventlog"]  # 管理日志
            
            # 处理所有发现的服务
            all_service_uris = discovered_services["managers"] + discovered_services["systems"]
            
            for service_uri in all_service_uris:
                if len(all_logs) >= max_entries:
                    break
                
                # 获取服务详情以确定类型
                service_response = self.client.get(service_uri)
                if service_response.status != 200:
                    continue
                
                service_data = service_response.dict
                service_id = service_data.get("Id", "").lower()
                service_name = service_data.get("Name", "").lower()
                
                # 根据log_type过滤服务
                is_sel_service = any(id_pattern in service_id for id_pattern in sel_service_ids) or \
                                any(id_pattern in service_name for id_pattern in sel_service_ids)
                is_mel_service = any(id_pattern in service_id for id_pattern in mel_service_ids) or \
                                any(id_pattern in service_name for id_pattern in mel_service_ids)
                
                # 应用过滤器
                if log_type == "sel" and not is_sel_service:
                    continue
                elif log_type == "mel" and not is_mel_service:
                    continue
                
                # 获取该服务的日志条目（支持增量获取）
                remaining_entries = max_entries - len(all_logs)
                service_logs = await self.get_log_service_entries(
                    service_uri, remaining_entries, since_entry_id, since_timestamp
                )
                all_logs.extend(service_logs)
            
            # 按创建时间排序（最新的在前）
            all_logs.sort(key=lambda x: x.get("created", ""), reverse=True)
            
            return all_logs[:max_entries]
            
        except Exception as e:
            logger.error(f"Error getting event logs from {self.host}: {str(e)}")
            return []
    
    async def get_system_event_logs(self, max_entries: int = 50,
                                   since_entry_id: Optional[str] = None,
                                   since_timestamp: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        获取系统事件日志(SEL)（支持增量获取）
        
        Args:
            max_entries: 最大返回条目数
            since_entry_id: 起始条目ID（用于增量获取）
            since_timestamp: 起始时间戳（用于增量获取）
            
        Returns:
            List[Dict]: SEL日志列表
        """
        return await self.get_event_logs("sel", max_entries, since_entry_id, since_timestamp)
    
    async def get_management_event_logs(self, max_entries: int = 50,
                                       since_entry_id: Optional[str] = None,
                                       since_timestamp: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        获取管理事件日志(MEL/IML)（支持增量获取）
        
        Args:
            max_entries: 最大返回条目数
            since_entry_id: 起始条目ID（用于增量获取）
            since_timestamp: 起始时间戳（用于增量获取）
            
        Returns:
            List[Dict]: MEL日志列表
        """
        return await self.get_event_logs("mel", max_entries, since_entry_id, since_timestamp)

    def _get_property(self, entry_data: Dict[str, Any], property_name: str) -> Any:
        """
        健壮地获取属性，兼容顶层和常见的OEM（如HPE）嵌套结构。
        未来可在此处扩展对其他厂商的支持。
        """
        # 1. 尝试从顶层获取
        value = entry_data.get(property_name)
        if value is not None:
            return value

        # 2. 尝试从HPE OEM结构中获取
        if 'Oem' in entry_data and 'Hpe' in entry_data['Oem']:
            try:
                hpe_oem_data = entry_data.get('Oem', {}).get('Hpe', {})
                value = hpe_oem_data.get(property_name)
                if value is not None:
                    return value
            except AttributeError:
                # 如果Oem或Hpe不是字典，则忽略
                pass
        
        # TODO: 在此处扩展对其他厂商（如Dell）的支持
        # elif 'Oem' in entry_data and 'Dell' in entry_data['Oem']:
        #     ...

        return None

    def _apply_incremental_filter(self, entries: List[Dict], since_entry_id: Optional[str] = None, 
                                 since_timestamp: Optional[datetime] = None) -> List[Dict]:
        """
        应用增量过滤逻辑
        
        策略：
        1. 无过滤条件：返回按时间戳排序的所有条目
        2. Entry ID过滤：SEL使用"不等于"，MEL使用"大于"
        3. 时间戳过滤：只保留时间戳晚于指定时间的条目
        
        Args:
            entries: 日志条目列表
            since_entry_id: 上次获取的Entry ID
            since_timestamp: 上次获取的时间戳
        
        Returns:
            List[Dict]: 过滤后的条目列表
        """
        if not entries:
            return []
        
        # 无过滤条件，返回按时间戳排序的所有条目
        if since_entry_id is None and since_timestamp is None:
            return sorted(entries, key=lambda x: x.get('entry_timestamp', datetime.min), reverse=True)
        
        filtered_entries = []
        
        # 检测日志类型（通过service_uri判断是否为MEL）
        is_mel_service = False
        if entries:
            service_uri = entries[0].get('service_uri', '').lower()
            service_name = entries[0].get('log_service_name', '').lower()
            service_id = entries[0].get('log_service_id', '').lower()
            
            mel_indicators = ['mel', 'management', 'iel', 'managereventlog', 'managementlog']
            is_mel_service = any(indicator in service_uri or indicator in service_name or indicator in service_id 
                               for indicator in mel_indicators)
        
        for entry in entries:
            include_entry = True
            
            # Entry ID过滤（根据日志类型使用不同策略）
            if since_entry_id is not None:
                entry_id = entry.get('redfish_log_id')
                
                if is_mel_service:
                    # MEL使用"大于"过滤，避免边界重叠
                    try:
                        entry_id_num = int(entry_id)
                        since_id_num = int(since_entry_id)
                        if entry_id_num <= since_id_num:
                            include_entry = False
                    except (ValueError, TypeError):
                        # 非数字ID，使用字符串相等比较
                        if entry_id == since_entry_id:
                            include_entry = False
                else:
                    # SEL和其他日志使用"不等于"过滤
                    if entry_id == since_entry_id:
                        include_entry = False
            
            # 时间戳过滤
            if since_timestamp is not None and include_entry:
                try:
                    entry_timestamp = entry.get('entry_timestamp')
                    if entry_timestamp is not None:
                        # 确保时间戳比较时的时区兼容性
                        if entry_timestamp.tzinfo is None and since_timestamp.tzinfo is not None:
                            # entry_timestamp是naive，since_timestamp是aware
                            entry_timestamp = entry_timestamp.replace(tzinfo=since_timestamp.tzinfo)
                        elif entry_timestamp.tzinfo is not None and since_timestamp.tzinfo is None:
                            # entry_timestamp是aware，since_timestamp是naive
                            since_timestamp = since_timestamp.replace(tzinfo=entry_timestamp.tzinfo)
                        
                        if entry_timestamp <= since_timestamp:
                            include_entry = False
                except Exception as e:
                    logger.warning(f"时间戳比较失败，保守包含条目: {e}")
                    # 比较失败时保守地包含条目
            
            if include_entry:
                filtered_entries.append(entry)
        
        # 按时间戳排序，最新的在前
        try:
            return sorted(filtered_entries, key=lambda x: x.get('entry_timestamp', datetime.min), reverse=True)
        except Exception:
            # 排序失败，按Entry ID排序
            return sorted(filtered_entries, key=lambda x: x.get('redfish_log_id', ''), reverse=True)


def encrypt_password(password: str) -> str:
    """
    加密密码
    
    Args:
        password: 明文密码
        
    Returns:
        str: 加密后的密码
    """
    # 获取或生成加密密钥
    key = RedfishConfig.redfish_encrypt_key
    if not key:
        key = Fernet.generate_key()
        logger.warning("No encryption key found, generated new key. Please set REDFISH_ENCRYPT_KEY environment variable.")
    
    if isinstance(key, str):
        key = key.encode()
    
    fernet = Fernet(key)
    encrypted_password = fernet.encrypt(password.encode())
    return encrypted_password.decode()


def decrypt_password(encrypted_password: str) -> str:
    """
    解密密码
    
    Args:
        encrypted_password: 加密的密码
        
    Returns:
        str: 明文密码
    """
    try:
        key = RedfishConfig.redfish_encrypt_key
        if not key:
            logger.error("No encryption key found. Please set REDFISH_ENCRYPT_KEY environment variable.")
            return encrypted_password
        
        if isinstance(key, str):
            key = key.encode()
        
        fernet = Fernet(key)
        decrypted_password = fernet.decrypt(encrypted_password.encode())
        return decrypted_password.decode()
    except Exception as e:
        logger.error(f"Failed to decrypt password: {str(e)}")
        return encrypted_password 