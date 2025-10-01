"""
设备连通性检测服务
基于业务IP判断设备在线/离线状态
"""
import asyncio
import platform
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from module_redfish.entity.do.device_do import DeviceInfoDO
from module_redfish.dao.device_dao import DeviceDao
from utils.log_util import logger


class ConnectivityService:
    """设备连通性检测服务"""
    
    @classmethod
    async def check_device_business_ip_connectivity(
        cls,
        db: AsyncSession,
        device_id: int = None,
        business_ip: str = None
    ) -> Dict[str, Any]:
        """
        检测单个设备的业务IP连通性
        
        Args:
            db: 数据库会话
            device_id: 设备ID（与business_ip二选一）
            business_ip: 业务IP（与device_id二选一）
            
        Returns:
            Dict[str, Any]: 连通性检测结果
        """
        if device_id:
            device = await DeviceDao.get_device_by_id(db, device_id)
            if not device:
                return {
                    "online": False, 
                    "error": "设备不存在", 
                    "check_time": datetime.now().isoformat()
                }
            target_ip = device.business_ip
            hostname = device.hostname
        elif business_ip:
            target_ip = business_ip
            hostname = business_ip
        else:
            return {
                "online": False, 
                "error": "必须提供device_id或business_ip", 
                "check_time": datetime.now().isoformat()
            }
        
        if not target_ip:
            return {
                "online": False, 
                "error": "设备业务IP为空", 
                "check_time": datetime.now().isoformat()
            }
        
        # 执行多种连通性检测
        start_time = time.time()
        
        # 主要方法：ping检测
        ping_result = await cls._ping_check(target_ip)
        
        # 辅助方法：常用端口检测（只在ping失败时执行，提高效率）
        port_results = {}
        if not ping_result.get("success", False):
            # 并发检测常用端口
            port_tasks = {
                "ssh": cls._tcp_port_check(target_ip, 22, timeout=2),
                "http": cls._tcp_port_check(target_ip, 80, timeout=2),
                "https": cls._tcp_port_check(target_ip, 443, timeout=2),
            }
            
            port_results = {}
            for port_name, task in port_tasks.items():
                try:
                    port_results[port_name] = await task
                except Exception as e:
                    port_results[port_name] = {
                        "success": False,
                        "method": f"tcp_port_{port_name}",
                        "error": str(e)
                    }
        
        # 综合判断在线状态
        online = ping_result.get("success", False) or any(
            result.get("success", False) for result in port_results.values()
        )
        
        check_duration = round(time.time() - start_time, 3)
        
        result = {
            "online": online,
            "hostname": hostname,
            "business_ip": target_ip,
            "check_duration_ms": check_duration * 1000,
            "ping": ping_result,
            "check_time": datetime.now().isoformat()
        }
        
        # 只在ping失败时包含端口检测结果
        if port_results:
            result["port_checks"] = port_results
        
        return result
    
    @classmethod
    async def check_device_oob_ip_connectivity(
        cls,
        db: AsyncSession,
        device_id: int = None,
        oob_ip: str = None
    ) -> Dict[str, Any]:
        """
        检测单个设备的带外IP连通性
        
        Args:
            db: 数据库会话
            device_id: 设备ID（与oob_ip二选一）
            oob_ip: 带外IP（与device_id二选一）
            
        Returns:
            Dict[str, Any]: 带外IP连通性检测结果
        """
        if device_id:
            device = await DeviceDao.get_device_by_id(db, device_id)
            if not device:
                return {
                    "online": False, 
                    "error": "设备不存在", 
                    "check_time": datetime.now().isoformat()
                }
            target_ip = device.oob_ip
            hostname = device.hostname
        elif oob_ip:
            target_ip = oob_ip
            hostname = oob_ip
        else:
            return {
                "online": False, 
                "error": "必须提供device_id或oob_ip", 
                "check_time": datetime.now().isoformat()
            }
        
        if not target_ip:
            return {
                "online": False, 
                "error": "设备带外IP为空", 
                "check_time": datetime.now().isoformat()
            }
        
        # 执行多种连通性检测
        start_time = time.time()
        
        # 主要方法：ping检测
        ping_result = await cls._ping_check(target_ip)
        
        # 辅助方法：常用端口检测（只在ping失败时执行，提高效率）
        port_results = {}
        if not ping_result.get("success", False):
            # 并发检测常用端口（带外IP常用端口）
            port_tasks = {
                "https": cls._tcp_port_check(target_ip, 443, timeout=2),
                "http": cls._tcp_port_check(target_ip, 80, timeout=2),
                "ssh": cls._tcp_port_check(target_ip, 22, timeout=2),
            }
            
            port_results = {}
            for port_name, task in port_tasks.items():
                try:
                    port_results[port_name] = await task
                except Exception as e:
                    port_results[port_name] = {
                        "success": False,
                        "method": f"tcp_port_{port_name}",
                        "error": str(e)
                    }
        
        # 综合判断在线状态
        online = ping_result.get("success", False) or any(
            result.get("success", False) for result in port_results.values()
        )
        
        check_duration = round(time.time() - start_time, 3)
        
        result = {
            "online": online,
            "hostname": hostname,
            "oob_ip": target_ip,
            "check_duration_ms": check_duration * 1000,
            "ping": ping_result,
            "check_time": datetime.now().isoformat()
        }
        
        # 只在ping失败时包含端口检测结果
        if port_results:
            result["port_checks"] = port_results
        
        return result
    
    @classmethod
    async def batch_check_connectivity(
        cls,
        db: AsyncSession,
        device_ids: List[int] = None,
        max_concurrent: int = 20
    ) -> Dict[str, Any]:
        """
        批量检测设备连通性
        
        Args:
            db: 数据库会话
            device_ids: 设备ID列表，为空则检测所有有业务IP的设备
            max_concurrent: 最大并发检测数
            
        Returns:
            Dict[str, Any]: 批量检测结果
        """
        # 查询设备
        if device_ids:
                    query = select(DeviceInfoDO).where(
            DeviceInfoDO.device_id.in_(device_ids),
            DeviceInfoDO.business_ip.isnot(None)
        )
        else:
            query = select(DeviceInfoDO).where(DeviceInfoDO.business_ip.isnot(None))
        
        result = await db.execute(query)
        devices = result.scalars().all()
        
        if not devices:
            return {
                "total_devices": 0,
                "online_devices": 0,
                "offline_devices": 0,
                "check_duration_ms": 0,
                "check_time": datetime.now().isoformat(),
                "details": []
            }
        
        start_time = time.time()
        logger.info(f"开始批量检测 {len(devices)} 台设备的业务IP连通性")
        
        # 使用信号量限制并发数
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def check_single_device(device):
            async with semaphore:
                connectivity = await cls.check_device_business_ip_connectivity(
                    db, device_id=device.device_id
                )
                return {
                    "device_id": device.device_id,
                    "hostname": device.hostname,
                    "business_ip": device.business_ip,
                    "location": device.location,
                    "online": connectivity["online"],
                    "check_details": connectivity
                }
        
        # 并发执行检测
        tasks = [check_single_device(device) for device in devices]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                device = devices[i]
                logger.error(f"检测设备 {device.hostname} 连通性时发生异常: {result}")
                valid_results.append({
                    "device_id": device.device_id,
                    "hostname": device.hostname,
                    "business_ip": device.business_ip,
                    "location": device.location,
                    "online": False,
                    "check_details": {
                        "online": False,
                        "error": str(result),
                        "check_time": datetime.now().isoformat()
                    }
                })
            else:
                valid_results.append(result)
        
        # 统计结果
        online_count = sum(1 for result in valid_results if result["online"])
        offline_count = len(valid_results) - online_count
        total_duration = round((time.time() - start_time) * 1000, 2)
        
        logger.info(f"批量连通性检测完成: {online_count} 在线, {offline_count} 离线, 耗时 {total_duration}ms")
        
        return {
            "total_devices": len(valid_results),
            "online_devices": online_count,
            "offline_devices": offline_count,
            "check_duration_ms": total_duration,
            "check_time": datetime.now().isoformat(),
            "details": valid_results
        }
    
    @classmethod
    async def batch_check_oob_connectivity(
        cls,
        db: AsyncSession,
        device_ids: List[int] = None,
        max_concurrent: int = 20
    ) -> Dict[str, Any]:
        """
        批量检测设备带外IP连通性
        
        Args:
            db: 数据库会话
            device_ids: 设备ID列表，为空则检测所有有带外IP的设备
            max_concurrent: 最大并发检测数
            
        Returns:
            Dict[str, Any]: 批量检测结果
        """
        # 查询设备
        if device_ids:
            query = select(DeviceInfoDO).where(
                DeviceInfoDO.device_id.in_(device_ids),
                DeviceInfoDO.oob_ip.isnot(None)
            )
        else:
            query = select(DeviceInfoDO).where(DeviceInfoDO.oob_ip.isnot(None))
        
        result = await db.execute(query)
        devices = result.scalars().all()
        
        if not devices:
            return {
                "total_devices": 0,
                "online_devices": 0,
                "offline_devices": 0,
                "check_duration_ms": 0,
                "check_time": datetime.now().isoformat(),
                "details": []
            }
        
        start_time = time.time()
        logger.info(f"开始批量检测 {len(devices)} 台设备的带外IP连通性")
        
        # 使用信号量限制并发数
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def check_single_device_oob(device):
            async with semaphore:
                connectivity = await cls.check_device_oob_ip_connectivity(
                    db, device_id=device.device_id
                )
                return {
                    "device_id": device.device_id,
                    "hostname": device.hostname,
                    "oob_ip": device.oob_ip,
                    "location": device.location,
                    "online": connectivity["online"],
                    "check_details": connectivity
                }
        
        # 并发执行检测
        tasks = [check_single_device_oob(device) for device in devices]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                device = devices[i]
                logger.error(f"检测设备 {device.hostname} 带外IP连通性时发生异常: {result}")
                valid_results.append({
                    "device_id": device.device_id,
                    "hostname": device.hostname,
                    "oob_ip": device.oob_ip,
                    "location": device.location,
                    "online": False,
                    "check_details": {
                        "online": False,
                        "error": str(result),
                        "check_time": datetime.now().isoformat()
                    }
                })
            else:
                valid_results.append(result)
        
        # 统计结果
        online_count = sum(1 for result in valid_results if result["online"])
        offline_count = len(valid_results) - online_count
        total_duration = round((time.time() - start_time) * 1000, 2)
        
        logger.info(f"批量带外IP连通性检测完成: {online_count} 在线, {offline_count} 离线, 耗时 {total_duration}ms")
        
        return {
            "total_devices": len(valid_results),
            "online_devices": online_count,
            "offline_devices": offline_count,
            "check_duration_ms": total_duration,
            "check_time": datetime.now().isoformat(),
            "details": valid_results
        }
    
    @classmethod
    async def get_connectivity_statistics(
        cls,
        db: AsyncSession,
        use_cache: bool = True,
        cache_ttl_minutes: int = 5
    ) -> Dict[str, Any]:
        """
        获取设备连通性统计（支持缓存）
        
        Args:
            db: 数据库会话
            use_cache: 是否使用缓存
            cache_ttl_minutes: 缓存时间（分钟）
            
        Returns:
            Dict[str, Any]: 连通性统计
        """
        cache_key = "connectivity_stats"
        
        if use_cache:
            try:
                from module_admin.service.cache_service import CacheService
                cached_result = await CacheService.get_cache(cache_key)
                if cached_result:
                    return cached_result
            except Exception as e:
                logger.warning(f"获取缓存失败，将执行实时检测: {e}")
        
        try:
            # 执行批量连通性检测
            connectivity_result = await cls.batch_check_connectivity(db)
            
            # 缓存结果
            if use_cache:
                try:
                    from module_admin.service.cache_service import CacheService
                    await CacheService.set_cache(
                        cache_key, 
                        connectivity_result, 
                        cache_ttl_minutes * 60
                    )
                except Exception as e:
                    logger.warning(f"设置缓存失败: {e}")
            
            return connectivity_result
            
        except Exception as e:
            logger.error(f"获取连通性统计失败: {e}")
            # 返回默认值
            return {
                "total_devices": 0,
                "online_devices": 0,
                "offline_devices": 0,
                "check_duration_ms": 0,
                "check_time": datetime.now().isoformat(),
                "details": [],
                "error": str(e)
            }
    
    @classmethod
    async def _ping_check(cls, ip: str, timeout: int = 3, count: int = 1) -> Dict[str, Any]:
        """
        跨平台Ping检测
        """
        try:
            # 根据操作系统选择ping命令参数
            system = platform.system().lower()
            if system == 'windows':
                cmd = ['ping', '-n', str(count), '-w', str(timeout * 1000), ip]
            else:  # Linux/macOS
                cmd = ['ping', '-c', str(count), '-W', str(timeout), ip]
            
            # 执行ping命令
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            success = process.returncode == 0
            output = stdout.decode() if stdout else stderr.decode()
            
            return {
                "success": success,
                "method": "ping",
                "response_time": cls._extract_ping_time(output) if success else None,
                "error": None if success else f"Ping failed (返回码: {process.returncode})"
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
        """
        TCP端口连通性检测
        """
        try:
            future = asyncio.open_connection(ip, port)
            reader, writer = await asyncio.wait_for(future, timeout=timeout)
            
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
                "error": f"连接超时 ({timeout}s)"
            }
        except Exception as e:
            return {
                "success": False,
                "method": f"tcp_port_{port}",
                "port": port,
                "error": str(e)
            }
    
    @classmethod
    def _extract_ping_time(cls, ping_output: str) -> Optional[str]:
        """
        从ping输出中提取响应时间（跨平台）
        """
        try:
            import re
            # 支持多种格式
            patterns = [
                r'时间[=<](\d+\.?\d*)ms',                    # Windows中文
                r'time[=<](\d+\.?\d*)\s*ms',                # Linux/macOS英文 time=XXms
                r'time=(\d+\.?\d*)\s*ms',                   # 通用格式
                r'平均\s*=\s*(\d+\.?\d*)ms',                # Windows中文平均值
                r'round-trip.*?=\s*(\d+\.?\d*)/.*?ms',      # macOS格式: round-trip min/avg/max/stddev = 23.523/...
                r'rtt.*?=\s*(\d+\.?\d*)/.*?ms',             # 某些Linux: rtt min/avg/max/mdev = XX.XX/...
                r'(\d+\.?\d*)\s*ms',                        # 简单匹配任何数字+ms
            ]
            
            for pattern in patterns:
                match = re.search(pattern, ping_output, re.IGNORECASE)
                if match:
                    return f"{match.group(1)}ms"
        except Exception:
            pass
        return None 