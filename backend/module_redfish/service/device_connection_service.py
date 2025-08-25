"""
设备连接测试Service层
"""
import asyncio
import subprocess
import socket
import platform
from datetime import datetime
from typing import Dict, List, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from module_redfish.dao.device_dao import DeviceDao
from module_redfish.entity.do.device_do import DeviceInfoDO
from module_redfish.entity.vo.device_vo import DeviceConnectionResult
from module_redfish.core.redfish_client import RedfishClient, decrypt_password
from utils.log_util import logger


class DeviceConnectionService:
    """设备连接测试服务"""
    
    @classmethod
    async def test_device_connection_by_id_services(
        cls, 
        db: AsyncSession,
        device_id: int
    ) -> DeviceConnectionResult:
        """
        通过设备ID测试设备连接
        
        Args:
            db: 数据库会话
            device_id: 设备ID
            
        Returns:
            DeviceConnectionResult: 连接测试结果
        """
        try:
            # 从数据库获取设备信息
            device = await DeviceDao.get_device_by_id(db, device_id)
            if not device:
                return DeviceConnectionResult(
                    success=False,
                    message="设备不存在",
                    system_info=None
                )
            
            # 解密密码
            try:
                decrypted_password = decrypt_password(device.redfish_password)
            except ValueError as e:
                logger.error(f"设备 {device.hostname} 密码解密失败: {str(e)}")
                return DeviceConnectionResult(
                    success=False,
                    message="设备密码解密失败，请重新设置密码",
                    system_info=None
                )
            
            # 创建Redfish客户端
            client = RedfishClient(
                host=device.oob_ip,
                username=device.redfish_username,
                password=decrypted_password,
                port=device.oob_port,
                timeout=6
            )
            
            # 尝试连接
            try:
                success = await asyncio.wait_for(client.connect(), timeout=6)
            except asyncio.TimeoutError:
                logger.warning("Redfish连接超时 (6s)")
                return DeviceConnectionResult(
                    success=False,
                    message="连接测试失败",
                    system_info=None
                )
            
            if success:
                # 获取系统信息
                try:
                    system_info = await asyncio.wait_for(client.get_system_info(), timeout=6)
                except asyncio.TimeoutError:
                    logger.warning("获取系统信息超时 (6s)")
                    await client.disconnect()
                    return DeviceConnectionResult(
                        success=False,
                        message="连接测试失败",
                        system_info=None
                    )
                await client.disconnect()
                
                return DeviceConnectionResult(
                    success=True,
                    message="连接成功",
                    system_info=system_info
                )
            else:
                return DeviceConnectionResult(
                    success=False,
                    message="连接测试失败",
                    system_info=None
                )
        except Exception as e:
            logger.error(f"测试设备连接失败 (设备ID: {device_id}): {str(e)}")
            return DeviceConnectionResult(
                success=False,
                message="连接测试失败",
                system_info=None
            )
    
    @classmethod
    async def check_business_ip_connectivity_services(
        cls,
        db: AsyncSession,
        device_id: int = None,
        business_ip: str = None
    ) -> Dict[str, Any]:
        """
        检测设备业务IP连通性
        
        Args:
            db: 数据库会话
            device_id: 设备ID（二选一）
            business_ip: 业务IP（二选一）
            
        Returns:
            Dict[str, Any]: 连通性检测结果
        """
        if device_id:
            device = await DeviceDao.get_device_by_id(db, device_id)
            if not device:
                return {"online": False, "error": "设备不存在", "check_time": datetime.now().isoformat()}
            target_ip = device.business_ip
            hostname = device.hostname
        elif business_ip:
            target_ip = business_ip
            hostname = business_ip
        else:
            return {"online": False, "error": "必须提供device_id或business_ip", "check_time": datetime.now().isoformat()}
        
        if not target_ip:
            return {"online": False, "error": "设备业务IP为空", "check_time": datetime.now().isoformat()}
        
        # 并发执行多种检测方法
        ping_task = asyncio.create_task(cls._ping_check(target_ip))
        ssh_task = asyncio.create_task(cls._tcp_port_check(target_ip, 22, timeout=2))
        http_task = asyncio.create_task(cls._tcp_port_check(target_ip, 80, timeout=2))
        https_task = asyncio.create_task(cls._tcp_port_check(target_ip, 443, timeout=2))
        
        # 等待所有检测完成
        ping_result, ssh_result, http_result, https_result = await asyncio.gather(
            ping_task, ssh_task, http_task, https_task, return_exceptions=True
        )
        
        # 处理异常结果
        def safe_result(result, method):
            if isinstance(result, Exception):
                return {"success": False, "method": method, "error": str(result)}
            return result
        
        ping_result = safe_result(ping_result, "ping")
        ssh_result = safe_result(ssh_result, "tcp_port_22")
        http_result = safe_result(http_result, "tcp_port_80") 
        https_result = safe_result(https_result, "tcp_port_443")
        
        # 综合判断：ping通或任一端口可达即认为在线
        online = (ping_result.get("success", False) or 
                 ssh_result.get("success", False) or 
                 http_result.get("success", False) or 
                 https_result.get("success", False))
        
        return {
            "online": online,
            "hostname": hostname,
            "business_ip": target_ip,
            "ping": ping_result,
            "ssh_port": ssh_result,
            "http_port": http_result,
            "https_port": https_result,
            "check_time": datetime.now().isoformat()
        }
    
    @classmethod
    async def batch_check_business_connectivity_services(
        cls,
        db: AsyncSession,
        device_ids: List[int] = None,
        max_concurrent: int = 20
    ) -> Dict[str, Any]:
        """
        批量检测设备业务IP连通性
        
        Args:
            db: 数据库会话
            device_ids: 设备ID列表，为空则检测所有设备
            max_concurrent: 最大并发数
            
        Returns:
            Dict[str, Any]: 批量检测结果
        """
        if device_ids:
            devices_query = select(DeviceInfoDO).where(DeviceInfoDO.device_id.in_(device_ids))
        else:
            devices_query = select(DeviceInfoDO).where(DeviceInfoDO.business_ip.isnot(None))
        
        result = await db.execute(devices_query)
        devices = result.scalars().all()
        
        if not devices:
            return {
                "total_devices": 0,
                "online_devices": 0,
                "offline_devices": 0,
                "check_time": datetime.now().isoformat(),
                "details": []
            }
        
        # 使用信号量限制并发数
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def check_single_device(device):
            async with semaphore:
                connectivity = await cls.check_business_ip_connectivity_services(
                    db, device_id=device.device_id
                )
                return {
                    "device_id": device.device_id,
                    "hostname": device.hostname,
                    "business_ip": device.business_ip,
                    "online": connectivity["online"],
                    "details": connectivity
                }
        
        # 并发执行所有检测
        logger.info(f"开始批量检测 {len(devices)} 台设备的业务IP连通性")
        
        tasks = [check_single_device(device) for device in devices]
        results = await asyncio.gather(*tasks)
        
        # 统计结果
        online_count = sum(1 for result in results if result["online"])
        offline_count = len(results) - online_count
        
        logger.info(f"批量连通性检测完成: {online_count} 在线, {offline_count} 离线")
        
        return {
            "total_devices": len(devices),
            "online_devices": online_count,
            "offline_devices": offline_count,
            "check_time": datetime.now().isoformat(),
            "details": results
        }
    
    @classmethod
    async def _ping_check(cls, ip: str, timeout: int = 3, count: int = 1) -> Dict[str, Any]:
        """跨平台Ping检测"""
        try:
            # 根据操作系统选择ping命令参数
            system = platform.system().lower()
            if system == 'windows':
                cmd = ['ping', '-n', str(count), '-w', str(timeout * 1000), ip]
            else:  # Linux/macOS
                cmd = ['ping', '-c', str(count), '-W', str(timeout), ip]
            
            # 执行ping命令
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            success = result.returncode == 0
            output = stdout.decode() if stdout else stderr.decode()
            
            return {
                "success": success,
                "method": "ping",
                "response_time": cls._extract_ping_time(output) if success else None,
                "output": output if not success else None,
                "error": None if success else f"Ping failed (code: {result.returncode})"
            }
        except Exception as e:
            return {
                "success": False,
                "method": "ping",
                "response_time": None,
                "error": str(e)
            }
    
    @classmethod
    async def _tcp_port_check(cls, ip: str, port: int, timeout: int = 3) -> Dict[str, Any]:
        """TCP端口连通性检测"""
        try:
            # 创建连接并设置超时
            future = asyncio.open_connection(ip, port)
            reader, writer = await asyncio.wait_for(future, timeout=timeout)
            
            # 关闭连接
            writer.close()
            await writer.wait_closed()
            
            return {
                "success": True,
                "method": f"tcp_port_{port}",
                "port": port,
                "error": None
            }
        except asyncio.TimeoutError:
            return {
                "success": False,
                "method": f"tcp_port_{port}",
                "port": port,
                "error": f"Connection timeout ({timeout}s)"
            }
        except Exception as e:
            return {
                "success": False,
                "method": f"tcp_port_{port}",
                "port": port,
                "error": str(e)
            }
    
    @classmethod
    def _extract_ping_time(cls, ping_output: str) -> str:
        """从ping输出中提取响应时间"""
        try:
            import re
            patterns = [
                r'时间[=<](\d+\.?\d*)ms',  # Windows中文
                r'time[=<](\d+\.?\d*)\s*ms',  # Linux/macOS英文
                r'time=(\d+\.?\d*)\s*ms',  # 通用格式
            ]
            
            for pattern in patterns:
                match = re.search(pattern, ping_output, re.IGNORECASE)
                if match:
                    return f"{match.group(1)}ms"
        except:
            pass
        return None
