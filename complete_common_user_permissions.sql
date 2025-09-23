-- 完善普通用户redfish权限配置SQL脚本
-- 目标：让普通用户可以完整访问首页和redfish相关功能

-- 1. 为普通角色添加缺少的日志信息菜单权限
INSERT INTO sys_role_menu (role_id, menu_id) VALUES (2, 2005);

-- 2. 创建并分配设备相关的详细操作权限
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, query, route_name, 
    is_frame, is_cache, menu_type, visible, status, perms, icon, 
    create_by, create_time, update_by, update_time, remark
) VALUES 
-- 设备详细操作权限
(3010, '设备查询权限', 0, 10, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:device:query', '#', 'admin', current_timestamp, 'admin', current_timestamp, '设备查询权限'),
(3011, '设备连通性测试权限', 0, 11, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:device:test', '#', 'admin', current_timestamp, 'admin', current_timestamp, '设备连通性测试权限'),
(3012, '设备统计权限', 0, 12, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:device:statistics', '#', 'admin', current_timestamp, 'admin', current_timestamp, '设备统计权限'),

-- 告警详细操作权限
(3020, '告警查询权限', 0, 20, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:alert:query', '#', 'admin', current_timestamp, 'admin', current_timestamp, '告警查询权限'),
(3021, '告警详情权限', 0, 21, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:alert:detail', '#', 'admin', current_timestamp, 'admin', current_timestamp, '告警详情权限'),

-- 排期规则详细操作权限
(3030, '排期规则查询权限', 0, 30, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:maintenance:query', '#', 'admin', current_timestamp, 'admin', current_timestamp, '排期规则查询权限');

-- 3. 为普通角色分配这些新的权限
INSERT INTO sys_role_menu (role_id, menu_id) VALUES 
(2, 3010), -- 设备查询权限
(2, 3011), -- 设备连通性测试权限
(2, 3012), -- 设备统计权限
(2, 3020), -- 告警查询权限
(2, 3021), -- 告警详情权限
(2, 3030); -- 排期规则查询权限

-- 4. 验证配置结果
SELECT '普通用户的完整redfish权限' as description;
SELECT rm.role_id, r.role_name, rm.menu_id, m.menu_name, m.perms, m.menu_type, m.visible
FROM sys_role_menu rm 
JOIN sys_role r ON rm.role_id = r.role_id 
JOIN sys_menu m ON rm.menu_id = m.menu_id 
WHERE r.role_key = 'common' 
AND (m.perms LIKE '%redfish%' OR m.menu_name LIKE '%首页%')
ORDER BY m.menu_id;

-- 5. 检查普通用户可访问的redfish菜单
SELECT '普通用户可访问的redfish菜单' as description;
SELECT rm.role_id, r.role_name, rm.menu_id, m.menu_name, m.path, m.component, m.menu_type, m.visible
FROM sys_role_menu rm 
JOIN sys_role r ON rm.role_id = r.role_id 
JOIN sys_menu m ON rm.menu_id = m.menu_id 
WHERE r.role_key = 'common' 
AND m.menu_type = 'C'
AND (m.path LIKE '%device%' OR m.path LIKE '%alert%' OR m.path LIKE '%log%' OR m.path LIKE '%maintenance%')
ORDER BY m.menu_id;

-- 说明：
-- 1. 添加了日志信息菜单权限，让普通用户可以访问日志管理功能
-- 2. 创建了设备、告警、排期规则的详细操作权限
-- 3. 普通用户现在拥有完整的redfish功能访问权限
-- 4. 所有权限菜单都设置为隐藏（visible=1），不影响前端菜单显示
-- 5. 执行后需要重启应用或清除缓存以确保配置生效
