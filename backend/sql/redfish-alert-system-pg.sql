-- ===========================
-- Redfish告警系统数据库脚本 (PostgreSQL)
-- 创建时间: 2024
-- 说明: 基于RuoYi-Vue3-FastAPI项目的Redfish告警系统扩展
-- ===========================

-- ----------------------------
-- 1、设备信息表
-- ----------------------------
drop table if exists device_info;
create table device_info (
    device_id bigserial not null,                    -- 设备ID（主键）
    device_name varchar(100) not null,               -- 设备名称
    hostname varchar(100),                           -- 主机名
    business_ip varchar(45),                         -- 业务IP地址
    oob_ip varchar(45) not null,                     -- 带外IP地址（BMC IP）
    oob_port int4 default 443,                       -- 带外端口号
    location varchar(200) not null,                  -- 机房位置（如：XW_B1B04_21-24）
    operating_system varchar(100),                   -- 操作系统
    serial_number varchar(100),                      -- 序列号
    model varchar(100),                              -- 设备型号
    manufacturer varchar(100),                       -- 厂商
    technical_system varchar(100),                   -- 技术系统
    system_owner varchar(100),                       -- 系统负责人
    business_purpose varchar(200),                   -- 业务用途
    business_type varchar(50),                       -- 业务类型（OB/DB/WEB/APP等）
    redfish_username varchar(100),                   -- Redfish用户名
    redfish_password varchar(255),                   -- Redfish密码（加密存储）
    monitor_enabled smallint default 1,              -- 是否启用监控（1启用/0禁用）
    last_check_time timestamp(0),                    -- 最后检查时间
    health_status varchar(20) default 'unknown',     -- 健康状态（ok/warning/critical/unknown）
    device_status varchar(20) default 'unknown',     -- 设备状态（online/offline/error/unknown）
    create_by varchar(64) default '',                -- 创建者
    create_time timestamp(0) default current_timestamp, -- 创建时间
    update_by varchar(64) default '',                -- 更新者
    update_time timestamp(0) default current_timestamp, -- 更新时间
    remark varchar(500),                             -- 备注
    primary key (device_id)
);

-- 创建索引
create index idx_device_info_oob_ip on device_info(oob_ip);
create index idx_device_info_business_ip on device_info(business_ip);
create index idx_device_info_hostname on device_info(hostname);
create index idx_device_info_location on device_info(location);
create index idx_device_info_health_status on device_info(health_status);
create index idx_device_info_system_owner on device_info(system_owner);
create index idx_device_info_manufacturer on device_info(manufacturer);
create index idx_device_info_business_type on device_info(business_type);

-- 表注释
comment on table device_info is '设备信息表';
comment on column device_info.device_id is '设备ID';
comment on column device_info.device_name is '设备名称';
comment on column device_info.hostname is '主机名';
comment on column device_info.business_ip is '业务IP地址';
comment on column device_info.oob_ip is '带外IP地址（BMC IP）';
comment on column device_info.location is '机房位置（格式：XW_B1B04_21-24）';
comment on column device_info.operating_system is '操作系统';
comment on column device_info.serial_number is '序列号';
comment on column device_info.model is '设备型号';
comment on column device_info.manufacturer is '厂商';
comment on column device_info.technical_system is '技术系统';
comment on column device_info.system_owner is '系统负责人';
comment on column device_info.business_purpose is '业务用途';
comment on column device_info.business_type is '业务类型（OB/DB/WEB/APP等）';
comment on column device_info.redfish_username is 'Redfish用户名';
comment on column device_info.redfish_password is 'Redfish密码';
comment on column device_info.monitor_enabled is '是否启用监控（1启用/0禁用）';
comment on column device_info.last_check_time is '最后检查时间';
comment on column device_info.health_status is '健康状态（ok正常/warning警告/critical严重/unknown未知）';

-- ----------------------------
-- 2、告警信息表（首页显示用）
-- ----------------------------
drop table if exists alert_info;
create table alert_info (
    alert_id bigserial not null,                     -- 告警ID（主键）
    device_id bigint not null,                       -- 设备ID（外键关联device_info）
    alert_source varchar(50) not null,               -- 告警来源（redfish/snmp/agent等）
    component_type varchar(50) not null,             -- 组件类型（cpu/memory/storage/fan/power/temperature等）
    component_name varchar(100),                     -- 组件名称（如：CPU1、Memory_DIMM_A1等）
    alert_level varchar(20) not null,                -- 告警级别（critical/warning/info）
    alert_type varchar(20) not null,                 -- 告警类型（urgent紧急/scheduled择期）
    alert_type_original varchar(20),                 -- 原始告警类型（系统自动判断）
    alert_message text,                              -- 告警详细信息
    alert_status varchar(20) default 'active',       -- 告警状态（active活跃/acknowledged已确认/resolved已解决/closed已关闭）
    first_occurrence timestamp(0) not null,          -- 首次发生时间
    last_occurrence timestamp(0),                    -- 最后发生时间
    occurrence_count int4 default 1,                 -- 发生次数
    acknowledged_time timestamp(0),                  -- 确认时间
    resolved_time timestamp(0),                      -- 解决时间
    resolution_note text,                            -- 解决说明
    auto_resolved smallint default 0,                -- 是否自动解决（1是/0否）
    notification_sent smallint default 0,            -- 是否已发送通知（1是/0否）
    is_manual_override smallint default 0,           -- 是否手动覆盖（1是/0否）
    override_reason varchar(500),                    -- 覆盖原因
    override_by varchar(64),                         -- 覆盖操作人
    override_time timestamp(0),                      -- 覆盖时间
    raw_data text,                                   -- 原始数据（JSON格式）
    create_time timestamp(0) default current_timestamp, -- 创建时间
    update_time timestamp(0) default current_timestamp, -- 更新时间
    primary key (alert_id),
    foreign key (device_id) references device_info(device_id)
);

-- 创建索引
create index idx_alert_info_device_id on alert_info(device_id);
create index idx_alert_info_level on alert_info(alert_level);
create index idx_alert_info_type on alert_info(alert_type);
create index idx_alert_info_status on alert_info(alert_status);
create index idx_alert_info_component on alert_info(component_type);
create index idx_alert_info_first_occurrence on alert_info(first_occurrence);
create index idx_alert_info_manual_override on alert_info(is_manual_override);

-- 表注释
comment on table alert_info is '告警信息表（首页显示用）';
comment on column alert_info.alert_id is '告警ID';
comment on column alert_info.device_id is '设备ID';
comment on column alert_info.alert_source is '告警来源';
comment on column alert_info.component_type is '组件类型（cpu/memory/storage/fan/power/temperature等）';
comment on column alert_info.alert_level is '告警级别（critical严重/warning警告/info信息）';
comment on column alert_info.alert_type is '告警类型（urgent紧急/scheduled择期）';
comment on column alert_info.alert_type_original is '原始告警类型（系统根据规则自动判断）';
comment on column alert_info.alert_status is '告警状态（active活跃/acknowledged已确认/resolved已解决/closed已关闭）';
comment on column alert_info.occurrence_count is '发生次数（重复告警计数）';
comment on column alert_info.auto_resolved is '是否自动解决（1是/0否）';
comment on column alert_info.is_manual_override is '是否手动覆盖（1是/0否）';
comment on column alert_info.override_reason is '手动覆盖的原因说明';

-- ----------------------------
-- 3、Redfish告警日志表（详细日志显示用）
-- ----------------------------
drop table if exists redfish_alert_log;
create table redfish_alert_log (
    log_id bigserial not null,                       -- 日志ID（主键）
    device_id bigint not null,                       -- 设备ID（外键关联device_info）
    alert_id bigint,                                 -- 关联的告警ID（外键关联alert_info，可为空）
    log_source varchar(50) default 'redfish',        -- 日志来源
    component_type varchar(50),                      -- 组件类型
    component_name varchar(100),                     -- 组件名称
    log_level varchar(20),                           -- 日志级别
    log_message text,                                -- 日志消息
    raw_data text,                                   -- 原始JSON数据
    occurrence_time timestamp(0) not null,           -- 发生时间
    create_time timestamp(0) default current_timestamp, -- 创建时间
    primary key (log_id),
    foreign key (device_id) references device_info(device_id),
    foreign key (alert_id) references alert_info(alert_id)
);

-- 创建索引
create index idx_redfish_log_device_id on redfish_alert_log(device_id);
create index idx_redfish_log_alert_id on redfish_alert_log(alert_id);
create index idx_redfish_log_occurrence_time on redfish_alert_log(occurrence_time);
create index idx_redfish_log_component on redfish_alert_log(component_type);

-- 表注释
comment on table redfish_alert_log is 'Redfish告警日志表（详细日志显示用）';
comment on column redfish_alert_log.log_id is '日志ID';
comment on column redfish_alert_log.device_id is '设备ID';
comment on column redfish_alert_log.alert_id is '关联的告警ID';
comment on column redfish_alert_log.log_source is '日志来源';
comment on column redfish_alert_log.occurrence_time is '日志发生时间';

-- ----------------------------
-- 4、业务硬件紧急度规则表
-- ----------------------------
drop table if exists business_hardware_urgency_rules;
create table business_hardware_urgency_rules (
    rule_id bigserial not null,                      -- 规则ID（主键）
    business_type varchar(50) not null,              -- 业务类型（如：OB/DB/WEB/APP等）
    hardware_type varchar(50) not null,              -- 硬件类型（cpu/memory/disk/power/fan/temperature等）
    urgency_level varchar(20) not null,              -- 紧急程度（urgent紧急/scheduled择期）
    description varchar(200),                        -- 规则描述
    is_active smallint default 1,                    -- 是否启用（1启用/0禁用）
    create_by varchar(64) default '',                -- 创建者
    create_time timestamp(0) default current_timestamp, -- 创建时间
    update_by varchar(64) default '',                -- 更新者
    update_time timestamp(0) default current_timestamp, -- 更新时间
    primary key (rule_id),
    unique (business_type, hardware_type)
);

-- 创建索引
create index idx_urgency_rules_business_type on business_hardware_urgency_rules(business_type);
create index idx_urgency_rules_hardware_type on business_hardware_urgency_rules(hardware_type);
create index idx_urgency_rules_urgency on business_hardware_urgency_rules(urgency_level);

-- 表注释
comment on table business_hardware_urgency_rules is '业务硬件紧急度规则表';
comment on column business_hardware_urgency_rules.business_type is '业务类型（OB/DB/WEB/APP等）';
comment on column business_hardware_urgency_rules.hardware_type is '硬件类型（cpu/memory/disk/power/fan/temperature等）';
comment on column business_hardware_urgency_rules.urgency_level is '紧急程度（urgent紧急/scheduled择期）';

-- ----------------------------
-- 5、值班管理表
-- ----------------------------
drop table if exists duty_schedule;
create table duty_schedule (
    duty_id bigserial not null,                      -- 值班ID（主键）
    user_id bigint not null,                         -- 值班人员ID（外键关联sys_user）
    duty_date date not null,                         -- 值班日期
    duty_type varchar(20) default 'normal',          -- 值班类型（normal普通/holiday节假日/emergency应急）
    shift_type varchar(20) default 'all_day',        -- 班次类型（all_day全天/day_shift白班/night_shift夜班/custom自定义）
    start_time time,                                 -- 开始时间（自定义班次时使用）
    end_time time,                                   -- 结束时间（自定义班次时使用）
    contact_phone varchar(20),                       -- 值班联系电话
    contact_email varchar(100),                      -- 值班联系邮箱
    backup_user_id bigint,                           -- 备班人员ID（外键关联sys_user）
    backup_phone varchar(20),                        -- 备班联系电话
    duty_status varchar(20) default 'scheduled',     -- 值班状态（scheduled计划/active进行中/completed完成/cancelled取消）
    location varchar(100),                           -- 值班地点
    responsibilities text,                           -- 值班职责
    handover_notes text,                             -- 交接说明
    actual_start_time timestamp(0),                  -- 实际开始时间
    actual_end_time timestamp(0),                    -- 实际结束时间
    create_by varchar(64) default '',                -- 创建者
    create_time timestamp(0) default current_timestamp, -- 创建时间
    update_by varchar(64) default '',                -- 更新者
    update_time timestamp(0) default current_timestamp, -- 更新时间
    remark varchar(500),                             -- 备注
    primary key (duty_id),
    foreign key (user_id) references sys_user(user_id),
    foreign key (backup_user_id) references sys_user(user_id)
);

-- 创建索引
create index idx_duty_schedule_user_id on duty_schedule(user_id);
create index idx_duty_schedule_date on duty_schedule(duty_date);
create index idx_duty_schedule_status on duty_schedule(duty_status);
create index idx_duty_schedule_type on duty_schedule(duty_type);
create index idx_duty_schedule_backup on duty_schedule(backup_user_id);
create index idx_duty_schedule_date_shift on duty_schedule(duty_date, shift_type);

-- 表注释
comment on table duty_schedule is '值班管理表';
comment on column duty_schedule.duty_id is '值班ID';
comment on column duty_schedule.user_id is '值班人员ID';
comment on column duty_schedule.duty_date is '值班日期';
comment on column duty_schedule.duty_type is '值班类型（normal普通/holiday节假日/emergency应急）';
comment on column duty_schedule.shift_type is '班次类型（all_day全天/day_shift白班/night_shift夜班/custom自定义）';
comment on column duty_schedule.backup_user_id is '备班人员ID';
comment on column duty_schedule.duty_status is '值班状态';
comment on column duty_schedule.responsibilities is '值班职责描述';

-- ----------------------------
-- 初始化业务硬件紧急度规则数据
-- ----------------------------
insert into business_hardware_urgency_rules (business_type, hardware_type, urgency_level, description, create_by) values
('OB', 'cpu', 'urgent', 'OB服务器CPU故障为紧急', 'admin'),
('OB', 'memory', 'urgent', 'OB服务器内存故障为紧急', 'admin'),
('OB', 'disk', 'scheduled', 'OB服务器磁盘故障为择期', 'admin'),
('OB', 'power', 'scheduled', 'OB服务器电源故障为择期', 'admin'),
('OB', 'fan', 'scheduled', 'OB服务器风扇故障为择期', 'admin'),
('OB', 'temperature', 'scheduled', 'OB服务器温度告警为择期', 'admin'),
('DB', 'cpu', 'urgent', '数据库服务器CPU故障为紧急', 'admin'),
('DB', 'memory', 'urgent', '数据库服务器内存故障为紧急', 'admin'),
('DB', 'disk', 'urgent', '数据库服务器磁盘故障为紧急', 'admin'),
('DB', 'power', 'urgent', '数据库服务器电源故障为紧急', 'admin'),
('DB', 'fan', 'scheduled', '数据库服务器风扇故障为择期', 'admin'),
('DB', 'temperature', 'scheduled', '数据库服务器温度告警为择期', 'admin'),
('WEB', 'cpu', 'scheduled', 'WEB服务器CPU故障为择期', 'admin'),
('WEB', 'memory', 'scheduled', 'WEB服务器内存故障为择期', 'admin'),
('WEB', 'disk', 'scheduled', 'WEB服务器磁盘故障为择期', 'admin'),
('WEB', 'power', 'scheduled', 'WEB服务器电源故障为择期', 'admin'),
('WEB', 'fan', 'scheduled', 'WEB服务器风扇故障为择期', 'admin'),
('WEB', 'temperature', 'scheduled', 'WEB服务器温度告警为择期', 'admin'),
('APP', 'cpu', 'scheduled', '应用服务器CPU故障为择期', 'admin'),
('APP', 'memory', 'scheduled', '应用服务器内存故障为择期', 'admin'),
('APP', 'disk', 'scheduled', '应用服务器磁盘故障为择期', 'admin'),
('APP', 'power', 'scheduled', '应用服务器电源故障为择期', 'admin'),
('APP', 'fan', 'scheduled', '应用服务器风扇故障为择期', 'admin'),
('APP', 'temperature', 'scheduled', '应用服务器温度告警为择期', 'admin');

-- ----------------------------
-- 设置序列起始值
-- ----------------------------
alter sequence device_info_device_id_seq restart 1000;
alter sequence alert_info_alert_id_seq restart 1000;
alter sequence redfish_alert_log_log_id_seq restart 1000;
alter sequence business_hardware_urgency_rules_rule_id_seq restart 100;
alter sequence duty_schedule_duty_id_seq restart 1000; 