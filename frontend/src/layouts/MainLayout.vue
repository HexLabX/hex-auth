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

/* ---------- 侧边栏（浅色单色系） ---------- */
.sidebar {
  width: 220px;
  background-color: #f6f7f9;
  border-right: 1px solid #ececef;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 16px 16px;
}

.brand-mark {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background-color: #111827;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.brand-mark :deep(svg) {
  width: 14px;
  height: 14px;
  color: #fff;
}

.brand-text h1 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: -0.01em;
  line-height: 1.2;
  color: #111827;
}

.brand-text span {
  font-size: 11px;
  color: #9ca3af;
}

.sidebar-nav {
  flex: 1;
  padding: 4px 10px;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 8px 10px;
  border-radius: 7px;
  color: #6b7280;
  text-decoration: none;
  transition: background-color 0.12s ease, color 0.12s ease;
}

.nav-item:hover {
  background-color: rgba(17, 24, 39, 0.04);
  color: #111827;
}

.nav-item.active {
  background-color: rgba(17, 24, 39, 0.06);
  color: #111827;
  font-weight: 600;
}

.nav-icon {
  margin-right: 10px;
  display: flex;
  align-items: center;
}

.nav-icon :deep(svg) {
  width: 16px;
  height: 16px;
  opacity: 0.75;
}

.nav-item.active .nav-icon :deep(svg) {
  opacity: 1;
}

.nav-text {
  font-size: 13.5px;
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
  height: 56px;
  background-color: transparent;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 28px;
  flex-shrink: 0;
}

.nav-left h2 {
  margin: 0;
  font-size: 15px;
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
  padding: 7px 10px;
  border: none;
  border-radius: 7px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  background-color: transparent;
  color: #6b7280;
  transition: background-color 0.12s ease, color 0.12s ease;
}

.ghost-btn :deep(svg) {
  width: 14px;
  height: 14px;
}

.ghost-btn:hover {
  background-color: rgba(17, 24, 39, 0.05);
  color: #111827;
}

.ghost-btn.danger:hover {
  background-color: #fef2f2;
  color: #dc2626;
}

.ghost-btn:active {
  transform: translateY(0.5px);
}

.content {
  flex: 1;
  padding: 4px 28px 28px;
  overflow-y: auto;
  box-sizing: border-box;
  min-height: 0;
}
</style>
