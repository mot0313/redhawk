"""
APScheduler定时任务配置
用于定期执行设备监控任务
定时任务配置由前端通过sys_job表管理
"""
import asyncio
from datetime import datetime
from typing import Dict, Any
from loguru import logger
from module_redfish.celery_tasks import monitor_all_devices, cleanup_old_logs
from module_redfish.core.websocket_manager import websocket_manager


def redfish_device_monitor_job(*args, **kwargs):
    """
    设备监控定时任务执行函数 - 同步版本
    该函数会被APScheduler调用，任务配置由sys_job表管理
    执行统一的设备监控任务，包括硬件状态和连通性检测
    
    Args:
        *args: 位置参数（来自sys_job.job_args）
        **kwargs: 关键字参数（来自sys_job.job_kwargs）
    """
    try:
        logger.info("开始执行设备监控定时任务")
        logger.info(f"接收到的参数 - args: {args}, kwargs: {kwargs}")
        
        # 记录任务执行时间
        execution_time = datetime.now()
        
        # 提交统一监控Celery异步任务（包含硬件状态和连通性检测）
        monitor_result = monitor_all_devices.delay()
        
        logger.info(f"设备监控Celery任务已提交，任务ID: {monitor_result.id}")
        
        # 创建异步任务进行WebSocket广播
        try:
            # 检查是否有运行的事件循环
            loop = asyncio.get_running_loop()
            # 在已有循环中创建任务
            loop.create_task(_broadcast_monitor_start(execution_time, monitor_result.id))
        except RuntimeError:
            # 如果没有运行的事件循环，在线程中运行
            import threading
            def run_broadcast():
                asyncio.run(_broadcast_monitor_start(execution_time, monitor_result.id))
            threading.Thread(target=run_broadcast, daemon=True).start()
        
        # 返回执行结果
        return {
            "success": True,
            "monitor_task_id": monitor_result.id,
            "execution_time": execution_time.isoformat(),
            "message": "设备监控任务执行成功（硬件状态+连通性检测）"
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


def device_downtime_monitor_job(*args, **kwargs):
    """
    设备宕机检测定时任务执行函数
    基于业务IP连通性检测设备是否宕机
    
    Args:
        *args: 位置参数（来自sys_job.job_args）
        **kwargs: 关键字参数（来自sys_job.job_kwargs）
    """
    try:
        logger.info("开始执行设备宕机检测定时任务")
        logger.info(f"接收到的参数 - args: {args}, kwargs: {kwargs}")
        
        # 记录任务执行时间
        execution_time = datetime.now()
        
        # 提交Celery异步任务
        result = check_all_devices_availability.delay()
        
        logger.info(f"设备宕机检测Celery任务已提交，任务ID: {result.id}")
        
        # 注意: 已删除独立的宕机检测任务，现在统一在monitor_all_devices中处理
        
        # 返回执行结果
        return {
            "success": True,
            "task_id": result.id,
            "execution_time": execution_time.isoformat(),
            "message": "设备宕机检测任务执行成功"
        }
        
    except Exception as e:
        error_msg = f"执行设备宕机检测任务失败: {str(e)}"
        logger.error(error_msg)
        
        # 错误处理: 已简化为统一监控任务
        
        # 重新抛出异常，让APScheduler记录
        raise e


def cleanup_old_logs_job(*args, **kwargs):
    """
    清理旧日志和告警定时任务执行函数
    
    Args:
        *args: 位置参数，第一个参数为保留天数，默认30天
        **kwargs: 关键字参数
    """
    try:
        # 获取保留天数参数
        days = int(args[0]) if args and args[0] else 30
        
        logger.info(f"开始执行清理旧日志任务，保留{days}天内的记录")
        logger.info(f"接收到的参数 - args: {args}, kwargs: {kwargs}")
        
        # 记录任务执行时间
        execution_time = datetime.now()
        
        # 提交Celery异步任务
        result = cleanup_old_logs.delay(days)
        
        logger.info(f"清理旧日志Celery任务已提交，任务ID: {result.id}")
        
        # 返回执行结果
        return {
            "success": True,
            "task_id": result.id,
            "execution_time": execution_time.isoformat(),
            "days": days,
            "message": f"清理旧日志任务执行成功，保留{days}天内记录"
        }
        
    except Exception as e:
        error_msg = f"执行清理旧日志任务失败: {str(e)}"
        logger.error(error_msg)
        
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


# 已删除 _broadcast_downtime_check_start 函数


# 已删除 _broadcast_downtime_check_error 函数





# ================================================================================
# 定时任务配置说明
# ================================================================================
# 本项目使用 APScheduler + 数据库 的方式管理定时任务：
# 1. 任务配置存储在 sys_job 表中
# 2. 应用启动时从数据库读取并注册任务
# 3. 通过 /monitor/job 页面管理任务（启停、修改cron表达式等）
# 4. 任务执行日志记录在 sys_job_log 表中
#
# 执行 add_downtime_monitor_jobs.sql 可以添加以下任务到数据库：
# - 设备全面监控任务：每5分钟执行（包含硬件健康+宕机检测）
# - 设备宕机检测任务：每2分钟执行（独立的宕机检测）
# - 清理旧日志和告警：每天凌晨2点执行
# ================================================================================


# ================================================================================
# APScheduler 定时任务使用说明
# ================================================================================
"""
1. 数据库管理：所有定时任务配置存储在 sys_job 表中
2. 自动加载：系统启动时自动从数据库读取并注册任务
3. Web管理：访问 /monitor/job 可视化管理所有任务
4. 动态配置：支持在线修改cron表达式、启停任务、手动触发
5. 日志记录：任务执行日志自动记录到 sys_job_log 表

快速部署：
1. 执行 cleanup_hardware_dict.sql（添加downtime硬件类型）
2. 执行 add_downtime_monitor_jobs.sql（添加定时任务）
3. 执行 init_redfish_log_management.sql（添加日志管理）
4. 重启应用（自动加载任务）
5. 访问 /monitor/job 查看任务状态
"""


# ================================================================================
# Redfish 日志清理任务
# ================================================================================

def redfish_log_cleanup_job(*args, **kwargs):
    """
    Redfish日志清理定时任务执行函数
    该函数会被APScheduler调用，任务配置由sys_job表管理
    每天凌晨2点执行，清理30天前的日志记录
    
    Args:
        *args: 位置参数（来自sys_job.job_args）
        **kwargs: 关键字参数（来自sys_job.job_kwargs）
    """
    try:
        logger.info("开始执行Redfish日志清理定时任务")
        logger.info(f"接收到的参数 - args: {args}, kwargs: {kwargs}")
        
        # 记录任务执行时间
        execution_time = datetime.now()
        
        # 执行异步清理任务
        result = asyncio.run(_async_cleanup_redfish_logs())
        
        # 计算执行时间
        duration = (datetime.now() - execution_time).total_seconds()
        
        if result['success']:
            logger.info(f"Redfish日志清理任务执行成功: {result['message']}, 耗时: {duration:.2f}秒")
        else:
            logger.error(f"Redfish日志清理任务执行失败: {result['message']}")
            
        return result
        
    except Exception as e:
        error_msg = f"Redfish日志清理任务执行异常: {str(e)}"
        logger.error(error_msg)
        return {
            'success': False,
            'message': error_msg,
            'cleaned_count': 0
        }


async def _async_cleanup_redfish_logs():
    """
    异步执行日志清理
    
    Returns:
        Dict: 清理结果
    """
    try:
        # 导入必要的模块
        from config.get_db import get_db_for_task
        from module_redfish.service.redfish_log_service import RedfishLogService
        
        # 获取数据库会话
        async for db in get_db_for_task():
            try:
                # 清理30天前的日志
                cleanup_result = await RedfishLogService.cleanup_old_logs_services(db, days=30)
                
                return {
                    'success': cleanup_result.success,
                    'message': cleanup_result.message,
                    'cleaned_count': cleanup_result.cleaned_count
                }
                
            except Exception as e:
                logger.error(f"日志清理异常: {str(e)}")
                await db.rollback()
                return {
                    'success': False,
                    'message': f'日志清理异常: {str(e)}',
                    'cleaned_count': 0
                }
            finally:
                await db.close()
                break
                
    except Exception as e:
        logger.error(f"日志清理启动失败: {str(e)}")
        return {
            'success': False,
            'message': f'日志清理启动失败: {str(e)}',
            'cleaned_count': 0
        } 