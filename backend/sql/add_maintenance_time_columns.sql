-- ===========================
-- 为alert_info表添加维修时间相关字段
-- 支持告警组件维修时间计划功能
-- 创建时间: 2024-12
-- ===========================

-- 添加维修时间相关字段
ALTER TABLE alert_info 
ADD COLUMN IF NOT EXISTS scheduled_maintenance_time timestamp(0),     -- 计划维修时间
ADD COLUMN IF NOT EXISTS maintenance_window_start timestamp(0),       -- 维修窗口开始时间
ADD COLUMN IF NOT EXISTS maintenance_window_end timestamp(0),         -- 维修窗口结束时间
ADD COLUMN IF NOT EXISTS maintenance_description text,                -- 维修描述
ADD COLUMN IF NOT EXISTS maintenance_assigned_to varchar(100),        -- 维修负责人
ADD COLUMN IF NOT EXISTS maintenance_status varchar(20) DEFAULT 'none', -- 维修状态：none未安排/planned已计划/in_progress进行中/completed已完成/cancelled已取消
ADD COLUMN IF NOT EXISTS maintenance_priority varchar(20) DEFAULT 'normal', -- 维修优先级：low低/normal正常/high高/urgent紧急
ADD COLUMN IF NOT EXISTS maintenance_notes text,                      -- 维修备注
ADD COLUMN IF NOT EXISTS maintenance_created_by varchar(100),         -- 维修计划创建人
ADD COLUMN IF NOT EXISTS maintenance_created_time timestamp(0),       -- 维修计划创建时间
ADD COLUMN IF NOT EXISTS maintenance_updated_by varchar(100),         -- 维修计划更新人
ADD COLUMN IF NOT EXISTS maintenance_updated_time timestamp(0);       -- 维修计划更新时间

-- 添加字段注释
COMMENT ON COLUMN alert_info.scheduled_maintenance_time IS '计划维修时间，告警组件的预定维修时间';
COMMENT ON COLUMN alert_info.maintenance_window_start IS '维修窗口开始时间，维修操作的起始时间';
COMMENT ON COLUMN alert_info.maintenance_window_end IS '维修窗口结束时间，维修操作的结束时间';
COMMENT ON COLUMN alert_info.maintenance_description IS '维修描述，详细的维修内容和步骤说明';
COMMENT ON COLUMN alert_info.maintenance_assigned_to IS '维修负责人，负责执行维修的工程师或团队';
COMMENT ON COLUMN alert_info.maintenance_status IS '维修状态：none未安排/planned已计划/in_progress进行中/completed已完成/cancelled已取消';
COMMENT ON COLUMN alert_info.maintenance_priority IS '维修优先级：low低/normal正常/high高/urgent紧急';
COMMENT ON COLUMN alert_info.maintenance_notes IS '维修备注，额外的注意事项和说明';
COMMENT ON COLUMN alert_info.maintenance_created_by IS '维修计划创建人，记录谁创建了维修计划';
COMMENT ON COLUMN alert_info.maintenance_created_time IS '维修计划创建时间，记录维修计划的创建时间';
COMMENT ON COLUMN alert_info.maintenance_updated_by IS '维修计划更新人，记录谁最后更新了维修计划';
COMMENT ON COLUMN alert_info.maintenance_updated_time IS '维修计划更新时间，记录维修计划的最后更新时间';

-- 创建维修相关索引
CREATE INDEX IF NOT EXISTS idx_alert_info_maintenance_time ON alert_info(scheduled_maintenance_time);
CREATE INDEX IF NOT EXISTS idx_alert_info_maintenance_status ON alert_info(maintenance_status);
CREATE INDEX IF NOT EXISTS idx_alert_info_maintenance_priority ON alert_info(maintenance_priority);
CREATE INDEX IF NOT EXISTS idx_alert_info_maintenance_assigned ON alert_info(maintenance_assigned_to);
CREATE INDEX IF NOT EXISTS idx_alert_info_maintenance_window ON alert_info(maintenance_window_start, maintenance_window_end);

-- 创建维修计划更新触发器
CREATE OR REPLACE FUNCTION update_maintenance_updated_time()
RETURNS TRIGGER AS $$
BEGIN
    -- 如果维修相关字段有更新，自动设置更新时间
    IF (NEW.scheduled_maintenance_time IS DISTINCT FROM OLD.scheduled_maintenance_time) OR
       (NEW.maintenance_window_start IS DISTINCT FROM OLD.maintenance_window_start) OR
       (NEW.maintenance_window_end IS DISTINCT FROM OLD.maintenance_window_end) OR
       (NEW.maintenance_description IS DISTINCT FROM OLD.maintenance_description) OR
       (NEW.maintenance_assigned_to IS DISTINCT FROM OLD.maintenance_assigned_to) OR
       (NEW.maintenance_status IS DISTINCT FROM OLD.maintenance_status) OR
       (NEW.maintenance_priority IS DISTINCT FROM OLD.maintenance_priority) OR
       (NEW.maintenance_notes IS DISTINCT FROM OLD.maintenance_notes) THEN
        
        NEW.maintenance_updated_time = CURRENT_TIMESTAMP;
        
        -- 如果是首次设置维修计划，也设置创建时间
        IF OLD.maintenance_status = 'none' AND NEW.maintenance_status != 'none' AND NEW.maintenance_created_time IS NULL THEN
            NEW.maintenance_created_time = CURRENT_TIMESTAMP;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER IF NOT EXISTS trigger_maintenance_update_time
    BEFORE UPDATE ON alert_info
    FOR EACH ROW
    EXECUTE FUNCTION update_maintenance_updated_time();

-- 验证字段添加成功
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'alert_info' 
    AND column_name LIKE '%maintenance%'
ORDER BY ordinal_position;

-- 输出成功信息
SELECT '维修时间相关字段添加成功！' as 状态; 