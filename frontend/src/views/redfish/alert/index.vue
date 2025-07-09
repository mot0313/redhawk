<template>
  <div class="app-container">

    <el-row :gutter="10" class="mb20">
      <el-col :span="1.5">
        <el-button-group>
          <el-button
            :type="viewMode === 'list' ? 'primary' : 'default'"
            icon="List"
            @click="viewMode = 'list'; handleViewModeChange()"
          >列表视图</el-button>
          <el-button
            :type="viewMode === 'calendar' ? 'primary' : 'default'"
            icon="Calendar"
            @click="viewMode = 'calendar'; handleViewModeChange()"
          >日历视图</el-button>
        </el-button-group>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="warning"
          plain
          icon="Calendar"
          :disabled="multiple"
          @click="handleBatchScheduleMaintenance"
          v-hasPermi="['redfish:alert:maintenance']"
          v-show="viewMode === 'list'"
        >批量计划时间</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="info"
          plain
          icon="Download"
          @click="handleExport"
          v-hasPermi="['redfish:alert:export']"
        >导出</el-button>
      </el-col>
      <right-toolbar
        v-model:showSearch="showSearch"
        @queryTable="getList"
        :columns="columns"
        v-show="viewMode === 'list'"
      ></right-toolbar>
    </el-row>

    <el-form
      :model="queryParams"
      ref="queryRef"
      :inline="true"
      v-show="showSearch && viewMode === 'list'"
      label-width="68px"
    >
        <el-form-item label="设备名称" prop="hostname">
          <el-input
            v-model="queryParams.hostname"
            placeholder="请输入设备名称"
            clearable
          style="width: 150px"
            @keyup.enter="handleQuery"
          />
        </el-form-item>
        <el-form-item label="业务IP" prop="businessIp">
          <el-input
            v-model="queryParams.businessIp"
            placeholder="请输入业务IP"
            clearable
          style="width: 150px"
            @keyup.enter="handleQuery"
          />
        </el-form-item>
        <el-form-item label="组件类型" prop="componentType">
          <el-select
            v-model="queryParams.componentType"
          placeholder="组件类型"
            clearable
          style="width: 100px"
          >
            <el-option label="CPU" value="cpu" />
            <el-option label="内存" value="memory" />
            <el-option label="存储" value="storage" />
            <el-option label="风扇" value="fan" />
            <el-option label="电源" value="power" />
            <el-option label="温度" value="temperature" />
            <el-option label="网络" value="network" />
          </el-select>
        </el-form-item>
        <el-form-item label="紧急程度" prop="urgencyLevel">
          <el-select
            v-model="queryParams.urgencyLevel"
          placeholder="紧急程度"
            clearable
          style="width: 100px"
          >
            <el-option label="紧急" value="urgent" />
            <el-option label="择期" value="scheduled" />
          </el-select>
        </el-form-item>
        <el-form-item label="告警状态" prop="alertStatus">
          <el-select
            v-model="queryParams.alertStatus"
          placeholder="告警状态"
            clearable
          style="width: 100px"
          >
            <el-option label="活跃" value="active" />
            <el-option label="已解决" value="resolved" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
          <el-button icon="Refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table
        v-show="viewMode === 'list'"
        v-loading="loading"
        :data="alertList"
        @selection-change="handleSelectionChange"
        :default-sort="{prop: 'lastOccurrence', order: 'descending'}"
      >
        <el-table-column type="selection" width="50" align="center" />
      <el-table-column
        label="序号"
        align="center"
        key="index"
        width="50"
        v-if="columns[0].visible"
      >
        <template #default="scope">
          {{ (queryParams.pageNum - 1) * queryParams.pageSize + scope.$index + 1 }}
        </template>
      </el-table-column>
      <el-table-column
        label="设备信息"
        align="center"
        key="deviceInfo"
        width="200"
        v-if="columns[1].visible"
        :show-overflow-tooltip="true"
      >
          <template #default="scope">
            <div>
              <div class="font-medium">{{ scope.row.hostname }}</div>
              <div class="text-sm text-gray-500">{{ scope.row.businessIp }}</div>
            </div>
          </template>
        </el-table-column>
      <el-table-column
        label="组件信息"
        align="center"
        key="componentInfo"
        width="180"
        v-if="columns[2].visible"
        :show-overflow-tooltip="true"
      >
          <template #default="scope">
            <div>
              <div class="font-medium">{{ scope.row.componentType }}</div>
              <div class="text-sm text-gray-500">{{ scope.row.componentName }}</div>
            </div>
          </template>
        </el-table-column>
      <el-table-column
        label="紧急程度"
        align="center"
        key="urgencyLevel"
        width="100"
        v-if="columns[3].visible"
      >
          <template #default="scope">
            <el-tag
              :type="scope.row.urgencyLevel === 'urgent' ? 'danger' : 'warning'"
              effect="dark"
            >
              {{ scope.row.urgencyLevel === 'urgent' ? '紧急' : '择期' }}
            </el-tag>
          </template>
        </el-table-column>
      <el-table-column
        label="健康状态"
        align="center"
        key="healthStatus"
        width="100"
        v-if="columns[4].visible"
      >
          <template #default="scope">
            <el-tag
              :type="getHealthStatusType(scope.row.healthStatus)"
              effect="plain"
            >
              {{ getHealthStatusText(scope.row.healthStatus) }}
            </el-tag>
          </template>
        </el-table-column>
      <el-table-column
        label="告警消息"
        align="center"
        key="alertMessage"
        prop="alertMessage"
        v-if="columns[5].visible"
        :show-overflow-tooltip="true"
      />
      <el-table-column
        label="发生时间"
        align="center"
        key="occurrenceTime"
        width="160"
        v-if="columns[6].visible"
      >
          <template #default="scope">
            <div>
              <div class="text-sm">首次：{{ parseTime(scope.row.firstOccurrence, '{y}-{m}-{d} {h}:{i}') }}</div>
              <div class="text-sm text-gray-500" v-if="scope.row.lastOccurrence">
                最新：{{ parseTime(scope.row.lastOccurrence, '{y}-{m}-{d} {h}:{i}') }}
              </div>
            </div>
          </template>
        </el-table-column>
      <el-table-column
        label="状态"
        align="center"
        key="alertStatus"
        width="80"
        v-if="columns[7].visible"
      >
          <template #default="scope">
            <el-tag
              :type="getAlertStatusType(scope.row.alertStatus)"
              size="small"
            >
              {{ getAlertStatusText(scope.row.alertStatus) }}
            </el-tag>
          </template>
        </el-table-column>
      <el-table-column
        label="维修计划"
        align="center"
        key="maintenanceInfo"
        width="160"
        v-if="columns[8].visible"
      >
          <template #default="scope">
            <div v-if="scope.row.scheduledMaintenanceTime">
              <div class="text-sm">{{ parseTime(scope.row.scheduledMaintenanceTime, '{m}-{d} {h}:{i}') }}</div>
              <el-tag 
                :type="getMaintenanceStatusType(scope.row.maintenanceStatus)" 
                size="small"
              >
                {{ getMaintenanceStatusText(scope.row.maintenanceStatus) }}
              </el-tag>
            </div>
            <div v-else class="text-gray-400">未安排</div>
          </template>
        </el-table-column>
      <el-table-column
        label="操作"
        align="center"
        width="200"
        fixed="right"
        v-if="columns[9].visible"
      >
          <template #default="scope">
            <el-button
              link
              type="primary"
              icon="View"
              @click="handleDetail(scope.row)"
            ></el-button>
            <el-button
              v-if="scope.row.alertStatus === 'active'"
              link
              type="warning"
              icon="Calendar"
              @click="handleScheduleMaintenance(scope.row)"
              v-hasPermi="['redfish:alert:maintenance']"
            ></el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 日历视图 -->
      <div v-show="viewMode === 'calendar'" class="calendar-container">
        <div v-if="loading" class="calendar-loading">
          <el-skeleton :rows="5" animated />
        </div>
        <div v-else>
          <div class="calendar-header">
            <el-alert
              title="日历视图说明"
              description="此视图显示已安排维修时间的告警。蓝色左边框表示计划中，绿色左边框表示已完成。红色表示紧急告警，橙色表示择期告警。点击维修项目可查看详细信息。"
              type="info"
              :closable="false"
              show-icon
            />
          </div>
          <el-calendar v-model="calendarDate" @click="handleCalendarClick" @input="handleCalendarDateChange">
            <template #date-cell="{ data }">
              <div class="calendar-cell">
                <div class="date-text">{{ data.day.split('-')[2] }}</div>
                <div class="maintenance-items">
                  <div 
                    v-for="item in getMaintenanceItemsForDate(data.day)" 
                    :key="item.alertId"
                    class="maintenance-item"
                    :class="getMaintenanceItemClass(item)"
                    @click.stop="handleCalendarItemClick(item)"
                  >
                    <div class="item-info">
                      <span class="device-name">{{ item.hostname }}</span>
                      <span class="component-type">{{ item.componentType }}</span>
                    </div>
                    <div class="maintenance-time">
                      {{ formatMaintenanceTime(item.scheduledMaintenanceTime) }}
                    </div>
                  </div>
                  <div v-if="getMaintenanceItemsForDate(data.day).length === 0 && isToday(data.day)" class="no-maintenance">
                    <span class="today-mark">今日无维修计划</span>
                  </div>
                </div>
              </div>
            </template>
          </el-calendar>
        </div>
      </div>

      <pagination
        v-show="total > 0 && viewMode === 'list'"
        :total="total"
        v-model:page="queryParams.pageNum"
        v-model:limit="queryParams.pageSize"
        @pagination="getList"
      />

    <!-- 告警详情弹窗 -->
    <el-dialog
      title="告警详情"
      v-model="detailVisible"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-descriptions v-if="alertDetail" :column="2" border>
        <el-descriptions-item label="告警ID">{{ alertDetail.alertId }}</el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ alertDetail.hostname }}</el-descriptions-item>
        <el-descriptions-item label="业务IP">{{ alertDetail.businessIp }}</el-descriptions-item>
        <el-descriptions-item label="组件类型">{{ alertDetail.componentType }}</el-descriptions-item>
        <el-descriptions-item label="组件名称">{{ alertDetail.componentName }}</el-descriptions-item>
        <el-descriptions-item label="紧急程度">
          <el-tag :type="alertDetail.urgencyLevel === 'urgent' ? 'danger' : 'warning'">
            {{ alertDetail.urgencyLevel === 'urgent' ? '紧急' : '择期' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="健康状态">
          <el-tag :type="getHealthStatusType(alertDetail.healthStatus)">
            {{ getHealthStatusText(alertDetail.healthStatus) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="当前状态">
          <el-tag :type="getAlertStatusType(alertDetail.alertStatus)">
            {{ getAlertStatusText(alertDetail.alertStatus) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="告警消息" :span="2">{{ alertDetail.alertMessage }}</el-descriptions-item>
        <el-descriptions-item label="首次发生">{{ parseTime(alertDetail.firstOccurrence) }}</el-descriptions-item>
        <el-descriptions-item label="最后发生">{{ parseTime(alertDetail.lastOccurrence) }}</el-descriptions-item>
        <el-descriptions-item label="发生次数">{{ alertDetail.occurrenceCount }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ parseTime(alertDetail.createTime) }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>





    <!-- 计划维修时间弹窗 -->
    <el-dialog
      title="安排维修时间"
      v-model="maintenanceVisible"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form ref="maintenanceRef" :model="maintenanceForm" :rules="maintenanceRules" label-width="120px">
        <el-form-item label="计划维修时间" prop="scheduledMaintenanceTime">
          <el-date-picker
            v-model="maintenanceForm.scheduledMaintenanceTime"
            type="datetime"
            placeholder="选择计划维修时间"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>

        <el-form-item label="维修描述">
          <el-input
            v-model="maintenanceForm.maintenanceDescription"
            type="textarea"
            :rows="3"
            placeholder="请输入维修描述"
          />
        </el-form-item>
        <el-form-item label="维修备注">
          <el-input
            v-model="maintenanceForm.maintenanceNotes"
            type="textarea"
            :rows="2"
            placeholder="请输入维修备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="maintenanceVisible = false">取消</el-button>
          <el-button type="primary" @click="submitMaintenance">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 批量计划维修时间弹窗 -->
    <el-dialog
      title="批量安排维修时间"
      v-model="batchMaintenanceVisible"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form ref="batchMaintenanceRef" :model="batchMaintenanceForm" :rules="batchMaintenanceRules" label-width="120px">
        <el-form-item label="计划维修时间" prop="scheduledMaintenanceTime">
          <el-date-picker
            v-model="batchMaintenanceForm.scheduledMaintenanceTime"
            type="datetime"
            placeholder="选择计划维修时间"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>

        <el-form-item label="维修描述">
          <el-input
            v-model="batchMaintenanceForm.maintenanceDescription"
            type="textarea"
            :rows="3"
            placeholder="请输入维修描述"
          />
        </el-form-item>
        <el-form-item label="维修备注">
          <el-input
            v-model="batchMaintenanceForm.maintenanceNotes"
            type="textarea"
            :rows="2"
            placeholder="请输入维修备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="batchMaintenanceVisible = false">取消</el-button>
          <el-button type="primary" @click="submitBatchMaintenance">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 精简版移除忽略告警功能 -->
  </div>
</template>

<script setup name="AlertManagement">
import { ref, onMounted, getCurrentInstance } from 'vue'
import { 
  getAlertList, 
  getAlertDetail, 
  exportAlerts,
  scheduleMaintenance,
  updateMaintenance,
  batchScheduleMaintenance,
  getCalendarMaintenance
} from '@/api/redfish/alert'
import { parseTime } from '@/utils/ruoyi'

const { proxy } = getCurrentInstance()

// 响应式数据
const alertList = ref([])
const loading = ref(true)
const ids = ref([])
const single = ref(true)
const multiple = ref(true)
const total = ref(0)
const showSearch = ref(true)

// 视图相关
const viewMode = ref('list') // 'list' 或 'calendar'
const calendarDate = ref(new Date())
const maintenanceData = ref([])

// 列显示控制
const columns = ref([
  { key: 0, label: `序号`, visible: true },
  { key: 1, label: `设备信息`, visible: true },
  { key: 2, label: `组件信息`, visible: true },
  { key: 3, label: `紧急程度`, visible: true },
  { key: 4, label: `健康状态`, visible: true },
  { key: 5, label: `告警消息`, visible: true },
  { key: 6, label: `发生时间`, visible: true },
  { key: 7, label: `状态`, visible: true },
  { key: 8, label: `维修计划`, visible: true },
  { key: 9, label: `操作`, visible: true }
])

// 查询参数
const queryParams = ref({
  pageNum: 1,
  pageSize: 10,
  hostname: null,
  businessIp: null,
  componentType: null,
  urgencyLevel: null,
  alertStatus: null
})

// 弹窗状态
const detailVisible = ref(false)
const maintenanceVisible = ref(false)
const batchMaintenanceVisible = ref(false)

// 详情数据
const alertDetail = ref(null)

// 表单数据
const maintenanceForm = ref({
  alertId: null,
  scheduledMaintenanceTime: null,
  maintenanceDescription: '',
  maintenanceNotes: ''
})

const batchMaintenanceForm = ref({
  alertIds: [],
  scheduledMaintenanceTime: null,
  maintenanceDescription: '',
  maintenanceNotes: ''
})



// 表单验证规则
const maintenanceRules = {
  scheduledMaintenanceTime: [
    { required: true, message: "计划维修时间不能为空", trigger: "change" }
  ]
}

const batchMaintenanceRules = {
  scheduledMaintenanceTime: [
    { required: true, message: "计划维修时间不能为空", trigger: "change" }
  ]
}



/** 查询告警列表 */
function getList() {
  loading.value = true
  getAlertList(queryParams.value).then(response => {
    if (response && response.rows) {
      alertList.value = response.rows
      total.value = response.total || 0
    } else {
      alertList.value = []
      total.value = 0
    }
    loading.value = false
  }).catch(error => {
    console.error('获取告警列表失败:', error)
    alertList.value = []
    total.value = 0
    loading.value = false
    proxy.$modal.msgError("获取告警列表失败，请检查后端服务是否正常")
  })
}

/** 搜索按钮操作 */
function handleQuery() {
  queryParams.value.pageNum = 1
  getList()
}

/** 重置按钮操作 */
function resetQuery() {
  queryParams.value = {
    pageNum: 1,
    pageSize: 10,
    hostname: null,
    businessIp: null,
    componentType: null,
    urgencyLevel: null,
    alertStatus: null
  }
  handleQuery()
}

/** 多选框选中数据 */
function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.alertId)
  single.value = selection.length != 1
  multiple.value = !selection.length
}

/** 查看详情 */
function handleDetail(row) {
  getAlertDetail(row.alertId).then(response => {
    if (response && response.data) {
      alertDetail.value = response.data
      detailVisible.value = true
    } else {
      proxy.$modal.msgError("获取告警详情失败")
    }
  }).catch(error => {
    console.error('获取告警详情失败:', error)
    proxy.$modal.msgError("获取告警详情失败，请检查后端服务是否正常")
  })
}

// 精简版移除解决和忽略告警功能

/** 导出 */
function handleExport() {
  proxy.download('redfish/alert/export', {
    ...queryParams.value
  }, `alert_${new Date().getTime()}.xlsx`)
}

/** 获取健康状态类型 */
function getHealthStatusType(status) {
  const statusMap = {
    'OK': 'success',
    'Warning': 'warning', 
    'Critical': 'warning',  // 简化分类：Critical合并到warning
    'Unknown': 'info'
  }
  return statusMap[status] || 'info'
}

/** 获取健康状态文本 */
function getHealthStatusText(status) {
  const statusMap = {
    'OK': '正常',
    'Warning': '警告',
    'Critical': '警告',  // 简化分类：Critical显示为警告
    'Unknown': '未知'
  }
  return statusMap[status] || status
}

/** 获取告警状态类型 */
function getAlertStatusType(status) {
  const statusMap = {
    'active': 'primary',
    'resolved': 'success',
    'ignored': 'info'
  }
  return statusMap[status] || 'info'
}

/** 获取告警状态文本 */
function getAlertStatusText(status) {
  const statusMap = {
    'active': '活跃',
    'resolved': '已解决',
    'ignored': '已忽略'
  }
  return statusMap[status] || status
}

/** 获取维修状态类型 */
function getMaintenanceStatusType(status) {
  const statusMap = {
    'none': 'info',
    'planned': 'warning',
    'in_progress': 'primary',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return statusMap[status] || 'info'
}

/** 获取维修状态文本 */
function getMaintenanceStatusText(status) {
  const statusMap = {
    'none': '未安排',
    'planned': '已计划',
    'in_progress': '进行中',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusMap[status] || status
}

/** 安排维修时间 */
function handleScheduleMaintenance(row) {
  maintenanceForm.value = {
    alertId: row.alertId,
    scheduledMaintenanceTime: row.scheduledMaintenanceTime || null,
    maintenanceDescription: row.maintenanceDescription || '',
    maintenanceNotes: row.maintenanceNotes || ''
  }
  maintenanceVisible.value = true
}

/** 提交维修计划 */
function submitMaintenance() {
  proxy.$refs["maintenanceRef"].validate(valid => {
    if (valid) {
      // 构建API请求数据，使用驼峰命名
      const requestData = {
        alertId: maintenanceForm.value.alertId,
        scheduledMaintenanceTime: maintenanceForm.value.scheduledMaintenanceTime,
        maintenanceDescription: maintenanceForm.value.maintenanceDescription,
        maintenanceNotes: maintenanceForm.value.maintenanceNotes
      }
      
      // 总是使用 scheduleMaintenance API，因为它能处理创建和更新
      scheduleMaintenance(requestData).then(() => {
        proxy.$modal.msgSuccess("维修计划设置成功")
        maintenanceVisible.value = false
        getList()
      }).catch(error => {
        console.error('设置维修计划失败:', error)
        proxy.$modal.msgError("设置维修计划失败，请检查后端服务是否正常")
      })
    }
  })
}

/** 批量安排维修时间 */
function handleBatchScheduleMaintenance() {
  if (ids.value.length === 0) {
    proxy.$modal.msgError("请选择要安排维修时间的告警")
    return
  }
  batchMaintenanceForm.value = {
    alertIds: ids.value,
    scheduledMaintenanceTime: null,
    maintenanceDescription: '',
    maintenanceNotes: ''
  }
  batchMaintenanceVisible.value = true
}

/** 提交批量维修计划 */
function submitBatchMaintenance() {
  proxy.$refs["batchMaintenanceRef"].validate(valid => {
    if (valid) {
      // 构建API请求数据，使用驼峰命名
      const requestData = {
        alertIds: batchMaintenanceForm.value.alertIds,
        scheduledMaintenanceTime: batchMaintenanceForm.value.scheduledMaintenanceTime,
        maintenanceDescription: batchMaintenanceForm.value.maintenanceDescription,
        maintenanceNotes: batchMaintenanceForm.value.maintenanceNotes
      }
      
      batchScheduleMaintenance(requestData).then(() => {
        proxy.$modal.msgSuccess("批量维修计划设置成功")
        batchMaintenanceVisible.value = false
        getList()
      }).catch(error => {
        console.error('批量设置维修计划失败:', error)
        proxy.$modal.msgError("批量设置维修计划失败，请检查后端服务是否正常")
      })
    }
  })
}

/** 日历相关方法 */

/** 获取指定日期的维修项目 */
function getMaintenanceItemsForDate(dateStr) {
  return alertList.value.filter(item => {
    if (!item.scheduledMaintenanceTime) return false
    const itemDate = new Date(item.scheduledMaintenanceTime).toDateString()
    const targetDate = new Date(dateStr).toDateString()
    return itemDate === targetDate
  })
}

/** 获取维修项目的样式类 */
function getMaintenanceItemClass(item) {
  const classMap = {
    'urgent': 'maintenance-urgent',
    'scheduled': 'maintenance-scheduled'
  }
  
  // 根据告警状态和维修计划安排情况设置边框
  let statusClass = ''
  if (item.scheduledMaintenanceTime) {
    if (item.alertStatus === 'active') {
      statusClass = 'status-planned' // 蓝色边框 - 计划中
    } else if (item.alertStatus === 'resolved') {
      statusClass = 'status-in-progress' // 绿色边框 - 已完成
    }
  }
  
  return [
    classMap[item.urgencyLevel] || 'maintenance-scheduled',
    statusClass
  ].filter(Boolean) // 过滤掉空字符串
}

/** 格式化维修时间 */
function formatMaintenanceTime(dateTime) {
  if (!dateTime) return ''
  const date = new Date(dateTime)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

/** 处理日历点击事件 */
function handleCalendarClick(date) {
  console.log('Calendar clicked:', date)
  // 可以在这里添加日期点击的处理逻辑
}

/** 处理日历日期变化事件 */
function handleCalendarDateChange(date) {
  console.log('Calendar date changed:', date)
  // 当用户切换月份时重新加载维修计划数据
  if (viewMode.value === 'calendar') {
    loadMaintenanceData()
  }
}

/** 处理日历项目点击事件 */
function handleCalendarItemClick(item) {
  handleDetail(item)
}

/** 判断是否为今天 */
function isToday(dateStr) {
  const today = new Date().toISOString().split('T')[0]
  return dateStr === today
}

/** 加载维修计划数据 */
function loadMaintenanceData() {
  // 在日历视图模式下，加载指定时间范围内的维修计划
  if (viewMode.value === 'calendar') {
    // 获取当前月份的开始和结束日期
    const currentDate = calendarDate.value
    const year = currentDate.getFullYear()
    const month = currentDate.getMonth()
    
    // 获取当前月份的第一天和最后一天
    const startDate = new Date(year, month, 1)
    const endDate = new Date(year, month + 1, 0)
    
    // 扩展到前后各一周，以覆盖日历显示的完整范围
    startDate.setDate(startDate.getDate() - 7)
    endDate.setDate(endDate.getDate() + 7)
    
    const startDateStr = startDate.toISOString().split('T')[0]
    const endDateStr = endDate.toISOString().split('T')[0]
    
    loading.value = true
    getCalendarMaintenance(startDateStr, endDateStr).then(response => {
      if (response && response.data) {
        alertList.value = response.data
      }
      loading.value = false
    }).catch(error => {
      console.error('获取维修计划数据失败:', error)
      loading.value = false
      proxy.$modal.msgError("获取维修计划数据失败")
    })
  }
}

// 监听视图模式变化
function handleViewModeChange() {
  if (viewMode.value === 'calendar') {
    loadMaintenanceData()
  } else {
    getList()
  }
}

onMounted(() => {
  getList()
})
</script>

<style scoped>
.font-medium {
  font-weight: 500;
}

.text-sm {
  font-size: 12px;
}

.text-gray-500 {
  color: #6b7280;
}

/* 日历视图样式 */
.calendar-container {
  margin-top: 20px;
}

.calendar-loading {
  margin-top: 20px;
  padding: 20px;
}

.calendar-header {
  margin-bottom: 15px;
}

.calendar-cell {
  height: 100px;
  padding: 4px;
  overflow: hidden;
}

.date-text {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 4px;
  color: #606266;
}

.maintenance-items {
  display: flex;
  flex-direction: column;
  gap: 2px;
  max-height: 70px;
  overflow-y: auto;
}

.maintenance-item {
  background-color: #f0f9ff;
  border: 1px solid #e0e7ff;
  border-radius: 4px;
  padding: 2px 4px;
  font-size: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.maintenance-item:hover {
  transform: scale(1.02);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.maintenance-urgent {
  background-color: #fef2f2;
  border-color: #fecaca;
  color: #dc2626;
}

.maintenance-scheduled {
  background-color: #fffbeb;
  border-color: #fed7aa;
  color: #d97706;
}

.status-planned {
  border-left: 3px solid #3b82f6;
}

.status-in-progress {
  border-left: 3px solid #10b981;
}

.status-completed {
  border-left: 3px solid #6b7280;
  opacity: 0.7;
}

.status-cancelled {
  border-left: 3px solid #ef4444;
  text-decoration: line-through;
}

.item-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2px;
}

.device-name {
  font-weight: bold;
  color: #374151;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 60px;
}

.component-type {
  color: #6b7280;
  font-size: 9px;
}

.maintenance-time {
  color: #9ca3af;
  font-size: 9px;
  text-align: center;
}

:deep(.el-calendar-table .el-calendar-day) {
  padding: 0;
}

:deep(.el-calendar__body) {
  padding: 12px;
}

.no-maintenance {
  text-align: center;
  padding: 4px;
  color: #9ca3af;
  font-size: 10px;
}

.today-mark {
  background-color: #e0f2fe;
  border: 1px dashed #0284c7;
  border-radius: 4px;
  padding: 2px 4px;
  color: #0284c7;
}
</style> 