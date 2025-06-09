-- ===========================
-- 业务规则字典表扩展脚本 (PostgreSQL)
-- 说明: 为业务硬件紧急度规则管理添加字典表支持
-- ===========================

-- ----------------------------
-- 1、业务类型字典表
-- ----------------------------
drop table if exists business_type_dict;
create table business_type_dict (
    type_id bigserial not null,                      -- 类型ID（主键）
    type_code varchar(50) not null,                  -- 类型编码
    type_name varchar(100) not null,                 -- 类型名称
    type_description varchar(200),                   -- 类型描述
    sort_order int4 default 0,                       -- 排序顺序
    is_active smallint default 1,                    -- 是否启用（1启用/0禁用）
    create_by varchar(64) default '',                -- 创建者
    create_time timestamp(0) default current_timestamp, -- 创建时间
    update_by varchar(64) default '',                -- 更新者
    update_time timestamp(0) default current_timestamp, -- 更新时间
    primary key (type_id),
    unique (type_code)
);

-- 创建索引
create index idx_business_type_dict_code on business_type_dict(type_code);
create index idx_business_type_dict_active on business_type_dict(is_active);
create index idx_business_type_dict_sort on business_type_dict(sort_order);

-- 表注释
comment on table business_type_dict is '业务类型字典表';
comment on column business_type_dict.type_id is '类型ID';
comment on column business_type_dict.type_code is '类型编码';
comment on column business_type_dict.type_name is '类型名称';
comment on column business_type_dict.type_description is '类型描述';
comment on column business_type_dict.sort_order is '排序顺序';
comment on column business_type_dict.is_active is '是否启用（1启用/0禁用）';

-- 初始化业务类型数据
insert into business_type_dict (type_code, type_name, type_description, sort_order) values
('OB', 'OceanBase数据库', 'OceanBase分布式数据库服务', 1),
('MYSQL', 'MySQL数据库', 'MySQL关系型数据库服务', 2),
('ORACLE', 'Oracle数据库', 'Oracle企业级数据库服务', 3),
('REDIS', 'Redis缓存', 'Redis内存数据库服务', 4),
('ES', 'ElasticSearch', 'ElasticSearch搜索引擎服务', 5),
('KAFKA', 'Kafka消息队列', 'Apache Kafka消息中间件服务', 6),
('WEB', 'Web应用服务', 'Web应用程序服务器', 7),
('APP', '应用服务', '业务应用程序服务', 8),
('API', 'API网关', 'API网关服务', 9),
('NGINX', 'Nginx代理', 'Nginx反向代理服务', 10),
('MONITOR', '监控服务', '系统监控相关服务', 11),
('STORAGE', '存储服务', '文件存储相关服务', 12),
('BACKUP', '备份服务', '数据备份相关服务', 13),
('OTHER', '其他服务', '其他类型业务服务', 99);

-- ----------------------------
-- 2、硬件类型字典表
-- ----------------------------
drop table if exists hardware_type_dict;
create table hardware_type_dict (
    type_id bigserial not null,                      -- 类型ID（主键）
    type_code varchar(50) not null,                  -- 类型编码
    type_name varchar(100) not null,                 -- 类型名称
    type_description varchar(200),                   -- 类型描述
    category varchar(50),                            -- 硬件分类（compute/storage/network/power/cooling）
    sort_order int4 default 0,                       -- 排序顺序
    is_active smallint default 1,                    -- 是否启用（1启用/0禁用）
    create_by varchar(64) default '',                -- 创建者
    create_time timestamp(0) default current_timestamp, -- 创建时间
    update_by varchar(64) default '',                -- 更新者
    update_time timestamp(0) default current_timestamp, -- 更新时间
    primary key (type_id),
    unique (type_code)
);

-- 创建索引
create index idx_hardware_type_dict_code on hardware_type_dict(type_code);
create index idx_hardware_type_dict_category on hardware_type_dict(category);
create index idx_hardware_type_dict_active on hardware_type_dict(is_active);
create index idx_hardware_type_dict_sort on hardware_type_dict(sort_order);

-- 表注释
comment on table hardware_type_dict is '硬件类型字典表';
comment on column hardware_type_dict.type_id is '类型ID';
comment on column hardware_type_dict.type_code is '类型编码';
comment on column hardware_type_dict.type_name is '类型名称';
comment on column hardware_type_dict.type_description is '类型描述';
comment on column hardware_type_dict.category is '硬件分类';
comment on column hardware_type_dict.sort_order is '排序顺序';
comment on column hardware_type_dict.is_active is '是否启用（1启用/0禁用）';

-- 初始化硬件类型数据
insert into hardware_type_dict (type_code, type_name, type_description, category, sort_order) values
-- 计算类硬件
('CPU', 'CPU处理器', 'Central Processing Unit 中央处理器', 'compute', 1),
('MEMORY', '内存', 'RAM 随机存取存储器', 'compute', 2),
('MOTHERBOARD', '主板', '系统主板', 'compute', 3),

-- 存储类硬件
('DISK', '硬盘', '机械硬盘或固态硬盘', 'storage', 10),
('SSD', '固态硬盘', 'Solid State Drive 固态存储设备', 'storage', 11),
('RAID', 'RAID控制器', 'RAID阵列控制器', 'storage', 12),
('STORAGE_CONTROLLER', '存储控制器', '存储设备控制器', 'storage', 13),

-- 网络类硬件
('NETWORK', '网卡', '网络接口卡', 'network', 20),
('SWITCH', '交换机', '网络交换设备', 'network', 21),
('ROUTER', '路由器', '网络路由设备', 'network', 22),

-- 电源类硬件
('POWER', '电源', 'Power Supply Unit 电源供应单元', 'power', 30),
('UPS', 'UPS电源', 'Uninterruptible Power Supply 不间断电源', 'power', 31),
('BATTERY', '电池', '备用电池', 'power', 32),

-- 散热类硬件
('FAN', '风扇', '散热风扇', 'cooling', 40),
('TEMPERATURE', '温度传感器', '温度监控传感器', 'cooling', 41),
('COOLING', '散热系统', '整体散热系统', 'cooling', 42),

-- 其他硬件
('CHASSIS', '机箱', '服务器机箱', 'other', 50),
('CABLE', '线缆', '数据线缆或电源线缆', 'other', 51),
('SENSOR', '传感器', '各类监控传感器', 'other', 52),
('OTHER', '其他硬件', '其他类型硬件组件', 'other', 99);

-- 序列号重置
alter sequence business_type_dict_type_id_seq restart 100;
alter sequence hardware_type_dict_type_id_seq restart 100; 