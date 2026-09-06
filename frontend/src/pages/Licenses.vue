<template>
  <div class="licenses-page">
    <div class="page-header">
      <button class="add-btn" @click="openCreateModal">
        <Icon :icon="icons.add" />
        添加授权
      </button>
    </div>

    <!-- 搜索和筛选栏 -->
    <div class="toolbar">
      <div class="search-box">
        <Icon :icon="icons.search" class="search-icon" />
        <input
          v-model="searchText"
          type="text"
          placeholder="搜索授权码或产品代码"
          @input="handleSearch"
        />
      </div>

      <select v-model="statusFilter" class="filter-select" @change="handleFilter">
        <option value="">全部状态</option>
        <option value="unactivated">未激活</option>
        <option value="activated">已激活</option>
        <option value="expired">已过期</option>
        <option value="revoked">已吊销</option>
      </select>

      <select v-model="productFilter" class="filter-select" @change="handleFilter">
        <option value="">全部产品</option>
        <option v-for="product in products" :key="product.product_code" :value="product.product_code">
          {{ product.product_code }}
        </option>
      </select>

      <button class="refresh-btn" @click="fetchLicenses" :disabled="isLoading">
        <Icon :icon="icons.refresh" />
      </button>
    </div>

    <!-- 表格 -->
    <div class="licenses-table-wrapper">
      <!-- 骨架屏 -->
      <TableSkeleton v-if="isLoading && licenses.length === 0" :columns="8" :rows="5" />

      <!-- 空状态 -->
      <div v-else-if="filteredLicenses.length === 0" class="empty-state">
        <Icon :icon="icons.info" class="empty-icon" />
        <p>{{ searchText || statusFilter || productFilter ? '未找到匹配的授权' : '暂无授权数据' }}</p>
        <button v-if="!searchText && !statusFilter && !productFilter" class="empty-action" @click="openCreateModal">
          创建第一个授权
        </button>
      </div>

      <!-- 数据表格 -->
      <table v-else class="licenses-table">
        <thead>
          <tr>
            <th>授权码</th>
            <th>产品</th>
            <th>最大设备数</th>
            <th>过期时间</th>
            <th>状态</th>
            <th>备注</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="license in paginatedLicenses" :key="license.id">
            <td><code>{{ license.license_key }}</code></td>
            <td>{{ license.product_code }}</td>
            <td>{{ license.max_devices }}</td>
            <td>{{ formatDate(license.expire_at) }}</td>
            <td>
              <span class="status-badge" :class="license.status">
                <Icon :icon="getStatusIcon(license.status)" />
                {{ getStatusText(license.status) }}
              </span>
            </td>
            <td>{{ license.remark || '-' }}</td>
            <td>{{ formatDate(license.created_at) }}</td>
            <td class="action-buttons">
              <button class="edit-btn" @click="openEditModal(license)">
                <Icon :icon="icons.edit" />
                编辑
              </button>
              <button
                v-if="license.status !== 'revoked'"
                class="revoke-btn"
                @click="confirmRevoke(license)"
                :disabled="isLoading"
              >
                <Icon :icon="icons.warning" />
                吊销
              </button>
              <button class="delete-btn" @click="confirmDelete(license)" :disabled="isLoading">
                <Icon :icon="icons.delete" />
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 分页 -->
      <div v-if="filteredLicenses.length > pageSize" class="pagination">
        <div class="pagination-info">
          显示 {{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, filteredLicenses.length) }}
          / 共 {{ filteredLicenses.length }} 条
        </div>
        <div class="pagination-controls">
          <button
            class="page-btn"
            :disabled="currentPage === 1"
            @click="currentPage--"
          >
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
          <button
            class="page-btn"
            :disabled="currentPage === totalPages"
            @click="currentPage++"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 创建授权模态框 -->
    <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>创建授权</h3>
          <button class="close-btn" @click="showCreateModal = false">×</button>
        </div>
        <form class="modal-form" @submit.prevent="createLicense">
          <div class="form-group">
            <label for="create-license-key">授权码</label>
            <div class="license-key-input-wrapper">
              <input
                type="text"
                id="create-license-key"
                v-model="createForm.license_key"
                placeholder="请输入授权码"
                required
              >
              <button
                type="button"
                class="regenerate-btn"
                @click="createForm.license_key = generateLicenseKey()"
              >
                <Icon :icon="icons.refresh" />
                重新生成
              </button>
            </div>
          </div>
          <div class="form-group">
            <label for="create-product-code">产品代码</label>
            <select
              id="create-product-code"
              v-model="createForm.product_code"
              required
            >
              <option value="">请选择产品</option>
              <option
                v-for="product in products"
                :key="product.product_code"
                :value="product.product_code"
              >
                {{ product.product_code }} - {{ product.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label for="create-max-devices">最大设备数</label>
            <input
              type="number"
              id="create-max-devices"
              v-model="createForm.max_devices"
              placeholder="请输入最大设备数"
              min="1"
              max="100"
              required
            >
          </div>
          <div class="form-group">
            <label for="create-expire-at">过期时间</label>
            <input
              type="date"
              id="create-expire-at"
              v-model="createForm.expire_at"
              required
            >
          </div>
          <div class="form-group">
            <label for="create-remark">备注</label>
            <textarea
              id="create-remark"
              v-model="createForm.remark"
              placeholder="请输入备注信息"
              rows="3"
            ></textarea>
          </div>
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="showCreateModal = false">取消</button>
            <button type="submit" class="confirm-btn" :disabled="isLoading">
              {{ isLoading ? '创建中...' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 编辑授权模态框 -->
    <div v-if="showEditModal" class="modal-overlay" @click="showEditModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>编辑授权</h3>
          <button class="close-btn" @click="showEditModal = false">×</button>
        </div>
        <form class="modal-form" @submit.prevent="updateLicense">
          <div class="form-group">
            <label for="edit-max-devices">最大设备数</label>
            <input
              type="number"
              id="edit-max-devices"
              v-model="editForm.max_devices"
              placeholder="请输入最大设备数"
              min="1"
              max="100"
              required
            >
          </div>
          <div class="form-group">
            <label for="edit-expire-at">过期时间</label>
            <input
              type="date"
              id="edit-expire-at"
              v-model="editForm.expire_at"
              required
            >
          </div>
          <div class="form-group">
            <label for="edit-remark">备注</label>
            <textarea
              id="edit-remark"
              v-model="editForm.remark"
              placeholder="请输入备注信息"
              rows="3"
            ></textarea>
          </div>
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="showEditModal = false">取消</button>
            <button type="submit" class="confirm-btn" :disabled="isLoading">
              {{ isLoading ? '更新中...' : '更新' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Icon } from '@iconify/vue'
import icons from '@/icons'
import { Message, Dialog } from '@/utils/message'
import api from '@/api'
import TableSkeleton from '@/components/TableSkeleton.vue'

// 授权列表
const licenses = ref<any[]>([])

// 产品列表
const products = ref<any[]>([])

// 加载状态
const isLoading = ref(false)

// 创建模态框状态
const showCreateModal = ref(false)

// 编辑模态框状态
const showEditModal = ref(false)

// 搜索和筛选
const searchText = ref('')
const statusFilter = ref('')
const productFilter = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

// 创建表单数据
const createForm = ref({
  license_key: '',
  product_code: '',
  max_devices: 1,
  expire_at: '',
  remark: ''
})

// 编辑表单数据
const editForm = ref({
  id: 0,
  max_devices: 1,
  expire_at: '',
  remark: ''
})

// 状态映射
const statusMap: Record<string, string> = {
  'unactivated': '未激活',
  'activated': '已激活',
  'expired': '已过期',
  'revoked': '已吊销'
}

// 获取状态文本
const getStatusText = (status: string) => {
  return statusMap[status] || status
}

// 获取状态图标
const getStatusIcon = (status: string) => {
  const iconMap: Record<string, any> = {
    'unactivated': icons.info,
    'activated': icons.check,
    'expired': icons.warning,
    'revoked': icons.stop
  }
  return iconMap[status] || icons.info
}

// 生成授权码（使用加密安全随机数）
const generateLicenseKey = () => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
  const bytes = new Uint8Array(16)
  crypto.getRandomValues(bytes)
  let licenseKey = ''
  for (let i = 0; i < 16; i++) {
    licenseKey += chars.charAt(bytes[i] % chars.length)
  }
  return licenseKey.replace(/(.{4})/g, '$1-').slice(0, -1)
}

// 格式化日期
const formatDate = (dateString: string | Date) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString()
}

// 过滤后的授权
const filteredLicenses = computed(() => {
  let result = licenses.value

  // 搜索过滤
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(l =>
      l.license_key.toLowerCase().includes(search) ||
      l.product_code.toLowerCase().includes(search)
    )
  }

  // 状态过滤
  if (statusFilter.value) {
    result = result.filter(l => l.status === statusFilter.value)
  }

  // 产品过滤
  if (productFilter.value) {
    result = result.filter(l => l.product_code === productFilter.value)
  }

  return result
})

// 总页数
const totalPages = computed(() => Math.ceil(filteredLicenses.value.length / pageSize.value))

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

// 当前页的授权
const paginatedLicenses = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredLicenses.value.slice(start, end)
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

// 获取授权列表
const fetchLicenses = async () => {
  isLoading.value = true
  try {
    const response = await api.get('/admin/license/')
    licenses.value = response
  } catch (error) {
    Message.error('获取授权列表失败')
  } finally {
    isLoading.value = false
  }
}

// 打开创建模态框
const openCreateModal = () => {
  createForm.value.license_key = generateLicenseKey()
  showCreateModal.value = true
}

// 创建授权
const createLicense = async () => {
  isLoading.value = true
  try {
    await api.post('/admin/license/', createForm.value)
    showCreateModal.value = false
    Message.success('授权创建成功')
    createForm.value = {
      license_key: '',
      product_code: '',
      max_devices: 1,
      expire_at: '',
      remark: ''
    }
    fetchLicenses()
  } catch (error) {
    Message.error('授权创建失败')
  } finally {
    isLoading.value = false
  }
}

// 打开编辑模态框
const openEditModal = (license: any) => {
  editForm.value = {
    id: license.id,
    max_devices: license.max_devices,
    expire_at: new Date(license.expire_at).toISOString().split('T')[0],
    remark: license.remark || ''
  }
  showEditModal.value = true
}

// 更新授权
const updateLicense = async () => {
  isLoading.value = true
  try {
    await api.put(`/admin/license/${editForm.value.id}`, editForm.value)
    showEditModal.value = false
    Message.success('授权更新成功')
    fetchLicenses()
  } catch (error) {
    Message.error('授权更新失败')
  } finally {
    isLoading.value = false
  }
}

// 确认吊销
const confirmRevoke = async (license: any) => {
  const confirmed = await Dialog.confirm({
    title: '确认吊销',
    content: `确定要吊销授权 "${license.license_key}" 吗？吊销后该授权将无法使用。`
  })

  if (confirmed) {
    await revokeLicense(license.id)
  }
}

// 吊销授权
const revokeLicense = async (id: number) => {
  isLoading.value = true
  try {
    await api.post(`/admin/license/${id}/revoke`)
    Message.success('授权吊销成功')
    fetchLicenses()
  } catch (error) {
    Message.error('授权吊销失败')
  } finally {
    isLoading.value = false
  }
}

// 确认删除
const confirmDelete = async (license: any) => {
  const confirmed = await Dialog.confirm({
    title: '确认删除',
    content: `确定要删除授权 "${license.license_key}" 吗？此操作不可恢复。`
  })

  if (confirmed) {
    await deleteLicense(license.id)
  }
}

// 删除授权
const deleteLicense = async (id: number) => {
  isLoading.value = true
  try {
    await api.delete(`/admin/license/${id}`)
    Message.success('授权删除成功')
    fetchLicenses()
  } catch (error) {
    Message.error('授权删除失败')
  } finally {
    isLoading.value = false
  }
}

// 页面挂载时获取授权列表和产品列表
onMounted(() => {
  fetchLicenses()
  fetchProducts()
})
</script>

<style scoped>
.licenses-page {
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

.add-btn {
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

.add-btn:hover {
  background-color: #2563eb;
}

.add-btn :deep(svg) {
  width: 16px;
  height: 16px;
}

/* 工具栏 */
.toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 300px;
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
.licenses-table-wrapper {
  background-color: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
  overflow: hidden;
}

.licenses-table {
  width: 100%;
  border-collapse: collapse;
}

.licenses-table th,
.licenses-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.licenses-table th {
  font-weight: 600;
  color: #1e293b;
  background-color: #f8fafc;
}

.licenses-table td code {
  background-color: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  color: #334155;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge :deep(svg) {
  width: 14px;
  height: 14px;
}

.status-badge.unactivated {
  background-color: #fef3c7;
  color: #92400e;
}

.status-badge.activated {
  background-color: #d1fae5;
  color: #065f46;
}

.status-badge.expired {
  background-color: #fee2e2;
  color: #991b1b;
}

.status-badge.revoked {
  background-color: #f3f4f6;
  color: #374151;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.edit-btn,
.revoke-btn,
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

.edit-btn :deep(svg),
.revoke-btn :deep(svg),
.delete-btn :deep(svg) {
  width: 14px;
  height: 14px;
}

.edit-btn {
  background-color: #3b82f6;
  color: #fff;
}

.edit-btn:hover {
  background-color: #2563eb;
}

.revoke-btn {
  background-color: #f59e0b;
  color: #fff;
}

.revoke-btn:hover:not(:disabled) {
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
  margin-bottom: 20px;
}

.empty-action {
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

.empty-action:hover {
  background-color: #2563eb;
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
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
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
  position: sticky;
  top: 0;
  background-color: #fff;
  z-index: 1;
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

.modal-form {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.license-key-input-wrapper {
  display: flex;
  gap: 12px;
}

.license-key-input-wrapper input {
  flex: 1;
}

.regenerate-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background-color: #64748b;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s ease;
  white-space: nowrap;
}

.regenerate-btn:hover {
  background-color: #475569;
}

.regenerate-btn :deep(svg) {
  width: 14px;
  height: 14px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.cancel-btn,
.confirm-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.cancel-btn {
  background-color: #f1f5f9;
  color: #64748b;
}

.cancel-btn:hover {
  background-color: #e2e8f0;
}

.confirm-btn {
  background-color: #3b82f6;
  color: #fff;
}

.confirm-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

.confirm-btn:disabled {
  background-color: #93c5fd;
  cursor: not-allowed;
}
</style>
