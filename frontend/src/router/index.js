import { createRouter, createWebHistory } from 'vue-router'

import { clearAuth, getToken, getUser } from '../utils/storage'

function defaultPathForUser(user) {
  if (!user) return '/login'
  switch (user.role) {
    case 'patient':
      return '/patient/appointment'
    case 'receptionist':
      return '/receptionist/register'
    case 'admin':
      return '/admin/statistics'
    default:
      return '/login'
  }
}

const Home = { template: '<div />' }

const routes = [
  { path: '/', component: Home },
  { path: '/login', component: () => import('../views/Login.vue') },
  { path: '/register', component: () => import('../views/Register.vue') },

  {
    path: '/patient/appointment',
    component: () => import('../views/PatientAppointment.vue'),
    meta: { requiresAuth: true, roles: ['patient'] },
  },

  {
    path: '/receptionist/register',
    component: () => import('../views/ReceptionistRegister.vue'),
    meta: { requiresAuth: true, roles: ['receptionist'] },
  },
  {
    path: '/receptionist/appointments',
    component: () => import('../views/ReceptionistAppointments.vue'),
    meta: { requiresAuth: true, roles: ['receptionist'] },
  },
  {
    path: '/receptionist/visits',
    component: () => import('../views/ReceptionistVisits.vue'),
    meta: { requiresAuth: true, roles: ['receptionist'] },
  },
  {
    path: '/receptionist/patients',
    component: () => import('../views/ReceptionistPatients.vue'),
    meta: { requiresAuth: true, roles: ['receptionist'] },
  },
  {
    path: '/receptionist/bills',
    component: () => import('../views/ReceptionistBills.vue'),
    meta: { requiresAuth: true, roles: ['receptionist'] },
  },

  {
    path: '/admin/rooms',
    component: () => import('../views/admin/AdminRooms.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/admin/schedules',
    component: () => import('../views/admin/AdminSchedules.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/admin/employees',
    component: () => import('../views/admin/AdminEmployees.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/admin/statistics',
    component: () => import('../views/admin/AdminStatistics.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/admin/patients',
    component: () => import('../views/admin/AdminPatients.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/admin/visits',
    component: () => import('../views/admin/AdminVisits.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/admin/bills',
    component: () => import('../views/admin/AdminBills.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/admin/income-records',
    component: () => import('../views/admin/AdminIncomeRecords.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },

  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = getToken()
  const user = getUser()

  if (to.path === '/') {
    if (!token || !user) return { path: '/login' }
    return { path: defaultPathForUser(user) }
  }

  if ((to.path === '/login' || to.path === '/register') && token && user) {
    return { path: defaultPathForUser(user) }
  }

  if (to.meta?.requiresAuth && !token) {
    clearAuth()
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  if (to.meta?.roles?.length) {
    if (!user || !to.meta.roles.includes(user.role)) {
      clearAuth()
      return { path: '/login', query: { redirect: to.fullPath } }
    }
  }
})

export default router
