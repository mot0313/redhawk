from typing import Dict, List, Any, Tuple
from .base import UnifiedComponent, BaseVendorAdaptor, _status_of, _normalize_health, _ignore_absent


class SupermicroAdaptor:
    vendor_names = ("SUPERMICRO", "SUPER SERVER")

    def normalize_system(self, system: Dict[str, Any]) -> UnifiedComponent:
        health, state = _status_of(system)
        return {"component_type": "system", "component_name": "System", "health_status": _normalize_health(health), "state": state, "raw": system}

    def normalize_processors(self, processors: List[Dict[str, Any]]) -> List[UnifiedComponent]:
        out: List[UnifiedComponent] = []
        for p in _ignore_absent(processors):
            health, state = _status_of(p)
            name = p.get("socket") or p.get("id") or p.get("name") or "Processor"
            out.append({"component_type": "processor", "component_name": name, "health_status": _normalize_health(health), "state": state, "raw": p})
        return out

    def normalize_memory(self, memory: List[Dict[str, Any]]) -> List[UnifiedComponent]:
        out: List[UnifiedComponent] = []
        for m in _ignore_absent(memory):
            health, state = _status_of(m)
            name = m.get("device_locator") or m.get("id") or m.get("name") or "Memory"
            out.append({"component_type": "memory", "component_name": name, "health_status": _normalize_health(health), "state": state, "raw": m})
        return out

    def normalize_storage(self, storage: List[Dict[str, Any]]) -> List[UnifiedComponent]:
        out: List[UnifiedComponent] = []
        for d in _ignore_absent(storage):
            health, state = _status_of(d)
            if (health in (None, "Unknown")) and state == "Enabled":
                health = "OK"
            name = d.get("name") or d.get("id") or d.get("model") or "Drive"
            out.append({"component_type": "storage", "component_name": name, "health_status": _normalize_health(health), "state": state, "raw": d})
        return out

    def normalize_power(self, power: List[Dict[str, Any]]) -> List[UnifiedComponent]:
        out: List[UnifiedComponent] = []
        for ps in _ignore_absent(power):
            health, state = _status_of(ps)
            name = ps.get("name") or ps.get("id") or "PowerSupply"
            out.append({"component_type": "power", "component_name": name, "health_status": _normalize_health(health), "state": state, "raw": ps})
        return out

    def normalize_thermal(self, temperatures: List[Dict[str, Any]], fans: List[Dict[str, Any]]) -> Tuple[List[UnifiedComponent], List[UnifiedComponent]]:
        temps_out: List[UnifiedComponent] = []
        for t in _ignore_absent(temperatures):
            health, state = _status_of(t)
            name = t.get("name") or t.get("id") or "Temp"
            temps_out.append({"component_type": "temperature", "component_name": name, "health_status": _normalize_health(health), "state": state, "raw": t})
        fans_out: List[UnifiedComponent] = []
        for f in _ignore_absent(fans):
            health, state = _status_of(f)
            name = f.get("name") or f.get("id") or "Fan"
            fans_out.append({"component_type": "fan", "component_name": name, "health_status": _normalize_health(health), "state": state, "raw": f})
        return temps_out, fans_out

    def postprocess(self, status: Dict[str, Any]) -> Dict[str, Any]:
        return status


