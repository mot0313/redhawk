-- 1. 删除 alert_info 表上现有的外键约束
ALTER TABLE alert_info DROP CONSTRAINT IF EXISTS alert_info_device_id_fkey;

-- 2. 重新添加外键约束，并启用 ON DELETE CASCADE
ALTER TABLE alert_info
ADD CONSTRAINT alert_info_device_id_fkey
FOREIGN KEY (device_id)
REFERENCES device_info(device_id)
ON DELETE CASCADE; 