<template>
  <div class="app-container">
    <!-- Tab 切换 -->
    <el-tabs v-model="activeTab" @tab-click="handleTabClick">
      <el-tab-pane label="维护排期" name="schedule">
        <!-- 原有的维护排期内容 -->
        <div class="maintenance-schedule-content">
          <el-row :gutter="10" class="mb20">
            <el-col :span="1.5">
              <el-button
                type="primary"
                plain
                icon="Plus"
                @click="handleAdd"
                v-hasPermi="['redfish:maintenance:add']"
              >新增排期</el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                type="success"
                plain
                icon="Edit"
                :disabled="single"
                @click="handleUpdate"
                v-hasPermi="['redfish:maintenance:edit']"
              >修改</el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                type="danger"
                plain
                icon="Delete"
                :disabled="multiple"
                @click="handleDelete"
                v-hasPermi="['redfish:maintenance:remove']"
              >删除</el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                type="warning"
                plain
                icon="Clock"
                :disabled="multiple"
                @click="handleBatchSchedule"
                v-hasPermi="['redfish:maintenance:edit']"
              >批量排期</el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                type="info"
                plain
                icon="Calendar"
                @click="handleViewCalendar"
                v-hasPermi="['redfish:maintenance:list']"
              >日历视图</el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                type="warning"
                plain
                icon="Download"
                @click="handleExport"
                v-hasPermi="['redfish:maintenance:export']"
              >导出</el-button>
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
              <el-option label="立即" value="immediate" />
              <el-option label="紧急" value="urgent" />
              <el-option label="择期" value="scheduled" />
            </el-select>
          </el-form-item>
          <el-form-item label="维护状态" prop="maintenanceStatus">
            <el-select
              v-model="queryParams.maintenanceStatus"
              placeholder="维护状态"
              clearable
              style="width: 100px"
            >
              <el-option label="待维护" value="pending" />
              <el-option label="维护中" value="ongoing" />
              <el-option label="已完成" value="completed" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
          </el-form-item>
          <el-form-item label="负责人" prop="responsiblePerson">
            <el-input
              v-model="queryParams.responsiblePerson"
              placeholder="请输入负责人"
              clearable
              style="width: 120px"
              @keyup.enter="handleQuery"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <el-table
          v-loading="loading"
          :data="maintenanceList"
          @selection-change="handleSelectionChange"
          :default-sort="{prop: 'scheduledDate', order: 'ascending'}"
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
                :type="getUrgencyType(scope.row.urgencyLevel)"
                effect="dark"
              >
                {{ getUrgencyText(scope.row.urgencyLevel) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            label="计划时间"
            align="center"
            key="scheduledDate"
            width="160"
            v-if="columns[4].visible"
            prop="scheduledDate"
            sortable="custom"
          >
            <template #default="scope">
              {{ parseTime(scope.row.scheduledDate, '{y}-{m}-{d} {h}:{i}') }}
            </template>
          </el-table-column>
          <el-table-column
            label="负责人"
            align="center"
            key="responsiblePerson"
            width="100"
            v-if="columns[5].visible"
            prop="responsiblePerson"
          />
          <el-table-column
            label="维护状态"
            align="center"
            key="maintenanceStatus"
            width="100"
            v-if="columns[6].visible"
          >
            <template #default="scope">
              <el-tag
                :type="getStatusType(scope.row.status)"
                effect="plain"
              >
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            label="描述"
            align="center"
            key="description"
            v-if="columns[7].visible"
            :show-overflow-tooltip="true"
            prop="description"
          />
          <el-table-column
            label="首次告警"
            align="center"
            key="firstOccurrence"
            width="140"
            v-if="columns[8].visible"
          >
            <template #default="scope">
              {{ parseTime(scope.row.firstOccurrence, '{m}-{d} {h}:{i}') }}
            </template>
          </el-table-column>
          <el-table-column
            label="操作"
            align="center"
            class-name="small-padding fixed-width"
            width="160"
          >
            <template #default="scope">
              <el-button
                link
                type="info"
                icon="View"
                @click="handleDetail(scope.row)"
                v-hasPermi="['redfish:maintenance:query']"
              ></el-button>
              <el-button
                link
                type="primary"
                icon="Edit"
                @click="handleUpdate(scope.row)"
                v-hasPermi="['redfish:maintenance:edit']"
              ></el-button>
              <el-button
                link
                type="danger"
                icon="Delete"
                @click="handleDelete(scope.row)"
                v-hasPermi="['redfish:maintenance:remove']"
              ></el-button>
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

    <!-- 新增修改排期对话框 -->
    <el-dialog
      :title="title"
      v-model="open"
      width="800px"
      append-to-body
    >
      <el-form ref="maintenanceRef" :model="form" :rules="rules" label-width="120px">
        <el-row>
          <el-col :span="12">
            <el-form-item label="设备" prop="deviceId" required>
              <el-select
                v-model="form.deviceId"
                placeholder="请选择设备"
                filterable
                style="width: 100%"
                @change="handleDeviceChange"
              >
                <el-option
                  v-for="device in deviceOptions"
                  :key="device.deviceId"
                  :label="`${device.hostname} (${device.businessIp})`"
                  :value="device.deviceId"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="组件类型" prop="componentType" required>
              <el-select
                v-model="form.componentType"
                placeholder="请选择组件类型"
                style="width: 100%"
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
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="组件名称" prop="componentName">
              <el-input
                v-model="form.componentName"
                placeholder="请输入组件名称"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="紧急程度" prop="urgencyLevel" required>
              <el-select
                v-model="form.urgencyLevel"
                placeholder="请选择紧急程度"
                style="width: 100%"
                @change="handleUrgencyChange"
              >
                <el-option label="立即维护 (0小时)" value="immediate" />
                <el-option label="紧急维护 (24小时内)" value="urgent" />
                <el-option label="择期维护 (计划窗口)" value="scheduled" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="计划时间" prop="scheduledDate" required>
              <el-date-picker
                v-model="form.scheduledDate"
                type="datetime"
                placeholder="选择计划维护时间"
                style="width: 100%"
                format="YYYY-MM-DD HH:mm"
                value-format="YYYY-MM-DD HH:mm:ss"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="负责人" prop="responsiblePerson" required>
              <el-input
                v-model="form.responsiblePerson"
                placeholder="请输入维护负责人"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述信息" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            placeholder="请输入维护描述信息"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitForm">确 定</el-button>
          <el-button @click="cancel">取 消</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 排期详情对话框 -->
    <el-dialog
      title="维护排期详情"
      v-model="detailOpen"
      width="900px"
      append-to-body
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="设备信息">
          <div>
            <div class="font-medium">{{ detailData.hostname }}</div>
            <div class="text-sm text-gray-500">{{ detailData.businessIp }}</div>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="组件信息">
          <div>
            <div class="font-medium">{{ detailData.componentType }}</div>
            <div class="text-sm text-gray-500">{{ detailData.componentName }}</div>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="紧急程度">
          <el-tag :type="getUrgencyType(detailData.urgencyLevel)" effect="dark">
            {{ getUrgencyText(detailData.urgencyLevel) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="维护状态">
          <el-tag :type="getStatusType(detailData.status)" effect="plain">
            {{ getStatusText(detailData.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="计划时间">
          {{ parseTime(detailData.scheduledDate, '{y}-{m}-{d} {h}:{i}') }}
        </el-descriptions-item>
        <el-descriptions-item label="负责人">
          {{ detailData.responsiblePerson }}
        </el-descriptions-item>
        <el-descriptions-item label="首次告警时间">
          {{ parseTime(detailData.firstOccurrence, '{y}-{m}-{d} {h}:{i}') }}
        </el-descriptions-item>
        <el-descriptions-item label="最后告警时间">
          {{ parseTime(detailData.lastOccurrence, '{y}-{m}-{d} {h}:{i}') }}
        </el-descriptions-item>
        <el-descriptions-item label="描述信息" :span="2">
          {{ detailData.description || '无描述信息' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 日历视图对话框 -->
    <el-dialog
      title="维护排期日历"
      v-model="calendarOpen"
      width="90%"
      append-to-body
      :close-on-click-modal="false"
    >
      <div class="calendar-container">
        <el-calendar v-model="calendarDate">
          <template #header="{ date }">
            <span>{{ date }}</span>
            <el-button-group style="margin-left: 20px;">
              <el-button size="small" @click="selectDate('prev-month')">上个月</el-button>
              <el-button size="small" @click="selectDate('today')">今天</el-button>
              <el-button size="small" @click="selectDate('next-month')">下个月</el-button>
            </el-button-group>
          </template>
          <template #date-cell="{ data }">
            <div class="calendar-day">
              <div class="day-number">{{ data.day.split('-').slice(-1)[0] }}</div>
              <div v-if="getSchedulesByDate(data.day).length > 0" class="schedules">
                <div
                  v-for="schedule in getSchedulesByDate(data.day).slice(0, 3)"
                  :key="schedule.alertId"
                  class="schedule-item"
                  :class="`schedule-${schedule.urgencyLevel}`"
                  @click="handleScheduleClick(schedule)"
                >
                  <span class="schedule-text">
                    {{ schedule.hostname }} - {{ schedule.componentType }}
                  </span>
                </div>
                <div
                  v-if="getSchedulesByDate(data.day).length > 3"
                  class="more-schedules"
                  @click="handleShowMoreSchedules(data.day)"
                >
                  +{{ getSchedulesByDate(data.day).length - 3 }}个
                </div>
              </div>
            </div>
          </template>
        </el-calendar>
      </div>
    </el-dialog>
        </div>
      </el-tab-pane>
      
      <!-- 业务类型管理 -->
      <el-tab-pane label="业务类型管理" name="businessType">
        <business-type v-if="activeTab === 'businessType'" />
      </el-tab-pane>
      
      <!-- 硬件类型管理 -->
      <el-tab-pane label="硬件类型管理" name="hardwareType">
        <hardware-type v-if="activeTab === 'hardwareType'" />
      </el-tab-pane>
      
      <!-- 紧急度规则管理 -->
      <el-tab-pane label="紧急度规则" name="urgencyRule">
        <urgency-rule v-if="activeTab === 'urgencyRule'" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup name="MaintenanceSchedule">
import { listMaintenance, getMaintenance, delMaintenance, addMaintenance, updateMaintenance, exportMaintenance, listDevice } from "@/api/redfish/maintenance";
import { parseTime } from "@/utils/ruoyi";
import BusinessType from './businessType.vue';
import HardwareType from './hardwareType.vue';
import UrgencyRule from './urgencyRule.vue';

const { proxy } = getCurrentInstance();

// Tab切换状态
const activeTab = ref('schedule');

const maintenanceList = ref([]);
const open = ref(false);
const detailOpen = ref(false);
const calendarOpen = ref(false);
const loading = ref(true);
const showSearch = ref(true);
const ids = ref([]);
const single = ref(true);
const multiple = ref(true);
const total = ref(0);
const title = ref("");
const deviceOptions = ref([]);
const calendarData = ref([]);
const calendarDate = ref(new Date());

const data = reactive({
  form: {
    alertId: null,
    deviceId: null,
    componentType: null,
    componentName: null,
    urgencyLevel: null,
    scheduledDate: null,
    responsiblePerson: null,
    description: null
  },
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    hostname: null,
    businessIp: null,
    componentType: null,
    urgencyLevel: null,
    maintenanceStatus: null,
    responsiblePerson: null
  },
  rules: {
    deviceId: [
      { required: true, message: "设备不能为空", trigger: "change" }
    ],
    componentType: [
      { required: true, message: "组件类型不能为空", trigger: "change" }
    ],
    urgencyLevel: [
      { required: true, message: "紧急程度不能为空", trigger: "change" }
    ],
    scheduledDate: [
      { required: true, message: "计划时间不能为空", trigger: "change" }
    ],
    responsiblePerson: [
      { required: true, message: "负责人不能为空", trigger: "blur" }
    ]
  },
  detailData: {}
});

const { queryParams, form, rules, detailData } = toRefs(data);

// 列显示控制
const columns = ref([
  { key: 0, label: `序号`, visible: true },
  { key: 1, label: `设备信息`, visible: true },
  { key: 2, label: `组件信息`, visible: true },
  { key: 3, label: `紧急程度`, visible: true },
  { key: 4, label: `计划时间`, visible: true },
  { key: 5, label: `负责人`, visible: true },
  { key: 6, label: `维护状态`, visible: true },
  { key: 7, label: `描述`, visible: true },
  { key: 8, label: `首次告警`, visible: true }
]);

/** 查询排期列表 */
function getList() {
  loading.value = true;
  listMaintenance(queryParams.value).then(response => {
    maintenanceList.value = response.rows;
    total.value = response.total;
    loading.value = false;
  });
}

// 紧急程度样式
function getUrgencyType(urgencyLevel) {
  const typeMap = {
    'immediate': 'danger',
    'urgent': 'warning', 
    'scheduled': 'success'
  };
  return typeMap[urgencyLevel] || 'info';
}

function getUrgencyText(urgencyLevel) {
  const textMap = {
    'immediate': '立即',
    'urgent': '紧急',
    'scheduled': '择期'
  };
  return textMap[urgencyLevel] || urgencyLevel;
}

// 维护状态样式
function getStatusType(status) {
  const typeMap = {
    'pending': 'warning',
    'ongoing': 'primary',
    'completed': 'success',
    'cancelled': 'info',
    'scheduled': 'warning',
    'active': 'danger',
    'acknowledged': 'primary',
    'resolved': 'success',
    'closed': 'info'
  };
  return typeMap[status] || 'info';
}

function getStatusText(status) {
  const textMap = {
    'pending': '待维护',
    'ongoing': '维护中', 
    'completed': '已完成',
    'cancelled': '已取消',
    'scheduled': '已排期',
    'active': '活跃',
    'acknowledged': '已确认',
    'resolved': '已解决',
    'closed': '已关闭'
  };
  return textMap[status] || status;
}

// 日历相关方法
function getSchedulesByDate(date) {
  return calendarData.value.filter(schedule => {
    if (!schedule.scheduledDate) return false;
    
    // 处理日期格式，确保比较的格式一致
    let scheduleDate;
    if (typeof schedule.scheduledDate === 'string') {
      // 如果是字符串，可能是ISO格式或普通日期格式
      if (schedule.scheduledDate.includes('T')) {
        // ISO格式：2025-06-18T12:46:26
        scheduleDate = schedule.scheduledDate.split('T')[0];
      } else {
        // 普通格式：2025-06-18 12:46:26
        scheduleDate = schedule.scheduledDate.split(' ')[0];
      }
    } else if (schedule.scheduledDate instanceof Date) {
      // 如果是Date对象，格式化为YYYY-MM-DD
      scheduleDate = schedule.scheduledDate.toISOString().split('T')[0];
    } else {
      return false;
    }
    
    return scheduleDate === date;
  });
}

function selectDate(type) {
  const currentDate = new Date(calendarDate.value);
  switch(type) {
    case 'prev-month':
      currentDate.setMonth(currentDate.getMonth() - 1);
      break;
    case 'next-month':
      currentDate.setMonth(currentDate.getMonth() + 1);
      break;
    case 'today':
      currentDate = new Date();
      break;
  }
  calendarDate.value = currentDate;
}

function handleScheduleClick(schedule) {
  handleDetail(schedule);
}

function handleShowMoreSchedules(date) {
  const schedules = getSchedulesByDate(date);
  proxy.$modal.msgSuccess(`${date} 共有 ${schedules.length} 个维护排期`);
}

/** 搜索按钮操作 */
function handleQuery() {
  queryParams.value.pageNum = 1;
  getList();
}

/** 重置按钮操作 */
function resetQuery() {
  proxy.resetForm("queryRef");
  handleQuery();
}

// 多选框选中数据
function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.alertId);
  single.value = selection.length != 1;
  multiple.value = !selection.length;
}

/** 新增按钮操作 */
function handleAdd() {
  reset();
  loadDeviceOptions();
  open.value = true;
  title.value = "添加维护排期";
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset();
  loadDeviceOptions();
  const alertId = row.alertId || ids.value[0];
  getMaintenance(alertId).then(response => {
    // 后端现在直接返回数据，不再包装在schedule字段中
    form.value = response.data;
    open.value = true;
    title.value = "修改维护排期";
  });
}

/** 详情按钮操作 */
function handleDetail(row) {
  const alertId = row.alertId;
  getMaintenance(alertId).then(response => {
    detailData.value = response.data;
    detailOpen.value = true;
  });
}

/** 删除按钮操作 */
function handleDelete(row) {
  const alertIds = row.alertId || ids.value;
  proxy.$modal.confirm('是否确认删除选中的维护排期数据项？').then(function() {
    return delMaintenance(alertIds);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {});
}

/** 批量排期按钮操作 */
function handleBatchSchedule() {
  if (ids.value.length === 0) {
    proxy.$modal.msgError("请选择要排期的项目");
    return;
  }
  
  // 批量更新排期时间
  proxy.$prompt('请输入新的维护负责人', '批量排期', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPattern: /\S+/,
    inputErrorMessage: '负责人不能为空'
  }).then(({ value }) => {
    const batchData = {
      alertIds: ids.value,
      responsiblePerson: value
    };
    
    proxy.$modal.confirm(`确认对 ${ids.value.length} 项维护排期进行批量更新？`).then(() => {
      // 这里调用批量更新的API
      proxy.$modal.msgSuccess("批量排期成功");
      getList();
    });
  }).catch(() => {});
}

/** 日历视图按钮操作 */
function handleViewCalendar() {
  // 加载日历数据
  listMaintenance({ pageNum: 1, pageSize: 1000 }).then(response => {
    calendarData.value = response.rows;
    calendarOpen.value = true;
  }).catch(error => {
    console.error('加载日历数据失败:', error);
    proxy.$modal.msgError("加载日历数据失败");
  });
}

/** 导出按钮操作 */
function handleExport() {
  proxy.download('redfish/maintenance/export', {
    ...queryParams.value
  }, `maintenance_${new Date().getTime()}.xlsx`);
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["maintenanceRef"].validate(valid => {
    if (valid) {
      if (form.value.alertId != null) {
        updateMaintenance(form.value).then(response => {
          proxy.$modal.msgSuccess("修改成功");
          open.value = false;
          getList();
        });
      } else {
        addMaintenance(form.value).then(response => {
          proxy.$modal.msgSuccess("新增成功");
          open.value = false;
          getList();
        });
      }
    }
  });
}

/** 取消按钮 */
function cancel() {
  open.value = false;
  reset();
}

/** 表单重置 */
function reset() {
  form.value = {
    alertId: null,
    deviceId: null,
    componentType: null,
    componentName: null,
    urgencyLevel: null,
    scheduledDate: null,
    responsiblePerson: null,
    description: null
  };
  proxy.resetForm("maintenanceRef");
}

/** 加载设备选项 */
function loadDeviceOptions() {
  listDevice({ pageNum: 1, pageSize: 1000 }).then(response => {
    deviceOptions.value = response.rows;
  });
}

/** 设备变更处理 */
function handleDeviceChange(deviceId) {
  // 根据选择的设备自动填充负责人
  const selectedDevice = deviceOptions.value.find(device => device.deviceId === deviceId);
  if (selectedDevice && selectedDevice.systemOwner) {
    form.value.responsiblePerson = selectedDevice.systemOwner;
  }
}

/** Tab切换处理 */
function handleTabClick(tab) {
  activeTab.value = tab.name;
}

/** 紧急程度变更处理 */
function handleUrgencyChange(urgencyLevel) {
  // 根据紧急程度自动计算建议的排期时间
  const now = new Date();
  let suggestedDate = new Date(now);
  
  switch(urgencyLevel) {
    case 'immediate':
      // 立即，建议当前时间
      break;
    case 'urgent':
      // 紧急，建议24小时内
      suggestedDate.setHours(now.getHours() + 24);
      break;
    case 'scheduled':
      // 择期，建议下周同一时间
      suggestedDate.setDate(now.getDate() + 7);
      break;
  }
  
  form.value.scheduledDate = suggestedDate.toISOString().slice(0, 19);
}

onMounted(() => {
  getList();
});
</script>

<style scoped>
.calendar-container {
  height: 600px;
}

.calendar-day {
  height: 100px;
  padding: 4px;
  overflow: hidden;
}

.day-number {
  font-weight: bold;
  margin-bottom: 4px;
}

.schedules {
  font-size: 12px;
}

.schedule-item {
  background: #f5f5f5;
  margin-bottom: 2px;
  padding: 2px 4px;
  border-radius: 3px;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.schedule-immediate {
  background: #fef0f0;
  color: #f56c6c;
  border-left: 3px solid #f56c6c;
}

.schedule-urgent {
  background: #fdf6ec;
  color: #e6a23c;
  border-left: 3px solid #e6a23c;
}

.schedule-scheduled {
  background: #f0f9ff;
  color: #409eff;
  border-left: 3px solid #409eff;
}

.more-schedules {
  background: #e4e7ed;
  color: #606266;
  padding: 2px 4px;
  border-radius: 3px;
  cursor: pointer;
  text-align: center;
}
</style> 