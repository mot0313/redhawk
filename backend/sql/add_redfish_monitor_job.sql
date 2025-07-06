-- 添加Redfish监控定时任务到数据库
-- 这样可以通过Web界面管理任务

INSERT INTO sys_job (
    job_id,
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
    1001,  -- 任务ID
    'Redfish设备监控任务',  -- 任务名称
    'default',  -- 任务组名
    'default',  -- 任务执行器
    'module_task.redfish_monitor_tasks.RedfishSchedulerTasks.execute_device_monitor_task',  -- 调用目标
    '',  -- 位置参数 (无)
    '{}',  -- 关键字参数 (无)
    '0 */5 * * * *',  -- Cron表达式: 每5分钟执行一次
    '3',  -- 错过执行策略: 3=放弃执行
    '1',  -- 是否并发: 1=禁止并发
    '0',  -- 状态: 0=正常, 1=暂停
    'system',  -- 创建者
    NOW(),  -- 创建时间
    'system',  -- 更新者  
    NOW(),  -- 更新时间
    'Redfish设备健康监控定时任务，每5分钟检查一次所有启用监控的设备'  -- 备注
)
ON DUPLICATE KEY UPDATE
    job_name = VALUES(job_name),
    cron_expression = VALUES(cron_expression),
    update_time = NOW(),
    remark = VALUES(remark);

-- 查询验证任务是否添加成功
SELECT 
    job_id,
    job_name,
    job_group,
    invoke_target,
    cron_expression,
    status,
    create_time
FROM sys_job 
WHERE job_id = 1001; 