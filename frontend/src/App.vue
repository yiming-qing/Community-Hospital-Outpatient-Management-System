<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { SwitchButton, Calendar, Service, Monitor, Setting, OfficeBuilding, UserFilled, Histogram } from '@element-plus/icons-vue'

import { clearAuth, getUser } from './utils/storage'

const router = useRouter()
const route = useRoute()
const user = computed(() => getUser())

const activeIndex = computed(() => route.path)

const roleLabel = computed(() => {
  if (!user.value) return ''
  if (user.value.role === 'patient') return '患者'
  if (user.value.role === 'receptionist') return '前台'
  if (user.value.role === 'admin') return '管理员'
  return user.value.role
})

function logout() {
  clearAuth()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<template>
  <el-container class="layout-container">
    <el-header class="header">
      <div class="header-content">
        <div class="brand" @click="router.push('/')">
          <el-icon class="brand-icon" :size="28" color="#009688"><Monitor /></el-icon>
          <span class="brand-text">社区医院门诊管理系统</span>
        </div>
        
        <div class="nav-menu">
           <el-menu
            :default-active="activeIndex"
            mode="horizontal"
            :ellipsis="false"
            router
            class="el-menu-demo"
            background-color="#ffffff"
            text-color="#303133"
            active-text-color="#009688"
          >
            <template v-if="user && user.role === 'patient'">
              <el-menu-item index="/patient/appointment">
                <el-icon><Calendar /></el-icon>预约挂号
              </el-menu-item>
            </template>

            <template v-if="user && user.role === 'receptionist'">
              <el-sub-menu index="/receptionist">
                <template #title>
                  <el-icon><Service /></el-icon>前台工作台
                </template>
                <el-menu-item index="/receptionist/register">挂号登记</el-menu-item>
                <el-menu-item index="/receptionist/appointments">预约处理</el-menu-item>
                <el-menu-item index="/receptionist/visits">就诊/缴费</el-menu-item>
                <el-menu-item index="/receptionist/patients">患者信息</el-menu-item>
                <el-menu-item index="/receptionist/bills">收费报表</el-menu-item>
              </el-sub-menu>
            </template>

            <template v-if="user && user.role === 'admin'">
              <el-sub-menu index="/admin">
                <template #title>
                  <el-icon><Setting /></el-icon>管理后台
                </template>
                <el-menu-item index="/admin/rooms">
                  <el-icon><OfficeBuilding /></el-icon>诊室管理
                </el-menu-item>
                <el-menu-item index="/admin/schedules">
                  <el-icon><Calendar /></el-icon>排班管理
                </el-menu-item>
                <el-menu-item index="/admin/employees">
                  <el-icon><UserFilled /></el-icon>员工管理
                </el-menu-item>
                <el-menu-item index="/admin/statistics">
                  <el-icon><Histogram /></el-icon>统计报表
                </el-menu-item>
                <el-menu-item index="/admin/bills">
                  <el-icon><Histogram /></el-icon>账单查询
                </el-menu-item>
                <el-menu-item index="/admin/income-records">
                  <el-icon><Histogram /></el-icon>收入明细
                </el-menu-item>
                <el-menu-item index="/admin/patients">
                  <el-icon><UserFilled /></el-icon>患者查询
                </el-menu-item>
                <el-menu-item index="/admin/visits">
                  <el-icon><Service /></el-icon>就诊查询
                </el-menu-item>
              </el-sub-menu>
            </template>
          </el-menu>
        </div>

        <div class="user-actions">
          <template v-if="user">
            <el-dropdown>
              <span class="el-dropdown-link">
                <el-avatar :size="32" class="user-avatar">{{ (user.username || '').slice(0, 1).toUpperCase() }}</el-avatar>
                <span class="username">{{ user.username }} ({{ roleLabel }})</span>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item divided @click="logout">
                    <el-icon><SwitchButton /></el-icon>退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <el-button round @click="$router.push('/register')">患者注册</el-button>
            <el-button type="primary" round @click="$router.push('/login')">登录</el-button>
          </template>
        </div>
      </div>
    </el-header>

    <el-main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>

    <el-footer class="footer">
      <p>© 2025 社区医院门诊管理系统 - 中山大学数据库系统实验大作业</p>
    </el-footer>
  </el-container>
</template>

<style scoped>
.layout-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 0;
  height: 60px;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.brand {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 10px;
}

.brand-text {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  letter-spacing: 0.5px;
}

.nav-menu {
  flex: 1;
  display: flex;
  justify-content: center;
}

.el-menu-demo {
  border-bottom: none !important;
  background: transparent !important;
}

.user-actions {
  display: flex;
  align-items: center;
}

.el-dropdown-link {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  outline: none;
}

.username {
  font-weight: 500;
  color: #606266;
}

.user-avatar {
  background-color: #009688;
}

.main-content {
  flex: 1;
  width: 100%;
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
}

.footer {
  text-align: center;
  color: #909399;
  font-size: 14px;
  padding: 20px 0;
  background: #fff;
  border-top: 1px solid #ebeef5;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
