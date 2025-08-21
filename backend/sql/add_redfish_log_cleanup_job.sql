-- ----------------------------
-- 添加Redfish日志清理定时任务到sys_job表
-- ----------------------------

-- 检查是否已存在日志清理任务
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
