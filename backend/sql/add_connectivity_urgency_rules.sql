-- 添加connectivity组件类型的紧急度规则
-- 用于配置不同业务类型的设备宕机(业务IP不可达)时的紧急程度

-- 示例规则：根据实际业务需求调整business_type和urgency_level
-- 注意：hardware_type使用小写'connectivity'以匹配component_type
INSERT INTO business_hardware_urgency_rules (business_type, hardware_type, urgency_level, description, is_active, create_by, create_time, update_by, update_time) VALUES
('生产系统', 'connectivity', 'urgent', '生产系统宕机为紧急', 1, 'system', NOW(), 'system', NOW()),
('测试系统', 'connectivity', 'scheduled', '测试系统宕机为择期', 1, 'system', NOW(), 'system', NOW()),
('开发系统', 'connectivity', 'scheduled', '开发系统宕机为择期', 1, 'system', NOW(), 'system', NOW()),
('核心业务', 'connectivity', 'urgent', '核心业务系统宕机为紧急', 1, 'system', NOW(), 'system', NOW()),
('辅助系统', 'connectivity', 'scheduled', '辅助系统宕机为择期', 1, 'system', NOW(), 'system', NOW());

-- 查询现有的business_type，便于配置
-- SELECT DISTINCT business_type FROM device_info WHERE business_type IS NOT NULL ORDER BY business_type;

-- 验证插入的规则
-- SELECT * FROM business_hardware_urgency_rules WHERE hardware_type = 'connectivity' ORDER BY business_type; 