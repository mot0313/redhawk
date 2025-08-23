-- ----------------------------
-- 更新Redfish日志管理为双视图结构
-- 日志管理
-- ├── 临时查看
-- └── 历史管理
-- ----------------------------

DO $$
BEGIN
    -- 1. 更新原有的日志管理菜单为父级菜单
    UPDATE sys_menu SET 
        component = '',
        menu_type = 'M',
        perms = '',
        remark = 'Redfish日志管理父级菜单'
    WHERE menu_id = 2002 AND menu_name = '日志管理';
    
    RAISE NOTICE '已更新日志管理为父级菜单';
    
    -- 2. 添加临时查看子菜单
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_name = '临时查看' AND parent_id = 2002) THEN
        INSERT INTO sys_menu VALUES(
            20025, 
            '临时查看', 
            2002, 
            1, 
            'temp', 
            'redfish/log/temp', 
            '', 
            '', 
            1, 
            0, 
            'C', 
            '0', 
            '0', 
            'redfish:log:temp', 
            'eye-open', 
            'admin', 
            current_timestamp, 
            '', 
            null, 
            '临时日志查看页面'
        );
        RAISE NOTICE '已添加临时查看子菜单';
    ELSE
        RAISE NOTICE '临时查看子菜单已存在，跳过添加';
    END IF;
    
    -- 3. 添加历史管理子菜单
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_name = '历史管理' AND parent_id = 2002) THEN
        INSERT INTO sys_menu VALUES(
            20026, 
            '历史管理', 
            2002, 
            2, 
            'history', 
            'redfish/log/index', 
            '', 
            '', 
            1, 
            0, 
            'C', 
            '0', 
            '0', 
            'redfish:log:history', 
            'log', 
            'admin', 
            current_timestamp, 
            '', 
            null, 
            '历史日志管理页面'
        );
        RAISE NOTICE '已添加历史管理子菜单';
    ELSE
        RAISE NOTICE '历史管理子菜单已存在，跳过添加';
    END IF;
    
    -- 4. 添加临时查看相关权限
    -- 临时日志查看权限
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'redfish:log:temp:view') THEN
        INSERT INTO sys_menu VALUES(
            200250, 
            '临时查看权限', 
            20025, 
            1, 
            '', 
            '', 
            '', 
            '', 
            1, 
            0, 
            'F', 
            '0', 
            '0', 
            'redfish:log:temp:view', 
            '#', 
            'admin', 
            current_timestamp, 
            '', 
            null, 
            ''
        );
        RAISE NOTICE '已添加临时查看权限';
    END IF;
    
    -- 临时日志收集权限
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'redfish:log:temp:collect') THEN
        INSERT INTO sys_menu VALUES(
            200251, 
            '临时收集权限', 
            20025, 
            2, 
            '', 
            '', 
            '', 
            '', 
            1, 
            0, 
            'F', 
            '0', 
            '0', 
            'redfish:log:temp:collect', 
            '#', 
            'admin', 
            current_timestamp, 
            '', 
            null, 
            ''
        );
        RAISE NOTICE '已添加临时收集权限';
    END IF;
    
    -- 临时日志导出权限
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'redfish:log:temp:export') THEN
        INSERT INTO sys_menu VALUES(
            200252, 
            '临时导出权限', 
            20025, 
            3, 
            '', 
            '', 
            '', 
            '', 
            1, 
            0, 
            'F', 
            '0', 
            '0', 
            'redfish:log:temp:export', 
            '#', 
            'admin', 
            current_timestamp, 
            '', 
            null, 
            ''
        );
        RAISE NOTICE '已添加临时导出权限';
    END IF;
    
    -- 5. 添加历史管理相关权限
    -- 历史日志查看权限
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'redfish:log:history:view') THEN
        INSERT INTO sys_menu VALUES(
            200260, 
            '历史查看权限', 
            20026, 
            1, 
            '', 
            '', 
            '', 
            '', 
            1, 
            0, 
            'F', 
            '0', 
            '0', 
            'redfish:log:history:view', 
            '#', 
            'admin', 
            current_timestamp, 
            '', 
            null, 
            ''
        );
        RAISE NOTICE '已添加历史查看权限';
    END IF;
    
    -- 更新现有权限到历史管理下
    UPDATE sys_menu SET parent_id = 20026 WHERE menu_id = 20020; -- 日志查询
    UPDATE sys_menu SET parent_id = 20026 WHERE menu_id = 20021; -- 日志收集
    UPDATE sys_menu SET parent_id = 20026 WHERE menu_id = 20022; -- 日志导出
    UPDATE sys_menu SET parent_id = 20026 WHERE menu_id = 20023; -- 日志删除
    
    RAISE NOTICE '已将现有权限移动到历史管理下';
    
    -- 6. 确保设备列表权限存在（临时查看需要）
    -- 查找设备列表权限的menu_id
    DO $device_perm$
    DECLARE
        device_list_menu_id INTEGER;
    BEGIN
        SELECT menu_id INTO device_list_menu_id FROM sys_menu WHERE perms = 'redfish:device:list' LIMIT 1;
        
        IF device_list_menu_id IS NOT NULL THEN
            -- 为admin角色添加设备列表权限（如果还没有）
            INSERT INTO sys_role_menu (role_id, menu_id) VALUES (1, device_list_menu_id)
            ON CONFLICT (role_id, menu_id) DO NOTHING;
            RAISE NOTICE '已确保admin角色拥有设备列表权限';
        ELSE
            RAISE NOTICE '警告：未找到设备列表权限，可能需要手动配置';
        END IF;
    END $device_perm$;
    
    -- 7. 更新角色权限，确保admin角色拥有所有权限
    INSERT INTO sys_role_menu (role_id, menu_id) 
    SELECT 1, menu_id FROM sys_menu WHERE menu_id IN (20025, 20026, 200250, 200251, 200252, 200260)
    ON CONFLICT (role_id, menu_id) DO NOTHING;
    
    RAISE NOTICE '已为admin角色添加新权限';
    
END $$;

-- 验证菜单结构
SELECT 
    m.menu_id,
    m.menu_name,
    m.parent_id,
    p.menu_name as parent_name,
    m.order_num,
    m.path,
    m.component,
    m.menu_type,
    m.perms,
    m.icon
FROM sys_menu m
LEFT JOIN sys_menu p ON m.parent_id = p.menu_id
WHERE m.menu_id = 2002 OR m.parent_id = 2002 OR m.parent_id IN (20025, 20026)
ORDER BY m.parent_id, m.order_num;
