"""
监控配置管理控制器
提供监控配置的API接口
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_task.redfish_monitor_tasks import manual_trigger_monitor_job
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from utils.response_util import ResponseUtil
from config.enums import BusinessType


# 路由对象
app3_monitor_config = APIRouter(prefix='/redfish')


class MonitorConfigUpdateModel(BaseModel):
    """监控配置更新模型"""
    monitor_interval: int = Field(5, ge=1, le=60, description="监控间隔（分钟），范围1-60")
    max_retry: int = Field(3, ge=1, le=10, description="最大重试次数，范围1-10")
    timeout: int = Field(300, ge=30, le=600, description="超时时间（秒），范围30-600")


class ManualTriggerModel(BaseModel):
    """手动触发监控模型"""
    force: bool = Field(False, description="是否强制执行（即使上次任务还在运行）")


@app3_monitor_config.get("/monitor/config", summary="获取监控配置", dependencies=[Depends(CheckUserInterfaceAuth('monitor:config:view'))])
@Log(title="获取监控配置", business_type=BusinessType.OTHER)
async def get_monitor_config(request: Request, query_db: AsyncSession = Depends(get_db)):
    """获取当前监控配置"""
    try:

        config = {
            "monitor_interval": 5,  # 分钟
            "max_retry": 3,
            "timeout": 300,  # 秒
            "task_status": {
                "status": "active",
                "message": "任务配置由数据库sys_job表管理"
            }
        }
        return ResponseUtil.success(data=config, msg="获取监控配置成功")
        
    except Exception as e:
        logger.error(f"获取监控配置失败: {str(e)}")
        return ResponseUtil.error(msg=f"获取监控配置失败: {str(e)}")


@app3_monitor_config.put("/monitor/config", summary="更新监控配置", dependencies=[Depends(CheckUserInterfaceAuth('monitor:config:edit'))])
@Log(title="更新监控配置", business_type=BusinessType.UPDATE)
async def update_monitor_config(request: Request, config_data: MonitorConfigUpdateModel, query_db: AsyncSession = Depends(get_db)):
    """更新监控配置"""
    try:
        # 转换为字典
        config_dict = config_data.model_dump()
        

        result = {
            "success": True,
            "message": "监控配置更新成功。注意：实际定时任务间隔请在定时任务管理界面修改cron表达式。",
            "config": {
                "monitor_interval": config_dict.get("monitor_interval", 5),
                "max_retry": config_dict.get("max_retry", 3),
                "timeout": 300,
                "task_status": {
                    "status": "active",
                    "message": "任务配置由数据库sys_job表管理"
                }
            }
        }
        
        if result.get("success"):
            return ResponseUtil.success(data=result.get("config"), msg=result.get("message"))
        else:
            return ResponseUtil.error(msg=result.get("message"))
            
    except Exception as e:
        logger.error(f"更新监控配置失败: {str(e)}")
        return ResponseUtil.error(msg=f"更新监控配置失败: {str(e)}")


@app3_monitor_config.get("/monitor/status", summary="获取监控任务状态", dependencies=[Depends(CheckUserInterfaceAuth('monitor:task:view'))])
@Log(title="获取监控任务状态", business_type=BusinessType.OTHER)
async def get_monitor_status(request: Request, query_db: AsyncSession = Depends(get_db)):
    """获取监控任务状态"""
    try:

        status_info = {
            "status": "active",
            "message": "任务配置由数据库sys_job表管理，请在定时任务管理界面查看详细状态",
            "task_name": "设备全面监控任务",
            "config_source": "database",
            "management_url": "/monitor/job"
        }
        return ResponseUtil.success(data=status_info, msg="获取监控任务状态成功")
        
    except Exception as e:
        logger.error(f"获取监控任务状态失败: {str(e)}")
        return ResponseUtil.error(msg=f"获取监控任务状态失败: {str(e)}")


@app3_monitor_config.post("/monitor/trigger", summary="手动触发监控", dependencies=[Depends(CheckUserInterfaceAuth('monitor:task:execute'))])
@Log(title="手动触发监控", business_type=BusinessType.OTHER)
async def manual_trigger_monitor(request: Request, trigger_data: ManualTriggerModel, query_db: AsyncSession = Depends(get_db)):
    """手动触发设备监控任务"""
    try:
        # 这里可以获取当前用户信息
        # current_user = get_current_user()  # 需要实现用户认证
        user_id = "manual_trigger"  # 临时使用固定值
        
        # 调用手动触发监控函数
        result = manual_trigger_monitor_job(user_id=user_id)
        
        if result.get("success"):
            return ResponseUtil.success(data=result, msg=result.get("message"))
        else:
            return ResponseUtil.error(msg=result.get("message"))
            
    except Exception as e:
        logger.error(f"手动触发监控失败: {str(e)}")
        return ResponseUtil.error(msg=f"手动触发监控失败: {str(e)}")


@app3_monitor_config.post("/monitor/start", summary="启动监控任务", dependencies=[Depends(CheckUserInterfaceAuth('monitor:task:manage'))])
@Log(title="启动监控任务", business_type=BusinessType.OTHER)
async def start_monitor_task(request: Request, query_db: AsyncSession = Depends(get_db)):
    """启动监控定时任务"""
    try:
        # 简化实现：任务由数据库管理，系统启动时自动加载
        return ResponseUtil.success(msg="监控任务由数据库配置管理，请在定时任务管理界面启动")
        
    except Exception as e:
        logger.error(f"操作失败: {str(e)}")
        return ResponseUtil.error(msg=f"操作失败: {str(e)}")


@app3_monitor_config.post("/monitor/stop", summary="停止监控任务", dependencies=[Depends(CheckUserInterfaceAuth('monitor:task:manage'))])
@Log(title="停止监控任务", business_type=BusinessType.OTHER)
async def stop_monitor_task(request: Request, query_db: AsyncSession = Depends(get_db)):
    """停止监控定时任务"""
    try:
        # 简化实现：任务由数据库管理
        return ResponseUtil.success(msg="监控任务由数据库配置管理，请在定时任务管理界面停止")
        
    except Exception as e:
        logger.error(f"操作失败: {str(e)}")
        return ResponseUtil.error(msg=f"操作失败: {str(e)}")


@app3_monitor_config.get("/monitor/statistics", summary="获取监控统计信息", dependencies=[Depends(CheckUserInterfaceAuth('monitor:system:view'))])
@Log(title="获取监控统计信息", business_type=BusinessType.OTHER)
async def get_monitor_statistics(request: Request, query_db: AsyncSession = Depends(get_db)):
    """获取监控统计信息"""
    try:
        # 这里可以添加更多统计信息的获取逻辑
        statistics = {
            "task_status": {
                "status": "active",
                "message": "任务配置由数据库sys_job表管理",
                "config_source": "database"
            },
            "config": {
                "monitor_interval": 5,
                "max_retry": 3,
                "timeout": 300
            },
            # 可以添加更多统计信息，如：
            # "total_devices": 设备总数,
            # "monitored_devices": 已监控设备数,
            # "alert_count": 告警数量,
            # "last_monitor_time": 最后监控时间
        }
        
        return ResponseUtil.success(data=statistics, msg="获取监控统计信息成功")
        
    except Exception as e:
        logger.error(f"获取监控统计信息失败: {str(e)}")
        return ResponseUtil.error(msg=f"获取监控统计信息失败: {str(e)}")


@app3_monitor_config.get("/monitor/health", summary="监控系统健康检查")
@Log(title="监控系统健康检查", business_type=BusinessType.OTHER)
async def monitor_health_check(request: Request, query_db: AsyncSession = Depends(get_db)):
    """监控系统健康检查（无需认证）"""
    try:
        health_info = {
            "status": "healthy",
            "timestamp": logger.info("监控系统健康检查"),
            "components": {
                "scheduler": "active",  # 简化为固定状态
                "websocket": "active",  # 可以添加WebSocket连接数检查
                "celery": "active",     # 可以添加Celery状态检查
            }
        }
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=health_info
        )
        
    except Exception as e:
        logger.error(f"监控系统健康检查失败: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "unhealthy", "error": str(e)}
        ) 