import request from '@/utils/request'

// 检测单个设备的业务IP连通性
export function checkDeviceConnectivity(deviceId) {
  return request({
    url: `/redfish/connectivity/check/${deviceId}`,
    method: 'post'
  })
}

// 批量检测设备连通性
export function batchCheckConnectivity(data) {
  return request({
    url: '/redfish/connectivity/batch-check',
    method: 'post',
    params: {
      maxConcurrent: data.maxConcurrent || 20
    },
    data: {
      deviceIds: data.deviceIds
    }
  })
}

// 获取设备连通性统计
export function getConnectivityStatistics(params) {
  return request({
    url: '/redfish/connectivity/statistics',
    method: 'get',
    params: {
      useCache: params?.useCache !== false,
      cacheTtlMinutes: params?.cacheTtlMinutes || 5
    }
  })
}

// 刷新连通性统计缓存
export function refreshConnectivityCache() {
  return request({
    url: '/redfish/connectivity/refresh-cache',
    method: 'post'
  })
}

// 检测指定IP的连通性
export function checkIpConnectivity(businessIp) {
  return request({
    url: '/redfish/connectivity/check-ip',
    method: 'post',
    data: {
      businessIp
    }
  })
} 