-- ===========================
-- 替换alert_info表为精简版结构 (PostgreSQL)
-- 先备份原表，再创建新的精简版alert_info表
-- 创建时间: 2024-12
-- 注意：这会替换现有的alert_info表，请确保已备份数据！
-- ===========================

-- 第一步：备份原表（如果存在）
DROP TABLE IF EXISTS alert_info_backup CASCADE;
CREATE TABLE alert_info_backup AS SELECT * FROM alert_info;
COMMENT ON TABLE alert_info_backup IS '原始alert_info表备份（替换前）';

-- 第二步：删除原表和相关对象
DROP TABLE IF EXISTS alert_info CASCADE;

-- 第三步：创建新的精简版alert_info表
CREATE TABLE alert_info (
    alert_id bigserial NOT NULL,                     -- 告警ID（主键），用于唯一标识告警记录
    device_id bigint NOT NULL,                       -- 设备ID（外键关联device_info表），标识故障设备
    component_type varchar(50) NOT NULL,             -- 组件类型（如：CPU/Memory/Storage/Fan/Power/Temperature），首页展示核心字段
    component_name varchar(100),                     -- 组件名称（如：CPU1/Memory_DIMM_A1/Fan1），首页展示具体故障组件
    health_status varchar(20) NOT NULL,              -- 健康状态（ok正常/warning警告/critical严重），首页展示设备组件状态
    urgency_level varchar(20) NOT NULL,              -- 紧急程度（urgent紧急/scheduled择期），首页展示告警紧急度，用于分类显示
    alert_status varchar(20) DEFAULT 'active',       -- 告警状态（active活跃/resolved已解决），业务流程状态管理
    first_occurrence timestamp(0) NOT NULL,          -- 首次发生时间，告警最初发现时间，用于时间排序
    last_occurrence timestamp(0),                    -- 最后发生时间，最近一次相同告警时间，用于重复告警判断
    resolved_time timestamp(0),                      -- 解决时间，告警处理完成时间，用于统计和排期管理
    create_time timestamp(0) DEFAULT CURRENT_TIMESTAMP, -- 创建时间，记录插入数据库时间，数据审计用
    update_time timestamp(0) DEFAULT CURRENT_TIMESTAMP, -- 更新时间，记录最后修改时间，数据审计用
    PRIMARY KEY (alert_id),
    FOREIGN KEY (device_id) REFERENCES device_info(device_id)
);

-- 第四步：创建优化索引
CREATE INDEX idx_alert_info_device_component ON alert_info(device_id, component_type);
CREATE INDEX idx_alert_info_urgency_status ON alert_info(urgency_level, alert_status);
CREATE INDEX idx_alert_info_health_status ON alert_info(health_status);
CREATE INDEX idx_alert_info_first_occurrence ON alert_info(first_occurrence);
CREATE INDEX idx_alert_info_device_id ON alert_info(device_id);
CREATE INDEX idx_alert_info_status ON alert_info(alert_status);

-- 第五步：添加表注释
COMMENT ON TABLE alert_info IS '精简版告警信息表（专注首页展示）';

-- 第六步：添加字段注释
COMMENT ON COLUMN alert_info.alert_id IS '告警ID（主键），唯一标识告警记录，用于硬件排期关联';
COMMENT ON COLUMN alert_info.device_id IS '设备ID（外键），关联device_info表，标识发生故障的设备';
COMMENT ON COLUMN alert_info.component_type IS '组件类型（首页核心展示字段），如：CPU/Memory/Storage/Fan/Power/Temperature';
COMMENT ON COLUMN alert_info.component_name IS '组件名称（首页展示），具体故障组件标识，如：CPU1/Memory_DIMM_A1/Fan1';
COMMENT ON COLUMN alert_info.health_status IS '健康状态（首页核心展示），ok正常/warning警告/critical严重';
COMMENT ON COLUMN alert_info.urgency_level IS '紧急程度（首页核心展示），urgent紧急告警/scheduled择期告警，用于首页分类显示';
COMMENT ON COLUMN alert_info.alert_status IS '告警状态，active活跃告警/resolved已解决告警，用于业务流程管理';
COMMENT ON COLUMN alert_info.first_occurrence IS '首次发生时间，告警最初发现的时间，用于时间排序';
COMMENT ON COLUMN alert_info.last_occurrence IS '最后发生时间，最近一次相同告警的发生时间，用于重复告警判断';
COMMENT ON COLUMN alert_info.resolved_time IS '解决时间，告警处理完成的时间，用于统计分析和排期管理';
COMMENT ON COLUMN alert_info.create_time IS '创建时间，记录插入数据库的时间，用于数据审计';
COMMENT ON COLUMN alert_info.update_time IS '更新时间，记录最后修改的时间，用于数据审计和变更跟踪';

-- 第七步：创建更新时间自动触发器
CREATE OR REPLACE FUNCTION update_alert_info_updated_time()
RETURNS TRIGGER AS $$
BEGIN
    NEW.update_time = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_alert_info_update_time
    BEFORE UPDATE ON alert_info
    FOR EACH ROW
    EXECUTE FUNCTION update_alert_info_updated_time();

-- 第八步：验证新表创建
SELECT 
    'alert_info表已成功替换为精简版' as 状态,
    COUNT(*) as 当前记录数
FROM alert_info;

-- 查看备份表记录数（供参考）
SELECT 
    'alert_info_backup备份表记录数' as 状态,
    COUNT(*) as 备份记录数
FROM alert_info_backup; 