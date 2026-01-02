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

export default router