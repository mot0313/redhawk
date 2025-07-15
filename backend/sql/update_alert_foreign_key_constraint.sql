-- 更新alert_info表外键约束，支持逻辑删除告警，物理删除设备
-- 执行日期: 2025-01-13

-- 1. 首先删除现有的外键约束
ALTER TABLE alert_info DROP CONSTRAINT IF EXISTS alert_info_device_id_fkey;

-- 2. 修改device_id列允许NULL值
ALTER TABLE alert_info ALTER COLUMN device_id DROP NOT NULL;

-- 3. 重新创建外键约束，添加ON DELETE SET NULL
ALTER TABLE alert_info 
ADD CONSTRAINT alert_info_device_id_fkey 
FOREIGN KEY (device_id) 
REFERENCES device_info(device_id) 
ON DELETE SET NULL ON UPDATE CASCADE;

-- 4. 为del_flag字段添加索引以提升查询性能
CREATE INDEX IF NOT EXISTS idx_alert_info_del_flag ON alert_info(del_flag);

-- 5. 更新现有数据：确保del_flag字段有默认值
UPDATE alert_info SET del_flag = 0 WHERE del_flag IS NULL;

-- 6. 为查询性能添加复合索引
CREATE INDEX IF NOT EXISTS idx_alert_info_device_del_flag ON alert_info(device_id, del_flag) WHERE del_flag = 0;
CREATE INDEX IF NOT EXISTS idx_alert_info_status_del_flag ON alert_info(alert_status, del_flag) WHERE del_flag = 0;

COMMIT; 