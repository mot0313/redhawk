-- 🔧 修复缺失的缓存列表菜单
-- 添加缓存列表功能，区别于缓存监控

BEGIN;

-- ==========================================
-- 第一步：检查当前缓存相关菜单
-- ==========================================

SELECT '=== 当前缓存相关菜单 ===' as info;
SELECT 
    m.menu_id,
    m.menu_name,
    m.order_num,
    m.path,
    m.component,
    m.perms,
    CASE WHEN rm.role_id IS NOT NULL THEN '✅ 已分配' ELSE '❌ 未分配' END as common_user_access
FROM sys_menu m
LEFT JOIN sys_role_menu rm ON m.menu_id = rm.menu_id AND rm.role_id = 2
WHERE m.menu_name LIKE '%缓存%' OR m.path LIKE '%cache%'
ORDER BY m.menu_id;

-- ==========================================
-- 第二步：添加缺失的缓存列表菜单
-- ==========================================

-- 添加缓存列表菜单
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
) VALUES 
(114, '缓存列表', 2, 6, 'cache-list', 'monitor/cache/list', null, '',
 1, 0, 'C', '0', '0', 'monitor:cache:manage', 'redis-list',
 'admin', current_timestamp, 'admin', current_timestamp, 'Redis缓存键值管理')
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
-- 第三步：为普通用户分配缓存列表权限
-- ==========================================

-- 为普通用户分配缓存列表权限
INSERT INTO sys_role_menu (role_id, menu_id) VALUES 
(2, 114) -- 缓存列表
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

-- 检查缓存相关菜单
SELECT '=== 缓存功能菜单对比 ===' as info;
SELECT 
    m.menu_name,
    m.path,
    m.component,
    m.perms,
    '功能说明' as description
FROM sys_menu m
WHERE m.menu_name LIKE '%缓存%'
ORDER BY m.menu_id;

SELECT '
🎉 缓存列表菜单修复完成！

✅ 缓存功能区分：
   - 缓存监控 (113) - monitor/cache/index
     * 功能：显示Redis基本信息、连接状态、内存使用等
     * 路径：/monitor/cache
     * 权限：monitor:cache:list
   
   - 缓存列表 (114) - monitor/cache/list (新增)
     * 功能：显示缓存键值列表，可查看、删除缓存内容
     * 路径：/monitor/cache-list  
     * 权限：monitor:cache:manage

✅ 完整的系统监控菜单：
   1. 在线用户 (/monitor/online)
   2. 定时任务 (/monitor/job)
   3. 数据监控 (/monitor/druid)
   4. 服务监控 (/monitor/server)
   5. 缓存监控 (/monitor/cache)
   6. 缓存列表 (/monitor/cache-list) - 新增

✅ 普通用户权限：
   - 已分配缓存监控和缓存列表访问权限
   - 可以查看Redis状态和管理缓存内容

✅ 前端组件：
   - monitor/cache/index.vue (缓存监控)
   - monitor/cache/list.vue (缓存列表)

📋 访问路径：
   - /monitor/cache - 缓存监控(Redis状态信息)
   - /monitor/cache-list - 缓存列表(键值管理)

🚀 修复完成，请刷新页面查看效果！
' as summary;
