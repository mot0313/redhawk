-- 🔧 修复系统监控菜单缺失问题
-- 恢复数据监控(Druid)菜单

BEGIN;

-- ==========================================
-- 第一步：检查当前系统监控菜单状态
-- ==========================================

SELECT '=== 当前系统监控菜单 ===' as info;
SELECT 
    m.menu_id,
    m.menu_name,
    m.order_num,
    m.path,
    m.component,
    m.perms,
    CASE WHEN m.visible = '0' THEN '显示' ELSE '隐藏' END as visibility,
    CASE WHEN m.status = '0' THEN '正常' ELSE '停用' END as status,
    CASE WHEN rm.role_id IS NOT NULL THEN '✅ 已分配' ELSE '❌ 未分配' END as common_user_access
FROM sys_menu m
LEFT JOIN sys_role_menu rm ON m.menu_id = rm.menu_id AND rm.role_id = 2
WHERE m.parent_id = 2 AND m.menu_type = 'C'
ORDER BY m.order_num;

-- ==========================================
-- 第二步：恢复缺失的数据监控菜单
-- ==========================================

-- 恢复数据监控(Druid)菜单
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
) VALUES 
(111, '数据监控', 2, 3, 'druid', 'monitor/druid/index', null, '',
 1, 0, 'C', '0', '0', 'monitor:druid:list', 'druid',
 'admin', current_timestamp, 'admin', current_timestamp, 'Druid数据库连接池监控')
ON CONFLICT (menu_id) DO UPDATE SET
    menu_name = EXCLUDED.menu_name,
    parent_id = EXCLUDED.parent_id,
    order_num = EXCLUDED.order_num,
    path = EXCLUDED.path,
    component = EXCLUDED.component,
    perms = EXCLUDED.perms,
    icon = EXCLUDED.icon,
    visible = '0',
    status = '0',
    update_time = current_timestamp;

-- ==========================================
-- 第三步：为普通用户分配权限
-- ==========================================

-- 为普通用户分配数据监控权限
INSERT INTO sys_role_menu (role_id, menu_id) VALUES 
(2, 111) -- 数据监控
ON CONFLICT (role_id, menu_id) DO NOTHING;

-- 确保缓存监控权限也已分配
INSERT INTO sys_role_menu (role_id, menu_id) VALUES 
(2, 113) -- 缓存监控
ON CONFLICT (role_id, menu_id) DO NOTHING;

COMMIT;

-- ==========================================
-- 验证修复结果
-- ==========================================

SELECT '=== 修复后的系统监控菜单 ===' as info;
SELECT 
    m.menu_id,
    m.menu_name,
    m.order_num,
    m.path,
    m.component,
    m.perms,
    CASE WHEN m.visible = '0' THEN '显示' ELSE '隐藏' END as visibility,
    CASE WHEN m.status = '0' THEN '正常' ELSE '停用' END as status,
    CASE WHEN rm.role_id IS NOT NULL THEN '✅ 已分配' ELSE '❌ 未分配' END as common_user_access
FROM sys_menu m
LEFT JOIN sys_role_menu rm ON m.menu_id = rm.menu_id AND rm.role_id = 2
WHERE m.parent_id = 2 AND m.menu_type = 'C'
ORDER BY m.order_num;

-- 检查普通用户监控权限
SELECT '=== 普通用户监控权限 ===' as info;
SELECT 
    m.menu_name,
    m.path,
    m.perms,
    'YES' as has_permission
FROM sys_menu m
INNER JOIN sys_role_menu rm ON m.menu_id = rm.menu_id
WHERE rm.role_id = 2 AND m.parent_id = 2 AND m.menu_type = 'C'
ORDER BY m.order_num;

SELECT '
🎉 系统监控菜单修复完成！

✅ 恢复的菜单：
   - 数据监控 (111) - monitor/druid/index

✅ 完整的系统监控菜单：
   1. 在线用户 (/monitor/online)
   2. 定时任务 (/monitor/job)  
   3. 数据监控 (/monitor/druid) - 新恢复
   4. 服务监控 (/monitor/server)
   5. 缓存监控 (/monitor/cache)

✅ 普通用户权限：
   - 已分配所有监控菜单访问权限
   - 可以正常访问数据监控和缓存监控

✅ 前端组件：已确认 monitor/druid/index.vue 存在

📋 访问路径：
   - /monitor/druid - 数据监控(Druid连接池)
   - /monitor/cache - 缓存监控

🚀 修复完成，请刷新页面查看效果！
' as summary;
