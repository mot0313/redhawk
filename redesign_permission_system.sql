-- 重新设计权限体系 - 层级清晰、一一对应
-- 完全重新设计菜单和权限结构，确保层级清晰，权限与功能一一对应

-- ================================================================================
-- 第一步：清理现有的redfish相关权限配置
-- ================================================================================

-- 删除普通角色的所有redfish相关权限
DELETE FROM sys_role_menu WHERE role_id = 2 AND menu_id IN (
    SELECT menu_id FROM sys_menu WHERE 
    perms LIKE '%redfish%' OR 
    menu_name LIKE '%设备%' OR 
    menu_name LIKE '%告警%' OR 
    menu_name LIKE '%日志%' OR 
    menu_name LIKE '%排期%' OR
    menu_name LIKE '%首页%' OR
    menu_name LIKE '%dashboard%'
);

-- 删除所有redfish相关的菜单
DELETE FROM sys_menu WHERE menu_id BETWEEN 2000 AND 2999;
DELETE FROM sys_menu WHERE menu_id BETWEEN 3000 AND 3999;
DELETE FROM sys_menu WHERE menu_id BETWEEN 20000 AND 29999;
DELETE FROM sys_menu WHERE menu_id BETWEEN 200000 AND 299999;

-- ================================================================================
-- 第二步：重新创建层级清晰的菜单结构
-- ================================================================================

-- 1. 一级菜单：设备管理
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
) VALUES (
    2000, '设备管理', 0, 1, 'devices', null, null, '',
    1, 0, 'M', '0', '0', '', 'monitor',
    'admin', current_timestamp, 'admin', current_timestamp, '设备管理模块'
);

-- 2. 二级菜单
-- 2.1 设备信息
INSERT INTO sys_menu VALUES (
    2100, '设备信息', 2000, 1, 'device', 'redfish/device/index', null, 'DeviceInfo',
    1, 0, 'C', '0', '0', 'redfish:device:list', 'server',
    'admin', current_timestamp, 'admin', current_timestamp, '设备信息管理'
);

-- 2.2 告警管理
INSERT INTO sys_menu VALUES (
    2200, '告警管理', 2000, 2, 'alert', 'redfish/alert/index', null, 'AlertInfo',
    1, 0, 'C', '0', '0', 'redfish:alert:list', 'warning',
    'admin', current_timestamp, 'admin', current_timestamp, '告警信息管理'
);

-- 2.3 日志管理
INSERT INTO sys_menu VALUES (
    2300, '日志管理', 2000, 3, 'log', null, null, '',
    1, 0, 'M', '0', '0', '', 'documentation',
    'admin', current_timestamp, 'admin', current_timestamp, '日志管理模块'
);

-- 2.4 排期规则
INSERT INTO sys_menu VALUES (
    2400, '排期规则', 2000, 4, 'maintenance', 'redfish/maintenance/index', null, 'MaintenanceRule',
    1, 0, 'C', '0', '0', 'redfish:businessRule:list', 'calendar',
    'admin', current_timestamp, 'admin', current_timestamp, '排期规则管理'
);

-- 3. 三级菜单（日志管理子菜单）
-- 3.1 日志信息
INSERT INTO sys_menu VALUES (
    2310, '日志信息', 2300, 1, 'loginfo', 'redfish/log/index', null, 'LogInfo',
    1, 0, 'C', '0', '0', 'redfish:log:list', 'document',
    'admin', current_timestamp, 'admin', current_timestamp, '日志信息查看'
);

-- 3.2 临时查看
INSERT INTO sys_menu VALUES (
    2320, '临时查看', 2300, 2, 'temp', 'redfish/log/temp', null, 'LogTemp',
    1, 0, 'C', '0', '0', 'redfish:log:temp', 'view',
    'admin', current_timestamp, 'admin', current_timestamp, '临时日志查看'
);

-- 3.3 历史管理
INSERT INTO sys_menu VALUES (
    2330, '历史管理', 2300, 3, 'history', 'redfish/log/history', null, 'LogHistory',
    1, 0, 'C', '0', '0', 'redfish:log:history', 'time',
    'admin', current_timestamp, 'admin', current_timestamp, '历史日志管理'
);

-- ================================================================================
-- 第三步：创建功能权限（隐藏按钮权限）
-- ================================================================================

-- 1. 首页Dashboard权限
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
) VALUES 
-- Dashboard权限组
(3100, '首页概览', 0, 100, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:dashboard:overview', '#', 'admin', current_timestamp, 'admin', current_timestamp, '首页概览数据权限'),
(3101, '首页告警', 0, 101, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:dashboard:alert', '#', 'admin', current_timestamp, 'admin', current_timestamp, '首页告警数据权限'),
(3102, '首页设备', 0, 102, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:dashboard:device', '#', 'admin', current_timestamp, 'admin', current_timestamp, '首页设备数据权限'),
(3103, '首页指标', 0, 103, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:dashboard:metrics', '#', 'admin', current_timestamp, 'admin', current_timestamp, '首页系统指标权限'),
(3104, '首页完整', 0, 104, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:dashboard:view', '#', 'admin', current_timestamp, 'admin', current_timestamp, '首页完整数据权限'),

-- 设备权限组
(3200, '设备查询', 2100, 1, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:device:query', '#', 'admin', current_timestamp, 'admin', current_timestamp, '设备详情查询权限'),
(3201, '设备新增', 2100, 2, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:device:add', '#', 'admin', current_timestamp, 'admin', current_timestamp, '设备新增权限'),
(3202, '设备修改', 2100, 3, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:device:edit', '#', 'admin', current_timestamp, 'admin', current_timestamp, '设备修改权限'),
(3203, '设备删除', 2100, 4, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:device:remove', '#', 'admin', current_timestamp, 'admin', current_timestamp, '设备删除权限'),
(3204, '设备测试', 2100, 5, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:device:test', '#', 'admin', current_timestamp, 'admin', current_timestamp, '设备连通性测试权限'),
(3205, '设备导入', 2100, 6, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:device:import', '#', 'admin', current_timestamp, 'admin', current_timestamp, '设备数据导入权限'),
(3206, '设备导出', 2100, 7, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:device:export', '#', 'admin', current_timestamp, 'admin', current_timestamp, '设备数据导出权限'),

-- 告警权限组
(3300, '告警查询', 2200, 1, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:alert:query', '#', 'admin', current_timestamp, 'admin', current_timestamp, '告警详情查询权限'),
(3301, '告警删除', 2200, 2, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:alert:remove', '#', 'admin', current_timestamp, 'admin', current_timestamp, '告警删除权限'),
(3302, '告警导出', 2200, 3, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:alert:export', '#', 'admin', current_timestamp, 'admin', current_timestamp, '告警数据导出权限'),
(3303, '告警维护', 2200, 4, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:alert:maintenance', '#', 'admin', current_timestamp, 'admin', current_timestamp, '告警维护计划权限'),

-- 日志权限组
(3400, '日志查询', 2310, 1, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:log:query', '#', 'admin', current_timestamp, 'admin', current_timestamp, '日志详情查询权限'),
(3401, '日志收集', 2310, 2, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:log:collect', '#', 'admin', current_timestamp, 'admin', current_timestamp, '日志收集权限'),
(3402, '日志导出', 2310, 3, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:log:export', '#', 'admin', current_timestamp, 'admin', current_timestamp, '日志导出权限'),
(3403, '日志删除', 2310, 4, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:log:remove', '#', 'admin', current_timestamp, 'admin', current_timestamp, '日志删除权限'),
(3404, '日志清理', 2310, 5, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:log:cleanup', '#', 'admin', current_timestamp, 'admin', current_timestamp, '日志清理权限'),

-- 临时日志权限
(3410, '临时查看权限', 2320, 1, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:log:temp:view', '#', 'admin', current_timestamp, 'admin', current_timestamp, '临时日志查看权限'),
(3411, '临时收集权限', 2320, 2, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:log:temp:collect', '#', 'admin', current_timestamp, 'admin', current_timestamp, '临时日志收集权限'),
(3412, '临时导出权限', 2320, 3, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:log:temp:export', '#', 'admin', current_timestamp, 'admin', current_timestamp, '临时日志导出权限'),

-- 历史日志权限
(3420, '历史查看权限', 2330, 1, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:log:history:view', '#', 'admin', current_timestamp, 'admin', current_timestamp, '历史日志查看权限'),

-- 排期规则权限组
(3500, '业务规则查询', 2400, 1, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:query', '#', 'admin', current_timestamp, 'admin', current_timestamp, '业务规则查询权限'),
(3501, '业务规则新增', 2400, 2, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:add', '#', 'admin', current_timestamp, 'admin', current_timestamp, '业务规则新增权限'),
(3502, '业务规则修改', 2400, 3, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:edit', '#', 'admin', current_timestamp, 'admin', current_timestamp, '业务规则修改权限'),
(3503, '业务规则删除', 2400, 4, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:remove', '#', 'admin', current_timestamp, 'admin', current_timestamp, '业务规则删除权限'),

-- 业务规则权限组（如果需要）
(3600, '业务规则查询', 0, 600, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:query', '#', 'admin', current_timestamp, 'admin', current_timestamp, '业务规则查询权限'),
(3601, '业务规则列表', 0, 601, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:list', '#', 'admin', current_timestamp, 'admin', current_timestamp, '业务规则列表权限'),
(3602, '业务规则新增', 0, 602, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:add', '#', 'admin', current_timestamp, 'admin', current_timestamp, '业务规则新增权限'),
(3603, '业务规则修改', 0, 603, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:edit', '#', 'admin', current_timestamp, 'admin', current_timestamp, '业务规则修改权限'),
(3604, '业务规则删除', 0, 604, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:remove', '#', 'admin', current_timestamp, 'admin', current_timestamp, '业务规则删除权限'),

-- 监控配置权限组
(3700, '监控配置查看', 0, 700, '', '', null, '', 1, 0, 'F', '1', '0', 'monitor:config:view', '#', 'admin', current_timestamp, 'admin', current_timestamp, '监控配置查看权限'),
(3701, '监控配置编辑', 0, 701, '', '', null, '', 1, 0, 'F', '1', '0', 'monitor:config:edit', '#', 'admin', current_timestamp, 'admin', current_timestamp, '监控配置编辑权限'),
(3702, '监控任务查看', 0, 702, '', '', null, '', 1, 0, 'F', '1', '0', 'monitor:task:view', '#', 'admin', current_timestamp, 'admin', current_timestamp, '监控任务查看权限'),
(3703, '监控任务执行', 0, 703, '', '', null, '', 1, 0, 'F', '1', '0', 'monitor:task:execute', '#', 'admin', current_timestamp, 'admin', current_timestamp, '监控任务执行权限'),
(3704, '监控任务管理', 0, 704, '', '', null, '', 1, 0, 'F', '1', '0', 'monitor:task:manage', '#', 'admin', current_timestamp, 'admin', current_timestamp, '监控任务管理权限'),
(3705, '监控系统查看', 0, 705, '', '', null, '', 1, 0, 'F', '1', '0', 'monitor:system:view', '#', 'admin', current_timestamp, 'admin', current_timestamp, '监控系统查看权限');

-- ================================================================================
-- 第四步：为普通角色分配权限
-- ================================================================================

-- 分配菜单权限（可见菜单）
INSERT INTO sys_role_menu (role_id, menu_id) VALUES 
-- 主菜单
(2, 2000), -- 设备管理
-- 二级菜单
(2, 2100), -- 设备信息
(2, 2200), -- 告警管理
(2, 2300), -- 日志管理
(2, 2400), -- 排期规则
-- 三级菜单
(2, 2310), -- 日志信息
(2, 2320), -- 临时查看
(2, 2330), -- 历史管理

-- 分配功能权限（隐藏权限）
-- Dashboard权限
(2, 3100), (2, 3101), (2, 3102), (2, 3103), (2, 3104),
-- 设备权限（给普通用户基础查看和测试权限）
(2, 3200), (2, 3204), (2, 3206),
-- 告警权限（给普通用户查看和导出权限）
(2, 3300), (2, 3302),
-- 日志权限（给普通用户查看、收集、导出权限）
(2, 3400), (2, 3401), (2, 3402),
-- 临时日志权限
(2, 3410), (2, 3411), (2, 3412),
-- 历史日志权限
(2, 3420),
-- 排期规则权限（给普通用户查看权限）
(2, 3500),
-- 业务规则权限（给普通用户查看权限）
(2, 3600), (2, 3601),
-- 监控权限（给普通用户基础查看和执行权限）
(2, 3700), (2, 3702), (2, 3703);

-- ================================================================================
-- 第五步：验证权限配置
-- ================================================================================

-- 查看菜单结构
SELECT '=== 菜单结构 ===' as info;
SELECT 
    CASE 
        WHEN parent_id = 0 THEN CONCAT('├─ ', menu_name)
        WHEN parent_id IN (SELECT menu_id FROM sys_menu WHERE parent_id = 0) THEN CONCAT('│  ├─ ', menu_name)
        ELSE CONCAT('│  │  ├─ ', menu_name)
    END as menu_structure,
    menu_id,
    path,
    perms,
    menu_type,
    visible
FROM sys_menu 
WHERE menu_id BETWEEN 2000 AND 3999
ORDER BY 
    CASE WHEN parent_id = 0 THEN menu_id ELSE parent_id END,
    parent_id,
    order_num,
    menu_id;

-- 查看普通角色权限
SELECT '=== 普通角色权限 ===' as info;
SELECT 
    m.menu_name,
    m.path,
    m.perms,
    m.menu_type,
    CASE WHEN m.menu_type = 'M' THEN '目录'
         WHEN m.menu_type = 'C' THEN '菜单'
         WHEN m.menu_type = 'F' THEN '权限'
         ELSE '其他' END as type_desc,
    CASE WHEN m.visible = '0' THEN '显示' ELSE '隐藏' END as visible_desc
FROM sys_role_menu rm 
JOIN sys_menu m ON rm.menu_id = m.menu_id 
WHERE rm.role_id = 2 AND m.menu_id BETWEEN 2000 AND 3999
ORDER BY m.menu_id;

-- 说明
SELECT '=== 权限体系说明 ===' as info;
SELECT '
权限体系设计说明：
1. 菜单层级：一级菜单(2000) -> 二级菜单(21xx-24xx) -> 三级菜单(231x-233x)
2. 功能权限：Dashboard(31xx) | 设备(32xx) | 告警(33xx) | 日志(34xx) | 排期(35xx) | 业务规则(36xx) | 监控(37xx)
3. 权限对应：每个后端CheckUserInterfaceAuth权限都有对应的菜单权限
4. 普通用户权限：拥有查看、基础操作权限，不含删除、新增等敏感权限
5. 权限可扩展：可根据需要为普通用户添加更多权限
' as description;
