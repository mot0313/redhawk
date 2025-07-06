-- 插入示例告警数据
-- 基于真实设备数据：device_id 1000, 1003, 1004

-- 插入紧急告警示例
INSERT INTO alert_info (
    device_id, component_type, component_name, 
    health_status, urgency_level, alert_status, first_occurrence, 
    last_occurrence, create_time, update_time
) VALUES 
-- 紧急告警 - CPU故障
(1000, 'cpu', 'CPU-1', 'critical', 'urgent', 'active', 
 NOW() - INTERVAL '2 hours', NOW() - INTERVAL '30 minutes', NOW(), NOW()),

-- 紧急告警 - 内存故障  
(1003, 'memory', 'DIMM-A1', 'critical', 'urgent', 'active',
 NOW() - INTERVAL '4 hours', NOW() - INTERVAL '1 hour', NOW(), NOW()),

-- 紧急告警 - 电源故障
(1004, 'power', 'PSU-1', 'critical', 'urgent', 'active',
 NOW() - INTERVAL '1 hour', NOW() - INTERVAL '15 minutes', NOW(), NOW()),

-- 择期告警 - 风扇警告
(1000, 'fan', 'Fan-1', 'warning', 'scheduled', 'active',
 NOW() - INTERVAL '1 day', NOW() - INTERVAL '2 hours', NOW(), NOW()),

-- 择期告警 - 温度警告
(1003, 'temperature', 'CPU-Temp', 'warning', 'scheduled', 'active',
 NOW() - INTERVAL '3 days', NOW() - INTERVAL '6 hours', NOW(), NOW()),

-- 择期告警 - 存储警告
(1004, 'storage', 'Disk-1', 'warning', 'scheduled', 'active',
 NOW() - INTERVAL '5 days', NOW() - INTERVAL '12 hours', NOW(), NOW()),

-- 择期告警 - 网络警告
(1000, 'network', 'NIC-1', 'warning', 'scheduled', 'active',
 NOW() - INTERVAL '2 days', NOW() - INTERVAL '8 hours', NOW(), NOW()),

-- 已解决的告警示例
(1003, 'memory', 'DIMM-B1', 'ok', 'urgent', 'resolved',
 NOW() - INTERVAL '1 week', NOW() - INTERVAL '2 days', NOW(), NOW()),

(1004, 'storage', 'Disk-2', 'ok', 'scheduled', 'resolved',
 NOW() - INTERVAL '10 days', NOW() - INTERVAL '3 days', NOW(), NOW()),

-- 更多紧急告警
(1000, 'cpu', 'CPU-2', 'critical', 'urgent', 'active',
 NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '5 minutes', NOW(), NOW()),

-- 更多择期告警
(1003, 'fan', 'Fan-2', 'warning', 'scheduled', 'active',
 NOW() - INTERVAL '6 days', NOW() - INTERVAL '1 day', NOW(), NOW()),

(1004, 'power', 'PSU-2', 'warning', 'scheduled', 'active',
 NOW() - INTERVAL '4 days', NOW() - INTERVAL '18 hours', NOW(), NOW());

-- 更新统计信息（PostgreSQL语法）
ANALYZE alert_info; 