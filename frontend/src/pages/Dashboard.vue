<template>
  <div class="dashboard">
    <div v-if="isLoading" class="loading-wrapper">
      <CardSkeleton :count="4" />
      <div class="skeleton-activity"></div>
    </div>

    <template v-else>
      <h2>仪表盘</h2>

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
          <div class="stat-trend">
            <span class="trend-up">↑ +10%</span> 较上月
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-header">
            <h3>授权数量</h3>
            <span class="stat-icon"><Icon :icon="icons.licenses" /></span>
          </div>
          <div class="stat-value">{{ stats.licenseCount }}</div>
          <div class="stat-trend">
            <span class="trend-up">↑ +15%</span> 较上月
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-header">
            <h3>活跃实例</h3>
            <span class="stat-icon"><Icon :icon="icons.clients" /></span>
          </div>
          <div class="stat-value">{{ stats.activeClientCount }}</div>
          <div class="stat-trend">
            <span class="trend-down">↓ -5%</span> 较上月
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-header">
            <h3>今日激活</h3>
            <span class="stat-icon"><Icon :icon="icons.check" /></span>
          </div>
          <div class="stat-value">{{ stats.todayActivations }}</div>
          <div class="stat-trend">
            <span class="trend-up">↑ +20%</span> 较昨日
          </div>
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
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
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
  font-size: 24px;
  display: flex;
  align-items: center;
}

.stat-icon :deep(svg) {
  width: 24px;
  height: 24px;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.stat-trend {
  font-size: 14px;
  font-weight: 500;
}

.trend-up {
  color: #10b981;
}

.trend-down {
  color: #ef4444;
}

.recent-activity {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
  background-color: #f8fafc;
  border-radius: 8px;
  transition: all 0.2s ease;
  border-left: 4px solid #ef4444;
}

.health-card.healthy {
  border-left-color: #10b981;
  background-color: #f0fdf4;
}

.health-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.health-icon {
  font-size: 32px;
  margin-right: 16px;
  display: flex;
  align-items: center;
}

.health-icon :deep(svg) {
  width: 32px;
  height: 32px;
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
  font-size: 16px;
  font-weight: 600;
  color: #ef4444;
}

.health-card.healthy .health-status {
  color: #10b981;
}
</style>