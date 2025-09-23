-- 通知公告系统启用所需的数据库更新
-- 执行日期：需要手动执行

-- 1. 确保通知公告菜单对所有用户可见
UPDATE sys_menu SET visible = '0', status = '0' WHERE menu_id = 107;

-- 2. 验证普通用户是否拥有通知查看权限（应该已经有了）
-- 查询确认：
-- SELECT rm.role_id, r.role_name, rm.menu_id, m.menu_name, m.perms 
-- FROM sys_role_menu rm 
-- JOIN sys_role r ON rm.role_id = r.role_id 
-- JOIN sys_menu m ON rm.menu_id = m.menu_id 
-- WHERE rm.menu_id IN (107, 1035) AND rm.role_id = 2;

-- 如果普通用户没有权限，执行以下语句：
-- INSERT INTO sys_role_menu (role_id, menu_id) VALUES (2, 107);  -- 通知公告菜单
-- INSERT INTO sys_role_menu (role_id, menu_id) VALUES (2, 1035); -- 公告查询权限

-- 3. 验证现有通知数据
SELECT notice_id, notice_title, notice_type, status, create_time FROM sys_notice ORDER BY create_time DESC LIMIT 5;
