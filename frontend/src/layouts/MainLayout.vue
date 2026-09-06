<template>
  <div class="main-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="brand-mark">
          <Icon :icon="icons.licenses" />
        </div>
        <div class="brand-text">
          <h1>hex-auth</h1>
          <span>授权中心</span>
        </div>
      </div>
      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: route.path === item.path }"
        >
          <span class="nav-icon"><Icon :icon="item.icon" /></span>
          <span class="nav-text">{{ item.label }}</span>
        </router-link>
      </nav>
    </aside>
    <main class="main-content">
      <header class="top-nav">
        <div class="nav-left">
          <h2>{{ currentPageTitle }}</h2>
        </div>
        <div class="nav-right">
          <button class="ghost-btn" @click="goToProfile" title="个人中心">
            <Icon :icon="icons.user" />
            <span class="btn-text">个人中心</span>
          </button>
          <button class="ghost-btn danger" @click="logout" title="退出登录">
            <Icon :icon="icons.logout" />
            <span class="btn-text">退出</span>
          </button>
        </div>
      </header>
      <div class="content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Icon } from '@iconify/vue'
import icons from '@/icons'

const router = useRouter()
const route = useRoute()

// 菜单配置
const menuItems = [
  { path: '/dashboard', label: '仪表盘', icon: icons.dashboard },
  { path: '/products', label: '产品管理', icon: icons.products },
  { path: '/licenses', label: '授权管理', icon: icons.licenses },
  { path: '/clients', label: '客户端管理', icon: icons.clients },
  { path: '/audit-logs', label: '审计日志', icon: icons.auditLogs }
]

// 当前页面标题
const currentPageTitle = computed(() => {
  const currentRoute = menuItems.find(item => item.path === route.path)
  if (route.path === '/profile') return '个人中心'
  return currentRoute?.label || 'hex-auth'
})

// 跳转到个人中心
const goToProfile = () => {
  router.push('/profile')
}

// 退出登录
const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
.main-layout {
  display: flex;
  width: 100%;
  height: 100%;
  background-color: #f6f7f9;
  overflow: hidden;
}

/* ---------- 侧边栏 ---------- */
.sidebar {
  width: 232px;
  background-color: #0f172a;
  color: #fff;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 20px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.brand-mark {
  width: 34px;
  height: 34px;
  border-radius: 9px;
  background-color: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.brand-mark :deep(svg) {
  width: 17px;
  height: 17px;
  color: #fff;
}

.brand-text h1 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: -0.01em;
  line-height: 1.2;
}

.brand-text span {
  font-size: 11px;
  color: #64748b;
}

.sidebar-nav {
  flex: 1;
  padding: 14px 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border-radius: 8px;
  color: #94a3b8;
  text-decoration: none;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.06);
  color: #e2e8f0;
}

.nav-item.active {
  background-color: rgba(37, 99, 235, 0.18);
  color: #fff;
}

.nav-icon {
  margin-right: 11px;
  display: flex;
  align-items: center;
}

.nav-icon :deep(svg) {
  width: 17px;
  height: 17px;
}

.nav-text {
  font-size: 14px;
  font-weight: 500;
}

/* ---------- 主区域 ---------- */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.top-nav {
  height: 60px;
  background-color: #fff;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  flex-shrink: 0;
}

.nav-left h2 {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: #111827;
}

.nav-right {
  display: flex;
  gap: 8px;
  align-items: center;
}

.ghost-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  background-color: #fff;
  color: #475569;
  transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.ghost-btn :deep(svg) {
  width: 15px;
  height: 15px;
}

.ghost-btn:hover {
  background-color: #f6f7f9;
  color: #111827;
}

.ghost-btn.danger:hover {
  background-color: #fef2f2;
  border-color: #fecaca;
  color: #dc2626;
}

.ghost-btn:active {
  transform: translateY(0.5px);
}

.content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  box-sizing: border-box;
  min-height: 0;
}
</style>
