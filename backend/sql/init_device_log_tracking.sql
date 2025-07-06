-- 初始化device_log_check_tracking表的SQL脚本
-- 用于增量获取未处理的日志

-- 创建序列（如果不存在）
CREATE SEQUENCE IF NOT EXISTS device_log_check_tracking_id_seq;

-- 创建表（如果不存在）
CREATE TABLE IF NOT EXISTS "public"."device_log_check_tracking" (
  "id" int8 NOT NULL DEFAULT nextval('device_log_check_tracking_id_seq'::regclass),
  "device_id" int8 NOT NULL,
  "log_type" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'sel'::character varying,
  "last_check_time" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "last_entry_id" varchar(100) COLLATE "pg_catalog"."default",
  "last_entry_timestamp" timestamp(6),
  "created_time" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_time" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "device_log_check_tracking_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "device_log_check_tracking_device_id_fkey" FOREIGN KEY ("device_id") REFERENCES "public"."device_info" ("device_id") ON DELETE CASCADE ON UPDATE NO ACTION
);

-- 设置表所有者
ALTER TABLE "public"."device_log_check_tracking" OWNER TO "postgres";

-- 创建索引（如果不存在）
CREATE INDEX IF NOT EXISTS "idx_device_log_type" ON "public"."device_log_check_tracking" USING btree (
  "device_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "log_type" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

CREATE INDEX IF NOT EXISTS "idx_last_check_time" ON "public"."device_log_check_tracking" USING btree (
  "last_check_time" "pg_catalog"."timestamp_ops" ASC NULLS LAST
);

CREATE UNIQUE INDEX IF NOT EXISTS "unique_device_log_type" ON "public"."device_log_check_tracking" USING btree (
  "device_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "log_type" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- 添加表注释
COMMENT ON TABLE "public"."device_log_check_tracking" IS '设备日志检查时间跟踪表，用于增量获取未处理日志';

-- 添加列注释
COMMENT ON COLUMN "public"."device_log_check_tracking"."id" IS '主键ID';
COMMENT ON COLUMN "public"."device_log_check_tracking"."device_id" IS '设备ID（外键关联device_info表）';
COMMENT ON COLUMN "public"."device_log_check_tracking"."log_type" IS '日志类型（sel, mel等）';
COMMENT ON COLUMN "public"."device_log_check_tracking"."last_check_time" IS '最后检查时间';
COMMENT ON COLUMN "public"."device_log_check_tracking"."last_entry_id" IS '最后获取的日志条目ID';
COMMENT ON COLUMN "public"."device_log_check_tracking"."last_entry_timestamp" IS '最后获取的日志条目时间戳';
COMMENT ON COLUMN "public"."device_log_check_tracking"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."device_log_check_tracking"."updated_time" IS '更新时间';

-- 初始化现有设备的跟踪记录
-- 为所有启用监控的设备创建SEL和MEL的跟踪记录
INSERT INTO "public"."device_log_check_tracking" (
    "device_id", 
    "log_type", 
    "last_check_time",
    "created_time",
    "updated_time"
)
SELECT 
    d.device_id,
    log_types.log_type,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
FROM 
    "public"."device_info" d
CROSS JOIN (
    VALUES ('sel'), ('mel')
) AS log_types(log_type)
WHERE 
    d.monitor_enabled = 1
    AND NOT EXISTS (
        SELECT 1 
        FROM "public"."device_log_check_tracking" t 
        WHERE t.device_id = d.device_id 
        AND t.log_type = log_types.log_type
    );

-- 显示初始化结果
SELECT 
    COUNT(*) as total_tracking_records,
    COUNT(DISTINCT device_id) as tracked_devices
FROM "public"."device_log_check_tracking";

-- 显示按日志类型的分布
SELECT 
    log_type,
    COUNT(*) as count
FROM "public"."device_log_check_tracking"
GROUP BY log_type
ORDER BY log_type; 