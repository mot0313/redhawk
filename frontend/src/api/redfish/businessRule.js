import request from '@/utils/request'

// 查询业务规则列表
export function listBusinessRule(query) {
  return request({
    url: '/redfish/businessRule/list',
    method: 'get',
    params: query
  })
}

// 查询业务规则详细
export function getBusinessRule(ruleId) {
  return request({
    url: '/redfish/businessRule/' + ruleId,
    method: 'get'
  })
}

// 新增业务规则
export function addBusinessRule(data) {
  return request({
    url: '/redfish/businessRule',
    method: 'post',
    data: data
  })
}

// 修改业务规则
export function updateBusinessRule(data) {
  return request({
    url: '/redfish/businessRule',
    method: 'put',
    data: data
  })
}

// 删除业务规则
export function delBusinessRule(ruleIds) {
  return request({
    url: '/redfish/businessRule/' + ruleIds,
    method: 'delete'
  })
}

// 获取业务类型列表
export function getBusinessTypes() {
  return request({
    url: '/redfish/businessRule/types/business',
    method: 'get'
  })
}

// 获取硬件类型列表
export function getHardwareTypes() {
  return request({
    url: '/redfish/businessRule/types/hardware',
    method: 'get'
  })
}

// 获取分类硬件类型
export function getHardwareTypesByCategory() {
  return request({
    url: '/redfish/businessRule/types/hardware/categories',
    method: 'get'
  })
}

// 匹配紧急度规则
export function matchUrgencyRule(data) {
  return request({
    url: '/redfish/businessRule/match',
    method: 'post',
    data: data
  })
}

// 获取规则统计信息
export function getBusinessRuleStatistics() {
  return request({
    url: '/redfish/businessRule/statistics',
    method: 'get'
  })
}

// 修改规则状态
export function changeRuleStatus(ruleId, isActive) {
  return request({
    url: '/redfish/businessRule/changeStatus',
    method: 'put',
    params: {
      ruleId,
      isActive
    }
  })
}

// 批量修改规则状态
export function batchChangeRuleStatus(ruleIds, isActive) {
  return request({
    url: '/redfish/businessRule/batchStatus',
    method: 'put',
    params: {
      ruleIds,
      isActive
    }
  })
} 