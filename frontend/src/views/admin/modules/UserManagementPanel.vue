<template>
  <div class="user-management-panel">
    <!-- 顶部统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon">
          <el-icon :size="24"><UserFilled /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ users.length }}</div>
          <div class="stat-label">总用户</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon active">
          <el-icon :size="24"><Check /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ activeUsers }}</div>
          <div class="stat-label">活跃</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon admin">
          <el-icon :size="24"><Key /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ adminCount }}</div>
          <div class="stat-label">管理员</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon today">
          <el-icon :size="24"><Calendar /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ todayNew }}</div>
          <div class="stat-label">今日新增</div>
        </div>
      </div>
    </div>

    <!-- 标签页 -->
    <el-tabs v-model="activeTab" class="custom-tabs" @tab-change="handleTabChange">
      <el-tab-pane label="用户列表" name="users">
        <template #label>
          <span class="tab-label"><el-icon><UserFilled /></el-icon> 用户列表</span>
        </template>
      </el-tab-pane>
      <el-tab-pane label="操作日志" name="logs">
        <template #label>
          <span class="tab-label"><el-icon><Document /></el-icon> 操作日志 <el-tag v-if="logs.length" type="danger" size="small" round>{{ logs.length }}</el-tag></span>
        </template>
      </el-tab-pane>
    </el-tabs>

    <!-- 用户列表内容 -->
    <Transition name="fade-slide" mode="out-in">
      <div v-if="activeTab === 'users'" key="users" class="tab-content">
        <!-- 工具栏 -->
        <div class="toolbar">
          <div class="search-box">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索用户名 / 邮箱"
              clearable
              @clear="filteredUsers = users"
              @input="filterUsers"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>

          <div class="toolbar-actions">
            <el-button @click="exportUsers" plain class="hidden-xs">
              <el-icon><Download /></el-icon> 导出
            </el-button>
            <el-button 
              type="info" 
              plain 
              :disabled="selectedUsers.length === 0"
              @click="openSendMessageModal(selectedUsers)"
            >
              <el-icon><Message /></el-icon> 群发消息 ({{ selectedUsers.length }})
            </el-button>
            <el-button type="primary" @click="openAddUserModal">
              <el-icon><Plus /></el-icon> 添加用户
            </el-button>
          </div>
        </div>

        <!-- 桌面端表格视图 (屏幕 > 768px) -->
        <div class="desktop-view">
          <el-table
            :data="filteredUsers"
            v-loading="loading"
            style="width: 100%"
            row-key="id"
            :row-class-name="tableRowClassName"
            @selection-change="handleSelectionChange"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column label="用户" min-width="200">
              <template #default="{ row }">
                <div class="user-cell">
                  <el-avatar :size="36" class="user-avatar-gradient">
                    {{ row.username.charAt(0).toUpperCase() }}
                  </el-avatar>
                  <div class="user-info">
                    <div class="username">{{ row.username }}</div>
                    <div class="email">{{ row.email || '未设置邮箱' }}</div>
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="等级" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="levelTagType(row.level)" effect="dark" size="small">
                  Lv.{{ row.level }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="角色" width="120" align="center">
              <template #default="{ row }">
                <el-tag :type="roleTagType(row.role)" size="small">
                  {{ getRoleName(row.role) }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-switch
                  v-model="row.is_active"
                  @change="toggleUserStatus(row)"
                  active-color="#13ce66"
                  inactive-color="#ff4949"
                />
              </template>
            </el-table-column>

            <el-table-column label="注册时间" width="180" align="center">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>

            <el-table-column label="操作" width="180" align="center" fixed="right">
              <template #default="{ row }">
                <div class="action-buttons">
                  <el-tooltip content="编辑" placement="top">
                    <el-button link type="primary" @click="openEditModal(row)">
                      <el-icon><EditPen /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="发送消息" placement="top">
                    <el-button link type="info" @click="openSendMessageModal([row])">
                      <el-icon><Message /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="重置密码" placement="top">
                    <el-button link type="warning" @click="resetPassword(row)">
                      <el-icon><Key /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="删除" placement="top">
                    <el-button link type="danger" @click="deleteUser(row)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 移动端卡片视图 (屏幕 <= 768px) -->
        <div class="mobile-view">
          <div v-if="filteredUsers.length === 0 && !loading" class="empty-state">
            <el-empty description="未找到用户" />
          </div>
          
          <div v-else class="user-cards-container" v-loading="loading">
            <div v-for="user in filteredUsers" :key="user.id" class="mobile-user-card">
              <!-- 卡片头部 -->
              <div class="card-header">
                <div class="card-user-info">
                  <el-avatar :size="40" class="user-avatar-gradient">
                    {{ user.username.charAt(0).toUpperCase() }}
                  </el-avatar>
                  <div class="card-user-text">
                    <div class="card-username">{{ user.username }}</div>
                    <div class="card-email">{{ user.email || '未设置邮箱' }}</div>
                  </div>
                </div>
                <el-tag :type="roleTagType(user.role)" size="small" class="role-tag">
                  {{ getRoleName(user.role) }}
                </el-tag>
              </div>

              <!-- 卡片内容 -->
              <div class="card-body">
                <div class="info-grid">
                  <div class="info-item">
                    <span class="label">等级</span>
                    <el-tag :type="levelTagType(user.level)" effect="dark" size="small">
                      Lv.{{ user.level }}
                    </el-tag>
                  </div>
                  <div class="info-item">
                    <span class="label">注册时间</span>
                    <span class="value">{{ formatDate(user.created_at) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">状态</span>
                    <el-switch
                      v-model="user.is_active"
                      @change="toggleUserStatus(user)"
                      size="small"
                      active-color="#13ce66"
                      inactive-color="#ff4949"
                    />
                  </div>
                </div>
              </div>

              <!-- 卡片底部操作 -->
              <div class="card-footer">
                <el-button size="small" @click="openEditModal(user)">
                  <el-icon><EditPen /></el-icon> 编辑
                </el-button>
                <el-button size="small" type="info" plain @click="openSendMessageModal([user])">
                  <el-icon><Message /></el-icon> 发消息
                </el-button>
                <el-button size="small" type="warning" plain @click="resetPassword(user)">
                  <el-icon><Key /></el-icon> 重置密码
                </el-button>
                <el-button size="small" type="danger" plain @click="deleteUser(user)">
                  <el-icon><Delete /></el-icon> 删除
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 操作日志 -->
    <Transition name="fade-slide" mode="out-in">
      <div v-if="activeTab === 'logs'" key="logs" class="tab-content logs-content">
        <div class="toolbar">
          <div class="toolbar-left">
            <el-button type="danger" plain :disabled="!selectedLogs.length" @click="deleteSelectedLogs">
              <el-icon><Delete /></el-icon> 删除选中 ({{ selectedLogs.length }})
            </el-button>
          </div>
          <div class="toolbar-right">
            <el-button type="warning" plain @click="clearAllLogs">
              <el-icon><DeleteFilled /></el-icon> 清空
            </el-button>
            <el-button plain @click="fetchLogs">
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
          </div>
        </div>

        <div v-loading="logsLoading" class="logs-container">
          <div v-if="!logs.length" class="empty-logs">
            <el-empty description="暂无操作日志" />
          </div>
          <div v-else class="log-item" v-for="log in logs" :key="log.id">
            <div class="log-checkbox">
              <el-checkbox v-model="selectedLogs" :label="log.id" />
            </div>
            <div class="log-icon">
              <el-icon :size="18" :color="logColor(log.action)">
                <component :is="logIcon(log.action)" />
              </el-icon>
            </div>
            <div class="log-main">
              <div class="log-header-row">
                <span class="log-action">{{ log.action }}</span>
                <span class="log-time">{{ formatDate(log.created_at, true) }}</span>
              </div>
              <div class="log-user-row">
                <el-tag size="small" :type="logTagType(log.action)">{{ log.username }}</el-tag>
                <span class="log-desc" v-if="log.details">{{ log.details }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 对话框组件 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑用户' : '创建新用户'"
      width="90%"
      style="max-width: 500px;"
      custom-class="responsive-dialog"
      :close-on-click-modal="false"
      append-to-body
    >
      <el-form :model="form" :rules="rules" ref="userForm" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="isEdit" placeholder="3-20位字母数字下划线">
            <template #prefix><el-icon><User /></el-icon></template>
          </el-input>
        </el-form-item>

        <el-form-item label="邮箱" prop="email" v-if="!isEdit">
          <el-input v-model="form.email" placeholder="用于找回密码（可选）">
            <template #prefix><el-icon><Message /></el-icon></template>
          </el-input>
        </el-form-item>

        <el-form-item label="等级" prop="level">
          <el-input-number v-model="form.level" :min="1" :max="10" :step="1" style="width: 100%" />
          <div class="tip">Lv.10 为最高权限，自动继承所有功能</div>
        </el-form-item>

        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="选择角色" style="width: 100%">
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
            <el-option v-if="currentUser.role === 'super_admin'" label="超级管理员" value="super_admin" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitLoading" @click="submitForm">
            {{ isEdit ? '保存更改' : '立即创建' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 密码弹窗 -->
    <el-dialog
      v-model="passwordModalVisible"
      title="临时密码"
      width="90%"
      style="max-width: 400px;"
      custom-class="password-dialog"
      append-to-body
    >
      <div class="password-content">
        <p class="password-tip">请立即保存以下密码，关闭后无法查看！</p>
        <div class="password-box" @click="copyPassword">
          <span class="password-text">{{ tempPassword }}</span>
          <el-icon class="copy-icon"><CopyDocument /></el-icon>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" size="large" style="width: 100%" @click="passwordModalVisible = false">
          我已保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 发送消息弹窗 -->
    <el-dialog
      v-model="messageModalVisible"
      title="发送消息"
      width="90%"
      style="max-width: 500px;"
      custom-class="message-dialog"
      :close-on-click-modal="false"
      append-to-body
    >
      <el-form :model="messageForm" :rules="messageRules" ref="messageFormRef" label-width="80px">
        <!-- 收件人 -->
        <el-form-item label="收件人" prop="recipients">
          <div class="recipients-tags">
            <el-tag 
              v-for="recipient in messageForm.recipients" 
              :key="recipient.id" 
              type="info" 
              effect="light"
              closable
              @close="removeRecipient(recipient.id)"
            >
              {{ recipient.username }}
            </el-tag>
            <el-tag v-if="messageForm.recipients.length === 0" type="danger" effect="light">
              请选择收件人
            </el-tag>
          </div>
        </el-form-item>

        <!-- 消息标题 -->
        <el-form-item label="标题" prop="title">
          <el-input 
            v-model="messageForm.title" 
            placeholder="请输入消息标题"
          >
            <template #prefix><el-icon><Document /></el-icon></template>
          </el-input>
        </el-form-item>

        <!-- 消息内容 -->
        <el-form-item label="内容" prop="content">
          <el-input 
            v-model="messageForm.content" 
            type="textarea" 
            :rows="4" 
            placeholder="请输入消息内容"
          ></el-input>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="messageModalVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            :loading="sendingMessage"
            @click="sendMessage"
          >
            发送消息
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import request from '@/api/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  UserFilled, User, Document, Plus, EditPen, Key, Delete, Clock, Message, Warning,
  Search, Download, Refresh, Check, Calendar, DeleteFilled, CopyDocument
} from '@element-plus/icons-vue'

const authStore = useAuthStore()
const currentUser = computed(() => authStore.user)

// ==================== 数据 ====================
const loading = ref(false)
const logsLoading = ref(false)
const submitLoading = ref(false)
const sendingMessage = ref(false)
const users = ref([])
const logs = ref([])
const filteredUsers = ref([])
const searchKeyword = ref('')

const activeTab = ref('users')
const dialogVisible = ref(false)
const passwordModalVisible = ref(false)
const messageModalVisible = ref(false)
const isEdit = ref(false)
const tempPassword = ref('')
const selectedLogs = ref([])
const selectedUsers = ref([])
const messageFormRef = ref(null)

// 自定义验证：至少选择一个收件人
const validateRecipients = (rule, value, callback) => {
  if (!Array.isArray(value) || value.length === 0) {
    callback(new Error('请选择至少一个收件人'))
  } else {
    callback()
  }
}

// 消息发送表单
const messageForm = reactive({
  recipients: [],
  title: '',
  content: ''
})

// 消息发送表单验证规则
const messageRules = {
  recipients: [{ validator: validateRecipients, trigger: ['change', 'submit'] }],
  title: [{ required: true, message: '请输入消息标题', trigger: ['blur', 'submit'] }],
  content: [{ required: true, message: '请输入消息内容', trigger: ['blur', 'submit'] }]
}

// ==================== 计算属性 ====================
const activeUsers = computed(() => users.value.filter(u => u.is_active).length)
const adminCount = computed(() => users.value.filter(u => ['admin', 'super_admin'].includes(u.role)).length)
const todayNew = computed(() => {
  const today = new Date().toDateString()
  return users.value.filter(u => new Date(u.created_at).toDateString() === today).length
})

// ==================== 表单 ====================
const form = reactive({
  id: '',
  username: '',
  email: '',
  level: 1,
  role: 'user'
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  level: [{ required: true, message: '请选择等级', trigger: 'change' }]
}

// ==================== 方法 ====================
const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await request.get('/api/users/')
    users.value = res.users || []
    filteredUsers.value = [...users.value]
  } finally {
    loading.value = false
  }
}

const fetchLogs = async () => {
  logsLoading.value = true
  try {
    const res = await request.get('/api/users/logs/all')
    logs.value = (res.logs || []).reverse()
  } finally {
    logsLoading.value = false
  }
}

const handleTabChange = (tab) => {
  if (tab === 'logs' && !logs.value.length) fetchLogs()
}

const filterUsers = () => {
  const kw = searchKeyword.value.toLowerCase()
  filteredUsers.value = users.value.filter(u =>
    u.username.toLowerCase().includes(kw) ||
    (u.email && u.email.toLowerCase().includes(kw))
  )
}

const handleSelectionChange = (val) => {
  selectedUsers.value = val
}

const openAddUserModal = () => {
  isEdit.value = false
  Object.assign(form, { id: '', username: '', email: '', level: 1, role: 'user' })
  dialogVisible.value = true
}

const openEditModal = (user) => {
  isEdit.value = true
  Object.assign(form, { ...user })
  dialogVisible.value = true
}

const submitForm = async () => {
  submitLoading.value = true
  try {
    if (isEdit.value) {
      await request.put(`/api/users/${form.id}/level`, { level: form.level })
      await request.put(`/api/users/${form.id}/role`, { role: form.role })
      ElMessage.success('更新成功')
    } else {
      const res = await request.post('/api/users/', form)
      if (res.temp_password) {
        tempPassword.value = res.temp_password
        passwordModalVisible.value = true
      }
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchUsers()
  } catch (err) {
    ElMessage.error(err.message || '操作失败')
  } finally {
    submitLoading.value = false
  }
}

const deleteUser = async (user) => {
  await ElMessageBox.confirm(`确定永久删除用户 "${user.username}" 吗？`, '警告', { type: 'warning' })
  await request.delete(`/api/users/${user.id}`)
  ElMessage.success('删除成功')
  fetchUsers()
}

const resetPassword = async (user) => {
  await ElMessageBox.confirm(`将为 "${user.username}" 生成新临时密码`, '重置密码', { type: 'warning' })
  const res = await request.post(`/api/users/${user.id}/reset-password`, {})
  tempPassword.value = res.temp_password
  passwordModalVisible.value = true
}

const toggleUserStatus = async (user) => {
  await request.put(`/api/users/${user.id}/status`, { is_active: user.is_active })
  ElMessage.success(user.is_active ? '已启用' : '已禁用')
}

const deleteSelectedLogs = async () => {
  await ElMessageBox.confirm(`删除 ${selectedLogs.value.length} 条日志？`, '确认', { type: 'warning' })
  await request.delete('/api/users/logs', { data: { log_ids: selectedLogs.value } })
  ElMessage.success('删除成功')
  selectedLogs.value = []
  fetchLogs()
}

const clearAllLogs = async () => {
  await ElMessageBox.confirm('确定清空所有操作日志？此操作不可恢复！', '危险操作', { type: 'warning' })
  await request.delete('/api/users/logs/all')
  ElMessage.success('已清空')
  fetchLogs()
}

const copyPassword = () => {
  navigator.clipboard.writeText(tempPassword.value)
  ElMessage.success('密码已复制到剪贴板')
}

const exportUsers = () => {
  ElMessage.info('导出功能开发中，敬请期待~')
}

// ==================== 消息发送相关方法 ====================
// 打开消息发送对话框
const openSendMessageModal = (selectedUsers) => {
  // 清空表单
  messageForm.recipients = [...selectedUsers]
  messageForm.title = ''
  messageForm.content = ''
  messageModalVisible.value = true
}

// 移除收件人
const removeRecipient = (userId) => {
  messageForm.recipients = messageForm.recipients.filter(recipient => recipient.id !== userId)
}

// 发送消息
const sendMessage = async () => {
  try {
    // 表单验证
    await messageFormRef.value.validate()
    
    // 检查收件人数量
    if (messageForm.recipients.length === 0) {
      ElMessage.error('请选择至少一个收件人')
      return
    }
    
    sendingMessage.value = true
    
    // 构造消息发送数据
    const messageData = {
      user_ids: messageForm.recipients.map(recipient => recipient.id),
      title: messageForm.title,
      content: messageForm.content
    }
    
    // 真实 API 调用
    const res = await request.post('/api/messages', messageData)
    
    // 显示成功消息
    if (res.status === 'success') {
      ElMessage.success(res.message || `消息发送成功！已发送给 ${messageForm.recipients.length} 位用户`)
      messageModalVisible.value = false
      
      // 清空表单
      messageForm.recipients = []
      messageForm.title = ''
      messageForm.content = ''
    } else {
      ElMessage.error(res.message || '发送消息失败')
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    if (error.name === 'ValidationError') {
      // 表单验证失败，不显示额外提示
    } else {
      ElMessage.error(error.response?.data?.message || '发送消息失败，请稍后重试')
    }
  } finally {
    sendingMessage.value = false
  }
}

// ==================== 辅助函数 ====================
const getRoleName = (role) => ({ super_admin: '超级管理员', admin: '管理员', user: '普通用户' })[role] || role

const levelTagType = (level) => level >= 8 ? 'danger' : level >= 5 ? 'warning' : 'success'
const roleTagType = (role) => role === 'super_admin' ? 'danger' : role === 'admin' ? 'warning' : 'info'

const formatDate = (date, withTime = false) => {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' }).replace(/\//g, '-').slice(0, withTime ? 19 : 10)
}

const logIcon = (action) => {
  const map = {
    '登录': 'User', '创建用户': 'Plus', '删除用户': 'Delete', '修改权限': 'Key', '重置密码': 'Refresh'
  }
  return map[action] || 'Document'
}

const logColor = (action) => {
  const map = {
    '登录': '#67c23a', '创建用户': '#409eff', '删除用户': '#f56c6c', '修改权限': '#e6a23c', '重置密码': '#909399'
  }
  return map[action] || '#909399'
}

const logTagType = (action) => action.includes('删除') ? 'danger' : action.includes('创建') ? 'success' : 'warning'

const tableRowClassName = ({ row }) => row.role === 'super_admin' ? 'super-admin-row' : ''

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-management-panel {
  width: 100%;
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.stat-icon.active { background: linear-gradient(135deg, #42d392, #13966d); }
.stat-icon.admin { background: linear-gradient(135deg, #f093fb, #f5576c); }
.stat-icon.today { background: linear-gradient(135deg, #4facfe, #00f2fe); }

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

.stat-label {
  font-size: 13px;
  color: #6b7280;
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.search-box {
  width: 280px;
}

.toolbar-actions {
  display: flex;
  gap: 8px;
}

/* 桌面端表格 */
.desktop-view {
  display: block;
}

.mobile-view {
  display: none;
}

:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.04);
}

:deep(.el-table__header th) {
  background: #f9fafb !important;
  color: #374151;
  font-weight: 600;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar-gradient {
  background: linear-gradient(135deg, #818cf8, #c084fc);
  font-weight: 700;
  font-size: 14px;
}

.username {
  font-weight: 600;
  color: #1f2937;
}

.email {
  font-size: 12px;
  color: #9ca3af;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 4px;
}

/* 移动端卡片 */
.mobile-user-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  border: 1px solid #f3f4f6;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.card-user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-user-text {
  display: flex;
  flex-direction: column;
}

.card-username {
  font-weight: 600;
  font-size: 16px;
  color: #1f2937;
}

.card-email {
  font-size: 12px;
  color: #9ca3af;
}

.card-body {
  background: #f9fafb;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 16px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.info-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.info-item .label {
  font-size: 11px;
  color: #9ca3af;
}

.info-item .value {
  font-size: 13px;
  color: #4b5563;
  font-weight: 500;
}

.card-footer {
  display: flex;
  gap: 8px;
}

.card-footer .el-button {
  flex: 1;
}

/* 日志区域 */
.logs-content {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}

.log-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #f3f4f6;
}

.log-item:last-child {
  border-bottom: none;
}

.log-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.log-main {
  flex: 1;
  min-width: 0;
}

.log-header-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.log-action {
  font-weight: 600;
  font-size: 14px;
  color: #374151;
}

.log-time {
  font-size: 12px;
  color: #9ca3af;
}

.log-user-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.log-desc {
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 密码弹窗 */
.password-content {
  text-align: center;
  padding: 10px 0;
}

.password-tip {
  color: #f59e0b;
  font-size: 13px;
  margin-bottom: 12px;
}

.password-box {
  background: #1f2937;
  color: #10b981;
  font-family: monospace;
  font-size: 20px;
  padding: 16px;
  border-radius: 8px;
  position: relative;
  cursor: pointer;
}

.copy-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #6366f1;
}

/* 消息发送弹窗 */
.recipients-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  max-height: 120px;
  overflow-y: auto;
  padding: 8px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.recipients-tags .el-tag {
  margin: 0;
}

/* 响应式媒体查询 */
@media (max-width: 768px) {
  .desktop-view {
    display: none;
  }
  
  .mobile-view {
    display: block;
  }
  
  .stats-cards {
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
  
  .stat-card {
    padding: 12px;
    flex-direction: column;
    text-align: center;
    gap: 8px;
  }
  
  .stat-icon {
    width: 36px;
    height: 36px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .stat-label {
    font-size: 12px;
  }
  
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    width: 100%;
  }
  
  .toolbar-actions {
    justify-content: flex-end;
  }
  
  .hidden-xs {
    display: none;
  }
  
  .logs-content {
    padding: 0;
    background: transparent;
    box-shadow: none;
  }
  
  .log-item {
    background: white;
    border-radius: 8px;
    margin-bottom: 8px;
    border: none;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }
}

@media (max-width: 480px) {
  .stats-cards {
    grid-template-columns: 1fr 1fr;
  }
}
</style>