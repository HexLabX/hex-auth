<template>
  <div class="products-page">
    <div class="page-header">
      <h2>产品管理</h2>
      <button class="add-btn" @click="showCreateModal = true">添加产品</button>
    </div>
    
    <div class="products-table-wrapper">
      <table class="products-table">
        <thead>
          <tr>
            <th>产品代码</th>
            <th>产品名称</th>
            <th>心跳间隔</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in products" :key="product.id">
            <td>{{ product.product_code }}</td>
            <td>{{ product.name }}</td>
            <td>{{ product.heartbeat_interval }}秒</td>
            <td>
              <span class="status-badge" :class="product.status">
                {{ product.status }}
              </span>
            </td>
            <td>{{ formatDate(product.created_at) }}</td>
            <td class="action-buttons">
              <button class="edit-btn" @click="openEditModal(product)">编辑</button>
              <n-popconfirm 
                placement="top"
                positive-text="确定"
                negative-text="取消"
                @positive-click="deleteProduct(product.id)"
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
                  <div>确定要删除该产品吗？</div>
                </template>
              </n-popconfirm>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="products.length === 0" class="empty-state">
        暂无产品数据
      </div>
    </div>
    
    <!-- 创建产品模态框 -->
    <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>创建产品</h3>
          <button class="close-btn" @click="showCreateModal = false">×</button>
        </div>
        <form class="modal-form" @submit.prevent="createProduct">
          <div class="form-group">
            <label for="create-product-code">产品代码</label>
            <input 
              type="text" 
              id="create-product-code"
              v-model="createForm.product_code"
              placeholder="请输入产品代码"
              required
            >
          </div>
          <div class="form-group">
            <label for="create-name">产品名称</label>
            <input 
              type="text" 
              id="create-name"
              v-model="createForm.name"
              placeholder="请输入产品名称"
              required
            >
          </div>
          <div class="form-group">
            <label for="create-heartbeat-interval">心跳间隔（秒）</label>
            <input 
              type="number" 
              id="create-heartbeat-interval"
              v-model="createForm.heartbeat_interval"
              placeholder="请输入心跳间隔"
              min="60"
              max="86400"
              required
            >
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
    
    <!-- 编辑产品模态框 -->
    <div v-if="showEditModal" class="modal-overlay" @click="showEditModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>编辑产品</h3>
          <button class="close-btn" @click="showEditModal = false">×</button>
        </div>
        <form class="modal-form" @submit.prevent="updateProduct">
          <div class="form-group">
            <label for="edit-name">产品名称</label>
            <input 
              type="text" 
              id="edit-name"
              v-model="editForm.name"
              placeholder="请输入产品名称"
              required
            >
          </div>
          <div class="form-group">
            <label for="edit-heartbeat-interval">心跳间隔（秒）</label>
            <input 
              type="number" 
              id="edit-heartbeat-interval"
              v-model="editForm.heartbeat_interval"
              placeholder="请输入心跳间隔"
              min="60"
              max="86400"
              required
            >
          </div>
          <div class="form-group">
            <label for="edit-status">状态</label>
            <select id="edit-status" v-model="editForm.status" required>
              <option value="enabled">启用</option>
              <option value="disabled">禁用</option>
            </select>
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
import { ref, onMounted } from 'vue'
import { NPopconfirm } from 'naive-ui'
import api from '@/api'

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
  product_code: '',
  name: '',
  heartbeat_interval: 3600
})

// 编辑表单数据
const editForm = ref({
  id: 0,
  name: '',
  heartbeat_interval: 3600,
  status: 'enabled'
})

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

// 获取产品列表
const fetchProducts = async () => {
  isLoading.value = true
  try {
    // 调用API获取产品列表
    const response = await api.get('/admin/product')
    products.value = response
  } catch (error) {
    console.error('Failed to fetch products:', error)
  } finally {
    isLoading.value = false
  }
}

// 创建产品
const createProduct = async () => {
  isLoading.value = true
  try {
    await api.post('/admin/product', createForm.value)
    showCreateModal.value = false
    // 重置表单
    createForm.value = {
      product_code: '',
      name: '',
      heartbeat_interval: 3600
    }
    // 重新获取产品列表
    fetchProducts()
  } catch (error) {
    console.error('Failed to create product:', error)
  } finally {
    isLoading.value = false
  }
}

// 显示编辑模态框
const openEditModal = (product: any) => {
  editForm.value = {
    id: product.id,
    name: product.name,
    heartbeat_interval: product.heartbeat_interval,
    status: product.status
  }
  showEditModal.value = true
}

// 更新产品
const updateProduct = async () => {
  isLoading.value = true
  try {
    await api.put(`/admin/product/${editForm.value.id}`, editForm.value)
    showEditModal.value = false
    // 重新获取产品列表
    fetchProducts()
  } catch (error) {
    console.error('Failed to update product:', error)
  } finally {
    isLoading.value = false
  }
}

// 删除产品
const deleteProduct = async (id: number) => {
  isLoading.value = true
  try {
    await api.delete(`/admin/product/${id}`)
    // 重新获取产品列表
    fetchProducts()
  } catch (error) {
    console.error('Failed to delete product:', error)
  } finally {
    isLoading.value = false
  }
}

// 页面挂载时获取产品列表
onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.products-page {
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

.products-table-wrapper {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.products-table {
  width: 100%;
  border-collapse: collapse;
}

.products-table th,
.products-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.products-table th {
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

.status-badge.enabled {
  background-color: #d1fae5;
  color: #065f46;
}

.status-badge.disabled {
  background-color: #fee2e2;
  color: #991b1b;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.edit-btn,
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

.delete-btn {
  background-color: #ef4444;
  color: #fff;
}

.delete-btn:hover:not(:disabled) {
  background-color: #dc2626;
}

.delete-btn:disabled {
  background-color: #fecaca;
  cursor: not-allowed;
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
.form-group select {
  width: 100%;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.form-group input:focus,
.form-group select:focus {
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

.confirm-btn:disabled {
  background-color: #93c5fd;
  cursor: not-allowed;
}
</style>