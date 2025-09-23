-- 修复首页路径问题的SQL脚本
-- 问题：首页菜单路径与前端路由不匹配
-- 前端路由路径：/index
-- 数据库菜单路径：index

-- 更新首页菜单路径，使其与前端路由配置一致
UPDATE sys_menu 
SET path = '/index' 
WHERE menu_id = 10 AND menu_name = '首页';

-- 验证修改结果
SELECT menu_id, menu_name, parent_id, path, component, perms, menu_type, visible, status 
FROM sys_menu 
WHERE menu_id = 10;

-- 说明：
-- 1. 将首页菜单路径从"index"更新为"/index"
-- 2. 使其与前端路由配置完全匹配
-- 3. 执行后需要重启应用或清除缓存

