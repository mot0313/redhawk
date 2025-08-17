-- 清理 hardware_type_dict，只保留 check_redfish 支持的硬件类型
-- 基于 https://github.com/bb-Ricardo/check_redfish 项目实际支持的监控组件
-- 支持的组件：--storage, --proc, --memory, --power, --temp, --fan, --nic, --bmc, --info, --firmware

-- 1. 备份当前数据（可选）
-- CREATE TABLE hardware_type_dict_backup AS SELECT * FROM hardware_type_dict;

-- 2. 删除不需要的硬件类型
-- 保留的核心类型对应 check_redfish 支持的监控组件
DELETE FROM hardware_type_dict 
WHERE type_code NOT IN (
    'cpu',              -- --proc: processor -> cpu
    'memory',           -- --memory: memory -> memory  
    'system',           -- --info: system info -> system
    'storage',          -- --storage: storage devices (统一存储设备)
    'power',            -- --power: power supply -> power
    'temperature',      -- --temp: temperature sensors -> temperature
    'fan',              -- --fan: fan -> fan
    'network',          -- --nic: network interface -> network
    'bmc',              -- --bmc: BMC info -> bmc
    'firmware',         -- --firmware: firmware info -> firmware
    'unknown'           -- 兜底类型
);

-- 3. 确保核心类型存在（如果之前删除了）
-- CPU
INSERT INTO hardware_type_dict (type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time)
SELECT 'cpu', 'CPU处理器', 'Central Processing Unit 中央处理器', 'compute', 1, 1, 'system', NOW(), '', NOW()
WHERE NOT EXISTS (SELECT 1 FROM hardware_type_dict WHERE type_code = 'cpu');

-- Memory
INSERT INTO hardware_type_dict (type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time)
SELECT 'memory', '内存', 'RAM 随机存取存储器', 'compute', 2, 1, 'system', NOW(), '', NOW()
WHERE NOT EXISTS (SELECT 1 FROM hardware_type_dict WHERE type_code = 'memory');

-- System Info
INSERT INTO hardware_type_dict (type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time)
SELECT 'system', '系统信息', '系统基本信息（型号、BIOS、序列号等）', 'system', 3, 1, 'system', NOW(), '', NOW()
WHERE NOT EXISTS (SELECT 1 FROM hardware_type_dict WHERE type_code = 'system');

-- Storage (统一存储设备)
INSERT INTO hardware_type_dict (type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time)
SELECT 'storage', '存储设备', '存储设备（硬盘、SSD、控制器等）', 'storage', 10, 1, 'system', NOW(), '', NOW()
WHERE NOT EXISTS (SELECT 1 FROM hardware_type_dict WHERE type_code = 'storage');

-- Power
INSERT INTO hardware_type_dict (type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time)
SELECT 'power', '电源', 'Power Supply Unit 电源供应单元', 'power', 20, 1, 'system', NOW(), '', NOW()
WHERE NOT EXISTS (SELECT 1 FROM hardware_type_dict WHERE type_code = 'power');

-- Temperature  
INSERT INTO hardware_type_dict (type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time)
SELECT 'temperature', '温度传感器', '温度监控传感器', 'cooling', 30, 1, 'system', NOW(), '', NOW()
WHERE NOT EXISTS (SELECT 1 FROM hardware_type_dict WHERE type_code = 'temperature');

-- Fan
INSERT INTO hardware_type_dict (type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time)
SELECT 'fan', '风扇', '散热风扇', 'cooling', 31, 1, 'system', NOW(), '', NOW()
WHERE NOT EXISTS (SELECT 1 FROM hardware_type_dict WHERE type_code = 'fan');

-- Network (--nic: network interface -> network)
INSERT INTO hardware_type_dict (type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time)
SELECT 'network', '网络接口', '网络接口卡状态监控', 'network', 40, 1, 'system', NOW(), '', NOW()
WHERE NOT EXISTS (SELECT 1 FROM hardware_type_dict WHERE type_code = 'network');

-- BMC (--bmc: BMC info -> bmc)
INSERT INTO hardware_type_dict (type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time)
SELECT 'bmc', 'BMC管理器', 'Baseboard Management Controller 基板管理控制器', 'management', 41, 1, 'system', NOW(), '', NOW()
WHERE NOT EXISTS (SELECT 1 FROM hardware_type_dict WHERE type_code = 'bmc');

-- Firmware (--firmware: firmware info -> firmware)
INSERT INTO hardware_type_dict (type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time)
SELECT 'firmware', '固件版本', '系统固件信息监控', 'management', 42, 1, 'system', NOW(), '', NOW()
WHERE NOT EXISTS (SELECT 1 FROM hardware_type_dict WHERE type_code = 'firmware');

-- Unknown (兜底类型)
INSERT INTO hardware_type_dict (type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time)
SELECT 'unknown', '未知硬件', '未识别的硬件组件', 'other', 99, 1, 'system', NOW(), '', NOW()
WHERE NOT EXISTS (SELECT 1 FROM hardware_type_dict WHERE type_code = 'unknown');

-- 4. 验证清理结果
SELECT 'Remaining hardware types after cleanup:' as info;
SELECT type_code, type_name, category, sort_order 
FROM hardware_type_dict 
ORDER BY sort_order, type_code;

-- 5. 检查是否有孤立的urgency rules
SELECT 'Checking orphaned urgency rules:' as info;
SELECT DISTINCT r.hardware_type
FROM business_hardware_urgency_rules r
LEFT JOIN hardware_type_dict h ON r.hardware_type = h.type_code
WHERE h.type_code IS NULL
ORDER BY r.hardware_type;

SELECT 'Total hardware types remaining:' as info, COUNT(*) as count
FROM hardware_type_dict;
