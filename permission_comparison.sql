-- 📊 权限清理前后对比脚本
-- 在执行 complete_permission_cleanup.sql 前后分别运行此脚本，以对比清理效果

-- ==========================================
-- 当前权限统计概览
-- ==========================================
SELECT '=== 当前权限统计概览 ===' as info;

SELECT 
    CASE 
        WHEN perms LIKE 'redfish:%' THEN 'Redfish模块'
        WHEN perms LIKE 'system:%' THEN '系统管理'
        WHEN perms LIKE 'monitor:%' THEN '系统监控'
        WHEN perms LIKE 'tool:%' THEN '系统工具'
        ELSE '其他'
    END as module,
    COUNT(*) as permission_count
FROM sys_menu 
WHERE perms IS NOT NULL AND perms != ''
GROUP BY 
    CASE 
        WHEN perms LIKE 'redfish:%' THEN 'Redfish模块'
        WHEN perms LIKE 'system:%' THEN '系统管理'
        WHEN perms LIKE 'monitor:%' THEN '系统监控'
        WHEN perms LIKE 'tool:%' THEN '系统工具'
        ELSE '其他'
    END
ORDER BY module;

-- ==========================================
-- 详细权限列表
-- ==========================================
SELECT '=== 所有权限详细列表 ===' as info;

SELECT 
    perms,
    menu_name,
    menu_type,
    visible,
    status,
    CASE WHEN rm.role_id IS NOT NULL THEN '✅ 普通用户可用' ELSE '❌ 普通用户不可用' END as common_user_access
FROM sys_menu m
LEFT JOIN sys_role_menu rm ON m.menu_id = rm.menu_id AND rm.role_id = 2
WHERE perms IS NOT NULL AND perms != ''
ORDER BY perms;

-- ==========================================
-- 即将删除的权限列表
-- ==========================================
SELECT '=== 即将删除的权限 ===' as info;

SELECT 
    perms,
    menu_name,
    '🗑️ 原因：' || 
    CASE 
        WHEN perms IN ('redfish:maintenance:query', 'redfish:maintenance:add', 'redfish:maintenance:edit', 'redfish:maintenance:remove') 
            THEN '无对应后端controller实现'
        WHEN perms IN ('redfish:log:temp:view', 'redfish:log:temp:collect', 'redfish:log:temp:export', 'redfish:log:history:view') 
            THEN '功能已整合到主要接口中'
        WHEN perms = 'redfish:alert:query' 
            THEN '功能已整合在list接口中'
        WHEN perms IN ('monitor:druid:list', 'tool:build:list', 'tool:swagger:list') 
            THEN '功能已停用'
        WHEN perms IN ('monitor:online:query', 'monitor:online:batchLogout', 'monitor:operlog:query', 'monitor:logininfor:query') 
            THEN '功能已整合或未实现'
        ELSE '其他原因'
    END as reason
FROM sys_menu 
WHERE perms IN (
    'redfish:maintenance:query',
    'redfish:maintenance:add', 
    'redfish:maintenance:edit',
    'redfish:maintenance:remove',
    'redfish:log:temp:view',
    'redfish:log:temp:collect', 
    'redfish:log:temp:export',
    'redfish:log:history:view',
    'redfish:alert:query',
    'monitor:druid:list',
    'monitor:online:query',
    'monitor:online:batchLogout',
    'monitor:operlog:query',
    'monitor:logininfor:query',
    'tool:build:list',
    'tool:swagger:list'
)
ORDER BY perms;

-- ==========================================
-- 普通用户当前Redfish权限
-- ==========================================
SELECT '=== 普通用户当前Redfish权限 ===' as info;

SELECT 
    m.perms,
    m.menu_name,
    CASE WHEN rm.role_id IS NOT NULL THEN '✅ 当前已有' ELSE '❌ 当前没有' END as current_status
FROM sys_menu m
LEFT JOIN sys_role_menu rm ON m.menu_id = rm.menu_id AND rm.role_id = 2
WHERE m.perms LIKE 'redfish:%'
ORDER BY m.perms;

-- ==========================================
-- 角色权限分布统计
-- ==========================================
SELECT '=== 各角色权限数量统计 ===' as info;

SELECT 
    r.role_name,
    r.role_id,
    COUNT(rm.menu_id) as total_permissions,
    COUNT(CASE WHEN m.perms LIKE 'redfish:%' THEN 1 END) as redfish_permissions,
    COUNT(CASE WHEN m.perms LIKE 'system:%' THEN 1 END) as system_permissions,
    COUNT(CASE WHEN m.perms LIKE 'monitor:%' THEN 1 END) as monitor_permissions
FROM sys_role r
LEFT JOIN sys_role_menu rm ON r.role_id = rm.role_id
LEFT JOIN sys_menu m ON rm.menu_id = m.menu_id AND m.perms IS NOT NULL AND m.perms != ''
WHERE r.status = '0'
GROUP BY r.role_id, r.role_name
ORDER BY r.role_id;

-- ==========================================
-- 重复权限检查
-- ==========================================
SELECT '=== 重复权限检查 ===' as info;

SELECT 
    perms,
    COUNT(*) as duplicate_count,
    STRING_AGG(menu_id::text, ', ') as menu_ids
FROM sys_menu 
WHERE perms IS NOT NULL AND perms != ''
GROUP BY perms
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC, perms;

-- ==========================================
-- 总结信息
-- ==========================================
SELECT 
    '📊 权限清理前统计：
    
    ✅ 总权限数：' || (SELECT COUNT(*) FROM sys_menu WHERE perms IS NOT NULL AND perms != '') || '
    ❌ 将删除权限：' || (
        SELECT COUNT(*) FROM sys_menu WHERE perms IN (
            'redfish:maintenance:query', 'redfish:maintenance:add', 'redfish:maintenance:edit', 'redfish:maintenance:remove',
            'redfish:log:temp:view', 'redfish:log:temp:collect', 'redfish:log:temp:export', 'redfish:log:history:view',
            'redfish:alert:query', 'monitor:druid:list', 'monitor:online:query', 'monitor:online:batchLogout',
            'monitor:operlog:query', 'monitor:logininfor:query', 'tool:build:list', 'tool:swagger:list'
        )
    ) || '
    🔧 普通用户当前Redfish权限：' || (
        SELECT COUNT(*) FROM sys_role_menu rm 
        JOIN sys_menu m ON rm.menu_id = m.menu_id 
        WHERE rm.role_id = 2 AND m.perms LIKE 'redfish:%'
    ) || '
    
    📋 清理后预期效果：
    - 删除未使用权限，提升系统性能
    - 统一权限体系，便于管理维护  
    - 为普通用户分配合理的基础权限
    - 保持管理员权限完整性
    
    ⚠️  执行前请务必备份数据库！' as summary;
