<template>
  <div class="audit-logs-page">
    <div class="page-header">
      <h2>审计日志</h2>
      <div class="header-actions">
        <button 
          class="clear-btn" 
          @click="showClearConfirm = true" 
          :disabled="selectedLogs.length === 0"
        >
          清空选中日志 ({{ selectedLogs.length }})
        </button>
        <button 
          class="clear-all-btn" 
          @click="showClearAllConfirm = true" 
          :disabled="auditLogs.length === 0"
        >
          清空所有日志
        </button>
      </div>
    </div>
    
    <div class="audit-logs-table-wrapper">
      <table class="audit-logs-table">
        <thead>
          <tr>
            <th class="checkbox-col">
              <input 
                type="checkbox" 
                id="select-all"
                v-model="selectAll"
                @change="toggleSelectAll"
              />
              <label for="select-all" class="select-all-label">全选</label>
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
          <tr v-for="log in auditLogs" :key="log.id">
            <td class="checkbox-col">
              <input 
                type="checkbox" 
                :id="`log-${log.id}`"
                v-model="selectedLogs"
                :value="log.id"
              />
              <label :for="`log-${log.id}`" class="checkbox-label"></label>
            </td>
            <td>{{ log.admin_username }}</td>
            <td>{{ log.action }}</td>
            <td>{{ log.target_type }}</td>
            <td class="target-id">
              <!-- 根据不同对象类型显示更有意义的信息 -->
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
              <button class="detail-btn" @click="showDetail(log)">查看详情</button>
            </td>
            <td>{{ formatDate(log.created_at) }}</td>
          </tr>
        </tbody>
      </table>
      <div v-if="auditLogs.length === 0" class="empty-state">
        暂无审计日志
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
          <button class="close-btn" @click="showDetailModal = false">关闭</button>
        </div>
      </div>
    </div>
    
    <!-- 清空选中日志确认模态框 -->
    <div v-if="showClearConfirm" class="modal-overlay" @click="showClearConfirm = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>确认清空</h3>
          <button class="close-btn" @click="showClearConfirm = false">×</button>
        </div>
        <div class="modal-body">
          <p>确定要清空选中的 {{ selectedLogs.length }} 条日志吗？</p>
          <p class="warning">此操作不可恢复！</p>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showClearConfirm = false">取消</button>
          <button class="confirm-btn" @click="clearSelectedLogs">确认清空</button>
        </div>
      </div>
    </div>
    
    <!-- 清空所有日志确认模态框 -->
    <div v-if="showClearAllConfirm" class="modal-overlay" @click="showClearAllConfirm = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>确认清空所有日志</h3>
          <button class="close-btn" @click="showClearAllConfirm = false">×</button>
        </div>
        <div class="modal-body">
          <p>确定要清空所有 {{ auditLogs.length }} 条审计日志吗？</p>
          <p class="warning">此操作不可恢复！</p>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showClearAllConfirm = false">取消</button>
          <button class="confirm-btn" @click="clearAllLogs">确认清空</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '@/api'

// 审计日志列表
const auditLogs = ref([])
// 加载状态
const isLoading = ref(false)
// 详情模态框状态
const showDetailModal = ref(false)
// 当前日志详情
const currentLog = ref({ detail: {} })
// 选中的日志ID列表
const selectedLogs = ref<number[]>([])
// 全选状态
const selectAll = ref(false)
// 清空选中日志确认模态框
const showClearConfirm = ref(false)
// 清空所有日志确认模态框
const showClearAllConfirm = ref(false)

// 计算全选状态
const updateSelectAll = () => {
  selectAll.value = auditLogs.value.length > 0 && selectedLogs.value.length === auditLogs.value.length
}

// 监听选中日志变化，更新全选状态
selectedLogs.value = selectedLogs.value
selectedLogs.value.forEach(() => {
  updateSelectAll()
})

// 切换全选状态
const toggleSelectAll = () => {
  if (selectAll.value) {
    // 全选：将所有日志ID加入选中列表
    selectedLogs.value = auditLogs.value.map(log => log.id)
  } else {
    // 取消全选：清空选中列表
    selectedLogs.value = []
  }
}

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString()
}

// 获取审计日志
const fetchAuditLogs = async () => {
  isLoading.value = true
  try {
    // 调用API获取审计日志
    const response = await api.get('/admin/audit')
    auditLogs.value = response
    // 清空选中列表
    selectedLogs.value = []
  } catch (error) {
    console.error('Failed to fetch audit logs:', error)
  } finally {
    isLoading.value = false
  }
}

// 显示日志详情
const showDetail = (log: any) => {
  currentLog.value = log
  showDetailModal.value = true
}

// 清空选中日志
const clearSelectedLogs = async () => {
  if (selectedLogs.value.length === 0) return
  
  try {
    // 调用API清空选中日志
    await api.delete('/admin/audit/clear', {
      params: { log_ids: selectedLogs.value }
    })
    // 重新获取日志列表
    await fetchAuditLogs()
    // 关闭确认模态框
    showClearConfirm.value = false
  } catch (error) {
    console.error('Failed to clear selected logs:', error)
  }
}

// 清空所有日志
const clearAllLogs = async () => {
  try {
    // 调用API清空所有日志
    await api.delete('/admin/audit/clear')
    // 重新获取日志列表
    await fetchAuditLogs()
    // 关闭确认模态框
    showClearAllConfirm.value = false
  } catch (error) {
    console.error('Failed to clear all logs:', error)
  }
}

// 页面挂载时获取审计日志
onMounted(() => {
  fetchAuditLogs()
})
</script>

<style scoped>
.audit-logs-page {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.clear-btn,
.clear-all-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
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

.audit-logs-table-wrapper {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
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

/* 复选框列样式 */
.checkbox-col {
  width: 80px;
  text-align: center;
}

.checkbox-col input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.select-all-label,
.checkbox-label {
  margin-left: 6px;
  font-size: 14px;
  color: #64748b;
  cursor: pointer;
}

.target-id {
  font-weight: 500;
}

.target-id .secondary {
  color: #64748b;
  font-size: 12px;
  font-weight: normal;
  margin-left: 4px;
}

.log-detail {
  white-space: nowrap;
}

.detail-btn {
  padding: 6px 12px;
  background-color: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.detail-btn:hover {
  background-color: #2563eb;
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
  max-width: 600px;
  max-height: 80vh;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
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
  border-radius: 4px;
  overflow: auto;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
  color: #1e293b;
  max-height: 400px;
}

/* 警告文本 */
.warning {
  color: #ef4444;
  font-weight: 500;
  margin-top: 8px;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 确认和取消按钮 */
.cancel-btn,
.confirm-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.cancel-btn {
  background-color: #f1f5f9;
  color: #64748b;
}

.cancel-btn:hover {
  background-color: #e2e8f0;
}

.confirm-btn {
  background-color: #ef4444;
  color: #fff;
}

.confirm-btn:hover {
  background-color: #dc2626;
}
</style>