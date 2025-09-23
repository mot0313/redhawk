-- 🔧 完整权限体系清理和重构脚本
-- 基于后端实际使用权限的分析结果
-- 执行前请备份数据库！

-- ==========================================
-- 第一步：清理未使用的权限
-- ==========================================

-- 删除未使用的权限对应的角色关联
DELETE FROM sys_role_menu WHERE menu_id IN (
    SELECT menu_id FROM sys_menu WHERE perms IN (
        -- Redfish模块未使用权限
        'redfish:maintenance:query',
        'redfish:maintenance:add', 
        'redfish:maintenance:edit',
        'redfish:maintenance:remove',
        'redfish:log:temp:view',
        'redfish:log:temp:collect', 
        'redfish:log:temp:export',
        'redfish:log:history:view',
        'redfish:alert:query',
        
        -- 系统监控未使用权限
        'monitor:druid:list',
        'monitor:online:query',
        'monitor:online:batchLogout',
        'monitor:operlog:query',
        'monitor:logininfor:query',
        
        -- 系统工具未使用权限
        'tool:build:list',
        'tool:swagger:list'
    )
);

-- 删除未使用的权限菜单
DELETE FROM sys_menu WHERE perms IN (
    -- Redfish模块未使用权限
    'redfish:maintenance:query',
    'redfish:maintenance:add',
    'redfish:maintenance:edit', 
    'redfish:maintenance:remove',
    'redfish:log:temp:view',
    'redfish:log:temp:collect',
    'redfish:log:temp:export', 
    'redfish:log:history:view',
    'redfish:alert:query',
    
    -- 系统监控未使用权限
    'monitor:druid:list',
    'monitor:online:query',
    'monitor:online:batchLogout',
    'monitor:operlog:query', 
    'monitor:logininfor:query',
    
    -- 系统工具未使用权限
    'tool:build:list',
    'tool:swagger:list'
);

-- ==========================================
-- 第二步：确保关键权限存在并正确配置
-- ==========================================

-- 确保Dashboard权限存在（隐藏的API权限）
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
) VALUES 
(3000, '首页概览权限', 2100, 1, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:dashboard:overview', '#', 'admin', current_timestamp, 'admin', current_timestamp, '首页概览数据权限'),
(3001, '首页告警权限', 2100, 2, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:dashboard:alert', '#', 'admin', current_timestamp, 'admin', current_timestamp, '首页告警数据权限'),
(3002, '首页设备权限', 2100, 3, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:dashboard:device', '#', 'admin', current_timestamp, 'admin', current_timestamp, '首页设备数据权限'),
(3003, '首页指标权限', 2100, 4, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:dashboard:metrics', '#', 'admin', current_timestamp, 'admin', current_timestamp, '首页指标数据权限'),
(3004, '首页视图权限', 2100, 5, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:dashboard:view', '#', 'admin', current_timestamp, 'admin', current_timestamp, '首页完整视图权限')
ON CONFLICT (menu_id) DO UPDATE SET
    menu_name = EXCLUDED.menu_name,
    perms = EXCLUDED.perms,
    update_time = current_timestamp;

-- 确保设备管理权限完整
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
) VALUES 
(3100, '设备查询权限', 2200, 1, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:device:list', '#', 'admin', current_timestamp, 'admin', current_timestamp, '设备列表查询权限'),
(3101, '设备详情权限', 2200, 2, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:device:query', '#', 'admin', current_timestamp, 'admin', current_timestamp, '设备详情查询权限'),
(3102, '设备新增权限', 2200, 3, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:device:add', '#', 'admin', current_timestamp, 'admin', current_timestamp, '设备新增权限'),
(3103, '设备修改权限', 2200, 4, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:device:edit', '#', 'admin', current_timestamp, 'admin', current_timestamp, '设备修改权限'),
(3104, '设备删除权限', 2200, 5, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:device:remove', '#', 'admin', current_timestamp, 'admin', current_timestamp, '设备删除权限'),
(3105, '设备测试权限', 2200, 6, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:device:test', '#', 'admin', current_timestamp, 'admin', current_timestamp, '设备连通性测试权限'),
(3106, '设备导入权限', 2200, 7, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:device:import', '#', 'admin', current_timestamp, 'admin', current_timestamp, '设备数据导入权限'),
(3107, '设备导出权限', 2200, 8, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:device:export', '#', 'admin', current_timestamp, 'admin', current_timestamp, '设备数据导出权限')
ON CONFLICT (menu_id) DO UPDATE SET
    menu_name = EXCLUDED.menu_name,
    perms = EXCLUDED.perms,
    update_time = current_timestamp;

-- 确保告警管理权限完整
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
) VALUES 
(3200, '告警查询权限', 2300, 1, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:alert:list', '#', 'admin', current_timestamp, 'admin', current_timestamp, '告警列表查询权限'),
(3201, '告警维护权限', 2300, 2, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:alert:maintenance', '#', 'admin', current_timestamp, 'admin', current_timestamp, '告警维护计划权限'),
(3202, '告警删除权限', 2300, 3, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:alert:remove', '#', 'admin', current_timestamp, 'admin', current_timestamp, '告警删除权限'),
(3203, '告警导出权限', 2300, 4, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:alert:export', '#', 'admin', current_timestamp, 'admin', current_timestamp, '告警数据导出权限')
ON CONFLICT (menu_id) DO UPDATE SET
    menu_name = EXCLUDED.menu_name,
    perms = EXCLUDED.perms,
    update_time = current_timestamp;

-- 确保日志管理权限完整
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
) VALUES 
(3300, '日志查询权限', 2400, 1, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:log:list', '#', 'admin', current_timestamp, 'admin', current_timestamp, '日志列表查询权限'),
(3301, '日志详情权限', 2400, 2, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:log:query', '#', 'admin', current_timestamp, 'admin', current_timestamp, '日志详情查询权限'),
(3302, '日志清理权限', 2400, 3, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:log:cleanup', '#', 'admin', current_timestamp, 'admin', current_timestamp, '日志清理权限'),
(3303, '日志删除权限', 2400, 4, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:log:remove', '#', 'admin', current_timestamp, 'admin', current_timestamp, '日志删除权限'),
(3304, '日志导出权限', 2400, 5, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:log:export', '#', 'admin', current_timestamp, 'admin', current_timestamp, '日志导出权限'),
(3305, '日志收集权限', 2400, 6, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:log:collect', '#', 'admin', current_timestamp, 'admin', current_timestamp, '日志主动收集权限'),
(3306, '临时日志权限', 2400, 7, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:log:temp', '#', 'admin', current_timestamp, 'admin', current_timestamp, '临时日志管理权限'),
(3307, '历史日志权限', 2400, 8, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:log:history', '#', 'admin', current_timestamp, 'admin', current_timestamp, '历史日志查看权限')
ON CONFLICT (menu_id) DO UPDATE SET
    menu_name = EXCLUDED.menu_name,
    perms = EXCLUDED.perms,
    update_time = current_timestamp;

-- 确保业务规则权限完整
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
) VALUES 
(3400, '规则查询权限', 2400, 1, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:list', '#', 'admin', current_timestamp, 'admin', current_timestamp, '业务规则列表权限'),
(3401, '规则详情权限', 2400, 2, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:query', '#', 'admin', current_timestamp, 'admin', current_timestamp, '业务规则详情权限'),
(3402, '规则新增权限', 2400, 3, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:add', '#', 'admin', current_timestamp, 'admin', current_timestamp, '业务规则新增权限'),
(3403, '规则修改权限', 2400, 4, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:edit', '#', 'admin', current_timestamp, 'admin', current_timestamp, '业务规则修改权限'),
(3404, '规则删除权限', 2400, 5, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:remove', '#', 'admin', current_timestamp, 'admin', current_timestamp, '业务规则删除权限')
ON CONFLICT (menu_id) DO UPDATE SET
    menu_name = EXCLUDED.menu_name,
    perms = EXCLUDED.perms,
    update_time = current_timestamp;

-- ==========================================
-- 第三步：为普通用户分配合适的权限
-- ==========================================

-- 删除普通用户(role_id=2)的所有redfish权限，重新分配
DELETE FROM sys_role_menu WHERE role_id = 2 AND menu_id IN (
    SELECT menu_id FROM sys_menu WHERE perms LIKE 'redfish:%'
);

-- 为普通用户分配基础查看权限
INSERT INTO sys_role_menu (role_id, menu_id) VALUES 
-- Dashboard权限 - 普通用户可以查看首页
(2, 3000), -- dashboard:overview
(2, 3001), -- dashboard:alert
(2, 3002), -- dashboard:device
(2, 3003), -- dashboard:metrics
(2, 3004), -- dashboard:view

-- 设备权限 - 普通用户可以查看和测试设备
(2, 3100), -- device:list
(2, 3101), -- device:query
(2, 3105), -- device:test

-- 告警权限 - 普通用户可以查看告警
(2, 3200), -- alert:list

-- 日志权限 - 普通用户可以查看日志
(2, 3300), -- log:list
(2, 3301), -- log:query
(2, 3306), -- log:temp 
(2, 3307), -- log:history

-- 业务规则权限 - 普通用户可以查看规则
(2, 3400), -- businessRule:list
(2, 3401)  -- businessRule:query
ON CONFLICT (role_id, menu_id) DO NOTHING;

-- ==========================================
-- 第四步：清理重复和无效的缓存权限
-- ==========================================

-- 删除重复的缓存权限
DELETE FROM sys_menu WHERE menu_id IN (
    SELECT menu_id FROM (
        SELECT menu_id, ROW_NUMBER() OVER (PARTITION BY perms ORDER BY menu_id) as rn
        FROM sys_menu 
        WHERE perms = 'monitor:cache:list'
    ) t WHERE t.rn > 1
);

-- ==========================================
-- 第五步：验证清理结果
-- ==========================================

-- 显示清理后的权限统计
SELECT '=== 清理后的权限统计 ===' as info;

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

-- 显示普通用户的Redfish权限
SELECT '=== 普通用户Redfish权限 ===' as info;
SELECT 
    m.perms,
    m.menu_name,
    CASE WHEN rm.role_id IS NOT NULL THEN '✅ 已分配' ELSE '❌ 未分配' END as status
FROM sys_menu m
LEFT JOIN sys_role_menu rm ON m.menu_id = rm.menu_id AND rm.role_id = 2
WHERE m.perms LIKE 'redfish:%'
ORDER BY m.perms;

-- 显示清理说明
SELECT '
🎉 权限清理完成！

✅ 已删除的权限：
   - redfish:maintenance:* (除list外)
   - redfish:log:temp:* 详细权限
   - redfish:log:history:view
   - redfish:alert:query
   - monitor:druid:list
   - monitor:*:query 系列
   - monitor:online:batchLogout
   - tool:build:list
   - tool:swagger:list

✅ 已重新整理的权限：
   - Dashboard权限 (5个)
   - 设备管理权限 (8个)
   - 告警管理权限 (4个)
   - 日志管理权限 (8个)
   - 业务规则权限 (5个)

✅ 普通用户权限：
   - 首页完整访问权限
   - 设备查看和测试权限
   - 告警查看权限
   - 日志查看权限
   - 业务规则查看权限

⚠️  管理员用户保持全部权限不变

建议：清理完成后重启应用以清除权限缓存
' as description;
