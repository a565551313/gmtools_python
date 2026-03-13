<template>
  <div class="bind-id-panel">
    <div class="panel-header">
      <div class="header-info">
        <h3>角色 ID 绑定</h3>
        <p>绑定您的游戏角色 ID，以便进行后续操作</p>
      </div>
      <div class="header-stats" v-if="!isUnrestricted">
        <div class="stat-item">
          <span class="label">已绑定</span>
          <span class="value">{{ boundIds.length }}</span>
        </div>
        <div class="stat-item">
          <span class="label">最大限制</span>
          <span class="value">{{ maxBindCount === -2 ? '无限' : maxBindCount }}</span>
        </div>
      </div>
    </div>

    <el-row :gutter="20">
      <!-- 绑定操作卡片 -->
      <el-col :xs="24" :md="10">
        <el-card class="action-card glass-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Link /></el-icon> 新增绑定</span>
            </div>
          </template>
          
          <div class="bind-form">
            <div class="info-alert" v-if="isUnrestricted">
              <el-icon><InfoFilled /></el-icon>
              <span>您当前的权限等级无需绑定 ID，可直接操作任何角色。</span>
            </div>
            
            <template v-else>
              <div class="bind-input-group">
                <label>角色 ID</label>
                <el-input 
                  v-model="newId" 
                  placeholder="请输入要绑定的角色 ID" 
                  :disabled="isMaxed"
                  @keyup.enter="handleBind"
                >
                  <template #prefix>
                    <el-icon><User /></el-icon>
                  </template>
                </el-input>
              </div>
              
              <div class="bind-tips">
                <p><el-icon><Warning /></el-icon> 注意事项：</p>
                <ul>
                  <li>绑定后<strong>无法自行修改或删除</strong>。</li>
                  <li>如果填错或需要更换，请联系管理员处理。</li>
                  <li>请确保 ID 输入正确，否则将无法进行操作。</li>
                </ul>
              </div>

              <el-button 
                type="primary" 
                class="bind-btn" 
                :loading="loading" 
                :disabled="isMaxed || !newId"
                @click="handleBind"
              >
                立即绑定
              </el-button>
              
              <p v-if="isMaxed" class="maxed-hint">已达到最大绑定数量限制</p>
            </template>
          </div>
        </el-card>
      </el-col>

      <!-- 已绑定列表卡片 -->
      <el-col :xs="24" :md="14">
        <el-card class="list-card glass-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><List /></el-icon> 已绑定 ID 列表</span>
              <el-tag size="small" type="info" v-if="boundIds.length > 0">共 {{ boundIds.length }} 个</el-tag>
            </div>
          </template>

          <div class="id-list" v-if="boundIds.length > 0">
            <div v-for="id in boundIds" :key="id" class="id-item">
              <div class="id-info">
                <el-icon class="id-icon"><UserFilled /></el-icon>
                <span class="id-value">{{ id }}</span>
              </div>
              <el-tag size="small" type="success" effect="plain">已绑定</el-tag>
            </div>
          </div>
          
          <el-empty v-else description="暂无绑定的角色 ID" :image-size="100">
            <template #extra>
              <p class="empty-hint">请在左侧输入 ID 进行绑定</p>
            </template>
          </el-empty>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { 
  Link, User, InfoFilled, Warning, List, UserFilled 
} from '@element-plus/icons-vue'
import request from '@/api/request'

const authStore = useAuthStore()
const loading = ref(false)
const newId = ref('')
const boundIds = ref([])
const maxBindCount = ref(1)

const isUnrestricted = computed(() => maxBindCount.value === -1 || authStore.user?.role === 'super_admin')
const isMaxed = computed(() => {
  if (maxBindCount.value === -2) return false
  return boundIds.value.length >= maxBindCount.value
})

async function fetchUserInfo() {
  try {
    const res = await request.get('/api/users/me')
    if (res.status === 'success') {
      boundIds.value = res.user.bound_ids || []
      maxBindCount.value = res.user.max_bind_ids || 1
      // Update store user info as well
      authStore.user = { ...authStore.user, ...res.user }
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

async function fetchLevelConfig() {
  // Now handled by fetchUserInfo to avoid 403 on admin-only endpoint
  if (authStore.user?.max_bind_ids !== undefined) {
    maxBindCount.value = authStore.user.max_bind_ids
  }
}

async function handleBind() {
  if (!newId.value.trim()) return
  
  try {
    await ElMessageBox.confirm(
      `确定要绑定角色 ID: ${newId.value} 吗？绑定后无法自行修改。`,
      '确认绑定',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    loading.value = true
    const res = await request.post('/api/users/me/bind-id', {
      character_id: newId.value.trim()
    })
    
    if (res.status === 'success') {
      ElMessage.success('绑定成功')
      newId.value = ''
      await fetchUserInfo()
    } else {
      ElMessage.error(res.detail || '绑定失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('绑定失败:', error)
      ElMessage.error('绑定过程中发生错误')
    }
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchUserInfo()
  await fetchLevelConfig()
})
</script>

<style scoped>
.bind-id-panel {
  padding: 10px;
}

.panel-header {
  margin-bottom: 25px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.header-info h3 {
  font-size: 24px;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #1f2937 0%, #4f46e5 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-info p {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.header-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  text-align: right;
}

.stat-item .label {
  display: block;
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 4px;
}

.stat-item .value {
  font-size: 20px;
  font-weight: bold;
  color: #4f46e5;
}

.glass-card {
  background: white !important;
  border: 1px solid #f3f4f6 !important;
  border-radius: 16px;
  color: #1f2937 !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05) !important;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.card-header .el-icon {
  margin-right: 8px;
  vertical-align: middle;
}

.bind-form {
  padding: 10px 0;
}

.info-alert {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f5f3ff;
  border-radius: 12px;
  color: #5b21b6;
  font-size: 14px;
  line-height: 1.5;
  border: 1px solid #ddd6fe;
}

.bind-input-group {
  margin-bottom: 20px;
}

.bind-input-group label {
  display: block;
  margin-bottom: 10px;
  font-size: 14px;
  color: #4b5563;
  font-weight: 500;
}

.bind-tips {
  background: rgba(255, 153, 0, 0.05);
  border: 1px solid rgba(255, 153, 0, 0.2);
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 25px;
}

.bind-tips p {
  margin: 0 0 10px 0;
  color: #ff9900;
  font-weight: bold;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.bind-tips ul {
  margin: 0;
  padding-left: 20px;
  color: #6b7280;
  font-size: 13px;
}

.bind-tips li {
  margin-bottom: 6px;
}

.bind-btn {
  width: 100%;
  height: 45px;
  font-size: 16px;
  border-radius: 12px;
}

.maxed-hint {
  text-align: center;
  color: #f56c6c;
  font-size: 13px;
  margin-top: 12px;
}

.id-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.id-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: #f9fafb;
  border: 1px solid #f3f4f6;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.id-item:hover {
  background: #f3f4f6;
  border-color: #e5e7eb;
  transform: translateX(5px);
}

.id-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.id-icon {
  font-size: 18px;
  color: #4f46e5;
}

.id-value {
  font-size: 16px;
  font-family: 'Courier New', Courier, monospace;
  letter-spacing: 1px;
}

.empty-hint {
  color: #9ca3af;
  font-size: 14px;
}

@media (max-width: 768px) {
  .panel-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .header-stats {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
