-- 🔄 统一maintenance权限为businessRule权限
-- 将 redfish:maintenance:list 改为 redfish:businessRule:list

BEGIN;

-- ==========================================
-- 第一步：更新排期规则页面的权限配置
-- ==========================================

-- 将排期规则页面的权限从 redfish:maintenance:list 改为 redfish:businessRule:list
UPDATE sys_menu 
SET perms = 'redfish:businessRule:list'
WHERE menu_id = 2400 AND perms = 'redfish:maintenance:list';

-- ==========================================
-- 第二步：清理不再需要的maintenance权限
-- ==========================================

-- 删除其他未使用的maintenance权限（如果存在）
DELETE FROM sys_role_menu WHERE menu_id IN (
    SELECT menu_id FROM sys_menu WHERE perms LIKE 'redfish:maintenance:%' AND perms != 'redfish:businessRule:list'
);

DELETE FROM sys_menu WHERE perms LIKE 'redfish:maintenance:%' AND perms != 'redfish:businessRule:list';

-- ==========================================
-- 第三步：确保业务规则权限完整存在
-- ==========================================

-- 确保业务规则的核心权限存在
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
) VALUES 
(3400, '业务规则查询', 2400, 1, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:list', '#', 'admin', current_timestamp, 'admin', current_timestamp, '业务规则列表查询权限'),
(3401, '业务规则详情', 2400, 2, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:query', '#', 'admin', current_timestamp, 'admin', current_timestamp, '业务规则详情查询权限'),
(3402, '业务规则新增', 2400, 3, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:add', '#', 'admin', current_timestamp, 'admin', current_timestamp, '业务规则新增权限'),
(3403, '业务规则修改', 2400, 4, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:edit', '#', 'admin', current_timestamp, 'admin', current_timestamp, '业务规则修改权限'),
(3404, '业务规则删除', 2400, 5, '', '', null, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:remove', '#', 'admin', current_timestamp, 'admin', current_timestamp, '业务规则删除权限')
ON CONFLICT (menu_id) DO UPDATE SET
    menu_name = EXCLUDED.menu_name,
    parent_id = EXCLUDED.parent_id,
    perms = EXCLUDED.perms,
    update_time = current_timestamp;

-- ==========================================
-- 第四步：为普通用户分配统一的权限
-- ==========================================

-- 删除普通用户的旧maintenance权限
DELETE FROM sys_role_menu WHERE role_id = 2 AND menu_id IN (
    SELECT menu_id FROM sys_menu WHERE perms LIKE 'redfish:maintenance:%'
);

-- 为普通用户分配业务规则查看权限
INSERT INTO sys_role_menu (role_id, menu_id) VALUES 
(2, 2400), -- 排期规则页面访问权限
(2, 3400), -- businessRule:list
(2, 3401)  -- businessRule:query
ON CONFLICT (role_id, menu_id) DO NOTHING;

COMMIT;

-- ==========================================
-- 验证统一后的权限配置
-- ==========================================

SELECT '=== 统一后的业务规则权限 ===' as info;

SELECT 
    m.menu_id,
    m.menu_name,
    m.parent_id,
    m.path,
    m.component,
    m.perms,
    m.menu_type,
    CASE WHEN m.visible = '0' THEN '显示' ELSE '隐藏' END as visibility,
    CASE WHEN rm.role_id IS NOT NULL THEN '✅ 普通用户可用' ELSE '❌ 普通用户不可用' END as common_user_access
FROM sys_menu m
LEFT JOIN sys_role_menu rm ON m.menu_id = rm.menu_id AND rm.role_id = 2
WHERE (m.menu_id = 2400 OR m.perms LIKE 'redfish:businessRule:%')
  AND m.status = '0'
ORDER BY m.menu_id;

-- 验证是否还有maintenance相关权限
SELECT '=== 检查剩余的maintenance权限 ===' as info;

SELECT 
    menu_id,
    menu_name,
    perms,
    CASE WHEN COUNT(*) > 0 THEN '⚠️ 仍有maintenance权限存在' ELSE '✅ 已全部统一' END as status
FROM sys_menu 
WHERE perms LIKE 'redfish:maintenance:%'
GROUP BY menu_id, menu_name, perms;

SELECT '
🎯 权限统一完成！

✅ 统一效果：
   - 排期规则页面权限：redfish:maintenance:list → redfish:businessRule:list
   - 所有maintenance相关权限已清理
   - 业务规则权限体系完整
   - 普通用户权限已重新分配

✅ 页面功能映射：
   - 排期规则页面 (2400) → redfish:businessRule:list
   - 紧急度规则 Tab → redfish:businessRule:list/query
   - 业务类型管理 Tab → redfish:businessRule:list/query  
   - 硬件类型管理 Tab → redfish:businessRule:list/query

✅ 权限层级：
   排期规则 (2400) - redfish:businessRule:list
   ├── 业务规则查询 (3400) - redfish:businessRule:list
   ├── 业务规则详情 (3401) - redfish:businessRule:query
   ├── 业务规则新增 (3402) - redfish:businessRule:add
   ├── 业务规则修改 (3403) - redfish:businessRule:edit
   └── 业务规则删除 (3404) - redfish:businessRule:remove

✅ 普通用户权限：
   - 可访问排期规则页面
   - 可查看业务规则
   - 可查看规则详情
   - 无管理操作权限

🔄 权限体系现在完全统一为 redfish:businessRule 系列！
' as summary;
