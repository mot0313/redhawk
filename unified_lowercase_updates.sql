-- 统一数据库字段为小写的SQL脚本
-- 执行前请备份数据库

-- 1. 更新 hardware_type_dict 表的 type_code 字段为小写
UPDATE hardware_type_dict SET type_code = lower(type_code);

-- 2. 更新 business_hardware_urgency_rules 表的 hardware_type 字段为小写
UPDATE business_hardware_urgency_rules SET hardware_type = lower(hardware_type);

-- 3. 检查缺失的字典项并补齐
-- 根据 component_type_mapper.py 的输出，检查是否存在这些硬件类型码

-- 检查是否缺失 network (映射自 connectivity)
INSERT INTO hardware_type_dict (type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time)
SELECT 'network', '网络设备', '网络连接设备', 'network', 23, 1, 'system', NOW(), '', NOW()
WHERE NOT EXISTS (SELECT 1 FROM hardware_type_dict WHERE type_code = 'network');

-- 检查是否缺失 motherboard (映射自 system)  
INSERT INTO hardware_type_dict (type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time)  
SELECT 'motherboard', '主板系统', '系统主板', 'compute', 3, 1, 'system', NOW(), '', NOW()
WHERE NOT EXISTS (SELECT 1 FROM hardware_type_dict WHERE type_code = 'motherboard');

-- 检查是否缺失其他可能的硬件类型码
INSERT INTO hardware_type_dict (type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time)
SELECT 'unknown', '未知硬件', '未识别的硬件组件', 'other', 100, 1, 'system', NOW(), '', NOW()
WHERE NOT EXISTS (SELECT 1 FROM hardware_type_dict WHERE type_code = 'unknown');

-- 4. 验证更新结果
SELECT 'hardware_type_dict type_codes after update:' as info;
SELECT type_code, type_name FROM hardware_type_dict ORDER BY type_code;

SELECT 'business_hardware_urgency_rules hardware_types after update:' as info;
SELECT DISTINCT hardware_type FROM business_hardware_urgency_rules ORDER BY hardware_type;

-- 5. 检查component_type_mapper输出与字典的匹配情况
SELECT 'Checking coverage of component_type_mapper outputs:' as info;

-- 检查component_type_mapper可能输出的类型码是否都在字典中
WITH mapper_outputs AS (
    SELECT unnest(ARRAY['cpu', 'memory', 'disk', 'storage_controller', 'power', 'fan', 'temperature', 'motherboard', 'network', 'unknown']) as code
)
SELECT 
    m.code as mapper_output,
    CASE WHEN h.type_code IS NOT NULL THEN '✓ Found' ELSE '✗ Missing' END as status
FROM mapper_outputs m
LEFT JOIN hardware_type_dict h ON m.code = h.type_code
ORDER BY m.code;
