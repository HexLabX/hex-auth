<template>
  <div class="clients-page">
    <div class="page-header">
      <button class="refresh-btn" @click="fetchClients" :disabled="isLoading">
        <Icon :icon="icons.refresh" />
        刷新
      </button>
    </div>

    <!-- 搜索和筛选栏 -->
    <div class="toolbar">
      <div class="search-box">
        <Icon :icon="icons.search" class="search-icon" />
        <input
          v-model="searchText"
          type="text"
          placeholder="搜索客户端指纹或产品代码"
          @input="handleSearch"
        />
      </div>

      <select v-model="statusFilter" class="filter-select" @change="handleFilter">
        <option value="">全部状态</option>
        <option value="normal">正常</option>
        <option value="abnormal">异常</option>
        <option value="disabled">已禁用</option>
      </select>

      <select v-model="typeFilter" class="filter-select" @change="handleFilter">
        <option value="">全部类型</option>
        <option value="GUI">GUI</option>
        <option value="CLI">CLI</option>
        <option value="SERVICE">SERVICE</option>
        <option value="PLUGIN">PLUGIN</option>
      </select>

      <select v-model="productFilter" class="filter-select" @change="handleFilter">
        <option value="">全部产品</option>
        <option v-for="product in products" :key="product.product_code" :value="product.product_code">
          {{ product.product_code }}
        </option>
      </select>
    </div>

    <!-- 表格 -->
    <div class="clients-table-wrapper">
      <!-- 骨架屏 -->
      <TableSkeleton v-if="isLoading && clients.length === 0" :columns="8" :rows="5" />

      <!-- 空状态 -->
      <div v-else-if="filteredClients.length === 0" class="empty-state">
        <Icon :icon="icons.info" class="empty-icon" />
        <p>{{ searchText || statusFilter || typeFilter || productFilter ? '未找到匹配的客户端' : '暂无客户端数据' }}</p>
      </div>

      <!-- 数据表格 -->
      <table v-else class="clients-table">
        <thead>
          <tr>
            <th>客户端指纹</th>
            <th>产品</th>
            <th>客户端类型</th>
            <th>IP地址</th>
            <th>最后心跳</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="client in paginatedClients" :key="client.id">
            <td><code>{{ client.client_fp }}</code></td>
            <td>{{ client.product_code }}</td>
            <td>
              <span class="type-badge">
                {{ client.client_type }}
              </span>
            </td>
            <td>{{ client.ip_address || '-' }}</td>
            <td>{{ formatDate(client.last_heartbeat) }}</td>
            <td>
              <span class="status-badge" :class="client.status">
                {{ getStatusText(client.status) }}
              </span>
            </td>
            <td>{{ formatDate(client.created_at) }}</td>
            <td class="action-buttons">
              <button
                v-if="client.status === 'disabled'"
                class="enable-btn"
                @click="confirmEnable(client)"
                :disabled="isLoading"
              >
                <Icon :icon="icons.play" />
                启用
              </button>
              <button
                v-else
                class="disable-btn"
                @click="confirmDisable(client)"
                :disabled="isLoading"
              >
                <Icon :icon="icons.stop" />
                禁用
              </button>
              <button class="delete-btn" @click="confirmDelete(client)" :disabled="isLoading">
                <Icon :icon="icons.delete" />
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 分页 -->
      <div v-if="filteredClients.length > pageSize" class="pagination">
        <div class="pagination-info">
          显示 {{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, filteredClients.length) }}
          / 共 {{ filteredClients.length }} 条
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import icons from '@/icons'
import { Message, Dialog } from '@/utils/message'
import api from '@/api'
import TableSkeleton from '@/components/TableSkeleton.vue'

// 客户端列表
const clients = ref<any[]>([])

// 产品列表
const products = ref<any[]>([])

// 加载状态
const isLoading = ref(false)

// 搜索和筛选
const searchText = ref('')
const statusFilter = ref('')
const typeFilter = ref('')
const productFilter = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

// 状态映射
const statusMap: Record<string, string> = {
  'normal': '正常',
  'abnormal': '异常',
  'disabled': '已禁用'
}

// 获取状态文本
const getStatusText = (status: string) => {
  return statusMap[status] || status
}

// 获取状态图标
const getStatusIcon = (status: string) => {
  const iconMap: Record<string, any> = {
    'normal': icons.check,
    'abnormal': icons.warning,
    'disabled': icons.stop
  }
  return iconMap[status] || icons.info
}

// 获取类型图标
const getTypeIcon = (type: string) => {
  const iconMap: Record<string, any> = {
    'GUI': icons.desktop,
    'CLI': icons.desktop,
    'SERVICE': icons.settings,
    'PLUGIN': icons.products
  }
  return iconMap[type] || icons.desktop
}

// 格式化日期
const formatDate = (dateString: string | Date) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString()
}

// 过滤后的客户端
const filteredClients = computed(() => {
  let result = clients.value

  // 搜索过滤
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(c =>
      c.client_fp.toLowerCase().includes(search) ||
      c.product_code.toLowerCase().includes(search)
    )
  }

  // 状态过滤
  if (statusFilter.value) {
    result = result.filter(c => c.status === statusFilter.value)
  }

  // 类型过滤
  if (typeFilter.value) {
    result = result.filter(c => c.client_type === typeFilter.value)
  }

  // 产品过滤
  if (productFilter.value) {
    result = result.filter(c => c.product_code === productFilter.value)
  }

  return result
})

// 总页数
const totalPages = computed(() => Math.ceil(filteredClients.value.length / pageSize.value))

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

// 当前页的客户端
const paginatedClients = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredClients.value.slice(start, end)
})

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
}

// 筛选处理
const handleFilter = () => {
  currentPage.value = 1
}

// 获取产品列表
const fetchProducts = async () => {
  try {
    const response = await api.get('/admin/product/')
    products.value = response
  } catch (error) {
    Message.error('获取产品列表失败')
  }
}

// 获取客户端列表
const fetchClients = async () => {
  isLoading.value = true
  try {
    const response = await api.get('/admin/client/')
    clients.value = response
  } catch (error) {
    Message.error('获取客户端列表失败')
  } finally {
    isLoading.value = false
  }
}

// 确认启用
const confirmEnable = async (client: any) => {
  const confirmed = await Dialog.confirm({
    title: '确认启用',
    content: `确定要启用该客户端吗？`
  })

  if (confirmed) {
    await enableClient(client.id)
  }
}

// 启用客户端
const enableClient = async (id: number) => {
  isLoading.value = true
  try {
    await api.post(`/admin/client/${id}/enable`)
    Message.success('客户端启用成功')
    fetchClients()
  } catch (error) {
    Message.error('客户端启用失败')
  } finally {
    isLoading.value = false
  }
}

// 确认禁用
const confirmDisable = async (client: any) => {
  const confirmed = await Dialog.confirm({
    title: '确认禁用',
    content: `确定要禁用该客户端吗？禁用后该客户端将无法继续使用。`
  })

  if (confirmed) {
    await disableClient(client.id)
  }
}

// 禁用客户端
const disableClient = async (id: number) => {
  isLoading.value = true
  try {
    await api.post(`/admin/client/${id}/disable`)
    Message.success('客户端禁用成功')
    fetchClients()
  } catch (error) {
    Message.error('客户端禁用失败')
  } finally {
    isLoading.value = false
  }
}

// 确认删除
const confirmDelete = async (client: any) => {
  const confirmed = await Dialog.confirm({
    title: '确认删除',
    content: `确定要删除该客户端吗？此操作不可恢复。`
  })

  if (confirmed) {
    await deleteClient(client.id)
  }
}

// 删除客户端
const deleteClient = async (id: number) => {
  isLoading.value = true
  try {
    await api.delete(`/admin/client/${id}`)
    Message.success('客户端删除成功')
    fetchClients()
  } catch (error) {
    Message.error('客户端删除失败')
  } finally {
    isLoading.value = false
  }
}

// 页面挂载时获取数据
onMounted(() => {
  fetchClients()
  fetchProducts()
})
</script>

<style scoped>
.clients-page {
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

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
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

.refresh-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-btn :deep(svg) {
  width: 16px;
  height: 16px;
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

/* 表格容器 */
.clients-table-wrapper {
  background-color: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 6px 8px;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
  overflow: hidden;
}

.clients-table {
  width: 100%;
  border-collapse: collapse;
}

.clients-table th,
.clients-table td {
  padding: 13px 16px;
  text-align: left;
  border-bottom: 1px solid #f0f1f3;
}

.clients-table tbody tr {
  transition: background-color 0.1s ease;
}

.clients-table tbody tr:hover {
  background-color: #fafafa;
}

.clients-table th {
  font-weight: 500;
  font-size: 12.5px;
  color: #9ca3af;
  background-color: transparent;
  white-space: nowrap;
}

.clients-table td code {
  background-color: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  color: #334155;
}

.type-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  background-color: #e0e7ff;
  color: #4338ca;
}

.type-badge :deep(svg) {
  width: 14px;
  height: 14px;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge :deep(svg) {
  width: 14px;
  height: 14px;
}

.status-badge.normal {
  background-color: #ecfdf5;
  color: #047857;
}

.status-badge.abnormal {
  background-color: #fffbeb;
  color: #b45309;
}

.status-badge.disabled {
  background-color: #fef2f2;
  color: #b91c1c;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.enable-btn,
.disable-btn,
.delete-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.enable-btn :deep(svg),
.disable-btn :deep(svg),
.delete-btn :deep(svg) {
  width: 14px;
  height: 14px;
}

.enable-btn {
  background-color: #10b981;
  color: #fff;
}

.enable-btn:hover:not(:disabled) {
  background-color: #059669;
}

.disable-btn {
  background-color: #f59e0b;
  color: #fff;
}

.disable-btn:hover:not(:disabled) {
  background-color: #d97706;
}

.delete-btn {
  background-color: #ef4444;
  color: #fff;
}

.delete-btn:hover:not(:disabled) {
  background-color: #dc2626;
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
</style>
