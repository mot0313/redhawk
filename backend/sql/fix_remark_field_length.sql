-- 修复remark字段长度限制问题
-- 将remark字段从VARCHAR(500)扩展为TEXT类型

DO $$
BEGIN
    -- 扩展remark字段长度
    ALTER TABLE redfish_log ALTER COLUMN remark TYPE TEXT;
    
    RAISE NOTICE '已将redfish_log.remark字段类型修改为TEXT';
    
    -- 验证字段类型
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'redfish_log' 
        AND column_name = 'remark' 
        AND data_type = 'text'
    ) THEN
        RAISE NOTICE '✓ 字段类型验证成功：remark现在是TEXT类型';
    ELSE
        RAISE NOTICE '✗ 字段类型验证失败';
    END IF;
    
END $$;

-- 查看字段信息
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'redfish_log' 
AND column_name = 'remark';
