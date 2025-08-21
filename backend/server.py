from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from config.env import AppConfig
from config.get_db import init_create_table
from config.get_redis import RedisUtil
from config.get_scheduler import SchedulerUtil
from exceptions.handle import handle_exception
from middlewares.handle import handle_middleware
from module_admin.controller.cache_controller import cacheController
from module_admin.controller.captcha_controller import captchaController
from module_admin.controller.common_controller import commonController
from module_admin.controller.config_controller import configController
from module_admin.controller.dept_controller import deptController
from module_admin.controller.dict_controller import dictController
from module_admin.controller.log_controller import logController
from module_admin.controller.login_controller import loginController
from module_admin.controller.job_controller import jobController
from module_admin.controller.menu_controller import menuController
from module_admin.controller.notice_controller import noticeController
from module_admin.controller.online_controller import onlineController
from module_admin.controller.post_controler import postController
from module_admin.controller.role_controller import roleController
from module_admin.controller.server_controller import serverController
from module_admin.controller.user_controller import userController
from module_generator.controller.gen_controller import genController
from module_redfish.controller.device_controller import deviceController
from module_redfish.controller.alert_controller import alertController
from module_redfish.controller.business_rule_controller import businessRuleController
from module_redfish.controller.dashboard_controller import dashboardController
from module_redfish.controller.redfish_log_controller import redfishLogController 

from module_redfish.controller.connectivity_controller import connectivityController
from module_redfish.controller.websocket_controller import WebSocketController
from module_redfish.controller.monitor_config_controller import app3_monitor_config
from module_redfish.core.websocket_manager import init_websocket_manager, cleanup_websocket_manager
# RedfishSchedulerTasks已迁移到APScheduler，由数据库管理
from sub_applications.handle import handle_sub_applications
from utils.common_util import worship
from utils.log_util import logger


# 生命周期事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f'{AppConfig.app_name}开始启动')
    worship()
    await init_create_table()
    app.state.redis = await RedisUtil.create_redis_pool()
    await RedisUtil.init_sys_dict(app.state.redis)
    await RedisUtil.init_sys_config(app.state.redis)
    await SchedulerUtil.init_system_scheduler()
    
    # 初始化WebSocket管理器
    await init_websocket_manager()
    
    # Redfish监控任务和日志清理任务现在由APScheduler管理，从数据库sys_job表自动加载
    logger.info("Redfish相关定时任务由APScheduler从数据库加载，无需手动初始化")
    
    logger.info(f'{AppConfig.app_name}启动成功')
    yield
    await RedisUtil.close_redis_pool(app)
    await SchedulerUtil.close_system_scheduler()
    
    # 清理WebSocket管理器
    await cleanup_websocket_manager()


# 初始化FastAPI对象
app = FastAPI(
    title=AppConfig.app_name,
    description=f'{AppConfig.app_name}接口文档',
    version=AppConfig.app_version,
    lifespan=lifespan,
)

# 挂载子应用
handle_sub_applications(app)
# 加载中间件处理方法
handle_middleware(app)
# 加载全局异常处理方法
handle_exception(app)


# 加载路由列表
controller_list = [
    {'router': loginController, 'tags': ['登录模块']},
    {'router': captchaController, 'tags': ['验证码模块']},
    {'router': userController, 'tags': ['系统管理-用户管理']},
    {'router': roleController, 'tags': ['系统管理-角色管理']},
    {'router': menuController, 'tags': ['系统管理-菜单管理']},
    {'router': deptController, 'tags': ['系统管理-部门管理']},
    {'router': postController, 'tags': ['系统管理-岗位管理']},
    {'router': dictController, 'tags': ['系统管理-字典管理']},
    {'router': configController, 'tags': ['系统管理-参数管理']},
    {'router': noticeController, 'tags': ['系统管理-通知公告管理']},
    {'router': logController, 'tags': ['系统管理-日志管理']},
    {'router': onlineController, 'tags': ['系统监控-在线用户']},
    {'router': jobController, 'tags': ['系统监控-定时任务']},
    {'router': serverController, 'tags': ['系统监控-菜单管理']},
    {'router': cacheController, 'tags': ['系统监控-缓存监控']},
    {'router': commonController, 'tags': ['通用模块']},
    {'router': genController, 'tags': ['代码生成']},
    {'router': deviceController, 'tags': ['Redfish-设备管理']},
    {'router': alertController, 'tags': ['Redfish-告警管理']},
    {'router': businessRuleController, 'tags': ['Redfish-规则管理']},
    {'router': dashboardController, 'tags': ['Redfish-首页数据']},
    {'router': redfishLogController, 'tags': ['Redfish-日志管理']},

    {'router': connectivityController, 'tags': ['Redfish-连通性检测']},
    {'router': app3_monitor_config, 'tags': ['Redfish-监控配置']},
]

for controller in controller_list:
    app.include_router(router=controller.get('router'), tags=controller.get('tags'))


# WebSocket路由
@app.websocket("/ws/redfish")
async def websocket_redfish_endpoint(websocket: WebSocket):
    """Redfish实时监控WebSocket端点"""
    await WebSocketController.handle_websocket_connection(websocket)


@app.websocket("/ws/redfish/{user_id}")
async def websocket_redfish_user_endpoint(websocket: WebSocket, user_id: str):
    """Redfish实时监控WebSocket端点（带用户ID）"""
    await WebSocketController.handle_websocket_connection(websocket, user_id)
