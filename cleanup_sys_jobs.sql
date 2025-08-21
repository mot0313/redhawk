-- 清理sys_job表中的冗余和无效任务
-- 执行时间：修复ImportError后的清理操作

-- 删除已不存在的异步监控任务（函数已删除）
DELETE FROM sys_job 
WHERE job_name = '设备健康监控任务（异步）' 
  AND invoke_target = 'module_task.redfish_monitor_tasks.async_redfish_device_monitor_job';

-- 删除测试任务（每分钟执行太频繁，不适合生产环境）
DELETE FROM sys_job 
WHERE job_name = '设备监控测试任务' 
  AND cron_expression = '0 * * * * *';

-- 更新主监控任务的备注，说明现在包含硬件+宕机检测
UPDATE sys_job 
SET remark = '设备监控任务每5分钟执行一次（包含硬件健康+宕机检测）',
    update_time = NOW()
WHERE job_name = '设备健康监控任务' 
  AND invoke_target = 'module_task.redfish_monitor_tasks.redfish_device_monitor_job';

-- 查询清理后的任务列表
SELECT job_id, job_name, job_group, invoke_target, cron_expression, status, remark 
FROM sys_job 
ORDER BY job_name;
