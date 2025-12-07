<template>
  <div class="account-panel">
    <!-- Basic Info -->
    <div class="panel-card">
      <div class="card-header">
        <div class="header-icon-wrapper blue">
          <el-icon :size="20"><User /></el-icon>
        </div>
        <h3 class="header-title">基础信息</h3>
      </div>
      
      <div class="form-grid">
        <div class="form-field">
          <label class="field-label">账号</label>
          <el-input 
            v-model="form.account" 
            placeholder="输入账号"
            clearable
            :prefix-icon="User"
          />
        </div>
        <div class="form-field">
          <label class="field-label">新密码</label>
          <el-input 
            v-model="form.password" 
            placeholder="输入新密码"
            type="password"
            show-password
            clearable
            :prefix-icon="Lock"
          />
        </div>
        <div class="form-field">
          <label class="field-label">称谓</label>
          <el-input 
            v-model="form.title" 
            placeholder="输入称谓"
            clearable
            :prefix-icon="Medal"
          />
        </div>
      </div>
    </div>

    <!-- Account Operations -->
    <div class="panel-card">
      <div class="card-header">
        <div class="header-icon-wrapper amber">
          <el-icon :size="20"><Setting /></el-icon>
        </div>
        <h3 class="header-title">账号操作</h3>
      </div>
      
      <div class="operations-grid">
        <button 
          v-for="op in operations" 
          :key="op.cmd"
          class="operation-btn"
          :class="[op.type, { 'is-danger': op.danger }]"
          @click="handleOperation(op)"
        >
          <div class="btn-icon-wrapper" :class="op.iconClass">
            <component :is="op.icon" class="btn-icon" />
          </div>
          <span class="btn-label">{{ op.label }}</span>
          <span v-if="op.desc" class="btn-desc">{{ op.desc }}</span>
        </button>
      </div>
    </div>

    <!-- Player Info Display -->
    <transition name="slide-fade">
      <div v-if="playerInfo" class="panel-card info-card">
        <div class="card-header">
          <div class="header-icon-wrapper green">
            <el-icon :size="20"><UserFilled /></el-icon>
          </div>
          <h3 class="header-title">玩家详细信息</h3>
          <el-button 
            text 
            circle 
            class="close-btn"
            @click="playerInfo = null"
          >
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
        
        <div class="info-grid">
          <div 
            v-for="(value, key) in playerInfo" 
            :key="key"
            class="info-item"
            :class="{ 'col-span-2': typeof value === 'object' }"
          >
            <div class="info-label">{{ formatLabel(key) }}</div>
            <div class="info-value">
              <pre v-if="typeof value === 'object'" class="json-display">{{ JSON.stringify(value, null, 2) }}</pre>
              <span v-else>{{ formatValue(value) || '-' }}</span>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { reactive, ref, inject, computed } from 'vue'
import request from '@/api/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, Setting, InfoFilled, CircleClose, SwitchButton, 
  Lock, Unlock, Key, Medal, Money, Check, Close, UserFilled 
} from '@element-plus/icons-vue'

const playerId = inject('playerId')
const logToConsole = inject('logToConsole')

const form = reactive({
  account: '',
  password: '',
  title: ''
})

const playerInfo = ref(null)

const operations = computed(() => [
  { 
    cmd: '玩家信息', 
    label: '玩家信息', 
    desc: '查看详细',
    icon: InfoFilled, 
    idType: 'player_id',
    type: 'info',
    iconClass: 'blue'
  },
  { 
    cmd: '踢出战斗', 
    label: '踢出战斗', 
    desc: '强制退出',
    icon: CircleClose, 
    idType: 'player_id',
    type: 'warning',
    iconClass: 'orange'
  },
  { 
    cmd: '强制下线', 
    label: '强制下线', 
    desc: '断开连接',
    icon: SwitchButton, 
    idType: 'player_id',
    type: 'warning',
    iconClass: 'orange'
  },
  { 
    cmd: '封禁账号', 
    label: '封禁账号', 
    desc: '禁止登录',
    icon: Lock, 
    idType: 'account',
    type: 'danger',
    iconClass: 'red',
    danger: true
  },
  { 
    cmd: '解封账号', 
    label: '解封账号', 
    desc: '恢复访问',
    icon: Unlock, 
    idType: 'account',
    type: 'success',
    iconClass: 'green'
  },
  { 
    cmd: '修改密码', 
    label: '修改密码', 
    desc: '重置密码',
    icon: Key, 
    idType: 'account',
    useExtra: true,
    type: 'primary',
    iconClass: 'blue'
  },
  { 
    cmd: '给予称谓', 
    label: '给予称谓', 
    desc: '授予荣誉',
    icon: Medal, 
    idType: 'player_id',
    useExtra: true,
    type: 'primary',
    iconClass: 'purple'
  },
  { 
    cmd: '发送路费', 
    label: '发送路费', 
    desc: '赠送金币',
    icon: Money, 
    idType: 'special',
    type: 'success',
    iconClass: 'yellow'
  },
  { 
    cmd: '开通管理', 
    label: '开通管理', 
    desc: '授予权限',
    icon: Check, 
    idType: 'account',
    type: 'success',
    iconClass: 'green'
  },
  { 
    cmd: '关闭管理', 
    label: '关闭管理', 
    desc: '撤销权限',
    icon: Close, 
    idType: 'account',
    type: 'warning',
    iconClass: 'gray'
  }
])

async function handleOperation(op) {
  if (op.danger) {
    try {
      await ElMessageBox.confirm(
        `确定要${op.label}吗？此操作不可撤销。`,
        '危险操作',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      )
    } catch {
      return
    }
  }

  if (op.cmd === '发送路费') {
    sendTravelFee()
  } else {
    runCmd(op.cmd, op.idType, op.useExtra)
  }
}

async function runCmd(cmd, idType, useExtra = false) {
  const id = idType === 'player_id' ? playerId.value : form.account
  if (!id) {
    ElMessage.error(`请输入${idType === 'player_id' ? '角色ID' : '账号'}`)
    return
  }
  
  const payload = { 
    function: 'manage_account', 
    args: { 
      command: cmd, 
      target_id: id, 
      id_type: idType === 'player_id' ? '角色ID' : '账号' 
    } 
  }
  
  if (useExtra) {
    if (cmd === '修改密码') {
      if (!form.password) {
        ElMessage.error('请输入新密码')
        return
      }
      payload.args.extra = form.password
    }
    if (cmd === '给予称谓') {
      if (!form.title) {
        ElMessage.error('请输入称谓')
        return
      }
      payload.args.extra = form.title
    }
  }
  
  try {
    const res = await request.post('/api/account', payload)
    logToConsole('POST', '/api/account', 200, res)
    ElMessage.success(`${cmd}执行成功`)
    
    if (cmd === '玩家信息' && res.data) {
      playerInfo.value = res.data
    }
  } catch (e) {
    logToConsole('POST', '/api/account', 0, { error: e.message })
    ElMessage.error(`操作失败: ${e.message}`)
  }
}

async function sendTravelFee() {
  if (!form.account || !playerId.value) {
    ElMessage.error('请输入账号和角色ID')
    return
  }
  try {
    const res = await request.post('/api/account', { 
      function: 'send_travel_fee', 
      args: { account: form.account, player_id: playerId.value } 
    })
    logToConsole('POST', '/api/account', 200, res)
    ElMessage.success('路费发送成功')
  } catch (e) {
    logToConsole('POST', '/api/account', 0, { error: e.message })
    ElMessage.error(`发送失败: ${e.message}`)
  }
}

function formatLabel(key) {
  // Handle numeric keys (array indices) or non-string keys
  if (typeof key !== 'string') {
    return `#${key}`
  }
  // Convert snake_case to readable format
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

function formatValue(value) {
  if (typeof value === 'boolean') return value ? '是' : '否'
  if (value === null || value === undefined) return '-'
  return value
}
</script>

<style scoped>
.account-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 4px;
}

.panel-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.panel-card:hover {
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
  position: relative;
}

.header-icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.header-icon-wrapper.blue { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.header-icon-wrapper.amber { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.header-icon-wrapper.green { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }

.header-icon-wrapper :deep(.el-icon) {
  color: white;
}

.header-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a202c;
}

.close-btn {
  margin-left: auto;
}

/* Form Grid */
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  padding: 24px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-label {
  font-size: 13px;
  font-weight: 500;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Operations Grid */
.operations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
  padding: 24px;
}

@media (max-width: 640px) {
  .operations-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .operations-grid {
    grid-template-columns: repeat(5, 1fr);
  }
}

.operation-btn {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 12px;
  background: #f8fafc;
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  outline: none;
}

.operation-btn:hover {
  transform: translateY(-2px);
  background: white;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.operation-btn.is-danger:hover {
  border-color: #ef4444;
  background: #fef2f2;
}

.btn-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.btn-icon-wrapper.blue { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.btn-icon-wrapper.orange { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
.btn-icon-wrapper.red { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.btn-icon-wrapper.green { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
.btn-icon-wrapper.purple { background: linear-gradient(135deg, #9D50BB 0%, #6E48AA 100%); }
.btn-icon-wrapper.yellow { background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); }
.btn-icon-wrapper.gray { background: linear-gradient(135deg, #667eea 0%, #64748b 100%); }

.btn-icon {
  font-size: 24px;
  color: white;
}

.btn-label {
  font-size: 14px;
  font-weight: 600;
  color: #2d3748;
}

.btn-desc {
  font-size: 11px;
  color: #94a3b8;
}

/* Info Grid */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 0;
  padding: 24px;
}

.info-item {
  display: flex;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  border-right: 1px solid #f0f0f0;
}

.info-item.col-span-2 {
  grid-column: 1 / -1;
}

.info-label {
  flex: 0 0 120px;
  font-size: 13px;
  font-weight: 500;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  flex: 1;
  font-size: 14px;
  color: #1a202c;
  word-break: break-word;
}

.json-display {
  background: #f8fafc;
  padding: 12px;
  border-radius: 8px;
  font-size: 12px;
  line-height: 1.6;
  overflow-x: auto;
  margin: 0;
}

/* Transitions */
.slide-fade-enter-active {
  transition: all 0.3s ease;
}

.slide-fade-leave-active {
  transition: all 0.2s ease;
}

.slide-fade-enter-from {
  transform: translateY(20px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .panel-card {
    background: #1e293b;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  }
  
  .card-header {
    border-bottom-color: #334155;
  }
  
  .header-title {
    color: #f1f5f9;
  }
  
  .field-label,
  .info-label {
    color: #94a3b8;
  }
  
  .operation-btn {
    background: #334155;
  }
  
  .operation-btn:hover {
    background: #475569;
  }
  
  .btn-label {
    color: #e2e8f0;
  }
  
  .info-value {
    color: #cbd5e1;
  }
  
  .json-display {
    background: #334155;
    color: #cbd5e1;
  }
  
  .info-item {
    border-color: #334155;
  }
}
</style>