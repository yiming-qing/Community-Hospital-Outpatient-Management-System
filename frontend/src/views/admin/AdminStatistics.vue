<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'

import { statsIncome, statsVisits } from '../../api/admin'

const loading = ref(false)

const filters = reactive({
  start_date: '',
  end_date: '',
  income_group_by: 'dept',
  visits_group_by: 'dept',
})

const income = ref(null)
const visits = ref(null)

const incomeRows = computed(() => income.value?.data || [])
const visitsRows = computed(() => visits.value?.data || [])

async function load() {
  loading.value = true
  try {
    const [start, end] = filters.start_date && filters.end_date ? [filters.start_date, filters.end_date] : ['', '']

    const incomeResp = await statsIncome({
      start_date: start || undefined,
      end_date: end || undefined,
      group_by: filters.income_group_by,
    })
    const visitsResp = await statsVisits({
      start_date: start || undefined,
      end_date: end || undefined,
      group_by: filters.visits_group_by,
    })
    income.value = incomeResp
    visits.value = visitsResp
  } catch (e) {
    ElMessage.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <el-space direction="vertical" fill size="large">
    <el-card>
      <template #header>
        <div class="header">
          <div class="title">统计报表</div>
          <el-space>
            <el-date-picker
              v-model="filters.start_date"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="开始日期"
            />
            <el-date-picker v-model="filters.end_date" type="date" value-format="YYYY-MM-DD" placeholder="结束日期" />
            <el-button :icon="Refresh" :loading="loading" @click="load">刷新</el-button>
          </el-space>
        </div>
      </template>

      <el-row :gutter="16">
        <el-col :xs="24" :lg="12">
          <el-card shadow="never">
            <template #header>
              <div class="sub-header">
                <div class="sub-title">收入统计</div>
                <el-select v-model="filters.income_group_by" style="width: 140px" @change="load">
                  <el-option label="按科室" value="dept" />
                  <el-option label="按医生" value="doctor" />
                  <el-option label="按日期" value="day" />
                </el-select>
              </div>
            </template>

            <el-table :data="incomeRows" v-loading="loading" style="width: 100%">
              <el-table-column v-if="income?.group_by === 'day'" prop="date" label="日期" width="120" />
              <el-table-column v-if="income?.group_by === 'dept'" prop="dept_name" label="科室" min-width="140" />
              <el-table-column v-if="income?.group_by === 'doctor'" prop="doctor_name" label="医生" min-width="140" />
              <el-table-column prop="amount" label="金额" width="120" />
              <el-table-column prop="records" label="记录数" width="100" />
            </el-table>
          </el-card>
        </el-col>

        <el-col :xs="24" :lg="12">
          <el-card shadow="never">
            <template #header>
              <div class="sub-header">
                <div class="sub-title">就诊统计</div>
                <el-select v-model="filters.visits_group_by" style="width: 140px" @change="load">
                  <el-option label="按科室" value="dept" />
                  <el-option label="按医生" value="doctor" />
                  <el-option label="按日期" value="day" />
                </el-select>
              </div>
            </template>

            <el-table :data="visitsRows" v-loading="loading" style="width: 100%">
              <el-table-column v-if="visits?.group_by === 'day'" prop="date" label="日期" width="120" />
              <el-table-column v-if="visits?.group_by === 'dept'" prop="dept_name" label="科室" min-width="140" />
              <el-table-column v-if="visits?.group_by === 'doctor'" prop="doctor_name" label="医生" min-width="140" />
              <el-table-column prop="visits" label="就诊人次" width="120" />
              <el-table-column prop="patients" label="患者数" width="100" />
            </el-table>
          </el-card>
        </el-col>
      </el-row>
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
.sub-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.sub-title {
  font-weight: 700;
}
</style>

