"""
厂商适配器注册与选择（adapters）
"""
from typing import Dict, Type

from .base import BaseVendorAdaptor, GenericAdaptor

# 导入各厂商适配器（先占位，以后逐步完善具体规则）
try:
    from .hpe import HpeAdaptor
except Exception:  # pragma: no cover
    HpeAdaptor = None

try:
    from .dell import DellAdaptor
except Exception:  # pragma: no cover
    DellAdaptor = None

try:
    from .lenovo import LenovoAdaptor
except Exception:  # pragma: no cover
    LenovoAdaptor = None

try:
    from .huawei import HuaweiAdaptor
except Exception:  # pragma: no cover
    HuaweiAdaptor = None

try:
    from .fujitsu import FujitsuAdaptor
except Exception:  # pragma: no cover
    FujitsuAdaptor = None

try:
    from .supermicro import SupermicroAdaptor
except Exception:  # pragma: no cover
    SupermicroAdaptor = None

try:
    from .inspur import InspurAdaptor
except Exception:  # pragma: no cover
    InspurAdaptor = None

try:
    from .cisco import CiscoAdaptor
except Exception:  # pragma: no cover
    CiscoAdaptor = None

try:
    from .gigabyte import GigabyteAdaptor
except Exception:  # pragma: no cover
    GigabyteAdaptor = None


_ADAPTORS = []
for cls in [HpeAdaptor, DellAdaptor, LenovoAdaptor, HuaweiAdaptor, FujitsuAdaptor, SupermicroAdaptor, InspurAdaptor, CiscoAdaptor, GigabyteAdaptor]:
    if cls is not None:
        _ADAPTORS.append(cls())


def get_vendor_adaptor(manufacturer: str) -> BaseVendorAdaptor:
    name = (manufacturer or "").upper()
    for adaptor in _ADAPTORS:
        if any(v in name for v in adaptor.vendor_names):
            return adaptor
    return GenericAdaptor()


