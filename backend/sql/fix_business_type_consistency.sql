-- ===========================
-- 业务类型数据一致性检查和修正脚本 (PostgreSQL)
-- 说明: 修正business_hardware_urgency_rules表与字典表的关联关系
-- ===========================

-- ----------------------------
-- 1、数据一致性检查
-- ----------------------------

-- 检查business_hardware_urgency_rules中未在business_type_dict中的业务类型
SELECT '=== 检查业务类型一致性 ===' as info;
SELECT 
    r.business_type,
    COUNT(*) as rule_count,
    '未在字典表中' as status
FROM business_hardware_urgency_rules r
LEFT JOIN business_type_dict bt ON r.business_type = bt.type_code
WHERE bt.type_code IS NULL
GROUP BY r.business_type;

-- 检查hardware_type一致性（大小写问题）
SELECT '=== 检查硬件类型一致性 ===' as info;
SELECT 
    r.hardware_type,
    COUNT(*) as rule_count,
    CASE 
        WHEN ht.type_code IS NOT NULL THEN '完全匹配'
        WHEN EXISTS (SELECT 1 FROM hardware_type_dict WHERE UPPER(type_code) = UPPER(r.hardware_type)) THEN '大小写不匹配'
        ELSE '未在字典表中'
    END as status
FROM business_hardware_urgency_rules r
LEFT JOIN hardware_type_dict ht ON r.hardware_type = ht.type_code
GROUP BY r.hardware_type, ht.type_code
ORDER BY status, r.hardware_type;

-- ----------------------------
-- 2、修正business_type_dict表 - 添加缺失的业务类型
-- ----------------------------

-- 添加DB作为通用数据库类型
INSERT INTO business_type_dict (type_code, type_name, type_description, sort_order, is_active, create_by, create_time)
SELECT 'DB', '数据库服务', '通用数据库服务（包含各类数据库）', 15, 1, 'system', current_timestamp
WHERE NOT EXISTS (SELECT 1 FROM business_type_dict WHERE type_code = 'DB');

-- 检查并添加其他可能缺失的业务类型
INSERT INTO business_type_dict (type_code, type_name, type_description, sort_order, is_active, create_by, create_time)
SELECT 
    r.business_type,
    r.business_type || '服务',
    '自动添加的业务类型 - ' || r.business_type,
    90,
    1,
    'system',
    current_timestamp
FROM (
    SELECT DISTINCT r.business_type
    FROM business_hardware_urgency_rules r
    LEFT JOIN business_type_dict bt ON r.business_type = bt.type_code
    WHERE bt.type_code IS NULL
) r
WHERE r.business_type IS NOT NULL;

-- ----------------------------
-- 3、修正hardware_type大小写问题
-- ----------------------------

-- 更新business_hardware_urgency_rules中的hardware_type为大写
UPDATE business_hardware_urgency_rules 
SET 
    hardware_type = UPPER(hardware_type),
    update_time = current_timestamp,
    update_by = 'system'
WHERE hardware_type != UPPER(hardware_type);

-- 检查是否还有未匹配的硬件类型
INSERT INTO hardware_type_dict (type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time)
SELECT 
    UPPER(r.hardware_type),
    INITCAP(r.hardware_type),
    '自动添加的硬件类型 - ' || r.hardware_type,
    'other',
    80,
    1,
    'system',
    current_timestamp
FROM (
    SELECT DISTINCT r.hardware_type
    FROM business_hardware_urgency_rules r
    LEFT JOIN hardware_type_dict ht ON UPPER(r.hardware_type) = ht.type_code
    WHERE ht.type_code IS NULL
) r
WHERE r.hardware_type IS NOT NULL;

-- ----------------------------
-- 4、验证修正结果
-- ----------------------------

SELECT '=== 修正后的一致性检查 ===' as info;

-- 检查业务类型一致性
SELECT 
    '业务类型一致性' as check_type,
    COUNT(*) as total_rules,
    COUNT(bt.type_code) as matched_rules,
    COUNT(*) - COUNT(bt.type_code) as unmatched_rules
FROM business_hardware_urgency_rules r
LEFT JOIN business_type_dict bt ON r.business_type = bt.type_code;

-- 检查硬件类型一致性
SELECT 
    '硬件类型一致性' as check_type,
    COUNT(*) as total_rules,
    COUNT(ht.type_code) as matched_rules,
    COUNT(*) - COUNT(ht.type_code) as unmatched_rules
FROM business_hardware_urgency_rules r
LEFT JOIN hardware_type_dict ht ON r.hardware_type = ht.type_code;

-- 显示所有规则及其对应的字典信息
SELECT 
    r.rule_id,
    r.business_type,
    bt.type_name as business_type_name,
    r.hardware_type,
    ht.type_name as hardware_type_name,
    r.urgency_level,
    r.description
FROM business_hardware_urgency_rules r
LEFT JOIN business_type_dict bt ON r.business_type = bt.type_code
LEFT JOIN hardware_type_dict ht ON r.hardware_type = ht.type_code
WHERE r.is_active = 1
ORDER BY r.business_type, r.hardware_type;

-- ----------------------------
-- 5、创建数据一致性约束（可选）
-- ----------------------------

-- 为了确保未来数据一致性，可以考虑添加检查约束
-- 注意：这会在INSERT/UPDATE时检查数据是否在字典表中存在

-- 创建函数检查业务类型是否存在
CREATE OR REPLACE FUNCTION check_business_type_exists(business_type_code varchar)
RETURNS boolean AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM business_type_dict 
        WHERE type_code = business_type_code AND is_active = 1
    );
END;
$$ LANGUAGE plpgsql;

-- 创建函数检查硬件类型是否存在
CREATE OR REPLACE FUNCTION check_hardware_type_exists(hardware_type_code varchar)
RETURNS boolean AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM hardware_type_dict 
        WHERE type_code = hardware_type_code AND is_active = 1
    );
END;
$$ LANGUAGE plpgsql;

-- 添加检查约束（可选，谨慎使用）
-- ALTER TABLE business_hardware_urgency_rules 
-- ADD CONSTRAINT chk_business_type_exists 
-- CHECK (check_business_type_exists(business_type));

-- ALTER TABLE business_hardware_urgency_rules 
-- ADD CONSTRAINT chk_hardware_type_exists 
-- CHECK (check_hardware_type_exists(hardware_type));

SELECT '=== 数据一致性修正完成 ===' as result; 