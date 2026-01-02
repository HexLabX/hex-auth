<template>
  <div class="licenses-page">
    <div class="page-header">
      <h2>授权管理</h2>
      <button class="add-btn" @click="showCreateModal = true">添加授权</button>
    </div>
    
    <div class="licenses-table-wrapper">
      <table class="licenses-table">
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
          <tr v-for="license in licenses" :key="license.id">
            <td>{{ license.license_key }}</td>
            <td>{{ license.product_code }}</td>
            <td>{{ license.max_devices }}</td>
            <td>{{ formatDate(license.expire_at) }}</td>
            <td>
              <span class="status-badge" :class="license.status">
                {{ license.status }}
              </span>
            </td>
            <td>{{ license.remark || '-' }}</td>
            <td>{{ formatDate(license.created_at) }}</td>
            <td class="action-buttons">
              <button class="edit-btn" @click="openEditModal(license)">编辑</button>
              <n-popconfirm 
                placement="top"
                positive-text="确定"
                negative-text="取消"
                @positive-click="revokeLicense(license.id)"
              >
                <template #trigger>
                  <button 
                    v-if="license.status !== 'revoked'" 
                    class="revoke-btn" 
                    :disabled="isLoading"
                  >
                    吊销
                  </button>
                </template>
                <template #default>
                  <div>确定要吊销该授权吗？</div>
                </template>
              </n-popconfirm>
              <n-popconfirm 
                placement="top"
                positive-text="确定"
                negative-text="取消"
                @positive-click="deleteLicense(license.id)"
              >
                <template #trigger>
                  <button 
                    class="delete-btn" 
                    :disabled="isLoading"
                  >
                    删除
                  </button>
                </template>
                <template #default>
                  <div>确定要删除该授权吗？</div>
                </template>
              </n-popconfirm>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="licenses.length === 0" class="empty-state">
        暂无授权数据
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
import { ref, onMounted, watch } from 'vue'
import { NDialog, NButton, NCard, NPopconfirm } from 'naive-ui'
import api from '@/api'

// 授权列表
const licenses = ref([])
// 产品列表
const products = ref([])
// 加载状态
const isLoading = ref(false)
// 创建模态框状态
const showCreateModal = ref(false)
// 编辑模态框状态
const showEditModal = ref(false)

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

// 生成授权码
const generateLicenseKey = () => {
  // 生成16位随机字符串作为授权码
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
  let licenseKey = ''
  for (let i = 0; i < 16; i++) {
    licenseKey += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  // 每4位添加一个连字符
  return licenseKey.replace(/(.{4})/g, '$1-').slice(0, -1)
}

// 获取产品列表
const fetchProducts = async () => {
  try {
    const response = await api.get('/admin/product')
    products.value = response
  } catch (error) {
    console.error('Failed to fetch products:', error)
  }
}

// 格式化日期
const formatDate = (dateString: string | Date) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString()
}

// 获取授权列表
const fetchLicenses = async () => {
  isLoading.value = true
  try {
    // 调用API获取授权列表
    const response = await api.get('/admin/license')
    licenses.value = response
  } catch (error) {
    console.error('Failed to fetch licenses:', error)
  } finally {
    isLoading.value = false
  }
}

// 创建授权
const createLicense = async () => {
  isLoading.value = true
  try {
    await api.post('/admin/license', createForm.value)
    showCreateModal.value = false
    // 重置表单
    createForm.value = {
      license_key: '',
      product_code: '',
      max_devices: 1,
      expire_at: '',
      remark: ''
    }
    // 重新获取授权列表
    fetchLicenses()
  } catch (error) {
    console.error('Failed to create license:', error)
  } finally {
    isLoading.value = false
  }
}

// 显示编辑模态框
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
    // 重新获取授权列表
    fetchLicenses()
  } catch (error) {
    console.error('Failed to update license:', error)
  } finally {
    isLoading.value = false
  }
}

// 吊销授权
const revokeLicense = async (id: number) => {
  isLoading.value = true
  try {
    await api.post(`/admin/license/${id}/revoke`)
    // 重新获取授权列表
    fetchLicenses()
  } catch (error) {
    console.error('Failed to revoke license:', error)
  } finally {
    isLoading.value = false
  }
}

// 删除授权
const deleteLicense = async (id: number) => {
  isLoading.value = true
  try {
    await api.delete(`/admin/license/${id}`)
    // 重新获取授权列表
    fetchLicenses()
  } catch (error) {
    console.error('Failed to delete license:', error)
  } finally {
    isLoading.value = false
  }
}

// 监听创建模态框显示状态，自动生成授权码
watch(showCreateModal, (newValue) => {
  if (newValue) {
    // 打开模态框时自动生成授权码
    createForm.value.license_key = generateLicenseKey()
  }
})

// 页面挂载时获取授权列表和产品列表
onMounted(() => {
  fetchLicenses()
  fetchProducts()
})
</script>

<style scoped>
.licenses-page {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.add-btn {
  padding: 8px 16px;
  background-color: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.add-btn:hover {
  background-color: #2563eb;
}

.licenses-table-wrapper {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
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

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
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
}

.edit-btn,
.revoke-btn,
.delete-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s ease;
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

.empty-state {
  text-align: center;
  padding: 40px;
  color: #64748b;
  font-size: 16px;
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
}

.modal {
  background-color: #fff;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
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
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.license-key-input-wrapper {
  display: flex;
  gap: 12px;
}

.license-key-input-wrapper input {
  flex: 1;
}

.regenerate-btn {
  padding: 8px 16px;
  background-color: #64748b;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s ease;
  align-self: flex-start;
}

.regenerate-btn:hover {
  background-color: #475569;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
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
  border-radius: 4px;
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
</style>