"""
Redfish模块DO层统一入口
"""
from .base import Base
from .device_do import DeviceInfoDO
from .alert_do import AlertInfoDO
from .business_urgency_rule_do import BusinessHardwareUrgencyRulesDO
from .maintenance_schedule_do import MaintenanceScheduleDO
from .business_type_dict_do import BusinessTypeDictDO
from .hardware_type_dict_do import HardwareTypeDictDO

# 导出所有DO模型
__all__ = [
    'Base',
    # 核心表
    'DeviceInfoDO',
    'AlertInfoDO', 
    # 附属表
    'BusinessHardwareUrgencyRulesDO',

    'MaintenanceScheduleDO',
    'BusinessTypeDictDO',
    'HardwareTypeDictDO',
] 