-- 修复临时日志查看页面的设备列表权限问题
-- 为admin角色添加设备列表权限

DO $$
DECLARE
    device_list_menu_id INTEGER;
BEGIN
    -- 查找设备列表权限的menu_id
    SELECT menu_id INTO device_list_menu_id FROM sys_menu WHERE perms = 'redfish:device:list' LIMIT 1;
    
    IF device_list_menu_id IS NOT NULL THEN
        -- 为admin角色添加设备列表权限（如果还没有）
        INSERT INTO sys_role_menu (role_id, menu_id) VALUES (1, device_list_menu_id)
        ON CONFLICT (role_id, menu_id) DO NOTHING;
        RAISE NOTICE '已为admin角色添加设备列表权限，menu_id: %', device_list_menu_id;
    ELSE
        RAISE NOTICE '警告：未找到设备列表权限(redfish:device:list)';
    END IF;
    
    -- 验证权限
    IF EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND menu_id = device_list_menu_id) THEN
        RAISE NOTICE '✓ 权限验证成功：admin角色已拥有设备列表权限';
    ELSE
        RAISE NOTICE '✗ 权限验证失败：admin角色缺少设备列表权限';
    END IF;
END $$;

-- 查看相关权限信息
SELECT 
    m.menu_id,
    m.menu_name,
    m.perms,
    rm.role_id,
    r.role_name
FROM sys_menu m
LEFT JOIN sys_role_menu rm ON m.menu_id = rm.menu_id
LEFT JOIN sys_role r ON rm.role_id = r.role_id
WHERE m.perms = 'redfish:device:list'
ORDER BY rm.role_id;
