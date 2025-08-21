-- ----------------------------
-- 添加Redfish日志管理菜单
-- ----------------------------

-- 检查是否已存在日志管理菜单
DO $$
BEGIN
    -- 添加日志管理子菜单（在设备管理下）
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_name = '日志管理' AND parent_id = 2000) THEN
        INSERT INTO sys_menu VALUES(
            2002, 
            '日志管理', 
            2000, 
            3, 
            'log', 
            'redfish/log/index', 
            '', 
            '', 
            1, 
            0, 
            'C', 
            '0', 
            '0', 
            'redfish:log:list', 
            'log', 
            'admin', 
            current_timestamp, 
            '', 
            null, 
            'Redfish日志管理菜单'
        );
        RAISE NOTICE '已添加日志管理菜单';
    ELSE
        RAISE NOTICE '日志管理菜单已存在，跳过添加';
    END IF;

    -- 添加日志管理相关按钮权限
    -- 日志查询
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'redfish:log:query') THEN
        INSERT INTO sys_menu VALUES(
            20020, 
            '日志查询', 
            2002, 
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
            'redfish:log:query', 
            '#', 
            'admin', 
            current_timestamp, 
            '', 
            null, 
            ''
        );
        RAISE NOTICE '已添加日志查询权限';
    END IF;

    -- 日志收集
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'redfish:log:collect') THEN
        INSERT INTO sys_menu VALUES(
            20021, 
            '日志收集', 
            2002, 
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
            'redfish:log:collect', 
            '#', 
            'admin', 
            current_timestamp, 
            '', 
            null, 
            ''
        );
        RAISE NOTICE '已添加日志收集权限';
    END IF;

    -- 日志导出
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'redfish:log:export') THEN
        INSERT INTO sys_menu VALUES(
            20022, 
            '日志导出', 
            2002, 
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
            'redfish:log:export', 
            '#', 
            'admin', 
            current_timestamp, 
            '', 
            null, 
            ''
        );
        RAISE NOTICE '已添加日志导出权限';
    END IF;

    -- 日志删除
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'redfish:log:remove') THEN
        INSERT INTO sys_menu VALUES(
            20023, 
            '日志删除', 
            2002, 
            4, 
            '', 
            '', 
            '', 
            '', 
            1, 
            0, 
            'F', 
            '0', 
            '0', 
            'redfish:log:remove', 
            '#', 
            'admin', 
            current_timestamp, 
            '', 
            null, 
            ''
        );
        RAISE NOTICE '已添加日志删除权限';
    END IF;

    -- 日志清理
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'redfish:log:cleanup') THEN
        INSERT INTO sys_menu VALUES(
            20024, 
            '日志清理', 
            2002, 
            5, 
            '', 
            '', 
            '', 
            '', 
            1, 
            0, 
            'F', 
            '0', 
            '0', 
            'redfish:log:cleanup', 
            '#', 
            'admin', 
            current_timestamp, 
            '', 
            null, 
            ''
        );
        RAISE NOTICE '已添加日志清理权限';
    END IF;

    RAISE NOTICE 'Redfish日志管理菜单和权限添加完成';
END $$;
