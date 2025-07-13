"""
设备管理DAO层
"""
from sqlalchemy import and_, or_, func, desc, asc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple, Dict, Any
from module_redfish.models import DeviceInfo
from module_redfish.entity.vo.device_vo import DevicePageQueryModel, AddDeviceModel, EditDeviceModel
from utils.page_util import PageUtil


class DeviceDao:
    """设备管理DAO"""
    
    @classmethod
    async def get_device_list(
        cls,
        db: AsyncSession,
        query_object: DevicePageQueryModel,
        is_page: bool = False
    ) -> Tuple[List[DeviceInfo], int]:
        """
        获取设备列表
        
        Args:
            db: 数据库会话
            query_object: 查询对象
            is_page: 是否分页
            
        Returns:
            Tuple[List[DeviceInfo], int]: 设备列表和总数
        """
        query = select(DeviceInfo)
        
        # 构建查询条件
        conditions = []
        
        if query_object.hostname:
            conditions.append(DeviceInfo.hostname.like(f'%{query_object.hostname}%'))
        
        if query_object.business_ip:
            conditions.append(DeviceInfo.business_ip.like(f'%{query_object.business_ip}%'))
        
        if query_object.oob_ip:
            conditions.append(DeviceInfo.oob_ip.like(f'%{query_object.oob_ip}%'))
        
        if query_object.location:
            conditions.append(DeviceInfo.location.like(f'%{query_object.location}%'))
        
        if query_object.technical_system:
            conditions.append(DeviceInfo.technical_system.like(f'%{query_object.technical_system}%'))
        
        if query_object.system_owner:
            conditions.append(DeviceInfo.system_owner.like(f'%{query_object.system_owner}%'))
        
        if query_object.manufacturer:
            conditions.append(DeviceInfo.manufacturer.like(f'%{query_object.manufacturer}%'))
        
        if query_object.monitor_enabled is not None:
            conditions.append(DeviceInfo.monitor_enabled == query_object.monitor_enabled)
        

        
        if query_object.health_status:
            conditions.append(DeviceInfo.health_status == query_object.health_status)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 排序
        query = query.order_by(desc(DeviceInfo.create_time))
        
        # 分页
        if is_page:
            # 获取总数
            count_query = select(func.count(DeviceInfo.device_id))
            if conditions:
                count_query = count_query.where(and_(*conditions))
            total_count = await db.scalar(count_query)
            
            # 分页查询
            query = query.offset((query_object.page_num - 1) * query_object.page_size).limit(query_object.page_size)
            result = await db.execute(query)
            device_list = result.scalars().all()
            
            return device_list, total_count
        else:
            result = await db.execute(query)
            device_list = result.scalars().all()
            return device_list, len(device_list)
    
    @classmethod
    async def get_device_by_id(cls, db: AsyncSession, device_id: int) -> Optional[DeviceInfo]:
        """
        根据ID获取设备信息
        
        Args:
            db: 数据库会话
            device_id: 设备ID
            
        Returns:
            Optional[DeviceInfo]: 设备信息
        """
        result = await db.execute(
            select(DeviceInfo).where(DeviceInfo.device_id == device_id)
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_device_by_ip(cls, db: AsyncSession, business_ip: str = None, oob_ip: str = None) -> Optional[DeviceInfo]:
        """
        根据IP获取设备信息
        
        Args:
            db: 数据库会话
            business_ip: 业务IP
            oob_ip: 带外IP
            
        Returns:
            Optional[DeviceInfo]: 设备信息
        """
        conditions = []
        if business_ip:
            conditions.append(DeviceInfo.business_ip == business_ip)
        if oob_ip:
            conditions.append(DeviceInfo.oob_ip == oob_ip)
        
        if not conditions:
            return None
        
        result = await db.execute(
            select(DeviceInfo).where(or_(*conditions))
        )
        return result.scalar_one_or_none()
    

    
    @classmethod
    async def add_device(cls, db: AsyncSession, device: AddDeviceModel) -> DeviceInfo:
        """
        添加设备
        
        Args:
            db: 数据库会话
            device: 设备信息
            
        Returns:
            DeviceInfo: 新增的设备信息
        """
        db_device = DeviceInfo(**device.model_dump())
        db.add(db_device)
        await db.commit()
        await db.refresh(db_device)
        return db_device
    
    @classmethod
    async def edit_device(cls, db: AsyncSession, device: EditDeviceModel) -> bool:
        """
        编辑设备
        
        Args:
            db: 数据库会话
            device: 设备信息
            
        Returns:
            bool: 是否成功
        """
        result = await db.execute(
            select(DeviceInfo).where(DeviceInfo.device_id == device.device_id)
        )
        db_device = result.scalar_one_or_none()
        
        if not db_device:
            return False
        
        # 更新字段
        update_data = device.model_dump(exclude={'device_id'}, exclude_none=True)
        for field, value in update_data.items():
            setattr(db_device, field, value)
        
        await db.commit()
        return True
    
    @classmethod
    async def delete_device(cls, db: AsyncSession, device_ids: List[int]) -> bool:
        """
        删除设备
        
        Args:
            db: 数据库会话
            device_ids: 设备ID列表
            
        Returns:
            bool: 是否成功
        """
        from sqlalchemy import delete
        await db.execute(
            delete(DeviceInfo).where(DeviceInfo.device_id.in_(device_ids))
        )
        await db.commit()
        return True
    
    @classmethod
    async def get_monitoring_devices(cls, db: AsyncSession) -> List[DeviceInfo]:
        """
        获取启用监控的设备列表
        
        Args:
            db: 数据库会话
            
        Returns:
            List[DeviceInfo]: 设备列表
        """
        result = await db.execute(
            select(DeviceInfo).where(
                DeviceInfo.monitor_enabled == 1
            ).order_by(DeviceInfo.device_id)
        )
        return result.scalars().all()
    
    @classmethod
    async def get_devices_by_location(cls, db: AsyncSession, location_pattern: str) -> List[DeviceInfo]:
        """
        根据位置模式获取设备列表
        
        Args:
            db: 数据库会话
            location_pattern: 位置模式
            
        Returns:
            List[DeviceInfo]: 设备列表
        """
        result = await db.execute(
            select(DeviceInfo).where(DeviceInfo.location.like(f'%{location_pattern}%'))
        )
        return result.scalars().all()
    
    @classmethod
    async def get_devices_by_manufacturer(cls, db: AsyncSession, manufacturer: str) -> List[DeviceInfo]:
        """
        根据制造商获取设备列表
        
        Args:
            db: 数据库会话
            manufacturer: 制造商
            
        Returns:
            List[DeviceInfo]: 设备列表
        """
        result = await db.execute(
            select(DeviceInfo).where(DeviceInfo.manufacturer == manufacturer)
        )
        return result.scalars().all()
    
    @classmethod
    async def update_device_system_info(
        cls, 
        db: AsyncSession, 
        device_id: int, 
        system_info: Dict[str, Any]
    ) -> bool:
        """
        更新设备系统信息
        
        Args:
            db: 数据库会话
            device_id: 设备ID
            system_info: 系统信息
            
        Returns:
            bool: 是否成功
        """
        result = await db.execute(
            select(DeviceInfo).where(DeviceInfo.device_id == device_id)
        )
        db_device = result.scalar_one_or_none()
        
        if not db_device:
            return False
        
        # 更新系统信息字段
        if 'manufacturer' in system_info:
            db_device.manufacturer = system_info['manufacturer']
        if 'model' in system_info:
            db_device.model = system_info['model']
        if 'serial_number' in system_info:
            db_device.serial_number = system_info['serial_number']
        
        await db.commit()
        return True
    
    @classmethod
    async def get_device_statistics(cls, db: AsyncSession) -> Dict[str, int]:
        """
        获取设备统计信息
        
        Args:
            db: 数据库会话
            
        Returns:
            Dict[str, int]: 统计信息
        """
        # 总设备数
        total_result = await db.execute(
            select(func.count(DeviceInfo.device_id))
        )
        total_devices = total_result.scalar()
        
        # 启用监控的设备数
        monitoring_result = await db.execute(
            select(func.count(DeviceInfo.device_id)).where(DeviceInfo.monitor_enabled == 1)
        )
        monitoring_devices = monitoring_result.scalar()
        
        # 健康状态为OK的设备数
        healthy_result = await db.execute(
            select(func.count(DeviceInfo.device_id)).where(DeviceInfo.health_status == 'ok')
        )
        healthy_devices = healthy_result.scalar()
        
        return {
            'total_devices': total_devices,
            'monitoring_devices': monitoring_devices,
            'healthy_devices': healthy_devices,
            'unhealthy_devices': total_devices - healthy_devices
        }

    @classmethod
    async def get_device_by_hostname_or_ip(
        cls, 
        db: AsyncSession, 
        hostname: str, 
        oob_ip: str
    ) -> Optional[DeviceInfo]:
        """
        根据主机名或带外IP获取设备信息（用于检查重复）
        
        Args:
            db: 数据库会话
            hostname: 主机名
            oob_ip: 带外IP
            
        Returns:
            Optional[DeviceInfo]: 设备信息
        """
        result = await db.execute(
            select(DeviceInfo).where(
                or_(
                    DeviceInfo.hostname == hostname,
                    DeviceInfo.oob_ip == oob_ip
                )
            )
        )
        return result.scalar_one_or_none() 