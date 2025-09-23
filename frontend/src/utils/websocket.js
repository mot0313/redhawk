/**
 * WebSocket客户端服务
 * 用于实时接收后端推送的监控数据和告警信息
 */
import { ElNotification, ElMessage } from 'element-plus'

class WebSocketService {
  constructor() {
    this.ws = null
    this.reconnectTimer = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectInterval = 3000
    this.listeners = new Map()
    this.isConnecting = false
    this.shouldReconnect = true
    
    // 消息去重缓存
    this.messageCache = new Map()
    this.cacheTimeout = 5000 // 5秒缓存时间
    
    // WebSocket就绪状态管理
    this.connectionState = {
      connected: false,      // WebSocket连接是否建立
      authenticated: false,  // 是否已认证
      roomsSubscribed: false // 是否已订阅房间
    }
    
    // 房间订阅管理
    this.roomSubscription = {
      targetRooms: ['dashboard', 'alerts', 'urgent_alerts', 'device_monitoring'],
      joinedRooms: new Set(),
      subscriptionTimeout: null
    }
    
    // 获取WebSocket URL
    this.wsUrl = this.getWebSocketUrl()
  }

  /**
   * 获取WebSocket连接URL
   */
  getWebSocketUrl() {
    // 根据当前协议选择ws或wss
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    
    // 在开发环境下，明确指定后端服务器地址
    // if (process.env.NODE_ENV === 'development') {
    //   return `${protocol}//192.168.1.158:9099/ws/redfish`
    // }
    
    // 生产环境使用当前域名
    const host = window.location.hostname
    const port = window.location.port
    // return `${protocol}//${host}:${port}/ws/redfish`
    return `${protocol}//${host}:9099/ws/redfish`
  }

  /**
   * 连接WebSocket
   */
  connect() {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      console.log('[WebSocket] 连接已存在或正在连接中')
      return
    }

    this.isConnecting = true
    
    // 输出详细的连接信息
    console.log(`[WebSocket] 开始连接到: ${this.wsUrl}`)
    console.log(`[WebSocket] 环境: ${process.env.NODE_ENV}`)
    console.log(`[WebSocket] 当前页面: ${window.location.href}`)

    try {
      this.ws = new WebSocket(this.wsUrl)

      this.ws.onopen = this.onOpen.bind(this)
      this.ws.onmessage = this.onMessage.bind(this)
      this.ws.onclose = this.onClose.bind(this)
      this.ws.onerror = this.onError.bind(this)

    } catch (error) {
      console.error('[WebSocket] 连接创建失败:', error)
      this.isConnecting = false
      this.scheduleReconnect()
    }
  }

  /**
   * 连接成功处理
   */
  onOpen(event) {
    console.log('[WebSocket] ✅ 连接成功！')
    console.log('[WebSocket] ReadyState:', this.ws.readyState)
    console.log('[WebSocket] URL:', this.ws.url)
    
    this.isConnecting = false
    this.reconnectAttempts = 0
    
    // 更新连接状态
    this.connectionState.connected = true
    this.connectionState.authenticated = false
    this.connectionState.roomsSubscribed = false
    
    // 发送认证和订阅消息
    console.log('[WebSocket] 开始认证和房间订阅...')
    this.authenticate()
    this.subscribeToRooms()
    
    // 通知连接成功（但还未就绪）
    this.emitEvent('connection', { status: 'connected', is_connected: true, is_ready: false })
    
    ElMessage.success('实时推送连接成功')
  }

  /**
   * 接收消息处理
   */
  onMessage(event) {
    try {
      const message = JSON.parse(event.data)
      console.log('[WebSocket] 📥 接收消息:', message)
      
      // 检查消息是否重复
      if (this.isDuplicateMessage(message)) {
        console.log('[WebSocket] ⚠️ 跳过重复消息:', message.type, message.timestamp)
        return
      }
      
      // 根据消息类型分发处理
      this.handleMessage(message)
      
    } catch (error) {
      console.error('[WebSocket] 消息解析失败:', error, 'Raw data:', event.data)
    }
  }

  /**
   * 连接关闭处理
   */
  onClose(event) {
    console.log('[WebSocket] ❌ 连接关闭')
    console.log('[WebSocket] 关闭代码:', event.code)
    console.log('[WebSocket] 关闭原因:', event.reason)
    console.log('[WebSocket] 是否干净关闭:', event.wasClean)
    
    this.isConnecting = false
    
    // 重置连接状态
    this.connectionState.connected = false
    this.connectionState.authenticated = false
    this.connectionState.roomsSubscribed = false
    
    // 清理房间订阅状态
    this.roomSubscription.joinedRooms.clear()
    if (this.roomSubscription.subscriptionTimeout) {
      clearTimeout(this.roomSubscription.subscriptionTimeout)
      this.roomSubscription.subscriptionTimeout = null
    }
    
    this.emitEvent('connection', { status: 'disconnected', is_connected: false, is_ready: false })
    this.emitEvent('not_ready', { reason: 'connection_closed' })
    
    if (this.shouldReconnect && event.code !== 1000) {
      console.log('[WebSocket] 准备重连...')
      this.scheduleReconnect()
    } else {
      console.log('[WebSocket] 不进行重连')
    }
  }

  /**
   * 连接错误处理
   */
  onError(error) {
    console.error('[WebSocket] 🚨 连接错误:', error)
    console.log('[WebSocket] 当前状态:', this.ws ? this.ws.readyState : 'WebSocket不存在')
    
    this.isConnecting = false
    
    // 重置连接状态
    this.connectionState.connected = false
    this.connectionState.authenticated = false
    this.connectionState.roomsSubscribed = false
    
    // 清理房间订阅状态
    this.roomSubscription.joinedRooms.clear()
    if (this.roomSubscription.subscriptionTimeout) {
      clearTimeout(this.roomSubscription.subscriptionTimeout)
      this.roomSubscription.subscriptionTimeout = null
    }
    
    this.emitEvent('connection', { status: 'error', error, is_connected: false, is_ready: false })
    this.emitEvent('not_ready', { reason: 'connection_error', error })
  }

  /**
   * 发送认证信息
   */
  authenticate() {
    // 获取当前用户token
    const token = localStorage.getItem('Admin-Token')
    
    if (token) {
      console.log('[WebSocket] 🔐 使用Token进行认证...')
      // 后端会自动处理认证，这里发送心跳确认连接
      const authResult = this.send({
        type: 'ping'
      })
      
      if (authResult) {
        // 模拟认证成功（实际应等待后端确认）
        setTimeout(() => {
          this.connectionState.authenticated = true
          console.log('[WebSocket] 🔐 Token认证完成')
          this.checkReadyState()
        }, 100)
      } else {
        console.error('[WebSocket] 认证消息发送失败')
        // 即使发送失败也标记为已认证，允许降级使用
        this.connectionState.authenticated = true
        this.checkReadyState()
      }
    } else {
      console.log('[WebSocket] 🔓 未找到认证Token，使用匿名模式')
      // 即使没有token也标记为已认证（如果后端允许匿名连接）
      this.connectionState.authenticated = true
      this.checkReadyState()
    }
  }

  /**
   * 订阅房间
   */
  subscribeToRooms() {
    console.log('[WebSocket] 🏠 开始订阅房间...')
    
    // 重置房间订阅状态
    this.roomSubscription.joinedRooms.clear()
    this.connectionState.roomsSubscribed = false
    
    // 清除之前的超时定时器
    if (this.roomSubscription.subscriptionTimeout) {
      clearTimeout(this.roomSubscription.subscriptionTimeout)
    }
    
    let subscribedCount = 0
    
    this.roomSubscription.targetRooms.forEach(room => {
      console.log(`[WebSocket] 订阅 ${room} 房间`)
      const result = this.send({
        type: 'join_room',
        room: room
      })
      
      if (result) {
        subscribedCount++
      }
    })
    
    console.log('[WebSocket] ✅ 房间订阅请求已发送')
    
    // 设置超时检查，如果3秒内没有收到所有房间确认，则认为订阅完成
    this.roomSubscription.subscriptionTimeout = setTimeout(() => {
      if (!this.connectionState.roomsSubscribed) {
        console.log('[WebSocket] 🏠 房间订阅超时，强制标记为完成')
        this.connectionState.roomsSubscribed = true
        this.checkReadyState()
      }
    }, 3000)
    
    // 如果发送失败，立即标记为完成（降级处理）
    if (subscribedCount === 0) {
      console.warn('[WebSocket] 所有房间订阅请求发送失败，降级处理')
      setTimeout(() => {
        this.connectionState.roomsSubscribed = true
        this.checkReadyState()
      }, 100)
    }
  }

  /**
   * 检查WebSocket是否完全就绪
   */
  checkReadyState() {
    const isReady = this.connectionState.connected && 
                   this.connectionState.authenticated && 
                   this.connectionState.roomsSubscribed
    
    if (isReady) {
      console.log('[WebSocket] 🚀 WebSocket完全就绪！')
      this.emitEvent('ready', { 
        status: 'ready', 
        is_connected: true, 
        is_ready: true,
        connectionState: { ...this.connectionState }
      })
      // ElMessage.success('实时推送已就绪，可以进行操作') // 已取消此提示
    } else {
      console.log('[WebSocket] ⏳ WebSocket未完全就绪', this.connectionState)
    }
  }

  /**
   * 检查消息是否重复
   */
  isDuplicateMessage(message) {
    // 对于监控相关的消息和通知消息，使用timestamp和type作为唯一标识
    if (message.type === 'monitoring_started' || 
        message.type === 'monitoring_completed' || 
        message.type === 'monitor_task' ||
        message.type === 'new_notice') {
      const messageKey = `${message.type}_${message.timestamp}`
      
      if (this.messageCache.has(messageKey)) {
        return true // 重复消息
      }
      
      // 添加到缓存
      this.messageCache.set(messageKey, true)
      
      // 设置过期清理
      setTimeout(() => {
        this.messageCache.delete(messageKey)
      }, this.cacheTimeout)
      
      return false // 新消息
    }
    
    return false // 其他类型消息不做去重
  }

  /**
   * 处理不同类型的消息
   */
  handleMessage(message) {
    const { type, action } = message
    
    switch (type) {
      case 'new_alert':
        this.handleNewAlert(message)
        break
        
      case 'device_status_change':
        this.handleDeviceStatusChange(message)
        break
        
      case 'monitoring_started':
        this.handleMonitoringStarted(message)
        break
        
      case 'monitoring_completed':
        this.handleMonitoringCompleted(message)
        break
        
      case 'dashboard_update':
        this.handleDashboardUpdate(message)
        break
        
      case 'health_status_silent_update':
        this.handleHealthStatusSilentUpdate(message)
        break
        
      case 'urgent_alert_notification':
        this.handleUrgentAlertNotification(message)
        break
        
      case 'system_notification':
        this.handleSystemNotification(message)
        break
        
      case 'monitoring_progress':
        this.handleMonitoringProgress(message)
        break
        
      case 'new_notice':
        this.emitEvent('new_notice', message)
        break
        
      // 新增消息类型处理
      case 'connection':
        this.handleConnectionMessage(message)
        break
        
      case 'room':
        this.handleRoomMessage(message)
        break
        
      case 'initial_status':
        this.handleInitialStatus(message)
        break
        
      case 'monitor_task':
        this.handleMonitorTask(message)
        break
        
      case 'manual_monitor_result':
        this.handleManualMonitorResult(message)
        break
        
      case 'urgency_recalculation_completed':
        this.emitEvent('urgency_recalculation_completed', message)
        break
        
      // 新增数据推送类型处理
      case 'alert_statistics_update':
        this.handleAlertStatisticsUpdate(message)
        break
        
      case 'device_health_summary':
        this.handleDeviceHealthSummary(message)
        break
        
      case 'dashboard_statistics':
        this.handleDashboardStatistics(message)
        break
        
      case 'monitoring_task_status':
        this.handleMonitoringTaskStatus(message)
        break
        
      default:
        console.log('[WebSocket] 未知消息类型:', type)
        this.emitEvent('message', message)
    }
  }

  /**
   * 处理新告警
   */
  handleNewAlert(message) {
    console.log('[WebSocket] 新告警:', message)
    
    const alertData = message.alert || message
    
    // 发出告警事件
    this.emitEvent('new_alert', alertData)
    
    // 如果是紧急告警，显示通知
    if (alertData.alert_type === 'urgent') {
      ElNotification({
        title: '紧急告警',
        message: `设备 ${alertData.hostname} 出现紧急告警: ${alertData.alert_message}`,
        type: 'error',
        duration: 0, // 不自动关闭
        position: 'top-right'
      })
    } else {
      ElNotification({
        title: '新告警',
        message: `设备 ${alertData.hostname} 出现告警: ${alertData.alert_message}`,
        type: 'warning',
        duration: 5000,
        position: 'top-right'
      })
    }
  }

  /**
   * 处理设备状态变化
   */
  handleDeviceStatusChange(message) {
    console.log('[WebSocket] 设备状态变化:', message)
    this.emitEvent('device_status_change', message)
  }

  /**
   * 处理监控开始
   */
  handleMonitoringStarted(message) {
    console.log('[WebSocket] 监控开始:', message)
    this.emitEvent('monitoring_started', message)
  }

  /**
   * 处理监控完成
   */
  handleMonitoringCompleted(message) {
    console.log('[WebSocket] 监控完成:', message)
    this.emitEvent('monitoring_completed', message)
  }

  /**
   * 处理Dashboard更新
   */
  handleDashboardUpdate(message) {
    console.log('[WebSocket] Dashboard update:', message)
    this.emitEvent('dashboard_update', message)
  }

  /**
   * 处理设备健康状态静默更新（仅更新健康图，不显示通知）
   */
  handleHealthStatusSilentUpdate(message) {
    const { data } = message
    
    if (data && data.device_id) {
      console.log(`[WebSocket] Silent health update: ${data.device_id} ${data.old_health_status} -> ${data.new_health_status}`)
      
      // 发出静默更新事件，不显示用户通知，只更新图表
      this.emitEvent('health_status_silent_update', {
        device_id: data.device_id,
        hostname: data.hostname,
        old_health_status: data.old_health_status,
        new_health_status: data.new_health_status,
        silent: true
      })
    }
  }

  /**
   * 处理紧急告警通知
   */
  handleUrgentAlertNotification(message) {
    console.log('[WebSocket] Urgent alert notification:', message)
    
    const alertData = message.alert || message
    
    // 播放声音提醒（如果支持）
    this.playNotificationSound()
    
    // 显示紧急通知
    ElNotification({
      title: '紧急告警',
      message: `设备 ${alertData.hostname} 出现紧急故障，请立即处理！`,
      type: 'error',
      duration: 0,
      position: 'top-right',
      showClose: true,
      customClass: 'urgent-alert-notification'
    })
    
    this.emitEvent('urgent_alert', alertData)
  }

  /**
   * 处理系统通知
   */
  handleSystemNotification(message) {
    console.log('[WebSocket] System notification:', message)
    
    const title = message.title || '系统通知'
    const content = message.message || '收到系统通知'
    const type = message.level || 'info'
    
    // 显示Element Plus通知
    ElNotification({
      title: title,
      message: content,
      type: type === 'success' ? 'success' : type === 'error' ? 'error' : 'info',
      duration: 4000
    })
    
    this.emitEvent('system_notification', message)
  }

  /**
   * 处理监控进度
   */
  handleMonitoringProgress(message) {
    this.emitEvent('monitoring_progress', message)
  }

  /**
   * 处理连接相关消息
   */
  handleConnectionMessage(message) {
    this.emitEvent('connection_message', message)
  }

  /**
   * 处理房间相关消息
   */
  handleRoomMessage(message) {
    if (message.action === 'joined') {
      console.log(`[WebSocket] ✅ 成功加入房间: ${message.room}`)
      
      // 记录已加入的房间
      this.roomSubscription.joinedRooms.add(message.room)
      
      // 检查是否所有房间都已加入
      if (this.roomSubscription.joinedRooms.size >= this.roomSubscription.targetRooms.length) {
        console.log('[WebSocket] 🏠 所有房间订阅完成')
        this.connectionState.roomsSubscribed = true
        
        // 清除超时定时器
        if (this.roomSubscription.subscriptionTimeout) {
          clearTimeout(this.roomSubscription.subscriptionTimeout)
          this.roomSubscription.subscriptionTimeout = null
        }
        
        // 检查就绪状态
        this.checkReadyState()
      }
    } else if (message.action === 'left') {
      console.log(`[WebSocket] ❌ 离开房间: ${message.room}`)
      this.roomSubscription.joinedRooms.delete(message.room)
    }
    
    this.emitEvent('room_message', message)
  }

  /**
   * 处理初始状态
   */
  handleInitialStatus(message) {
    this.emitEvent('initial_status', message.data)
  }

  /**
   * 处理监控任务消息
   */
  handleMonitorTask(message) {
    // 移除重复通知，由dashboard组件统一处理
    this.emitEvent('monitor_task', message)
  }

  /**
   * 处理手动监控结果
   */
  handleManualMonitorResult(message) {
    const result = message.data
    if (result.success) {
      ElNotification({
        title: '监控任务',
        message: result.message || '手动监控任务已开始执行',
        type: 'success',
        duration: 3000
      })
    } else {
      ElNotification({
        title: '监控任务失败',
        message: result.message || '手动监控任务执行失败',
        type: 'error',
        duration: 5000
      })
    }
    
    this.emitEvent('manual_monitor_result', result)
  }

  /**
   * 播放通知声音
   */
  playNotificationSound() {
    try {
      // 创建简单的提示音
      const audioContext = new (window.AudioContext || window.webkitAudioContext)()
      const oscillator = audioContext.createOscillator()
      const gainNode = audioContext.createGain()
      
      oscillator.connect(gainNode)
      gainNode.connect(audioContext.destination)
      
      oscillator.frequency.value = 800
      gainNode.gain.setValueAtTime(0.3, audioContext.currentTime)
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5)
      
      oscillator.start(audioContext.currentTime)
      oscillator.stop(audioContext.currentTime + 0.5)
    } catch (error) {
      console.warn('[WebSocket] 无法播放通知声音:', error)
    }
  }

  /**
   * 发送消息
   */
  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      try {
        const messageStr = JSON.stringify(message)
        this.ws.send(messageStr)
        return true
      } catch (error) {
        console.error('[WebSocket] Send message failed:', error, 'Message:', message)
        return false
      }
    } else {
      console.warn('[WebSocket] Connection not established, cannot send message')
      return false
    }
  }

  /**
   * 安排重连
   */
  scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WebSocket] 达到最大重连次数，停止重连')
      
      // 提供手动重连选项
      ElNotification({
        title: '连接失败',
        message: '实时推送连接失败，点击重新连接或刷新页面',
        type: 'error',
        duration: 0, // 不自动关闭
        dangerouslyUseHTMLString: true,
        customClass: 'websocket-reconnect-notification',
        onClose: () => {
          // 通知连接彻底失败
          this.emitEvent('connection_failed', { 
            attempts: this.reconnectAttempts,
            message: '达到最大重连次数'
          })
        }
      })
      
      return
    }

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
    }

    const delay = this.reconnectInterval * Math.pow(2, this.reconnectAttempts)
    this.reconnectAttempts++

    console.log(`[WebSocket] ${delay/1000}秒后尝试第${this.reconnectAttempts}次重连`)
    
    this.reconnectTimer = setTimeout(() => {
      this.connect()
    }, delay)
  }

  /**
   * 手动重连（重置重连计数）
   */
  manualReconnect() {
    console.log('[WebSocket] 手动触发重连...')
    this.reconnectAttempts = 0
    this.shouldReconnect = true
    
    // 断开现有连接
    if (this.ws) {
      this.ws.close(1000, '手动重连')
    }
    
    // 清除重连定时器
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    
    // 立即尝试连接
    setTimeout(() => {
      this.connect()
    }, 1000)
  }

  /**
   * 添加事件监听器
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  /**
   * 移除事件监听器
   */
  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  /**
   * 触发事件
   */
  emitEvent(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`[WebSocket] 事件回调错误 (${event}):`, error)
        }
      })
    }
  }

  /**
   * 断开连接
   */
  disconnect() {
    this.shouldReconnect = false
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    
    if (this.ws) {
      this.ws.close(1000, '用户主动断开')
      this.ws = null
    }
  }

  /**
   * 获取连接状态
   */
  getReadyState() {
    return this.ws ? this.ws.readyState : WebSocket.CLOSED
  }

  /**
   * 检查是否已连接
   */
  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN
  }

  /**
   * 检查是否完全就绪（连接+认证+订阅）
   */
  isReady() {
    return this.connectionState.connected && 
           this.connectionState.authenticated && 
           this.connectionState.roomsSubscribed &&
           this.isConnected()
  }

  /**
   * 处理告警统计更新
   */
  handleAlertStatisticsUpdate(message) {
    console.log('[WebSocket] 告警统计更新:', message)
    this.emitEvent('alert_statistics_update', message.statistics || message)
  }

  /**
   * 处理设备健康状态汇总
   */
  handleDeviceHealthSummary(message) {
    console.log('[WebSocket] 设备健康状态汇总:', message)
    this.emitEvent('device_health_summary', message.devices || message)
  }

  /**
   * 处理Dashboard统计数据
   */
  handleDashboardStatistics(message) {
    console.log('[WebSocket] Dashboard统计数据:', message)
    this.emitEvent('dashboard_statistics', message.statistics || message)
  }

  /**
   * 处理监控任务状态更新
   */
  handleMonitoringTaskStatus(message) {
    console.log('[WebSocket] 监控任务状态更新:', message)
    this.emitEvent('monitoring_task_status', message)
  }
}

// 创建全局WebSocket服务实例
export const websocketService = new WebSocketService()

// 自动连接
if (typeof window !== 'undefined') {
  websocketService.connect()
}

export default websocketService 