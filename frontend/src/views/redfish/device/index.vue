<template>
  <div class="app-container">

    <el-row :gutter="10" class="mb20">
      <el-col :span="1.5">
        <el-button-group>
          <el-button :type="viewMode === 'list' ? 'primary' : 'default'" icon="List"
            @click="viewMode = 'list'; handleViewModeChange()">列表视图</el-button>
          <el-button :type="viewMode === 'datacenter' ? 'primary' : 'default'" icon="OfficeBuilding"
            @click="viewMode = 'datacenter'; handleViewModeChange()">机房视图</el-button>
        </el-button-group>
      </el-col>
      <el-col :span="1.5">
        <el-button type="primary" plain icon="Plus" @click="handleAdd" v-hasPermi="['redfish:device:add']"
          v-show="viewMode === 'list'">新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="success" plain icon="Edit" :disabled="single" @click="handleUpdate"
          v-hasPermi="['redfish:device:edit']" v-show="viewMode === 'list'">修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="danger" plain icon="Delete" :disabled="multiple" @click="handleDelete"
          v-hasPermi="['redfish:device:remove']" v-show="viewMode === 'list'">删除</el-button>
      </el-col>

      <el-col :span="1.5">
        <el-button type="info" plain icon="Upload" @click="handleImport" v-hasPermi="['redfish:device:import']"
          v-show="viewMode === 'list'">导入</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="warning" plain icon="Download" @click="handleExport" v-hasPermi="['redfish:device:export']"
          v-show="viewMode === 'list'">导出</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList" :columns="columns"
        v-show="viewMode === 'list'"></right-toolbar>

      <el-col :span="1.5">
        <el-tooltip content="业务连通性测试" placement="top">
          <el-button circle icon="Connection" @click="handleBatchCheckConnectivity" :disabled="multiple"
            v-show="viewMode === 'list'"></el-button>
        </el-tooltip>
      </el-col>
      <el-col :span="1.5">
        <el-tooltip content="业务连通性统计" placement="top">
          <el-button circle icon="DataAnalysis" @click="handleGetConnectivityStats"
            v-show="viewMode === 'list'"></el-button>
        </el-tooltip>
      </el-col>

    </el-row>

    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch && viewMode === 'list'"
      label-width="68px">
      <el-form-item label="主机名" prop="hostname">
        <el-input v-model="queryParams.hostname" placeholder="请输入主机名" clearable style="width: 150px"
          @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="业务IP" prop="businessIp">
        <el-input v-model="queryParams.businessIp" placeholder="请输入业务IP" clearable style="width: 150px"
          @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="带外IP" prop="oobIp">
        <el-input v-model="queryParams.oobIp" placeholder="请输入带外IP" clearable style="width: 150px"
          @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="健康状态" prop="healthStatus">
        <el-select v-model="queryParams.healthStatus" placeholder="健康状态" clearable style="width: 100px">
          <el-option label="正常" value="ok" />
          <el-option label="警告" value="warning" />
          <el-option label="未知" value="unknown" />
        </el-select>
      </el-form-item>
      <el-form-item label="监控状态" prop="monitorEnabled">
        <el-select v-model="queryParams.monitorEnabled" placeholder="监控状态" clearable style="width: 100px">
          <el-option label="启用" :value="1" />
          <el-option label="禁用" :value="0" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>


    <el-table ref="deviceListRef" v-loading="loading" :data="deviceList" border
      @selection-change="handleSelectionChange" v-show="viewMode === 'list'">
      <el-table-column type="selection" width="50" align="center" />
      <el-table-column label="序号" align="center" key="index" width="50" v-if="columns[0].visible">
        <template #default="scope">
          {{ (queryParams.pageNum - 1) * queryParams.pageSize + scope.$index + 1 }}
        </template>
      </el-table-column>
      <el-table-column label="主机名" align="center" key="hostname" prop="hostname" v-if="columns[1].visible"
        :show-overflow-tooltip="true" />
      <el-table-column label="业务IP" align="center" key="businessIp" prop="businessIp" v-if="columns[2].visible"
        width="140" />
      <el-table-column label="带外IP" align="center" key="oobIp" prop="oobIp" v-if="columns[3].visible" width="140" />
      <el-table-column label="机房位置" align="center" key="location" prop="location" v-if="columns[4].visible">
        <template #default="scope">
          <div 
            class="copyable-cell" 
            @click="copyToClipboard(scope.row.location, '机房位置', $event)"
            :title="`点击复制机房位置: ${scope.row.location}`"
          >
            <span class="copyable-text">{{ scope.row.location }}</span>
            <el-icon class="copy-icon" size="12">
              <CopyDocument />
            </el-icon>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="序列号" align="center" key="serialNumber" prop="serialNumber" v-if="columns[5].visible">
        <template #default="scope">
          <div 
            class="copyable-cell" 
            @click="copyToClipboard(scope.row.serialNumber, '序列号', $event)"
            :title="`点击复制序列号: ${scope.row.serialNumber}`"
          >
            <span class="copyable-text">{{ scope.row.serialNumber || '未设置' }}</span>
            <el-icon class="copy-icon" size="12">
              <CopyDocument />
            </el-icon>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="系统负责人" align="center" key="systemOwner" prop="systemOwner" v-if="columns[6].visible"
        width="80" />
      <el-table-column label="健康状态" align="center" key="healthStatus" prop="healthStatus" v-if="columns[7].visible"
        width="80">
        <template #default="scope">
          <el-tag :type="getHealthStatusType(scope.row.healthStatus)" disable-transitions>
            {{ getHealthStatusText(scope.row.healthStatus) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="连通状态" align="center" key="connectivityStatus" v-if="columns[9].visible" width="80">
        <template #default="scope">
          <div class="connectivity-status">
            <!-- 连通性状态 -->
            <el-tag v-if="scope.row.connectivityResult"
              :type="scope.row.connectivityResult.online ? 'success' : 'danger'" size="small" class="connectivity-tag">
              <el-icon style="margin-right: 2px">
                <Check v-if="scope.row.connectivityResult.online" />
                <Close v-else />
              </el-icon>
              {{ scope.row.connectivityResult.online ? '在线' : '离线' }}
            </el-tag>
            <span v-else class="no-test">未检测</span>

            <!-- Ping响应时间 -->
            <div v-if="scope.row.connectivityResult?.check_details?.ping?.response_time"
              :class="['ping-time', getPingResponseClass(scope.row.connectivityResult.check_details.ping.response_time)]">
              {{ scope.row.connectivityResult.check_details.ping.response_time }}
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="监控状态" align="center" key="monitorEnabled" prop="monitorEnabled" v-if="columns[8].visible"
        width="80">
        <template #default="scope">
          <el-switch v-model="scope.row.monitorEnabled" :active-value="1" :inactive-value="0"
            @change="handleMonitorChange(scope.row)" v-hasPermi="['redfish:device:edit']" :disabled="loading" />
        </template>
      </el-table-column>
      <el-table-column label="最后检查时间" align="center" key="lastCheckTime" prop="lastCheckTime" v-if="columns[10].visible"
        width="110">
        <template #default="scope">
          <span>{{ parseTime(scope.row.lastCheckTime) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="180" fixed="right" class-name="small-padding fixed-width">
        <template #default="scope">
          <el-tooltip content="查看详情" placement="top">
            <el-button link type="primary" icon="View" @click="handleUpdate(scope.row)"
              v-hasPermi="['redfish:device:query']"></el-button>
          </el-tooltip>
          <el-tooltip content="修改" placement="top">
            <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)"
              v-hasPermi="['redfish:device:edit']"></el-button>
          </el-tooltip>
          <el-tooltip content="Redfish连接测试" placement="top">
            <el-button link type="warning" icon="Link" @click="handleTestConnection(scope.row)"
              v-hasPermi="['redfish:device:test']"></el-button>
          </el-tooltip>
          <el-tooltip content="业务IP连通性检测" placement="top">
            <el-button link type="info" icon="Connection" @click="handleCheckConnectivity(scope.row)"
              v-hasPermi="['redfish:device:test']"></el-button>
          </el-tooltip>
          <el-tooltip content="删除" placement="top">
            <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)"
              v-hasPermi="['redfish:device:remove']"></el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total > 0 && viewMode === 'list'" :total="total" v-model:page="queryParams.pageNum"
      v-model:limit="queryParams.pageSize" @pagination="getList" />

    <!-- 机房可视化视图 -->
    <div v-show="viewMode === 'datacenter'" class="datacenter-container">
      <div v-if="loading" class="datacenter-loading">
        <el-skeleton :rows="3" animated />
      </div>
      <div v-else>
        <!-- 面包屑导航 -->
        <el-breadcrumb separator=">" class="mb-4" v-if="currentView !== 'dataCenter'">
          <el-breadcrumb-item @click="backToDataCenter" class="breadcrumb-link">数据中心</el-breadcrumb-item>
          <el-breadcrumb-item v-if="selectedDataCenter" @click="backToRoom" class="breadcrumb-link">
            {{ getDataCenterName(selectedDataCenter) }}
          </el-breadcrumb-item>
          <el-breadcrumb-item v-if="selectedRoom" class="breadcrumb-current">
            {{ selectedRoom }}
          </el-breadcrumb-item>
        </el-breadcrumb>

        <!-- 数据中心总览 -->
        <div v-if="currentView === 'dataCenter'" class="datacenter-overview">
          <div class="overview-header">
            <el-alert title="机房可视化说明" description="此视图显示设备在数据中心的分布情况。绿色表示设备正常，黄色表示有警告，灰色表示未知状态。点击数据中心可查看详细机房分布。"
              type="info" :closable="false" show-icon class="mb-4" />
          </div>

          <el-row :gutter="20" class="datacenter-cards">
            <el-col :xl="6" :lg="8" :md="12" :sm="24" v-for="(dc, code) in dataCenterData" :key="code" class="mb-4">
              <el-card :body-style="{ padding: '24px' }" shadow="hover" class="datacenter-card-simple"
                :class="`datacenter-${code.toLowerCase()}`" @click="selectDataCenter(code)">
                <div class="card-header-simple">
                  <div class="title-section">
                    <el-icon size="28" class="datacenter-icon-simple">
                      <OfficeBuilding />
                    </el-icon>
                    <h3 class="datacenter-title-simple">{{ dc.name }}</h3>
                  </div>
                  <div class="health-indicator" :class="getDataCenterHealthClass(dc.healthStats)">
                    {{ getDataCenterHealthText(dc.healthStats) }}
                  </div>
                </div>

                <div class="stats-section">
                  <div class="stat-item-simple">
                    <div class="stat-value-simple">{{ dc.totalDevices }}</div>
                    <div class="stat-label-simple">设备总数</div>
                  </div>
                  <div class="stat-divider"></div>
                  <div class="stat-item-simple">
                    <div class="stat-value-simple">{{ dc.roomCount }}</div>
                    <div class="stat-label-simple">机房数量</div>
                  </div>
                </div>

                <div class="health-detail">
                  <div class="health-item-simple">
                    <span class="health-dot health-ok"></span>
                    <span class="health-text">正常 {{ dc.healthStats.ok || 0 }}</span>
                  </div>
                  <div class="health-item-simple">
                    <span class="health-dot health-warning"></span>
                    <span class="health-text">警告 {{ dc.healthStats.warning || 0 }}</span>
                  </div>
                  <div class="health-item-simple">
                    <span class="health-dot health-unknown"></span>
                    <span class="health-text">未知 {{ dc.healthStats.unknown || 0 }}</span>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 机房视图 -->
        <div v-if="currentView === 'room'" class="room-view">
          <div class="room-header">
            <h2>{{ getDataCenterName(selectedDataCenter) }} - 机房分布</h2>
          </div>

          <el-row :gutter="16" class="room-grid">
            <el-col :xl="6" :lg="8" :md="12" :sm="24" v-for="room in roomData" :key="room.code" class="mb-3">
              <el-card :body-style="{ padding: '16px' }" shadow="hover" class="room-card"
                :class="getRoomStatusClass(room)" @click="selectRoom(room.code)">
                <div class="room-info">
                  <h4 class="room-title">{{ room.code }}</h4>
                  <div class="room-stats">
                    <span class="device-count">{{ room.deviceCount }}台设备</span>
                    <span class="rack-count">{{ room.rackCount }}个机柜</span>
                  </div>
                </div>
                <div class="room-status" :class="getRoomHealthClass(room)">
                  {{ getRoomHealthText(room) }}
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 机柜视图 -->
        <div v-if="currentView === 'rack'" class="rack-view">
          <div class="rack-header">
            <h2>{{ selectedRoom }} - 机柜分布</h2>
          </div>

          <el-row :gutter="12" class="rack-grid">
            <el-col :xl="4" :lg="6" :md="8" :sm="12" v-for="rack in rackData" :key="rack.code" class="mb-3">
              <el-card :body-style="{ padding: '12px' }" shadow="hover" class="rack-card"
                :class="getRackStatusClass(rack)">
                <div class="rack-header-info">
                  <h5 class="rack-title">{{ rack.code }}</h5>
                  <el-tag size="small" :type="getRackOccupancyType(rack.occupancyRate)">
                    {{ rack.occupancyRate }}%
                  </el-tag>
                </div>

                <div class="rack-units">
                  <div class="rack-scale">
                    <div v-for="unit in getRackUnits(rack)" :key="unit.unitNumber" class="unit-slot" :class="[
                      unit.device ? `unit-occupied ${getDeviceHealthClass(unit.device)}` : 'unit-empty',
                      unit.isDeviceStart ? 'device-start' : '',
                      unit.isDeviceMiddle ? 'device-middle' : '',
                      'unit-clickable'
                    ]"
                      :title="unit.device ? `${unit.device.hostname} (${unit.device.uRange}) - 点击查看设备详情` : `${unit.unitNumber}U - 空闲，点击查看机柜详情`"
                      @click="handleUnitClick(unit, rack, $event)">
                      <div class="unit-number">{{ unit.unitNumber }}</div>
                      <div v-if="unit.isDeviceStart" class="unit-device-merged"
                        :style="{ height: (unit.deviceHeight * 13) + 'px' }">
                        <div class="device-name-merged">{{ unit.device.hostname }}</div>
                        <div class="device-range">{{ unit.device.uRange }}</div>
                      </div>
                      <div v-else-if="unit.isDeviceMiddle" class="unit-device-middle">
                        <!-- 设备占用的中间部分 -->
                      </div>
                      <div v-else class="unit-empty-space"></div>
                    </div>
                  </div>
                  <div v-if="rack.devices.length === 0" class="no-devices">
                    无设备
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 设备详情抽屉 -->
        <el-drawer v-model="deviceDrawerVisible" :title="`机柜 ${selectedRack?.code} - 设备详情`" direction="rtl"
          size="600px">
          <div v-if="selectedRack" class="device-details">
            <el-table :data="selectedRack.devices" style="width: 100%">
              <el-table-column prop="hostname" label="设备名称" />
              <el-table-column prop="businessIp" label="业务IP" />
              <el-table-column prop="uRange" label="U位" width="80" />
              <el-table-column prop="healthStatus" label="状态" width="100">
                <template #default="scope">
                  <el-tag :type="getHealthStatusType(scope.row.healthStatus)">
                    {{ getHealthStatusText(scope.row.healthStatus) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100">
                <template #default="scope">
                  <el-button link type="primary" @click="handleDetail(scope.row)" size="small">
                    详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-drawer>

        <!-- 设备信息弹窗 -->
        <el-dialog v-model="deviceInfoVisible" :title="`设备信息 - ${selectedDevice?.hostname || ''}`" width="500px"
          @close="selectedDevice = null">
          <div v-if="selectedDevice" class="device-info-content">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="主机名">
                {{ selectedDevice.hostname }}
              </el-descriptions-item>
              <el-descriptions-item label="业务IP">
                {{ selectedDevice.businessIp }}
              </el-descriptions-item>
              <el-descriptions-item label="带外IP">
                {{ selectedDevice.oobIp }}
              </el-descriptions-item>
              <el-descriptions-item label="U位范围">
                {{ selectedDevice.uRange }}
              </el-descriptions-item>
              <el-descriptions-item label="机房位置">
                <div 
                  class="copyable-cell detail-copyable" 
                  @click="copyToClipboard(selectedDevice.location, '机房位置', $event)"
                  :title="`点击复制机房位置: ${selectedDevice.location}`"
                >
                  <span>{{ selectedDevice.location }}</span>
                  <el-icon class="copy-icon" size="12">
                    <CopyDocument />
                  </el-icon>
                </div>
              </el-descriptions-item>
              <el-descriptions-item label="健康状态">
                <el-tag :type="getHealthStatusType(selectedDevice.healthStatus)">
                  {{ getHealthStatusText(selectedDevice.healthStatus) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="系统负责人">
                {{ selectedDevice.systemOwner || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="操作系统">
                {{ selectedDevice.operatingSystem || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="设备型号">
                {{ selectedDevice.model || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="厂商">
                {{ selectedDevice.manufacturer || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="序列号">
                <div 
                  class="copyable-cell detail-copyable" 
                  @click="copyToClipboard(selectedDevice.serialNumber, '序列号', $event)"
                  :title="`点击复制序列号: ${selectedDevice.serialNumber}`"
                >
                  <span>{{ selectedDevice.serialNumber || '-' }}</span>
                  <el-icon class="copy-icon" size="12">
                    <CopyDocument />
                  </el-icon>
                </div>
              </el-descriptions-item>
              <el-descriptions-item label="技术系统">
                {{ selectedDevice.technicalSystem || '-' }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-dialog>
      </div>
    </div>

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
              <el-select v-model="form.businessType" placeholder="请选择业务类型" clearable style="width: 100%">
                <el-option v-for="item in businessTypes" :key="item.typeCode" :label="item.typeName"
                  :value="item.typeCode">
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
        <el-descriptions-item label="机房位置">
          <div 
            class="copyable-cell detail-copyable" 
            @click="copyToClipboard(detailForm.location, '机房位置', $event)"
            :title="`点击复制机房位置: ${detailForm.location}`"
          >
            <span>{{ detailForm.location }}</span>
            <el-icon class="copy-icon" size="12">
              <CopyDocument />
            </el-icon>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="操作系统">{{ detailForm.operatingSystem || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="序列号">
          <div 
            class="copyable-cell detail-copyable" 
            @click="copyToClipboard(detailForm.serialNumber, '序列号', $event)"
            :title="`点击复制序列号: ${detailForm.serialNumber}`"
          >
            <span>{{ detailForm.serialNumber || '未知' }}</span>
            <el-icon class="copy-icon" size="12">
              <CopyDocument />
            </el-icon>
          </div>
        </el-descriptions-item>
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
      <el-upload ref="uploadRef" :limit="1" accept=".xlsx, .xls" :headers="upload.headers"
        :action="upload.url + '?updateSupport=' + upload.updateSupport" :disabled="upload.isUploading"
        :on-progress="handleFileUploadProgress" :on-success="handleFileSuccess" :auto-upload="false" drag>
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip text-center">
            <div class="el-upload__tip">
              <el-checkbox v-model="upload.updateSupport" />是否更新已经存在的设备数据
            </div>
            <span>仅允许导入xls、xlsx格式文件。</span>
            <el-link type="primary" :underline="false" style="font-size: 12px; vertical-align: baseline"
              @click="importTemplate">下载模板</el-link>
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

    <!-- 连通性统计对话框 -->
    <el-dialog title="业务连通性统计" v-model="connectivityStatsVisible" width="900px" append-to-body>
      <div class="connectivity-stats-container">
        <!-- 整体概览 -->
        <div class="stats-overview">
          <div class="overview-card">
            <div class="card-content">
              <div class="stats-header">
                <el-icon size="24" color="#1F9E91">
                  <Monitor />
                </el-icon>
                <h3>连通性概览</h3>
              </div>

              <!-- 环形进度条 -->
              <div class="circular-progress">
                <el-progress type="circle" :percentage="connectivityStatsData.onlineRate" :width="120" :stroke-width="8"
                  :color="getProgressColor(connectivityStatsData.onlineRate)">
                  <template #default="{ percentage }">
                    <span class="progress-text">
                      <div class="percentage">{{ percentage }}%</div>
                      <div class="label">在线率</div>
                    </span>
                  </template>
                </el-progress>
              </div>
            </div>
          </div>
        </div>

        <!-- 详细统计 -->
        <div class="stats-details">
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="stat-card total">
                <div class="stat-icon">
                  <el-icon size="20">
                    <Cpu />
                  </el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ connectivityStatsData.totalDevices }}</div>
                  <div class="stat-label">总设备数</div>
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-card online">
                <div class="stat-icon">
                  <el-icon size="20">
                    <Check />
                  </el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ connectivityStatsData.onlineDevices }}</div>
                  <div class="stat-label">在线设备</div>
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-card offline">
                <div class="stat-icon">
                  <el-icon size="20">
                    <Close />
                  </el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ connectivityStatsData.offlineDevices }}</div>
                  <div class="stat-label">离线设备</div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 检测信息 -->
        <div class="check-info">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="info-item">
                <el-icon color="#909399">
                  <Timer />
                </el-icon>
                <div class="info-content">
                  <div class="info-label">检测耗时</div>
                  <div class="info-value">{{ connectivityStatsData.checkDuration }}ms</div>
                </div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="info-item">
                <el-icon color="#909399">
                  <Clock />
                </el-icon>
                <div class="info-content">
                  <div class="info-label">检测时间</div>
                  <div class="info-value">{{ connectivityStatsData.checkTime }}</div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 状态分析 -->
        <div class="status-analysis">
          <h4>状态分析</h4>
          <div class="analysis-content">
            <div class="analysis-item" v-if="connectivityStatsData.onlineRate >= 95">
              <el-tag type="success" size="small">
                <el-icon>
                  <SuccessFilled />
                </el-icon>
                优秀
              </el-tag>
              <span>网络连通性良好，{{ connectivityStatsData.onlineRate }}% 设备在线</span>
            </div>
            <div class="analysis-item" v-else-if="connectivityStatsData.onlineRate >= 80">
              <el-tag type="warning" size="small">
                <el-icon>
                  <WarningFilled />
                </el-icon>
                良好
              </el-tag>
              <span>网络连通性较好，但有 {{ connectivityStatsData.offlineDevices }} 台设备离线</span>
            </div>
            <div class="analysis-item" v-else>
              <el-tag type="danger" size="small">
                <el-icon>
                  <CircleCloseFilled />
                </el-icon>
                需要关注
              </el-tag>
              <span>{{ connectivityStatsData.offlineDevices }} 台设备离线，建议检查网络状况</span>
            </div>
          </div>
        </div>

        <!-- 离线设备详情 -->
        <div v-if="connectivityStatsData.offlineDevicesList.length > 0" class="offline-devices-section">
          <div class="section-header">
            <h4>
              <el-icon color="#f56c6c">
                <Warning />
              </el-icon>
              离线设备详情 ({{ connectivityStatsData.offlineDevicesList.length }} 台)
            </h4>
          </div>

                     <el-table :data="connectivityStatsData.offlineDevicesList" style="width: 100%" size="small"
             :header-cell-style="{ background: '#fef0f0', color: '#f56c6c' }" max-height="300">
             <el-table-column type="index" label="序号" width="60" align="center" />
             <el-table-column prop="hostname" label="主机名" min-width="120">
               <template #default="scope">
                 <div 
                   class="copyable-cell offline-copyable" 
                   @click="copyToClipboard(scope.row.hostname, '主机名', $event)"
                   :title="`点击复制主机名: ${scope.row.hostname}`"
                 >
                   <span class="hostname-text">{{ scope.row.hostname }}</span>
                   <el-icon class="copy-icon" size="10">
                     <CopyDocument />
                   </el-icon>
                 </div>
               </template>
             </el-table-column>
             <el-table-column prop="businessIp" label="业务IP" width="140">
               <template #default="scope">
                 <div 
                   v-if="scope.row.businessIp !== '未设置'"
                   class="copyable-cell offline-copyable" 
                   @click="copyToClipboard(scope.row.businessIp, '业务IP', $event)"
                   :title="`点击复制业务IP: ${scope.row.businessIp}`"
                 >
                   <el-tag type="info" size="small">
                     {{ scope.row.businessIp }}
                   </el-tag>
                   <el-icon class="copy-icon" size="10">
                     <CopyDocument />
                   </el-icon>
                 </div>
                 <span v-else class="no-ip">{{ scope.row.businessIp }}</span>
               </template>
             </el-table-column>
            <el-table-column prop="location" label="机房位置" width="120">
              <template #default="scope">
                <span class="location-text">{{ scope.row.location }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="errorMessage" label="故障原因" min-width="150">
              <template #default="scope">
                <el-tooltip :content="scope.row.errorMessage" placement="top"
                  :disabled="scope.row.errorMessage.length < 20">
                  <span class="error-message">{{ scope.row.errorMessage }}</span>
                </el-tooltip>
              </template>
            </el-table-column>
          </el-table>

          <div class="offline-summary">
            <el-alert :title="`共发现 ${connectivityStatsData.offlineDevicesList.length} 台设备离线`" type="error"
              :description="`建议运维人员优先检查这些设备的网络连接状态和业务服务运行情况`" :closable="false" show-icon />
          </div>
        </div>
      </div>
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
import { ElMessageBox } from "element-plus";

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

// 机房可视化相关状态
const viewMode = ref('list') // 'list' 或 'datacenter'
const currentView = ref('dataCenter') // 'dataCenter' 或 'room' 或 'rack'
const selectedDataCenter = ref('')
const selectedRoom = ref('')
const selectedRack = ref(null)
const deviceDrawerVisible = ref(false)
const selectedDevice = ref(null)
const deviceInfoVisible = ref(false)

// 连通性统计对话框
const connectivityStatsVisible = ref(false)
const connectivityStatsData = ref({
  totalDevices: 0,
  onlineDevices: 0,
  offlineDevices: 0,
  checkDuration: 0,
  checkTime: '',
  onlineRate: 0,
  offlineDevicesList: []  // 离线设备详细列表
})



// 数据中心数据
const dataCenterData = ref({})
const roomData = ref([])
const rackData = ref([])

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
  { key: 9, label: `连通状态`, visible: true },
  { key: 10, label: `最后检查时间`, visible: true }
]);

/** 查询设备列表 */
function getList() {
  loading.value = true;
  listDevice(queryParams.value).then(response => {
    console.log('设备列表响应:', response);
    // 使用 model_content 响应格式，数据直接在响应根级别
    if (response && response.rows) {
      deviceList.value = response.rows;
      total.value = response.total || 0;

      // 如果当前在机房视图模式，重新加载机房数据
      if (viewMode.value === 'datacenter') {
        loadDataCenterData();
      }
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
  let mainMessage = '';
  if (row.deviceId) {
    // 单个删除
    mainMessage = `是否确认删除业务IP为"${row.businessIp || '未设置'}"的设备？`;
  } else {
    // 批量删除
    const selectedDevices = deviceList.value.filter(device => ids.value.includes(device.deviceId));
    const businessIps = selectedDevices.map(device => device.businessIp || '未设置').join('、');
    mainMessage = `是否确认删除业务IP为"${businessIps}"的设备？`;
  }

  const noteMessage = "注意：删除设备将同时删除该设备的告警信息（不影响历史告警统计数据）。";

  const confirmMessageHTML = `
    <div>
      <p style="margin-bottom: 10px;">${mainMessage}</p>
      <div style="background-color: #fdf6ec; border-left: 5px solid #e6a23c; padding: 8px 15px;">
        <p style="margin: 0; color: #606266;">${noteMessage}</p>
      </div>
    </div>`;

  ElMessageBox.confirm(
    confirmMessageHTML,
    "确认删除",
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(function () {
    return delDevice(deviceIds);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => { });
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
  proxy.$modal.confirm('确认要"' + text + '""' + row.hostname + '"的监控吗？').then(function () {
    return changeMonitorStatus(row.deviceId, row.monitorEnabled);
  }).then(() => {
    proxy.$modal.msgSuccess(text + "成功");
  }).catch(function () {
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

// 更新设备列表中的连通性状态
function updateDeviceListConnectivity(result) {
  if (!result.details) return

  // 创建设备ID到连通性结果的映射
  const connectivityMap = {}
  result.details.forEach(detail => {
    // 尝试多种可能的设备ID字段名
    const deviceId = detail.device_id || detail.deviceId || detail.id
    if (deviceId) {
      connectivityMap[deviceId] = detail
    }
  })

  // 更新设备列表中的连通性结果
  deviceList.value.forEach((device, index) => {
    if (connectivityMap[device.deviceId]) {
      // 使用Vue的响应式更新方式，确保触发视图更新
      const connectivityResult = { ...connectivityMap[device.deviceId] }
      deviceList.value[index].connectivityResult = connectivityResult
    }
  })
}

// 更新单个设备的连通性状态
function updateSingleDeviceConnectivity(deviceId, connectivityResult) {
  const device = deviceList.value.find(d => d.deviceId === deviceId)
  if (device) {
    // 使用Vue的响应式更新方式
    device.connectivityResult = { ...connectivityResult }
  }
}

// 获取Ping响应时间的样式类
function getPingResponseClass(responseTime) {
  if (!responseTime || responseTime === 'N/A') return 'ping-unknown'

  const time = parseFloat(responseTime.replace('ms', ''))
  if (time <= 10) return 'ping-excellent'
  if (time <= 50) return 'ping-good'
  if (time <= 100) return 'ping-fair'
  return 'ping-poor'
}

// 获取进度条颜色
function getProgressColor(percentage) {
  if (percentage >= 95) return '#67c23a'      // 绿色 - 优秀
  if (percentage >= 80) return '#e6a23c'      // 橙色 - 良好
  if (percentage >= 60) return '#f56c6c'      // 红色 - 需要关注
  return '#909399'                            // 灰色 - 很差
}

// 复制到剪贴板功能
async function copyToClipboard(text, fieldName, event) {
  if (!text) {
    proxy.$modal.msgWarning(`${fieldName}为空，无法复制`)
    return
  }

  const targetElement = event?.currentTarget

  try {
    // 使用现代浏览器的 Clipboard API
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text)
    } else {
      // 回退到传统方法
      const textArea = document.createElement('textarea')
      textArea.value = text
      textArea.style.position = 'fixed'
      textArea.style.left = '-999999px'
      textArea.style.top = '-999999px'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      document.execCommand('copy')
      textArea.remove()
    }
    
    // 添加成功视觉反馈
    if (targetElement) {
      targetElement.classList.add('copy-success')
      setTimeout(() => {
        targetElement.classList.remove('copy-success')
      }, 1000)
    }
    
    proxy.$modal.msgSuccess(`${fieldName}已复制: ${text}`)
  } catch (error) {
    console.error('复制失败:', error)
    proxy.$modal.msgError(`复制${fieldName}失败，请手动复制`)
  }
}

// 检测单个设备连通性
function handleCheckConnectivity(row) {
  const loading = proxy.$modal.loading("正在检测设备连通性...")

  checkDeviceConnectivity(row.deviceId).then(response => {
    proxy.$modal.closeLoading()
    
    // 使用 model_content 响应格式，数据直接在响应根级别
    updateSingleDeviceConnectivity(row.deviceId, response)

    const status = response.online ? '在线' : '离线'
    // 根据实际响应数据结构访问字段
    const pingTime = response.ping?.response_time || 'N/A'
    const duration = response.checkDurationMs || 0

    if (response.online) {
      proxy.$modal.msgSuccess(`设备 ${row.hostname} (${response.businessIp}) 
      
连通性检测结果: ${status}
Ping响应时间: ${pingTime}
检测耗时: ${duration.toFixed(1)}ms`)
    } else {
      proxy.$modal.msgWarning(`设备 ${row.hostname} (${response.businessIp}) 
      
连通性检测结果: ${status}
错误信息: ${response.ping?.error || response.error || '无详细错误信息'}
检测耗时: ${duration.toFixed(1)}ms`)
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

    // 使用 model_content 响应格式，数据直接在响应根级别
    const result = response
    const onlineCount = result.onlineDevices || result.online_devices
    const offlineCount = result.offlineDevices || result.offline_devices
    const totalTime = (result.checkDurationMs || result.check_duration_ms || 0).toFixed(1)

    // 将连通性检测结果更新到设备列表中
    updateDeviceListConnectivity(result)

    // 显示简要提示信息
    proxy.$modal.msgSuccess(`批量连通性检测完成！
    
在线设备: ${onlineCount}台  |  离线设备: ${offlineCount}台  |  检测耗时: ${totalTime}ms`)

    // 注意：不需要刷新列表，因为我们已经更新了前端状态
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

    // 当使用model_content时，数据在响应的根级别，而不是data字段
    const result = response
    const onlineCount = result.onlineDevices || 0
    const offlineCount = result.offlineDevices || 0
    const totalDevices = result.totalDevices || 0
    const onlineRate = totalDevices > 0 ? Math.round((onlineCount / totalDevices) * 100) : 0

    // 提取离线设备详细信息
    const offlineDevicesList = (result.details || []).filter(device => !device.online).map(device => ({
      deviceId: device.deviceId,
      hostname: device.hostname,
      businessIp: device.businessIp || '未设置',
      location: device.location || '未知',
      errorMessage: device.checkDetails?.error || device.checkDetails?.ping?.error || '连接超时'
    }))

    // 更新统计数据
    connectivityStatsData.value = {
      totalDevices,
      onlineDevices: onlineCount,
      offlineDevices: offlineCount,
      checkDuration: result.checkDurationMs?.toFixed(1) || 0,
      checkTime: result.checkTime ? new Date(result.checkTime).toLocaleString() : '未知',
      onlineRate,
      offlineDevicesList
    }

    // 显示统计对话框
    connectivityStatsVisible.value = true
  }).catch(error => {
    proxy.$modal.closeLoading()
    proxy.$modal.msgError(`获取统计失败: ${error.message}`)
  })
}

/** ================ 机房可视化相关函数 ================ */

/** 位置解析工具函数 */
function parseLocation(location) {
  if (!location) return null

  // 解析 "XW_B1B04_21-24" 格式
  const regex = /^([A-Z]{2})_([A-Z]+\d+)([A-Z]+\d+)_(\d+)-(\d+)$/
  const match = location.match(regex)

  if (match) {
    return {
      dataCenter: match[1],        // XW
      room: match[2],              // B1  
      rack: match[3],              // B04
      startU: parseInt(match[4]),  // 21
      endU: parseInt(match[5]),    // 24
      uRange: `${match[4]}-${match[5]}U`
    }
  }
  return null
}

/** 获取数据中心名称 */
function getDataCenterName(code) {
  const dataCenterMap = {
    'XW': '西五环',
    'YJ': '翌景',
    'YZ': '亦庄'
  }
  return dataCenterMap[code] || code
}

/** 处理视图模式变化 */
function handleViewModeChange() {
  if (viewMode.value === 'datacenter') {
    currentView.value = 'dataCenter'
    loadDataCenterData()
  } else {
    // 重置机房视图状态
    currentView.value = 'dataCenter'
    selectedDataCenter.value = ''
    selectedRoom.value = ''
    selectedRack.value = null
    deviceDrawerVisible.value = false
  }
}

/** 加载数据中心数据 */
function loadDataCenterData() {
  // 解析所有设备的位置信息
  const parsedDevices = deviceList.value.map(device => ({
    ...device,
    locationInfo: parseLocation(device.location)
  })).filter(device => device.locationInfo) // 过滤无效位置

  // 按数据中心分组统计
  const dcStats = {}

  parsedDevices.forEach(device => {
    const dc = device.locationInfo.dataCenter
    if (!dcStats[dc]) {
      dcStats[dc] = {
        name: getDataCenterName(dc),
        totalDevices: 0,
        roomCount: new Set(),
        healthStats: { ok: 0, warning: 0, unknown: 0 }
      }
    }

    dcStats[dc].totalDevices++
    dcStats[dc].roomCount.add(device.locationInfo.room)

    // 统计健康状态
    const healthStatus = device.healthStatus || 'unknown'
    if (dcStats[dc].healthStats[healthStatus] !== undefined) {
      dcStats[dc].healthStats[healthStatus]++
    } else {
      dcStats[dc].healthStats.unknown++
    }
  })

  // 转换roomCount为数字
  Object.keys(dcStats).forEach(dc => {
    dcStats[dc].roomCount = dcStats[dc].roomCount.size
  })

  dataCenterData.value = dcStats
}

/** 选择数据中心 */
function selectDataCenter(dcCode) {
  selectedDataCenter.value = dcCode
  currentView.value = 'room'
  loadRoomData(dcCode)
}

/** 加载机房数据 */
function loadRoomData(dcCode) {
  const parsedDevices = deviceList.value.map(device => ({
    ...device,
    locationInfo: parseLocation(device.location)
  })).filter(device =>
    device.locationInfo && device.locationInfo.dataCenter === dcCode
  )

  // 按机房分组统计
  const roomStats = {}

  parsedDevices.forEach(device => {
    const room = device.locationInfo.room
    if (!roomStats[room]) {
      roomStats[room] = {
        code: room,
        deviceCount: 0,
        rackCount: new Set(),
        healthStats: { ok: 0, warning: 0, unknown: 0 }
      }
    }

    roomStats[room].deviceCount++
    roomStats[room].rackCount.add(device.locationInfo.rack)

    // 统计健康状态
    const healthStatus = device.healthStatus || 'unknown'
    if (roomStats[room].healthStats[healthStatus] !== undefined) {
      roomStats[room].healthStats[healthStatus]++
    } else {
      roomStats[room].healthStats.unknown++
    }
  })

  // 转换为数组并处理rackCount
  roomData.value = Object.values(roomStats).map(room => ({
    ...room,
    rackCount: room.rackCount.size
  }))
}

/** 选择机房 */
function selectRoom(roomCode) {
  selectedRoom.value = roomCode
  currentView.value = 'rack'
  loadRackData(selectedDataCenter.value, roomCode)
}

/** 加载机柜数据 */
function loadRackData(dcCode, roomCode) {
  const parsedDevices = deviceList.value.map(device => ({
    ...device,
    locationInfo: parseLocation(device.location)
  })).filter(device =>
    device.locationInfo &&
    device.locationInfo.dataCenter === dcCode &&
    device.locationInfo.room === roomCode
  )

  // 按机柜分组
  const rackStats = {}

  parsedDevices.forEach(device => {
    const rack = device.locationInfo.rack
    if (!rackStats[rack]) {
      rackStats[rack] = {
        code: rack,
        devices: [],
        occupancyRate: 0
      }
    }

    rackStats[rack].devices.push({
      ...device,
      uRange: device.locationInfo.uRange
    })
  })

  // 计算占用率（假设每个机柜42U）
  Object.values(rackStats).forEach(rack => {
    const totalUUsed = rack.devices.reduce((sum, device) => {
      const uRange = device.locationInfo
      return sum + (uRange.endU - uRange.startU + 1)
    }, 0)
    rack.occupancyRate = Math.round((totalUUsed / 42) * 100)
  })

  rackData.value = Object.values(rackStats)
}

/** 返回数据中心视图 */
function backToDataCenter() {
  currentView.value = 'dataCenter'
  selectedDataCenter.value = ''
  selectedRoom.value = ''
  selectedRack.value = null
  deviceDrawerVisible.value = false
}

/** 返回机房视图 */
function backToRoom() {
  currentView.value = 'room'
  selectedRoom.value = ''
  selectedRack.value = null
  deviceDrawerVisible.value = false
}

/** 显示机柜详情 */
function showRackDetails(rack) {
  selectedRack.value = rack
  deviceDrawerVisible.value = true
}

/** 显示设备信息 */
function showDeviceInfo(device) {
  selectedDevice.value = device
  deviceInfoVisible.value = true
}

/** 获取数据中心健康状态样式类 */
function getDataCenterHealthClass(healthStats) {
  if ((healthStats.warning || 0) > 0) return 'health-warning'
  if ((healthStats.ok || 0) > 0 && (healthStats.warning || 0) === 0) return 'health-ok'
  return 'health-unknown'
}

/** 获取数据中心健康状态文本 */
function getDataCenterHealthText(healthStats) {
  if ((healthStats.warning || 0) > 0) return '有警告'
  if ((healthStats.ok || 0) > 0 && (healthStats.warning || 0) === 0) return '正常'
  return '未知'
}

/** 处理U位点击事件 */
function handleUnitClick(unit, rack, event) {
  event.stopPropagation() // 阻止事件冒泡

  if (unit.device) {
    // 点击占用U位，显示设备详情
    showDeviceInfo(unit.device)
  } else {
    // 点击空闲U位，显示机柜详情
    showRackDetails(rack)
  }
}

/** 获取机房状态样式类 */
function getRoomStatusClass(room) {
  const healthStats = room.healthStats
  if (healthStats.warning > 0) return 'room-warning'
  if (healthStats.ok === room.deviceCount) return 'room-healthy'
  return 'room-unknown'
}

/** 获取机房健康状态样式类 */
function getRoomHealthClass(room) {
  const healthStats = room.healthStats
  if (healthStats.warning > 0) return 'status-warning'
  if (healthStats.ok === room.deviceCount) return 'status-healthy'
  return 'status-unknown'
}

/** 获取机房健康状态文本 */
function getRoomHealthText(room) {
  const healthStats = room.healthStats
  if (healthStats.warning > 0) return '有警告'
  if (healthStats.ok === room.deviceCount) return '正常'
  return '未知'
}

/** 获取机柜状态样式类 */
function getRackStatusClass(rack) {
  const hasWarning = rack.devices.some(device => device.healthStatus === 'warning')
  if (hasWarning) return 'rack-warning'

  const allHealthy = rack.devices.every(device => device.healthStatus === 'ok')
  if (allHealthy && rack.devices.length > 0) return 'rack-healthy'

  return 'rack-unknown'
}

/** 获取机柜占用率类型 */
function getRackOccupancyType(rate) {
  if (rate >= 80) return 'danger'
  if (rate >= 60) return 'warning'
  return 'success'
}

/** 获取设备健康状态样式类 */
function getDeviceHealthClass(device) {
  const statusMap = {
    'ok': 'device-healthy',
    'warning': 'device-warning',
    'unknown': 'device-unknown'
  }
  return statusMap[device.healthStatus] || 'device-unknown'
}

/** 生成机柜U位布局 */
function getRackUnits(rack) {
  // 创建42个U位的数组（从42U到1U，顶部到底部）
  const units = []

  // 初始化所有U位为空
  for (let i = 42; i >= 1; i--) {
    units.push({
      unitNumber: i,
      device: null,
      isDeviceStart: false,
      isDeviceMiddle: false,
      deviceHeight: 0
    })
  }

  // 将设备分配到对应的U位
  if (rack.devices && rack.devices.length > 0) {
    rack.devices.forEach(device => {
      const startU = device.locationInfo.startU
      const endU = device.locationInfo.endU
      const deviceHeight = endU - startU + 1

      // 为设备占用的每个U位分配状态
      for (let u = startU; u <= endU; u++) {
        const unitIndex = 42 - u // 数组索引（42U在索引0，1U在索引41）
        if (unitIndex >= 0 && unitIndex < 42) {
          units[unitIndex].device = device

          // 在最低位U位（startU）显示设备信息
          if (u === startU) {
            units[unitIndex].isDeviceStart = true
            units[unitIndex].deviceHeight = deviceHeight
          } else {
            units[unitIndex].isDeviceMiddle = true
          }
        }
      }
    })
  }

  return units
}

getList();
</script>

<style scoped>
/* ================ 机房可视化样式 ================ */

/* 面包屑导航 */
.breadcrumb-link {
  cursor: pointer;
  color: #1F9E91;
}

.breadcrumb-link:hover {
  color: #79bbff;
}

.breadcrumb-current {
  color: #909399;
}

/* 数据中心总览 */
.datacenter-container {
  margin-top: 20px;
}

.datacenter-loading {
  margin-top: 20px;
  padding: 20px;
}

.datacenter-overview .overview-header {
  margin-bottom: 20px;
}

.datacenter-cards {
  margin-top: 20px;
}

/* 简洁数据中心卡片样式 */
.datacenter-card-simple {
  cursor: pointer;
  transition: all 0.3s ease;
  height: 280px;
  border-radius: 8px;
  border-top: 4px solid #52c41a;
}

.datacenter-card-simple:hover {
  border-top: 4px solid #1890ff;
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
}

.card-header-simple {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
}

.title-section {
  display: flex;
  align-items: center;
}

.datacenter-icon-simple {
  color: #1F9E91;
  margin-right: 12px;
}

.datacenter-title-simple {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
}

.health-indicator {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.health-indicator.health-ok {
  background-color: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.health-indicator.health-warning {
  background-color: #fffbe6;
  color: #faad14;
  border: 1px solid #ffe58f;
}

.health-indicator.health-unknown {
  background-color: #f5f5f5;
  color: #8c8c8c;
  border: 1px solid #d9d9d9;
}

.stats-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 40px;
  padding: 20px;
  background: #fafafa;
  border-radius: 6px;
}

.stat-item-simple {
  text-align: center;
  flex: 1;
}

.stat-value-simple {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 6px;
}

.stat-label-simple {
  font-size: 13px;
  color: #8c8c8c;
  font-weight: 500;
}

.stat-divider {
  width: 1px;
  height: 30px;
  background: #e8e8e8;
  margin: 0 16px;
}

.health-detail {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-top: 8px;
}

.health-item-simple {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #666;
  flex: 1;
}

.health-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-right: 4px;
}

.health-ok {
  background-color: #52c41a;
}

.health-warning {
  background-color: #faad14;
}

.health-unknown {
  background-color: #8c8c8c;
}

.health-text {
  white-space: nowrap;
}

/* 机房视图 */
.room-view {
  margin-top: 20px;
}

.room-header h2 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 20px;
}

.room-grid {
  margin-top: 16px;
}

.room-card {
  cursor: pointer;
  transition: all 0.2s ease;
  height: 120px;
}

.room-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.room-healthy {
  border-left: 4px solid #52c41a;
}

.room-warning {
  border-left: 4px solid #faad14;
}

.room-unknown {
  border-left: 4px solid #8c8c8c;
}

.room-info {
  margin-bottom: 12px;
}

.room-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.room-stats {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #8c8c8c;
}

.room-status {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  text-align: center;
}

.status-healthy {
  background-color: #f6ffed;
  color: #52c41a;
}

.status-warning {
  background-color: #fffbe6;
  color: #faad14;
}

.status-unknown {
  background-color: #f5f5f5;
  color: #8c8c8c;
}

/* 机柜视图 */
.rack-view {
  margin-top: 20px;
}

.rack-header h2 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 20px;
}

.rack-grid {
  margin-top: 16px;
}

.rack-card {
  cursor: pointer;
  transition: all 0.2s ease;
  height: 600px;
  display: flex;
  flex-direction: column;
}

.rack-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.rack-healthy {
  border-left: 3px solid #52c41a;
}

.rack-warning {
  border-left: 3px solid #faad14;
}

.rack-unknown {
  border-left: 3px solid #8c8c8c;
}

.rack-header-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.rack-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.rack-units {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.rack-scale {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1.5px solid #c5c4c4;
  /* border-radius: 4px; */
  background: #ffffff;
  position: relative;
}

.unit-slot {
  display: flex;
  align-items: center;
  height: 13px;
  position: relative;
  font-size: 8px;
  border-bottom: 1.5px dashed #c7c6c6;
}

.unit-slot:last-child {
  border-bottom: none;
}

.unit-number {
  width: 22px;
  text-align: center;
  font-size: 9px;
  color: #727272;
  font-weight: 400;
  background: #fafafa;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.unit-device {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 0 3px;
  height: 100%;
}

.unit-empty-space {
  flex: 1;
  height: 100%;
  background: #ffffff;
}

.unit-empty {
  background-color: #ffffff;
}

.unit-occupied {
  position: relative;
  border-left: 2px solid transparent;
}

.unit-occupied.device-healthy {
  background-color: #e8f5e8;
  border-left-color: #52c41a;
}

.unit-occupied.device-warning {
  background-color: #fdefbe;
  border-left-color: #faad14;
}

.unit-occupied.device-unknown {
  background-color: #e5e3e3;
  border-left-color: #d9d9d9;
}

.device-name {
  font-weight: 400;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 7px;
  flex: 1;
}

/* 合并设备显示样式 */
.unit-device-merged {
  position: absolute;
  left: 22px;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: 0 2px 2px 0;
  padding: 2px 4px;
  border: 1px solid;
  border-left: none;
  box-sizing: border-box;
}

.unit-device-middle {
  flex: 1;
  height: 100%;
}

.unit-occupied.device-middle {
  border-top: none;
  border-bottom: none;
}

.unit-occupied.device-healthy .unit-device-merged {
  background-color: #e8f5e8;
  border-color: #52c41a;
}

.unit-occupied.device-warning .unit-device-merged {
  background-color: #fdefbe;
  border-color: #faad14;
}

.unit-occupied.device-unknown .unit-device-merged {
  background-color: #cbcaca;
  border-color: #c5c4c4;
}

.device-name-merged {
  font-weight: 500;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 9px;
  text-align: center;
  line-height: 1.2;
}

.device-range {
  font-size: 7px;
  color: #666;
  text-align: center;
  margin-top: 3px;
}

/* 可点击U位样式 */
.unit-clickable {
  cursor: pointer;
}

.unit-clickable:hover {
  opacity: 0.8;
  transition: all 0.2s ease;
}

.unit-clickable.unit-occupied:hover {
  transform: scale(1.02);
}

.unit-clickable.unit-empty:hover {
  background-color: #f5f5f5;
}

.no-devices {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
  color: #8c8c8c;
  font-size: 12px;
  border: 1px dashed #d9d9d9;
  border-radius: 4px;
  margin-top: 8px;
}

/* 设备详情抽屉 */
.device-details {
  padding: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .datacenter-card-simple {
    height: auto;
    min-height: 200px;
  }

  .stats-section {
    flex-direction: column;
    gap: 12px;
  }

  .stat-divider {
    display: none;
  }

  .health-detail {
    flex-direction: column;
    gap: 6px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .datacenter-icon {
    margin-bottom: 8px;
  }

  .datacenter-stats {
    flex-direction: column;
    gap: 8px;
  }

  .stat-item {
    text-align: left;
  }

  .health-distribution {
    justify-content: flex-start;
  }

  .room-card,
  .rack-card {
    height: auto;
    min-height: 100px;
  }
}

/* 列表中的连通性状态样式 */
.connectivity-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.connectivity-tag {
  display: flex;
  align-items: center;
  white-space: nowrap;
}

.no-test {
  color: #909399;
  font-size: 12px;
  font-style: italic;
}

.ping-time {
  font-size: 11px;
  font-weight: bold;
  line-height: 1;
}

/* 连通性检测结果样式 */
.connectivity-summary {
  margin-bottom: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.connectivity-summary .el-statistic {
  text-align: center;
}

.connectivity-summary .success .el-statistic__content {
  color: #67c23a;
}

.connectivity-summary .danger .el-statistic__content {
  color: #f56c6c;
}

/* Ping响应时间样式 */
.ping-excellent {
  color: #67c23a;
  font-weight: bold;
}

.ping-good {
  color: #95d475;
  font-weight: bold;
}

.ping-fair {
  color: #e6a23c;
  font-weight: bold;
}

.ping-poor {
  color: #f56c6c;
  font-weight: bold;
}

.ping-unknown {
  color: #909399;
}

/* 状态文本样式 */
.success-text {
  color: #67c23a;
  font-weight: 500;
}

.error-text {
  color: #f56c6c;
  font-size: 12px;
}

.warning-text {
  color: #e6a23c;
  font-style: italic;
}

/* 连通性统计对话框样式 */
.connectivity-stats-container {
  padding: 20px 0;
}

.stats-overview {
  margin-bottom: 30px;
}

.overview-card {
  text-align: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 12px;
  padding: 30px;
}

.stats-header {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  gap: 12px;
}

.stats-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.circular-progress {
  display: flex;
  justify-content: center;
}

.progress-text {
  text-align: center;
}

.progress-text .percentage {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
  line-height: 1;
}

.progress-text .label {
  font-size: 12px;
  color: #606266;
  margin-top: 4px;
}

.stats-details {
  margin-bottom: 30px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 8px;
  background: #fff;
  border: 1px solid #ebeef5;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-card.total {
  border-left: 4px solid #1F9E91;
}

.stat-card.online {
  border-left: 4px solid #67c23a;
}

.stat-card.offline {
  border-left: 4px solid #f56c6c;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.stat-card.total .stat-icon {
  background: rgba(31, 158, 145, 0.1);
  color: #1F9E91;
}

.stat-card.online .stat-icon {
  background: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.stat-card.offline .stat-icon {
  background: rgba(245, 108, 108, 0.1);
  color: #f56c6c;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #2c3e50;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.check-info {
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-content {
  flex: 1;
}

.info-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.info-value {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.status-analysis {
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}

.status-analysis h4 {
  margin: 0 0 16px 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
}

.analysis-content {
  background: #fafbfc;
  border-radius: 6px;
  padding: 16px;
  border-left: 4px solid #1F9E91;
}

.analysis-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.analysis-item span {
  color: #606266;
  font-size: 14px;
}

/* 离线设备详情区域样式 */
.offline-devices-section {
  margin-top: 30px;
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}

.section-header {
  margin-bottom: 16px;
}

.section-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.hostname-text {
  font-weight: 600;
  color: #2c3e50;
}

.location-text {
  color: #606266;
  font-size: 13px;
}

.no-ip {
  color: #c0c4cc;
  font-style: italic;
  font-size: 12px;
}

.error-message {
  color: #f56c6c;
  font-size: 12px;
  cursor: help;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 150px;
  display: inline-block;
}

.offline-summary {
  margin-top: 16px;
}

/* 可复制单元格样式 */
.copyable-cell {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  max-width: 100%;
  position: relative;
}

.copyable-cell:hover {
  background-color: #f0f9ff;
  color: #1F9E91;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.copyable-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.copy-icon {
  opacity: 0;
  transition: opacity 0.2s ease;
  color: #1F9E91;
  flex-shrink: 0;
}

.copyable-cell:hover .copy-icon {
  opacity: 1;
}

/* 复制成功的动画效果 */
.copyable-cell.copy-success {
  background-color: #f0f9ff;
  color: #67c23a;
}

.copyable-cell.copy-success .copy-icon {
  color: #67c23a;
  opacity: 1;
}

/* 离线设备表格中的可复制单元格样式 */
.offline-copyable {
  padding: 2px 6px;
  margin: -2px;
}

.offline-copyable:hover {
  background-color: rgba(31, 158, 145, 0.1);
  color: #1F9E91;
  transform: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.offline-copyable .copy-icon {
  color: #909399;
}

.offline-copyable:hover .copy-icon {
  color: #1F9E91;
  opacity: 1;
}

.offline-copyable.copy-success {
  background-color: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.offline-copyable.copy-success .copy-icon {
  color: #67c23a;
}

/* 详情对话框中的可复制单元格样式 */
.detail-copyable {
  display: inline-flex;
  padding: 2px 6px;
  margin: -2px -6px;
  border-radius: 3px;
}

.detail-copyable:hover {
  background-color: #f0f9ff;
  color: #1F9E91;
  transform: none;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.detail-copyable .copy-icon {
  color: #c0c4cc;
}

.detail-copyable:hover .copy-icon {
  color: #1F9E91;
  opacity: 1;
}

/* 工具类 */
.mb-4 {
  margin-bottom: 16px;
}

.mb-3 {
  margin-bottom: 12px;
}
</style>