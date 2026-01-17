<template>
  <div class="audit-logs-page">
    <div class="page-header">
      <h2>审计日志</h2>
      <div class="header-actions">
        <button
          class="clear-btn"
          @click="confirmClearSelected"
          :disabled="selectedLogs.length === 0"
        >
          <Icon :icon="icons.delete" />
          清空选中 ({{ selectedLogs.length }})
        </button>
        <button
          class="clear-all-btn"
          @click="confirmClearAll"
          :disabled="auditLogs.length === 0"
        >
          <Icon :icon="icons.delete" />
          清空所有
        </button>
      </div>
    </div>

    <!-- 搜索和筛选栏 -->
    <div class="toolbar">
      <div class="search-box">
        <Icon :icon="icons.search" class="search-icon" />
        <input
          v-model="searchText"
          type="text"
          placeholder="搜索用户、操作类型或对象"
          @input="handleSearch"
        />
      </div>

      <select v-model="actionFilter" class="filter-select" @change="handleFilter">
        <option value="">全部操作</option>
        <option value="创建">创建</option>
        <option value="更新">更新</option>
        <option value="删除">删除</option>
        <option value="启用">启用</option>
        <option value="禁用">禁用</option>
        <option value="吊销">吊销</option>
        <option value="登录">登录</option>
        <option value="登出">登出</option>
      </select>

      <select v-model="targetTypeFilter" class="filter-select" @change="handleFilter">
        <option value="">全部对象</option>
        <option value="产品">产品</option>
        <option value="授权">授权</option>
        <option value="客户端实例">客户端实例</option>
        <option value="管理员">管理员</option>
      </select>

      <button class="refresh-btn" @click="fetchAuditLogs" :disabled="isLoading">
        <Icon :icon="icons.refresh" />
      </button>
    </div>

    <!-- 表格 -->
    <div class="audit-logs-table-wrapper">
      <!-- 骨架屏 -->
      <TableSkeleton v-if="isLoading && auditLogs.length === 0" :columns="7" :rows="5" />

      <!-- 空状态 -->
      <div v-else-if="filteredAuditLogs.length === 0" class="empty-state">
        <Icon :icon="icons.info" class="empty-icon" />
        <p>{{ searchText || actionFilter || targetTypeFilter ? '未找到匹配的日志' : '暂无审计日志' }}</p>
      </div>

      <!-- 数据表格 -->
      <table v-else class="audit-logs-table">
        <thead>
          <tr>
            <th class="checkbox-col">
              <div class="select-all-wrapper">
                <input
                  type="checkbox"
                  id="select-all"
                  v-model="selectAll"
                  @change="toggleSelectAll"
                />
                <label for="select-all" class="select-all-label">全选</label>
              </div>
            </th>
            <th>操作用户</th>
            <th>操作类型</th>
            <th>操作对象</th>
            <th>对象ID</th>
            <th>操作详情</th>
            <th>操作时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in paginatedAuditLogs" :key="log.id" :class="{ selected: selectedLogs.includes(log.id) }">
            <td class="checkbox-col">
              <input
                type="checkbox"
                :id="`log-${log.id}`"
                v-model="selectedLogs"
                :value="log.id"
              />
              <label :for="`log-${log.id}`" class="checkbox-label"></label>
            </td>
            <td>
              <span class="user-badge">
                <Icon :icon="icons.user" />
                {{ log.admin_username }}
              </span>
            </td>
            <td>
              <span class="action-badge" :class="getActionClass(log.action)">
                <Icon :icon="getActionIcon(log.action)" />
                {{ log.action }}
              </span>
            </td>
            <td>{{ log.target_type }}</td>
            <td class="target-id">
              <template v-if="log.target_type === '产品'">
                {{ log.detail?.name || log.target_id }}
                <span class="secondary">({{ log.detail?.product_code }})</span>
              </template>
              <template v-else-if="log.target_type === '授权'">
                {{ log.detail?.license_key || log.target_id }}
                <span class="secondary">({{ log.detail?.product_code }})</span>
              </template>
              <template v-else-if="log.target_type === '客户端实例'">
                {{ log.detail?.client_key || log.target_id }}
                <span class="secondary">({{ log.detail?.product_code }})</span>
              </template>
              <template v-else-if="log.target_type === '管理员'">
                {{ log.detail?.username || log.target_id }}
              </template>
              <template v-else>
                {{ log.target_id }}
              </template>
            </td>
            <td class="log-detail">
              <button class="detail-btn" @click="showDetail(log)">
                <Icon :icon="icons.view" />
                查看详情
              </button>
            </td>
            <td>{{ formatDate(log.created_at) }}</td>
          </tr>
        </tbody>
      </table>

      <!-- 分页 -->
      <div v-if="filteredAuditLogs.length > pageSize" class="pagination">
        <div class="pagination-info">
          显示 {{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, filteredAuditLogs.length) }}
          / 共 {{ filteredAuditLogs.length }} 条
        </div>
        <div class="pagination-controls">
          <button class="page-btn" :disabled="currentPage === 1" @click="currentPage--">
            上一页
          </button>
          <span class="page-numbers">
            <button
              v-for="page in visiblePages"
              :key="page"
              class="page-number"
              :class="{ active: page === currentPage }"
              @click="currentPage = page"
            >
              {{ page }}
            </button>
          </span>
          <button class="page-btn" :disabled="currentPage === totalPages" @click="currentPage++">
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 日志详情模态框 -->
    <div v-if="showDetailModal" class="modal-overlay" @click="showDetailModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>操作详情</h3>
          <button class="close-btn" @click="showDetailModal = false">×</button>
        </div>
        <div class="modal-body">
          <pre class="detail-content">{{ JSON.stringify(currentLog.detail, null, 2) }}</pre>
        </div>
        <div class="modal-footer">
          <button class="modal-btn" @click="showDetailModal = false">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import icons from '@/icons'
import { Message, Dialog } from '@/utils/message'
import api from '@/api'
import TableSkeleton from '@/components/TableSkeleton.vue'

// 审计日志列表
const auditLogs = ref<any[]>([])

// 选中的日志
const selectedLogs = ref<number[]>([])

// 加载状态
const isLoading = ref(false)

// 搜索和筛选
const searchText = ref('')
const actionFilter = ref('')
const targetTypeFilter = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(20)

// 模态框状态
const showDetailModal = ref(false)
const currentLog = ref<any>({})

// 全选
const selectAll = ref(false)

// 获取操作图标
const getActionIcon = (action: string) => {
  const iconMap: Record<string, any> = {
    '创建': icons.add,
    '更新': icons.edit,
    '删除': icons.delete,
    '启用': icons.play,
    '禁用': icons.stop,
    '吊销': icons.warning,
    '登录': icons.login,
    '登出': icons.logout
  }
  return iconMap[action] || icons.info
}

// 获取操作样式类
const getActionClass = (action: string) => {
  const classMap: Record<string, string> = {
    '创建': 'create',
    '更新': 'update',
    '删除': 'delete',
    '启用': 'enable',
    '禁用': 'disable',
    '吊销': 'revoke',
    '登录': 'login',
    '登出': 'logout'
  }
  return classMap[action] || 'default'
}

// 格式化日期
const formatDate = (dateString: string | Date) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString()
}

// 过滤后的日志
const filteredAuditLogs = computed(() => {
  let result = auditLogs.value

  // 搜索过滤
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(l =>
      l.admin_username.toLowerCase().includes(search) ||
      l.action.toLowerCase().includes(search) ||
      l.target_type.toLowerCase().includes(search) ||
      l.target_id.toString().includes(search)
    )
  }

  // 操作类型过滤
  if (actionFilter.value) {
    result = result.filter(l => l.action === actionFilter.value)
  }

  // 对象类型过滤
  if (targetTypeFilter.value) {
    result = result.filter(l => l.target_type === targetTypeFilter.value)
  }

  return result
})

// 总页数
const totalPages = computed(() => Math.ceil(filteredAuditLogs.value.length / pageSize.value))

// 可见页码
const visiblePages = computed(() => {
  const pages: number[] = []
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages.value, start + maxVisible - 1)

  if (end - start < maxVisible - 1) {
    start = Math.max(1, end - maxVisible + 1)
  }

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  return pages
})

// 当前页的日志
const paginatedAuditLogs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredAuditLogs.value.slice(start, end)
})

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
}

// 筛选处理
const handleFilter = () => {
  currentPage.value = 1
}

// 全选/取消全选
const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedLogs.value = paginatedAuditLogs.value.map(l => l.id)
  } else {
    selectedLogs.value = []
  }
}

// 获取审计日志
const fetchAuditLogs = async () => {
  isLoading.value = true
  try {
    const response = await api.get('/admin/audit/')
    auditLogs.value = response
  } catch (error) {
    Message.error('获取审计日志失败')
  } finally {
    isLoading.value = false
  }
}

// 显示详情
const showDetail = (log: any) => {
  currentLog.value = log
  showDetailModal.value = true
}

// 确认清空选中
const confirmClearSelected = async () => {
  const confirmed = await Dialog.confirm({
    title: '确认清空',
    content: `确定要清空选中的 ${selectedLogs.value.length} 条日志吗？此操作不可恢复！`
  })

  if (confirmed) {
    await clearSelectedLogs()
  }
}

// 清空选中的日志
const clearSelectedLogs = async () => {
  isLoading.value = true
  try {
    console.log('清空选中的日志:', selectedLogs.value)
    const response = await api.post('/admin/audit/clear', { log_ids: selectedLogs.value })
    console.log('清空选中响应:', response)
    Message.success('清空成功')
    selectedLogs.value = []
    selectAll.value = false
    fetchAuditLogs()
  } catch (error: any) {
    console.error('清空选中失败:', error)
    console.error('错误详情:', error.response?.data)
    Message.error(error.response?.data?.detail || '清空失败')
  } finally {
    isLoading.value = false
  }
}

// 确认清空所有
const confirmClearAll = async () => {
  const confirmed = await Dialog.confirm({
    title: '确认清空所有日志',
    content: `确定要清空所有 ${auditLogs.value.length} 条审计日志吗？此操作不可恢复！`
  })

  if (confirmed) {
    await clearAllLogs()
  }
}

// 清空所有日志
const clearAllLogs = async () => {
  isLoading.value = true
  try {
    console.log('清空所有日志')
    const response = await api.post('/admin/audit/clear-all')
    console.log('清空所有响应:', response)
    Message.success('清空成功')
    fetchAuditLogs()
  } catch (error: any) {
    console.error('清空所有失败:', error)
    console.error('错误详情:', error.response?.data)
    Message.error(error.response?.data?.detail || '清空失败')
  } finally {
    isLoading.value = false
  }
}

// 页面挂载时获取数据
onMounted(() => {
  fetchAuditLogs()
})
</script>

<style scoped>
.audit-logs-page {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.clear-btn,
.clear-all-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.clear-btn :deep(svg),
.clear-all-btn :deep(svg) {
  width: 14px;
  height: 14px;
}

.clear-btn {
  background-color: #f59e0b;
  color: #fff;
}

.clear-btn:hover:not(:disabled) {
  background-color: #d97706;
}

.clear-all-btn {
  background-color: #ef4444;
  color: #fff;
}

.clear-all-btn:hover:not(:disabled) {
  background-color: #dc2626;
}

.clear-btn:disabled,
.clear-all-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 工具栏 */
.toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 250px;
  max-width: 350px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
}

.search-icon :deep(svg) {
  width: 16px;
  height: 16px;
}

.search-box input {
  width: 100%;
  padding: 10px 12px 10px 36px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.search-box input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.filter-select {
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  background-color: #fff;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.filter-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.refresh-btn {
  padding: 10px;
  background-color: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.refresh-btn:hover:not(:disabled) {
  background-color: #f8fafc;
  border-color: #3b82f6;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-btn :deep(svg) {
  width: 16px;
  height: 16px;
}

/* 表格容器 */
.audit-logs-table-wrapper {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.audit-logs-table {
  width: 100%;
  border-collapse: collapse;
}

.audit-logs-table th,
.audit-logs-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.audit-logs-table th {
  font-weight: 600;
  color: #1e293b;
  background-color: #f8fafc;
}

.audit-logs-table tr.selected {
  background-color: #eff6ff;
}

.checkbox-col {
  width: 80px;
  min-width: 80px;
}

.select-all-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
}

.select-all-label,
.checkbox-label {
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}

.user-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
  background-color: #e0f2fe;
  color: #0369a1;
}

.user-badge :deep(svg) {
  width: 14px;
  height: 14px;
}

.action-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.action-badge :deep(svg) {
  width: 14px;
  height: 14px;
}

.action-badge.create {
  background-color: #d1fae5;
  color: #065f46;
}

.action-badge.update {
  background-color: #dbeafe;
  color: #1e40af;
}

.action-badge.delete {
  background-color: #fee2e2;
  color: #991b1b;
}

.action-badge.enable {
  background-color: #d1fae5;
  color: #065f46;
}

.action-badge.disable {
  background-color: #fef3c7;
  color: #92400e;
}

.action-badge.revoke {
  background-color: #f3e8ff;
  color: #6b21a8;
}

.action-badge.login {
  background-color: #e0e7ff;
  color: #4338ca;
}

.action-badge.logout {
  background-color: #f1f5f9;
  color: #475569;
}

.target-id {
  font-size: 13px;
}

.target-id .secondary {
  color: #64748b;
  margin-left: 4px;
}

.detail-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background-color: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.detail-btn :deep(svg) {
  width: 14px;
  height: 14px;
}

.detail-btn:hover {
  background-color: #2563eb;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #64748b;
}

.empty-icon {
  color: #cbd5e1;
  margin-bottom: 16px;
}

.empty-icon :deep(svg) {
  width: 64px;
  height: 64px;
}

.empty-state p {
  font-size: 16px;
  margin: 0;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.pagination-info {
  font-size: 14px;
  color: #64748b;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-btn {
  padding: 6px 12px;
  background-color: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.page-btn:hover:not(:disabled) {
  background-color: #f8fafc;
  border-color: #3b82f6;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 4px;
}

.page-number {
  min-width: 32px;
  height: 32px;
  padding: 6px;
  background-color: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.page-number:hover {
  background-color: #f8fafc;
  border-color: #3b82f6;
}

.page-number.active {
  background-color: #3b82f6;
  border-color: #3b82f6;
  color: #fff;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal {
  background-color: #fff;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.2s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #64748b;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.close-btn:hover {
  background-color: #f1f5f9;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.detail-content {
  background-color: #f8fafc;
  padding: 16px;
  border-radius: 6px;
  font-size: 13px;
  color: #334155;
  overflow-x: auto;
  margin: 0;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.modal-btn {
  padding: 10px 20px;
  background-color: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.modal-btn:hover {
  background-color: #2563eb;
}
</style>
