"""
设备管理Service层 - 核心CRUD操作
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from module_redfish.dao.device_dao import DeviceDao
from module_redfish.dao.alert_dao import AlertDao
from module_redfish.entity.do.device_do import DeviceInfoDO
from module_redfish.entity.vo.device_vo import (
    DevicePageQueryModel, AddDeviceModel, EditDeviceModel, DeleteDeviceModel,
    DeviceDetailModel, DeviceHealthModel, DeviceHealthStatusModel, DeviceModel
)
from module_redfish.core.redfish_client import encrypt_password, decrypt_password
from module_redfish.service.business_rule_service import BusinessRuleService
# from module_redfish.celery_tasks import recalculate_urgency_for_device
from module_admin.entity.vo.common_vo import CrudResponseModel
from utils.response_util import ResponseUtil
from utils.page_util import PageResponseModel, PageUtil
from utils.log_util import logger


class DeviceService:
    """设备管理服务 - 核心CRUD操作"""
    
    @classmethod
    async def get_device_list_services(
        cls,
        db: AsyncSession,
        query_object: DevicePageQueryModel,
        is_page: bool = False
    ) -> PageResponseModel:
        """
        获取设备列表
        
        Args:
            db: 数据库会话
            query_object: 查询对象
            is_page: 是否分页
            
        Returns:
            PageResponseModel: 分页响应
        """
        device_list, total = await DeviceDao.get_device_list(db, query_object, is_page)
        
        # 获取业务类型映射字典
        business_type_mapping = {}
        try:
            business_types = await BusinessRuleService.get_business_types_services(db)
            business_type_mapping = {bt['typeCode']: bt['typeName'] for bt in business_types}
        except Exception as e:
            logger.warning(f"获取业务类型映射失败: {str(e)}")
        
        # 解密密码字段并转换业务类型
        for device in device_list:
            device.redfish_password = "******"  # 隐藏密码
            # 将 type_code 转换为 type_name
            if device.business_type and device.business_type in business_type_mapping:
                device.business_type = business_type_mapping[device.business_type]
        
        if is_page:
            # 使用DevicePageResponseModel创建分页响应
            from module_redfish.entity.vo.device_vo import DevicePageResponseModel
            device_dict_list = [device.__dict__.copy() for device in device_list]
            for device_dict in device_dict_list:
                device_dict.pop('_sa_instance_state', None)
            return DevicePageResponseModel.create(
                devices=device_dict_list,
                page_num=query_object.page_num,
                page_size=query_object.page_size,
                total=total
            )
        else:
            # 非分页模式，返回设备列表
            from module_redfish.entity.vo.device_vo import DeviceResponseModel
            device_dict_list = [device.__dict__.copy() for device in device_list]
            for device_dict in device_dict_list:
                device_dict.pop('_sa_instance_state', None)
            return [DeviceResponseModel(**device_dict) for device_dict in device_dict_list]
    
    @classmethod
    async def get_device_detail_services(cls, db: AsyncSession, device_id: int, for_edit: bool = False) -> DeviceDetailModel:
        """
        获取设备详情
        
        Args:
            db: 数据库会话
            device_id: 设备ID
            for_edit: 是否用于编辑
            
        Returns:
            DeviceDetailModel: 设备详情
        """
        device = await DeviceDao.get_device_by_id(db, device_id)
        if not device:
            raise ValueError("设备不存在")
        
        # 获取设备健康状态
        try:
            health_status_info = await cls._get_device_health_status(db, device_id)
        except Exception as e:
            logger.warning(f"获取设备健康状态失败: {str(e)}")
            health_status_info = DeviceHealthStatusModel(
                overall_status='unknown',
                components={},
                last_check_time=None,
                alert_count=0
            )
        
        # 获取业务类型映射
        business_type_name = device.business_type
        try:
            business_types = await BusinessRuleService.get_business_types_services(db)
            business_type_mapping = {bt['typeCode']: bt['typeName'] for bt in business_types}
            if device.business_type and device.business_type in business_type_mapping:
                business_type_name = business_type_mapping[device.business_type]
        except Exception as e:
            logger.warning(f"获取业务类型映射失败: {str(e)}")
        
        # 转换为详情模型
        device_dict = device.__dict__.copy()
        device_dict.pop('_sa_instance_state', None)
        
        # 处理密码字段
        if for_edit:
            # 编辑模式下解密密码
            try:
                device_dict['redfish_password'] = decrypt_password(device.redfish_password)
            except ValueError as e:
                # 密码解密失败，返回空字符串，让用户重新输入
                logger.warning(f"设备 {device.hostname} 密码解密失败，编辑时需要重新输入密码: {str(e)}")
                device_dict['redfish_password'] = ""
        else:
            # 查看模式下隐藏密码
            device_dict['redfish_password'] = "******"
        
        # 替换业务类型为名称
        device_dict['business_type'] = business_type_name
        
        # 构造设备详情模型
        device_model = DeviceModel(**device_dict)
        
        return DeviceDetailModel(
            device=device_model,
            health_status=health_status_info.overall_status,
            last_check_time=health_status_info.last_check_time,
            connection_status='connected' if health_status_info.overall_status != 'unknown' else 'unknown'
        )
    
    @classmethod
    async def add_device_services(cls, db: AsyncSession, device: AddDeviceModel) -> ResponseUtil:
        """
        添加设备
        
        Args:
            db: 数据库会话
            device: 设备信息
            
        Returns:
            ResponseUtil: 响应结果
        """
        try:
            # 检查设备是否已存在
            existing_device = await DeviceDao.get_device_by_hostname_or_ip(
                db, device.hostname, device.oob_ip
            )
            if existing_device:
                return ResponseUtil.failure(msg="设备已存在（主机名或带外IP重复）")
            
            # 加密密码
            device.redfish_password = encrypt_password(device.redfish_password)
            
            # 添加设备
            await DeviceDao.add_device(db, device)
            await db.commit()
            
            logger.info(f"添加设备成功: {device.hostname}")
            return ResponseUtil.success(msg="添加设备成功")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"添加设备失败: {str(e)}")
            return ResponseUtil.failure(msg="添加设备失败")

    @classmethod
    async def edit_device_services(cls, db: AsyncSession, device: EditDeviceModel) -> ResponseUtil:
        """
        编辑设备
        
        Args:
            db: 数据库会话
            device: 设备信息
            
        Returns:
            ResponseUtil: 响应结果
        """
        try:
            # 检查设备是否存在
            existing_device = await DeviceDao.get_device_by_id(db, device.device_id)
            if not existing_device:
                return ResponseUtil.failure(msg="设备不存在")
            
            # 检查主机名和IP是否与其他设备冲突
            if device.hostname or device.oob_ip:
                conflict_device = await DeviceDao.get_device_by_hostname_or_ip(
                    db, device.hostname, device.oob_ip
                )
                if conflict_device and conflict_device.device_id != device.device_id:
                    return ResponseUtil.failure(msg="主机名或带外IP与其他设备冲突")
            
            # 如果更新了密码，需要加密
            if device.redfish_password and device.redfish_password != "******":
                device.redfish_password = encrypt_password(device.redfish_password)
            else:
                # 如果密码是掩码，保持原有密码不变
                device.redfish_password = existing_device.redfish_password
            
            # 更新设备
            await DeviceDao.edit_device(db, device)
            await db.commit()
            
            logger.info(f"编辑设备成功: {device.hostname}")
            
            # 事务已提交，后续操作失败不影响数据库
            try:
                # 如果业务类型发生变化，重新计算紧急度
                if device.business_type and device.business_type != existing_device.business_type:
                    # TODO: 实现紧急度重算任务
                    logger.info(f"设备 {device.device_id} 业务类型已变更，需要重新计算紧急度")
                    # recalculate_urgency_for_device.delay(device.device_id)
            except Exception as e:
                logger.warning(f"触发紧急度重算失败: {str(e)}")
            
            return ResponseUtil.success(msg="编辑设备成功")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"编辑设备失败: {str(e)}")
            return ResponseUtil.failure(msg="编辑设备失败")

    @classmethod
    async def delete_device_services(cls, db: AsyncSession, delete_device: DeleteDeviceModel) -> ResponseUtil:
        """
        删除设备
        
        Args:
            db: 数据库会话
            delete_device: 删除设备信息
            
        Returns:
            ResponseUtil: 响应结果
        """
        try:
            device_ids = [int(id.strip()) for id in delete_device.device_ids.split(',') if id.strip()]
            if not device_ids:
                return ResponseUtil.failure(msg="未选择要删除的设备")
            
            # 检查设备是否存在
            for device_id in device_ids:
                device = await DeviceDao.get_device_by_id(db, device_id)
                if not device:
                    return ResponseUtil.failure(msg=f"设备ID {device_id} 不存在")
            
            # 删除设备
            success_count = 0
            for device_id in device_ids:
                try:
                    await DeviceDao.delete_device_by_ids(db, str(device_id))
                    success_count += 1
                except Exception as e:
                    logger.error(f"删除设备 {device_id} 失败: {str(e)}")
            
            await db.commit()
            
            # 事务已提交，记录日志
            if success_count == len(device_ids):
                logger.info(f"删除设备成功: {delete_device.device_ids}")
                return ResponseUtil.success(msg=f"成功删除 {success_count} 台设备")
            else:
                logger.info(f"部分删除设备成功: {success_count}/{len(device_ids)}")
                return ResponseUtil.success(msg=f"部分删除成功: {success_count}/{len(device_ids)} 台设备")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"删除设备失败: {str(e)}")
            return ResponseUtil.failure(msg="删除设备失败")
    
    @classmethod
    async def get_monitoring_devices_services(cls, db: AsyncSession) -> List[Dict[str, Any]]:
        """
        获取启用监控的设备列表
        
        Args:
            db: 数据库会话
            
        Returns:
            List[Dict[str, Any]]: 设备列表
        """
        devices = await DeviceDao.get_monitoring_devices(db)
        
        result = []
        for device in devices:
            # 解密密码用于监控
            decrypted_password = decrypt_password(device.redfish_password)
            
            result.append({
                'device_id': device.device_id,
                'hostname': device.hostname,
                'business_ip': device.business_ip,
                'oob_ip': device.oob_ip,
                'oob_port': device.oob_port,
                'redfish_username': device.redfish_username,
                'redfish_password': decrypted_password,
                'location': device.location,
                'technical_system': device.technical_system,
                'manufacturer': device.manufacturer,
                'model': device.model
            })
        
        return result
    
    @classmethod
    async def update_device_system_info_services(
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
        try:
            success = await DeviceDao.update_device_system_info(db, device_id, system_info)
            if success:
                logger.info(f"成功更新设备 {device_id} 的系统信息")
            return success
        except Exception as e:
            logger.error(f"更新设备系统信息失败: {str(e)}")
            return False
    
    @classmethod
    async def get_device_statistics_services(cls, db: AsyncSession):
        """
        获取设备统计信息
        
        Args:
            db: 数据库会话
            
        Returns:
            DeviceStatsResponseModel: 统计信息
        """
        from module_redfish.entity.vo.device_vo import DeviceStatsResponseModel
        stats = await DeviceDao.get_device_statistics(db)
        return DeviceStatsResponseModel.create(stats)

    @classmethod
    async def _get_device_health_status(cls, db: AsyncSession, device_id: int) -> DeviceHealthStatusModel:
        """
        获取设备健康状态（内部方法）
        
        Args:
            db: 数据库会话
            device_id: 设备ID
            
        Returns:
            DeviceHealthStatusModel: 健康状态模型
        """
        # 获取设备的活跃告警
        try:
            alerts = await AlertDao.get_device_alerts(db, device_id)
            alert_count = len(alerts)
            
            # 根据告警情况确定整体状态
            if alert_count == 0:
                overall_status = 'ok'
            else:
                # 检查是否有紧急告警
                has_urgent = any(alert.urgency_level == 'urgent' for alert in alerts)
                overall_status = 'critical' if has_urgent else 'warning'
            
            # 组件状态统计
            components = {}
            for alert in alerts:
                component_type = alert.component_type or 'unknown'
                if component_type not in components:
                    components[component_type] = {
                        'status': 'warning',
                        'alert_count': 0
                    }
                components[component_type]['alert_count'] += 1
                if alert.urgency_level == 'urgent':
                    components[component_type]['status'] = 'critical'
            
            return DeviceHealthStatusModel(
                overall_status=overall_status,
                components=components,
                last_check_time=datetime.now(),
                alert_count=alert_count
            )
        except Exception as e:
            logger.error(f"获取设备健康状态失败: {str(e)}")
            return DeviceHealthStatusModel(
                overall_status='unknown',
                components={},
                last_check_time=None,
                alert_count=0
            )