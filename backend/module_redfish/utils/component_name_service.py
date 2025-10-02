"""
组件名称服务
负责管理组件类型到标准名称的映射，从hardware_type_dict表获取标准名称
使用Redis缓存实现进程间共享
"""
import logging
import json
from typing import Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from config.get_db import get_sync_db
import redis
from config.env import RedisConfig

logger = logging.getLogger(__name__)


class ComponentNameService:
    """组件名称服务 - 使用Redis缓存实现进程间共享"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ComponentNameService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            # Redis配置
            self._redis_client = redis.Redis(
                host=RedisConfig.redis_host,
                port=RedisConfig.redis_port,
                password=RedisConfig.redis_password,
                db=RedisConfig.redis_database,  # 使用系统配置的Redis数据库
                decode_responses=True
            )
            
            # Redis键名
            self._mapping_key = "component_name_mappings"
            self._special_components_key = "special_components"
            
            # 特殊组件配置
            self._special_components: Dict[str, str] = {
                "MemorySummary": "MemorySummary",
                "System": "System",
            }
            self._default_name = "未知组件"
            
            # 初始化Redis缓存
            self._initialize_redis_cache()
            ComponentNameService._initialized = True
    
    def _initialize_redis_cache(self):
        """初始化Redis缓存"""
        try:
            # 检查Redis连接
            self._redis_client.ping()
            
            # 检查缓存是否存在，如果不存在则从数据库加载
            if not self._redis_client.exists(self._mapping_key):
                self._load_mapping_from_db()
            
            # 存储特殊组件配置到Redis
            self._redis_client.hset(self._special_components_key, mapping=self._special_components)
            
            logger.info("Redis cache initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {str(e)}")
            # 降级到内存缓存
            self._fallback_to_memory_cache()
    
    def _load_mapping_from_db(self):
        """从数据库加载映射到Redis"""
        try:
            logger.info("Starting to load component name mappings from database...")
            db = next(get_sync_db())
            try:
                # 查询所有激活的硬件类型
                result = db.execute(text("""
                    SELECT type_code, type_name 
                    FROM hardware_type_dict 
                    WHERE is_active = 1
                """)).fetchall()
                
                logger.info(f"Database query returned {len(result)} rows")
                
                # 构建映射字典
                mappings = {}
                for row in result:
                    type_code = row[0]
                    type_name = row[1]
                    mappings[type_code] = type_name
                
                logger.info(f"Built {len(mappings)} mappings from database")
                
                # 存储到Redis
                if mappings:
                    self._redis_client.hset(self._mapping_key, mapping=mappings)
                    logger.info(f"Successfully loaded {len(mappings)} component name mappings to Redis")
                else:
                    logger.warning("No mappings found, loading default mappings")
                    # 如果没有数据，使用默认映射
                    self._load_default_mapping_to_redis()
            finally:
                db.close()
                logger.info("Database connection closed")
                
        except Exception as e:
            logger.error(f"Failed to load component name mappings from database: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # 使用默认映射作为降级策略
            self._load_default_mapping_to_redis()
    
    def _load_default_mapping_to_redis(self):
        """加载默认映射到Redis作为降级策略"""
        default_mappings = {
            "cpu": "CPU处理器",
            "memory": "内存",
            "storage": "存储设备",
            "network": "网卡",
            "power": "电源",
            "fan": "风扇",
            "temperature": "温度传感器",
            "system": "系统信息",
            "bmc": "BMC管理器",
            "firmware": "固件版本",
            "downtime": "宕机",
            "oob_connectivity": "带外IP连通性",
            "unknown": "未知硬件"
        }
        self._redis_client.hset(self._mapping_key, mapping=default_mappings)
        logger.warning("Using default component name mappings due to database error")
    
    def _fallback_to_memory_cache(self):
        """降级到内存缓存"""
        self._memory_cache = {}
        self._use_memory_cache = True
        logger.warning("Falling back to memory cache due to Redis error")
    
    def get_standard_name(self, component_type: str, component_name: Optional[str] = None) -> str:
        """
        获取组件的标准名称
        
        Args:
            component_type: 组件类型（如：cpu, memory, downtime等）
            component_name: 组件名称（可选，用于特殊组件判断）
            
        Returns:
            str: 标准化的组件名称
        """
        if not component_type:
            return self._default_name
        
        try:
            # 检查是否为特殊组件
            if component_name:
                special_name = self._redis_client.hget(self._special_components_key, component_name)
                if special_name:
                    return special_name
            
            # 标准化组件类型（转换为小写）
            normalized_type = component_type.lower().strip()
            
            # 从Redis获取标准名称
            standard_name = self._redis_client.hget(self._mapping_key, normalized_type)
            
            if standard_name:
                return standard_name
            
            # 如果找不到映射，返回组件类型本身或默认名称
            logger.warning(f"No mapping found for component type: {component_type}")
            return component_type if component_type else self._default_name
            
        except Exception as e:
            logger.error(f"Error getting standard name from Redis: {str(e)}")
            # 降级处理
            return self._get_standard_name_fallback(component_type, component_name)
    
    def refresh_mapping(self):
        """刷新映射关系（重新从数据库加载到Redis）"""
        logger.info("Refreshing component name mappings...")
        try:
            self._load_mapping_from_db()
            logger.info("Component name mappings refreshed successfully")
        except Exception as e:
            logger.error(f"Failed to refresh component name mappings: {str(e)}")
    
    def get_all_mappings(self) -> Dict[str, str]:
        """获取所有映射关系（用于调试）"""
        try:
            return self._redis_client.hgetall(self._mapping_key)
        except Exception as e:
            logger.error(f"Error getting all mappings from Redis: {str(e)}")
            return {}
    
    def add_special_component(self, component_name: str, standard_name: str):
        """添加特殊组件的自定义名称"""
        try:
            self._redis_client.hset(self._special_components_key, component_name, standard_name)
            logger.info(f"Added special component mapping: {component_name} -> {standard_name}")
        except Exception as e:
            logger.error(f"Error adding special component to Redis: {str(e)}")
    
    def _get_standard_name_fallback(self, component_type: str, component_name: Optional[str] = None) -> str:
        """降级处理：当Redis不可用时使用默认值"""
        if not component_type:
            return self._default_name
        
        # 检查特殊组件
        if component_name and component_name in self._special_components:
            return self._special_components[component_name]
        
        # 使用默认映射
        normalized_type = component_type.lower().strip()
        default_mappings = {
            "cpu": "CPU处理器",
            "memory": "内存",
            "storage": "存储设备",
            "network": "网卡",
            "power": "电源",
            "fan": "风扇",
            "temperature": "温度传感器",
            "system": "系统信息",
            "bmc": "BMC管理器",
            "firmware": "固件版本",
            "downtime": "宕机",
            "oob_connectivity": "带外IP连通性测试",
            "unknown": "未知硬件"
        }
        
        return default_mappings.get(normalized_type, component_type if component_type else self._default_name)


# 全局实例
component_name_service = ComponentNameService()

