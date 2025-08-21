-- ----------------------------
-- Redfish日志表结构
-- ----------------------------

-- 创建Redfish日志表
DROP TABLE IF EXISTS redfish_log;
CREATE TABLE redfish_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id INTEGER NOT NULL,
    device_ip VARCHAR(45) NOT NULL,
    entry_id VARCHAR(100),
    entry_type VARCHAR(50),
    log_source VARCHAR(10) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    created_time TIMESTAMP NOT NULL,
    collected_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    message TEXT,
    message_id VARCHAR(100),
    sensor_type VARCHAR(50),
    sensor_number INTEGER,
    create_by VARCHAR(50),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_by VARCHAR(50),
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    remark VARCHAR(500)
);

-- 创建索引以提高查询性能
CREATE INDEX idx_redfish_log_device_id ON redfish_log (device_id);
CREATE INDEX idx_redfish_log_device_ip ON redfish_log (device_ip);
CREATE INDEX idx_redfish_log_severity ON redfish_log (severity);
CREATE INDEX idx_redfish_log_created_time ON redfish_log (created_time);
CREATE INDEX idx_redfish_log_collected_time ON redfish_log (collected_time);
CREATE INDEX idx_redfish_log_source ON redfish_log (log_source);
CREATE INDEX idx_redfish_log_device_time ON redfish_log (device_id, created_time);

-- 添加表注释
COMMENT ON TABLE redfish_log IS 'Redfish设备日志表';
COMMENT ON COLUMN redfish_log.log_id IS '日志ID';
COMMENT ON COLUMN redfish_log.device_id IS '设备ID';
COMMENT ON COLUMN redfish_log.device_ip IS '设备IP地址';
COMMENT ON COLUMN redfish_log.entry_id IS '原始条目ID';
COMMENT ON COLUMN redfish_log.entry_type IS '条目类型';
COMMENT ON COLUMN redfish_log.log_source IS '日志来源(SEL/MEL)';
COMMENT ON COLUMN redfish_log.severity IS '严重程度(CRITICAL/WARNING)';
COMMENT ON COLUMN redfish_log.created_time IS '日志创建时间';
COMMENT ON COLUMN redfish_log.collected_time IS '日志收集时间';
COMMENT ON COLUMN redfish_log.message IS '日志消息';
COMMENT ON COLUMN redfish_log.message_id IS '消息ID';
COMMENT ON COLUMN redfish_log.sensor_type IS '传感器类型';
COMMENT ON COLUMN redfish_log.sensor_number IS '传感器编号';
COMMENT ON COLUMN redfish_log.create_by IS '创建者';
COMMENT ON COLUMN redfish_log.create_time IS '创建时间';
COMMENT ON COLUMN redfish_log.update_by IS '更新者';
COMMENT ON COLUMN redfish_log.update_time IS '更新时间';
COMMENT ON COLUMN redfish_log.remark IS '备注';
