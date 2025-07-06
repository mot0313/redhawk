-- 添加Redfish日志获取定时任务到sys_job表（重构版）
-- 专注于获取Management Processor Log和System Log
-- 基于现有APScheduler架构，通过数据库配置管理

-- 首先删除可能存在的旧任务
DELETE FROM sys_job WHERE job_name LIKE '%Redfish日志获取任务%';

-- 插入重构后的Redfish日志获取任务
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
    'Redfish日志获取任务（重构版）',
    'redfish',
    'default',
    'module_task.redfish_log_tasks.redfish_log_fetch_job',
    '',
    '{"max_entries": 50, "log_types": ["sel", "mel"], "enable_deduplication": true, "incremental_fetch": true}',
    '0 */10 * * * *',  -- 每10分钟执行一次
    '3',  -- 错过执行则放弃
    '1',  -- 禁止并发执行
    '0',  -- 启用状态
    'admin',
    NOW(),
    '基于重构后的架构，专注获取Redfish SEL/MEL原始日志，支持去重和增量获取。移除了设备健康分析日志生成。'
);

-- 检查插入结果
SELECT 
    job_id,
    job_name,
    job_group,
    invoke_target,
    job_kwargs,
    cron_expression,
    status,
    remark
FROM sys_job 
WHERE job_name LIKE '%Redfish日志获取任务%'
ORDER BY create_time DESC;

-- 显示任务配置说明
SELECT 
    'Task Configuration' as info_type,
    'SEL (System Event Log) + MEL (Management Event Log)' as log_types,
    'Every 10 minutes' as frequency,
    'Hash-based deduplication + Incremental fetch' as features,
    'unprocessed status for all new logs' as initial_status;

-- 使用说明：
-- 1. 执行此SQL脚本后，系统会自动注册Redfish日志获取定时任务
-- 2. 任务默认每10分钟执行一次，可以通过修改cron_expression调整频率
-- 3. 可以通过前端"系统管理 > 定时任务"界面管理此任务
-- 4. 任务参数说明：
--    - max_entries: 每台设备最大获取条目数 (默认50)
--    - log_types: 日志类型 ("sel", "mel") (默认"sel"和"mel")
--    - enable_deduplication: 是否启用去重 (默认true)
--    - incremental_fetch: 是否启用增量获取 (默认true)
-- 5. 如需修改参数，更新job_kwargs字段的JSON值
-- 6. 如需暂停任务，将status字段设为'1'
-- 7. 任务执行日志会自动记录到sys_job_log表中

-- 常用cron表达式示例：
-- '0 */5 * * * *'   - 每5分钟执行一次
-- '0 */10 * * * *'  - 每10分钟执行一次 (推荐)
-- '0 */15 * * * *'  - 每15分钟执行一次
-- '0 0 */1 * * *'   - 每小时执行一次
-- '0 0 8 * * *'     - 每天上午8点执行 