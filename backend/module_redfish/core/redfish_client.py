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
    
    async def get_event_logs(self, log_type: str = "all", max_entries: int = 100,
                           since_entry_id: Optional[str] = None,
                           since_timestamp: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        获取事件日志
        
        Args:
            log_type: 日志类型 ("sel", "mel", "all")
            max_entries: 每个日志服务的最大条目数
            since_entry_id: 从此条目ID后获取日志
            since_timestamp: 从此时间戳后获取日志
            
        Returns:
            List[Dict]: 事件日志列表
        """
        return []


def encrypt_password(password: str) -> str:
    """加密密码"""
    if not RedfishConfig.redfish_encrypt_key:
        raise ValueError("redfish_encrypt_key is not set in the environment variables.")
    key = RedfishConfig.redfish_encrypt_key.encode()
    f = Fernet(key)
    encrypted_password = f.encrypt(password.encode())
    return encrypted_password.decode()

def decrypt_password(encrypted_password: str) -> str:
    """解密密码"""
    if not RedfishConfig.redfish_encrypt_key:
        raise ValueError("redfish_encrypt_key is not set in the environment variables.")
    key = RedfishConfig.redfish_encrypt_key.encode()
    f = Fernet(key)
    decrypted_password = f.decrypt(encrypted_password.encode())
    return decrypted_password.decode()