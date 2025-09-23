-- 修正maintenance权限配置
-- 删除未使用的权限，保留实际需要的权限

-- 删除未使用的maintenance权限
DELETE FROM sys_role_menu WHERE menu_id IN (3500, 3501, 3502, 3503);
DELETE FROM sys_menu WHERE menu_id IN (3500, 3501, 3502, 3503);

-- 确保保留实际使用的权限
-- 1. redfish:maintenance:list (已存在于menu_id: 2400)
-- 2. redfish:alert:maintenance (告警维护功能)

-- 检查并确保告警维护权限存在
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
) VALUES (
    3303, '告警维护权限', 2200, 4, '', '', null, '',
    1, 0, 'F', '1', '0', 'redfish:alert:maintenance', '#',
    'admin', current_timestamp, 'admin', current_timestamp, '告警维护计划权限'
) ON CONFLICT (menu_id) DO NOTHING;

-- 为普通角色分配告警维护权限
INSERT INTO sys_role_menu (role_id, menu_id) VALUES (2, 3303)
ON CONFLICT (role_id, menu_id) DO NOTHING;

-- 验证修正后的maintenance相关权限
SELECT '=== 修正后的maintenance权限 ===' as info;
SELECT 
    m.menu_id,
    m.menu_name,
    m.path,
    m.perms,
    m.menu_type,
    CASE WHEN rm.role_id IS NOT NULL THEN '✅ 已分配给普通用户' ELSE '❌ 未分配' END as assignment_status
FROM sys_menu m
LEFT JOIN sys_role_menu rm ON m.menu_id = rm.menu_id AND rm.role_id = 2
WHERE m.perms LIKE '%maintenance%'
ORDER BY m.menu_id;

-- 说明
SELECT '修正说明：
1. ✅ 保留 redfish:maintenance:list - 对应排期规则菜单
2. ✅ 保留 redfish:alert:maintenance - 对应告警维护功能  
3. ❌ 删除未使用的 maintenance CRUD 权限
4. 建议：如需要完整的维护管理功能，应创建对应的后端controller
' as description;
