DROP TABLE IF EXISTS "public"."alert_info";

CREATE TABLE "public"."alert_info" (
  "alert_id" BIGSERIAL PRIMARY KEY,
  "device_id" int8 NOT NULL,
  "component_type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "component_name" varchar(100) COLLATE "pg_catalog"."default",
  "health_status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "urgency_level" varchar(20) COLLATE "pg_catalog"."default" NOT NULL
  "alert_status" varchar(20) COLLATE "pg_catalog"."default" DEFAULT 'active'::character varying,
  "first_occurrence" timestamp(0) NOT NULL,
  "last_occurrence" timestamp(0),
  "resolved_time" timestamp(0),
  "create_time" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "update_time" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "scheduled_maintenance_time" timestamp(0),
  "maintenance_description" text COLLATE "pg_catalog"."default",
  "maintenance_status" varchar(20) COLLATE "pg_catalog"."default" DEFAULT 'none'::character varying,
  "maintenance_notes" text COLLATE "pg_catalog"."default"
)
;
ALTER TABLE "public"."alert_info" OWNER TO "postgres";
COMMENT ON COLUMN "public"."alert_info"."alert_id" IS '告警ID（主键），唯一标识告警记录，用于硬件排期关联';
COMMENT ON COLUMN "public"."alert_info"."device_id" IS '设备ID（外键），关联device_info表，标识发生故障的设备';
COMMENT ON COLUMN "public"."alert_info"."component_type" IS '组件类型（首页核心展示字段），如：CPU/Memory/Storage/Fan/Power/Temperature';
COMMENT ON COLUMN "public"."alert_info"."component_name" IS '组件名称（首页展示），具体故障组件标识，如：CPU1/Memory_DIMM_A1/Fan1';
COMMENT ON COLUMN "public"."alert_info"."health_status" IS '健康状态（首页核心展示），ok正常/warning警告/critical严重';
COMMENT ON COLUMN "public"."alert_info"."urgency_level" IS '紧急程度（首页核心展示），urgent紧急告警/scheduled择期告警，用于首页分类显示';
COMMENT ON COLUMN "public"."alert_info"."alert_status" IS '告警状态，active活跃告警/resolved已解决告警，用于业务流程管理';
COMMENT ON COLUMN "public"."alert_info"."first_occurrence" IS '首次发生时间，告警最初发现的时间，用于时间排序';
COMMENT ON COLUMN "public"."alert_info"."last_occurrence" IS '最后发生时间，最近一次相同告警的发生时间，用于重复告警判断';
COMMENT ON COLUMN "public"."alert_info"."resolved_time" IS '解决时间，告警处理完成的时间，用于统计分析和排期管理';
COMMENT ON COLUMN "public"."alert_info"."create_time" IS '创建时间，记录插入数据库的时间，用于数据审计';
COMMENT ON COLUMN "public"."alert_info"."update_time" IS '更新时间，记录最后修改的时间，用于数据审计和变更跟踪';
COMMENT ON TABLE "public"."alert_info" IS '精简版告警信息表（专注首页展示）';

-- ----------------------------
-- Indexes structure for table alert_info
-- ----------------------------
CREATE INDEX "idx_alert_info_device_component" ON "public"."alert_info" USING btree (
  "device_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "component_type" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_alert_info_device_id" ON "public"."alert_info" USING btree (
  "device_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "idx_alert_info_first_occurrence" ON "public"."alert_info" USING btree (
  "first_occurrence" "pg_catalog"."timestamp_ops" ASC NULLS LAST
);
CREATE INDEX "idx_alert_info_health_status" ON "public"."alert_info" USING btree (
  "health_status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_alert_info_status" ON "public"."alert_info" USING btree (
  "alert_status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_alert_info_urgency_status" ON "public"."alert_info" USING btree (
  "urgency_level" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "alert_status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_alert_info_display" ON "public"."alert_info" USING btree (
  "alert_status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "urgency_level" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "last_occurrence" "pg_catalog"."timestamp_ops" DESC NULLS FIRST
);
CREATE INDEX "ix_alert_info_first_occurrence" ON "public"."alert_info" USING btree (
  "first_occurrence" "pg_catalog"."timestamp_ops" ASC NULLS LAST
);
CREATE INDEX "ix_alert_info_lifecycle" ON "public"."alert_info" USING btree (
  "device_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "component_type" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "component_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "alert_status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table alert_info
-- ----------------------------
CREATE TRIGGER "trigger_alert_info_update_time" BEFORE UPDATE ON "public"."alert_info"
FOR EACH ROW
EXECUTE PROCEDURE "public"."update_alert_info_updated_time"();

-- ----------------------------
-- Primary Key structure for table alert_info
-- ----------------------------
ALTER TABLE "public"."alert_info" ADD CONSTRAINT "alert_info_pkey" PRIMARY KEY ("alert_id");

-- ----------------------------
-- Foreign Keys structure for table alert_info
-- ----------------------------
ALTER TABLE "public"."alert_info" ADD CONSTRAINT "alert_info_device_id_fkey" FOREIGN KEY ("device_id") REFERENCES "public"."device_info" ("device_id") ON DELETE NO ACTION ON UPDATE NO ACTION;


-- ----------------------------
-- Table structure for device_info
-- ----------------------------
DROP TABLE IF EXISTS "public"."device_info";
CREATE TABLE "public"."device_info" (
  "device_id" BIGSERIAL PRIMARY KEY,
  "hostname" varchar(100) COLLATE "pg_catalog"."default",
  "business_ip" varchar(45) COLLATE "pg_catalog"."default",
  "oob_ip" varchar(45) COLLATE "pg_catalog"."default" NOT NULL,
  "oob_port" int4 DEFAULT 443,
  "location" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "operating_system" varchar(100) COLLATE "pg_catalog"."default",
  "serial_number" varchar(100) COLLATE "pg_catalog"."default",
  "model" varchar(100) COLLATE "pg_catalog"."default",
  "manufacturer" varchar(100) COLLATE "pg_catalog"."default",
  "technical_system" varchar(100) COLLATE "pg_catalog"."default",
  "system_owner" varchar(100) COLLATE "pg_catalog"."default",
  "business_type" varchar(50) COLLATE "pg_catalog"."default",
  "redfish_username" varchar(100) COLLATE "pg_catalog"."default",
  "redfish_password" varchar(255) COLLATE "pg_catalog"."default",
  "monitor_enabled" int2 DEFAULT 1,
  "last_check_time" timestamp(0),
  "health_status" varchar(20) COLLATE "pg_catalog"."default" DEFAULT 'unknown'::character varying,
  "create_by" varchar(64) COLLATE "pg_catalog"."default" DEFAULT ''::character varying,
  "create_time" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "update_by" varchar(64) COLLATE "pg_catalog"."default" DEFAULT ''::character varying,
  "update_time" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "remark" varchar(500) COLLATE "pg_catalog"."default"
)
;
ALTER TABLE "public"."device_info" OWNER TO "postgres";
COMMENT ON COLUMN "public"."device_info"."device_id" IS '设备ID';
COMMENT ON COLUMN "public"."device_info"."hostname" IS '主机名';
COMMENT ON COLUMN "public"."device_info"."business_ip" IS '业务IP地址';
COMMENT ON COLUMN "public"."device_info"."oob_ip" IS '带外IP地址（BMC IP）';
COMMENT ON COLUMN "public"."device_info"."location" IS '机房位置（格式：XW_B1B04_21-24）';
COMMENT ON COLUMN "public"."device_info"."operating_system" IS '操作系统';
COMMENT ON COLUMN "public"."device_info"."serial_number" IS '序列号';
COMMENT ON COLUMN "public"."device_info"."model" IS '设备型号';
COMMENT ON COLUMN "public"."device_info"."manufacturer" IS '厂商';
COMMENT ON COLUMN "public"."device_info"."technical_system" IS '技术系统';
COMMENT ON COLUMN "public"."device_info"."system_owner" IS '系统负责人';
COMMENT ON COLUMN "public"."device_info"."business_type" IS '业务类型（OB/DB/WEB/APP等）';
COMMENT ON COLUMN "public"."device_info"."redfish_username" IS 'Redfish用户名';
COMMENT ON COLUMN "public"."device_info"."redfish_password" IS 'Redfish密码';
COMMENT ON COLUMN "public"."device_info"."monitor_enabled" IS '是否启用监控（1启用/0禁用）';
COMMENT ON COLUMN "public"."device_info"."last_check_time" IS '最后检查时间';
COMMENT ON COLUMN "public"."device_info"."health_status" IS '健康状态（ok正常/warning警告/critical严重/unknown未知）';
COMMENT ON TABLE "public"."device_info" IS '设备信息表';

-- ----------------------------
-- Indexes structure for table device_info
-- ----------------------------
CREATE INDEX "idx_device_info_business_ip" ON "public"."device_info" USING btree (
  "business_ip" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_device_info_business_type" ON "public"."device_info" USING btree (
  "business_type" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_device_info_health_status" ON "public"."device_info" USING btree (
  "health_status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_device_info_hostname" ON "public"."device_info" USING btree (
  "hostname" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_device_info_location" ON "public"."device_info" USING btree (
  "location" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_device_info_manufacturer" ON "public"."device_info" USING btree (
  "manufacturer" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_device_info_oob_ip" ON "public"."device_info" USING btree (
  "oob_ip" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_device_info_system_owner" ON "public"."device_info" USING btree (
  "system_owner" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table device_info
-- ----------------------------
ALTER TABLE "public"."device_info" ADD CONSTRAINT "device_info_pkey" PRIMARY KEY ("device_id");


-- ----------------------------
-- Table structure for hardware_type_dict
-- ----------------------------
DROP TABLE IF EXISTS "public"."hardware_type_dict";
CREATE TABLE "public"."hardware_type_dict" (
  "type_id" BIGSERIAL PRIMARY KEY,
  "type_code" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "type_name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "type_description" varchar(200) COLLATE "pg_catalog"."default",
  "category" varchar(50) COLLATE "pg_catalog"."default",
  "sort_order" int4 DEFAULT 0,
  "is_active" int2 DEFAULT 1,
  "create_by" varchar(64) COLLATE "pg_catalog"."default" DEFAULT ''::character varying,
  "create_time" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "update_by" varchar(64) COLLATE "pg_catalog"."default" DEFAULT ''::character varying,
  "update_time" timestamp(0) DEFAULT CURRENT_TIMESTAMP
)
;
ALTER TABLE "public"."hardware_type_dict" OWNER TO "postgres";
COMMENT ON COLUMN "public"."hardware_type_dict"."type_id" IS '类型ID';
COMMENT ON COLUMN "public"."hardware_type_dict"."type_code" IS '类型编码';
COMMENT ON COLUMN "public"."hardware_type_dict"."type_name" IS '类型名称';
COMMENT ON COLUMN "public"."hardware_type_dict"."type_description" IS '类型描述';
COMMENT ON COLUMN "public"."hardware_type_dict"."category" IS '硬件分类';
COMMENT ON COLUMN "public"."hardware_type_dict"."sort_order" IS '排序顺序';
COMMENT ON COLUMN "public"."hardware_type_dict"."is_active" IS '是否启用（1启用/0禁用）';
COMMENT ON TABLE "public"."hardware_type_dict" IS '硬件类型字典表';

-- ----------------------------
-- Indexes structure for table hardware_type_dict
-- ----------------------------
CREATE INDEX "idx_hardware_type_dict_active" ON "public"."hardware_type_dict" USING btree (
  "is_active" "pg_catalog"."int2_ops" ASC NULLS LAST
);
CREATE INDEX "idx_hardware_type_dict_category" ON "public"."hardware_type_dict" USING btree (
  "category" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_hardware_type_dict_code" ON "public"."hardware_type_dict" USING btree (
  "type_code" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_hardware_type_dict_sort" ON "public"."hardware_type_dict" USING btree (
  "sort_order" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table hardware_type_dict
-- ----------------------------
ALTER TABLE "public"."hardware_type_dict" ADD CONSTRAINT "hardware_type_dict_type_code_key" UNIQUE ("type_code");

-- ----------------------------
-- Primary Key structure for table hardware_type_dict
-- ----------------------------
ALTER TABLE "public"."hardware_type_dict" ADD CONSTRAINT "hardware_type_dict_pkey" PRIMARY KEY ("type_id");


-- ----------------------------
-- Table structure for business_type_dict
-- ----------------------------
DROP TABLE IF EXISTS "public"."business_type_dict";
CREATE TABLE "public"."business_type_dict" (
  "type_id" BIGSERIAL PRIMARY KEY,
  "type_code" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "type_name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "type_description" varchar(200) COLLATE "pg_catalog"."default",
  "sort_order" int4 DEFAULT 0,
  "is_active" int2 DEFAULT 1,
  "create_by" varchar(64) COLLATE "pg_catalog"."default" DEFAULT ''::character varying,
  "create_time" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "update_by" varchar(64) COLLATE "pg_catalog"."default" DEFAULT ''::character varying,
  "update_time" timestamp(0) DEFAULT CURRENT_TIMESTAMP
)
;
ALTER TABLE "public"."business_type_dict" OWNER TO "postgres";
COMMENT ON COLUMN "public"."business_type_dict"."type_id" IS '类型ID';
COMMENT ON COLUMN "public"."business_type_dict"."type_code" IS '类型编码';
COMMENT ON COLUMN "public"."business_type_dict"."type_name" IS '类型名称';
COMMENT ON COLUMN "public"."business_type_dict"."type_description" IS '类型描述';
COMMENT ON COLUMN "public"."business_type_dict"."sort_order" IS '排序顺序';
COMMENT ON COLUMN "public"."business_type_dict"."is_active" IS '是否启用（1启用/0禁用）';
COMMENT ON TABLE "public"."business_type_dict" IS '业务类型字典表';

-- ----------------------------
-- Indexes structure for table business_type_dict
-- ----------------------------
CREATE INDEX "idx_business_type_dict_active" ON "public"."business_type_dict" USING btree (
  "is_active" "pg_catalog"."int2_ops" ASC NULLS LAST
);
CREATE INDEX "idx_business_type_dict_code" ON "public"."business_type_dict" USING btree (
  "type_code" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_business_type_dict_sort" ON "public"."business_type_dict" USING btree (
  "sort_order" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table business_type_dict
-- ----------------------------
ALTER TABLE "public"."business_type_dict" ADD CONSTRAINT "business_type_dict_type_code_key" UNIQUE ("type_code");

-- ----------------------------
-- Primary Key structure for table business_type_dict
-- ----------------------------
ALTER TABLE "public"."business_type_dict" ADD CONSTRAINT "business_type_dict_pkey" PRIMARY KEY ("type_id");


INSERT INTO "business_type_dict" ("type_code", "type_name", "type_description", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('STORAGE', '存储服务', '文件存储相关服务', 12, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "business_type_dict" ("type_code", "type_name", "type_description", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('OTHER', '其他服务', '其他类型业务服务', 99, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "business_type_dict" ("type_code", "type_name", "type_description", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('TRAD-MB-2N', '传统服务器（主备两节点部署）', 'Oracle企业级数据库服务', 3, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "business_type_dict" ("type_code", "type_name", "type_description", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('BIGDATA-5N', '大数据服务器（五节点部署）', 'Redis内存数据库服务', 4, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "business_type_dict" ("type_code", "type_name", "type_description", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('VIRT-CLUSTER-8_16N', '虚拟化宿主机（一个集群内16台或8台部署）', 'ElasticSearch搜索引擎服务', 5, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "business_type_dict" ("type_code", "type_name", "type_description", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('BIGDATA-3N', '大数据服务器（三节点部署）', 'Web应用程序服务器', 7, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "business_type_dict" ("type_code", "type_name", "type_description", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('CLOUD-3N', '云资源服务器（三节点部署）', '业务应用程序服务', 8, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "business_type_dict" ("type_code", "type_name", "type_description", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('CLOUD-5N', '云资源服务器（五节点部署）', 'API网关服务', 9, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "business_type_dict" ("type_code", "type_name", "type_description", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('OB-DATA-5N', 'OB服务器（数据节点，五节点部署）', 'OB服务器（数据节点，五节点部署）', 2, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "business_type_dict" ("type_code", "type_name", "type_description", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('CLOUD-CTRL', '云资源服务器（管控节点）', 'Apache Kafka消息中间件服务', 5, 1, '', '2025-06-08 19:45:38', 'admin', '2025-06-11 18:53:13');
INSERT INTO "business_type_dict" ("type_code", "type_name", "type_description", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('OB-GMT-3N', 'OB服务器（管理节点，三节点部署）', 'OB服务器（管理节点，三节点部署）', 1, 1, '', '2025-06-08 19:45:38', 'admin', '2025-07-13 18:49:33');


INSERT INTO "hardware_type_dict" ("type_code", "type_name", "type_description", "category", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('MEMORY', '内存', 'RAM 随机存取存储器', 'compute', 2, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "hardware_type_dict" ("type_code", "type_name", "type_description", "category", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('MOTHERBOARD', '主板', '系统主板', 'compute', 3, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "hardware_type_dict" ("type_code", "type_name", "type_description", "category", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('DISK', '硬盘', '机械硬盘或固态硬盘', 'storage', 10, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "hardware_type_dict" ("type_code", "type_name", "type_description", "category", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('SSD', '固态硬盘', 'Solid State Drive 固态存储设备', 'storage', 11, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "hardware_type_dict" ("type_code", "type_name", "type_description", "category", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('RAID', 'RAID控制器', 'RAID阵列控制器', 'storage', 12, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "hardware_type_dict" ("type_code", "type_name", "type_description", "category", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('STORAGE_CONTROLLER', '存储控制器', '存储设备控制器', 'storage', 13, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "hardware_type_dict" ("type_code", "type_name", "type_description", "category", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('NETWORK', '网卡', '网络接口卡', 'network', 20, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "hardware_type_dict" ("type_code", "type_name", "type_description", "category", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('SWITCH', '交换机', '网络交换设备', 'network', 21, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "hardware_type_dict" ("type_code", "type_name", "type_description", "category", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('ROUTER', '路由器', '网络路由设备', 'network', 22, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "hardware_type_dict" ("type_code", "type_name", "type_description", "category", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('POWER', '电源', 'Power Supply Unit 电源供应单元', 'power', 30, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "hardware_type_dict" ("type_code", "type_name", "type_description", "category", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('UPS', 'UPS电源', 'Uninterruptible Power Supply 不间断电源', 'power', 31, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "hardware_type_dict" ("type_code", "type_name", "type_description", "category", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('BATTERY', '电池', '备用电池', 'power', 32, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "hardware_type_dict" ("type_code", "type_name", "type_description", "category", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('FAN', '风扇', '散热风扇', 'cooling', 40, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "hardware_type_dict" ("type_code", "type_name", "type_description", "category", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('TEMPERATURE', '温度传感器', '温度监控传感器', 'cooling', 41, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "hardware_type_dict" ("type_code", "type_name", "type_description", "category", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('COOLING', '散热系统', '整体散热系统', 'cooling', 42, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "hardware_type_dict" ("type_code", "type_name", "type_description", "category", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('CHASSIS', '机箱', '服务器机箱', 'other', 50, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "hardware_type_dict" ("type_code", "type_name", "type_description", "category", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('CABLE', '线缆', '数据线缆或电源线缆', 'other', 51, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "hardware_type_dict" ("type_code", "type_name", "type_description", "category", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('SENSOR', '传感器', '各类监控传感器', 'other', 52, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "hardware_type_dict" ("type_code", "type_name", "type_description", "category", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('OTHER', '其他硬件', '其他类型硬件组件', 'other', 99, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO "hardware_type_dict" ("type_code", "type_name", "type_description", "category", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('CPU', 'CPU处理器1', 'Central Processing Unit 中央处理器', 'compute', 1, 1, '', '2025-06-08 19:45:38', 'admin', '2025-07-12 18:05:47');
INSERT INTO "hardware_type_dict" ("type_code", "type_name", "type_description", "category", "sort_order", "is_active", "create_by", "create_time", "update_by", "update_time") VALUES ('CONNECTIVITY', '宕机', NULL, 'compute', 0, 1, 'admin', '2025-07-13 20:24:21', '', '2025-07-13 20:24:21');
