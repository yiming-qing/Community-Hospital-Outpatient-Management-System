<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Calendar, List, Plus, Close } from '@element-plus/icons-vue'

import { cancelAppointment, createAppointment, listDepartments, queryAppointments } from '../api/patient'
import { getUser } from '../utils/storage'

const deptOptions = ref([])
const creating = ref(false)
const querying = ref(false)
const appointments = ref([])

const user = computed(() => getUser())
const patient = computed(() => user.value?.patient || null)

const createForm = reactive({
  dept_id: null,
  expected_time: '',
})

const queryForm = reactive({
  status: '',
})

async function loadDepartments() {
  try {
    deptOptions.value = await listDepartments()
  } catch (e) {
    deptOptions.value = []
    ElMessage.error(e?.message || '加载科室失败')
  }
}

async function onCreate() {
  if (!createForm.dept_id || !createForm.expected_time) {
    ElMessage.warning('请选择科室和预计到达时间')
    return
  }

  creating.value = true
  try {
    const payload = {
      dept_id: createForm.dept_id,
      expected_time: createForm.expected_time,
    }
    const appt = await createAppointment(payload)
    ElMessage.success(`预约成功，预约号：${appt.appt_id}`)
    await onQuery()
  } catch (e) {
    ElMessage.error(e?.message || '预约失败')
  } finally {
    creating.value = false
  }
}

async function onQuery() {
  querying.value = true
  try {
    appointments.value = await queryAppointments({ status: queryForm.status || undefined })
  } catch (e) {
    ElMessage.error(e?.message || '查询失败')
  } finally {
    querying.value = false
  }
}

async function onCancel(appt) {
  try {
    await cancelAppointment(appt.appt_id)
    ElMessage.success('已取消')
    await onQuery()
  } catch (e) {
    ElMessage.error(e?.message || '取消失败')
  }
}

function getStatusType(status) {
  switch (status) {
    case '已确认': return 'success'
    case '已完成': return 'info'
    case '已取消': return 'danger'
    default: return 'warning' // 待确认
  }
}

onMounted(async () => {
  await loadDepartments()
  await onQuery()
})
</script>

<template>
  <div class="appointment-page">
    <el-row :gutter="20">
      <el-col :xs="24" :lg="10">
        <el-card class="box-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon class="header-icon"><Plus /></el-icon>
              <span>在线预约挂号</span>
            </div>
          </template>

          <el-form :model="createForm" label-position="top" size="large">
            <el-alert
              v-if="patient"
              :title="`当前登录：${patient.name}（${patient.phone}）`"
              type="info"
              :closable="false"
              show-icon
              style="margin-bottom: 16px"
            />

            <el-form-item label="就诊科室">
              <el-select v-model="createForm.dept_id" placeholder="请选择科室" style="width: 100%">
                <el-option v-for="d in deptOptions" :key="d.dept_id" :label="d.dept_name" :value="d.dept_id" />
              </el-select>
            </el-form-item>

            <el-form-item label="预计到达时间">
              <el-date-picker 
                v-model="createForm.expected_time" 
                type="datetime" 
                placeholder="选择日期时间"
                format="YYYY-MM-DD HH:mm"
                value-format="YYYY-MM-DD HH:mm:ss" 
                style="width: 100%"
                :prefix-icon="Calendar"
              />
            </el-form-item>

            <div class="form-actions">
              <el-button type="primary" class="submit-btn" :loading="creating" @click="onCreate">
                立即预约
              </el-button>
            </div>
          </el-form>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="14">
        <el-card class="box-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon class="header-icon"><List /></el-icon>
              <span>我的预约记录</span>
            </div>
          </template>

          <div class="query-bar">
            <el-select v-model="queryForm.status" clearable placeholder="状态筛选" style="width: 120px; margin-left: 10px;">
              <el-option label="待确认" value="待确认" />
              <el-option label="已确认" value="已确认" />
              <el-option label="已完成" value="已完成" />
              <el-option label="已取消" value="已取消" />
            </el-select>
            <el-button type="primary" :loading="querying" @click="onQuery" style="margin-left: 10px;">刷新</el-button>
          </div>

          <el-table :data="appointments" style="width: 100%" stripe>
            <el-table-column prop="appt_id" label="号源" width="80" align="center" />
            <el-table-column prop="patient_name" label="姓名" width="100" />
            <el-table-column prop="dept_name" label="科室" width="120" />
            <el-table-column prop="expected_time" label="预约时间" min-width="160" />
            <el-table-column prop="status" label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small" effect="light" round>
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center" fixed="right">
              <template #default="{ row }">
                <el-popconfirm 
                  v-if="row.status !== '已完成' && row.status !== '已取消'"
                  title="确定要取消这个预约吗?"
                  @confirm="onCancel(row)"
                  confirm-button-text="确定"
                  cancel-button-text="暂不"
                  confirm-button-type="danger"
                >
                   <template #reference>
                     <el-button link type="danger" size="small">
                       <el-icon><Close /></el-icon>取消
                     </el-button>
                   </template>
                </el-popconfirm>
              </template>
            </el-table-column>
            <template #empty>
               <el-empty description="暂无预约记录" />
            </template>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.appointment-page {
  padding-bottom: 20px;
}

.box-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.card-header {
  display: flex;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

.header-icon {
  margin-right: 8px;
  color: var(--el-color-primary);
}

.form-actions {
  margin-top: 30px;
}

.submit-btn {
  width: 100%;
  font-weight: 600;
  letter-spacing: 1px;
}

.query-bar {
  display: flex;
  margin-bottom: 20px;
}

.query-input {
  flex: 1;
}
</style>
