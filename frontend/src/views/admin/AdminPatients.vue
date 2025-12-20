<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Search } from '@element-plus/icons-vue'

import { searchPatients } from '../../api/admin'

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
    patients.value = await searchPatients({
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
  <el-space direction="vertical" fill size="large">
    <el-card>
      <template #header>
        <div class="header">
          <div class="title">患者查询</div>
          <el-space>
            <el-button :icon="Refresh" @click="load">刷新</el-button>
          </el-space>
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

      <el-table :data="patients" v-loading="loading" style="width: 100%">
        <el-table-column prop="patient_id" label="ID" width="80" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="gender" label="性别" width="80" />
        <el-table-column prop="phone" label="电话" width="140" />
        <el-table-column prop="id_card" label="身份证" min-width="180" />
      </el-table>
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
</style>

