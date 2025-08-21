-- 添加宕机检测和清理任务到APScheduler系统
-- 需要先执行 cleanup_hardware_dict.sql 确保downtime硬件类型存在

-- 0. 清理默认的测试任务（如果存在）
DELETE FROM sys_job WHERE invoke_target = 'module_task.scheduler_test.job';

-- 1. 添加设备宕机检测任务
INSERT INTO sys_job (
    job_name, job_group, job_executor, invoke_target, 
    job_args, job_kwargs, cron_expression, misfire_policy, 
    concurrent, status, create_by, create_time, remark
) 
SELECT 
    '设备宕机检测任务', 'default', 'default', 
    'module_task.redfish_monitor_tasks.device_downtime_monitor_job',
    '', '', '0 */2 * * * *', '3', 
    '1', '0', 'system', NOW(), 
    '定期检测设备业务IP连通性，发现宕机立即告警，支持1000台设备'
WHERE NOT EXISTS (
    SELECT 1 FROM sys_job 
    WHERE job_name = '设备宕机检测任务' 
    AND invoke_target = 'module_task.redfish_monitor_tasks.device_downtime_monitor_job'
);

-- 2. 更新现有的清理任务为APScheduler版本
UPDATE sys_job 
SET invoke_target = 'module_task.redfish_monitor_tasks.cleanup_old_logs_job',
    job_group = 'default',
    remark = '定期清理超过30天的旧Redfish日志和已解决的告警（APScheduler版本）'
WHERE job_name = '清理旧日志和告警' 
AND invoke_target = 'module_redfish.celery_tasks.cleanup_old_logs';

-- 3. 如果清理任务不存在，则新增
INSERT INTO sys_job (
    job_name, job_group, job_executor, invoke_target, 
    job_args, job_kwargs, cron_expression, misfire_policy, 
    concurrent, status, create_by, create_time, remark
) 
SELECT 
    '清理旧日志和告警', 'default', 'default', 
    'module_task.redfish_monitor_tasks.cleanup_old_logs_job',
    '30', '', '0 0 2 * * *', '3', 
    '1', '0', 'system', NOW(), 
    '定期清理超过30天的旧Redfish日志和已解决的告警'
WHERE NOT EXISTS (
    SELECT 1 FROM sys_job 
    WHERE job_name = '清理旧日志和告警'
);

-- 4. 验证插入结果
SELECT 
    job_id, job_name, job_group, invoke_target, 
    cron_expression, status, create_time, remark
FROM sys_job 
WHERE job_name IN ('设备宕机检测任务', '清理旧日志和告警')
ORDER BY create_time DESC;

-- 5. 显示所有Redfish相关定时任务
SELECT 
    job_id, job_name, job_group, invoke_target, 
    cron_expression, 
    CASE status 
        WHEN '0' THEN '启用'
        WHEN '1' THEN '暂停'
        ELSE '未知'
    END as status_desc,
    create_time
FROM sys_job 
WHERE invoke_target LIKE '%redfish%' 
   OR job_name IN ('设备宕机检测任务', '清理旧日志和告警')
ORDER BY job_group, job_name;

-- 使用说明：
-- 1. 执行此SQL脚本后，定时任务会在应用重启时自动加载
-- 2. 可通过 /monitor/job 页面管理这些任务
-- 3. 设备监控任务每5分钟执行一次（包含硬件健康+宕机检测）
-- 4. 独立宕机检测任务每2分钟执行一次（仅宕机检测）
-- 5. 清理任务每天凌晨2点执行一次
-- 6. 手动触发设备监控将同时执行硬件和宕机检测
-- 7. 任务执行日志会记录在 sys_job_log 表中
