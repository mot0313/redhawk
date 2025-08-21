-- ----------------------------
-- Redfish日志管理系统初始化脚本
-- 包含：数据库表、菜单权限、定时任务
-- ----------------------------

-- 1. 创建Redfish日志表
DROP TABLE IF EXISTS redfish_log;
CREATE TABLE redfish_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id INTEGER NOT NULL,
    device_ip VARCHAR(45) NOT NULL,
    entry_id VARCHAR(100),
    entry_type VARCHAR(50),
    log_source VARCHAR(10) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    created_time TIMESTAMP NOT NULL,
    collected_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    message TEXT,
    message_id VARCHAR(100),
    sensor_type VARCHAR(50),
    sensor_number INTEGER,
    create_by VARCHAR(50),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_by VARCHAR(50),
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    remark VARCHAR(500)
);

-- 创建索引以提高查询性能
CREATE INDEX idx_redfish_log_device_id ON redfish_log (device_id);
CREATE INDEX idx_redfish_log_device_ip ON redfish_log (device_ip);
CREATE INDEX idx_redfish_log_severity ON redfish_log (severity);
CREATE INDEX idx_redfish_log_created_time ON redfish_log (created_time);
CREATE INDEX idx_redfish_log_collected_time ON redfish_log (collected_time);
CREATE INDEX idx_redfish_log_source ON redfish_log (log_source);
CREATE INDEX idx_redfish_log_device_time ON redfish_log (device_id, created_time);

-- 添加表注释
COMMENT ON TABLE redfish_log IS 'Redfish设备日志表';
COMMENT ON COLUMN redfish_log.log_id IS '日志ID';
COMMENT ON COLUMN redfish_log.device_id IS '设备ID';
COMMENT ON COLUMN redfish_log.device_ip IS '设备IP地址';
COMMENT ON COLUMN redfish_log.entry_id IS '原始条目ID';
COMMENT ON COLUMN redfish_log.entry_type IS '条目类型';
COMMENT ON COLUMN redfish_log.log_source IS '日志来源(SEL/MEL)';
COMMENT ON COLUMN redfish_log.severity IS '严重程度(CRITICAL/WARNING)';
COMMENT ON COLUMN redfish_log.created_time IS '日志创建时间';
COMMENT ON COLUMN redfish_log.collected_time IS '日志收集时间';
COMMENT ON COLUMN redfish_log.message IS '日志消息';
COMMENT ON COLUMN redfish_log.message_id IS '消息ID';
COMMENT ON COLUMN redfish_log.sensor_type IS '传感器类型';
COMMENT ON COLUMN redfish_log.sensor_number IS '传感器编号';
COMMENT ON COLUMN redfish_log.create_by IS '创建者';
COMMENT ON COLUMN redfish_log.create_time IS '创建时间';
COMMENT ON COLUMN redfish_log.update_by IS '更新者';
COMMENT ON COLUMN redfish_log.update_time IS '更新时间';
COMMENT ON COLUMN redfish_log.remark IS '备注';

-- 2. 添加菜单和权限
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
    END IF;

    -- 添加日志管理相关按钮权限
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'redfish:log:query') THEN
        INSERT INTO sys_menu VALUES(20020, '日志查询', 2002, 1, '', '', '', '', 1, 0, 'F', '0', '0', 'redfish:log:query', '#', 'admin', current_timestamp, '', null, '');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'redfish:log:collect') THEN
        INSERT INTO sys_menu VALUES(20021, '日志收集', 2002, 2, '', '', '', '', 1, 0, 'F', '0', '0', 'redfish:log:collect', '#', 'admin', current_timestamp, '', null, '');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'redfish:log:export') THEN
        INSERT INTO sys_menu VALUES(20022, '日志导出', 2002, 3, '', '', '', '', 1, 0, 'F', '0', '0', 'redfish:log:export', '#', 'admin', current_timestamp, '', null, '');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'redfish:log:remove') THEN
        INSERT INTO sys_menu VALUES(20023, '日志删除', 2002, 4, '', '', '', '', 1, 0, 'F', '0', '0', 'redfish:log:remove', '#', 'admin', current_timestamp, '', null, '');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'redfish:log:cleanup') THEN
        INSERT INTO sys_menu VALUES(20024, '日志清理', 2002, 5, '', '', '', '', 1, 0, 'F', '0', '0', 'redfish:log:cleanup', '#', 'admin', current_timestamp, '', null, '');
    END IF;

    RAISE NOTICE '日志管理菜单和权限添加完成';
END $$;

-- 3. 添加定时任务
DO $$
BEGIN
    -- 添加Redfish日志清理定时任务
    IF NOT EXISTS (SELECT 1 FROM sys_job WHERE job_name = 'Redfish日志清理任务') THEN
        INSERT INTO sys_job (
            job_name,
            job_group,
            invoke_target,
            cron_expression,
            misfire_policy,
            concurrent,
            status,
            create_by,
            create_time,
            remark
        ) VALUES (
            'Redfish日志清理任务',
            'default',
            'module_task.redfish_monitor_tasks.redfish_log_cleanup_job',
            '0 0 2 * * *',  -- 每天凌晨2点执行
            '2',            -- 忽略
            '0',            -- 不允许并发
            '1',            -- 暂停状态，需要手动启用
            'admin',
            CURRENT_TIMESTAMP,
            '自动清理30天前的Redfish日志记录，轻量版设计每日执行'
        );
        RAISE NOTICE '已添加Redfish日志清理定时任务到sys_job表';
    ELSE
        RAISE NOTICE 'Redfish日志清理任务已存在，跳过添加';
    END IF;
END $$;

-- 4. 完成提示
SELECT 
    'Redfish日志管理系统初始化完成' as status,
    '包含：数据库表、菜单权限、定时任务' as description,
    '请在系统管理-定时任务中启用"Redfish日志清理任务"' as note;
