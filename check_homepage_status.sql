-- 检查首页状态SQL脚本
-- 用于诊断首页显示问题

-- 1. 检查所有首页相关的菜单
SELECT '所有首页相关菜单' as description;
SELECT menu_id, menu_name, parent_id, path, component, perms, menu_type, visible, status, order_num
FROM sys_menu 
WHERE menu_name LIKE '%首页%' OR path LIKE '%index%' OR path LIKE '%dashboard%'
ORDER BY menu_id;

-- 2. 检查可见的顶级菜单
SELECT '可见的顶级菜单' as description;
SELECT menu_id, menu_name, parent_id, path, component, perms, menu_type, visible, status, order_num
FROM sys_menu 
WHERE visible = '0' AND menu_type = 'C' AND parent_id = 0
ORDER BY order_num, menu_id;

-- 3. 检查普通角色的菜单权限
SELECT '普通角色的菜单权限' as description;
SELECT rm.role_id, r.role_name, rm.menu_id, m.menu_name, m.path, m.component, m.perms, m.menu_type, m.visible, m.order_num
FROM sys_role_menu rm 
JOIN sys_role r ON rm.role_id = r.role_id 
JOIN sys_menu m ON rm.menu_id = m.menu_id 
WHERE r.role_key = 'common' AND m.visible = '0' AND m.menu_type = 'C'
ORDER BY m.order_num, m.menu_id;

-- 4. 检查是否有重复的菜单名称
SELECT '重复的菜单名称' as description;
SELECT menu_name, COUNT(*) as count
FROM sys_menu 
WHERE visible = '0' AND menu_type = 'C'
GROUP BY menu_name
HAVING COUNT(*) > 1;

