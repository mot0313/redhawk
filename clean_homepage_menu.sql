-- 清理首页菜单配置SQL脚本
-- 确保只有一个首页菜单

-- 1. 删除所有首页相关的菜单（包括权限菜单）
DELETE FROM sys_role_menu WHERE menu_id IN (10, 3000, 3001, 3002, 3003, 3004);
DELETE FROM sys_menu WHERE menu_id IN (10, 3000, 3001, 3002, 3003, 3004);

-- 2. 重新创建正确的首页菜单配置
INSERT INTO sys_menu (
    menu_id, 
    menu_name, 
    parent_id, 
    order_num, 
    path, 
    component, 
    query, 
    route_name, 
    is_frame, 
    is_cache, 
    menu_type, 
    visible, 
    status, 
    perms, 
    icon, 
    create_by, 
    create_time, 
    update_by, 
    update_time, 
    remark
) VALUES (
    10,                                    -- menu_id: 首页菜单
    '首页',                                -- menu_name: 菜单名称
    0,                                     -- parent_id: 顶级菜单
    0,                                     -- order_num: 显示顺序，0表示最前面
    'index',                               -- path: 路由地址
    'redfish/dashboard/index',             -- component: 组件路径
    null,                                  -- query: 路由参数
    'Index',                               -- route_name: 路由名称
    1,                                     -- is_frame: 是否为外链（1否）
    0,                                     -- is_cache: 是否缓存（0缓存）
    'C',                                   -- menu_type: 菜单类型（C菜单）
    '0',                                   -- visible: 菜单状态（0显示）
    '0',                                   -- status: 菜单状态（0正常）
    null,                                  -- perms: 权限标识
    'dashboard',                           -- icon: 菜单图标
    'admin',                               -- create_by: 创建者
    current_timestamp,                     -- create_time: 创建时间
    'admin',                               -- update_by: 更新者
    current_timestamp,                     -- update_time: 更新时间
    '首页菜单'                             -- remark: 备注
);

-- 3. 创建dashboard权限菜单（隐藏）
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

-- 4. 为普通角色分配权限
INSERT INTO sys_role_menu (role_id, menu_id) VALUES 
(2, 10),   -- 普通角色 - 首页菜单
(2, 3000), -- 普通角色 - 首页概览权限
(2, 3001), -- 普通角色 - 告警数据权限
(2, 3002), -- 普通角色 - 设备健康权限
(2, 3003), -- 普通角色 - 完整首页权限
(2, 3004); -- 普通角色 - 系统指标权限

-- 5. 验证结果
SELECT '清理后的首页菜单' as description;
SELECT menu_id, menu_name, parent_id, path, component, perms, menu_type, visible, status, order_num
FROM sys_menu 
WHERE menu_name LIKE '%首页%' OR path LIKE '%index%' OR path LIKE '%dashboard%'
ORDER BY menu_id;

SELECT '普通角色的首页权限' as description;
SELECT rm.role_id, r.role_name, rm.menu_id, m.menu_name, m.path, m.perms, m.menu_type, m.visible
FROM sys_role_menu rm 
JOIN sys_role r ON rm.role_id = r.role_id 
JOIN sys_menu m ON rm.menu_id = m.menu_id 
WHERE r.role_key = 'common' AND (m.menu_name LIKE '%首页%' OR m.path LIKE '%index%' OR m.path LIKE '%dashboard%')
ORDER BY m.menu_id;

-- 说明：
-- 1. 完全清理了所有首页相关的菜单配置
-- 2. 重新创建了正确的首页菜单和权限配置
-- 3. 确保只有一个可见的首页菜单
-- 4. 执行后需要重启应用或清除缓存

