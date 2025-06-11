-- ===========================
-- 业务类型与硬件类型联动查询演示 (PostgreSQL)
-- 说明: 演示如何根据设备业务类型和告警组件类型自动确定紧急度
-- ===========================

-- ----------------------------
-- 1、基础联动查询：根据设备ID和组件类型获取紧急度
-- ----------------------------
-- 查询逻辑：设备信息 -> 业务类型 + 组件类型 -> 紧急度规则 -> 紧急程度
SELECT 
    d.device_id,
    d.device_name,
    d.business_type,
    bt.type_name as business_type_name,
    'CPU' as component_type,  -- 假设是CPU告警
    ht.type_name as component_type_name,
    COALESCE(r.urgency_level, 'scheduled') as urgency_level,
    CASE 
        WHEN r.rule_id IS NOT NULL THEN '匹配到规则'
        ELSE '未匹配规则，默认择期'
    END as match_status,
    r.description as rule_description,
    r.rule_id
FROM device_info d
LEFT JOIN business_hardware_urgency_rules r ON (
    d.business_type = r.business_type 
    AND r.hardware_type = 'CPU'
    AND r.is_active = 1
)
LEFT JOIN business_type_dict bt ON d.business_type = bt.type_code
LEFT JOIN hardware_type_dict ht ON r.hardware_type = ht.type_code
WHERE d.device_id = 1000;  -- 替换为实际设备ID

-- ----------------------------
-- 2、告警表联动查询：根据告警ID获取紧急度
-- ----------------------------
-- 查询逻辑：告警信息 -> 设备信息 -> 业务类型 + 组件类型 -> 紧急度规则 -> 紧急程度
SELECT 
    a.alert_id,
    a.device_id,
    d.device_name,
    d.business_type,
    bt.type_name as business_type_name,
    a.component_type,
    ht.type_name as component_type_name,
    a.alert_message,
    COALESCE(r.urgency_level, 'scheduled') as urgency_level,
    CASE 
        WHEN r.rule_id IS NOT NULL THEN '匹配到规则'
        ELSE '未匹配规则，默认择期'
    END as match_status,
    r.description as rule_description,
    r.rule_id
FROM alert_info a
JOIN device_info d ON a.device_id = d.device_id
LEFT JOIN business_hardware_urgency_rules r ON (
    d.business_type = r.business_type 
    AND UPPER(a.component_type) = r.hardware_type
    AND r.is_active = 1
)
LEFT JOIN business_type_dict bt ON d.business_type = bt.type_code
LEFT JOIN hardware_type_dict ht ON r.hardware_type = ht.type_code
WHERE a.alert_status = 'active'
ORDER BY 
    CASE WHEN r.urgency_level = 'urgent' THEN 1 ELSE 2 END,  -- 紧急告警优先
    a.first_occurrence DESC;

-- ----------------------------
-- 3、设备紧急度统计查询
-- ----------------------------
-- 统计指定设备的紧急告警和择期告警数量
SELECT 
    d.device_id,
    d.device_name,
    d.business_type,
    bt.type_name as business_type_name,
    COUNT(*) as total_alerts,
    COUNT(CASE WHEN COALESCE(r.urgency_level, 'scheduled') = 'urgent' THEN 1 END) as urgent_count,
    COUNT(CASE WHEN COALESCE(r.urgency_level, 'scheduled') = 'scheduled' THEN 1 END) as scheduled_count,
    -- 紧急告警详情
    STRING_AGG(
        CASE WHEN COALESCE(r.urgency_level, 'scheduled') = 'urgent' 
        THEN a.component_type || '(' || a.alert_id || ')' 
        END, ', '
    ) as urgent_components,
    -- 择期告警详情
    STRING_AGG(
        CASE WHEN COALESCE(r.urgency_level, 'scheduled') = 'scheduled' 
        THEN a.component_type || '(' || a.alert_id || ')' 
        END, ', '
    ) as scheduled_components
FROM device_info d
JOIN alert_info a ON d.device_id = a.device_id
LEFT JOIN business_hardware_urgency_rules r ON (
    d.business_type = r.business_type 
    AND UPPER(a.component_type) = r.hardware_type
    AND r.is_active = 1
)
LEFT JOIN business_type_dict bt ON d.business_type = bt.type_code
WHERE a.alert_status = 'active'
  AND d.device_id = 1000  -- 替换为实际设备ID
GROUP BY d.device_id, d.device_name, d.business_type, bt.type_name;

-- ----------------------------
-- 4、全局紧急度分布统计
-- ----------------------------
-- 统计所有活跃告警的紧急度分布
SELECT 
    d.business_type,
    a.component_type,
    COALESCE(r.urgency_level, 'scheduled') as urgency_level,
    COUNT(*) as alert_count,
    COUNT(DISTINCT d.device_id) as affected_devices
FROM alert_info a
JOIN device_info d ON a.device_id = d.device_id
LEFT JOIN business_hardware_urgency_rules r ON (
    d.business_type = r.business_type 
    AND a.component_type = r.hardware_type
    AND r.is_active = 1
)
WHERE a.alert_status = 'active'
GROUP BY d.business_type, a.component_type, COALESCE(r.urgency_level, 'scheduled')
ORDER BY 
    CASE WHEN COALESCE(r.urgency_level, 'scheduled') = 'urgent' THEN 1 ELSE 2 END,
    alert_count DESC;

-- ----------------------------
-- 5、规则覆盖率分析
-- ----------------------------
-- 分析哪些业务类型+硬件类型组合没有配置规则
SELECT 
    d.business_type,
    a.component_type,
    COUNT(*) as alert_count,
    COUNT(DISTINCT d.device_id) as affected_devices,
    CASE 
        WHEN r.rule_id IS NOT NULL THEN '已配置规则'
        ELSE '未配置规则'
    END as rule_status
FROM alert_info a
JOIN device_info d ON a.device_id = d.device_id
LEFT JOIN business_hardware_urgency_rules r ON (
    d.business_type = r.business_type 
    AND a.component_type = r.hardware_type
    AND r.is_active = 1
)
WHERE a.alert_status = 'active'
GROUP BY d.business_type, a.component_type, r.rule_id
HAVING COUNT(*) > 0
ORDER BY 
    CASE WHEN r.rule_id IS NULL THEN 1 ELSE 2 END,  -- 未配置规则的优先显示
    alert_count DESC;

-- ----------------------------
-- 6、建议新增规则的查询
-- ----------------------------
-- 找出告警数量较多但未配置规则的业务类型+硬件类型组合
SELECT 
    d.business_type,
    a.component_type,
    COUNT(*) as alert_count,
    COUNT(DISTINCT d.device_id) as affected_devices,
    '建议配置为紧急' as suggested_urgency,
    '告警数量较多，建议配置规则' as reason
FROM alert_info a
JOIN device_info d ON a.device_id = d.device_id
LEFT JOIN business_hardware_urgency_rules r ON (
    d.business_type = r.business_type 
    AND a.component_type = r.hardware_type
    AND r.is_active = 1
)
WHERE a.alert_status = 'active'
  AND r.rule_id IS NULL  -- 未配置规则
GROUP BY d.business_type, a.component_type
HAVING COUNT(*) >= 3  -- 告警数量阈值
ORDER BY alert_count DESC, affected_devices DESC; 