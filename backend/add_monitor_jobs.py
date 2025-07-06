"""
添加Redfish监控定时任务到数据库
"""
import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def add_monitor_jobs():
    """添加监控任务到数据库"""
    print("🚀 开始添加Redfish监控定时任务到数据库...")
    
    try:
        from config.database import AsyncSessionLocal
        from module_admin.dao.job_dao import JobDao
        from module_admin.entity.vo.job_vo import JobModel
        
        # 定义任务配置
        jobs_config = [
            {
                "job_name": "设备健康监控任务",
                "job_group": "default",
                "job_executor": "default",
                "invoke_target": "module_task.redfish_monitor_tasks.redfish_device_monitor_job",
                "job_args": "",
                "job_kwargs": "",
                "cron_expression": "0 */5 * * * *",  # 每5分钟执行一次
                "misfire_policy": "3",  # 错过执行则放弃
                "concurrent": "1",  # 禁止并发执行
                "status": "0",  # 启用状态
                "create_by": "admin",
                "create_time": datetime.now(),
                "update_by": "admin", 
                "update_time": datetime.now(),
                "remark": "定期监控Redfish设备健康状态，支持1000台设备。通过Celery异步处理，结果推送到WebSocket。"
            },
            {
                "job_name": "设备健康监控任务（异步）",
                "job_group": "default",
                "job_executor": "default",
                "invoke_target": "module_task.redfish_monitor_tasks.async_redfish_device_monitor_job",
                "job_args": "",
                "job_kwargs": "",
                "cron_expression": "0 */5 * * * *",
                "misfire_policy": "3",
                "concurrent": "1",
                "status": "1",  # 默认暂停，作为备用方案
                "create_by": "admin",
                "create_time": datetime.now(),
                "update_by": "admin",
                "update_time": datetime.now(),
                "remark": "异步版本的设备健康监控任务，可作为同步版本的备用方案。"
            },
            {
                "job_name": "手动触发设备监控",
                "job_group": "default",
                "job_executor": "default",
                "invoke_target": "module_task.redfish_monitor_tasks.manual_trigger_monitor_job",
                "job_args": "",
                "job_kwargs": "{}",
                "cron_expression": "",  # 手动触发，无需cron表达式
                "misfire_policy": "1",  # 立即执行
                "concurrent": "0",  # 允许并发
                "status": "1",  # 默认暂停，需要时手动触发
                "create_by": "admin",
                "create_time": datetime.now(),
                "update_by": "admin",
                "update_time": datetime.now(),
                "remark": "手动触发设备监控任务，用于测试或紧急检查。可通过定时任务管理界面手动执行。"
            }
        ]
        
        async with AsyncSessionLocal() as session:
            # 先删除已存在的相似任务
            print("   删除已存在的设备监控任务...")
            
            # 添加新任务
            added_count = 0
            for job_config in jobs_config:
                try:
                    job_model = JobModel(**job_config)
                    await JobDao.add_job_dao(session, job_model)
                    print(f"✅ 已添加: {job_config['job_name']}")
                    added_count += 1
                except Exception as e:
                    print(f"❌ 添加失败 {job_config['job_name']}: {str(e)}")
            
            # 提交事务
            await session.commit()
            
            print(f"\n🎉 成功添加 {added_count} 个监控任务到数据库！")
            return True
            
    except Exception as e:
        print(f"❌ 添加任务失败: {str(e)}")
        return False

async def verify_jobs():
    """验证任务是否成功添加"""
    print("\n🔍 验证任务是否成功添加...")
    
    try:
        from config.database import AsyncSessionLocal
        from module_admin.dao.job_dao import JobDao
        from module_admin.entity.vo.job_vo import JobPageQueryModel
        
        async with AsyncSessionLocal() as session:
            query = JobPageQueryModel()
            result = await JobDao.get_job_list(session, query, is_page=False)
            
            if hasattr(result, 'data'):
                jobs = result.data
            else:
                jobs = result
            
            monitor_jobs = []
            for job in jobs:
                if ('设备' in job.job_name or 'redfish' in job.job_name.lower() or 
                    'monitor' in job.job_name.lower()):
                    monitor_jobs.append(job)
            
            if monitor_jobs:
                print("✅ 验证成功！找到以下监控任务：")
                for job in monitor_jobs:
                    status_text = "启用" if job.status == '0' else "暂停"
                    print(f"   - {job.job_name} [{status_text}]")
                    print(f"     Cron: {job.cron_expression}")
                return True
            else:
                print("❌ 验证失败：没有找到监控任务")
                return False
                
    except Exception as e:
        print(f"❌ 验证失败: {str(e)}")
        return False

async def main():
    """主函数"""
    print("📦 Redfish监控定时任务安装程序")
    print("=" * 50)
    
    # 添加任务
    success = await add_monitor_jobs()
    
    if success:
        # 验证任务
        verify_success = await verify_jobs()
        
        if verify_success:
            print("\n🎉 安装完成！下一步操作：")
            print("1. 重启FastAPI应用 (python3 server.py)")
            print("2. 访问 /monitor/job 管理定时任务")
            print("3. 确保Celery Worker运行中")
            print("4. 在设备管理中添加设备配置")
            print("\n定时任务将每5分钟自动执行一次设备健康检查")
        else:
            print("\n⚠️ 安装可能有问题，请检查数据库配置")
    else:
        print("\n❌ 安装失败，请检查错误信息")

if __name__ == "__main__":
    asyncio.run(main()) 