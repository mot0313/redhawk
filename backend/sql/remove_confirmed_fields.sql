-- 移除确认功能相关字段
-- 恢复alert_status字段注释为原始状态
COMMENT ON COLUMN alert_info.alert_status IS '告警状态，active活跃告警/resolved已解决告警，用于业务流程管理';

-- 移除确认相关字段
ALTER TABLE alert_info DROP COLUMN IF EXISTS confirmed_by;
ALTER TABLE alert_info DROP COLUMN IF EXISTS confirmed_time;
ALTER TABLE alert_info DROP COLUMN IF EXISTS confirmed_note;

-- 保留解决相关字段（这些是需要的）
-- resolved_by 和 resolved_note 字段保留 