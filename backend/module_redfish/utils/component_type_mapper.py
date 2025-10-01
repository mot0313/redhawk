"""
统一组件类型到硬件类型字典码的归一化工具
输出一律小写，与 rules 和 hardware_type_dict 对齐
"""
from typing import Dict


_BASIC_MAP = {
    # 监控内部类型 -> 硬件字典码 (基于 check_redfish 支持的组件)
    "processor": "cpu",           # --proc: 处理器
    "cpu": "cpu",
    "memory": "memory",           # --memory: 内存
    "storage": "storage",         # --storage: 存储设备（统一）
    "disk": "storage",            # 统一到storage
    "power": "power",             # --power: 电源供应
    "fan": "fan",                 # --fan: 风扇
    "temperature": "temperature", # --temp: 温度传感器
    # 扩展映射
    "system": "system",           # --info: 系统信息
    "network": "network",         # --nic: 网络接口
    "bmc": "bmc",                 # --bmc: BMC管理器
    "firmware": "firmware",       # --firmware: 固件信息
    "downtime": "downtime",         # 宕机检测（业务IP连通性）
    "oob_connectivity": "oob_connectivity",  # 带外IP连通性
}


def to_hardware_code(component_type: str, raw: Dict) -> str:
    t = (component_type or "").strip().lower()
    if not t:
        return "unknown"

    # 存储统一：所有存储相关组件统一映射到 storage
    if t in ("storage", "disk"):
        return "storage"

    return _BASIC_MAP.get(t, t)



