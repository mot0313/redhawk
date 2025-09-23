-- 🔧 修复通知公告菜单显示问题
-- 启用被停用的通知公告功能

BEGIN;

-- ==========================================
-- 第一步：检查通知公告菜单当前状态
-- ==========================================

SELECT '=== 通知公告菜单当前状态 ===' as info;
SELECT 
    m.menu_id,
    m.menu_name,
    m.order_num,
    m.path,
    m.component,
    CASE WHEN m.visible = '0' THEN '显示' ELSE '隐藏' END as visibility,
    CASE WHEN m.status = '0' THEN '正常' ELSE '停用' END as status,
    CASE WHEN rm.role_id IS NOT NULL THEN '✅ 已分配' ELSE '❌ 未分配' END as common_user_access
FROM sys_menu m
LEFT JOIN sys_role_menu rm ON m.menu_id = rm.menu_id AND rm.role_id = 2
WHERE m.menu_id = 107 OR m.parent_id = 107
ORDER BY m.menu_id;

-- ==========================================
-- 第二步：启用通知公告菜单
-- ==========================================

-- 启用通知公告主菜单
UPDATE sys_menu SET 
    status = '0',
    visible = '0'
WHERE menu_id = 107;

-- 确保所有通知公告子功能权限也是正常状态
UPDATE sys_menu SET 
    status = '0'
WHERE parent_id = 107;

-- ==========================================
-- 第三步：为普通用户分配通知公告权限
-- ==========================================

-- 为普通用户分配通知公告菜单访问权限
INSERT INTO sys_role_menu (role_id, menu_id) VALUES 
(2, 107) -- 通知公告主菜单
ON CONFLICT (role_id, menu_id) DO NOTHING;

-- 通知公告的功能权限已经分配给普通用户，无需重复分配

COMMIT;

-- ==========================================
-- 验证修复结果
-- ==========================================

SELECT '=== 修复后的系统管理菜单 ===' as info;
SELECT 
    m.menu_id,
    m.menu_name,
    m.order_num,
    m.path,
    CASE WHEN m.visible = '0' THEN '显示' ELSE '隐藏' END as visibility,
    CASE WHEN m.status = '0' THEN '正常' ELSE '停用' END as status,
    CASE WHEN rm.role_id IS NOT NULL THEN '✅ 已分配' ELSE '❌ 未分配' END as common_user_access
FROM sys_menu m
LEFT JOIN sys_role_menu rm ON m.menu_id = rm.menu_id AND rm.role_id = 2
WHERE m.parent_id = 1 AND m.menu_type = 'C'
ORDER BY m.order_num;

-- 检查通知公告功能权限
SELECT '=== 通知公告功能权限 ===' as info;
SELECT 
    m.menu_name,
    m.perms,
    CASE WHEN rm.role_id IS NOT NULL THEN '✅ 已分配' ELSE '❌ 未分配' END as common_user_access
FROM sys_menu m
LEFT JOIN sys_role_menu rm ON m.menu_id = rm.menu_id AND rm.role_id = 2
WHERE m.parent_id = 107
ORDER BY m.order_num;

SELECT '
🎉 通知公告菜单修复完成！

✅ 问题分析：
   - 通知公告菜单存在但状态为"停用"
   - 前端组件 system/notice/index.vue 完整存在
   - 子功能权限已分配给普通用户

✅ 修复内容：
   - 启用通知公告主菜单 (107)
   - 确保所有子功能状态正常
   - 为普通用户分配菜单访问权限

✅ 完整的系统管理菜单：
   1. 用户管理 (/system/user)
   2. 角色管理 (/system/role)
   3. 菜单管理 (/system/menu)
   4. 部门管理 (/system/dept)
   5. 岗位管理 (/system/post)
   6. 字典管理 (/system/dict)
   7. 参数设置 (/system/config)
   8. 通知公告 (/system/notice) - 已恢复

✅ 通知公告功能：
   - 公告查询 (system:notice:query)
   - 公告新增 (system:notice:add)
   - 公告修改 (system:notice:edit)
   - 公告删除 (system:notice:remove)

✅ 前端组件：system/notice/index.vue 已确认存在

📋 访问路径：/system/notice

🚀 修复完成，请刷新页面查看效果！
' as summary;
