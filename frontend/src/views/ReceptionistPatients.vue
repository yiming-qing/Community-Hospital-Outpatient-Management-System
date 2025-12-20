<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Search, User } from '@element-plus/icons-vue'

import { listPatients } from '../api/receptionist'

const loading = ref(false)
const patients = ref([])

const form = reactive({
  name: '',
  phone: '',
  id_card: '',
})

async function load() {
  loading.value = true
  try {
    patients.value = await listPatients({
      name: form.name || undefined,
      phone: form.phone || undefined,
      id_card: form.id_card || undefined,
    })
  } catch (e) {
    ElMessage.error(e?.message || '加载失败')
  } finally {
    loading.value = false
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
            <el-icon class="header-icon"><User /></el-icon>
            <span>前台工作台 - 患者信息</span>
          </div>
          <el-button :icon="Refresh" circle @click="load" />
        </div>
      </template>

      <el-form :inline="true" :model="form">
        <el-form-item label="姓名">
          <el-input v-model="form.name" placeholder="模糊匹配" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="身份证">
          <el-input v-model="form.id_card" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" :loading="loading" @click="load">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="patients" v-loading="loading" style="width: 100%" stripe>
        <el-table-column prop="patient_id" label="ID" width="80" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="gender" label="性别" width="80" />
        <el-table-column prop="phone" label="电话" width="140" />
        <el-table-column prop="id_card" label="身份证" min-width="180" />
      </el-table>
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
</style>

