<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, ArrowRight } from '@element-plus/icons-vue'

import { login } from '../api/auth'
import { setAuth } from '../utils/storage'

const router = useRouter()
const route = useRoute()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

async function onSubmit() {
  if (!form.username || !form.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    const data = await login(form.username, form.password)
    setAuth(data.access_token, data.user)
    ElMessage.success('登录成功')
    router.replace(route.query.redirect || '/')
  } catch (e) {
    ElMessage.error(e?.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h2>欢迎回来</h2>
        <p>社区医院门诊管理系统</p>
      </div>
      
      <el-form :model="form" size="large" @submit.prevent="onSubmit">
        <el-form-item>
          <el-input 
            v-model="form.username" 
            placeholder="用户名" 
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item>
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="密码" 
            show-password 
            :prefix-icon="Lock"
          />
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            :loading="loading" 
            class="submit-btn" 
            @click="onSubmit"
          >
            登录
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <el-button text @click="$router.push('/register')">患者注册</el-button>
        <p>默认账号: admin / reception</p>
        <p>默认密码: admin123 / reception123</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh; /* Account for header/footer in App.vue */
  background-color: transparent;
}

.login-box {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.login-header h2 {
  margin: 0 0 10px;
  font-size: 28px;
  color: #2c3e50;
  font-weight: 700;
}

.login-header p {
  margin: 0 0 30px;
  color: #909399;
  font-size: 16px;
}

.submit-btn {
  width: 100%;
  font-weight: 600;
  letter-spacing: 1px;
}

.login-footer {
  margin-top: 20px;
  font-size: 13px;
  color: #c0c4cc;
}

.login-footer p {
  margin: 4px 0;
}
</style>
