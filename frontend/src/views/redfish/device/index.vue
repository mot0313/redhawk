<template>
  <div class="app-container">

    <el-row :gutter="10" class="mb20">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="Plus"
          @click="handleAdd"
          v-hasPermi="['redfish:device:add']"
        >新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="Edit"
          :disabled="single"
          @click="handleUpdate"
          v-hasPermi="['redfish:device:edit']"
        >修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="Delete"
          :disabled="multiple"
          @click="handleDelete"
          v-hasPermi="['redfish:device:remove']"
        >删除</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="info"
          plain
          icon="Connection"
          :disabled="single"
          @click="handleTestConnection"
          v-hasPermi="['redfish:device:test']"
        >测试连接</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="info"
          plain
          icon="Upload"
          @click="handleImport"
          v-hasPermi="['redfish:device:import']"
        >导入</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="warning"
          plain
          icon="Download"
          @click="handleExport"
          v-hasPermi="['redfish:device:export']"
        >导出</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="info"
          plain
          icon="Connection"
          @click="handleBatchCheckConnectivity"
          :disabled="multiple"
        >批量检测连通性</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="warning"
          plain
          icon="DataAnalysis"
          @click="handleGetConnectivityStats"
        >连通性统计</el-button>
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
      <el-form-item label="主机名" prop="hostname">
        <el-input
          v-model="queryParams.hostname"
          placeholder="请输入主机名"
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
      <el-form-item label="带外IP" prop="oobIp">
        <el-input
          v-model="queryParams.oobIp"
          placeholder="请输入带外IP"
          clearable
          style="width: 150px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="健康状态" prop="healthStatus">
        <el-select
          v-model="queryParams.healthStatus"
          placeholder="健康状态"
          clearable
          style="width: 100px"
        >
          <el-option label="正常" value="ok" />
          <el-option label="警告" value="warning" />
          <el-option label="未知" value="unknown" />
        </el-select>
      </el-form-item>
      <el-form-item label="监控状态" prop="monitorEnabled">
        <el-select
          v-model="queryParams.monitorEnabled"
          placeholder="监控状态"
          clearable
          style="width: 100px"
        >
          <el-option label="启用" :value="1" />
          <el-option label="禁用" :value="0" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>


    <el-table
      ref="deviceListRef"
      v-loading="loading"
      :data="deviceList"
      @selection-change="handleSelectionChange"
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
        label="主机名"
        align="center"
        key="hostname"
        prop="hostname"
        v-if="columns[1].visible"
        :show-overflow-tooltip="true"
      />
      <el-table-column
        label="业务IP"
        align="center"
        key="businessIp"
        prop="businessIp"
        v-if="columns[2].visible"
        width="140"
      />
      <el-table-column
        label="带外IP"
        align="center"
        key="oobIp"
        prop="oobIp"
        v-if="columns[3].visible"
        width="140"
      />
      <el-table-column
        label="机房位置"
        align="center"
        key="location"
        prop="location"
        v-if="columns[4].visible"
        :show-overflow-tooltip="true"
      />
      <el-table-column
        label="序列号"
        align="center"
        key="serialNumber"
        prop="serialNumber"
        v-if="columns[5].visible"
        :show-overflow-tooltip="true"
      />
      <el-table-column
        label="系统负责人"
        align="center"
        key="systemOwner"
        prop="systemOwner"
        v-if="columns[6].visible"
        width="100"
      />
      <el-table-column
        label="健康状态"
        align="center"
        key="healthStatus"
        prop="healthStatus"
        v-if="columns[7].visible"
        width="100"
      >
        <template #default="scope">
          <el-tag
            :type="getHealthStatusType(scope.row.healthStatus)"
            disable-transitions
          >
            {{ getHealthStatusText(scope.row.healthStatus) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column
        label="监控状态"
        align="center"
        key="monitorEnabled"
        prop="monitorEnabled"
        v-if="columns[8].visible"
        width="100"
      >
        <template #default="scope">
          <el-switch
            v-model="scope.row.monitorEnabled"
            :active-value="1"
            :inactive-value="0"
            @change="handleMonitorChange(scope.row)"
            v-hasPermi="['redfish:device:edit']"
            :disabled="loading"
          />
        </template>
      </el-table-column>
      <el-table-column
        label="最后检查时间"
        align="center"
        key="lastCheckTime"
        prop="lastCheckTime"
        v-if="columns[9].visible"
        width="150"
      >
        <template #default="scope">
          <span>{{ parseTime(scope.row.lastCheckTime) }}</span>
        </template>
      </el-table-column>
      <el-table-column
        label="操作"
        align="center"
        width="280"
        fixed="right"
        class-name="small-padding fixed-width"
      >
        <template #default="scope">
          <el-tooltip content="查看详情" placement="top">
            <el-button
              link
              type="primary"
              icon="View"
              @click="handleUpdate(scope.row)"
              v-hasPermi="['redfish:device:query']"
            ></el-button>
          </el-tooltip>
          <el-tooltip content="修改" placement="top">
            <el-button
              link
              type="primary"
              icon="Edit"
              @click="handleUpdate(scope.row)"
              v-hasPermi="['redfish:device:edit']"
            ></el-button>
          </el-tooltip>
          <el-tooltip content="Redfish连接测试" placement="top">
            <el-button
              link
              type="warning"
              icon="Link"
              @click="handleTestConnection(scope.row)"
              v-hasPermi="['redfish:device:test']"
            ></el-button>
          </el-tooltip>
          <el-tooltip content="业务IP连通性检测" placement="top">
            <el-button
              link
              type="info"
              icon="Connection"
              @click="handleCheckConnectivity(scope.row)"
              v-hasPermi="['redfish:device:test']"
            ></el-button>
          </el-tooltip>
          <el-tooltip content="删除" placement="top">
            <el-button
              link
              type="danger"
              icon="Delete"
              @click="handleDelete(scope.row)"
              v-hasPermi="['redfish:device:remove']"
            ></el-button>
          </el-tooltip>
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

    <!-- 添加或修改设备对话框 -->
    <el-dialog :title="title" v-model="open" width="920px" append-to-body>
      <el-form ref="deviceRef" :model="form" :rules="rules" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="11">
            <el-form-item label="主机名" prop="hostname">
              <el-input v-model="form.hostname" placeholder="请输入主机名" />
            </el-form-item>
          </el-col>
          <el-col :span="11">
            <el-form-item label="系统负责人" prop="systemOwner">
              <el-input v-model="form.systemOwner" placeholder="请输入系统负责人" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="11">
            <el-form-item label="业务IP" prop="businessIp">
              <el-input v-model="form.businessIp" placeholder="请输入业务IP地址" />
            </el-form-item>
          </el-col>
          <el-col :span="11">
            <el-form-item label="带外IP" prop="oobIp">
              <el-input v-model="form.oobIp" placeholder="请输入带外IP地址" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="11">
            <el-form-item label="带外端口" prop="oobPort">
              <el-input-number v-model="form.oobPort" :min="1" :max="65535" placeholder="443" />
            </el-form-item>
          </el-col>
          <el-col :span="11">
            <el-form-item label="机房位置" prop="location">
              <el-input v-model="form.location" placeholder="请输入机房位置" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="11">
            <el-form-item label="操作系统" prop="operatingSystem">
              <el-input v-model="form.operatingSystem" placeholder="请输入操作系统" />
            </el-form-item>
          </el-col>
          <el-col :span="11">
            <el-form-item label="序列号" prop="serialNumber">
              <el-input v-model="form.serialNumber" placeholder="请输入序列号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="11">
            <el-form-item label="设备型号" prop="model">
              <el-input v-model="form.model" placeholder="请输入设备型号" />
            </el-form-item>
          </el-col>
          <el-col :span="11">
            <el-form-item label="厂商" prop="manufacturer">
              <el-input v-model="form.manufacturer" placeholder="请输入厂商" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="11">
            <el-form-item label="技术系统" prop="technicalSystem">
              <el-input v-model="form.technicalSystem" placeholder="请输入技术系统" />
            </el-form-item>
          </el-col>
          <el-col :span="11">
            <el-form-item label="业务类型" prop="businessType">
              <el-select 
                v-model="form.businessType" 
                placeholder="请选择业务类型" 
                clearable 
                style="width: 100%"
              >
                <el-option
                  v-for="item in businessTypes"
                  :key="item.typeCode"
                  :label="item.typeName"
                  :value="item.typeCode"
                >
                  {{ item.typeName }}
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="11">
            <el-form-item label="Redfish用户名" prop="redfishUsername">
              <el-input v-model="form.redfishUsername" placeholder="请输入Redfish用户名" />
            </el-form-item>
          </el-col>
          <el-col :span="11">
            <el-form-item label="Redfish密码" prop="redfishPassword">
              <el-input v-model="form.redfishPassword" type="password" placeholder="请输入Redfish密码" show-password />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="11">
            <el-form-item label="启用监控" prop="monitorEnabled">
              <el-radio-group v-model="form.monitorEnabled">
                <el-radio :value="1">启用</el-radio>
                <el-radio :value="0">禁用</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitForm">确 定</el-button>
          <el-button @click="cancel">取 消</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 设备详情对话框 -->
    <el-dialog title="设备详情" v-model="detailOpen" width="900px" append-to-body>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="主机名">{{ detailForm.hostname }}</el-descriptions-item>
        <el-descriptions-item label="业务IP">{{ detailForm.businessIp || '未设置' }}</el-descriptions-item>
        <el-descriptions-item label="带外IP">{{ detailForm.oobIp }}</el-descriptions-item>
        <el-descriptions-item label="带外端口">{{ detailForm.oobPort }}</el-descriptions-item>
        <el-descriptions-item label="机房位置">{{ detailForm.location }}</el-descriptions-item>
        <el-descriptions-item label="操作系统">{{ detailForm.operatingSystem || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="序列号">{{ detailForm.serialNumber || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="设备型号">{{ detailForm.model || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="厂商">{{ detailForm.manufacturer || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="技术系统">{{ detailForm.technicalSystem || '未设置' }}</el-descriptions-item>
        <el-descriptions-item label="系统负责人">{{ detailForm.systemOwner || '未设置' }}</el-descriptions-item>
        <el-descriptions-item label="业务类型">{{ detailForm.businessType || '未设置' }}</el-descriptions-item>
        <el-descriptions-item label="Redfish用户名">{{ detailForm.redfishUsername || '未设置' }}</el-descriptions-item>
        <el-descriptions-item label="健康状态">
          <el-tag :type="getHealthStatusType(detailForm.healthStatus)">
            {{ getHealthStatusText(detailForm.healthStatus) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="监控状态">
          <el-tag :type="detailForm.monitorEnabled ? 'success' : 'danger'">
            {{ detailForm.monitorEnabled ? '启用' : '禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="最后检查时间">{{ parseTime(detailForm.lastCheckTime) || '未检查' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ parseTime(detailForm.createTime) }}</el-descriptions-item>
        <el-descriptions-item label="创建者">{{ detailForm.createBy || '系统' }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ parseTime(detailForm.updateTime) }}</el-descriptions-item>
        <el-descriptions-item label="更新者">{{ detailForm.updateBy || '系统' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ detailForm.remark || '无' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 设备导入对话框 -->
    <el-dialog :title="upload.title" v-model="upload.open" width="400px" append-to-body>
      <el-upload
        ref="uploadRef"
        :limit="1"
        accept=".xlsx, .xls"
        :headers="upload.headers"
        :action="upload.url + '?updateSupport=' + upload.updateSupport"
        :disabled="upload.isUploading"
        :on-progress="handleFileUploadProgress"
        :on-success="handleFileSuccess"
        :auto-upload="false"
        drag
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip text-center">
            <div class="el-upload__tip">
              <el-checkbox
                v-model="upload.updateSupport"
              />是否更新已经存在的设备数据
            </div>
            <span>仅允许导入xls、xlsx格式文件。</span>
            <el-link
              type="primary"
              :underline="false"
              style="font-size: 12px; vertical-align: baseline"
              @click="importTemplate"
              >下载模板</el-link
            >
          </div>
        </template>
      </el-upload>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitFileForm">确 定</el-button>
          <el-button @click="upload.open = false">取 消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="Device">
import { getCurrentInstance, onMounted, reactive, ref, toRefs } from 'vue'
import { listDevice, getDevice, delDevice, addDevice, updateDevice, testConnectionById, changeMonitorStatus } from "@/api/redfish/device";
import { getBusinessTypes } from "@/api/redfish/businessRule";
import { parseTime } from "@/utils/ruoyi";
import { getToken } from "@/utils/auth";
import { 
  checkDeviceConnectivity, 
  batchCheckConnectivity,
  getConnectivityStatistics 
} from '@/api/redfish/connectivity'

const { proxy } = getCurrentInstance();

const deviceList = ref([]);
const deviceListRef = ref(); // 添加表格ref
const businessTypes = ref([]);
const open = ref(false);
const detailOpen = ref(false);
const loading = ref(true);
const showSearch = ref(false);
const ids = ref([]);
const single = ref(true);
const multiple = ref(true);
const total = ref(0);
const title = ref("");

/*** 设备导入参数 */
const upload = reactive({
  // 是否显示弹出层（设备导入）
  open: false,
  // 弹出层标题（设备导入）
  title: "",
  // 是否禁用上传
  isUploading: false,
  // 是否更新已经存在的设备数据
  updateSupport: 0,
  // 设置上传的请求头部
  headers: { Authorization: "Bearer " + getToken() },
  // 上传的地址
  url: import.meta.env.VITE_APP_BASE_API + "/redfish/device/importData",
});

const data = reactive({
  form: {},
  detailForm: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    hostname: undefined,
    businessIp: undefined,
    oobIp: undefined,
    healthStatus: undefined,
    monitorEnabled: undefined
  },
  rules: {
    hostname: [{ required: true, message: '主机名不能为空', trigger: 'blur' }],
    businessIp: [{ required: true, message: '业务IP不能为空', trigger: 'blur' }],
    oobIp: [{ required: true, message: '带外IP不能为空', trigger: 'blur' }],
    businessType: [{ required: true, message: '业务类型不能为空', trigger: 'change' }]
  }
});

const { queryParams, form, detailForm, rules } = toRefs(data);

// 列显示控制
const columns = ref([
  { key: 0, label: `序号`, visible: true },
  { key: 1, label: `主机名`, visible: true },
  { key: 2, label: `业务IP`, visible: true },
  { key: 3, label: `带外IP`, visible: true },
  { key: 4, label: `机房位置`, visible: true },
  { key: 5, label: `序列号`, visible: true },
  { key: 6, label: `系统负责人`, visible: true },
  { key: 7, label: `健康状态`, visible: true },
  { key: 8, label: `监控状态`, visible: true },
  { key: 9, label: `最后检查时间`, visible: true }
]);

/** 查询设备列表 */
function getList() {
  loading.value = true;
  listDevice(queryParams.value).then(response => {
    console.log('设备列表响应:', response);
    if (response && response.rows) {
      deviceList.value = response.rows;
      total.value = response.total || 0;
    } else {
      console.error('响应数据格式错误:', response);
      deviceList.value = [];
      total.value = 0;
    }
    loading.value = false;
  }).catch(error => {
    console.error('获取设备列表失败:', error);
    loading.value = false;
    proxy.$modal.msgError('获取设备列表失败');
  });
}

/** 获取业务类型列表 */
function getBusinessTypeList() {
  return getBusinessTypes().then(response => {
    console.log('业务类型响应:', response);
    if (response && response.data) {
      businessTypes.value = response.data;
    } else {
      console.error('业务类型响应数据格式错误:', response);
      businessTypes.value = [];
    }
  }).catch(error => {
    console.error('获取业务类型列表失败:', error);
    proxy.$modal.msgError('获取业务类型列表失败');
  });
}

// 取消按钮
function cancel() {
  open.value = false;
  reset();
}

// 表单重置
function reset() {
  form.value = {
    deviceId: null,
    hostname: null,
    businessIp: null,
    oobIp: null,
    oobPort: 443,
    location: '',
    operatingSystem: null,
    serialNumber: null,
    model: null,
    manufacturer: null,
    technicalSystem: null,
    systemOwner: null,
    businessType: null,
    redfishUsername: null,
    redfishPassword: null,
    monitorEnabled: 1
  };
  proxy.resetForm("deviceRef");
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
  ids.value = selection.map(item => item.deviceId);
  single.value = selection.length != 1;
  multiple.value = !selection.length;
}

/** 新增按钮操作 */
function handleAdd() {
  reset();
  getBusinessTypeList();
  open.value = true;
  title.value = "添加设备";
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset();
  const deviceId = row.deviceId || ids.value;
  
  // 先获取业务类型列表，再获取设备数据
  getBusinessTypeList().then(() => {
    getDevice(deviceId, true).then(response => {
      // 使用response.data.device来获取设备数据
      form.value = response.data.device;
      open.value = true;
      title.value = "修改设备";
    });
  });
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["deviceRef"].validate(valid => {
    if (valid) {
      if (form.value.deviceId != null) {
        updateDevice(form.value).then(response => {
          proxy.$modal.msgSuccess("修改成功");
          open.value = false;
          getList();
        });
      } else {
        addDevice(form.value).then(response => {
          proxy.$modal.msgSuccess("新增成功");
          open.value = false;
          getList();
        });
      }
    }
  });
}

/** 删除按钮操作 */
function handleDelete(row) {
  const deviceIds = row.deviceId || ids.value;
  
  // 获取要删除的设备信息用于确认对话框
  let confirmMessage = '';
  if (row.deviceId) {
    // 单个删除
    confirmMessage = `是否确认删除业务IP为"${row.businessIp || '未设置'}"的设备？`;
  } else {
    // 批量删除
    const selectedDevices = deviceList.value.filter(device => ids.value.includes(device.deviceId));
    const businessIps = selectedDevices.map(device => device.businessIp || '未设置').join('、');
    confirmMessage = `是否确认删除业务IP为"${businessIps}"的设备？`;
  }
  
  proxy.$modal.confirm(confirmMessage).then(function() {
    return delDevice(deviceIds);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {});
}

/** 导出按钮操作 */
function handleExport() {
  proxy.download('redfish/device/export', {
    ...queryParams.value
  }, `device_${new Date().getTime()}.xlsx`)
}

/** 测试连接按钮操作 */
function handleTestConnection(row) {
  const deviceId = row.deviceId || ids.value[0];
  
  proxy.$modal.loading("正在测试连接...");
  testConnectionById(deviceId).then(response => {
    proxy.$modal.closeLoading();
    if (response.success) {
      proxy.$modal.msgSuccess("连接测试成功");
    } else {
      proxy.$modal.msgError("连接测试失败：" + response.message);
    }
  }).catch(() => {
    proxy.$modal.closeLoading();
    proxy.$modal.msgError("连接测试失败");
  });
}

/** 查看详情按钮操作 */
function handleDetail(row) {
  const deviceId = row.deviceId;
  getDevice(deviceId).then(response => {
    // 使用response.data.device来获取设备数据
    detailForm.value = response.data.device;
    detailOpen.value = true;
  });
}

/** 监控状态切换 */
function handleMonitorChange(row) {
  // 检查主机名是否存在，避免在数据加载过程中触发
  if (!row.hostname) {
    console.warn('主机名为空，忽略监控状态切换事件');
    return;
  }
  
  let text = row.monitorEnabled === 1 ? "启用" : "停用";
  proxy.$modal.confirm('确认要"' + text + '""' + row.hostname + '"的监控吗？').then(function() {
    return changeMonitorStatus(row.deviceId, row.monitorEnabled);
  }).then(() => {
    proxy.$modal.msgSuccess(text + "成功");
  }).catch(function() {
    row.monitorEnabled = row.monitorEnabled === 0 ? 1 : 0;
  });
}

/** 获取健康状态类型 */
function getHealthStatusType(status) {
  const statusMap = {
    'ok': 'success',
    'warning': 'warning', 
    'critical': 'warning',  // 简化分类：critical合并到warning
    'unknown': 'info'
  };
  return statusMap[status] || 'info';
}

/** 获取健康状态文本 */
function getHealthStatusText(status) {
  const statusMap = {
    'ok': '正常',
    'warning': '警告',
    'critical': '警告',  // 简化分类：critical显示为警告
    'unknown': '未知'
  };
  return statusMap[status] || '未知';
}

/** 导入按钮操作 */
function handleImport() {
  upload.title = "设备导入";
  upload.open = true;
}

/** 下载模板操作 */
function importTemplate() {
  proxy.download("redfish/device/importTemplate", {}, `设备导入模板_${new Date().getTime()}.xlsx`);
}

/** 文件上传中处理 */
function handleFileUploadProgress(event, file, fileList) {
  upload.isUploading = true;
}

/** 文件上传成功处理 */
function handleFileSuccess(response, file, fileList) {
  upload.open = false;
  upload.isUploading = false;
  proxy.$refs["uploadRef"].clearFiles();
  proxy.$alert("<div style='overflow: auto;overflow-x: hidden;max-height: 70vh;padding: 10px 20px 0;'>" + response.msg + "</div>", "导入结果", { dangerouslyUseHTMLString: true });
  getList();
}

/** 提交上传文件 */
function submitFileForm() {
  proxy.$refs["uploadRef"].submit();
}

// 检测单个设备连通性
function handleCheckConnectivity(row) {
  const loading = proxy.$modal.loading("正在检测设备连通性...")
  
  checkDeviceConnectivity(row.deviceId).then(response => {
    proxy.$modal.closeLoading()
    
    if (response.data.online) {
      proxy.$modal.msgSuccess(`设备 ${row.hostname} (${response.data.business_ip}) 连通性检测成功！

检测详情：
• Ping响应时间: ${response.data.ping?.response_time || 'N/A'}
• 检测耗时: ${response.data.check_duration_ms?.toFixed(1)}ms
• 检测时间: ${new Date(response.data.check_time).toLocaleString()}`)
    } else {
      let errorInfo = `设备 ${row.hostname} (${response.data.business_ip}) 连通性检测失败！
      
错误信息：
• Ping错误: ${response.data.ping?.error || 'N/A'}
• 检测耗时: ${response.data.check_duration_ms?.toFixed(1)}ms`

      // 显示端口检测结果（如果有）
      if (response.data.port_checks) {
        errorInfo += '\n\n端口检测结果：'
        Object.entries(response.data.port_checks).forEach(([portName, result]) => {
          const status = result.success ? '可达' : '不可达'
          errorInfo += `\n• ${portName}: ${status}`
        })
      }

      proxy.$modal.msgWarning(errorInfo)
    }
  }).catch(error => {
    proxy.$modal.closeLoading()
    proxy.$modal.msgError(`连通性检测失败: ${error.message}`)
  })
}

// 批量检测连通性
function handleBatchCheckConnectivity() {
  // 修复：使用表格ref获取选中的行
  const selectedRows = deviceListRef.value ? 
    deviceListRef.value.getSelectionRows() : 
    deviceList.value.filter(device => ids.value.includes(device.deviceId))
  
  if (selectedRows.length === 0) {
    proxy.$modal.msgWarning('请先选择要检测的设备')
    return
  }
  
  const deviceIds = selectedRows.map(row => row.deviceId)
  const loading = proxy.$modal.loading(`正在批量检测 ${selectedRows.length} 台设备的连通性...`)
  
  batchCheckConnectivity({ 
    deviceIds, 
    maxConcurrent: 20 
  }).then(response => {
    proxy.$modal.closeLoading()
    
    const result = response.data
    const onlineCount = result.online_devices
    const offlineCount = result.offline_devices
    const totalTime = result.check_duration_ms?.toFixed(1)
    
    // 构建详细结果
    let detailText = `批量连通性检测完成！
    
统计结果：
• 总设备数: ${result.total_devices}
• 在线设备: ${onlineCount}
• 离线设备: ${offlineCount}
• 检测耗时: ${totalTime}ms

设备详情：`

    result.details?.forEach((detail, index) => {
      const status = detail.online ? '在线' : '离线'
      const pingTime = detail.check_details?.ping?.response_time || 'N/A'
      detailText += `\n${index + 1}. ${detail.hostname}: ${status} (Ping: ${pingTime})`
    })
    
    proxy.$modal.alert(detailText, '批量检测结果')
    
    // 检测完成后刷新列表
    handleQuery()
  }).catch(error => {
    proxy.$modal.closeLoading()
    proxy.$modal.msgError(`批量检测失败: ${error.message}`)
  })
}

// 获取连通性统计
function handleGetConnectivityStats() {
  const loading = proxy.$modal.loading('正在获取设备连通性统计...')
  
  getConnectivityStatistics({ useCache: false }).then(response => {
    proxy.$modal.closeLoading()
    
    const result = response.data
    const onlineCount = result.online_devices
    const offlineCount = result.offline_devices
    const totalTime = result.check_duration_ms?.toFixed(1)
    
    proxy.$modal.alert(
      `设备连通性统计结果：
      
• 总设备数: ${result.total_devices}
• 在线设备: ${onlineCount}
• 离线设备: ${offlineCount}
• 检测耗时: ${totalTime}ms
• 检测时间: ${new Date(result.check_time).toLocaleString()}`,
      '连通性统计'
    )
  }).catch(error => {
    proxy.$modal.closeLoading()
    proxy.$modal.msgError(`获取统计失败: ${error.message}`)
  })
}

getList();
</script> 