from typing import Any
import json
from redis import asyncio as aioredis
from fastapi import Request
from config.env import RedisConfig
from config.enums import RedisInitKeyConfig
from config.get_redis import RedisUtil
from module_admin.entity.vo.cache_vo import CacheInfoModel, CacheMonitorModel
from module_admin.entity.vo.common_vo import CrudResponseModel


class CacheService:
    """
    缓存监控模块服务层
    """

    @classmethod
    async def get_cache_monitor_statistical_info_services(cls, request: Request):
        """
        获取缓存监控信息service

        :param request: Request对象
        :return: 缓存监控信息
        """
        info = await request.app.state.redis.info()
        db_size = await request.app.state.redis.dbsize()
        command_stats_dict = await request.app.state.redis.info('commandstats')
        command_stats = [
            dict(name=key.split('_')[1], value=str(value.get('calls'))) for key, value in command_stats_dict.items()
        ]
        result = CacheMonitorModel(commandStats=command_stats, dbSize=db_size, info=info)

        return result

    @classmethod
    async def get_cache_monitor_cache_name_services(cls):
        """
        获取缓存名称列表信息service

        :return: 缓存名称列表信息
        """
        name_list = []
        for key_config in RedisInitKeyConfig:
            name_list.append(
                CacheInfoModel(
                    cacheKey='',
                    cacheName=key_config.key,
                    cacheValue='',
                    remark=key_config.remark,
                )
            )

        return name_list

    @classmethod
    async def get_cache_monitor_cache_key_services(cls, request: Request, cache_name: str):
        """
        获取缓存键名列表信息service

        :param request: Request对象
        :param cache_name: 缓存名称
        :return: 缓存键名列表信息
        """
        cache_keys = await request.app.state.redis.keys(f'{cache_name}*')
        cache_key_list = [key.split(':', 1)[1] for key in cache_keys if key.startswith(f'{cache_name}:')]

        return cache_key_list

    @classmethod
    async def get_cache_monitor_cache_value_services(cls, request: Request, cache_name: str, cache_key: str):
        """
        获取缓存内容信息service

        :param request: Request对象
        :param cache_name: 缓存名称
        :param cache_key: 缓存键名
        :return: 缓存内容信息
        """
        cache_value = await request.app.state.redis.get(f'{cache_name}:{cache_key}')

        return CacheInfoModel(cacheKey=cache_key, cacheName=cache_name, cacheValue=cache_value, remark='')

    @classmethod
    async def clear_cache_monitor_cache_name_services(cls, request: Request, cache_name: str):
        """
        清除缓存名称对应所有键值service

        :param request: Request对象
        :param cache_name: 缓存名称
        :return: 操作缓存响应信息
        """
        cache_keys = await request.app.state.redis.keys(f'{cache_name}*')
        if cache_keys:
            await request.app.state.redis.delete(*cache_keys)

        return CrudResponseModel(is_success=True, message=f'{cache_name}对应键值清除成功')

    @classmethod
    async def clear_cache_monitor_cache_key_services(cls, request: Request, cache_key: str):
        """
        清除缓存名称对应所有键值service

        :param request: Request对象
        :param cache_key: 缓存键名
        :return: 操作缓存响应信息
        """
        cache_keys = await request.app.state.redis.keys(f'*{cache_key}')
        if cache_keys:
            await request.app.state.redis.delete(*cache_keys)

        return CrudResponseModel(is_success=True, message=f'{cache_key}清除成功')

    @classmethod
    async def clear_cache_monitor_all_services(cls, request: Request):
        """
        清除所有缓存service

        :param request: Request对象
        :return: 操作缓存响应信息
        """
        cache_keys = await request.app.state.redis.keys()
        if cache_keys:
            await request.app.state.redis.delete(*cache_keys)

        await RedisUtil.init_sys_dict(request.app.state.redis)
        await RedisUtil.init_sys_config(request.app.state.redis)

        return CrudResponseModel(is_success=True, message='所有缓存清除成功')

    @classmethod
    async def set_cache(cls, key: str, value: Any, expire: int = -1):
        """
        设置缓存（通用方法，不依赖request）

        :param key: 缓存键
        :param value: 缓存值
        :param expire: 过期时间（秒），-1表示不过期
        """
        redis = None
        try:
            redis = await aioredis.from_url(
                url=f'redis://{RedisConfig.redis_host}',
                port=RedisConfig.redis_port,
                username=RedisConfig.redis_username,
                password=RedisConfig.redis_password,
                db=RedisConfig.redis_database,
                encoding='utf-8',
                decode_responses=True,
            )
            serialized_value = json.dumps(value, ensure_ascii=False)
            if expire > 0:
                await redis.set(key, serialized_value, ex=expire)
            else:
                await redis.set(key, serialized_value)
        finally:
            if redis:
                await redis.close()

    @classmethod
    async def get_cache(cls, key: str) -> Any:
        """
        获取缓存（通用方法，不依赖request）

        :param key: 缓存键
        :return: 缓存值
        """
        redis = None
        try:
            redis = await aioredis.from_url(
                url=f'redis://{RedisConfig.redis_host}',
                port=RedisConfig.redis_port,
                username=RedisConfig.redis_username,
                password=RedisConfig.redis_password,
                db=RedisConfig.redis_database,
                encoding='utf-8',
                decode_responses=True,
            )
            cached_value = await redis.get(key)
            if cached_value:
                return json.loads(cached_value)
            return None
        finally:
            if redis:
                await redis.close()

    @classmethod
    async def delete_cache(cls, key: str):
        """
        删除缓存（通用方法，不依赖request）

        :param key: 缓存键
        """
        redis = None
        try:
            redis = await aioredis.from_url(
                url=f'redis://{RedisConfig.redis_host}',
                port=RedisConfig.redis_port,
                username=RedisConfig.redis_username,
                password=RedisConfig.redis_password,
                db=RedisConfig.redis_database,
                encoding='utf-8',
                decode_responses=True,
            )
            await redis.delete(key)
        finally:
            if redis:
                await redis.close()
