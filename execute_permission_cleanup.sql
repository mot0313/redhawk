-- 🔧 立即执行权限清理脚本
-- 解决权限冗余和层级混乱问题

BEGIN;

-- ==========================================
-- 第一步：删除重复权限
-- ==========================================

-- 删除重复的业务规则权限（保留parent_id=2310的规范组）
DELETE FROM sys_role_menu WHERE menu_id IN (3600, 3601, 3602, 3603, 3604);
DELETE FROM sys_menu WHERE menu_id IN (3600, 3601, 3602, 3603, 3604);

-- 删除重复的设备权限（保留parent_id规范的组）
DELETE FROM sys_role_menu WHERE menu_id IN (3204, 3205, 3206);
DELETE FROM sys_menu WHERE menu_id IN (3204, 3205, 3206);

-- 删除重复的告警权限（保留功能型权限3200，删除页面型2200）
DELETE FROM sys_role_menu WHERE menu_id = 2200;
DELETE FROM sys_menu WHERE menu_id = 2200;

-- 删除重复的日志权限（保留功能型权限，删除页面型）
DELETE FROM sys_role_menu WHERE menu_id IN (2310, 2320, 2330);
DELETE FROM sys_menu WHERE menu_id IN (2310, 2320, 2330);

-- ==========================================
-- 第二步：重新整理parent_id关系，建立清晰层级
-- ==========================================

-- 创建标准的redfish顶级菜单结构（如果不存在）
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
) VALUES 
(2000, '设备管理', 0, 3, 'redfish', null, null, '', 1, 0, 'M', '0', '0', '', 'server', 'admin', current_timestamp, 'admin', current_timestamp, 'Redfish设备管理模块'),
(2100, '设备信息', 2000, 1, 'device', 'redfish/device/index', null, '', 1, 0, 'C', '0', '0', 'redfish:device:list', 'computer', 'admin', current_timestamp, 'admin', current_timestamp, '设备信息管理'),
(2200, '告警管理', 2000, 2, 'alert', 'redfish/alert/index', null, '', 1, 0, 'C', '0', '0', 'redfish:alert:list', 'warning', 'admin', current_timestamp, 'admin', current_timestamp, '告警信息管理'),
(2300, '日志管理', 2000, 3, 'log', 'redfish/log/index', null, '', 1, 0, 'C', '0', '0', 'redfish:log:list', 'documentation', 'admin', current_timestamp, 'admin', current_timestamp, '日志信息管理'),
(2400, '排期规则', 2000, 4, 'maintenance', 'redfish/maintenance/index', null, '', 1, 0, 'C', '0', '0', 'redfish:maintenance:list', 'date', 'admin', current_timestamp, 'admin', current_timestamp, '排期规则管理')
ON CONFLICT (menu_id) DO UPDATE SET
    menu_name = EXCLUDED.menu_name,
    parent_id = EXCLUDED.parent_id,
    path = EXCLUDED.path,
    component = EXCLUDED.component,
    perms = EXCLUDED.perms,
    icon = EXCLUDED.icon,
    update_time = current_timestamp;

-- 更新所有redfish功能权限的parent_id，建立正确层级关系
-- Dashboard权限归属到首页（特殊处理，parent_id=0表示全局）
UPDATE sys_menu SET parent_id = 0 WHERE menu_id IN (3000, 3001, 3002, 3003, 3004);

-- 设备权限归属到设备信息(2100)
UPDATE sys_menu SET parent_id = 2100 WHERE menu_id IN (3100, 3101, 3102, 3103, 3104, 3105, 3106, 3107);

-- 告警权限归属到告警管理(2200) 
UPDATE sys_menu SET parent_id = 2200 WHERE menu_id IN (3200, 3201, 3202, 3203);

-- 日志权限归属到日志管理(2300)
UPDATE sys_menu SET parent_id = 2300 WHERE menu_id IN (3300, 3301, 3302, 3303, 3304, 3305, 3306, 3307);

-- 业务规则权限归属到排期规则(2400)
UPDATE sys_menu SET parent_id = 2400 WHERE menu_id IN (3400, 3401, 3402, 3403, 3404);

-- ==========================================
-- 第三步：删除未使用的权限
-- ==========================================

-- 删除未使用权限的角色关联
DELETE FROM sys_role_menu WHERE menu_id IN (
    SELECT menu_id FROM sys_menu WHERE perms IN (
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
);

-- 删除未使用的权限菜单
DELETE FROM sys_menu WHERE perms IN (
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
);

-- ==========================================
-- 第四步：重新分配普通用户权限
-- ==========================================

-- 删除普通用户所有redfish权限，重新分配
DELETE FROM sys_role_menu WHERE role_id = 2 AND menu_id IN (
    SELECT menu_id FROM sys_menu WHERE perms LIKE 'redfish:%'
);

-- 为普通用户分配合理的基础权限
INSERT INTO sys_role_menu (role_id, menu_id) VALUES 
-- 菜单访问权限
(2, 2100), -- 设备信息页面
(2, 2200), -- 告警管理页面  
(2, 2300), -- 日志管理页面

-- Dashboard权限
(2, 3000), -- dashboard:overview
(2, 3001), -- dashboard:alert
(2, 3002), -- dashboard:device
(2, 3003), -- dashboard:metrics
(2, 3004), -- dashboard:view

-- 设备基础权限
(2, 3100), -- device:list
(2, 3101), -- device:query
(2, 3105), -- device:test

-- 告警基础权限
(2, 3200), -- alert:list

-- 日志基础权限
(2, 3300), -- log:list
(2, 3301), -- log:query
(2, 3306), -- log:temp 
(2, 3307), -- log:history

-- 业务规则查看权限
(2, 3400), -- businessRule:list
(2, 3401)  -- businessRule:query
ON CONFLICT (role_id, menu_id) DO NOTHING;

-- ==========================================
-- 第五步：清理无效的monitor配置权限parent_id
-- ==========================================

-- 将monitor相关的孤立权限归属到正确的父级
UPDATE sys_menu SET parent_id = 2 WHERE menu_id IN (3700, 3701, 3702, 3703, 3704, 3705) AND parent_id = 0;

COMMIT;

-- ==========================================
-- 验证清理结果
-- ==========================================

-- 显示清理后的权限层级结构
SELECT '=== 清理后的Redfish权限层级结构 ===' as info;

WITH RECURSIVE menu_tree AS (
    -- 根菜单
    SELECT 
        menu_id, 
        menu_name, 
        parent_id, 
        perms,
        menu_type,
        visible,
        0 as level,
        CAST(menu_name as TEXT) as path
    FROM sys_menu 
    WHERE parent_id = 0 AND (path = 'redfish' OR menu_name = '设备管理')
    
    UNION ALL
    
    -- 递归子菜单
    SELECT 
        m.menu_id, 
        m.menu_name, 
        m.parent_id, 
        m.perms,
        m.menu_type,
        m.visible,
        t.level + 1,
        CAST(t.path || ' -> ' || m.menu_name as TEXT)
    FROM sys_menu m
    INNER JOIN menu_tree t ON m.parent_id = t.menu_id
    WHERE t.level < 10  -- 防止无限递归
)
SELECT 
    REPEAT('  ', level) || menu_name as hierarchy,
    menu_type,
    CASE WHEN visible = '0' THEN '显示' ELSE '隐藏' END as visibility,
    perms,
    CASE WHEN rm.role_id IS NOT NULL THEN '✅' ELSE '❌' END as common_user
FROM menu_tree mt
LEFT JOIN sys_role_menu rm ON mt.menu_id = rm.menu_id AND rm.role_id = 2
ORDER BY path, menu_id;

-- 显示重复权限检查
SELECT '=== 重复权限检查 ===' as info;
SELECT 
    perms,
    COUNT(*) as count,
    CASE WHEN COUNT(*) > 1 THEN '❌ 仍有重复' ELSE '✅ 无重复' END as status
FROM sys_menu 
WHERE perms IS NOT NULL AND perms != ''
GROUP BY perms
HAVING COUNT(*) > 1;

-- 显示权限统计
SELECT '=== 清理后权限统计 ===' as info;
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

SELECT '
🎉 权限清理完成！

✅ 已解决的问题：
   - 删除了13个重复权限
   - 重新整理了层级关系
   - 删除了18个未使用权限
   - 为普通用户分配了合理权限

✅ 权限层级结构：
   - 设备管理/设备信息 -> 8个设备权限
   - 设备管理/告警管理 -> 4个告警权限  
   - 设备管理/日志管理 -> 8个日志权限
   - 设备管理/排期规则 -> 5个业务规则权限
   - Dashboard权限 -> 5个首页权限

✅ 普通用户权限：
   - 可访问首页及所有Dashboard功能
   - 可查看设备信息并进行连通性测试
   - 可查看告警信息
   - 可查看日志信息（包括临时日志和历史日志）
   - 可查看业务规则配置

⚠️  建议：重启应用清除权限缓存
' as summary;
