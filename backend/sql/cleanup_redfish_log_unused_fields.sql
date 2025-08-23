-- 清理redfish_log表中的无用字段
-- 删除sensor_type和sensor_number字段，因为前端已不再使用

DO $$
BEGIN
    -- 检查并删除sensor_type字段
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'redfish_log' 
        AND column_name = 'sensor_type'
    ) THEN
        ALTER TABLE redfish_log DROP COLUMN sensor_type;
        RAISE NOTICE '✓ 已删除sensor_type字段';
    ELSE
        RAISE NOTICE '! sensor_type字段不存在，跳过';
    END IF;
    
    -- 检查并删除sensor_number字段
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'redfish_log' 
        AND column_name = 'sensor_number'
    ) THEN
        ALTER TABLE redfish_log DROP COLUMN sensor_number;
        RAISE NOTICE '✓ 已删除sensor_number字段';
    ELSE
        RAISE NOTICE '! sensor_number字段不存在，跳过';
    END IF;
    
    -- 检查并删除message_id字段
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'redfish_log' 
        AND column_name = 'message_id'
    ) THEN
        ALTER TABLE redfish_log DROP COLUMN message_id;
        RAISE NOTICE '✓ 已删除message_id字段';
    ELSE
        RAISE NOTICE '! message_id字段不存在，跳过';
    END IF;
    
    -- 检查并扩展remark字段类型（如果还未扩展）
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'redfish_log' 
        AND column_name = 'remark' 
        AND data_type = 'character varying'
    ) THEN
        ALTER TABLE redfish_log ALTER COLUMN remark TYPE TEXT;
        RAISE NOTICE '✓ 已将remark字段扩展为TEXT类型';
    ELSE
        RAISE NOTICE '! remark字段已是TEXT类型，跳过';
    END IF;
    
END $$;

-- 查看清理后的表结构
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'redfish_log'
ORDER BY ordinal_position;
