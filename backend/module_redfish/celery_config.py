"""
Celery配置文件
用于启动Celery worker和beat调度器
"""
import os
from celery import Celery
from kombu import Queue

# 从环境变量获取Redis配置
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_DB_BROKER = os.getenv('REDIS_DB_BROKER', '1')
REDIS_DB_BACKEND = os.getenv('REDIS_DB_BACKEND', '2')

# 构建Redis URL
BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_BROKER}'
RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_BACKEND}'

# Celery应用配置
def make_celery():
    """创建Celery应用实例"""
    celery = Celery(
        'redfish_monitor',
        broker=BROKER_URL,
        backend=RESULT_BACKEND,
        include=['module_redfish.celery_tasks']
    )
    
    # 更新配置
    celery.conf.update(
        # 序列化配置
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        
        # 时区配置
        timezone='Asia/Shanghai',
        enable_utc=True,
        
        # 任务配置
        task_track_started=True,
        task_time_limit=300,  # 5分钟硬超时
        task_soft_time_limit=240,  # 4分钟软超时
        task_acks_late=True,  # 任务完成后才确认
        task_reject_on_worker_lost=True,  # worker丢失时拒绝任务
        
        # Worker配置
        worker_prefetch_multiplier=1,  # 每次只预取1个任务，防止任务堆积
        worker_max_tasks_per_child=1000,  # 防止内存泄漏
        worker_disable_rate_limits=False,
        
        # 结果配置
        result_expires=3600,  # 结果保存1小时
        result_persistent=True,  # 持久化结果
        
        # 路由配置
        task_routes={
            'monitor_single_device': {'queue': 'monitoring'},
            'monitor_all_devices': {'queue': 'batch'},
            'cleanup_old_logs': {'queue': 'maintenance'},
        },
        
        # 队列配置
        task_default_queue='default',
        task_queues=(
            Queue('default', routing_key='default'),
            Queue('monitoring', routing_key='monitoring'),
            Queue('batch', routing_key='batch'),
            Queue('maintenance', routing_key='maintenance'),
        ),
        
        # Beat调度配置
        beat_schedule={
            # 每5分钟执行一次全设备监控
            'monitor-all-devices': {
                'task': 'monitor_all_devices',
                'schedule': 300.0,  # 5分钟
                'options': {'queue': 'batch'}
            },
            # 每2小时清理一次旧日志
            'cleanup-old-logs': {
                'task': 'cleanup_old_logs',
                'schedule': 7200.0,  # 2小时
                'kwargs': {'days': 30},
                'options': {'queue': 'maintenance'}
            },
        },
        beat_schedule_filename='celerybeat-schedule',
        
        # 监控配置
        worker_send_task_events=True,
        task_send_sent_event=True,
        
        # 错误处理
        task_annotations={
            '*': {
                'rate_limit': '100/m',  # 每分钟最多100个任务
                'time_limit': 300,
                'soft_time_limit': 240,
            },
            'monitor_single_device': {
                'rate_limit': '50/m',  # 单设备监控限制
                'retry_policy': {
                    'max_retries': 3,
                    'interval_start': 60,
                    'interval_step': 60,
                    'interval_max': 300,
                }
            },
            'monitor_all_devices': {
                'rate_limit': '1/m',  # 批量监控限制
                'retry_policy': {
                    'max_retries': 2,
                    'interval_start': 300,
                    'interval_step': 300,
                    'interval_max': 600,
                }
            }
        }
    )
    
    return celery


# 创建Celery实例
celery_app = make_celery()


if __name__ == '__main__':
    """
    启动Celery worker
    使用方法：
    python -m module_redfish.celery_config worker --loglevel=info
    """
    celery_app.start() 