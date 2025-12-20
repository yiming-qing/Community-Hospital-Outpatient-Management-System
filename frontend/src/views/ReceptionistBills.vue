<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Search, Tickets } from '@element-plus/icons-vue'

import { listDepartments } from '../api/patient'
import { listBills } from '../api/receptionist'

const loading = ref(false)
const items = ref([])
const total = ref(0)
const deptOptions = ref([])

const pagination = reactive({
  page: 1,
  pageSize: 20,
})

const form = reactive({
  pay_status: '已支付',
  dept_id: null,
  doctor_id: '',
  name: '',
  phone: '',
  id_card: '',
  room_number: '',
  start_date: '',
  end_date: '',
})

const pageAmount = computed(() => {
  const sum = items.value.reduce((acc, row) => acc + Number(row?.bill?.total_amount || 0), 0)
  return sum.toFixed(2)
})

function deptName(deptId) {
  const d = deptOptions.value.find((x) => x.dept_id === deptId)
  return d?.dept_name || ''
}

function buildParams() {
  return {
    limit: pagination.pageSize,
    offset: (pagination.page - 1) * pagination.pageSize,
    pay_status: form.pay_status || undefined,
    dept_id: form.dept_id ?? undefined,
    doctor_id: form.doctor_id || undefined,
    name: form.name || undefined,
    phone: form.phone || undefined,
    id_card: form.id_card || undefined,
    room_number: form.room_number || undefined,
    start_date: form.start_date || undefined,
    end_date: form.end_date || undefined,
  }
}

async function load() {
  loading.value = true
  try {
    const resp = await listBills(buildParams())
    items.value = resp.items || []
    total.value = resp.total || 0
  } catch (e) {
    ElMessage.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

async function onSearch() {
  pagination.page = 1
  await load()
}

onMounted(async () => {
  try {
    deptOptions.value = await listDepartments()
  } catch (e) {
    deptOptions.value = []
    ElMessage.error(e?.message || '加载科室失败')
  }
  await load()
})
</script>

<template>
  <div class="page-container">
    <el-card class="box-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="header-icon"><Tickets /></el-icon>
            <span>前台工作台 - 收费报表</span>
          </div>
          <el-space>
            <el-tag type="info">本页合计：{{ pageAmount }}</el-tag>
            <el-button :icon="Refresh" circle @click="load" />
          </el-space>
        </div>
      </template>

      <el-form :model="form" label-width="90px">
        <el-row :gutter="12">
          <el-col :xs="24" :md="6">
            <el-form-item label="支付状态">
              <el-select v-model="form.pay_status" clearable placeholder="全部" style="width: 100%">
                <el-option label="未支付" value="未支付" />
                <el-option label="已支付" value="已支付" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="6">
            <el-form-item label="科室">
              <el-select v-model="form.dept_id" clearable placeholder="全部" style="width: 100%">
                <el-option v-for="d in deptOptions" :key="d.dept_id" :label="d.dept_name" :value="d.dept_id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="6">
            <el-form-item label="医生工号">
              <el-input v-model="form.doctor_id" placeholder="可选，如 D001" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="6" class="actions">
            <el-button type="primary" :icon="Search" :loading="loading" @click="onSearch">查询</el-button>
          </el-col>
        </el-row>

        <el-row :gutter="12">
          <el-col :xs="24" :md="6">
            <el-form-item label="姓名">
              <el-input v-model="form.name" placeholder="模糊匹配" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="6">
            <el-form-item label="电话">
              <el-input v-model="form.phone" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="6">
            <el-form-item label="身份证">
              <el-input v-model="form.id_card" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="6">
            <el-form-item label="诊室号">
              <el-input v-model="form.room_number" placeholder="如 101" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="12">
          <el-col :xs="24" :md="6">
            <el-form-item label="开始日期">
              <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="6">
            <el-form-item label="结束日期">
              <el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <el-table :data="items" v-loading="loading" style="width: 100%" stripe>
        <el-table-column label="账单号" width="90">
          <template #default="{ row }">{{ row.bill?.bill_id }}</template>
        </el-table-column>
        <el-table-column label="就诊号" width="90">
          <template #default="{ row }">{{ row.bill?.visit_id }}</template>
        </el-table-column>
        <el-table-column label="患者" width="120">
          <template #default="{ row }">{{ row.visit?.patient?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="科室" width="140">
          <template #default="{ row }">{{ row.visit?.room?.dept_name || deptName(row.visit?.room?.dept_id) || '-' }}</template>
        </el-table-column>
        <el-table-column label="诊室" width="90" align="center">
          <template #default="{ row }">{{ row.visit?.room?.room_number || '-' }}</template>
        </el-table-column>
        <el-table-column label="医生" width="160">
          <template #default="{ row }">
            {{ row.visit?.doctor?.name ? `${row.visit.doctor.name} (${row.visit.doctor.emp_id})` : row.visit?.doctor?.emp_id || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="总额" width="100" align="right">
          <template #default="{ row }">{{ row.bill?.total_amount ?? '-' }}</template>
        </el-table-column>
        <el-table-column label="医保" width="100" align="right">
          <template #default="{ row }">{{ row.bill?.insurance_amount ?? '-' }}</template>
        </el-table-column>
        <el-table-column label="自费" width="100" align="right">
          <template #default="{ row }">{{ row.bill?.self_pay_amount ?? '-' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">{{ row.bill?.pay_status || '-' }}</template>
        </el-table-column>
        <el-table-column label="支付时间" width="170">
          <template #default="{ row }">{{ row.bill?.pay_time || '-' }}</template>
        </el-table-column>
      </el-table>

      <div class="pager">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          :total="total"
          @size-change="onSearch"
          @current-change="load"
        />
      </div>
    </el-card>
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

.actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  height: 100%;
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}
</style>

