-- 修复带外IP连通性告警问题
-- 解决为什么有时只显示部分离线设备告警的问题

-- 问题根源：
-- 1. 设备业务类型使用的是描述性文本，而不是标准代码
-- 2. 缺少oob_connectivity的紧急度规则

-- ===========================
-- 1. 修正设备业务类型
-- ===========================

-- 将描述性业务类型修正为标准代码
UPDATE device_info 
SET business_type = CASE 
    WHEN business_type = 'OB服务器（管理节点，三节点部署）' THEN 'OB-GMT-3N'
    WHEN business_type = 'OB服务器（数据节点，五节点部署）' THEN 'OB-DATA-5N'
    ELSE business_type
END
WHERE business_type IN (
    'OB服务器（管理节点，三节点部署）',
    'OB服务器（数据节点，五节点部署）'
);

-- 验证修正结果
SELECT device_id, hostname, business_type, oob_ip 
FROM device_info 
WHERE monitor_enabled = 1
ORDER BY device_id;

-- ===========================
-- 2. 添加带外连通性紧急度规则
-- ===========================

-- 为OB-GMT-3N业务类型添加oob_connectivity规则
INSERT INTO business_hardware_urgency_rules 
(business_type, hardware_type, urgency_level, description, create_by) 
VALUES 
('OB-GMT-3N', 'oob_connectivity', 'scheduled', 'OB管理节点带外IP连通性告警为择期', 'admin')
ON CONFLICT (business_type, hardware_type) 
DO UPDATE SET 
    urgency_level = EXCLUDED.urgency_level,
    description = EXCLUDED.description,
    update_time = CURRENT_TIMESTAMP;

-- 为OB-DATA-5N业务类型添加oob_connectivity规则
INSERT INTO business_hardware_urgency_rules 
(business_type, hardware_type, urgency_level, description, create_by) 
VALUES 
('OB-DATA-5N', 'oob_connectivity', 'scheduled', 'OB数据节点带外IP连通性告警为择期', 'admin')
ON CONFLICT (business_type, hardware_type) 
DO UPDATE SET 
    urgency_level = EXCLUDED.urgency_level,
    description = EXCLUDED.description,
    update_time = CURRENT_TIMESTAMP;

-- 为其他业务类型添加默认的oob_connectivity规则
INSERT INTO business_hardware_urgency_rules 
(business_type, hardware_type, urgency_level, description, create_by) 
SELECT 
    type_code,
    'oob_connectivity',
    'scheduled',
    type_name || '带外IP连通性告警为择期',
    'admin'
FROM business_type_dict 
WHERE type_code NOT IN (
    SELECT DISTINCT business_type 
    FROM business_hardware_urgency_rules 
    WHERE hardware_type = 'oob_connectivity'
)
AND is_active = 1
ON CONFLICT (business_type, hardware_type) 
DO NOTHING;

-- 验证添加的规则
SELECT business_type, hardware_type, urgency_level, description
FROM business_hardware_urgency_rules 
WHERE hardware_type = 'oob_connectivity'
AND is_active = 1
ORDER BY business_type;

-- ===========================
-- 3. 清理历史错误数据（可选）
-- ===========================

-- 可选：删除错误的connectivity规则（如果确认不需要）
-- DELETE FROM business_hardware_urgency_rules 
-- WHERE hardware_type = 'connectivity' 
-- AND business_type = 'OB-DATA-5N';

-- ===========================
-- 4. 验证修复结果
-- ===========================

-- 检查修复后的设备-规则匹配情况
SELECT 
    d.device_id,
    d.hostname,
    d.business_type,
    d.oob_ip,
    r.hardware_type,
    r.urgency_level
FROM device_info d
LEFT JOIN business_hardware_urgency_rules r 
    ON d.business_type = r.business_type 
    AND r.hardware_type = 'oob_connectivity'
    AND r.is_active = 1
WHERE d.monitor_enabled = 1
ORDER BY d.device_id;

-- 显示当前活跃的带外连通性告警
SELECT 
    a.device_id,
    d.hostname,
    d.business_type,
    a.component_type,
    a.component_name,
    a.health_status,
    a.urgency_level,
    a.alert_status,
    a.create_time
FROM alert_info a
JOIN device_info d ON a.device_id = d.device_id
WHERE a.component_type = 'oob_connectivity'
AND a.alert_status = 'active'
ORDER BY a.device_id;

-- ===========================
-- 5. 测试建议
-- ===========================

/*
修复后的测试步骤：
1. 运行此SQL脚本完成修复
2. 重新执行设备监控任务
3. 验证所有离线设备都生成了对应的告警
4. 检查告警的紧急度是否正确设置

预期结果：
- 设备1044应该生成带外IP连通性告警（business_type=OB-GMT-3N）
- 设备1045应该继续保持告警（business_type=OB-DATA-5N）
- 设备1046不应该有告警（在线状态）
*/

