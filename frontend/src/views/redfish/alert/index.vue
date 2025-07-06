<template>
  <div class="app-container">

    <el-row :gutter="10" class="mb20">
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="Check"
          :disabled="multiple"
          @click="handleBatchResolve"
          v-hasPermi="['redfish:alert:resolve']"
        >批量解决</el-button>
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
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="Refresh"
          @click="handleRefresh"
        >刷新</el-button>
      </el-col>
      <right-toolbar
        v-model:showSearch="showSearch"
        @queryTable="getList"
        :columns="columns"
      ></right-toolbar>
    </el-row>

    <el-form
      :model="queryParams"
      ref="queryRef"
      :inline="true"
      v-show="showSearch"
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
        label="操作"
        align="center"
        width="200"
        fixed="right"
        v-if="columns[8].visible"
      >
          <template #default="scope">
            <el-button
              link
              type="primary"
              icon="View"
              @click="handleDetail(scope.row)"
            >详情</el-button>
            <el-button
              v-if="scope.row.alertStatus === 'active'"
              link
              type="success"
              icon="Check"
              @click="handleResolve(scope.row)"
            >解决</el-button>
          </template>
        </el-table-column>
      </el-table>

      <pagination
        v-show="total > 0"
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

    <!-- 解决告警弹窗 -->
    <el-dialog
      title="解决告警"
      v-model="resolveVisible"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="resolveRef" :model="resolveForm" :rules="resolveRules" label-width="100px">
        <el-form-item label="操作人" prop="operator">
          <el-input v-model="resolveForm.operator" placeholder="请输入操作人" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="resolveVisible = false">取消</el-button>
          <el-button type="primary" @click="submitResolve">确定</el-button>
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
  resolveAlerts,
  exportAlerts
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
  { key: 8, label: `操作`, visible: true }
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
const resolveVisible = ref(false)

// 详情数据
const alertDetail = ref(null)

// 表单数据
const resolveForm = ref({
  alertIds: '',
  operator: ''
})



// 表单验证规则
const resolveRules = {
  operator: [
    { required: true, message: "操作人不能为空", trigger: "blur" }
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

/** 解决告警 */
function handleResolve(row) {
  resolveForm.value = {
    alertIds: row.alertId.toString(),
    operator: ''
  }
  resolveVisible.value = true
}

/** 提交解决 */
function submitResolve() {
  proxy.$refs["resolveRef"].validate(valid => {
    if (valid) {
      resolveAlerts(resolveForm.value).then(() => {
        proxy.$modal.msgSuccess("解决成功")
        resolveVisible.value = false
        getList()
      }).catch(error => {
        console.error('解决告警失败:', error)
        proxy.$modal.msgError("解决告警失败，请检查后端服务是否正常")
      })
    }
  })
}



// 精简版移除忽略告警功能

/** 批量解决 */
function handleBatchResolve() {
  if (ids.value.length === 0) {
    proxy.$modal.msgError("请选择要解决的告警")
    return
  }
  resolveForm.value = {
    alertIds: ids.value.join(','),
    operator: ''
  }
  resolveVisible.value = true
}

/** 导出 */
function handleExport() {
  proxy.download('redfish/alert/export', {
    ...queryParams.value
  }, `alert_${new Date().getTime()}.xlsx`)
}

/** 刷新 */
function handleRefresh() {
  getList()
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
</style> 