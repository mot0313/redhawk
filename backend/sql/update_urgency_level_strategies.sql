-- 硬件更换排期策略扩展SQL脚本
-- 为business_hardware_urgency_rules表添加immediate策略支持

-- 添加immediate策略的示例规则数据（如果表中还没有）
INSERT INTO business_hardware_urgency_rules (business_type, hardware_type, urgency_level, description, is_active, create_by, create_time)
SELECT 'core', 'cpu', 'immediate', '核心业务CPU故障-立即修复', 1, 'system', NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM business_hardware_urgency_rules 
    WHERE business_type = 'core' AND hardware_type = 'cpu' AND urgency_level = 'immediate'
);

INSERT INTO business_hardware_urgency_rules (business_type, hardware_type, urgency_level, description, is_active, create_by, create_time)
SELECT 'core', 'memory', 'immediate', '核心业务内存故障-立即修复', 1, 'system', NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM business_hardware_urgency_rules 
    WHERE business_type = 'core' AND hardware_type = 'memory' AND urgency_level = 'immediate'
);

INSERT INTO business_hardware_urgency_rules (business_type, hardware_type, urgency_level, description, is_active, create_by, create_time)
SELECT 'critical', 'storage', 'urgent', '关键业务存储故障-24小时内修复', 1, 'system', NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM business_hardware_urgency_rules 
    WHERE business_type = 'critical' AND hardware_type = 'storage' AND urgency_level = 'urgent'
);

INSERT INTO business_hardware_urgency_rules (business_type, hardware_type, urgency_level, description, is_active, create_by, create_time)
SELECT 'normal', 'fan', 'scheduled', '普通业务风扇故障-择期修复', 1, 'system', NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM business_hardware_urgency_rules 
    WHERE business_type = 'normal' AND hardware_type = 'fan' AND urgency_level = 'scheduled'
);

INSERT INTO business_hardware_urgency_rules (business_type, hardware_type, urgency_level, description, is_active, create_by, create_time)
SELECT 'normal', 'power', 'scheduled', '普通业务电源故障-择期修复', 1, 'system', NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM business_hardware_urgency_rules 
    WHERE business_type = 'normal' AND hardware_type = 'power' AND urgency_level = 'scheduled'
);

-- 添加业务类型字典数据（如果表存在）
INSERT INTO business_type_dict (type_code, type_name, type_description, sort_order, is_active, create_by, create_time)
SELECT 'core', '核心业务', '核心业务系统，要求立即响应', 1, 1, 'system', NOW()
WHERE NOT EXISTS (SELECT 1 FROM business_type_dict WHERE type_code = 'core')
AND EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'business_type_dict');

INSERT INTO business_type_dict (type_code, type_name, type_description, sort_order, is_active, create_by, create_time)
SELECT 'critical', '关键业务', '关键业务系统，要求快速响应', 2, 1, 'system', NOW()
WHERE NOT EXISTS (SELECT 1 FROM business_type_dict WHERE type_code = 'critical')
AND EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'business_type_dict');

INSERT INTO business_type_dict (type_code, type_name, type_description, sort_order, is_active, create_by, create_time)
SELECT 'normal', '普通业务', '普通业务系统，可择期处理', 3, 1, 'system', NOW()
WHERE NOT EXISTS (SELECT 1 FROM business_type_dict WHERE type_code = 'normal')
AND EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'business_type_dict');

-- 添加硬件类型字典数据（如果表存在）
INSERT INTO hardware_type_dict (type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time)
SELECT 'cpu', 'CPU处理器', '中央处理器', 'compute', 1, 1, 'system', NOW()
WHERE NOT EXISTS (SELECT 1 FROM hardware_type_dict WHERE type_code = 'cpu')
AND EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'hardware_type_dict');

INSERT INTO hardware_type_dict (type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time)
SELECT 'memory', '内存', '系统内存', 'compute', 2, 1, 'system', NOW()
WHERE NOT EXISTS (SELECT 1 FROM hardware_type_dict WHERE type_code = 'memory')
AND EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'hardware_type_dict');

INSERT INTO hardware_type_dict (type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time)
SELECT 'storage', '存储', '硬盘存储设备', 'storage', 3, 1, 'system', NOW()
WHERE NOT EXISTS (SELECT 1 FROM hardware_type_dict WHERE type_code = 'storage')
AND EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'hardware_type_dict');

INSERT INTO hardware_type_dict (type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time)
SELECT 'fan', '风扇', '散热风扇', 'cooling', 4, 1, 'system', NOW()
WHERE NOT EXISTS (SELECT 1 FROM hardware_type_dict WHERE type_code = 'fan')
AND EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'hardware_type_dict');

INSERT INTO hardware_type_dict (type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time)
SELECT 'power', '电源', '电源供应器', 'power', 5, 1, 'system', NOW()
WHERE NOT EXISTS (SELECT 1 FROM hardware_type_dict WHERE type_code = 'power')
AND EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'hardware_type_dict');

-- 查询验证数据
SELECT '--- business_hardware_urgency_rules 规则数据 ---' as info;
SELECT business_type, hardware_type, urgency_level, description
FROM business_hardware_urgency_rules 
ORDER BY urgency_level, business_type, hardware_type;

SELECT '--- 策略统计 ---' as info;
SELECT urgency_level, COUNT(*) as count
FROM business_hardware_urgency_rules 
WHERE is_active = 1
GROUP BY urgency_level; 