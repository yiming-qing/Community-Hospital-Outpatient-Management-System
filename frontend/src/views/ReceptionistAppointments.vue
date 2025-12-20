<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Ticket, User, Phone, Postcard } from '@element-plus/icons-vue'

import { checkin, listAppointments, updateAppointmentStatus } from '../api/receptionist'

const loading = ref(false)
const appointments = ref([])
const statusFilter = ref('')

const dialogVisible = ref(false)
const dialogLoading = ref(false)
const selected = ref(null)

const checkinForm = reactive({
  phone: '',
  id_card: '',
})

async function load() {
  loading.value = true
  try {
    appointments.value = await listAppointments({ status: statusFilter.value || undefined })
  } catch (e) {
    ElMessage.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function openCheckin(row) {
  selected.value = row
  checkinForm.phone = row.phone
  checkinForm.id_card = ''
  dialogVisible.value = true
}

async function toStatus(row, status) {
  try {
    if (status === '已取消') {
      await ElMessageBox.confirm(`取消预约 ${row.appt_id}？`, '确认', { type: 'warning' })
    }
    await updateAppointmentStatus(row.appt_id, status)
    ElMessage.success('已更新')
    await load()
  } catch (e) {
    if (e === 'cancel') return
    ElMessage.error(e?.message || '更新失败')
  }
}

async function onCheckin() {
  if (!selected.value) return
  dialogLoading.value = true
  try {
    const visit = await checkin(selected.value.appt_id, {
      phone: checkinForm.phone,
      id_card: checkinForm.id_card || undefined,
    })
    ElMessage.success(`签到成功，Visit：${visit.visit_id}，诊室：${visit.room?.room_number || '-'}`)
    dialogVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e?.message || '签到失败')
  } finally {
    dialogLoading.value = false
  }
}

function getStatusType(status) {
  switch (status) {
    case '已确认': return 'success'
    case '已完成': return 'info'
    case '已取消': return 'danger'
    default: return 'warning'
  }
}

onMounted(load)
</script>

<template>
  <div class="page-container">
    <el-card class="box-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <div class="header-left">
             <el-icon class="header-icon"><Ticket /></el-icon>
             <span>前台工作台 - 预约管理</span>
          </div>
          <el-button :icon="Refresh" circle @click="load" />
        </div>
      </template>

      <div class="filter-bar">
        <span class="filter-label">状态筛选:</span>
        <el-select v-model="statusFilter" clearable placeholder="全部状态" style="width: 180px">
            <el-option label="待确认" value="待确认" />
            <el-option label="已确认" value="已确认" />
            <el-option label="已完成" value="已完成" />
            <el-option label="已取消" value="已取消" />
        </el-select>
        <el-button type="primary" :loading="loading" :icon="Search" @click="load" style="margin-left: 10px">刷新列表</el-button>
      </div>

      <el-table :data="appointments" style="width: 100%" v-loading="loading" stripe>
        <el-table-column prop="appt_id" label="预约号" width="100" align="center" sortable />
        <el-table-column prop="patient_name" label="姓名" width="120" />
        <el-table-column prop="phone" label="电话" width="140" />
        <el-table-column prop="dept_name" label="科室" width="140" />
        <el-table-column prop="expected_time" label="预计到达" min-width="160" sortable />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
             <el-tag :type="getStatusType(row.status)" size="small" effect="light" round>
                  {{ row.status }}
             </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template #default="{ row }">
            <el-space wrap>
              <el-button
                v-if="row.status === '待确认'"
                type="success"
                size="small"
                plain
                @click="toStatus(row, '已确认')"
              >
                确认
              </el-button>
              <el-button
                v-if="row.status === '待确认' || row.status === '已确认'"
                type="danger"
                size="small"
                plain
                @click="toStatus(row, '已取消')"
              >
                取消
              </el-button>
              <el-button
                v-if="row.status !== '已完成' && row.status !== '已取消'"
                type="primary"
                size="small"
                @click="openCheckin(row)"
                plain
              >
                到院签到
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="预约签到" width="460px" destroy-on-close align-center>
      <el-alert
        title="请核验患者身份信息后进行签到"
        type="info"
        show-icon
        :closable="false"
        style="margin-bottom: 20px;"
      />
      <el-form :model="checkinForm" label-width="100px" size="large">
        <el-form-item label="电话">
          <el-input v-model="checkinForm.phone" :prefix-icon="Phone" disabled />
        </el-form-item>
        <el-form-item label="身份证">
          <el-input v-model="checkinForm.id_card" placeholder="可选，输入后系统将自动核验" :prefix-icon="Postcard" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
           <el-button @click="dialogVisible = false">取消</el-button>
           <el-button type="primary" :loading="dialogLoading" @click="onCheckin">确认签到</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.page-container {
  padding-bottom: 20px;
}

.box-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

.header-icon {
  margin-right: 8px;
  color: var(--el-color-primary);
  font-size: 18px;
}

.filter-bar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
}

.filter-label {
  font-size: 14px;
  color: #606266;
  margin-right: 10px;
}
</style>
