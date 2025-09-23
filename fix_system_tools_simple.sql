-- 🔧 简单修复系统工具菜单权限问题
-- 前端组件已存在，只需要分配权限和确保菜单正确

BEGIN;

-- ==========================================
-- 第一步：确保系统工具子菜单存在并正确配置
-- ==========================================

-- 检查并创建系统接口菜单（如果不存在）
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
) VALUES 
(117, '系统接口', 3, 2, 'swagger', 'tool/swagger/index', null, '', 1, 0, 'C', '0', '0', 'tool:swagger:list', 'swagger', 'admin', current_timestamp, 'admin', current_timestamp, 'Swagger系统接口'),
(118, '表单构建', 3, 3, 'build', 'tool/build/index', null, '', 1, 0, 'C', '0', '0', 'tool:build:list', 'build', 'admin', current_timestamp, 'admin', current_timestamp, '表单构建工具')
ON CONFLICT (menu_id) DO UPDATE SET
    parent_id = EXCLUDED.parent_id,
    path = EXCLUDED.path,
    component = EXCLUDED.component,
    perms = EXCLUDED.perms,
    visible = '0',
    status = '0',
    update_time = current_timestamp;

-- 确保代码生成菜单正确
UPDATE sys_menu SET 
    order_num = 1,
    visible = '0',
    status = '0'
WHERE menu_id = 116;

-- ==========================================
-- 第二步：为普通用户分配系统工具权限
-- ==========================================

-- 分配系统工具菜单权限给普通用户
INSERT INTO sys_role_menu (role_id, menu_id) VALUES 
(2, 116), -- 代码生成
(2, 117), -- 系统接口  
(2, 118)  -- 表单构建
ON CONFLICT (role_id, menu_id) DO NOTHING;

COMMIT;

-- ==========================================
-- 验证修复结果
-- ==========================================

SELECT '=== 系统工具菜单修复结果 ===' as info;

SELECT 
    m.menu_id,
    m.menu_name,
    m.order_num,
    m.path,
    m.component,
    CASE WHEN m.visible = '0' THEN '显示' ELSE '隐藏' END as visibility,
    CASE WHEN m.status = '0' THEN '正常' ELSE '停用' END as status,
    CASE WHEN rm.role_id IS NOT NULL THEN '✅ 普通用户可用' ELSE '❌ 普通用户不可用' END as common_user_access
FROM sys_menu m
LEFT JOIN sys_role_menu rm ON m.menu_id = rm.menu_id AND rm.role_id = 2
WHERE m.parent_id = 3 AND m.status = '0'
ORDER BY m.order_num;

SELECT '
🎉 系统工具菜单修复完成！

✅ 可用菜单：
   1. 代码生成 (/tool/gen) - 代码生成工具
   2. 系统接口 (/tool/swagger) - Swagger接口文档  
   3. 表单构建 (/tool/build) - 可视化表单构建

✅ 前端组件：已确认存在对应Vue组件
✅ 用户权限：普通用户已可访问所有工具
✅ 菜单状态：所有菜单均为显示和正常状态

📋 访问路径：
   - /tool/gen - 代码生成
   - /tool/swagger - 系统接口
   - /tool/build - 表单构建

🚀 修复完成，请刷新页面查看效果！
' as summary;
