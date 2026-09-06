<template>
  <div class="dashboard">
    <div v-if="isLoading" class="loading-wrapper">
      <CardSkeleton :count="4" />
      <div class="skeleton-activity"></div>
    </div>

    <template v-else>
      <!-- 服务健康状态 -->
      <div class="health-section">
        <h3>服务健康状态</h3>
        <div class="health-grid">
          <div class="health-card" :class="{ 'healthy': healthStatus.api }">
            <div class="health-icon"><Icon :icon="healthStatus.api ? icons.check : icons.close" /></div>
            <div class="health-content">
              <div class="health-title">API服务</div>
              <div class="health-status">{{ healthStatus.api ? '正常' : '异常' }}</div>
            </div>
          </div>
          <div class="health-card" :class="{ 'healthy': healthStatus.database }">
            <div class="health-icon"><Icon :icon="healthStatus.database ? icons.check : icons.close" /></div>
            <div class="health-content">
              <div class="health-title">数据库</div>
              <div class="health-status">{{ healthStatus.database ? '正常' : '异常' }}</div>
            </div>
          </div>
          <div class="health-card" :class="{ 'healthy': healthStatus.service }">
            <div class="health-icon"><Icon :icon="healthStatus.service ? icons.check : icons.close" /></div>
            <div class="health-content">
              <div class="health-title">授权服务</div>
              <div class="health-status">{{ healthStatus.service ? '正常' : '异常' }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-header">
            <h3>产品数量</h3>
            <span class="stat-icon"><Icon :icon="icons.products" /></span>
          </div>
          <div class="stat-value">{{ stats.productCount }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-header">
            <h3>授权数量</h3>
            <span class="stat-icon"><Icon :icon="icons.licenses" /></span>
          </div>
          <div class="stat-value">{{ stats.licenseCount }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-header">
            <h3>活跃实例</h3>
            <span class="stat-icon"><Icon :icon="icons.clients" /></span>
          </div>
          <div class="stat-value">{{ stats.activeClientCount }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-header">
            <h3>今日激活</h3>
            <span class="stat-icon"><Icon :icon="icons.check" /></span>
          </div>
          <div class="stat-value">{{ stats.todayActivations }}</div>
        </div>
      </div>

      <!-- 近期操作 -->
      <div class="recent-activity">
        <h3>近期操作</h3>
        <div v-if="recentActivities.length > 0" class="activity-list">
          <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
            <div class="activity-icon"><Icon :icon="getActivityIcon(activity.action)" /></div>
            <div class="activity-content">
              <div class="activity-title">{{ activity.title }}</div>
              <div class="activity-time">{{ formatDate(activity.time) }}</div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <Icon :icon="icons.info" class="empty-icon" />
          <p>暂无操作记录</p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import icons from '@/icons'
import api from '@/api'
import CardSkeleton from '@/components/CardSkeleton.vue'

// 统计数据
const stats = ref({
  productCount: 0,
  licenseCount: 0,
  activeClientCount: 0,
  todayActivations: 0
})

// 服务健康状态
const healthStatus = ref({
  api: true,
  database: true,
  service: true
})

// 近期活动
const recentActivities = ref<any[]>([])

// 加载状态
const isLoading = ref(false)

// 获取操作图标
const getActivityIcon = (action: string) => {
  const iconMap: Record<string, any> = {
    '创建': icons.add,
    '更新': icons.edit,
    '删除': icons.delete,
    '登录': icons.user,
    '启用': icons.play,
    '禁用': icons.stop,
    '吊销': icons.warning
  }
  return iconMap[action] || icons.info
}

// 获取统计数据
const fetchStats = async () => {
  isLoading.value = true
  try {
    const response = await api.get('/admin/dashboard/')
    stats.value = response.stats
    healthStatus.value = response.healthStatus
    recentActivities.value = response.recentActivities || []
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  } finally {
    isLoading.value = false
  }
}

// 格式化日期
const formatDate = (dateString: string | Date) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString()
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.dashboard {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.loading-wrapper {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.skeleton-activity {
  background-color: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 20px;
  min-height: 200px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s ease-in-out infinite;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background-color: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.stat-card:hover {
  border-color: #d1d5db;
  box-shadow: 0 4px 12px rgba(16, 24, 40, 0.08);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.stat-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
}

.stat-icon {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  background-color: rgba(37, 99, 235, 0.08);
  color: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon :deep(svg) {
  width: 18px;
  height: 18px;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.recent-activity {
  background-color: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
}

.recent-activity h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background-color: #f8fafc;
  border-radius: 6px;
  transition: background-color 0.2s ease;
}

.activity-item:hover {
  background-color: #e2e8f0;
}

.activity-icon {
  font-size: 20px;
  margin-right: 12px;
  display: flex;
  align-items: center;
}

.activity-icon :deep(svg) {
  width: 20px;
  height: 20px;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 4px;
}

.activity-time {
  font-size: 12px;
  color: #64748b;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #64748b;
}

.empty-icon {
  color: #cbd5e1;
  margin-bottom: 16px;
}

.empty-icon :deep(svg) {
  width: 48px;
  height: 48px;
}

.empty-state p {
  font-size: 14px;
  margin: 0;
}

/* 服务健康状态样式 */
.health-section {
  margin-bottom: 32px;
  background-color: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
}

.health-section h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.health-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.health-card {
  display: flex;
  align-items: center;
  padding: 16px;
  background-color: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.health-card:hover {
  border-color: #d1d5db;
  box-shadow: 0 4px 12px rgba(16, 24, 40, 0.08);
}

.health-icon {
  width: 38px;
  height: 38px;
  border-radius: 9px;
  background-color: #fef2f2;
  color: #dc2626;
  margin-right: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.health-card.healthy .health-icon {
  background-color: #ecfdf5;
  color: #059669;
}

.health-icon :deep(svg) {
  width: 19px;
  height: 19px;
}

.health-content {
  flex: 1;
}

.health-title {
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
  margin-bottom: 4px;
}

.health-status {
  font-size: 15px;
  font-weight: 600;
  color: #dc2626;
}

.health-card.healthy .health-status {
  color: #059669;
}
</style>