-- 为redfish_alert_log表添加未处理日志相关字段
-- 执行时间：2024年
-- PostgreSQL版本

-- 添加处理状态字段
ALTER TABLE redfish_alert_log 
ADD COLUMN processed_status VARCHAR(20) DEFAULT 'unprocessed';

-- 添加字段注释
COMMENT ON COLUMN redfish_alert_log.processed_status IS '处理状态（unprocessed未处理/processed已处理/ignored已忽略）';

-- 添加Redfish原始日志ID字段
ALTER TABLE redfish_alert_log 
ADD COLUMN redfish_log_id VARCHAR(100);

-- 添加字段注释
COMMENT ON COLUMN redfish_alert_log.redfish_log_id IS 'Redfish原始日志ID';

-- 添加日志内容哈希值字段（用于去重）
ALTER TABLE redfish_alert_log 
ADD COLUMN log_hash VARCHAR(64);

-- 添加字段注释
COMMENT ON COLUMN redfish_alert_log.log_hash IS '日志内容哈希值（用于去重）';

-- 为processed_status字段创建索引以优化查询性能
CREATE INDEX idx_redfish_alert_log_processed_status ON redfish_alert_log(processed_status);

-- 为log_hash字段创建索引以优化去重查询
CREATE INDEX idx_redfish_alert_log_hash ON redfish_alert_log(log_hash);

-- 为redfish_log_id字段创建索引
CREATE INDEX idx_redfish_alert_log_redfish_id ON redfish_alert_log(redfish_log_id);

-- 将现有日志标记为已处理（因为它们是通过状态分析生成的）
UPDATE redfish_alert_log 
SET processed_status = 'processed' 
WHERE processed_status IS NULL OR processed_status = 'unprocessed';

-- 验证迁移结果
SELECT 
    COUNT(*) as total_logs,
    processed_status,
    COUNT(*) as count_by_status
FROM redfish_alert_log 
GROUP BY processed_status;

COMMIT; 