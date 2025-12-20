<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Search } from '@element-plus/icons-vue'

import { listDepartments } from '../../api/patient'
import { listEmployees, listIncomeRecords } from '../../api/admin'

const loading = ref(false)
const items = ref([])
const total = ref(0)

const deptOptions = ref([])
const employees = ref([])
const doctors = computed(() => employees.value.filter((e) => e.position === '医生'))

const pagination = reactive({
  page: 1,
  pageSize: 20,
})

const form = reactive({
  start_date: '',
  end_date: '',
  dept_id: null,
  doctor_id: '',
})

const pageAmount = computed(() => {
  const sum = items.value.reduce((acc, row) => acc + Number(row?.amount || 0), 0)
  return sum.toFixed(2)
})

function buildParams() {
  return {
    limit: pagination.pageSize,
    offset: (pagination.page - 1) * pagination.pageSize,
    start_date: form.start_date || undefined,
    end_date: form.end_date || undefined,
    dept_id: form.dept_id ?? undefined,
    doctor_id: form.doctor_id || undefined,
  }
}

async function load() {
  loading.value = true
  try {
    const resp = await listIncomeRecords(buildParams())
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

function deptName(deptId) {
  const d = deptOptions.value.find((x) => x.dept_id === deptId)
  return d?.dept_name || ''
}

onMounted(async () => {
  try {
    const [depts, emps] = await Promise.all([listDepartments(), listEmployees()])
    deptOptions.value = depts
    employees.value = emps
  } catch (e) {
    ElMessage.error(e?.message || '加载基础数据失败')
  }
  await load()
})
</script>

<template>
  <el-space direction="vertical" fill size="large">
    <el-card>
      <template #header>
        <div class="header">
          <div class="title">收入明细</div>
          <el-space>
            <el-tag type="info">本页合计：{{ pageAmount }}</el-tag>
            <el-button :icon="Refresh" :loading="loading" @click="load">刷新</el-button>
          </el-space>
        </div>
      </template>

      <el-form :model="form" label-width="90px">
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
          <el-col :xs="24" :md="6">
            <el-form-item label="科室">
              <el-select v-model="form.dept_id" clearable placeholder="全部" style="width: 100%">
                <el-option v-for="d in deptOptions" :key="d.dept_id" :label="d.dept_name" :value="d.dept_id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="6">
            <el-form-item label="医生">
              <el-select v-model="form.doctor_id" clearable filterable placeholder="全部" style="width: 100%">
                <el-option
                  v-for="d in doctors"
                  :key="d.emp_id"
                  :label="`${d.name} (${d.emp_id}) - ${d.dept_name || deptName(d.dept_id) || '无科室'}`"
                  :value="d.emp_id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="24" class="actions">
            <el-button type="primary" :icon="Search" :loading="loading" @click="onSearch">查询</el-button>
          </el-col>
        </el-row>
      </el-form>

      <el-table :data="items" v-loading="loading" style="width: 100%">
        <el-table-column prop="record_id" label="记录ID" width="90" />
        <el-table-column prop="record_date" label="日期" width="120" />
        <el-table-column prop="dept_name" label="科室" width="140" />
        <el-table-column prop="doctor_name" label="医生" width="140" />
        <el-table-column prop="bill_id" label="账单号" width="90" />
        <el-table-column prop="amount" label="金额" width="120" align="right" />
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
  </el-space>
</template>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title {
  font-weight: 700;
}
.actions {
  display: flex;
  justify-content: flex-end;
}
.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}
</style>

