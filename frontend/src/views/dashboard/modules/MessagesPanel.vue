<template>
  <div class="messages-panel">
    <!-- 头部区域 -->
    <div class="messages-header">
      <h2>站内消息</h2>
      <div class="header-actions">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索消息"
          clearable
          @input="filterMessages"
          style="width: 240px; margin-right: 12px;"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button
          type="primary"
          plain
          :disabled="filteredMessages.length === 0"
          @click="toggleSelectAll"
          style="margin-right: 12px;"
        >
          <el-icon><Check /></el-icon> {{ isAllSelected ? '取消全选' : '全选' }}
        </el-button>
        <el-button
          type="warning"
          plain
          :disabled="filteredMessages.length === 0"
          @click="reverseSelect"
          style="margin-right: 12px;"
        >
          <el-icon><RefreshLeft /></el-icon> 反选
        </el-button>
        <el-button
          type="danger"
          plain
          :disabled="selectedMessages.length === 0"
          @click="deleteSelectedMessages"
        >
          <el-icon><Delete /></el-icon> 批量删除
        </el-button>
      </div>
    </div>

    <!-- 标签页 -->
    <el-tabs v-model="activeTab" class="messages-tabs" @tab-change="handleTabChange">
      <el-tab-pane label="收件箱" name="inbox">
        <template #label>
          <span><el-icon><Message /></el-icon> 收件箱 <el-tag v-if="unreadCount > 0" type="danger" size="small" round>{{ unreadCount }}</el-tag></span>
        </template>
      </el-tab-pane>
      <el-tab-pane label="已发送" name="sent">
        <template #label>
          <span><el-icon><Message /></el-icon> 已发送</span>
        </template>
      </el-tab-pane>
    </el-tabs>

    <!-- 消息列表 -->
    <div class="messages-container" v-loading="loading">
      <div v-if="filteredMessages.length === 0 && !loading" class="empty-messages">
        <el-empty description="暂无消息" />
      </div>
      <div v-else class="messages-list">
        <div
          v-for="message in filteredMessages"
          :key="message.id"
          class="message-item"
          :class="{ 'read': message.is_read, 'unread': !message.is_read }"
          @click="viewMessage(message)"
        >
          <div class="message-checkbox">
            <el-checkbox-group v-model="selectedMessages">
              <el-checkbox :label="message.id" />
            </el-checkbox-group>
          </div>
          <div class="message-indicator">
            <div v-if="!message.is_read" class="unread-dot"></div>
          </div>
          <div class="message-content">
            <div class="message-header">
              <span class="message-sender">{{ message.sender_name || '系统' }}</span>
              <span class="message-time">{{ formatDate(message.created_at) }}</span>
            </div>
            <div class="message-title">{{ message.title }}</div>
            <div class="message-preview">{{ message.content }}</div>
          </div>
          <div class="message-actions">
            <el-button
              link
              :type="message.is_read ? 'primary' : 'info'"
              @click.stop="toggleReadStatus(message)"
            >
              <el-icon>
                <Message v-if="message.is_read" />
                <ChatDotRound v-else />
              </el-icon>
              {{ message.is_read ? '标为未读' : '标为已读' }}
            </el-button>
            <el-button
              link
              type="danger"
              @click.stop="deleteMessage(message.id)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="messages-pagination" v-if="filteredMessages.length > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="filteredMessages.length"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 消息详情弹窗 -->
    <el-dialog
      v-model="messageDetailVisible"
      :title="selectedMessage?.title || '消息详情'"
      width="90%"
      style="max-width: 600px;"
      custom-class="message-detail-dialog"
      :close-on-click-modal="false"
      append-to-body
    >
      <div class="message-detail" v-if="selectedMessage">
        <div class="detail-header">
          <div class="detail-meta">
            <span class="detail-sender">发件人：{{ selectedMessage.sender_name || '系统' }}</span>
            <span class="detail-time">{{ formatDate(selectedMessage.created_at, true) }}</span>
          </div>
          <el-tag :type="selectedMessage.is_read ? 'info' : 'primary'" size="small">
            {{ selectedMessage.is_read ? '已读' : '未读' }}
          </el-tag>
        </div>
        <div class="detail-content">
          {{ selectedMessage.content }}
        </div>
      </div>
      
      <!-- 回复表单 -->
      <div v-if="replyVisible" class="reply-form">
        <el-divider>回复消息</el-divider>
        <el-form :model="replyForm" :rules="replyRules" ref="replyFormRef" label-width="80px">
          <el-form-item label="标题" prop="title">
            <el-input v-model="replyForm.title" placeholder="请输入回复标题" />
          </el-form-item>
          <el-form-item label="内容" prop="content">
            <el-input
              v-model="replyForm.content"
              type="textarea"
              :rows="4"
              placeholder="请输入回复内容"
            />
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="messageDetailVisible = false">关闭</el-button>
          <el-button
            v-if="activeTab === 'inbox' && !replyVisible"
            type="success"
            @click="showReplyForm"
          >
            <el-icon><ChatRound /></el-icon> 回复
          </el-button>
          <template v-else-if="replyVisible">
            <el-button @click="hideReplyForm">取消回复</el-button>
            <el-button
              type="primary"
              @click="handleReply"
              :loading="replyLoading"
            >
              <el-icon><ChatRound /></el-icon> 发送回复
            </el-button>
          </template>
          <el-button
            :type="selectedMessage?.is_read ? 'info' : 'primary'"
            @click="toggleReadStatus(selectedMessage)"
            v-if="activeTab === 'inbox'"
          >
            {{ selectedMessage?.is_read ? '标为未读' : '标为已读' }}
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
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import { Message, Search, Delete, ChatDotRound, Check, RefreshLeft, ChatRound } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const isAdmin = computed(() => {
  const role = authStore.user?.role
  return role === 'admin' || role === 'super_admin'
})

// 数据
const loading = ref(false)
const messages = ref([])
const filteredMessages = ref([])
const searchKeyword = ref('')
const activeTab = ref('inbox')
const currentPage = ref(1)
const pageSize = ref(10)
const selectedMessages = ref([])
const selectedMessage = ref(null)
const messageDetailVisible = ref(false)

// 回复功能数据
const replyVisible = ref(false)
const replyLoading = ref(false)
const replyForm = ref({
  title: '',
  content: ''
})
const replyFormRef = ref(null)
const replyRules = {
  title: [
    { required: true, message: '请输入回复标题', trigger: 'blur' },
    { max: 100, message: '标题不能超过100个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入回复内容', trigger: 'blur' },
    { max: 1000, message: '内容不能超过1000个字符', trigger: 'blur' }
  ]
}

// 数据
const unreadCount = ref(0)

// 计算属性
const computedUnreadCount = computed(() => messages.value.filter(m => m.is_read === false && m.sender_id !== authStore.user?.id).length)

// 全选状态
const isAllSelected = computed(() => {
  if (filteredMessages.value.length === 0) return false
  return selectedMessages.value.length === filteredMessages.value.length
})

// 过滤后的消息（带分页）
const paginatedMessages = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredMessages.value.slice(start, end)
})

// 方法
const fetchMessages = async () => {
  loading.value = true
  try {
    // 获取所有消息（收件箱和已发送）
    const [inboxRes, sentRes] = await Promise.all([
      request.get('/api/messages', {
        params: {
          type: 'inbox',
          limit: 50,
          offset: 0
        }
      }),
      request.get('/api/messages', {
        params: {
          type: 'sent',
          limit: 50,
          offset: 0
        }
      })
    ])
    
    // 合并收件箱和已发送消息
    const inboxMessages = inboxRes.status === 'success' ? inboxRes.data || [] : []
    const sentMessages = sentRes.status === 'success' ? sentRes.data || [] : []
    messages.value = [...inboxMessages, ...sentMessages]
    
    // 更新未读计数
    unreadCount.value = inboxRes.unread_count || computedUnreadCount.value
    
    filterMessages()
  } catch (error) {
    console.error('获取消息失败:', error)
    ElMessage.error(error.response?.data?.message || '获取消息失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const filterMessages = () => {
  let filtered = [...messages.value]
  
  // 根据标签页筛选
  if (activeTab.value === 'inbox') {
    filtered = filtered.filter(m => m.recipient_id === authStore.user?.id)
  } else if (activeTab.value === 'sent') {
    filtered = filtered.filter(m => m.sender_id === authStore.user?.id)
  }
  
  // 搜索筛选
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(m => 
      m.title.toLowerCase().includes(keyword) || 
      m.content.toLowerCase().includes(keyword) ||
      (m.sender_name && m.sender_name.toLowerCase().includes(keyword))
    )
  }
  
  // 按时间倒序排序
  filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  
  filteredMessages.value = filtered
}

// 标签页切换处理
const handleTabChange = () => {
  filterMessages()
}

// 全选/取消全选
const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedMessages.value = []
  } else {
    selectedMessages.value = filteredMessages.value.map(m => m.id)
  }
}

// 反选
const reverseSelect = () => {
  const allIds = filteredMessages.value.map(m => m.id)
  const selectedIds = new Set(selectedMessages.value)
  const newSelected = allIds.filter(id => !selectedIds.has(id))
  selectedMessages.value = newSelected
}

const viewMessage = (message) => {
  selectedMessage.value = message
  messageDetailVisible.value = true
  replyVisible.value = false
  replyForm.value = {
    title: `回复: ${message.title}`,
    content: ''
  }
  
  // 标记为已读
  if (!message.is_read && activeTab.value === 'inbox') {
    markAsRead(message)
  }
}

// 显示回复表单
const showReplyForm = () => {
  replyVisible.value = true
}

// 隐藏回复表单
const hideReplyForm = () => {
  replyVisible.value = false
  replyForm.value = {
    title: '',
    content: ''
  }
  if (replyFormRef.value) {
    replyFormRef.value.resetFields()
  }
}

// 处理回复
const handleReply = async () => {
  if (!replyFormRef.value) return
  
  await replyFormRef.value.validate(async (valid) => {
    if (valid && selectedMessage.value) {
      replyLoading.value = true
      try {
        // 调用API发送回复
        const res = await request.post('/api/messages', {
          recipient_id: selectedMessage.value.sender_id,
          title: replyForm.value.title,
          content: replyForm.value.content
        })
        
        if (res.status === 'success') {
          ElMessage.success('回复发送成功')
          hideReplyForm()
          // 重新获取消息列表
          await fetchMessages()
        }
      } catch (error) {
        console.error('发送回复失败:', error)
        ElMessage.error(error.response?.data?.message || '发送回复失败，请稍后重试')
      } finally {
        replyLoading.value = false
      }
    }
  })
}

const markAsRead = async (message) => {
  try {
    // 真实 API 调用
    const res = await request.put(`/api/messages/${message.id}`, {
      is_read: true
    })
    
    if (res.status === 'success') {
      message.is_read = true
      ElMessage.success('已标记为已读')
      // 重新获取消息列表以更新状态
      await fetchMessages()
    }
  } catch (error) {
    console.error('标记已读失败:', error)
    ElMessage.error(error.response?.data?.message || '标记已读失败，请稍后重试')
  }
}

const toggleReadStatus = async (message) => {
  try {
    // 真实 API 调用
    const res = await request.put(`/api/messages/${message.id}`, {
      is_read: !message.is_read
    })
    
    if (res.status === 'success') {
      message.is_read = !message.is_read
      ElMessage.success(message.is_read ? '已标记为已读' : '已标记为未读')
      // 重新获取消息列表以更新状态
      await fetchMessages()
    }
  } catch (error) {
    console.error('更新状态失败:', error)
    ElMessage.error(error.response?.data?.message || '更新状态失败，请稍后重试')
  }
}

const deleteMessage = async (messageId) => {
  try {
    await ElMessageBox.confirm('确定要删除这条消息吗？', '确认删除', { type: 'warning' })
    
    // 真实 API 调用
    const res = await request.delete(`/api/messages/${messageId}`)
    
    if (res.status === 'success') {
      // 重新获取消息列表
      await fetchMessages()
      ElMessage.success('删除成功')
    }
  } catch (error) {
    console.error('删除失败:', error)
    if (error.name !== 'CanceledError') {
      ElMessage.error(error.response?.data?.message || '删除失败，请稍后重试')
    }
  }
}

const deleteSelectedMessages = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedMessages.value.length} 条消息吗？`, '确认批量删除', { type: 'warning' })
    
    // 真实 API 调用
    const res = await request.delete('/api/messages', {
      data: { message_ids: selectedMessages.value }
    })
    
    if (res.status === 'success') {
      // 重新获取消息列表
      await fetchMessages()
      selectedMessages.value = []
      ElMessage.success('批量删除成功')
    }
  } catch (error) {
    console.error('批量删除失败:', error)
    if (error.name !== 'CanceledError') {
      ElMessage.error(error.response?.data?.message || '批量删除失败，请稍后重试')
    }
  }
}

const formatDate = (date, withTime = false) => {
  if (!date) return '-'
  const d = new Date(date)
  if (withTime) {
    return d.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
  }
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

// 生命周期
onMounted(async () => {
  // 记录初始未读数量
  const initialUnreadCount = unreadCount.value
  await fetchMessages()
  
  // 检查是否有新消息
  if (unreadCount.value > initialUnreadCount && unreadCount.value > 0) {
    ElNotification({
      title: '新消息通知',
      message: `您有 ${unreadCount.value} 条未读消息，请及时查看`,
      type: 'info',
      duration: 5000,
      position: 'top-right',
      onClick: () => {
        // 点击通知可以跳转到消息面板
        ElNotification.closeAll()
      }
    })
  }
})
</script>

<style scoped>
.messages-panel {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.messages-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.messages-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.messages-tabs {
  margin-bottom: 20px;
}

.messages-container {
  background: #f9fafb;
  border-radius: 8px;
  padding: 16px;
  min-height: 400px;
}

.empty-messages {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-item {
  display: flex;
  align-items: flex-start;
  background: white;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.message-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.message-item.read {
  opacity: 0.8;
}

.message-item.unread {
  font-weight: 500;
  border-left: 3px solid #3b82f6;
}

.message-checkbox {
  margin-right: 12px;
}

.message-indicator {
  margin-right: 8px;
  padding-top: 6px;
}

.unread-dot {
  width: 8px;
  height: 8px;
  background: #ef4444;
  border-radius: 50%;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.message-sender {
  font-weight: 600;
  color: #374151;
}

.message-time {
  font-size: 12px;
  color: #9ca3af;
}

.message-title {
  margin-bottom: 4px;
  color: #1f2937;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.message-preview {
  font-size: 13px;
  color: #6b7280;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.message-actions {
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.message-item:hover .message-actions {
  opacity: 1;
}

.messages-pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.empty-messages {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.message-detail-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.detail-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-sender {
  font-weight: 600;
  color: #374151;
}

.detail-time {
  font-size: 12px;
  color: #9ca3af;
}

.detail-content {
  line-height: 1.6;
  color: #4b5563;
  white-space: pre-wrap;
}
</style>
