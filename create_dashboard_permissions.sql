-- 创建Dashboard权限配置SQL脚本
-- 解决普通用户首页权限问题
-- 问题：普通用户登录时首页提示没有权限
-- 原因：首页调用的API需要特定权限，而普通用户没有这些权限

-- 步骤1：在sys_menu表中创建dashboard相关的权限菜单
-- 使用3000-3010范围的菜单ID，避免与现有菜单冲突

-- 1. 首页概览权限
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
    3000,                                    -- menu_id: 首页概览权限
    '首页概览权限',                          -- menu_name: 菜单名称
    0,                                       -- parent_id: 顶级权限
    1,                                       -- order_num: 显示顺序
    '',                                      -- path: 路径为空
    '',                                      -- component: 组件为空
    null,                                    -- query: 路由参数
    '',                                      -- route_name: 路由名称
    1,                                       -- is_frame: 是否为外链（1否）
    0,                                       -- is_cache: 是否缓存（0缓存）
    'F',                                     -- menu_type: 菜单类型（F按钮权限）
    '1',                                     -- visible: 菜单状态（1隐藏）
    '0',                                     -- status: 菜单状态（0正常）
    'redfish:dashboard:overview',            -- perms: 权限标识
    '#',                                     -- icon: 菜单图标
    'admin',                                 -- create_by: 创建者
    current_timestamp,                       -- create_time: 创建时间
    'admin',                                 -- update_by: 更新者
    current_timestamp,                       -- update_time: 更新时间
    '首页概览数据权限'                       -- remark: 备注
);

-- 2. 告警数据权限
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, query, route_name, 
    is_frame, is_cache, menu_type, visible, status, perms, icon, 
    create_by, create_time, update_by, update_time, remark
) VALUES (
    3001, '告警数据权限', 0, 2, '', '', null, '', 
    1, 0, 'F', '1', '0', 'redfish:dashboard:alert', '#', 
    'admin', current_timestamp, 'admin', current_timestamp, '告警相关数据权限'
);

-- 3. 设备健康权限
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, query, route_name, 
    is_frame, is_cache, menu_type, visible, status, perms, icon, 
    create_by, create_time, update_by, update_time, remark
) VALUES (
    3002, '设备健康权限', 0, 3, '', '', null, '', 
    1, 0, 'F', '1', '0', 'redfish:dashboard:device', '#', 
    'admin', current_timestamp, 'admin', current_timestamp, '设备健康数据权限'
);

-- 4. 完整首页权限
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, query, route_name, 
    is_frame, is_cache, menu_type, visible, status, perms, icon, 
    create_by, create_time, update_by, update_time, remark
) VALUES (
    3003, '完整首页权限', 0, 4, '', '', null, '', 
    1, 0, 'F', '1', '0', 'redfish:dashboard:view', '#', 
    'admin', current_timestamp, 'admin', current_timestamp, '完整首页数据权限'
);

-- 5. 系统指标权限
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, query, route_name, 
    is_frame, is_cache, menu_type, visible, status, perms, icon, 
    create_by, create_time, update_by, update_time, remark
) VALUES (
    3004, '系统指标权限', 0, 5, '', '', null, '', 
    1, 0, 'F', '1', '0', 'redfish:dashboard:metrics', '#', 
    'admin', current_timestamp, 'admin', current_timestamp, '系统健康指标权限'
);

-- 步骤2：为普通角色(role_id=2)分配这些权限
INSERT INTO sys_role_menu (role_id, menu_id) VALUES 
(2, 3000),  -- 普通角色 - 首页概览权限
(2, 3001),  -- 普通角色 - 告警数据权限
(2, 3002),  -- 普通角色 - 设备健康权限
(2, 3003),  -- 普通角色 - 完整首页权限
(2, 3004);  -- 普通角色 - 系统指标权限

-- 步骤3：验证配置是否正确
-- 查询新创建的权限菜单
SELECT menu_id, menu_name, perms, menu_type, visible, status 
FROM sys_menu 
WHERE menu_id BETWEEN 3000 AND 3010
ORDER BY menu_id;

-- 查询普通角色的dashboard权限
SELECT rm.role_id, r.role_name, rm.menu_id, m.menu_name, m.perms 
FROM sys_role_menu rm 
JOIN sys_role r ON rm.role_id = r.role_id 
JOIN sys_menu m ON rm.menu_id = m.menu_id 
WHERE r.role_key = 'common' 
AND m.menu_id BETWEEN 3000 AND 3010
ORDER BY m.menu_id;

-- 说明：
-- 1. 这个脚本解决了普通用户无法访问首页的权限问题
-- 2. 创建了首页API调用所需的所有权限
-- 3. 为普通角色分配了这些权限
-- 4. 执行后需要重启应用或清除缓存以确保配置生效
-- 5. 权限菜单设置为隐藏，不影响前端菜单显示

