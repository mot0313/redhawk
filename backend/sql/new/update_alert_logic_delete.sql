-- 1. 为 alert_info 表添加 del_flag 字段，用于逻辑删除
ALTER TABLE alert_info ADD COLUMN del_flag SMALLINT DEFAULT 0;
COMMENT ON COLUMN alert_info.del_flag IS '删除标志（0代表存在 2代表删除）';

-- 2. 移除外键上的 ON DELETE CASCADE 规则
-- 首先删除现有的约束
ALTER TABLE alert_info DROP CONSTRAINT IF EXISTS alert_info_device_id_fkey;

-- 然后重新添加约束，但不包含 ON DELETE CASCADE
ALTER TABLE alert_info
ADD CONSTRAINT alert_info_device_id_fkey
FOREIGN KEY (device_id)
REFERENCES device_info(device_id); 