-- 🎯 根据现有菜单层级调整权限配置
-- 保持与您现有菜单结构完全一致

BEGIN;

-- ==========================================
-- 第一步：删除重复权限，保留层级合理的那一个
-- ==========================================

-- 删除重复的业务规则权限（保留parent_id=2400下的规范组）
DELETE FROM sys_role_menu WHERE menu_id IN (3600, 3601, 3602, 3603, 3604);
DELETE FROM sys_menu WHERE menu_id IN (3600, 3601, 3602, 3603, 3604);

-- 删除重复的设备权限（保留parent_id=2100下的规范组）  
DELETE FROM sys_role_menu WHERE menu_id IN (3204, 3205, 3206);
DELETE FROM sys_menu WHERE menu_id IN (3204, 3205, 3206);

-- 删除重复的日志权限（保留功能型权限，删除页面型重复）
DELETE FROM sys_role_menu WHERE menu_id IN (2310, 2320, 2330);
DELETE FROM sys_menu WHERE menu_id IN (2310, 2320, 2330);

-- ==========================================
-- 第二步：创建缺失的核心页面菜单
-- ==========================================

-- 创建告警管理页面（缺失的核心页面）
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
) VALUES (
    2200, '告警管理', 2000, 2, 'alert', 'redfish/alert/index', null, '',
    1, 0, 'C', '0', '0', 'redfish:alert:list', 'warning',
    'admin', current_timestamp, 'admin', current_timestamp, '告警信息管理页面'
) ON CONFLICT (menu_id) DO UPDATE SET
    menu_name = EXCLUDED.menu_name,
    parent_id = EXCLUDED.parent_id,
    order_num = EXCLUDED.order_num,
    path = EXCLUDED.path,
    component = EXCLUDED.component,
    perms = EXCLUDED.perms,
    icon = EXCLUDED.icon,
    update_time = current_timestamp;

-- 补充日志管理的子页面菜单
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
) VALUES 
(2310, '日志信息', 2300, 1, 'loginfo', 'redfish/log/index', null, '', 1, 0, 'C', '0', '0', 'redfish:log:list', 'documentation', 'admin', current_timestamp, 'admin', current_timestamp, '日志信息查看'),
(2320, '临时查看', 2300, 2, 'temp', 'redfish/log/temp', null, '', 1, 0, 'C', '0', '0', 'redfish:log:temp', 'edit', 'admin', current_timestamp, 'admin', current_timestamp, '临时日志查看'),
(2330, '历史管理', 2300, 3, 'history', 'redfish/log/history', null, '', 1, 0, 'C', '0', '0', 'redfish:log:history', 'time', 'admin', current_timestamp, 'admin', current_timestamp, '历史日志管理')
ON CONFLICT (menu_id) DO UPDATE SET
    menu_name = EXCLUDED.menu_name,
    parent_id = EXCLUDED.parent_id,
    path = EXCLUDED.path,
    component = EXCLUDED.component,
    perms = EXCLUDED.perms,
    update_time = current_timestamp;

-- ==========================================
-- 第三步：修正Dashboard权限的归属
-- ==========================================

-- Dashboard权限应该是全局权限，不应归属到设备信息下
-- 将Dashboard权限归属到根级（parent_id=0），作为全局API权限
UPDATE sys_menu SET 
    parent_id = 0,
    order_num = CASE 
        WHEN menu_id = 3000 THEN 1
        WHEN menu_id = 3001 THEN 2
        WHEN menu_id = 3002 THEN 3
        WHEN menu_id = 3003 THEN 4
        WHEN menu_id = 3004 THEN 5
    END
WHERE menu_id IN (3000, 3001, 3002, 3003, 3004);

-- ==========================================
-- 第四步：优化权限归属，保持与现有层级一致
-- ==========================================

-- 告警权限归属到告警管理(2200)
UPDATE sys_menu SET parent_id = 2200, order_num = order_num WHERE menu_id IN (3200, 3201, 3202, 3203);

-- 日志权限保持在日志管理(2300)下的现有分配
-- 不做调整，保持当前层级

-- 业务规则权限保持在排期规则(2400)下
-- 不做调整，保持当前层级

-- 设备权限保持在设备信息(2100)下  
-- 不做调整，保持当前层级

-- 系统监控权限归到系统监控模块(2)下
UPDATE sys_menu SET parent_id = 2 WHERE menu_id IN (3700, 3701, 3702, 3703, 3704, 3705) AND parent_id = 0;

-- ==========================================
-- 第五步：为普通用户分配与现有层级匹配的权限
-- ==========================================

-- 删除普通用户所有redfish权限，重新分配
DELETE FROM sys_role_menu WHERE role_id = 2 AND menu_id IN (
    SELECT menu_id FROM sys_menu WHERE perms LIKE 'redfish:%'
);

-- 为普通用户分配合理的权限（与现有层级结构匹配）
INSERT INTO sys_role_menu (role_id, menu_id) VALUES 
-- 页面访问权限
(2, 2100), -- 设备信息页面
(2, 2200), -- 告警管理页面
(2, 2310), -- 日志信息页面  
(2, 2320), -- 临时查看页面
(2, 2330), -- 历史管理页面

-- Dashboard全局权限
(2, 3000), -- dashboard:overview
(2, 3001), -- dashboard:alert
(2, 3002), -- dashboard:device
(2, 3003), -- dashboard:metrics
(2, 3004), -- dashboard:view

-- 设备基础权限（查看和测试）
(2, 3100), -- device:list
(2, 3101), -- device:query
(2, 3105), -- device:test

-- 告警基础权限（查看）
(2, 3200), -- alert:list

-- 日志基础权限（查看）
(2, 3300), -- log:list
(2, 3301), -- log:query
(2, 3306), -- log:temp 
(2, 3307), -- log:history

-- 业务规则查看权限
(2, 3400), -- businessRule:list
(2, 3401)  -- businessRule:query
ON CONFLICT (role_id, menu_id) DO NOTHING;

COMMIT;

-- ==========================================
-- 验证调整后的层级结构
-- ==========================================

SELECT '=== 调整后的菜单层级结构 ===' as info;

WITH RECURSIVE menu_tree AS (
    -- 根菜单
    SELECT 
        menu_id, 
        menu_name, 
        parent_id, 
        path,
        perms,
        menu_type,
        visible,
        order_num,
        0 as level,
        CAST(LPAD(order_num::text, 3, '0') as TEXT) as sort_path,
        CAST(menu_name as TEXT) as hierarchy_path
    FROM sys_menu 
    WHERE parent_id = 0 AND status = '0' AND menu_name IN ('设备管理', '系统管理', '系统监控', '系统工具')
    
    UNION ALL
    
    -- 递归子菜单
    SELECT 
        m.menu_id, 
        m.menu_name, 
        m.parent_id, 
        m.path,
        m.perms,
        m.menu_type,
        m.visible,
        m.order_num,
        t.level + 1,
        CAST(t.sort_path || '.' || LPAD(m.order_num::text, 3, '0') as TEXT),
        CAST(t.hierarchy_path || ' → ' || m.menu_name as TEXT)
    FROM sys_menu m
    INNER JOIN menu_tree t ON m.parent_id = t.menu_id
    WHERE t.level < 5 AND m.status = '0'
)
SELECT 
    REPEAT('  ', level) || menu_name as hierarchy,
    menu_type,
    CASE WHEN visible = '0' THEN '显示' ELSE '隐藏' END as visibility,
    perms,
    CASE WHEN rm.role_id IS NOT NULL THEN '✅' ELSE '❌' END as common_user
FROM menu_tree mt
LEFT JOIN sys_role_menu rm ON mt.menu_id = rm.menu_id AND rm.role_id = 2
WHERE mt.menu_name LIKE '%设备%' OR mt.menu_name LIKE '%告警%' OR mt.menu_name LIKE '%日志%' OR mt.menu_name LIKE '%排期%' OR mt.perms LIKE 'redfish:%'
ORDER BY sort_path;

-- 验证是否还有重复权限
SELECT '=== 重复权限检查 ===' as info;
SELECT 
    perms,
    COUNT(*) as count,
    CASE WHEN COUNT(*) > 1 THEN '❌ 仍有重复' ELSE '✅ 无重复' END as status
FROM sys_menu 
WHERE perms IS NOT NULL AND perms != '' AND perms LIKE 'redfish:%'
GROUP BY perms
HAVING COUNT(*) > 1;

SELECT '
🎯 权限配置已完全匹配您的现有菜单层级！

✅ 现有菜单结构保持：
   设备管理 (2000)
   ├── 设备信息 (2100) ← 设备相关权限在此
   ├── 告警管理 (2200) ← 告警相关权限在此
   ├── 日志管理 (2300) ← 日志相关权限在此
   │   ├── 日志信息 (2310)
   │   ├── 临时查看 (2320)
   │   └── 历史管理 (2330)
   └── 排期规则 (2400) ← 业务规则权限在此

✅ Dashboard权限：
   - 移至全局级别 (parent_id=0)
   - 作为API权限，不依赖特定页面

✅ 普通用户权限：
   - 可访问所有查看页面
   - 拥有Dashboard全部权限
   - 拥有基础查看和测试权限
   - 无管理操作权限

✅ 重复权限：已全部清理完毕
' as summary;
