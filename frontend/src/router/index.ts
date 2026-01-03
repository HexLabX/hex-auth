import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/pages/Login.vue')
    },
    {
      path: '/',
      name: 'home',
      redirect: '/dashboard',
      component: () => import('@/layouts/MainLayout.vue'),
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/pages/Dashboard.vue')
        },
        {
          path: 'products',
          name: 'products',
          component: () => import('@/pages/Products.vue')
        },
        {
          path: 'licenses',
          name: 'licenses',
          component: () => import('@/pages/Licenses.vue')
        },
        {
          path: 'clients',
          name: 'clients',
          component: () => import('@/pages/Clients.vue')
        },
        {
          path: 'audit-logs',
          name: 'audit-logs',
          component: () => import('@/pages/AuditLogs.vue')
        }
      ]
    }
  ]
})

// 路由守卫：检查登录状态
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  // 定义需要认证的路由白名单（不需要登录的路由）
  const whiteList = ['/login']
  
  // 如果是白名单路由，直接放行
  if (whiteList.includes(to.path)) {
    next()
    return
  }
  
  // 如果有token，放行
  if (token) {
    next()
    return
  }
  
  // 否则跳转到登录页
  next('/login')
})

export default router