-- 修复重复首页菜单问题的SQL脚本
-- 问题：菜单中出现了2个首页
-- 原因：之前创建的首页菜单路径与前端路由不匹配

-- 步骤1：删除之前创建的首页菜单（menu_id=10）
-- 这个菜单的路径是"dashboard"，与前端路由"/index"不匹配
DELETE FROM sys_role_menu WHERE menu_id = 10;
DELETE FROM sys_menu WHERE menu_id = 10;

-- 步骤2：创建正确的首页菜单配置
-- 路径应该与前端路由配置一致：/index
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
    10,                                    -- menu_id: 使用原来的ID
    '首页',                                -- menu_name: 菜单名称
    0,                                     -- parent_id: 顶级菜单
    0,                                     -- order_num: 显示顺序，0表示最前面
    '/index',                              -- path: 路由地址，与前端路由配置一致
    'redfish/dashboard/index',             -- component: 组件路径，与前端路由配置一致
    null,                                  -- query: 路由参数
    'Index',                               -- route_name: 路由名称，与前端路由配置一致
    1,                                     -- is_frame: 是否为外链（1否）
    0,                                     -- is_cache: 是否缓存（0缓存）
    'C',                                   -- menu_type: 菜单类型（C菜单）
    '0',                                   -- visible: 菜单状态（0显示）
    '0',                                   -- status: 菜单状态（0正常）
    null,                                  -- perms: 权限标识，首页可以设置为空
    'dashboard',                           -- icon: 菜单图标
    'admin',                               -- create_by: 创建者
    current_timestamp,                     -- create_time: 创建时间
    'admin',                               -- update_by: 更新者
    current_timestamp,                     -- update_time: 更新时间
    '首页菜单'                             -- remark: 备注
);

-- 步骤3：为普通角色分配首页菜单权限
INSERT INTO sys_role_menu (role_id, menu_id) VALUES (2, 10);

-- 步骤4：验证配置是否正确
-- 查询首页菜单配置
SELECT menu_id, menu_name, parent_id, path, component, perms, menu_type, visible, status 
FROM sys_menu 
WHERE menu_id = 10;

-- 查询普通角色的首页权限
SELECT rm.role_id, r.role_name, rm.menu_id, m.menu_name, m.path, m.perms 
FROM sys_role_menu rm 
JOIN sys_role r ON rm.role_id = r.role_id 
JOIN sys_menu m ON rm.menu_id = m.menu_id 
WHERE r.role_key = 'common' AND m.menu_id = 10;

-- 查询所有首页相关的菜单（应该只有1个可见的首页菜单）
SELECT menu_id, menu_name, parent_id, path, component, perms, menu_type, visible, status 
FROM sys_menu 
WHERE menu_name LIKE '%首页%' OR path = '/index' OR path = 'dashboard'
ORDER BY menu_id;

-- 说明：
-- 1. 删除了路径不匹配的首页菜单
-- 2. 创建了路径正确的首页菜单（/index）
-- 3. 保留了dashboard权限菜单（这些是隐藏的权限菜单，不会显示在菜单中）
-- 4. 现在应该只有1个可见的首页菜单
-- 5. 执行后需要重启应用或清除缓存以确保配置生效

