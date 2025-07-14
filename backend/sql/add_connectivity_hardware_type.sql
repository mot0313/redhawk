-- 在hardware_type_dict表中添加connectivity硬件类型
-- 用于支持业务IP连通性检查的硬件类型定义

INSERT INTO hardware_type_dict (type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES
('connectivity', '宕机', '设备业务IP连通性检查', '网络', 100, 1, 'system', NOW(), 'system', NOW());
 
-- 验证插入结果
-- SELECT * FROM hardware_type_dict WHERE type_code = 'connectivity'; 