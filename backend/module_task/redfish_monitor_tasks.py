"""
APScheduler定时任务配置
用于定期执行设备监控任务
定时任务配置由前端通过sys_job表管理
"""
import asyncio
from datetime import datetime
from typing import Dict, Any
from loguru import logger
from module_redfish.celery_tasks import monitor_all_devices
from module_redfish.websocket_manager import websocket_manager


def redfish_device_monitor_job(*args, **kwargs):
    """
    设备监控定时任务执行函数 - 同步版本
    该函数会被APScheduler调用，任务配置由sys_job表管理
    
    Args:
        *args: 位置参数（来自sys_job.job_args）
        **kwargs: 关键字参数（来自sys_job.job_kwargs）
    """
    try:
        logger.info("开始执行设备监控定时任务")
        logger.info(f"接收到的参数 - args: {args}, kwargs: {kwargs}")
        
        # 记录任务执行时间
        execution_time = datetime.now()
        
        # 提交Celery异步任务
        result = monitor_all_devices.delay()
        
        logger.info(f"设备监控Celery任务已提交，任务ID: {result.id}")
        
        # 创建异步任务进行WebSocket广播
        try:
            # 检查是否有运行的事件循环
            loop = asyncio.get_running_loop()
            # 在已有循环中创建任务
            loop.create_task(_broadcast_monitor_start(execution_time, result.id))
        except RuntimeError:
            # 如果没有运行的事件循环，在线程中运行
            import threading
            def run_broadcast():
                asyncio.run(_broadcast_monitor_start(execution_time, result.id))
            threading.Thread(target=run_broadcast, daemon=True).start()
        
        # 返回执行结果
        return {
            "success": True,
            "task_id": result.id,
            "execution_time": execution_time.isoformat(),
            "message": "设备监控任务执行成功"
        }
        
    except Exception as e:
        error_msg = f"执行设备监控任务失败: {str(e)}"
        logger.error(error_msg)
        
        # 广播错误通知
        try:
            # 检查是否有运行的事件循环
            loop = asyncio.get_running_loop()
            # 在已有循环中创建任务
            loop.create_task(_broadcast_monitor_error(error_msg))
        except RuntimeError:
            # 如果没有运行的事件循环，在线程中运行
            import threading
            def run_broadcast():
                asyncio.run(_broadcast_monitor_error(error_msg))
            threading.Thread(target=run_broadcast, daemon=True).start()
        
        # 重新抛出异常，让APScheduler记录
        raise e


async def async_redfish_device_monitor_job(*args, **kwargs):
    """
    设备监控定时任务执行函数 - 异步版本
    该函数会被APScheduler调用，任务配置由sys_job表管理
    
    Args:
        *args: 位置参数（来自sys_job.job_args）
        **kwargs: 关键字参数（来自sys_job.job_kwargs）
    """
    try:
        logger.info("开始执行设备监控定时任务（异步版本）")
        logger.info(f"接收到的参数 - args: {args}, kwargs: {kwargs}")
        
        # 记录任务执行时间
        execution_time = datetime.now()
        
        # 提交Celery异步任务
        result = monitor_all_devices.delay()
        
        logger.info(f"设备监控Celery任务已提交，任务ID: {result.id}")
        
        # 异步广播任务开始通知
        await _broadcast_monitor_start(execution_time, result.id)
        
        # 返回执行结果
        return {
            "success": True,
            "task_id": result.id,
            "execution_time": execution_time.isoformat(),
            "message": "设备监控任务执行成功"
        }
        
    except Exception as e:
        error_msg = f"执行设备监控任务失败: {str(e)}"
        logger.error(error_msg)
        
        # 广播错误通知
        await _broadcast_monitor_error(error_msg)
        
        # 重新抛出异常，让APScheduler记录
        raise e


def manual_trigger_monitor_job(*args, **kwargs):
    """
    手动触发设备监控任务
    可通过定时任务管理界面手动执行
    
    Args:
        *args: 位置参数
        **kwargs: 关键字参数，可包含user_id
    """
    try:
        user_id = kwargs.get('user_id', '系统')
        logger.info(f"手动触发设备监控任务，触发用户: {user_id}")
        
        # 调用主监控函数
        result = redfish_device_monitor_job(*args, **kwargs)
        
        # 添加手动触发标识
        result['trigger_type'] = 'manual'
        result['trigger_user'] = user_id
        
        return result
        
    except Exception as e:
        logger.error(f"手动触发设备监控失败: {str(e)}")
        raise e


async def _broadcast_monitor_start(execution_time: datetime, task_id: str):
    """
    广播监控任务开始通知
    
    Args:
        execution_time: 执行时间
        task_id: 任务ID
    """
    try:
        message = {
            "type": "monitor_task",
            "action": "started",
            "task_id": task_id,
            "execution_time": execution_time.isoformat(),
            "message": "设备监控任务已开始执行",
            "timestamp": datetime.now().isoformat()
        }
        
        # 广播到dashboard房间
        await websocket_manager.broadcast_to_room("dashboard", message)
        logger.debug("已广播监控任务开始通知")
        
    except Exception as e:
        logger.error(f"广播监控任务开始通知失败: {str(e)}")


async def _broadcast_monitor_error(error_message: str):
    """
    广播监控任务错误通知
    
    Args:
        error_message: 错误信息
    """
    try:
        message = {
            "type": "monitor_task",
            "action": "error",
            "error": error_message,
            "message": f"设备监控任务执行失败: {error_message}",
            "timestamp": datetime.now().isoformat()
        }
        
        # 广播到dashboard房间
        await websocket_manager.broadcast_to_room("dashboard", message)
        logger.debug("已广播监控任务错误通知")
        
    except Exception as e:
        logger.error(f"广播监控任务错误通知失败: {str(e)}")


# 监控配置类
class MonitorConfig:
    """监控配置管理（兼容性保留）"""
    
    # 默认配置
    DEFAULT_MONITOR_INTERVAL = 5  # 分钟
    DEFAULT_MAX_RETRY = 3
    DEFAULT_TIMEOUT = 300  # 秒
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """获取监控配置"""
        return {
            "monitor_interval": cls.DEFAULT_MONITOR_INTERVAL,
            "max_retry": cls.DEFAULT_MAX_RETRY,
            "timeout": cls.DEFAULT_TIMEOUT,
            "task_status": {
                "status": "active",
                "message": "任务配置由数据库sys_job表管理"
            }
        }
    
    @classmethod
    async def update_config(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新监控配置（兼容性方法）
        
        Args:
            config: 新配置
            
        Returns:
            Dict: 更新结果
        """
        try:
            # 更新监控间隔（这里只是更新类变量，实际间隔由数据库控制）
            if "monitor_interval" in config:
                interval = config["monitor_interval"]
                if 1 <= interval <= 60:  # 限制在1-60分钟之间
                    cls.DEFAULT_MONITOR_INTERVAL = interval
                    logger.info(f"监控间隔配置已更新为: {interval}分钟（实际间隔请在定时任务管理界面修改）")
                else:
                    raise ValueError("监控间隔必须在1-60分钟之间")
            
            return {
                "success": True,
                "message": "监控配置已更新。注意：实际定时任务间隔请在定时任务管理界面修改cron表达式。",
                "config": cls.get_config()
            }
            
        except Exception as e:
            logger.error(f"更新监控配置失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "更新监控配置失败"
            }


# 兼容性函数 - 保持向后兼容
class RedfishSchedulerTasks:
    """
    Redfish监控定时任务管理类（兼容性保留）
    主要功能已迁移到独立函数，建议使用数据库配置方式管理任务
    """
    
    @classmethod
    def execute_device_monitor_task(cls):
        """兼容性方法 - 调用新的函数式实现"""
        return redfish_device_monitor_job()
    
    @classmethod
    async def manual_trigger_monitor(cls, user_id: str = None) -> Dict[str, Any]:
        """兼容性方法 - 手动触发监控"""
        try:
            result = manual_trigger_monitor_job(user_id=user_id)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "手动触发设备监控失败"
            }
    
    @classmethod
    async def init_monitoring_tasks(cls):
        """
        初始化监控定时任务（兼容性方法）
        新版本中任务由数据库配置，系统启动时自动加载
        """
        try:
            logger.info("兼容性方法：init_monitoring_tasks")
            logger.info("注意：当前版本的定时任务由数据库sys_job表管理")
            logger.info("请确保已执行SQL脚本：sql/add_redfish_monitor_jobs.sql")
            logger.info("系统启动时会自动从数据库加载定时任务")
            
            # 这里不需要实际操作，因为任务已经通过数据库配置
            return True
            
        except Exception as e:
            logger.error(f"初始化监控任务失败: {str(e)}")
            return False
    
    @classmethod
    def get_monitor_task_status(cls) -> Dict[str, Any]:
        """
        获取监控任务状态（兼容性方法）
        
        Returns:
            Dict: 任务状态信息
        """
        try:
            # 返回兼容格式的状态信息
            return {
                "status": "active",
                "message": "任务配置由数据库sys_job表管理，请在定时任务管理界面查看详细状态",
                "task_name": "设备健康监控任务",
                "config_source": "database",
                "management_url": "/monitor/job"
            }
                
        except Exception as e:
            logger.error(f"获取监控任务状态失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "获取任务状态失败"
            }
    
    @classmethod
    def update_monitor_interval(cls, interval_minutes: int):
        """
        更新监控间隔（兼容性方法）
        
        Args:
            interval_minutes: 新的监控间隔（分钟）
        """
        try:
            logger.info(f"兼容性方法：update_monitor_interval({interval_minutes})")
            logger.warning("注意：当前版本的定时任务间隔由数据库sys_job表管理")
            logger.info("请在定时任务管理界面修改cron表达式来调整执行间隔")
            logger.info("例如：每5分钟执行 = '0 */5 * * * *'")
            logger.info(f"     每{interval_minutes}分钟执行 = '0 */{interval_minutes} * * * *'")
            
            # 更新默认配置（仅用于显示）
            MonitorConfig.DEFAULT_MONITOR_INTERVAL = interval_minutes
            
        except Exception as e:
            logger.error(f"更新监控间隔失败: {str(e)}")


# 任务配置信息 - 用于在sys_job表中配置
REDFISH_MONITOR_JOB_CONFIG = {
    "job_name": "设备健康监控任务",
    "job_group": "default",
    "job_executor": "default",
    "invoke_target": "module_task.redfish_monitor_tasks.redfish_device_monitor_job",
    "job_args": "",  # 可以传递参数，如设备组ID等
    "job_kwargs": "",  # JSON格式的关键字参数
    "cron_expression": "0 */5 * * * *",  # 每5分钟执行一次
    "misfire_policy": "3",  # 错过执行则放弃
    "concurrent": "1",  # 禁止并发执行
    "status": "0",  # 启用状态
    "remark": "定期监控Redfish设备健康状态，支持1000台设备"
}

# 异步版本的任务配置
ASYNC_REDFISH_MONITOR_JOB_CONFIG = {
    "job_name": "设备健康监控任务（异步）",
    "job_group": "default",
    "job_executor": "default",
    "invoke_target": "module_task.redfish_monitor_tasks.async_redfish_device_monitor_job",
    "job_args": "",
    "job_kwargs": "",
    "cron_expression": "0 */5 * * * *",  # 每5分钟执行一次
    "misfire_policy": "3",
    "concurrent": "1",
    "status": "0",
    "remark": "定期监控Redfish设备健康状态（异步版本）"
}

# 手动触发任务配置
MANUAL_TRIGGER_JOB_CONFIG = {
    "job_name": "手动触发设备监控",
    "job_group": "default",
    "job_executor": "default", 
    "invoke_target": "module_task.redfish_monitor_tasks.manual_trigger_monitor_job",
    "job_args": "",
    "job_kwargs": "",
    "cron_expression": "",  # 手动触发，无需cron表达式
    "misfire_policy": "1",  # 立即执行
    "concurrent": "0",  # 允许并发
    "status": "1",  # 默认暂停，需要时手动触发
    "remark": "手动触发设备监控任务，用于测试或紧急检查"
}


# ---------------- 新增的任务配置 ----------------

# 清理旧日志任务配置
CLEANUP_OLD_LOGS_JOB_CONFIG = {
    "job_name": "清理旧日志和告警",
    "job_group": "redfish",
    "job_executor": "default",
    "invoke_target": "module_redfish.celery_tasks.cleanup_old_logs",
    "job_args": "30",  # 保留30天
    "job_kwargs": "",
    "cron_expression": "0 0 2 * * *",  # 每天凌晨2点执行
    "misfire_policy": "3",  # 错过则放弃
    "concurrent": "1",  # 禁止并发
    "status": "0",  # 启用
    "remark": "定期清理超过30天的旧Redfish日志和已解决的告警"
}

# 更新设备健康状态任务配置
UPDATE_HEALTH_STATUS_JOB_CONFIG = {
    "job_name": "更新设备健康状态",
    "job_group": "redfish",
    "job_executor": "default",
    "invoke_target": "module_redfish.celery_tasks.update_device_health_status",
    "job_args": "",
    "job_kwargs": "",
    "cron_expression": "0 */5 * * * *",  # 每5分钟执行
    "misfire_policy": "3",
    "concurrent": "1",
    "status": "0",
    "remark": "定期从数据库汇总并更新所有设备的健康状态"
}

# 推送实时告警任务配置
PUSH_REALTIME_ALERTS_JOB_CONFIG = {
    "job_name": "推送实时告警摘要",
    "job_group": "redfish",
    "job_executor": "default",
    "invoke_target": "module_redfish.celery_tasks.push_realtime_alerts",
    "job_args": "",
    "job_kwargs": "",
    "cron_expression": "*/10 * * * * *",  # 每10秒执行
    "misfire_policy": "3",
    "concurrent": "1",
    "status": "0",
    "remark": "定期推送实时告警摘要到前端"
}

def get_all_redfish_job_configs():
    """获取所有Redfish相关的定时任务配置"""
    return [
        REDFISH_MONITOR_JOB_CONFIG,
        ASYNC_REDFISH_MONITOR_JOB_CONFIG, 
        MANUAL_TRIGGER_JOB_CONFIG,
        CLEANUP_OLD_LOGS_JOB_CONFIG,
        UPDATE_HEALTH_STATUS_JOB_CONFIG,
        PUSH_REALTIME_ALERTS_JOB_CONFIG,
    ]


# 使用说明
"""
使用说明：
1. 通过前端定时任务管理界面，添加以上配置到sys_job表
2. 系统启动时会自动从数据库读取并注册定时任务
3. 可以通过界面修改cron表达式、参数等配置
4. 支持手动触发、暂停、恢复等操作
5. 所有任务执行日志会自动记录到sys_job_log表

示例SQL插入语句：
INSERT INTO sys_job (job_name, job_group, job_executor, invoke_target, job_args, job_kwargs, 
                     cron_expression, misfire_policy, concurrent, status, create_by, create_time, remark)
VALUES ('设备健康监控任务', 'redfish', 'default', 
        'module_task.redfish_monitor_tasks.redfish_device_monitor_job',
        '', '', '0 */5 * * * *', '3', '1', '0', 'admin', NOW(),
        '定期监控Redfish设备健康状态，支持1000台设备');
""" 