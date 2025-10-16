--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alert_info; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alert_info (
    alert_id bigint NOT NULL,
    device_id bigint,
    component_type character varying(50) NOT NULL,
    component_name character varying(100),
    health_status character varying(20) NOT NULL,
    urgency_level character varying(20) NOT NULL,
    alert_status character varying(20) DEFAULT 'active'::character varying,
    first_occurrence timestamp(0) without time zone NOT NULL,
    last_occurrence timestamp(0) without time zone,
    resolved_time timestamp(0) without time zone,
    create_time timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    update_time timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    scheduled_maintenance_time timestamp(0) without time zone,
    maintenance_description text,
    maintenance_status character varying(20) DEFAULT 'none'::character varying,
    maintenance_notes text,
    del_flag smallint DEFAULT 0
);


--
-- Name: TABLE alert_info; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.alert_info IS '精简版告警信息表（专注首页展示）';


--
-- Name: COLUMN alert_info.alert_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.alert_info.alert_id IS '告警ID（主键），唯一标识告警记录，用于硬件排期关联';


--
-- Name: COLUMN alert_info.device_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.alert_info.device_id IS '设备ID（外键），关联device_info表，标识发生故障的设备';


--
-- Name: COLUMN alert_info.component_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.alert_info.component_type IS '组件类型（首页核心展示字段），如：CPU/Memory/Storage/Fan/Power/Temperature';


--
-- Name: COLUMN alert_info.component_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.alert_info.component_name IS '组件名称（首页展示），具体故障组件标识，如：CPU1/Memory_DIMM_A1/Fan1';


--
-- Name: COLUMN alert_info.health_status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.alert_info.health_status IS '健康状态（首页核心展示），ok正常/warning警告/critical严重';


--
-- Name: COLUMN alert_info.urgency_level; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.alert_info.urgency_level IS '紧急程度（首页核心展示），urgent紧急告警/scheduled择期告警，用于首页分类显示';


--
-- Name: COLUMN alert_info.alert_status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.alert_info.alert_status IS '告警状态，active活跃告警/resolved已解决告警，用于业务流程管理';


--
-- Name: COLUMN alert_info.first_occurrence; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.alert_info.first_occurrence IS '首次发生时间，告警最初发现的时间，用于时间排序';


--
-- Name: COLUMN alert_info.last_occurrence; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.alert_info.last_occurrence IS '最后发生时间，最近一次相同告警的发生时间，用于重复告警判断';


--
-- Name: COLUMN alert_info.resolved_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.alert_info.resolved_time IS '解决时间，告警处理完成的时间，用于统计分析和排期管理';


--
-- Name: COLUMN alert_info.create_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.alert_info.create_time IS '创建时间，记录插入数据库的时间，用于数据审计';


--
-- Name: COLUMN alert_info.update_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.alert_info.update_time IS '更新时间，记录最后修改的时间，用于数据审计和变更跟踪';


--
-- Name: COLUMN alert_info.del_flag; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.alert_info.del_flag IS '删除标志（0代表存在 2代表删除）';


--
-- Name: alert_info_alert_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.alert_info_alert_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: alert_info_alert_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.alert_info_alert_id_seq OWNED BY public.alert_info.alert_id;


--
-- Name: apscheduler_jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.apscheduler_jobs (
    id character varying(191) NOT NULL,
    next_run_time double precision,
    job_state bytea NOT NULL
);


--
-- Name: business_hardware_urgency_rules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.business_hardware_urgency_rules (
    rule_id bigint NOT NULL,
    business_type character varying(50) NOT NULL,
    hardware_type character varying(50) NOT NULL,
    urgency_level character varying(20) NOT NULL,
    description character varying(200),
    is_active smallint DEFAULT 1,
    create_by character varying(64) DEFAULT ''::character varying,
    create_time timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    update_by character varying(64) DEFAULT ''::character varying,
    update_time timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE business_hardware_urgency_rules; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.business_hardware_urgency_rules IS '业务硬件紧急度规则表';


--
-- Name: COLUMN business_hardware_urgency_rules.business_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.business_hardware_urgency_rules.business_type IS '业务类型（OB/DB/WEB/APP等）';


--
-- Name: COLUMN business_hardware_urgency_rules.hardware_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.business_hardware_urgency_rules.hardware_type IS '硬件类型（cpu/memory/disk/power/fan/temperature等）';


--
-- Name: COLUMN business_hardware_urgency_rules.urgency_level; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.business_hardware_urgency_rules.urgency_level IS '紧急程度（urgent紧急/scheduled择期）';


--
-- Name: business_hardware_urgency_rules_rule_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.business_hardware_urgency_rules_rule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: business_hardware_urgency_rules_rule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.business_hardware_urgency_rules_rule_id_seq OWNED BY public.business_hardware_urgency_rules.rule_id;


--
-- Name: business_type_dict; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.business_type_dict (
    type_id bigint NOT NULL,
    type_code character varying(50) NOT NULL,
    type_name character varying(100) NOT NULL,
    type_description character varying(200),
    sort_order integer DEFAULT 0,
    is_active smallint DEFAULT 1,
    create_by character varying(64) DEFAULT ''::character varying,
    create_time timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    update_by character varying(64) DEFAULT ''::character varying,
    update_time timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE business_type_dict; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.business_type_dict IS '业务类型字典表';


--
-- Name: COLUMN business_type_dict.type_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.business_type_dict.type_id IS '类型ID';


--
-- Name: COLUMN business_type_dict.type_code; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.business_type_dict.type_code IS '类型编码';


--
-- Name: COLUMN business_type_dict.type_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.business_type_dict.type_name IS '类型名称';


--
-- Name: COLUMN business_type_dict.type_description; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.business_type_dict.type_description IS '类型描述';


--
-- Name: COLUMN business_type_dict.sort_order; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.business_type_dict.sort_order IS '排序顺序';


--
-- Name: COLUMN business_type_dict.is_active; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.business_type_dict.is_active IS '是否启用（1启用/0禁用）';


--
-- Name: business_type_dict_type_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.business_type_dict_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: business_type_dict_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.business_type_dict_type_id_seq OWNED BY public.business_type_dict.type_id;


--
-- Name: device_info; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.device_info (
    device_id bigint NOT NULL,
    hostname character varying(100),
    business_ip character varying(45),
    oob_ip character varying(45) NOT NULL,
    oob_port integer DEFAULT 443,
    location character varying(200) NOT NULL,
    operating_system character varying(100),
    serial_number character varying(100),
    model character varying(100),
    manufacturer character varying(100),
    technical_system character varying(100),
    system_owner character varying(100),
    business_type character varying(50),
    redfish_username character varying(100),
    redfish_password character varying(255),
    monitor_enabled smallint DEFAULT 1,
    last_check_time timestamp(0) without time zone,
    health_status character varying(20) DEFAULT 'unknown'::character varying,
    create_by character varying(64) DEFAULT ''::character varying,
    create_time timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    update_by character varying(64) DEFAULT ''::character varying,
    update_time timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    remark character varying(500)
);


--
-- Name: TABLE device_info; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.device_info IS '设备信息表';


--
-- Name: COLUMN device_info.device_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.device_info.device_id IS '设备ID';


--
-- Name: COLUMN device_info.hostname; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.device_info.hostname IS '主机名';


--
-- Name: COLUMN device_info.business_ip; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.device_info.business_ip IS '业务IP地址';


--
-- Name: COLUMN device_info.oob_ip; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.device_info.oob_ip IS '带外IP地址（BMC IP）';


--
-- Name: COLUMN device_info.location; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.device_info.location IS '机房位置（格式：XW_B1B04_21-24）';


--
-- Name: COLUMN device_info.operating_system; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.device_info.operating_system IS '操作系统';


--
-- Name: COLUMN device_info.serial_number; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.device_info.serial_number IS '序列号';


--
-- Name: COLUMN device_info.model; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.device_info.model IS '设备型号';


--
-- Name: COLUMN device_info.manufacturer; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.device_info.manufacturer IS '厂商';


--
-- Name: COLUMN device_info.technical_system; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.device_info.technical_system IS '技术系统';


--
-- Name: COLUMN device_info.system_owner; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.device_info.system_owner IS '系统负责人';


--
-- Name: COLUMN device_info.business_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.device_info.business_type IS '业务类型（OB/DB/WEB/APP等）';


--
-- Name: COLUMN device_info.redfish_username; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.device_info.redfish_username IS 'Redfish用户名';


--
-- Name: COLUMN device_info.redfish_password; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.device_info.redfish_password IS 'Redfish密码';


--
-- Name: COLUMN device_info.monitor_enabled; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.device_info.monitor_enabled IS '是否启用监控（1启用/0禁用）';


--
-- Name: COLUMN device_info.last_check_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.device_info.last_check_time IS '最后检查时间';


--
-- Name: COLUMN device_info.health_status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.device_info.health_status IS '健康状态（ok正常/warning警告/critical严重/unknown未知）';


--
-- Name: device_info_device_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.device_info_device_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: device_info_device_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.device_info_device_id_seq OWNED BY public.device_info.device_id;


--
-- Name: gen_table; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.gen_table (
    table_id bigint NOT NULL,
    table_name character varying(200) DEFAULT ''::character varying,
    table_comment character varying(500) DEFAULT ''::character varying,
    sub_table_name character varying(64) DEFAULT NULL::character varying,
    sub_table_fk_name character varying(64) DEFAULT NULL::character varying,
    class_name character varying(100) DEFAULT ''::character varying,
    tpl_category character varying(200) DEFAULT 'crud'::character varying,
    tpl_web_type character varying(30) DEFAULT ''::character varying,
    package_name character varying(100),
    module_name character varying(30),
    business_name character varying(30),
    function_name character varying(50),
    function_author character varying(50),
    gen_type character(1) DEFAULT '0'::bpchar,
    gen_path character varying(200) DEFAULT '/'::character varying,
    options character varying(1000),
    create_by character varying(64) DEFAULT ''::character varying,
    create_time timestamp(0) without time zone,
    update_by character varying(64) DEFAULT ''::character varying,
    update_time timestamp(0) without time zone,
    remark character varying(500) DEFAULT NULL::character varying
);


--
-- Name: TABLE gen_table; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.gen_table IS '代码生成业务表';


--
-- Name: COLUMN gen_table.table_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table.table_id IS '编号';


--
-- Name: COLUMN gen_table.table_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table.table_name IS '表名称';


--
-- Name: COLUMN gen_table.table_comment; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table.table_comment IS '表描述';


--
-- Name: COLUMN gen_table.sub_table_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table.sub_table_name IS '关联子表的表名';


--
-- Name: COLUMN gen_table.sub_table_fk_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table.sub_table_fk_name IS '子表关联的外键名';


--
-- Name: COLUMN gen_table.class_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table.class_name IS '实体类名称';


--
-- Name: COLUMN gen_table.tpl_category; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table.tpl_category IS '使用的模板（crud单表操作 tree树表操作）';


--
-- Name: COLUMN gen_table.tpl_web_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table.tpl_web_type IS '前端模板类型（element-ui模版 element-plus模版）';


--
-- Name: COLUMN gen_table.package_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table.package_name IS '生成包路径';


--
-- Name: COLUMN gen_table.module_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table.module_name IS '生成模块名';


--
-- Name: COLUMN gen_table.business_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table.business_name IS '生成业务名';


--
-- Name: COLUMN gen_table.function_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table.function_name IS '生成功能名';


--
-- Name: COLUMN gen_table.function_author; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table.function_author IS '生成功能作者';


--
-- Name: COLUMN gen_table.gen_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table.gen_type IS '生成代码方式（0zip压缩包 1自定义路径）';


--
-- Name: COLUMN gen_table.gen_path; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table.gen_path IS '生成路径（不填默认项目路径）';


--
-- Name: COLUMN gen_table.options; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table.options IS '其它生成选项';


--
-- Name: COLUMN gen_table.create_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table.create_by IS '创建者';


--
-- Name: COLUMN gen_table.create_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table.create_time IS '创建时间';


--
-- Name: COLUMN gen_table.update_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table.update_by IS '更新者';


--
-- Name: COLUMN gen_table.update_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table.update_time IS '更新时间';


--
-- Name: COLUMN gen_table.remark; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table.remark IS '备注';


--
-- Name: gen_table_column; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.gen_table_column (
    column_id bigint NOT NULL,
    table_id bigint,
    column_name character varying(200),
    column_comment character varying(500),
    column_type character varying(100),
    python_type character varying(500),
    python_field character varying(200),
    is_pk character(1),
    is_increment character(1),
    is_required character(1),
    is_unique character(1),
    is_insert character(1),
    is_edit character(1),
    is_list character(1),
    is_query character(1),
    query_type character varying(200) DEFAULT 'EQ'::character varying,
    html_type character varying(200),
    dict_type character varying(200) DEFAULT ''::character varying,
    sort integer,
    create_by character varying(64) DEFAULT ''::character varying,
    create_time timestamp(0) without time zone,
    update_by character varying(64) DEFAULT ''::character varying,
    update_time timestamp(0) without time zone
);


--
-- Name: TABLE gen_table_column; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.gen_table_column IS '代码生成业务表字段';


--
-- Name: COLUMN gen_table_column.column_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.column_id IS '编号';


--
-- Name: COLUMN gen_table_column.table_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.table_id IS '归属表编号';


--
-- Name: COLUMN gen_table_column.column_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.column_name IS '列名称';


--
-- Name: COLUMN gen_table_column.column_comment; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.column_comment IS '列描述';


--
-- Name: COLUMN gen_table_column.column_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.column_type IS '列类型';


--
-- Name: COLUMN gen_table_column.python_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.python_type IS 'PYTHON类型';


--
-- Name: COLUMN gen_table_column.python_field; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.python_field IS 'PYTHON字段名';


--
-- Name: COLUMN gen_table_column.is_pk; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.is_pk IS '是否主键（1是）';


--
-- Name: COLUMN gen_table_column.is_increment; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.is_increment IS '是否自增（1是）';


--
-- Name: COLUMN gen_table_column.is_required; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.is_required IS '是否必填（1是）';


--
-- Name: COLUMN gen_table_column.is_unique; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.is_unique IS '是否唯一（1是）';


--
-- Name: COLUMN gen_table_column.is_insert; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.is_insert IS '是否为插入字段（1是）';


--
-- Name: COLUMN gen_table_column.is_edit; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.is_edit IS '是否编辑字段（1是）';


--
-- Name: COLUMN gen_table_column.is_list; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.is_list IS '是否列表字段（1是）';


--
-- Name: COLUMN gen_table_column.is_query; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.is_query IS '是否查询字段（1是）';


--
-- Name: COLUMN gen_table_column.query_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.query_type IS '查询方式（等于、不等于、大于、小于、范围）';


--
-- Name: COLUMN gen_table_column.html_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.html_type IS '显示类型（文本框、文本域、下拉框、复选框、单选框、日期控件）';


--
-- Name: COLUMN gen_table_column.dict_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.dict_type IS '字典类型';


--
-- Name: COLUMN gen_table_column.sort; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.sort IS '排序';


--
-- Name: COLUMN gen_table_column.create_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.create_by IS '创建者';


--
-- Name: COLUMN gen_table_column.create_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.create_time IS '创建时间';


--
-- Name: COLUMN gen_table_column.update_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.update_by IS '更新者';


--
-- Name: COLUMN gen_table_column.update_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.gen_table_column.update_time IS '更新时间';


--
-- Name: gen_table_column_column_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.gen_table_column_column_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: gen_table_column_column_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.gen_table_column_column_id_seq OWNED BY public.gen_table_column.column_id;


--
-- Name: gen_table_table_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.gen_table_table_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: gen_table_table_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.gen_table_table_id_seq OWNED BY public.gen_table.table_id;


--
-- Name: hardware_type_dict; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hardware_type_dict (
    type_id bigint NOT NULL,
    type_code character varying(50) NOT NULL,
    type_name character varying(100) NOT NULL,
    type_description character varying(200),
    category character varying(50),
    sort_order integer DEFAULT 0,
    is_active smallint DEFAULT 1,
    create_by character varying(64) DEFAULT ''::character varying,
    create_time timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    update_by character varying(64) DEFAULT ''::character varying,
    update_time timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE hardware_type_dict; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.hardware_type_dict IS '硬件类型字典表';


--
-- Name: COLUMN hardware_type_dict.type_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.hardware_type_dict.type_id IS '类型ID';


--
-- Name: COLUMN hardware_type_dict.type_code; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.hardware_type_dict.type_code IS '类型编码';


--
-- Name: COLUMN hardware_type_dict.type_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.hardware_type_dict.type_name IS '类型名称';


--
-- Name: COLUMN hardware_type_dict.type_description; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.hardware_type_dict.type_description IS '类型描述';


--
-- Name: COLUMN hardware_type_dict.category; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.hardware_type_dict.category IS '硬件分类';


--
-- Name: COLUMN hardware_type_dict.sort_order; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.hardware_type_dict.sort_order IS '排序顺序';


--
-- Name: COLUMN hardware_type_dict.is_active; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.hardware_type_dict.is_active IS '是否启用（1启用/0禁用）';


--
-- Name: hardware_type_dict_type_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hardware_type_dict_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hardware_type_dict_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hardware_type_dict_type_id_seq OWNED BY public.hardware_type_dict.type_id;


--
-- Name: maintenance_schedule; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.maintenance_schedule (
    schedule_id bigint NOT NULL,
    device_id bigint NOT NULL,
    component_type character varying(50) NOT NULL,
    component_name character varying(100),
    component_serial character varying(100),
    maintenance_type character varying(20) NOT NULL,
    priority_level character varying(20) NOT NULL,
    scheduled_date timestamp without time zone NOT NULL,
    estimated_duration integer,
    responsible_person character varying(100) NOT NULL,
    contact_phone character varying(20),
    status character varying(20),
    description text,
    pre_check_result text,
    maintenance_result text,
    actual_start_time timestamp without time zone,
    actual_end_time timestamp without time zone,
    create_time timestamp without time zone,
    update_time timestamp without time zone,
    remarks character varying(500)
);


--
-- Name: COLUMN maintenance_schedule.schedule_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.maintenance_schedule.schedule_id IS '排期ID';


--
-- Name: COLUMN maintenance_schedule.device_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.maintenance_schedule.device_id IS '设备ID';


--
-- Name: COLUMN maintenance_schedule.component_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.maintenance_schedule.component_type IS '组件类型';


--
-- Name: COLUMN maintenance_schedule.component_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.maintenance_schedule.component_name IS '组件名称';


--
-- Name: COLUMN maintenance_schedule.component_serial; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.maintenance_schedule.component_serial IS '组件序列号';


--
-- Name: COLUMN maintenance_schedule.maintenance_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.maintenance_schedule.maintenance_type IS '维护类型：replace=更换，repair=维修，upgrade=升级';


--
-- Name: COLUMN maintenance_schedule.priority_level; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.maintenance_schedule.priority_level IS '优先级：urgent=紧急，normal=正常，deferred=择期';


--
-- Name: COLUMN maintenance_schedule.scheduled_date; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.maintenance_schedule.scheduled_date IS '计划日期';


--
-- Name: COLUMN maintenance_schedule.estimated_duration; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.maintenance_schedule.estimated_duration IS '预计耗时（分钟）';


--
-- Name: COLUMN maintenance_schedule.responsible_person; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.maintenance_schedule.responsible_person IS '负责人';


--
-- Name: COLUMN maintenance_schedule.contact_phone; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.maintenance_schedule.contact_phone IS '联系电话';


--
-- Name: COLUMN maintenance_schedule.status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.maintenance_schedule.status IS '状态：pending=待执行，in_progress=执行中，completed=已完成，cancelled=已取消';


--
-- Name: COLUMN maintenance_schedule.description; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.maintenance_schedule.description IS '描述';


--
-- Name: COLUMN maintenance_schedule.pre_check_result; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.maintenance_schedule.pre_check_result IS '预检结果';


--
-- Name: COLUMN maintenance_schedule.maintenance_result; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.maintenance_schedule.maintenance_result IS '维护结果';


--
-- Name: COLUMN maintenance_schedule.actual_start_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.maintenance_schedule.actual_start_time IS '实际开始时间';


--
-- Name: COLUMN maintenance_schedule.actual_end_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.maintenance_schedule.actual_end_time IS '实际结束时间';


--
-- Name: COLUMN maintenance_schedule.create_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.maintenance_schedule.create_time IS '创建时间';


--
-- Name: COLUMN maintenance_schedule.update_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.maintenance_schedule.update_time IS '更新时间';


--
-- Name: COLUMN maintenance_schedule.remarks; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.maintenance_schedule.remarks IS '备注';


--
-- Name: maintenance_schedule_schedule_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.maintenance_schedule_schedule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: maintenance_schedule_schedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.maintenance_schedule_schedule_id_seq OWNED BY public.maintenance_schedule.schedule_id;


--
-- Name: redfish_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.redfish_log (
    log_id uuid DEFAULT gen_random_uuid() NOT NULL,
    device_id integer NOT NULL,
    device_ip character varying(45) NOT NULL,
    entry_id character varying(100),
    entry_type character varying(50),
    log_source character varying(10) NOT NULL,
    severity character varying(20) NOT NULL,
    created_time timestamp without time zone NOT NULL,
    collected_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    message text,
    create_by character varying(50),
    create_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    update_by character varying(50),
    update_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    remark text
);


--
-- Name: TABLE redfish_log; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.redfish_log IS 'Redfish设备日志表';


--
-- Name: COLUMN redfish_log.log_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.redfish_log.log_id IS '日志ID';


--
-- Name: COLUMN redfish_log.device_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.redfish_log.device_id IS '设备ID';


--
-- Name: COLUMN redfish_log.device_ip; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.redfish_log.device_ip IS '设备IP地址';


--
-- Name: COLUMN redfish_log.entry_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.redfish_log.entry_id IS '原始条目ID';


--
-- Name: COLUMN redfish_log.entry_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.redfish_log.entry_type IS '条目类型';


--
-- Name: COLUMN redfish_log.log_source; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.redfish_log.log_source IS '日志来源(SEL/MEL)';


--
-- Name: COLUMN redfish_log.severity; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.redfish_log.severity IS '严重程度(CRITICAL/WARNING)';


--
-- Name: COLUMN redfish_log.created_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.redfish_log.created_time IS '日志创建时间';


--
-- Name: COLUMN redfish_log.collected_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.redfish_log.collected_time IS '日志收集时间';


--
-- Name: COLUMN redfish_log.message; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.redfish_log.message IS '日志消息';


--
-- Name: COLUMN redfish_log.create_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.redfish_log.create_by IS '创建者';


--
-- Name: COLUMN redfish_log.create_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.redfish_log.create_time IS '创建时间';


--
-- Name: COLUMN redfish_log.update_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.redfish_log.update_by IS '更新者';


--
-- Name: COLUMN redfish_log.update_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.redfish_log.update_time IS '更新时间';


--
-- Name: COLUMN redfish_log.remark; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.redfish_log.remark IS '备注';


--
-- Name: sys_config; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sys_config (
    config_id integer NOT NULL,
    config_name character varying(100) DEFAULT ''::character varying,
    config_key character varying(100) DEFAULT ''::character varying,
    config_value character varying(500) DEFAULT ''::character varying,
    config_type character(1) DEFAULT 'N'::bpchar,
    create_by character varying(64) DEFAULT ''::character varying,
    create_time timestamp(0) without time zone,
    update_by character varying(64) DEFAULT ''::character varying,
    update_time timestamp(0) without time zone,
    remark character varying(500) DEFAULT NULL::character varying
);


--
-- Name: TABLE sys_config; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.sys_config IS '参数配置表';


--
-- Name: COLUMN sys_config.config_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_config.config_id IS '参数主键';


--
-- Name: COLUMN sys_config.config_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_config.config_name IS '参数名称';


--
-- Name: COLUMN sys_config.config_key; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_config.config_key IS '参数键名';


--
-- Name: COLUMN sys_config.config_value; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_config.config_value IS '参数键值';


--
-- Name: COLUMN sys_config.config_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_config.config_type IS '系统内置（Y是 N否）';


--
-- Name: COLUMN sys_config.create_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_config.create_by IS '创建者';


--
-- Name: COLUMN sys_config.create_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_config.create_time IS '创建时间';


--
-- Name: COLUMN sys_config.update_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_config.update_by IS '更新者';


--
-- Name: COLUMN sys_config.update_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_config.update_time IS '更新时间';


--
-- Name: COLUMN sys_config.remark; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_config.remark IS '备注';


--
-- Name: sys_config_config_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sys_config_config_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sys_config_config_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sys_config_config_id_seq OWNED BY public.sys_config.config_id;


--
-- Name: sys_dept; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sys_dept (
    dept_id bigint NOT NULL,
    parent_id bigint DEFAULT 0,
    ancestors character varying(50) DEFAULT ''::character varying,
    dept_name character varying(30) DEFAULT ''::character varying,
    order_num integer DEFAULT 0,
    leader character varying(20) DEFAULT NULL::character varying,
    phone character varying(11) DEFAULT NULL::character varying,
    email character varying(50) DEFAULT NULL::character varying,
    status character(1) DEFAULT '0'::bpchar,
    del_flag character(1) DEFAULT '0'::bpchar,
    create_by character varying(64) DEFAULT ''::character varying,
    create_time timestamp(0) without time zone,
    update_by character varying(64) DEFAULT ''::character varying,
    update_time timestamp(0) without time zone
);


--
-- Name: TABLE sys_dept; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.sys_dept IS '部门表';


--
-- Name: COLUMN sys_dept.dept_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dept.dept_id IS '部门id';


--
-- Name: COLUMN sys_dept.parent_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dept.parent_id IS '父部门id';


--
-- Name: COLUMN sys_dept.ancestors; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dept.ancestors IS '祖级列表';


--
-- Name: COLUMN sys_dept.dept_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dept.dept_name IS '部门名称';


--
-- Name: COLUMN sys_dept.order_num; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dept.order_num IS '显示顺序';


--
-- Name: COLUMN sys_dept.leader; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dept.leader IS '负责人';


--
-- Name: COLUMN sys_dept.phone; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dept.phone IS '联系电话';


--
-- Name: COLUMN sys_dept.email; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dept.email IS '邮箱';


--
-- Name: COLUMN sys_dept.status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dept.status IS '部门状态（0正常 1停用）';


--
-- Name: COLUMN sys_dept.del_flag; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dept.del_flag IS '删除标志（0代表存在 2代表删除）';


--
-- Name: COLUMN sys_dept.create_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dept.create_by IS '创建者';


--
-- Name: COLUMN sys_dept.create_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dept.create_time IS '创建时间';


--
-- Name: COLUMN sys_dept.update_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dept.update_by IS '更新者';


--
-- Name: COLUMN sys_dept.update_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dept.update_time IS '更新时间';


--
-- Name: sys_dept_dept_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sys_dept_dept_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sys_dept_dept_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sys_dept_dept_id_seq OWNED BY public.sys_dept.dept_id;


--
-- Name: sys_dict_data; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sys_dict_data (
    dict_code bigint NOT NULL,
    dict_sort integer DEFAULT 0,
    dict_label character varying(100) DEFAULT ''::character varying,
    dict_value character varying(100) DEFAULT ''::character varying,
    dict_type character varying(100) DEFAULT ''::character varying,
    css_class character varying(100) DEFAULT NULL::character varying,
    list_class character varying(100) DEFAULT NULL::character varying,
    is_default character(1) DEFAULT 'N'::bpchar,
    status character(1) DEFAULT '0'::bpchar,
    create_by character varying(64) DEFAULT ''::character varying,
    create_time timestamp(0) without time zone,
    update_by character varying(64) DEFAULT ''::character varying,
    update_time timestamp(0) without time zone,
    remark character varying(500) DEFAULT NULL::character varying
);


--
-- Name: TABLE sys_dict_data; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.sys_dict_data IS '字典数据表';


--
-- Name: COLUMN sys_dict_data.dict_code; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_data.dict_code IS '字典编码';


--
-- Name: COLUMN sys_dict_data.dict_sort; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_data.dict_sort IS '字典排序';


--
-- Name: COLUMN sys_dict_data.dict_label; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_data.dict_label IS '字典标签';


--
-- Name: COLUMN sys_dict_data.dict_value; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_data.dict_value IS '字典键值';


--
-- Name: COLUMN sys_dict_data.dict_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_data.dict_type IS '字典类型';


--
-- Name: COLUMN sys_dict_data.css_class; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_data.css_class IS '样式属性（其他样式扩展）';


--
-- Name: COLUMN sys_dict_data.list_class; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_data.list_class IS '表格回显样式';


--
-- Name: COLUMN sys_dict_data.is_default; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_data.is_default IS '是否默认（Y是 N否）';


--
-- Name: COLUMN sys_dict_data.status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_data.status IS '状态（0正常 1停用）';


--
-- Name: COLUMN sys_dict_data.create_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_data.create_by IS '创建者';


--
-- Name: COLUMN sys_dict_data.create_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_data.create_time IS '创建时间';


--
-- Name: COLUMN sys_dict_data.update_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_data.update_by IS '更新者';


--
-- Name: COLUMN sys_dict_data.update_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_data.update_time IS '更新时间';


--
-- Name: COLUMN sys_dict_data.remark; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_data.remark IS '备注';


--
-- Name: sys_dict_data_dict_code_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sys_dict_data_dict_code_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sys_dict_data_dict_code_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sys_dict_data_dict_code_seq OWNED BY public.sys_dict_data.dict_code;


--
-- Name: sys_dict_type; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sys_dict_type (
    dict_id bigint NOT NULL,
    dict_name character varying(100) DEFAULT ''::character varying,
    dict_type character varying(100) DEFAULT ''::character varying,
    status character(1) DEFAULT '0'::bpchar,
    create_by character varying(64) DEFAULT ''::character varying,
    create_time timestamp(0) without time zone,
    update_by character varying(64) DEFAULT ''::character varying,
    update_time timestamp(0) without time zone,
    remark character varying(500) DEFAULT NULL::character varying
);


--
-- Name: TABLE sys_dict_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.sys_dict_type IS '字典类型表';


--
-- Name: COLUMN sys_dict_type.dict_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_type.dict_id IS '字典主键';


--
-- Name: COLUMN sys_dict_type.dict_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_type.dict_name IS '字典名称';


--
-- Name: COLUMN sys_dict_type.dict_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_type.dict_type IS '字典类型';


--
-- Name: COLUMN sys_dict_type.status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_type.status IS '状态（0正常 1停用）';


--
-- Name: COLUMN sys_dict_type.create_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_type.create_by IS '创建者';


--
-- Name: COLUMN sys_dict_type.create_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_type.create_time IS '创建时间';


--
-- Name: COLUMN sys_dict_type.update_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_type.update_by IS '更新者';


--
-- Name: COLUMN sys_dict_type.update_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_type.update_time IS '更新时间';


--
-- Name: COLUMN sys_dict_type.remark; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_dict_type.remark IS '备注';


--
-- Name: sys_dict_type_dict_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sys_dict_type_dict_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sys_dict_type_dict_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sys_dict_type_dict_id_seq OWNED BY public.sys_dict_type.dict_id;


--
-- Name: sys_job; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sys_job (
    job_id bigint NOT NULL,
    job_name character varying(64) DEFAULT ''::character varying NOT NULL,
    job_group character varying(64) DEFAULT 'default'::character varying NOT NULL,
    job_executor character varying(64) DEFAULT 'default'::character varying,
    invoke_target character varying(500) NOT NULL,
    job_args character varying(255) DEFAULT ''::character varying,
    job_kwargs character varying(255) DEFAULT ''::character varying,
    cron_expression character varying(255) DEFAULT ''::character varying,
    misfire_policy character varying(20) DEFAULT '3'::character varying,
    concurrent character(1) DEFAULT '1'::bpchar,
    status character(1) DEFAULT '0'::bpchar,
    create_by character varying(64) DEFAULT ''::character varying,
    create_time timestamp(0) without time zone,
    update_by character varying(64) DEFAULT ''::character varying,
    update_time timestamp(0) without time zone,
    remark character varying(500) DEFAULT ''::character varying
);


--
-- Name: TABLE sys_job; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.sys_job IS '定时任务调度表';


--
-- Name: COLUMN sys_job.job_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job.job_id IS '任务ID';


--
-- Name: COLUMN sys_job.job_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job.job_name IS '任务名称';


--
-- Name: COLUMN sys_job.job_group; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job.job_group IS '任务组名';


--
-- Name: COLUMN sys_job.job_executor; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job.job_executor IS '任务执行器';


--
-- Name: COLUMN sys_job.invoke_target; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job.invoke_target IS '调用目标字符串';


--
-- Name: COLUMN sys_job.job_args; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job.job_args IS '位置参数';


--
-- Name: COLUMN sys_job.job_kwargs; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job.job_kwargs IS '关键字参数';


--
-- Name: COLUMN sys_job.cron_expression; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job.cron_expression IS 'cron执行表达式';


--
-- Name: COLUMN sys_job.misfire_policy; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job.misfire_policy IS '计划执行错误策略（1立即执行 2执行一次 3放弃执行）';


--
-- Name: COLUMN sys_job.concurrent; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job.concurrent IS '是否并发执行（0允许 1禁止）';


--
-- Name: COLUMN sys_job.status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job.status IS '状态（0正常 1暂停）';


--
-- Name: COLUMN sys_job.create_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job.create_by IS '创建者';


--
-- Name: COLUMN sys_job.create_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job.create_time IS '创建时间';


--
-- Name: COLUMN sys_job.update_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job.update_by IS '更新者';


--
-- Name: COLUMN sys_job.update_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job.update_time IS '更新时间';


--
-- Name: COLUMN sys_job.remark; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job.remark IS '备注信息';


--
-- Name: sys_job_job_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sys_job_job_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sys_job_job_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sys_job_job_id_seq OWNED BY public.sys_job.job_id;


--
-- Name: sys_job_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sys_job_log (
    job_log_id bigint NOT NULL,
    job_name character varying(64) NOT NULL,
    job_group character varying(64) NOT NULL,
    job_executor character varying(64) NOT NULL,
    invoke_target character varying(500) NOT NULL,
    job_args character varying(255) DEFAULT ''::character varying,
    job_kwargs character varying(255) DEFAULT ''::character varying,
    job_trigger character varying(255) DEFAULT ''::character varying,
    job_message character varying(500),
    status character(1) DEFAULT '0'::bpchar,
    exception_info character varying(2000) DEFAULT ''::character varying,
    create_time timestamp(0) without time zone
);


--
-- Name: TABLE sys_job_log; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.sys_job_log IS '定时任务调度日志表';


--
-- Name: COLUMN sys_job_log.job_log_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job_log.job_log_id IS '任务日志ID';


--
-- Name: COLUMN sys_job_log.job_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job_log.job_name IS '任务名称';


--
-- Name: COLUMN sys_job_log.job_group; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job_log.job_group IS '任务组名';


--
-- Name: COLUMN sys_job_log.job_executor; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job_log.job_executor IS '任务执行器';


--
-- Name: COLUMN sys_job_log.invoke_target; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job_log.invoke_target IS '调用目标字符串';


--
-- Name: COLUMN sys_job_log.job_args; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job_log.job_args IS '位置参数';


--
-- Name: COLUMN sys_job_log.job_kwargs; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job_log.job_kwargs IS '关键字参数';


--
-- Name: COLUMN sys_job_log.job_trigger; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job_log.job_trigger IS '任务触发器';


--
-- Name: COLUMN sys_job_log.job_message; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job_log.job_message IS '日志信息';


--
-- Name: COLUMN sys_job_log.status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job_log.status IS '执行状态（0正常 1失败）';


--
-- Name: COLUMN sys_job_log.exception_info; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job_log.exception_info IS '异常信息';


--
-- Name: COLUMN sys_job_log.create_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_job_log.create_time IS '创建时间';


--
-- Name: sys_job_log_job_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sys_job_log_job_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sys_job_log_job_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sys_job_log_job_log_id_seq OWNED BY public.sys_job_log.job_log_id;


--
-- Name: sys_logininfor; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sys_logininfor (
    info_id bigint NOT NULL,
    user_name character varying(50) DEFAULT ''::character varying,
    ipaddr character varying(128) DEFAULT ''::character varying,
    login_location character varying(255) DEFAULT ''::character varying,
    browser character varying(50) DEFAULT ''::character varying,
    os character varying(50) DEFAULT ''::character varying,
    status character(1) DEFAULT '0'::bpchar,
    msg character varying(255) DEFAULT ''::character varying,
    login_time timestamp(0) without time zone
);


--
-- Name: TABLE sys_logininfor; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.sys_logininfor IS '系统访问记录';


--
-- Name: COLUMN sys_logininfor.info_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_logininfor.info_id IS '访问ID';


--
-- Name: COLUMN sys_logininfor.user_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_logininfor.user_name IS '用户账号';


--
-- Name: COLUMN sys_logininfor.ipaddr; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_logininfor.ipaddr IS '登录IP地址';


--
-- Name: COLUMN sys_logininfor.login_location; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_logininfor.login_location IS '登录地点';


--
-- Name: COLUMN sys_logininfor.browser; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_logininfor.browser IS '浏览器类型';


--
-- Name: COLUMN sys_logininfor.os; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_logininfor.os IS '操作系统';


--
-- Name: COLUMN sys_logininfor.status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_logininfor.status IS '登录状态（0成功 1失败）';


--
-- Name: COLUMN sys_logininfor.msg; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_logininfor.msg IS '提示消息';


--
-- Name: COLUMN sys_logininfor.login_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_logininfor.login_time IS '访问时间';


--
-- Name: sys_logininfor_info_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sys_logininfor_info_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sys_logininfor_info_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sys_logininfor_info_id_seq OWNED BY public.sys_logininfor.info_id;


--
-- Name: sys_menu; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sys_menu (
    menu_id bigint NOT NULL,
    menu_name character varying(50) NOT NULL,
    parent_id bigint DEFAULT 0,
    order_num integer DEFAULT 0,
    path character varying(200) DEFAULT ''::character varying,
    component character varying(255) DEFAULT NULL::character varying,
    query character varying(255) DEFAULT NULL::character varying,
    route_name character varying(50) DEFAULT ''::character varying,
    is_frame integer DEFAULT 1,
    is_cache integer DEFAULT 0,
    menu_type character(1) DEFAULT ''::bpchar,
    visible character(1) DEFAULT '0'::bpchar,
    status character(1) DEFAULT '0'::bpchar,
    perms character varying(100) DEFAULT NULL::character varying,
    icon character varying(100) DEFAULT '#'::character varying,
    create_by character varying(64) DEFAULT ''::character varying,
    create_time timestamp(0) without time zone,
    update_by character varying(64) DEFAULT ''::character varying,
    update_time timestamp(0) without time zone,
    remark character varying(500) DEFAULT ''::character varying
);


--
-- Name: TABLE sys_menu; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.sys_menu IS '菜单权限表';


--
-- Name: COLUMN sys_menu.menu_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_menu.menu_id IS '菜单ID';


--
-- Name: COLUMN sys_menu.menu_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_menu.menu_name IS '菜单名称';


--
-- Name: COLUMN sys_menu.parent_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_menu.parent_id IS '父菜单ID';


--
-- Name: COLUMN sys_menu.order_num; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_menu.order_num IS '显示顺序';


--
-- Name: COLUMN sys_menu.path; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_menu.path IS '路由地址';


--
-- Name: COLUMN sys_menu.component; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_menu.component IS '组件路径';


--
-- Name: COLUMN sys_menu.query; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_menu.query IS '路由参数';


--
-- Name: COLUMN sys_menu.route_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_menu.route_name IS '路由名称';


--
-- Name: COLUMN sys_menu.is_frame; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_menu.is_frame IS '是否为外链（0是 1否）';


--
-- Name: COLUMN sys_menu.is_cache; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_menu.is_cache IS '是否缓存（0缓存 1不缓存）';


--
-- Name: COLUMN sys_menu.menu_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_menu.menu_type IS '菜单类型（M目录 C菜单 F按钮）';


--
-- Name: COLUMN sys_menu.visible; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_menu.visible IS '菜单状态（0显示 1隐藏）';


--
-- Name: COLUMN sys_menu.status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_menu.status IS '菜单状态（0正常 1停用）';


--
-- Name: COLUMN sys_menu.perms; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_menu.perms IS '权限标识';


--
-- Name: COLUMN sys_menu.icon; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_menu.icon IS '菜单图标';


--
-- Name: COLUMN sys_menu.create_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_menu.create_by IS '创建者';


--
-- Name: COLUMN sys_menu.create_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_menu.create_time IS '创建时间';


--
-- Name: COLUMN sys_menu.update_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_menu.update_by IS '更新者';


--
-- Name: COLUMN sys_menu.update_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_menu.update_time IS '更新时间';


--
-- Name: COLUMN sys_menu.remark; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_menu.remark IS '备注';


--
-- Name: sys_menu_menu_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sys_menu_menu_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sys_menu_menu_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sys_menu_menu_id_seq OWNED BY public.sys_menu.menu_id;


--
-- Name: sys_notice; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sys_notice (
    notice_id integer NOT NULL,
    notice_title character varying(50) NOT NULL,
    notice_type character(1) NOT NULL,
    notice_content bytea,
    status character(1) DEFAULT '0'::bpchar,
    create_by character varying(64) DEFAULT ''::character varying,
    create_time timestamp(0) without time zone,
    update_by character varying(64) DEFAULT ''::character varying,
    update_time timestamp(0) without time zone,
    remark character varying(255) DEFAULT NULL::character varying
);


--
-- Name: TABLE sys_notice; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.sys_notice IS '通知公告表';


--
-- Name: COLUMN sys_notice.notice_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_notice.notice_id IS '公告ID';


--
-- Name: COLUMN sys_notice.notice_title; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_notice.notice_title IS '公告标题';


--
-- Name: COLUMN sys_notice.notice_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_notice.notice_type IS '公告类型（1通知 2公告）';


--
-- Name: COLUMN sys_notice.notice_content; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_notice.notice_content IS '公告内容';


--
-- Name: COLUMN sys_notice.status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_notice.status IS '公告状态（0正常 1关闭）';


--
-- Name: COLUMN sys_notice.create_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_notice.create_by IS '创建者';


--
-- Name: COLUMN sys_notice.create_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_notice.create_time IS '创建时间';


--
-- Name: COLUMN sys_notice.update_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_notice.update_by IS '更新者';


--
-- Name: COLUMN sys_notice.update_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_notice.update_time IS '更新时间';


--
-- Name: COLUMN sys_notice.remark; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_notice.remark IS '备注';


--
-- Name: sys_notice_notice_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sys_notice_notice_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sys_notice_notice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sys_notice_notice_id_seq OWNED BY public.sys_notice.notice_id;


--
-- Name: sys_oper_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sys_oper_log (
    oper_id bigint NOT NULL,
    title character varying(50) DEFAULT ''::character varying,
    business_type integer DEFAULT 0,
    method character varying(100) DEFAULT ''::character varying,
    request_method character varying(10) DEFAULT ''::character varying,
    operator_type integer DEFAULT 0,
    oper_name character varying(50) DEFAULT ''::character varying,
    dept_name character varying(50) DEFAULT ''::character varying,
    oper_url character varying(255) DEFAULT ''::character varying,
    oper_ip character varying(128) DEFAULT ''::character varying,
    oper_location character varying(255) DEFAULT ''::character varying,
    oper_param character varying(2000) DEFAULT ''::character varying,
    json_result character varying(2000) DEFAULT ''::character varying,
    status integer DEFAULT 0,
    error_msg character varying(2000) DEFAULT ''::character varying,
    oper_time timestamp(0) without time zone,
    cost_time bigint DEFAULT 0
);


--
-- Name: TABLE sys_oper_log; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.sys_oper_log IS '操作日志记录';


--
-- Name: COLUMN sys_oper_log.oper_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_oper_log.oper_id IS '日志主键';


--
-- Name: COLUMN sys_oper_log.title; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_oper_log.title IS '模块标题';


--
-- Name: COLUMN sys_oper_log.business_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_oper_log.business_type IS '业务类型（0其它 1新增 2修改 3删除）';


--
-- Name: COLUMN sys_oper_log.method; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_oper_log.method IS '方法名称';


--
-- Name: COLUMN sys_oper_log.request_method; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_oper_log.request_method IS '请求方式';


--
-- Name: COLUMN sys_oper_log.operator_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_oper_log.operator_type IS '操作类别（0其它 1后台用户 2手机端用户）';


--
-- Name: COLUMN sys_oper_log.oper_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_oper_log.oper_name IS '操作人员';


--
-- Name: COLUMN sys_oper_log.dept_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_oper_log.dept_name IS '部门名称';


--
-- Name: COLUMN sys_oper_log.oper_url; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_oper_log.oper_url IS '请求URL';


--
-- Name: COLUMN sys_oper_log.oper_ip; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_oper_log.oper_ip IS '主机地址';


--
-- Name: COLUMN sys_oper_log.oper_location; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_oper_log.oper_location IS '操作地点';


--
-- Name: COLUMN sys_oper_log.oper_param; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_oper_log.oper_param IS '请求参数';


--
-- Name: COLUMN sys_oper_log.json_result; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_oper_log.json_result IS '返回参数';


--
-- Name: COLUMN sys_oper_log.status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_oper_log.status IS '操作状态（0正常 1异常）';


--
-- Name: COLUMN sys_oper_log.error_msg; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_oper_log.error_msg IS '错误消息';


--
-- Name: COLUMN sys_oper_log.oper_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_oper_log.oper_time IS '操作时间';


--
-- Name: sys_oper_log_oper_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sys_oper_log_oper_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sys_oper_log_oper_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sys_oper_log_oper_id_seq OWNED BY public.sys_oper_log.oper_id;


--
-- Name: sys_post; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sys_post (
    post_id bigint NOT NULL,
    post_code character varying(64) NOT NULL,
    post_name character varying(50) NOT NULL,
    post_sort integer NOT NULL,
    status character(1) NOT NULL,
    create_by character varying(64) DEFAULT ''::character varying,
    create_time timestamp(0) without time zone,
    update_by character varying(64) DEFAULT ''::character varying,
    update_time timestamp(0) without time zone,
    remark character varying(500) DEFAULT NULL::character varying
);


--
-- Name: TABLE sys_post; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.sys_post IS '岗位信息表';


--
-- Name: COLUMN sys_post.post_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_post.post_id IS '岗位ID';


--
-- Name: COLUMN sys_post.post_code; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_post.post_code IS '岗位编码';


--
-- Name: COLUMN sys_post.post_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_post.post_name IS '岗位名称';


--
-- Name: COLUMN sys_post.post_sort; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_post.post_sort IS '显示顺序';


--
-- Name: COLUMN sys_post.status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_post.status IS '状态（0正常 1停用）';


--
-- Name: COLUMN sys_post.create_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_post.create_by IS '创建者';


--
-- Name: COLUMN sys_post.create_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_post.create_time IS '创建时间';


--
-- Name: COLUMN sys_post.update_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_post.update_by IS '更新者';


--
-- Name: COLUMN sys_post.update_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_post.update_time IS '更新时间';


--
-- Name: COLUMN sys_post.remark; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_post.remark IS '备注';


--
-- Name: sys_post_post_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sys_post_post_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sys_post_post_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sys_post_post_id_seq OWNED BY public.sys_post.post_id;


--
-- Name: sys_role; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sys_role (
    role_id bigint NOT NULL,
    role_name character varying(30) NOT NULL,
    role_key character varying(100) NOT NULL,
    role_sort integer NOT NULL,
    data_scope character(1) DEFAULT '1'::bpchar,
    menu_check_strictly smallint DEFAULT 1,
    dept_check_strictly smallint DEFAULT 1,
    status character(1) NOT NULL,
    del_flag character(1) DEFAULT '0'::bpchar,
    create_by character varying(64) DEFAULT ''::character varying,
    create_time timestamp(0) without time zone,
    update_by character varying(64) DEFAULT ''::character varying,
    update_time timestamp(0) without time zone,
    remark character varying(500) DEFAULT NULL::character varying
);


--
-- Name: TABLE sys_role; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.sys_role IS '角色信息表';


--
-- Name: COLUMN sys_role.role_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_role.role_id IS '角色ID';


--
-- Name: COLUMN sys_role.role_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_role.role_name IS '角色名称';


--
-- Name: COLUMN sys_role.role_key; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_role.role_key IS '角色权限字符串';


--
-- Name: COLUMN sys_role.role_sort; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_role.role_sort IS '显示顺序';


--
-- Name: COLUMN sys_role.data_scope; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_role.data_scope IS '数据范围（1：全部数据权限 2：自定数据权限 3：本部门数据权限 4：本部门及以下数据权限）';


--
-- Name: COLUMN sys_role.menu_check_strictly; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_role.menu_check_strictly IS '菜单树选择项是否关联显示';


--
-- Name: COLUMN sys_role.dept_check_strictly; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_role.dept_check_strictly IS '部门树选择项是否关联显示';


--
-- Name: COLUMN sys_role.status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_role.status IS '角色状态（0正常 1停用）';


--
-- Name: COLUMN sys_role.del_flag; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_role.del_flag IS '删除标志（0代表存在 2代表删除）';


--
-- Name: COLUMN sys_role.create_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_role.create_by IS '创建者';


--
-- Name: COLUMN sys_role.create_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_role.create_time IS '创建时间';


--
-- Name: COLUMN sys_role.update_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_role.update_by IS '更新者';


--
-- Name: COLUMN sys_role.update_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_role.update_time IS '更新时间';


--
-- Name: COLUMN sys_role.remark; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_role.remark IS '备注';


--
-- Name: sys_role_menu; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sys_role_menu (
    role_id bigint NOT NULL,
    menu_id bigint NOT NULL
);


--
-- Name: TABLE sys_role_menu; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.sys_role_menu IS '角色和菜单关联表';


--
-- Name: COLUMN sys_role_menu.role_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_role_menu.role_id IS '角色ID';


--
-- Name: COLUMN sys_role_menu.menu_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_role_menu.menu_id IS '菜单ID';


--
-- Name: sys_role_role_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sys_role_role_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sys_role_role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sys_role_role_id_seq OWNED BY public.sys_role.role_id;


--
-- Name: sys_user; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sys_user (
    user_id bigint NOT NULL,
    dept_id bigint,
    user_name character varying(30) NOT NULL,
    nick_name character varying(30) NOT NULL,
    user_type character varying(2) DEFAULT '00'::character varying,
    email character varying(50) DEFAULT ''::character varying,
    phonenumber character varying(11) DEFAULT ''::character varying,
    sex character(1) DEFAULT '0'::bpchar,
    avatar character varying(100) DEFAULT ''::character varying,
    password character varying(100) DEFAULT ''::character varying,
    status character(1) DEFAULT '0'::bpchar,
    del_flag character(1) DEFAULT '0'::bpchar,
    login_ip character varying(128) DEFAULT ''::character varying,
    login_date timestamp(0) without time zone,
    create_by character varying(64) DEFAULT ''::character varying,
    create_time timestamp(0) without time zone,
    update_by character varying(64) DEFAULT ''::character varying,
    update_time timestamp(0) without time zone,
    remark character varying(500) DEFAULT NULL::character varying
);


--
-- Name: TABLE sys_user; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.sys_user IS '用户信息表';


--
-- Name: COLUMN sys_user.user_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user.user_id IS '用户ID';


--
-- Name: COLUMN sys_user.dept_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user.dept_id IS '部门ID';


--
-- Name: COLUMN sys_user.user_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user.user_name IS '用户账号';


--
-- Name: COLUMN sys_user.nick_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user.nick_name IS '用户昵称';


--
-- Name: COLUMN sys_user.user_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user.user_type IS '用户类型（00系统用户）';


--
-- Name: COLUMN sys_user.email; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user.email IS '用户邮箱';


--
-- Name: COLUMN sys_user.phonenumber; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user.phonenumber IS '手机号码';


--
-- Name: COLUMN sys_user.sex; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user.sex IS '用户性别（0男 1女 2未知）';


--
-- Name: COLUMN sys_user.avatar; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user.avatar IS '头像地址';


--
-- Name: COLUMN sys_user.password; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user.password IS '密码';


--
-- Name: COLUMN sys_user.status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user.status IS '帐号状态（0正常 1停用）';


--
-- Name: COLUMN sys_user.del_flag; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user.del_flag IS '删除标志（0代表存在 2代表删除）';


--
-- Name: COLUMN sys_user.login_ip; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user.login_ip IS '最后登录IP';


--
-- Name: COLUMN sys_user.login_date; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user.login_date IS '最后登录时间';


--
-- Name: COLUMN sys_user.create_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user.create_by IS '创建者';


--
-- Name: COLUMN sys_user.create_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user.create_time IS '创建时间';


--
-- Name: COLUMN sys_user.update_by; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user.update_by IS '更新者';


--
-- Name: COLUMN sys_user.update_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user.update_time IS '更新时间';


--
-- Name: COLUMN sys_user.remark; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user.remark IS '备注';


--
-- Name: sys_user_post; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sys_user_post (
    user_id bigint NOT NULL,
    post_id bigint NOT NULL
);


--
-- Name: TABLE sys_user_post; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.sys_user_post IS '用户与岗位关联表';


--
-- Name: COLUMN sys_user_post.user_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user_post.user_id IS '用户ID';


--
-- Name: COLUMN sys_user_post.post_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user_post.post_id IS '岗位ID';


--
-- Name: sys_user_role; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sys_user_role (
    user_id bigint NOT NULL,
    role_id bigint NOT NULL
);


--
-- Name: TABLE sys_user_role; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.sys_user_role IS '用户和角色关联表';


--
-- Name: COLUMN sys_user_role.user_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user_role.user_id IS '用户ID';


--
-- Name: COLUMN sys_user_role.role_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sys_user_role.role_id IS '角色ID';


--
-- Name: sys_user_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sys_user_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sys_user_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sys_user_user_id_seq OWNED BY public.sys_user.user_id;


--
-- Name: alert_info alert_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alert_info ALTER COLUMN alert_id SET DEFAULT nextval('public.alert_info_alert_id_seq'::regclass);


--
-- Name: business_hardware_urgency_rules rule_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.business_hardware_urgency_rules ALTER COLUMN rule_id SET DEFAULT nextval('public.business_hardware_urgency_rules_rule_id_seq'::regclass);


--
-- Name: business_type_dict type_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.business_type_dict ALTER COLUMN type_id SET DEFAULT nextval('public.business_type_dict_type_id_seq'::regclass);


--
-- Name: device_info device_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.device_info ALTER COLUMN device_id SET DEFAULT nextval('public.device_info_device_id_seq'::regclass);


--
-- Name: gen_table table_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gen_table ALTER COLUMN table_id SET DEFAULT nextval('public.gen_table_table_id_seq'::regclass);


--
-- Name: gen_table_column column_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gen_table_column ALTER COLUMN column_id SET DEFAULT nextval('public.gen_table_column_column_id_seq'::regclass);


--
-- Name: hardware_type_dict type_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hardware_type_dict ALTER COLUMN type_id SET DEFAULT nextval('public.hardware_type_dict_type_id_seq'::regclass);


--
-- Name: maintenance_schedule schedule_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.maintenance_schedule ALTER COLUMN schedule_id SET DEFAULT nextval('public.maintenance_schedule_schedule_id_seq'::regclass);


--
-- Name: sys_config config_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_config ALTER COLUMN config_id SET DEFAULT nextval('public.sys_config_config_id_seq'::regclass);


--
-- Name: sys_dept dept_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_dept ALTER COLUMN dept_id SET DEFAULT nextval('public.sys_dept_dept_id_seq'::regclass);


--
-- Name: sys_dict_data dict_code; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_dict_data ALTER COLUMN dict_code SET DEFAULT nextval('public.sys_dict_data_dict_code_seq'::regclass);


--
-- Name: sys_dict_type dict_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_dict_type ALTER COLUMN dict_id SET DEFAULT nextval('public.sys_dict_type_dict_id_seq'::regclass);


--
-- Name: sys_job job_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_job ALTER COLUMN job_id SET DEFAULT nextval('public.sys_job_job_id_seq'::regclass);


--
-- Name: sys_job_log job_log_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_job_log ALTER COLUMN job_log_id SET DEFAULT nextval('public.sys_job_log_job_log_id_seq'::regclass);


--
-- Name: sys_logininfor info_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_logininfor ALTER COLUMN info_id SET DEFAULT nextval('public.sys_logininfor_info_id_seq'::regclass);


--
-- Name: sys_menu menu_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_menu ALTER COLUMN menu_id SET DEFAULT nextval('public.sys_menu_menu_id_seq'::regclass);


--
-- Name: sys_notice notice_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_notice ALTER COLUMN notice_id SET DEFAULT nextval('public.sys_notice_notice_id_seq'::regclass);


--
-- Name: sys_oper_log oper_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_oper_log ALTER COLUMN oper_id SET DEFAULT nextval('public.sys_oper_log_oper_id_seq'::regclass);


--
-- Name: sys_post post_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_post ALTER COLUMN post_id SET DEFAULT nextval('public.sys_post_post_id_seq'::regclass);


--
-- Name: sys_role role_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_role ALTER COLUMN role_id SET DEFAULT nextval('public.sys_role_role_id_seq'::regclass);


--
-- Name: sys_user user_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_user ALTER COLUMN user_id SET DEFAULT nextval('public.sys_user_user_id_seq'::regclass);


--
-- Name: alert_info alert_info_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alert_info
    ADD CONSTRAINT alert_info_pkey PRIMARY KEY (alert_id);


--
-- Name: apscheduler_jobs apscheduler_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.apscheduler_jobs
    ADD CONSTRAINT apscheduler_jobs_pkey PRIMARY KEY (id);


--
-- Name: business_hardware_urgency_rules business_hardware_urgency_rules_business_type_hardware_type_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.business_hardware_urgency_rules
    ADD CONSTRAINT business_hardware_urgency_rules_business_type_hardware_type_key UNIQUE (business_type, hardware_type);


--
-- Name: business_hardware_urgency_rules business_hardware_urgency_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.business_hardware_urgency_rules
    ADD CONSTRAINT business_hardware_urgency_rules_pkey PRIMARY KEY (rule_id);


--
-- Name: business_type_dict business_type_dict_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.business_type_dict
    ADD CONSTRAINT business_type_dict_pkey PRIMARY KEY (type_id);


--
-- Name: business_type_dict business_type_dict_type_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.business_type_dict
    ADD CONSTRAINT business_type_dict_type_code_key UNIQUE (type_code);


--
-- Name: device_info device_info_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.device_info
    ADD CONSTRAINT device_info_pkey PRIMARY KEY (device_id);


--
-- Name: gen_table_column gen_table_column_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gen_table_column
    ADD CONSTRAINT gen_table_column_pkey PRIMARY KEY (column_id);


--
-- Name: gen_table gen_table_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gen_table
    ADD CONSTRAINT gen_table_pkey PRIMARY KEY (table_id);


--
-- Name: hardware_type_dict hardware_type_dict_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hardware_type_dict
    ADD CONSTRAINT hardware_type_dict_pkey PRIMARY KEY (type_id);


--
-- Name: hardware_type_dict hardware_type_dict_type_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hardware_type_dict
    ADD CONSTRAINT hardware_type_dict_type_code_key UNIQUE (type_code);


--
-- Name: maintenance_schedule maintenance_schedule_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.maintenance_schedule
    ADD CONSTRAINT maintenance_schedule_pkey PRIMARY KEY (schedule_id);


--
-- Name: redfish_log redfish_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.redfish_log
    ADD CONSTRAINT redfish_log_pkey PRIMARY KEY (log_id);


--
-- Name: sys_config sys_config_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_config
    ADD CONSTRAINT sys_config_pkey PRIMARY KEY (config_id);


--
-- Name: sys_dept sys_dept_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_dept
    ADD CONSTRAINT sys_dept_pkey PRIMARY KEY (dept_id);


--
-- Name: sys_dict_data sys_dict_data_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_dict_data
    ADD CONSTRAINT sys_dict_data_pkey PRIMARY KEY (dict_code);


--
-- Name: sys_dict_type sys_dict_type_dict_type_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_dict_type
    ADD CONSTRAINT sys_dict_type_dict_type_key UNIQUE (dict_type);


--
-- Name: sys_dict_type sys_dict_type_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_dict_type
    ADD CONSTRAINT sys_dict_type_pkey PRIMARY KEY (dict_id);


--
-- Name: sys_job_log sys_job_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_job_log
    ADD CONSTRAINT sys_job_log_pkey PRIMARY KEY (job_log_id);


--
-- Name: sys_job sys_job_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_job
    ADD CONSTRAINT sys_job_pkey PRIMARY KEY (job_id, job_name, job_group);


--
-- Name: sys_logininfor sys_logininfor_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_logininfor
    ADD CONSTRAINT sys_logininfor_pkey PRIMARY KEY (info_id);


--
-- Name: sys_menu sys_menu_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_menu
    ADD CONSTRAINT sys_menu_pkey PRIMARY KEY (menu_id);


--
-- Name: sys_notice sys_notice_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_notice
    ADD CONSTRAINT sys_notice_pkey PRIMARY KEY (notice_id);


--
-- Name: sys_oper_log sys_oper_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_oper_log
    ADD CONSTRAINT sys_oper_log_pkey PRIMARY KEY (oper_id);


--
-- Name: sys_post sys_post_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_post
    ADD CONSTRAINT sys_post_pkey PRIMARY KEY (post_id);


--
-- Name: sys_role_menu sys_role_menu_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_role_menu
    ADD CONSTRAINT sys_role_menu_pkey PRIMARY KEY (role_id, menu_id);


--
-- Name: sys_role sys_role_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_role
    ADD CONSTRAINT sys_role_pkey PRIMARY KEY (role_id);


--
-- Name: sys_user sys_user_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_user
    ADD CONSTRAINT sys_user_pkey PRIMARY KEY (user_id);


--
-- Name: sys_user_post sys_user_post_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_user_post
    ADD CONSTRAINT sys_user_post_pkey PRIMARY KEY (user_id, post_id);


--
-- Name: sys_user_role sys_user_role_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sys_user_role
    ADD CONSTRAINT sys_user_role_pkey PRIMARY KEY (user_id, role_id);


--
-- Name: idx_alert_info_del_flag; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_alert_info_del_flag ON public.alert_info USING btree (del_flag);


--
-- Name: idx_alert_info_device_component; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_alert_info_device_component ON public.alert_info USING btree (device_id, component_type);


--
-- Name: idx_alert_info_device_del_flag; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_alert_info_device_del_flag ON public.alert_info USING btree (device_id, del_flag) WHERE (del_flag = 0);


--
-- Name: idx_alert_info_device_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_alert_info_device_id ON public.alert_info USING btree (device_id);


--
-- Name: idx_alert_info_first_occurrence; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_alert_info_first_occurrence ON public.alert_info USING btree (first_occurrence);


--
-- Name: idx_alert_info_health_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_alert_info_health_status ON public.alert_info USING btree (health_status);


--
-- Name: idx_alert_info_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_alert_info_status ON public.alert_info USING btree (alert_status);


--
-- Name: idx_alert_info_status_del_flag; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_alert_info_status_del_flag ON public.alert_info USING btree (alert_status, del_flag) WHERE (del_flag = 0);


--
-- Name: idx_alert_info_urgency_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_alert_info_urgency_status ON public.alert_info USING btree (urgency_level, alert_status);


--
-- Name: idx_business_type_dict_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_business_type_dict_active ON public.business_type_dict USING btree (is_active);


--
-- Name: idx_business_type_dict_code; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_business_type_dict_code ON public.business_type_dict USING btree (type_code);


--
-- Name: idx_business_type_dict_sort; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_business_type_dict_sort ON public.business_type_dict USING btree (sort_order);


--
-- Name: idx_device_info_business_ip; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_device_info_business_ip ON public.device_info USING btree (business_ip);


--
-- Name: idx_device_info_business_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_device_info_business_type ON public.device_info USING btree (business_type);


--
-- Name: idx_device_info_health_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_device_info_health_status ON public.device_info USING btree (health_status);


--
-- Name: idx_device_info_hostname; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_device_info_hostname ON public.device_info USING btree (hostname);


--
-- Name: idx_device_info_location; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_device_info_location ON public.device_info USING btree (location);


--
-- Name: idx_device_info_manufacturer; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_device_info_manufacturer ON public.device_info USING btree (manufacturer);


--
-- Name: idx_device_info_oob_ip; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_device_info_oob_ip ON public.device_info USING btree (oob_ip);


--
-- Name: idx_device_info_system_owner; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_device_info_system_owner ON public.device_info USING btree (system_owner);


--
-- Name: idx_hardware_type_dict_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hardware_type_dict_active ON public.hardware_type_dict USING btree (is_active);


--
-- Name: idx_hardware_type_dict_category; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hardware_type_dict_category ON public.hardware_type_dict USING btree (category);


--
-- Name: idx_hardware_type_dict_code; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hardware_type_dict_code ON public.hardware_type_dict USING btree (type_code);


--
-- Name: idx_hardware_type_dict_sort; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hardware_type_dict_sort ON public.hardware_type_dict USING btree (sort_order);


--
-- Name: idx_redfish_log_collected_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_redfish_log_collected_time ON public.redfish_log USING btree (collected_time);


--
-- Name: idx_redfish_log_created_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_redfish_log_created_time ON public.redfish_log USING btree (created_time);


--
-- Name: idx_redfish_log_device_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_redfish_log_device_id ON public.redfish_log USING btree (device_id);


--
-- Name: idx_redfish_log_device_ip; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_redfish_log_device_ip ON public.redfish_log USING btree (device_ip);


--
-- Name: idx_redfish_log_device_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_redfish_log_device_time ON public.redfish_log USING btree (device_id, created_time);


--
-- Name: idx_redfish_log_severity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_redfish_log_severity ON public.redfish_log USING btree (severity);


--
-- Name: idx_redfish_log_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_redfish_log_source ON public.redfish_log USING btree (log_source);


--
-- Name: idx_sys_logininfor_lt; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sys_logininfor_lt ON public.sys_logininfor USING btree (login_time);


--
-- Name: idx_sys_logininfor_s; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sys_logininfor_s ON public.sys_logininfor USING btree (status);


--
-- Name: idx_sys_oper_log_bt; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sys_oper_log_bt ON public.sys_oper_log USING btree (business_type);


--
-- Name: idx_sys_oper_log_ot; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sys_oper_log_ot ON public.sys_oper_log USING btree (oper_time);


--
-- Name: idx_sys_oper_log_s; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sys_oper_log_s ON public.sys_oper_log USING btree (status);


--
-- Name: idx_urgency_rules_business_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_urgency_rules_business_type ON public.business_hardware_urgency_rules USING btree (business_type);


--
-- Name: idx_urgency_rules_hardware_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_urgency_rules_hardware_type ON public.business_hardware_urgency_rules USING btree (hardware_type);


--
-- Name: idx_urgency_rules_urgency; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_urgency_rules_urgency ON public.business_hardware_urgency_rules USING btree (urgency_level);


--
-- Name: ix_alert_info_display; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_alert_info_display ON public.alert_info USING btree (alert_status, urgency_level, last_occurrence DESC);


--
-- Name: ix_alert_info_first_occurrence; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_alert_info_first_occurrence ON public.alert_info USING btree (first_occurrence);


--
-- Name: ix_alert_info_lifecycle; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_alert_info_lifecycle ON public.alert_info USING btree (device_id, component_type, component_name, alert_status);


--
-- Name: ix_apscheduler_jobs_next_run_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_apscheduler_jobs_next_run_time ON public.apscheduler_jobs USING btree (next_run_time);


--
-- Name: alert_info trigger_alert_info_update_time; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trigger_alert_info_update_time BEFORE UPDATE ON public.alert_info FOR EACH ROW EXECUTE FUNCTION public.update_alert_info_updated_time();


--
-- Name: alert_info alert_info_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alert_info
    ADD CONSTRAINT alert_info_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.device_info(device_id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: maintenance_schedule maintenance_schedule_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.maintenance_schedule
    ADD CONSTRAINT maintenance_schedule_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.device_info(device_id);


--
-- PostgreSQL database dump complete
--


-- ===================================================================
-- Data seed section
-- ===================================================================
INSERT INTO public.sys_dept (dept_id, parent_id, ancestors, dept_name, order_num, leader, phone, email, status, del_flag, create_by, create_time, update_by, update_time) VALUES (100, 0, '0', '中体彩彩票运营管理有限公司', 0, '年糕', '15888888888', 'niangao@qq.com', '0', '0', 'admin', '2025-06-07 16:46:14', 'admin', '2025-09-20 17:09:44');
INSERT INTO public.sys_dept (dept_id, parent_id, ancestors, dept_name, order_num, leader, phone, email, status, del_flag, create_by, create_time, update_by, update_time) VALUES (200, 100, '0,100', '运行维护部', 1, '', NULL, NULL, '0', '0', 'admin', '2025-09-20 17:07:38', 'admin', '2025-09-20 17:16:22');
INSERT INTO public.sys_dept (dept_id, parent_id, ancestors, dept_name, order_num, leader, phone, email, status, del_flag, create_by, create_time, update_by, update_time) VALUES (201, 100, '0,100', '工程部', 2, NULL, NULL, NULL, '0', '0', 'admin', '2025-09-20 17:08:27', 'admin', '2025-09-20 17:16:32');

INSERT INTO public.sys_post (post_id, post_code, post_name, post_sort, status, create_by, create_time, update_by, update_time, remark) VALUES (1, 'dm', '值班经理', 1, '0', 'admin', '2025-06-07 16:46:14', 'admin', '2025-09-20 17:37:13', '');
INSERT INTO public.sys_post (post_id, post_code, post_name, post_sort, status, create_by, create_time, update_by, update_time, remark) VALUES (2, 'l1', '一线', 2, '0', 'admin', '2025-06-07 16:46:14', 'admin', '2025-09-20 17:37:25', '');
INSERT INTO public.sys_post (post_id, post_code, post_name, post_sort, status, create_by, create_time, update_by, update_time, remark) VALUES (3, 'l2', '二线', 4, '0', 'admin', '2025-06-07 16:46:14', 'niangao', '2025-09-20 18:09:02', '');
INSERT INTO public.sys_post (post_id, post_code, post_name, post_sort, status, create_by, create_time, update_by, update_time, remark) VALUES (4, 'user', '普通员工', 4, '0', 'admin', '2025-06-07 16:46:14', '', NULL, '');

INSERT INTO public.sys_user (user_id, dept_id, user_name, nick_name, user_type, email, phonenumber, sex, avatar, password, status, del_flag, login_ip, login_date, create_by, create_time, update_by, update_time, remark) VALUES (1, 200, 'admin', '超级管理员', '00', 'niangao@163.com', '15888888888', '1', '/profile/avatar/2025/07/11/avatar_20250711212616A189.png', '$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTH.ulu33dHOiBE8ByOhJIrdAu2', '0', '0', '127.0.0.1', '2025-10-02 17:21:22', 'admin', '2025-06-07 16:46:14', 'admin', '2025-07-11 21:26:19', '管理员');
INSERT INTO public.sys_user (user_id, dept_id, user_name, nick_name, user_type, email, phonenumber, sex, avatar, password, status, del_flag, login_ip, login_date, create_by, create_time, update_by, update_time, remark) VALUES (2, 200, 'niangao', '年糕', '00', 'niangao@qq.com', '15666666666', '1', '', '$2b$12$mFc5lYflB4fbjgC6nMm3tu75UtcFMXkn1qPArMhMHXR48qUe6BwWe', '0', '0', '127.0.0.1', '2025-09-23 13:32:19', 'admin', '2025-06-07 16:46:14', 'admin', '2025-09-20 17:42:45', '测试员');

INSERT INTO public.sys_role (role_id, role_name, role_key, role_sort, data_scope, menu_check_strictly, dept_check_strictly, status, del_flag, create_by, create_time, update_by, update_time, remark) VALUES (1, '超级管理员', 'admin', 1, '1', 1, 1, '0', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '超级管理员');
INSERT INTO public.sys_role (role_id, role_name, role_key, role_sort, data_scope, menu_check_strictly, dept_check_strictly, status, del_flag, create_by, create_time, update_by, update_time, remark) VALUES (2, '普通角色', 'common', 2, '2', 1, 1, '0', '0', 'admin', '2025-06-07 16:46:14', 'admin', '2025-09-23 13:31:42', '普通角色');
INSERT INTO public.sys_role (role_id, role_name, role_key, role_sort, data_scope, menu_check_strictly, dept_check_strictly, status, del_flag, create_by, create_time, update_by, update_time, remark) VALUES (4, '管理员', 'common-admin', 1, '1', 1, 1, '0', '0', 'admin', '2025-09-20 17:40:27', 'admin', '2025-09-20 17:40:27', NULL);

INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1, '系统管理', 0, 2, 'system', NULL, '', '', 1, 0, 'M', '0', '0', '', 'system', 'admin', '2025-06-07 16:46:14', 'admin', '2025-09-23 14:20:28', '系统管理目录');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (2, '系统监控', 0, 3, 'monitor', NULL, '', '', 1, 0, 'M', '0', '0', '', 'monitor', 'admin', '2025-06-07 16:46:14', 'admin', '2025-09-23 14:20:22', '系统监控目录');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3, '系统工具', 0, 3, 'tool', NULL, '', '', 1, 0, 'M', '0', '1', '', 'tool', 'admin', '2025-06-07 16:46:14', 'admin', '2025-10-02 19:34:04', '系统工具目录');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (100, '用户管理', 1, 1, 'user', 'system/user/index', '', '', 1, 0, 'C', '0', '0', 'system:user:list', 'user', 'admin', '2025-06-07 16:46:14', '', NULL, '用户管理菜单');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (101, '角色管理', 1, 4, 'role', 'system/role/index', '', '', 1, 0, 'C', '0', '0', 'system:role:list', 'peoples', 'admin', '2025-06-07 16:46:14', 'admin', '2025-10-02 19:37:15', '角色管理菜单');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (102, '菜单管理', 1, 5, 'menu', 'system/menu/index', '', '', 1, 0, 'C', '0', '0', 'system:menu:list', 'tree-table', 'admin', '2025-06-07 16:46:14', 'admin', '2025-10-02 19:38:07', '菜单管理菜单');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (103, '部门管理', 1, 3, 'dept', 'system/dept/index', '', '', 1, 0, 'C', '0', '0', 'system:dept:list', 'tree', 'admin', '2025-06-07 16:46:14', 'admin', '2025-10-02 19:37:07', '部门管理菜单');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (104, '岗位管理', 1, 2, 'post', 'system/post/index', '', '', 1, 0, 'C', '0', '0', 'system:post:list', 'post', 'admin', '2025-06-07 16:46:14', 'admin', '2025-10-02 19:37:39', '岗位管理菜单');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (105, '字典管理', 1, 6, 'dict', 'system/dict/index', '', '', 1, 0, 'C', '1', '0', 'system:dict:list', 'dict', 'admin', '2025-06-07 16:46:14', 'admin', '2025-10-02 19:39:34', '字典管理菜单');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (106, '参数设置', 1, 7, 'config', 'system/config/index', '', '', 1, 0, 'C', '0', '0', 'system:config:list', 'edit', 'admin', '2025-06-07 16:46:14', '', NULL, '参数设置菜单');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (107, '通知公告', 1, 0, 'notice', 'system/notice/index', '', '', 1, 0, 'C', '0', '0', 'system:notice:list', 'message', 'admin', '2025-06-07 16:46:14', 'admin', '2025-10-02 19:37:55', '通知公告菜单');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (108, '日志管理', 1, 9, 'log', '', '', '', 1, 0, 'M', '0', '0', '', 'log', 'admin', '2025-06-07 16:46:14', '', NULL, '日志管理菜单');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (109, '在线用户', 2, 1, 'online', 'monitor/online/index', '', '', 1, 0, 'C', '0', '0', 'monitor:online:list', 'online', 'admin', '2025-06-07 16:46:14', '', NULL, '在线用户菜单');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (110, '定时任务', 2, 2, 'job', 'monitor/job/index', '', '', 1, 0, 'C', '0', '0', 'monitor:job:list', 'job', 'admin', '2025-06-07 16:46:14', '', NULL, '定时任务菜单');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (111, '数据监控', 2, 3, 'druid', 'monitor/druid/index', NULL, '', 1, 0, 'C', '0', '1', 'monitor:druid:list', 'druid', 'admin', '2025-09-23 14:10:31', 'admin', '2025-10-02 19:34:25', 'Druid数据库连接池监控');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (112, '服务监控', 2, 4, 'server', 'monitor/server/index', '', '', 1, 0, 'C', '0', '0', 'monitor:server:list', 'server', 'admin', '2025-06-07 16:46:14', '', NULL, '服务监控菜单');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (113, '缓存监控', 2, 5, 'cache', 'monitor/cache/index', '', '', 1, 0, 'C', '0', '0', 'monitor:cache:list', 'redis', 'admin', '2025-06-07 16:46:14', '', NULL, '缓存监控菜单');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (114, '缓存列表', 2, 6, 'cache-list', 'monitor/cache/list', NULL, '', 1, 0, 'C', '0', '0', 'monitor:cache:manage', 'redis-list', 'admin', '2025-09-23 14:13:44', 'admin', '2025-09-23 14:18:54', 'Redis缓存键值管理');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (116, '代码生成', 3, 1, 'gen', 'tool/gen/index', '', '', 1, 0, 'C', '0', '0', 'tool:gen:list', 'code', 'admin', '2025-06-07 16:46:14', 'admin', '2025-09-23 14:00:40', '代码生成菜单');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (117, '系统接口', 3, 2, 'swagger', 'tool/swagger/index', NULL, '', 1, 0, 'C', '0', '0', 'tool:swagger:list', 'swagger', 'admin', '2025-09-23 14:06:10', 'admin', '2025-09-23 14:18:54', 'Swagger系统接口文档');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (118, '表单构建', 3, 3, 'build', 'tool/build/index', NULL, '', 1, 0, 'C', '0', '0', 'tool:build:list', 'build', 'admin', '2025-09-23 14:06:10', 'admin', '2025-09-23 14:18:54', '表单构建工具');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (500, '操作日志', 108, 1, 'operlog', 'monitor/operlog/index', '', '', 1, 0, 'C', '0', '0', 'monitor:operlog:list', 'form', 'admin', '2025-06-07 16:46:14', '', NULL, '操作日志菜单');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (501, '登录日志', 108, 2, 'logininfor', 'monitor/logininfor/index', '', '', 1, 0, 'C', '0', '0', 'monitor:logininfor:list', 'logininfor', 'admin', '2025-06-07 16:46:14', '', NULL, '登录日志菜单');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1000, '用户查询', 100, 1, '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:query', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1001, '用户新增', 100, 2, '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:add', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1002, '用户修改', 100, 3, '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:edit', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1003, '用户删除', 100, 4, '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:remove', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1004, '用户导出', 100, 5, '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:export', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1005, '用户导入', 100, 6, '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:import', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1006, '重置密码', 100, 7, '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:resetPwd', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1007, '角色查询', 101, 1, '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:query', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1008, '角色新增', 101, 2, '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:add', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1009, '角色修改', 101, 3, '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:edit', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1010, '角色删除', 101, 4, '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:remove', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1011, '角色导出', 101, 5, '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:export', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1012, '菜单查询', 102, 1, '', '', '', '', 1, 0, 'F', '0', '0', 'system:menu:query', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1013, '菜单新增', 102, 2, '', '', '', '', 1, 0, 'F', '0', '0', 'system:menu:add', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1014, '菜单修改', 102, 3, '', '', '', '', 1, 0, 'F', '0', '0', 'system:menu:edit', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1015, '菜单删除', 102, 4, '', '', '', '', 1, 0, 'F', '0', '0', 'system:menu:remove', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1016, '部门查询', 103, 1, '', '', '', '', 1, 0, 'F', '0', '0', 'system:dept:query', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1017, '部门新增', 103, 2, '', '', '', '', 1, 0, 'F', '0', '0', 'system:dept:add', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1018, '部门修改', 103, 3, '', '', '', '', 1, 0, 'F', '0', '0', 'system:dept:edit', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1019, '部门删除', 103, 4, '', '', '', '', 1, 0, 'F', '0', '0', 'system:dept:remove', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1020, '岗位查询', 104, 1, '', '', '', '', 1, 0, 'F', '0', '0', 'system:post:query', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1021, '岗位新增', 104, 2, '', '', '', '', 1, 0, 'F', '0', '0', 'system:post:add', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1022, '岗位修改', 104, 3, '', '', '', '', 1, 0, 'F', '0', '0', 'system:post:edit', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1023, '岗位删除', 104, 4, '', '', '', '', 1, 0, 'F', '0', '0', 'system:post:remove', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1024, '岗位导出', 104, 5, '', '', '', '', 1, 0, 'F', '0', '0', 'system:post:export', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1025, '字典查询', 105, 1, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:dict:query', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1026, '字典新增', 105, 2, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:dict:add', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1027, '字典修改', 105, 3, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:dict:edit', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1028, '字典删除', 105, 4, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:dict:remove', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1029, '字典导出', 105, 5, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:dict:export', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1030, '参数查询', 106, 1, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:config:query', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1031, '参数新增', 106, 2, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:config:add', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1032, '参数修改', 106, 3, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:config:edit', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1033, '参数删除', 106, 4, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:config:remove', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1034, '参数导出', 106, 5, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:config:export', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1035, '公告查询', 107, 1, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:notice:query', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1036, '公告新增', 107, 2, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:notice:add', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1037, '公告修改', 107, 3, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:notice:edit', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1038, '公告删除', 107, 4, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:notice:remove', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1040, '操作删除', 500, 2, '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:operlog:remove', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1041, '日志导出', 500, 3, '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:operlog:export', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1043, '登录删除', 501, 2, '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:logininfor:remove', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1044, '日志导出', 501, 3, '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:logininfor:export', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1045, '账户解锁', 501, 4, '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:logininfor:unlock', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1048, '单条强退', 109, 3, '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:online:forceLogout', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1049, '任务查询', 110, 1, '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:job:query', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1050, '任务新增', 110, 2, '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:job:add', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1051, '任务修改', 110, 3, '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:job:edit', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1052, '任务删除', 110, 4, '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:job:remove', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1053, '状态修改', 110, 5, '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:job:changeStatus', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1054, '任务导出', 110, 6, '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:job:export', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1055, '生成查询', 116, 1, '#', '', '', '', 1, 0, 'F', '0', '0', 'tool:gen:query', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1056, '生成修改', 116, 2, '#', '', '', '', 1, 0, 'F', '0', '0', 'tool:gen:edit', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1057, '生成删除', 116, 3, '#', '', '', '', 1, 0, 'F', '0', '0', 'tool:gen:remove', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1058, '导入代码', 116, 4, '#', '', '', '', 1, 0, 'F', '0', '0', 'tool:gen:import', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1059, '预览代码', 116, 5, '#', '', '', '', 1, 0, 'F', '0', '0', 'tool:gen:preview', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (1060, '生成代码', 116, 6, '#', '', '', '', 1, 0, 'F', '0', '0', 'tool:gen:code', '#', 'admin', '2025-06-07 16:46:14', '', NULL, '');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (2000, '设备管理', 0, 1, 'devices', NULL, NULL, '', 1, 0, 'M', '0', '0', '', 'monitor', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '设备管理模块');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (2100, '设备信息', 2000, 1, 'device', 'redfish/device/index', NULL, 'DeviceInfo', 1, 0, 'C', '0', '0', 'redfish:device:list', 'server', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '设备信息管理');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (2200, '告警管理', 2000, 2, 'alert', 'redfish/alert/index', NULL, 'AlertInfo', 1, 0, 'C', '0', '0', 'redfish:alert:list', 'warning', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 18:02:32', '告警信息管理');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (2300, '日志管理', 2000, 3, 'log', NULL, NULL, '', 1, 0, 'M', '0', '0', '', 'documentation', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '日志管理模块');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (2310, '日志信息', 2300, 1, 'loginfo', 'redfish/log/index', NULL, '', 1, 0, 'C', '0', '0', 'redfish:log:list', 'documentation', 'admin', '2025-09-22 18:02:32', 'admin', '2025-09-22 18:02:32', '日志信息查看');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (2320, '临时查看', 2300, 2, 'temp', 'redfish/log/temp', NULL, '', 1, 0, 'C', '0', '0', 'redfish:log:temp', 'edit', 'admin', '2025-09-22 18:02:32', 'admin', '2025-09-22 18:02:32', '临时日志查看');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (2330, '历史管理', 2300, 3, 'history', 'redfish/log/history', NULL, '', 1, 0, 'C', '0', '1', 'redfish:log:history', 'time', 'admin', '2025-09-22 18:02:32', 'admin', '2025-09-23 20:50:33', '历史日志管理');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (2400, '排期规则', 2000, 4, 'maintenance', 'redfish/maintenance/index', NULL, 'MaintenanceRule', 1, 0, 'C', '0', '0', 'redfish:businessRule:list', 'calendar', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '排期规则管理');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3100, '首页概览', 0, 100, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:dashboard:overview', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '首页概览数据权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3101, '首页告警', 0, 101, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:dashboard:alert', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '首页告警数据权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3102, '首页设备', 0, 102, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:dashboard:device', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '首页设备数据权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3103, '首页指标', 0, 103, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:dashboard:metrics', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '首页系统指标权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3104, '首页完整', 0, 104, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:dashboard:view', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '首页完整数据权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3200, '设备查询', 2200, 1, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:device:query', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '设备详情查询权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3201, '设备新增', 2200, 2, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:device:add', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '设备新增权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3202, '设备修改', 2200, 3, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:device:edit', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '设备修改权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3203, '设备删除', 2200, 4, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:device:remove', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '设备删除权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3300, '告警查询', 2200, 1, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:alert:query', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '告警详情查询权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3301, '告警删除', 2200, 2, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:alert:remove', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '告警删除权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3302, '告警导出', 2200, 3, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:alert:export', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '告警数据导出权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3303, '告警维护', 2200, 4, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:alert:maintenance', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '告警维护计划权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3400, '日志查询', 2310, 1, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:log:query', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '日志详情查询权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3401, '日志收集', 2310, 2, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:log:collect', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '日志收集权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3402, '日志导出', 2310, 3, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:log:export', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '日志导出权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3403, '日志删除', 2310, 4, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:log:remove', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '日志删除权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3404, '日志清理', 2310, 5, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:log:cleanup', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '日志清理权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3410, '临时查看权限', 2320, 1, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:log:temp:view', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '临时日志查看权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3411, '临时收集权限', 2320, 2, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:log:temp:collect', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '临时日志收集权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3412, '临时导出权限', 2320, 3, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:log:temp:export', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '临时日志导出权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3420, '历史查看权限', 2330, 1, '', '', NULL, '', 1, 0, 'F', '1', '1', 'redfish:log:history:view', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-23 20:50:38', '历史日志查看权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3500, '业务规则查询', 2400, 1, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:query', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '业务规则查询权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3501, '业务规则新增', 2400, 2, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:add', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '业务规则新增权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3502, '业务规则修改', 2400, 3, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:edit', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '业务规则修改权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3503, '业务规则删除', 2400, 4, '', '', NULL, '', 1, 0, 'F', '1', '0', 'redfish:businessRule:remove', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '业务规则删除权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3700, '监控配置查看', 2, 700, '', '', NULL, '', 1, 0, 'F', '1', '0', 'monitor:config:view', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '监控配置查看权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3701, '监控配置编辑', 2, 701, '', '', NULL, '', 1, 0, 'F', '1', '0', 'monitor:config:edit', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '监控配置编辑权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3702, '监控任务查看', 2, 702, '', '', NULL, '', 1, 0, 'F', '1', '0', 'monitor:task:view', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '监控任务查看权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3703, '监控任务执行', 2, 703, '', '', NULL, '', 1, 0, 'F', '1', '0', 'monitor:task:execute', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '监控任务执行权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3704, '监控任务管理', 2, 704, '', '', NULL, '', 1, 0, 'F', '1', '0', 'monitor:task:manage', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '监控任务管理权限');
INSERT INTO public.sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES (3705, '监控系统查看', 2, 705, '', '', NULL, '', 1, 0, 'F', '1', '0', 'monitor:system:view', '#', 'admin', '2025-09-22 17:56:01', 'admin', '2025-09-22 17:56:01', '监控系统查看权限');

INSERT INTO public.sys_dict_type (dict_id, dict_name, dict_type, status, create_by, create_time, update_by, update_time, remark) VALUES (1, '用户性别', 'sys_user_sex', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '用户性别列表');
INSERT INTO public.sys_dict_type (dict_id, dict_name, dict_type, status, create_by, create_time, update_by, update_time, remark) VALUES (2, '菜单状态', 'sys_show_hide', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '菜单状态列表');
INSERT INTO public.sys_dict_type (dict_id, dict_name, dict_type, status, create_by, create_time, update_by, update_time, remark) VALUES (3, '系统开关', 'sys_normal_disable', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '系统开关列表');
INSERT INTO public.sys_dict_type (dict_id, dict_name, dict_type, status, create_by, create_time, update_by, update_time, remark) VALUES (4, '任务状态', 'sys_job_status', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '任务状态列表');
INSERT INTO public.sys_dict_type (dict_id, dict_name, dict_type, status, create_by, create_time, update_by, update_time, remark) VALUES (5, '任务分组', 'sys_job_group', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '任务分组列表');
INSERT INTO public.sys_dict_type (dict_id, dict_name, dict_type, status, create_by, create_time, update_by, update_time, remark) VALUES (6, '任务执行器', 'sys_job_executor', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '任务执行器列表');
INSERT INTO public.sys_dict_type (dict_id, dict_name, dict_type, status, create_by, create_time, update_by, update_time, remark) VALUES (7, '系统是否', 'sys_yes_no', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '系统是否列表');
INSERT INTO public.sys_dict_type (dict_id, dict_name, dict_type, status, create_by, create_time, update_by, update_time, remark) VALUES (8, '通知类型', 'sys_notice_type', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '通知类型列表');
INSERT INTO public.sys_dict_type (dict_id, dict_name, dict_type, status, create_by, create_time, update_by, update_time, remark) VALUES (9, '通知状态', 'sys_notice_status', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '通知状态列表');
INSERT INTO public.sys_dict_type (dict_id, dict_name, dict_type, status, create_by, create_time, update_by, update_time, remark) VALUES (10, '操作类型', 'sys_oper_type', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '操作类型列表');
INSERT INTO public.sys_dict_type (dict_id, dict_name, dict_type, status, create_by, create_time, update_by, update_time, remark) VALUES (11, '系统状态', 'sys_common_status', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '登录状态列表');

INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (1, 1, '男', '0', 'sys_user_sex', '', '', 'Y', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '性别男');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (2, 2, '女', '1', 'sys_user_sex', '', '', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '性别女');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (3, 3, '未知', '2', 'sys_user_sex', '', '', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '性别未知');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (4, 1, '显示', '0', 'sys_show_hide', '', 'primary', 'Y', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '显示菜单');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (5, 2, '隐藏', '1', 'sys_show_hide', '', 'danger', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '隐藏菜单');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (6, 1, '正常', '0', 'sys_normal_disable', '', 'primary', 'Y', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '正常状态');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (7, 2, '停用', '1', 'sys_normal_disable', '', 'danger', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '停用状态');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (8, 1, '正常', '0', 'sys_job_status', '', 'primary', 'Y', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '正常状态');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (9, 2, '暂停', '1', 'sys_job_status', '', 'danger', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '停用状态');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (10, 1, '默认', 'default', 'sys_job_group', '', '', 'Y', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '默认分组');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (11, 2, '数据库', 'sqlalchemy', 'sys_job_group', '', '', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '数据库分组');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (12, 3, 'redis', 'redis', 'sys_job_group', '', '', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, 'reids分组');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (13, 1, '默认', 'default', 'sys_job_executor', '', '', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '线程池');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (14, 2, '进程池', 'processpool', 'sys_job_executor', '', '', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '进程池');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (15, 1, '是', 'Y', 'sys_yes_no', '', 'primary', 'Y', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '系统默认是');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (16, 2, '否', 'N', 'sys_yes_no', '', 'danger', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '系统默认否');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (17, 1, '通知', '1', 'sys_notice_type', '', 'warning', 'Y', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '通知');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (18, 2, '公告', '2', 'sys_notice_type', '', 'success', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '公告');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (19, 1, '正常', '0', 'sys_notice_status', '', 'primary', 'Y', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '正常状态');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (20, 2, '关闭', '1', 'sys_notice_status', '', 'danger', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '关闭状态');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (21, 99, '其他', '0', 'sys_oper_type', '', 'info', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '其他操作');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (22, 1, '新增', '1', 'sys_oper_type', '', 'info', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '新增操作');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (23, 2, '修改', '2', 'sys_oper_type', '', 'info', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '修改操作');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (24, 3, '删除', '3', 'sys_oper_type', '', 'danger', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '删除操作');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (25, 4, '授权', '4', 'sys_oper_type', '', 'primary', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '授权操作');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (26, 5, '导出', '5', 'sys_oper_type', '', 'warning', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '导出操作');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (27, 6, '导入', '6', 'sys_oper_type', '', 'warning', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '导入操作');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (28, 7, '强退', '7', 'sys_oper_type', '', 'danger', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '强退操作');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (29, 8, '生成代码', '8', 'sys_oper_type', '', 'warning', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '生成操作');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (30, 9, '清空数据', '9', 'sys_oper_type', '', 'danger', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '清空操作');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (31, 1, '成功', '0', 'sys_common_status', '', 'primary', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '正常状态');
INSERT INTO public.sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) VALUES (32, 2, '失败', '1', 'sys_common_status', '', 'danger', 'N', '0', 'admin', '2025-06-07 16:46:14', '', NULL, '停用状态');

INSERT INTO public.sys_config (config_id, config_name, config_key, config_value, config_type, create_by, create_time, update_by, update_time, remark) VALUES (1, '主框架页-默认皮肤样式名称', 'sys.index.skinName', 'skin-blue', 'Y', 'admin', '2025-06-07 16:46:14', '', NULL, '蓝色 skin-blue、绿色 skin-green、紫色 skin-purple、红色 skin-red、黄色 skin-yellow');
INSERT INTO public.sys_config (config_id, config_name, config_key, config_value, config_type, create_by, create_time, update_by, update_time, remark) VALUES (2, '用户管理-账号初始密码', 'sys.user.initPassword', '123456', 'Y', 'admin', '2025-06-07 16:46:14', '', NULL, '初始化密码 123456');
INSERT INTO public.sys_config (config_id, config_name, config_key, config_value, config_type, create_by, create_time, update_by, update_time, remark) VALUES (3, '主框架页-侧边栏主题', 'sys.index.sideTheme', 'theme-dark', 'Y', 'admin', '2025-06-07 16:46:14', '', NULL, '深色主题theme-dark，浅色主题theme-light');
INSERT INTO public.sys_config (config_id, config_name, config_key, config_value, config_type, create_by, create_time, update_by, update_time, remark) VALUES (4, '账号自助-验证码开关', 'sys.account.captchaEnabled', 'true', 'Y', 'admin', '2025-06-07 16:46:14', '', NULL, '是否开启验证码功能（true开启，false关闭）');
INSERT INTO public.sys_config (config_id, config_name, config_key, config_value, config_type, create_by, create_time, update_by, update_time, remark) VALUES (5, '账号自助-是否开启用户注册功能', 'sys.account.registerUser', 'false', 'Y', 'admin', '2025-06-07 16:46:14', '', NULL, '是否开启注册用户功能（true开启，false关闭）');
INSERT INTO public.sys_config (config_id, config_name, config_key, config_value, config_type, create_by, create_time, update_by, update_time, remark) VALUES (6, '用户登录-黑名单列表', 'sys.login.blackIPList', '', 'Y', 'admin', '2025-06-07 16:46:14', '', NULL, '设置登录IP黑名单限制，多个匹配项以;分隔，支持匹配（*通配、网段）');

INSERT INTO public.sys_user_post (user_id, post_id) VALUES (1, 2);
INSERT INTO public.sys_user_post (user_id, post_id) VALUES (2, 2);

INSERT INTO public.sys_user_role (user_id, role_id) VALUES (1, 1);
INSERT INTO public.sys_user_role (user_id, role_id) VALUES (2, 2);

INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 2000);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 2001);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 2002);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 2003);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 2004);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 2005);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 2006);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 2007);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 2008);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 2009);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 2010);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 2011);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 2012);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 3005);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 3006);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 3007);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 3008);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 3009);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 3010);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 3011);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 3012);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 20025);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 20026);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 20060);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 20061);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 20062);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 20063);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 200250);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 200251);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 200252);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (1, 200260);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 2);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 100);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 101);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 102);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 103);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 104);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 105);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 106);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 107);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 108);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 109);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 110);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 111);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 112);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 113);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 114);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 116);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 117);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 118);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 500);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 501);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1000);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1001);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1002);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1003);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1004);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1005);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1006);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1007);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1008);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1009);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1010);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1011);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1012);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1013);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1014);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1015);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1016);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1017);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1018);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1019);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1020);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1021);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1022);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1023);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1024);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1025);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1026);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1027);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1028);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1029);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1030);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1031);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1032);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1033);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1034);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1035);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1036);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1037);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1038);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1040);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1041);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1043);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1044);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1045);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1048);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1049);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1050);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1051);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1052);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1053);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1054);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1055);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1056);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1057);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1058);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1059);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 1060);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 2000);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 2100);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 2200);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 2300);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 2310);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 2320);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 2330);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 2400);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3100);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3101);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3102);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3103);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3104);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3200);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3201);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3202);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3203);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3300);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3301);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3302);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3303);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3400);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3401);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3402);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3403);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3404);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3410);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3411);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3412);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3420);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3500);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3501);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3502);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3503);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3700);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3701);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3702);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3703);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3704);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (2, 3705);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 2);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 3);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 100);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 101);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 102);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 103);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 104);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 105);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 106);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 108);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 109);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 110);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 112);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 113);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 114);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 500);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 501);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1000);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1001);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1002);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1003);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1004);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1005);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1006);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1007);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1008);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1009);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1010);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1011);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1012);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1013);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1014);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1015);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1016);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1017);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1018);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1019);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1020);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1021);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1022);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1023);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1024);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1025);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1026);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1027);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1028);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1029);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1030);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1031);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1032);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1033);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1034);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1035);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1036);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1037);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1038);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1040);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1041);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1043);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1044);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1045);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1048);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1049);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1050);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1051);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1052);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1053);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1054);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1055);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1056);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1057);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1058);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1059);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 1060);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 2000);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 2001);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 2002);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 2003);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 2004);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 20020);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 20021);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 20022);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 20023);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 20024);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 20025);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 20026);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 200250);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 200251);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 200252);
INSERT INTO public.sys_role_menu (role_id, menu_id) VALUES (4, 200260);

INSERT INTO public.sys_job (job_id, job_name, job_group, job_executor, invoke_target, job_args, job_kwargs, cron_expression, misfire_policy, concurrent, status, create_by, create_time, update_by, update_time, remark) VALUES (104, '设备健康监控任务', 'default', 'default', 'module_task.redfish_monitor_tasks.redfish_device_monitor_job', '', '', '0 0/5 * * * *', '3', '1', '1', 'admin', '2025-07-02 20:03:58', 'admin', '2025-08-20 17:46:55', '设备监控任务每5分钟执行一次（包含硬件健康+宕机检测）');
INSERT INTO public.sys_job (job_id, job_name, job_group, job_executor, invoke_target, job_args, job_kwargs, cron_expression, misfire_policy, concurrent, status, create_by, create_time, update_by, update_time, remark) VALUES (106, '手动触发设备监控', 'default', 'default', 'module_task.redfish_monitor_tasks.manual_trigger_monitor_job', '', '{}', '', '1', '0', '1', 'admin', '2025-07-02 20:03:58', 'admin', '2025-07-02 20:03:58', '手动触发设备监控任务，用于测试或紧急检查。可通过定时任务管理界面手动执行。');
INSERT INTO public.sys_job (job_id, job_name, job_group, job_executor, invoke_target, job_args, job_kwargs, cron_expression, misfire_policy, concurrent, status, create_by, create_time, update_by, update_time, remark) VALUES (111, '设备宕机检测任务', 'default', 'default', 'module_task.redfish_monitor_tasks.device_downtime_monitor_job', '', '', '0 */2 * * * *', '3', '1', '1', 'system', '2025-08-20 15:39:26', 'admin', '2025-08-20 17:19:37', '定期检测设备业务IP连通性，发现宕机立即告警，支持1000台设备');
INSERT INTO public.sys_job (job_id, job_name, job_group, job_executor, invoke_target, job_args, job_kwargs, cron_expression, misfire_policy, concurrent, status, create_by, create_time, update_by, update_time, remark) VALUES (112, '清理旧日志和告警', 'default', 'default', 'module_task.redfish_monitor_tasks.redfish_log_cleanup_job', '30', '', '0 0 2 * * *', '3', '1', '1', 'system', '2025-08-20 15:39:26', 'admin', '2025-08-20 17:19:40', '定期清理超过30天的旧Redfish日志和已解决的告警');
INSERT INTO public.sys_job (job_id, job_name, job_group, job_executor, invoke_target, job_args, job_kwargs, cron_expression, misfire_policy, concurrent, status, create_by, create_time, update_by, update_time, remark) VALUES (113, 'Redfish日志清理任务', 'default', 'default', 'module_redfish.tasks.log_cleanup_task.cleanup_old_redfish_logs', '', '', '0 0 2 * * *', '2', '0', '1', 'admin', '2025-08-21 19:49:18', '', NULL, '自动清理30天前的Redfish日志记录，轻量版设计每日执行');

INSERT INTO public.device_info (device_id, hostname, business_ip, oob_ip, oob_port, location, operating_system, serial_number, model, manufacturer, technical_system, system_owner, business_type, redfish_username, redfish_password, monitor_enabled, last_check_time, health_status, create_by, create_time, update_by, update_time, remark) VALUES (1044, 'server-001', '192.168.10.101', '192.168.100.101', 443, 'XW_B1B07_25-26', 'CentOS 7.9', 'SN20231001', 'PowerEdge R750', 'Lenovo', '虚拟化平台', '张三', 'OB服务器（管理节点，三节点部署）', 'Administrator', 'gAAAAABo3N0jderHHijRHZlGgvX4AS_Jr8Otsj4pwjlKaVqq58z44_xwfvN70_aPoUHvBRhDlLNd07H2IYLSi51gkPj69APCpQ==', 1, '2025-10-02 19:08:09', 'critical', 'admin', '2025-07-16 15:58:07', 'admin', '2025-10-02 19:08:09', '生产环境核心服务器');
INSERT INTO public.device_info (device_id, hostname, business_ip, oob_ip, oob_port, location, operating_system, serial_number, model, manufacturer, technical_system, system_owner, business_type, redfish_username, redfish_password, monitor_enabled, last_check_time, health_status, create_by, create_time, update_by, update_time, remark) VALUES (1045, 'server-002', '192.168.10.102', '192.168.100.102', 443, 'YJ_F3D13_24-25', 'Ubuntu 20.04', 'SN20231002', 'ProLiant DL380', 'HPE', '数据库服务', '李四', 'OB服务器（管理节点，三节点部署）', 'root', '******', 1, '2025-10-02 19:08:09', 'critical', 'admin', '2025-07-16 15:58:07', 'admin', '2025-10-02 19:08:09', '数据库集群主节点');
INSERT INTO public.device_info (device_id, hostname, business_ip, oob_ip, oob_port, location, operating_system, serial_number, model, manufacturer, technical_system, system_owner, business_type, redfish_username, redfish_password, monitor_enabled, last_check_time, health_status, create_by, create_time, update_by, update_time, remark) VALUES (1046, 'server-003', '192.168.1.14', '192.168.110.182', 8084, 'YZ_B6C10_14-15', 'Ubuntu 20.04', 'SN20231003', 'ProLiant DL380', 'HP', '测试', '王五', 'OB服务器（数据节点，五节点部署）', 'Administrator', 'gAAAAABo3kY_v4_GSBxZ2zIqEQjfUZtoVRtdDgnwtfUbPBdYQe1YHQk0fmQZ1regMVmfMznF8PkmI3PyVhOZ8uOma3R0Qi9Uew==', 1, '2025-10-02 19:08:03', 'warning', 'admin', '2025-07-16 15:58:07', 'admin', '2025-10-02 19:08:03', '测试环境核心服务器');

INSERT INTO public.business_type_dict (type_id, type_code, type_name, type_description, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (1, 'OB-GMT-3N', 'OB服务器（管理节点，三节点部署）', 'OB服务器（管理节点，三节点部署）', 1, 1, '', '2025-06-08 19:45:38', 'admin', '2025-07-16 14:32:28');
INSERT INTO public.business_type_dict (type_id, type_code, type_name, type_description, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (2, 'OB-DATA-5N', 'OB服务器（数据节点，五节点部署）', 'OB服务器（数据节点，五节点部署）', 2, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO public.business_type_dict (type_id, type_code, type_name, type_description, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (3, 'TRAD-MB-2N', '传统服务器（主备两节点部署）', 'Oracle企业级数据库服务', 3, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO public.business_type_dict (type_id, type_code, type_name, type_description, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (4, 'BIGDATA-5N', '大数据服务器（五节点部署）', 'Redis内存数据库服务', 4, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO public.business_type_dict (type_id, type_code, type_name, type_description, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (5, 'VIRT-CLUSTER-8_16N', '虚拟化宿主机（一个集群内16台或8台部署）', 'ElasticSearch搜索引擎服务', 5, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO public.business_type_dict (type_id, type_code, type_name, type_description, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (6, 'CLOUD-CTRL', '云资源服务器（管控节点）', 'Apache Kafka消息中间件服务', 5, 1, '', '2025-06-08 19:45:38', 'admin', '2025-06-11 18:53:13');
INSERT INTO public.business_type_dict (type_id, type_code, type_name, type_description, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (7, 'BIGDATA-3N', '大数据服务器（三节点部署）', 'Web应用程序服务器', 7, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO public.business_type_dict (type_id, type_code, type_name, type_description, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (8, 'CLOUD-3N', '云资源服务器（三节点部署）', '业务应用程序服务', 8, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO public.business_type_dict (type_id, type_code, type_name, type_description, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (9, 'CLOUD-5N', '云资源服务器（五节点部署）', 'API网关服务', 9, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO public.business_type_dict (type_id, type_code, type_name, type_description, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (12, 'STORAGE', '存储服务', '文件存储相关服务', 12, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO public.business_type_dict (type_id, type_code, type_name, type_description, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (14, 'OTHER', '其他服务', '其他类型业务服务', 99, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');

INSERT INTO public.hardware_type_dict (type_id, type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (109, 'oob_connectivity', '带外IP连通性测试123', '测试编辑描述', 'network', 0, 1, 'admin', '2025-09-25 19:09:19', 'admin', '2025-10-02 19:07:43');
INSERT INTO public.hardware_type_dict (type_id, type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (1, 'cpu', 'CPU处理器', 'Central Processing Unit 中央处理器', 'compute', 1, 1, '', '2025-06-08 19:45:38', 'admin', '2025-07-12 18:05:47');
INSERT INTO public.hardware_type_dict (type_id, type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (2, 'memory', '内存', 'RAM 随机存取存储器', 'compute', 2, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO public.hardware_type_dict (type_id, type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (105, 'system', '系统信息', '系统基本信息（型号、BIOS、序列号等）', 'system', 3, 1, 'system', '2025-08-17 21:22:51', '', '2025-08-17 21:22:51');
INSERT INTO public.hardware_type_dict (type_id, type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (104, 'storage', '存储设备', '存储设备（硬盘、SSD、控制器等）', 'storage', 10, 1, 'system', '2025-08-15 23:18:18', '', '2025-08-15 23:18:18');
INSERT INTO public.hardware_type_dict (type_id, type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (8, 'network', '网卡', '网络接口卡', 'network', 20, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO public.hardware_type_dict (type_id, type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (11, 'power', '电源', 'Power Supply Unit 电源供应单元', 'power', 30, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO public.hardware_type_dict (type_id, type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (14, 'fan', '风扇', '散热风扇', 'cooling', 40, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO public.hardware_type_dict (type_id, type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (102, 'bmc', 'BMC管理器', 'Baseboard Management Controller 基板管理控制器', 'management', 41, 1, 'system', '2025-08-15 22:18:34', '', '2025-08-15 22:18:34');
INSERT INTO public.hardware_type_dict (type_id, type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (15, 'temperature', '温度传感器', '温度监控传感器', 'cooling', 41, 1, '', '2025-06-08 19:45:38', '', '2025-06-08 19:45:38');
INSERT INTO public.hardware_type_dict (type_id, type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (103, 'firmware', '固件版本', '系统固件信息监控', 'management', 42, 1, 'system', '2025-08-15 22:18:34', '', '2025-08-15 22:18:34');
INSERT INTO public.hardware_type_dict (type_id, type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (108, 'downtime', '宕机', '设备网络连通性和宕机状态监控', 'network', 50, 1, 'system', '2025-08-20 16:41:08', 'admin', '2025-10-01 15:59:14');
INSERT INTO public.hardware_type_dict (type_id, type_code, type_name, type_description, category, sort_order, is_active, create_by, create_time, update_by, update_time) VALUES (101, 'unknown', '未知硬件', '未识别的硬件组件', 'other', 100, 1, 'system', '2025-08-15 17:01:46', '', '2025-08-15 17:01:46');

INSERT INTO public.business_hardware_urgency_rules (rule_id, business_type, hardware_type, urgency_level, description, is_active, create_by, create_time, update_by, update_time) VALUES (1, 'OB-GMT-3N', 'memory', 'urgent', 'OB服务器CPU故障为紧急', 1, 'admin', '2025-06-08 16:07:00', 'admin', '2025-07-16 14:32:38');
INSERT INTO public.business_hardware_urgency_rules (rule_id, business_type, hardware_type, urgency_level, description, is_active, create_by, create_time, update_by, update_time) VALUES (2, 'OB-DATA-5N', 'memory', 'scheduled', 'OB服务器内存故障为紧急', 1, 'admin', '2025-06-08 16:07:00', 'admin', '2025-07-16 14:26:47');
INSERT INTO public.business_hardware_urgency_rules (rule_id, business_type, hardware_type, urgency_level, description, is_active, create_by, create_time, update_by, update_time) VALUES (100, 'OB-DATA-5N', 'downtime', 'urgent', NULL, 1, 'admin', '2025-07-13 20:24:40', 'admin', '2025-09-25 19:35:52');

-- Sequence alignment
SELECT pg_catalog.setval('public.sys_dept_dept_id_seq', (SELECT COALESCE(MAX(dept_id), 0) FROM public.sys_dept), true);
SELECT pg_catalog.setval('public.sys_post_post_id_seq', (SELECT COALESCE(MAX(post_id), 0) FROM public.sys_post), true);
SELECT pg_catalog.setval('public.sys_user_user_id_seq', (SELECT COALESCE(MAX(user_id), 0) FROM public.sys_user), true);
SELECT pg_catalog.setval('public.sys_role_role_id_seq', (SELECT COALESCE(MAX(role_id), 0) FROM public.sys_role), true);
SELECT pg_catalog.setval('public.sys_menu_menu_id_seq', (SELECT COALESCE(MAX(menu_id), 0) FROM public.sys_menu), true);
SELECT pg_catalog.setval('public.sys_dict_type_dict_id_seq', (SELECT COALESCE(MAX(dict_id), 0) FROM public.sys_dict_type), true);
SELECT pg_catalog.setval('public.sys_dict_data_dict_code_seq', (SELECT COALESCE(MAX(dict_code), 0) FROM public.sys_dict_data), true);
SELECT pg_catalog.setval('public.sys_config_config_id_seq', (SELECT COALESCE(MAX(config_id), 0) FROM public.sys_config), true);
SELECT pg_catalog.setval('public.sys_job_job_id_seq', (SELECT COALESCE(MAX(job_id), 0) FROM public.sys_job), true);
SELECT pg_catalog.setval('public.device_info_device_id_seq', (SELECT COALESCE(MAX(device_id), 0) FROM public.device_info), true);
SELECT pg_catalog.setval('public.business_type_dict_type_id_seq', (SELECT COALESCE(MAX(type_id), 0) FROM public.business_type_dict), true);
SELECT pg_catalog.setval('public.hardware_type_dict_type_id_seq', (SELECT COALESCE(MAX(type_id), 0) FROM public.hardware_type_dict), true);
SELECT pg_catalog.setval('public.business_hardware_urgency_rules_rule_id_seq', (SELECT COALESCE(MAX(rule_id), 0) FROM public.business_hardware_urgency_rules), true);
SELECT pg_catalog.setval('public.alert_info_alert_id_seq', 1, false);
SELECT pg_catalog.setval('public.maintenance_schedule_schedule_id_seq', 1, false);
SELECT pg_catalog.setval('public.sys_oper_log_oper_id_seq', 1, false);
SELECT pg_catalog.setval('public.sys_logininfor_info_id_seq', 1, false);
SELECT pg_catalog.setval('public.sys_job_log_job_log_id_seq', 1, false);
SELECT pg_catalog.setval('public.sys_notice_notice_id_seq', 1, false);
SELECT pg_catalog.setval('public.gen_table_table_id_seq', 1, false);
SELECT pg_catalog.setval('public.gen_table_column_column_id_seq', 1, false);
