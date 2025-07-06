import request from '@/utils/request'

// 获取监控配置
export function getMonitorConfig() {
  return request({
    url: '/redfish/monitor/config',
    method: 'get'
  })
}

// 更新监控配置
export function updateMonitorConfig(data) {
  return request({
    url: '/redfish/monitor/config',
    method: 'put',
    data: data
  })
}

// 获取监控任务状态
export function getMonitorStatus() {
  return request({
    url: '/redfish/monitor/status',
    method: 'get'
  })
}

// 手动触发监控
export function triggerMonitor(force = false) {
  return request({
    url: '/redfish/monitor/trigger',
    method: 'post',
    data: {
      force: force
    }
  })
}

// 启动监控任务
export function startMonitorTask() {
  return request({
    url: '/redfish/monitor/start',
    method: 'post'
  })
}

// 停止监控任务
export function stopMonitorTask() {
  return request({
    url: '/redfish/monitor/stop',
    method: 'post'
  })
}

// 获取监控统计信息
export function getMonitorStatistics() {
  return request({
    url: '/redfish/monitor/statistics',
    method: 'get'
  })
}

// 监控系统健康检查
export function monitorHealthCheck() {
  return request({
    url: '/redfish/monitor/health',
    method: 'get'
  })
} 