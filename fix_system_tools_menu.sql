-- 🔧 修复系统工具菜单显示问题
-- 恢复系统接口(Swagger)和表单构建菜单

BEGIN;

-- ==========================================
-- 第一步：检查当前系统工具菜单状态
-- ==========================================

-- 查看当前系统工具下的子菜单
SELECT '=== 当前系统工具菜单 ===' as info;
SELECT 
    m.menu_id,
    m.menu_name,
    m.parent_id,
    m.path,
    m.component,
    m.perms,
    m.menu_type,
    CASE WHEN m.visible = '0' THEN '显示' ELSE '隐藏' END as visibility,
    CASE WHEN m.status = '0' THEN '正常' ELSE '停用' END as status,
    CASE WHEN rm.role_id IS NOT NULL THEN '✅ 已分配' ELSE '❌ 未分配' END as common_user_access
FROM sys_menu m
LEFT JOIN sys_role_menu rm ON m.menu_id = rm.menu_id AND rm.role_id = 2
WHERE m.parent_id = 3 OR m.menu_id = 3
ORDER BY m.order_num, m.menu_id;

-- ==========================================
-- 第二步：恢复缺失的系统接口和表单构建菜单
-- ==========================================

-- 恢复系统接口(Swagger)菜单
INSERT INTO sys_menu (
    menu_id, menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
) VALUES 
(117, '系统接口', 3, 2, 'swagger', 'tool/swagger/index', null, '',
 1, 0, 'C', '0', '0', 'tool:swagger:list', 'swagger',
 'admin', current_timestamp, 'admin', current_timestamp, 'Swagger系统接口文档'),

(118, '表单构建', 3, 3, 'build', 'tool/build/index', null, '',
 1, 0, 'C', '0', '0', 'tool:build:list', 'build',
 'admin', current_timestamp, 'admin', current_timestamp, '表单构建工具')
ON CONFLICT (menu_id) DO UPDATE SET
    menu_name = EXCLUDED.menu_name,
    parent_id = EXCLUDED.parent_id,
    order_num = EXCLUDED.order_num,
    path = EXCLUDED.path,
    component = EXCLUDED.component,
    perms = EXCLUDED.perms,
    icon = EXCLUDED.icon,
    visible = '0',
    status = '0',
    update_time = current_timestamp;

-- ==========================================
-- 第三步：为普通用户分配系统工具访问权限
-- ==========================================

-- 为普通用户分配系统工具菜单权限
INSERT INTO sys_role_menu (role_id, menu_id) VALUES 
(2, 116), -- 代码生成
(2, 117), -- 系统接口
(2, 118)  -- 表单构建
ON CONFLICT (role_id, menu_id) DO NOTHING;

-- ==========================================
-- 第四步：调整代码生成菜单的顺序
-- ==========================================

-- 确保代码生成菜单在第一位
UPDATE sys_menu SET order_num = 1 WHERE menu_id = 116;

COMMIT;

-- ==========================================
-- 验证修复结果
-- ==========================================

SELECT '=== 修复后的系统工具菜单 ===' as info;
SELECT 
    m.menu_id,
    m.menu_name,
    m.parent_id,
    m.order_num,
    m.path,
    m.component,
    m.perms,
    m.menu_type,
    CASE WHEN m.visible = '0' THEN '显示' ELSE '隐藏' END as visibility,
    CASE WHEN m.status = '0' THEN '正常' ELSE '停用' END as status,
    CASE WHEN rm.role_id IS NOT NULL THEN '✅ 已分配' ELSE '❌ 未分配' END as common_user_access
FROM sys_menu m
LEFT JOIN sys_role_menu rm ON m.menu_id = rm.menu_id AND rm.role_id = 2
WHERE m.parent_id = 3 OR m.menu_id = 3
ORDER BY m.order_num, m.menu_id;

-- 检查普通用户权限分配
SELECT '=== 普通用户工具权限 ===' as info;
SELECT 
    m.menu_name,
    m.perms,
    'YES' as has_permission
FROM sys_menu m
INNER JOIN sys_role_menu rm ON m.menu_id = rm.menu_id
WHERE rm.role_id = 2 AND m.parent_id = 3
ORDER BY m.order_num;

SELECT '
🎉 系统工具菜单修复完成！

✅ 恢复的菜单：
   - 代码生成 (116) - tool/gen/index
   - 系统接口 (117) - tool/swagger/index  
   - 表单构建 (118) - tool/build/index

✅ 普通用户权限：
   - 已分配所有系统工具访问权限
   - 可以正常访问代码生成、系统接口、表单构建

⚠️  注意：
   - 系统接口需要后端Swagger文档支持
   - 表单构建需要相应的前端组件
   - 如果前端组件不存在，可能需要额外开发

🚀 修复后请重启应用清除缓存
' as summary;
