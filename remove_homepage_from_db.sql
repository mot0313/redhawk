-- 完全移除数据库中的首页配置SQL脚本
-- 因为首页路由在constantRoutes中配置，不需要数据库中的首页菜单

-- 1. 删除所有首页相关的菜单权限
DELETE FROM sys_role_menu WHERE menu_id IN (10, 3000, 3001, 3002, 3003, 3004);

-- 2. 删除所有首页相关的菜单
DELETE FROM sys_menu WHERE menu_id IN (10, 3000, 3001, 3002, 3003, 3004);

-- 3. 只保留dashboard权限菜单（这些是API调用需要的权限）
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, query, route_name, 
    is_frame, is_cache, menu_type, visible, status, perms, icon, 
    create_by, create_time, update_by, update_time, remark
) VALUES 
(3000, '首页概览权限', 0, 1, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:dashboard:overview', '#', 'admin', current_timestamp, 'admin', current_timestamp, '首页概览数据权限'),
(3001, '告警数据权限', 0, 2, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:dashboard:alert', '#', 'admin', current_timestamp, 'admin', current_timestamp, '告警相关数据权限'),
(3002, '设备健康权限', 0, 3, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:dashboard:device', '#', 'admin', current_timestamp, 'admin', current_timestamp, '设备健康数据权限'),
(3003, '完整首页权限', 0, 4, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:dashboard:view', '#', 'admin', current_timestamp, 'admin', current_timestamp, '完整首页数据权限'),
(3004, '系统指标权限', 0, 5, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:dashboard:metrics', '#', 'admin', current_timestamp, 'admin', current_timestamp, '系统健康指标权限');

-- 4. 为普通角色分配dashboard权限（不包含首页菜单）
INSERT INTO sys_role_menu (role_id, menu_id) VALUES 
(2, 3000), -- 普通角色 - 首页概览权限
(2, 3001), -- 普通角色 - 告警数据权限
(2, 3002), -- 普通角色 - 设备健康权限
(2, 3003), -- 普通角色 - 完整首页权限
(2, 3004); -- 普通角色 - 系统指标权限

-- 5. 验证结果
SELECT '移除后的首页相关菜单' as description;
SELECT menu_id, menu_name, parent_id, path, component, perms, menu_type, visible, status, order_num
FROM sys_menu 
WHERE menu_name LIKE '%首页%' OR path LIKE '%index%' OR path LIKE '%dashboard%'
ORDER BY menu_id;

SELECT '普通角色的dashboard权限' as description;
SELECT rm.role_id, r.role_name, rm.menu_id, m.menu_name, m.path, m.perms, m.menu_type, m.visible
FROM sys_role_menu rm 
JOIN sys_role r ON rm.role_id = r.role_id 
JOIN sys_menu m ON rm.menu_id = m.menu_id 
WHERE r.role_key = 'common' AND m.menu_id BETWEEN 3000 AND 3010
ORDER BY m.menu_id;

-- 说明：
-- 1. 完全移除了数据库中的首页菜单配置
-- 2. 只保留了dashboard API调用需要的权限
-- 3. 首页路由由前端constantRoutes配置，不需要数据库菜单
-- 4. 普通用户现在有dashboard API的权限，可以正常访问首页
-- 5. 执行后需要重启应用或清除缓存

