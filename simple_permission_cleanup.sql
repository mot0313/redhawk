-- 🔧 简化版权限清理脚本
-- 针对数据库中发现的严重权限冗余问题

-- ==========================================
-- 立即删除的重复权限 (共13个重复权限需要清理)
-- ==========================================

-- 1. 删除重复的业务规则权限
DELETE FROM sys_role_menu WHERE menu_id IN (3600, 3601, 3602, 3603, 3604);
DELETE FROM sys_menu WHERE menu_id IN (3600, 3601, 3602, 3603, 3604);

-- 2. 删除重复的设备权限  
DELETE FROM sys_role_menu WHERE menu_id IN (3204, 3205, 3206);
DELETE FROM sys_menu WHERE menu_id IN (3204, 3205, 3206);

-- 3. 删除重复的告警权限（保留功能型3200，删除页面型2200）
DELETE FROM sys_role_menu WHERE menu_id = 2200;
DELETE FROM sys_menu WHERE menu_id = 2200;

-- 4. 删除重复的日志权限
DELETE FROM sys_role_menu WHERE menu_id IN (2310, 2320, 2330);
DELETE FROM sys_menu WHERE menu_id IN (2310, 2320, 2330);

-- ==========================================
-- 重新整理层级关系
-- ==========================================

-- 更新设备权限归属到设备信息(2100)
UPDATE sys_menu SET parent_id = 2100 WHERE menu_id IN (3100, 3101, 3102, 3103, 3104, 3105, 3106, 3107);

-- 更新告警权限归属到告警管理(2200) 
UPDATE sys_menu SET parent_id = 2200 WHERE menu_id IN (3200, 3201, 3202, 3203);

-- 更新日志权限归属到日志管理(2300)
UPDATE sys_menu SET parent_id = 2300 WHERE menu_id IN (3300, 3301, 3302, 3303, 3304, 3305, 3306, 3307);

-- 更新业务规则权限归属到排期规则(2400)
UPDATE sys_menu SET parent_id = 2400 WHERE menu_id IN (3400, 3401, 3402, 3403, 3404);

-- ==========================================
-- 为普通用户重新分配权限
-- ==========================================

-- 删除普通用户所有redfish权限，重新分配
DELETE FROM sys_role_menu WHERE role_id = 2 AND menu_id IN (
    SELECT menu_id FROM sys_menu WHERE perms LIKE 'redfish:%'
);

-- 为普通用户分配基础权限
INSERT INTO sys_role_menu (role_id, menu_id) VALUES 
-- 菜单访问权限
(2, 2100), -- 设备信息页面
(2, 2200), -- 告警管理页面  
(2, 2300), -- 日志管理页面

-- Dashboard权限
(2, 3000), (2, 3001), (2, 3002), (2, 3003), (2, 3004),

-- 设备基础权限
(2, 3100), (2, 3101), (2, 3105),

-- 告警基础权限
(2, 3200),

-- 日志基础权限
(2, 3300), (2, 3301), (2, 3306), (2, 3307),

-- 业务规则查看权限
(2, 3400), (2, 3401)
ON CONFLICT (role_id, menu_id) DO NOTHING;
