-- ======================================================
-- 添加Redfish设备监控定时任务到sys_job表
-- 该脚本会添加三个监控相关的任务配置
-- ======================================================

-- 删除已存在的Redfish监控任务（如果有）
DELETE FROM sys_job WHERE job_name LIKE '%设备%监控%' OR job_name LIKE '%redfish%' OR job_name LIKE '%Redfish%';

-- 1. 设备健康监控任务（同步版本） - 每5分钟执行一次
INSERT INTO sys_job (
    job_name, 
    job_group, 
    job_executor, 
    invoke_target, 
    job_args, 
    job_kwargs,
    cron_expression, 
    misfire_policy, 
    concurrent, 
    status, 
    create_by, 
    create_time,
    update_by,
    update_time,
    remark
) VALUES (
    '设备健康监控任务',
    'default',
    'default',
    'module_task.redfish_monitor_tasks.redfish_device_monitor_job',
    '',
    '',
    '0 */5 * * * *',  -- 每5分钟执行一次
    '3',              -- 错过执行则放弃
    '1',              -- 禁止并发执行
    '0',              -- 启用状态
    'admin',
    NOW(),
    'admin',
    NOW(),
    '定期监控Redfish设备健康状态，支持1000台设备。通过Celery异步处理，结果推送到WebSocket。'
);

-- 2. 设备健康监控任务（异步版本） - 备用方案
INSERT INTO sys_job (
    job_name, 
    job_group, 
    job_executor, 
    invoke_target, 
    job_args, 
    job_kwargs,
    cron_expression, 
    misfire_policy, 
    concurrent, 
    status, 
    create_by, 
    create_time,
    update_by,
    update_time,
    remark
) VALUES (
    '设备健康监控任务（异步）',
    'default',
    'default',
    'module_task.redfish_monitor_tasks.async_redfish_device_monitor_job',
    '',
    '',
    '0 */5 * * * *',  -- 每5分钟执行一次
    '3',              -- 错过执行则放弃
    '1',              -- 禁止并发执行
    '1',              -- 默认暂停，作为备用方案
    'admin',
    NOW(),
    'admin',
    NOW(),
    '异步版本的设备健康监控任务，可作为同步版本的备用方案。'
);

-- 3. 手动触发设备监控任务 - 用于测试和紧急检查
INSERT INTO sys_job (
    job_name, 
    job_group, 
    job_executor, 
    invoke_target, 
    job_args, 
    job_kwargs,
    cron_expression, 
    misfire_policy, 
    concurrent, 
    status, 
    create_by, 
    create_time,
    update_by,
    update_time,
    remark
) VALUES (
    '手动触发设备监控',
    'default',
    'default',
    'module_task.redfish_monitor_tasks.manual_trigger_monitor_job',
    '',
    '{}',             -- 空的JSON对象，可以传递user_id等参数
    '',               -- 手动触发，无需cron表达式
    '1',              -- 立即执行
    '0',              -- 允许并发
    '1',              -- 默认暂停，需要时手动触发
    'admin',
    NOW(),
    'admin',
    NOW(),
    '手动触发设备监控任务，用于测试或紧急检查。可通过定时任务管理界面手动执行。'
);

-- 4. 快速测试任务 - 每分钟执行一次（用于开发测试）
INSERT INTO sys_job (
    job_name, 
    job_group, 
    job_executor, 
    invoke_target, 
    job_args, 
    job_kwargs,
    cron_expression, 
    misfire_policy, 
    concurrent, 
    status, 
    create_by, 
    create_time,
    update_by,
    update_time,
    remark
) VALUES (
    '设备监控测试任务',
    'default',
    'default',
    'module_task.redfish_monitor_tasks.redfish_device_monitor_job',
    '',
    '{"test_mode": true}',  -- 测试模式参数
    '0 * * * * *',          -- 每分钟执行一次
    '3',                    -- 错过执行则放弃
    '1',                    -- 禁止并发执行
    '1',                    -- 默认暂停，测试时启用
    'admin',
    NOW(),
    'admin',
    NOW(),
    '每分钟执行的测试任务，用于开发和调试。生产环境请保持暂停状态。'
);

-- 查询结果确认
SELECT 
    job_id,
    job_name,
    job_group,
    invoke_target,
    cron_expression,
    status,
    remark
FROM sys_job 
WHERE job_name LIKE '%设备%监控%' OR job_name LIKE '%redfish%' OR job_name LIKE '%Redfish%'
ORDER BY job_id;

-- ======================================================
-- 使用说明：
-- 1. 执行此脚本后，系统重启时会自动加载这些定时任务
-- 2. 可通过前端 /monitor/job 页面管理这些任务
-- 3. 主要使用 "设备健康监控任务"，其他任务作为备用
-- 4. 可以随时通过界面修改cron表达式调整执行频率
-- 5. 测试任务默认暂停，需要时可手动启用
-- ======================================================

-- 高级配置示例：
-- 如果需要分组监控不同类型的设备，可以添加参数：

-- 示例：监控特定设备组
/*
INSERT INTO sys_job (
    job_name, 
    job_group, 
    job_executor, 
    invoke_target, 
    job_args, 
    job_kwargs,
    cron_expression, 
    misfire_policy, 
    concurrent, 
    status, 
    create_by, 
    create_time,
    remark
) VALUES (
    '核心设备监控',
    'default',
    'default',
    'module_task.redfish_monitor_tasks.redfish_device_monitor_job',
    '',
    '{"device_group": "core", "priority": "high"}',
    '0 */2 * * * *',  -- 每2分钟执行一次（高频率）
    '3',
    '1',
    '0',
    'admin',
    NOW(),
    '监控核心业务设备，执行频率更高'
);
*/ 