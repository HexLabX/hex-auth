<template>
  <div class="clients-page">
    <div class="page-header">
      <h2>客户端管理</h2>
    </div>
    
    <div class="clients-table-wrapper">
      <table class="clients-table">
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
          <tr v-for="client in clients" :key="client.id">
            <td>{{ client.client_fp }}</td>
            <td>{{ client.product_code }}</td>
            <td>{{ client.client_type }}</td>
            <td>{{ client.ip_address || '-' }}</td>
            <td>{{ formatDate(client.last_heartbeat) }}</td>
            <td>
              <span class="status-badge" :class="client.status">
                {{ client.status }}
              </span>
            </td>
            <td>{{ formatDate(client.created_at) }}</td>
            <td class="action-buttons">
              <n-popconfirm 
                v-if="client.status === 'disabled'"
                placement="top"
                positive-text="确定"
                negative-text="取消"
                @positive-click="enableClient(client.id)"
              >
                <template #trigger>
                  <button 
                    class="enable-btn" 
                    :disabled="isLoading"
                  >
                    启用
                  </button>
                </template>
                <template #default>
                  <div>确定要启用该客户端吗？</div>
                </template>
              </n-popconfirm>
              <n-popconfirm 
                v-else
                placement="top"
                positive-text="确定"
                negative-text="取消"
                @positive-click="disableClient(client.id)"
              >
                <template #trigger>
                  <button 
                    class="disable-btn" 
                    :disabled="isLoading"
                  >
                    禁用
                  </button>
                </template>
                <template #default>
                  <div>确定要禁用该客户端吗？</div>
                </template>
              </n-popconfirm>
              <n-popconfirm 
                placement="top"
                positive-text="确定"
                negative-text="取消"
                @positive-click="deleteClient(client.id)"
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
                  <div>确定要删除该客户端吗？</div>
                </template>
              </n-popconfirm>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="clients.length === 0" class="empty-state">
        暂无客户端数据
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NPopconfirm } from 'naive-ui'
import api from '@/api'

// 客户端列表
const clients = ref([])
// 加载状态
const isLoading = ref(false)

// 格式化日期
const formatDate = (dateString: string | null) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString()
}

// 获取客户端列表
const fetchClients = async () => {
  isLoading.value = true
  try {
    // 调用API获取客户端列表
    const response = await api.get('/admin/client')
    clients.value = response
  } catch (error) {
    console.error('Failed to fetch clients:', error)
  } finally {
    isLoading.value = false
  }
}

// 禁用客户端
const disableClient = async (id: number) => {
  isLoading.value = true
  try {
    await api.post(`/admin/client/${id}/disable`)
    // 重新获取客户端列表
    fetchClients()
  } catch (error) {
    console.error('Failed to disable client:', error)
  } finally {
    isLoading.value = false
  }
}

// 启用客户端
const enableClient = async (id: number) => {
  isLoading.value = true
  try {
    await api.post(`/admin/client/${id}/enable`)
    // 重新获取客户端列表
    fetchClients()
  } catch (error) {
    console.error('Failed to enable client:', error)
  } finally {
    isLoading.value = false
  }
}

// 删除客户端
const deleteClient = async (id: number) => {
  isLoading.value = true
  try {
    await api.delete(`/admin/client/${id}`)
    // 重新获取客户端列表
    fetchClients()
  } catch (error) {
    console.error('Failed to delete client:', error)
  } finally {
    isLoading.value = false
  }
}

// 页面挂载时获取客户端列表
onMounted(() => {
  fetchClients()
})
</script>

<style scoped>
.clients-page {
  width: 100%;
}

.page-header {
  margin-bottom: 24px;
}

.clients-table-wrapper {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.clients-table {
  width: 100%;
  border-collapse: collapse;
}

.clients-table th,
.clients-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.clients-table th {
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

.status-badge.normal {
  background-color: #d1fae5;
  color: #065f46;
}

.status-badge.abnormal {
  background-color: #fef3c7;
  color: #92400e;
}

.status-badge.disabled {
  background-color: #fee2e2;
  color: #991b1b;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.enable-btn,
.disable-btn,
.delete-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s ease;
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

.empty-state {
  text-align: center;
  padding: 40px;
  color: #64748b;
  font-size: 16px;
}
</style>