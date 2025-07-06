"""
设备日志跟踪控制器
提供设备日志跟踪状态的查看和管理功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from loguru import logger

from config.get_db import get_sync_db
from module_redfish.service.device_log_tracking_service import DeviceLogTrackingService
from module_redfish.entity.vo.device_log_check_tracking_vo import (
    DeviceLogCheckTrackingVO,
    DeviceLogTrackingDetailVO,
    DeviceLogCheckTrackingStatisticsVO,
    DeviceLogTrackingListVO,
    DeviceLogTrackingCreateVO
)
from module_system.service.sys_response import SysResponse

router = APIRouter(prefix="/api/redfish/log-tracking", tags=["设备日志跟踪管理"])


@router.get("/statistics", response_model=SysResponse[DeviceLogCheckTrackingStatisticsVO])
async def get_tracking_statistics(db: Session = Depends(get_sync_db)):
    """
    获取设备日志跟踪统计信息
    """
    try:
        statistics = DeviceLogTrackingService.get_tracking_statistics(db)
        return SysResponse.success(statistics)
    except Exception as e:
        logger.error(f"获取日志跟踪统计信息失败: {str(e)}")
        return SysResponse.error(f"获取统计信息失败: {str(e)}")


@router.get("/list", response_model=SysResponse[List[DeviceLogTrackingDetailVO]])
async def get_tracking_list(
    device_id: Optional[int] = Query(None, description="设备ID过滤"),
    db: Session = Depends(get_sync_db)
):
    """
    获取设备日志跟踪详情列表
    """
    try:
        tracking_details = DeviceLogTrackingService.get_tracking_details_with_device_info(
            db, device_id
        )
        return SysResponse.success(tracking_details)
    except Exception as e:
        logger.error(f"获取日志跟踪列表失败: {str(e)}")
        return SysResponse.error(f"获取跟踪列表失败: {str(e)}")


@router.post("/initialize", response_model=SysResponse[bool])
async def initialize_device_tracking(
    request: DeviceLogTrackingCreateVO,
    db: Session = Depends(get_sync_db)
):
    """
    为指定设备初始化日志跟踪记录
    """
    try:
        result = DeviceLogTrackingService.initialize_device_tracking(
            db, request.device_id, request.log_types
        )
        
        if result:
            db.commit()
            return SysResponse.success(True, "设备日志跟踪初始化成功")
        else:
            db.rollback()
            return SysResponse.error("设备日志跟踪初始化失败")
            
    except Exception as e:
        logger.error(f"初始化设备日志跟踪失败: {str(e)}")
        db.rollback()
        return SysResponse.error(f"初始化失败: {str(e)}")


@router.get("/device/{device_id}/{log_type}", response_model=SysResponse[Optional[DeviceLogCheckTrackingVO]])
async def get_device_tracking_info(
    device_id: int,
    log_type: str,
    db: Session = Depends(get_sync_db)
):
    """
    获取指定设备和日志类型的跟踪信息
    """
    try:
        tracking_info = DeviceLogTrackingService.get_tracking_info(db, device_id, log_type)
        
        if tracking_info:
            # 转换为VO对象
            tracking_vo = DeviceLogCheckTrackingVO(
                device_id=device_id,
                log_type=log_type,
                last_check_time=tracking_info.get('last_check_time'),
                last_entry_id=tracking_info.get('last_entry_id'),
                last_entry_timestamp=tracking_info.get('last_entry_timestamp')
            )
            return SysResponse.success(tracking_vo)
        else:
            return SysResponse.success(None, "未找到跟踪记录")
            
    except Exception as e:
        logger.error(f"获取设备跟踪信息失败: device_id={device_id}, log_type={log_type}, error={str(e)}")
        return SysResponse.error(f"获取跟踪信息失败: {str(e)}")


@router.delete("/device/{device_id}/{log_type}", response_model=SysResponse[bool])
async def delete_device_tracking(
    device_id: int,
    log_type: str,
    db: Session = Depends(get_sync_db)
):
    """
    删除指定设备和日志类型的跟踪记录
    """
    try:
        from module_redfish.dao.device_log_check_tracking_dao import DeviceLogCheckTrackingDao
        
        result = DeviceLogCheckTrackingDao.delete_tracking_record(db, device_id, log_type)
        
        if result:
            db.commit()
            return SysResponse.success(True, "跟踪记录删除成功")
        else:
            return SysResponse.error("跟踪记录不存在或删除失败")
            
    except Exception as e:
        logger.error(f"删除设备跟踪记录失败: device_id={device_id}, log_type={log_type}, error={str(e)}")
        db.rollback()
        return SysResponse.error(f"删除跟踪记录失败: {str(e)}")


@router.post("/cleanup", response_model=SysResponse[int])
async def cleanup_old_tracking_records(
    days_to_keep: int = Query(30, description="保留天数", ge=1, le=365),
    db: Session = Depends(get_sync_db)
):
    """
    清理旧的跟踪记录
    """
    try:
        deleted_count = DeviceLogTrackingService.cleanup_old_tracking_records(db, days_to_keep)
        
        if deleted_count >= 0:
            db.commit()
            return SysResponse.success(deleted_count, f"成功清理了 {deleted_count} 条旧跟踪记录")
        else:
            db.rollback()
            return SysResponse.error("清理操作失败")
            
    except Exception as e:
        logger.error(f"清理旧跟踪记录失败: error={str(e)}")
        db.rollback()
        return SysResponse.error(f"清理失败: {str(e)}")


@router.get("/health", response_model=SysResponse[dict])
async def get_tracking_health(db: Session = Depends(get_sync_db)):
    """
    获取日志跟踪系统健康状态
    """
    try:
        from datetime import datetime, timedelta
        from module_redfish.dao.device_log_check_tracking_dao import DeviceLogCheckTrackingDao
        
        # 获取统计信息
        stats = DeviceLogCheckTrackingDao.get_tracking_statistics(db)
        
        # 计算健康指标
        total_devices = db.execute("SELECT COUNT(*) FROM device_info WHERE monitor_enabled = 1").scalar()
        expected_tracking_records = total_devices * 2  # SEL + MEL
        
        # 检查延迟设备数量（超过24小时未检查）
        threshold_time = datetime.now() - timedelta(hours=24)
        delayed_count = db.execute(
            "SELECT COUNT(DISTINCT device_id) FROM device_log_check_tracking WHERE last_check_time < %s",
            (threshold_time,)
        ).scalar()
        
        health_info = {
            "total_devices": total_devices,
            "tracked_devices": stats["total_tracking_records"] // 2 if stats["total_tracking_records"] > 0 else 0,
            "expected_tracking_records": expected_tracking_records,
            "actual_tracking_records": stats["total_tracking_records"],
            "coverage_percentage": stats["check_coverage"],
            "delayed_devices": delayed_count,
            "log_type_distribution": stats["log_type_distribution"],
            "health_status": "healthy" if stats["check_coverage"] > 80 and delayed_count < total_devices * 0.1 else "warning"
        }
        
        return SysResponse.success(health_info)
        
    except Exception as e:
        logger.error(f"获取跟踪系统健康状态失败: error={str(e)}")
        return SysResponse.error(f"获取健康状态失败: {str(e)}")


@router.post("/batch-initialize", response_model=SysResponse[dict])
async def batch_initialize_tracking(
    force: bool = Query(False, description="是否强制重新初始化"),
    db: Session = Depends(get_sync_db)
):
    """
    批量初始化所有启用监控设备的日志跟踪记录
    """
    try:
        from module_redfish.models import DeviceInfo
        
        # 获取所有启用监控的设备
        devices = db.query(DeviceInfo).filter(DeviceInfo.monitor_enabled == 1).all()
        
        success_count = 0
        error_count = 0
        skipped_count = 0
        
        for device in devices:
            try:
                # 检查是否已存在跟踪记录
                existing_tracking = DeviceLogTrackingService.get_tracking_info(db, device.device_id, 'sel')
                
                if existing_tracking and not force:
                    skipped_count += 1
                    continue
                
                # 初始化跟踪记录
                result = DeviceLogTrackingService.initialize_device_tracking(
                    db, device.device_id, ['sel', 'mel']
                )
                
                if result:
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                logger.error(f"初始化设备 {device.device_id} 跟踪记录失败: {str(e)}")
                error_count += 1
        
        db.commit()
        
        result = {
            "total_devices": len(devices),
            "success_count": success_count,
            "error_count": error_count,
            "skipped_count": skipped_count,
            "message": f"批量初始化完成：成功 {success_count}，失败 {error_count}，跳过 {skipped_count}"
        }
        
        return SysResponse.success(result)
        
    except Exception as e:
        logger.error(f"批量初始化跟踪记录失败: error={str(e)}")
        db.rollback()
        return SysResponse.error(f"批量初始化失败: {str(e)}") 