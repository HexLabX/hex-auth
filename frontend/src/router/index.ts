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
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('@/pages/Profile.vue')
        }
      ]
    },
    // 404路由，处理所有未知路径
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      redirect: '/dashboard' // 未知路径重定向到仪表盘
    }
  ]
})

// 路由守卫：检查登录状态
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  console.log('=== 路由守卫调试 ===')
  console.log('从:', from.path, '→ 到:', to.path)
  console.log('Token状态:', token ? '存在' : '不存在')
  if (token) {
    console.log('Token长度:', token.length)
    console.log('Token前20字符:', token.substring(0, 20) + '...')
  }

  // 定义需要认证的路由白名单（不需要登录的路由）
  const whiteList = ['/login']

  // 如果是白名单路由，直接放行
  if (whiteList.includes(to.path)) {
    console.log('✓ 白名单路由，直接放行')
    next()
    return
  }

  // 如果有token，放行
  if (token) {
    console.log('✓ 有token，放行')
    next()
    return
  }

  // 否则跳转到登录页
  console.log('✗ 无token，跳转到登录页')
  next('/login')
})

export default router