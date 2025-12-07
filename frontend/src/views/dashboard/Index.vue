<template>
  <div class="dashboard-container">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ 'mobile-open': mobileMenuOpen }">
      <div class="logo-area">
        <div class="logo-icon">
          <el-icon :size="24" color="white"><Monitor /></el-icon>
        </div>
        <div class="logo-text">
          <h1>GMTools</h1>
          <p>功能管理系统</p>
        </div>
        <el-button class="close-menu-btn" link @click="mobileMenuOpen = false">
          <el-icon :size="24"><Close /></el-icon>
        </el-button>
      </div>
      
      <nav class="nav-menu">
        <div 
          v-for="(module, key) in modules" 
          :key="key"
          class="nav-item"
          :class="{ active: currentModule === key }"
          @click="switchModule(key)"
        >
          <el-icon :size="20"><component :is="module.icon" /></el-icon>
          <span>{{ module.name }}</span>
          <el-icon v-if="currentModule === key" class="arrow-icon"><ArrowRight /></el-icon>
        </div>
      </nav>
      
      <!-- Footer -->
      <div class="sidebar-footer">
        <p>© 2024 GMTools</p>
        <p class="version">v1.0.0 梦江南超级GM工具</p>
      </div>
    </aside>

    <!-- Mobile Overlay -->
    <div v-if="mobileMenuOpen" class="mobile-overlay" @click="mobileMenuOpen = false"></div>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Header -->
      <header class="header">
        <div class="header-left">
          <el-button class="menu-btn" link @click="mobileMenuOpen = true">
            <el-icon :size="24"><Menu /></el-icon>
          </el-button>
          <h2>{{ modules[currentModule]?.name }}</h2>
        </div>
        <div class="header-right">
          <!-- User Dropdown -->
          <el-dropdown trigger="click" @command="handleUserCommand">
            <div class="user-dropdown-trigger">
              <span class="user-name">{{ authStore.user?.username }}</span>
              <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>
                  <el-icon><User /></el-icon>{{ userRoleLabel }}
                </el-dropdown-item>
                <el-dropdown-item v-if="isAdmin" command="admin">
                  <el-icon><Setting /></el-icon>超管后台
                </el-dropdown-item>
                <el-dropdown-item command="activation">
                  <el-icon><Ticket /></el-icon>激活特权
                </el-dropdown-item>
                <el-dropdown-item command="change-password">
                  <el-icon><Lock /></el-icon>修改密码
                </el-dropdown-item>
                <el-dropdown-item command="user-messages" disabled>
                  <el-icon><ChatDotRound /></el-icon>用户消息
                </el-dropdown-item>
                <el-dropdown-item command="announcements" disabled>
                  <el-icon><Bell /></el-icon>站内公告
                </el-dropdown-item>
                <el-dropdown-item command="work-order" disabled>
                  <el-icon><Document /></el-icon>提交工单
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          
          <el-button :type="showConsole ? 'primary' : 'default'" @click="showConsole = !showConsole">
            <el-icon><Monitor /></el-icon>
            <span class="hidden-xs">控制台</span>
          </el-button>
        </div>
      </header>

      <!-- Content Area -->
      <div class="content-wrapper">
        <div class="content-scroll">
          <!-- Global Player ID Input -->
          <el-card class="player-id-card" shadow="hover">
            <div class="player-id-row">
              <div class="input-group">
                <label>当前操作角色</label>
                <el-input 
                  v-model="playerId" 
                  placeholder="请输入角色ID" 
                  prefix-icon="User"
                  size="large"
                  @blur="addPlayerIdToHistory"
                />
              </div>
              <div class="history-group" v-if="playerIdHistory.length > 0">
                <label>历史记录</label>
                <el-select v-model="playerId" placeholder="选择历史ID" size="large" style="width: 100%">
                  <el-option v-for="id in playerIdHistory" :key="id" :label="id" :value="id" />
                </el-select>
              </div>
            </div>
          </el-card>

          <!-- Dynamic Component for Modules -->
          <div class="module-content fade-in">
             <component :is="modules[currentModule]?.component" v-if="modules[currentModule]?.component" />
             <el-empty v-else description="Module Not Found" />
          </div>
        </div>

        <!-- Console Sidebar -->
        <transition name="slide-right">
          <div v-if="showConsole" class="console-sidebar">
            <div class="console-header">
              <div class="flex-center">
                <el-icon><Monitor /></el-icon>
                <span>控制台</span>
              </div>
              <div class="flex-center">
                <el-button link @click="clearLogs"><el-icon><Delete /></el-icon></el-button>
                <el-button link @click="showConsole = false"><el-icon><Close /></el-icon></el-button>
              </div>
            </div>
            <div class="console-body" ref="consoleRef">
              <div v-if="consoleLogs.length === 0" class="empty-logs">等待请求...</div>
              <div v-for="(log, idx) in consoleLogs" :key="idx" class="log-item" :class="log.type">
                <div class="log-meta">
                  <span class="time">{{ log.time }}</span>
                  <span class="status">{{ log.status }}</span>
                </div>
                <div class="log-title">{{ log.title }}</div>
                <pre class="log-data">{{ log.data }}</pre>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </main>

    <!-- 激活特权模态框 -->
    <el-dialog v-model="showActivationDialog" title="激活特权" width="500px" center>
      <div class="activation-dialog">
        <el-form :model="activationForm" label-width="100px">
          <el-form-item label="激活码">
            <el-input 
              v-model="activationForm.code" 
              placeholder="请输入激活码"
              @keyup.enter="useActivationCode"
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showActivationDialog = false">取消</el-button>
          <el-button type="primary" @click="useActivationCode" :loading="activationLoading">
            使用激活码
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="showChangePasswordDialog" title="修改密码" width="500px" center>
      <el-form :model="changePasswordForm" label-width="120px">
        <el-form-item label="原密码">
          <el-input v-model="changePasswordForm.currentPassword" type="password" placeholder="请输入原密码" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="changePasswordForm.newPassword" type="password" placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="changePasswordForm.confirmPassword" type="password" placeholder="请再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showChangePasswordDialog = false">取消</el-button>
          <el-button type="primary" :loading="changePasswordLoading" @click="changeUserPassword">
            修改
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, provide, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { 
  Monitor, User, Setting, Wallet, Goods, Present, 
  Ticket, Document, Menu, Close, ArrowRight, SwitchButton,
  Delete, UserFilled, ArrowDown, Lock, ChatDotRound, Bell
} from '@element-plus/icons-vue'

// Import Modules
import AccountPanel from './modules/AccountPanel.vue'
import RechargePanel from './modules/RechargePanel.vue'
import CharacterPanel from './modules/CharacterPanel.vue'
import PetPanel from './modules/PetPanel.vue'
import EquipmentPanel from './modules/EquipmentPanel.vue'
import GiftPanel from './modules/GiftPanel.vue'
import GamePanel from './modules/GamePanel.vue'
import ActivationPanel from './modules/ActivationPanel.vue'
import LogsPanel from './modules/LogsPanel.vue'

const authStore = useAuthStore()
const router = useRouter()

const mobileMenuOpen = ref(false)
const showConsole = ref(false)
const currentModule = ref('account')
const playerId = ref('')
const playerIdHistory = ref([])
const consoleLogs = ref([])
const consoleRef = ref(null)

// Dialog visibility states
const showActivationDialog = ref(false)
const showChangePasswordDialog = ref(false)

// Form data
const activationForm = ref({
  code: ''
})

const changePasswordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// Loading states
const activationLoading = ref(false)
const changePasswordLoading = ref(false)

const modules = {
  account: { name: '账号管理', icon: 'User', component: AccountPanel },
  recharge: { name: '充值组合', icon: 'Wallet', component: RechargePanel },
  character: { name: '角色管理', icon: 'User', component: CharacterPanel }, 
  pet: { name: '宝宝管理', icon: 'Goods', component: PetPanel },
  equipment: { name: '装备管理', icon: 'Setting', component: EquipmentPanel },
  gift: { name: '物品赠送', icon: 'Present', component: GiftPanel },
  game: { name: '游戏管理', icon: 'Setting', component: GamePanel },
  activation: { name: '激活码', icon: 'Ticket', component: ActivationPanel },
  logs: { name: '日志管理', icon: 'Document', component: LogsPanel }
}

// Provide playerId to child components
provide('playerId', playerId)
provide('logToConsole', logToConsole)

// Admin check
const isAdmin = computed(() => {
  const role = authStore.user?.role
  return role === 'admin' || role === 'super_admin'
})

// User role label for display
const userRoleLabel = computed(() => {
  const role = authStore.user?.role
  const level = authStore.user?.level
  if (role === 'super_admin') return '超级管理员'
  if (role === 'admin') return '管理员'
  return `Level.${level || 1}`
})

function goToUserManagement() {
  router.push('/admin')
}

function handleUserCommand(command) {
  if (command === 'admin') {
    router.push('/admin')
  } else if (command === 'activation') {
    showActivationDialog.value = true
  } else if (command === 'change-password') {
    showChangePasswordDialog.value = true
  } else if (command === 'user-messages' || command === 'announcements' || command === 'work-order') {
    ElMessage.info('功能即将上线，敬请期待')
  } else if (command === 'logout') {
    handleLogout()
  }
}

function switchModule(key) {
  currentModule.value = key
  mobileMenuOpen.value = false
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

function addPlayerIdToHistory() {
  const id = playerId.value.trim()
  if (id && !playerIdHistory.value.includes(id)) {
    playerIdHistory.value.unshift(id)
    if (playerIdHistory.value.length > 10) playerIdHistory.value.pop()
  }
}

function logToConsole(method, url, status, data) {
  consoleLogs.value.push({
    time: new Date().toLocaleTimeString(),
    title: `${method} ${url}`,
    status: status || 'ERR',
    type: status >= 400 || status === 0 ? 'error' : 'success',
    data: JSON.stringify(data, null, 2)
  })
  // Scroll to bottom
  setTimeout(() => {
    if (consoleRef.value) consoleRef.value.scrollTop = consoleRef.value.scrollHeight
  }, 100)
}

function clearLogs() {
  consoleLogs.value = []
}

// 激活特权功能
async function useActivationCode() {
  if (!activationForm.code) {
    ElMessage.warning('请填写激活码')
    return
  }
  
  activationLoading.value = true
  try {
    const response = await fetch('/api/activation/use', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        code: activationForm.code
      })
    })
    
    const data = await response.json()
    
    if (response.ok) {
      ElMessage.success(`激活成功：${data.message}`)
      showActivationDialog.value = false
      activationForm.code = ''
    } else {
      ElMessage.error(`激活失败：${data.message || '未知错误'}`)
    }
  } catch (error) {
    console.error('激活码使用失败:', error)
    ElMessage.error('激活码使用失败，请稍后重试')
  } finally {
    activationLoading.value = false
  }
}

// 修改密码功能
const changeUserPassword = async () => {
  if (!changePasswordForm.value.currentPassword || !changePasswordForm.value.newPassword || !changePasswordForm.value.confirmPassword) {
    ElMessage.warning('请填写原密码、新密码和确认新密码')
    return
  }
  
  if (changePasswordForm.value.newPassword !== changePasswordForm.value.confirmPassword) {
    ElMessage.warning('新密码和确认新密码不一致')
    return
  }
  
  if (changePasswordForm.value.newPassword.length < 6) {
    ElMessage.warning('新密码长度不能少于6位')
    return
  }
  
  changePasswordLoading.value = true
  
  try {
    const response = await fetch('/api/users/me/change-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        old_password: changePasswordForm.value.currentPassword,
        new_password: changePasswordForm.value.newPassword
      })
    })
    
    const data = await response.json()
    
    if (response.ok) {
      ElMessage.success(`密码修改成功：${data.message}`)
      showChangePasswordDialog.value = false
      // 重置表单
      changePasswordForm.value.currentPassword = ''
      changePasswordForm.value.newPassword = ''
      changePasswordForm.value.confirmPassword = ''
    } else {
      ElMessage.error(`密码修改失败：${data.message || '未知错误'}`)
    }
  } catch (error) {
    console.error('密码修改失败:', error)
    ElMessage.error('密码修改失败，请稍后重试')
  } finally {
    changePasswordLoading.value = false
  }
}
</script>

<style scoped>
.dashboard-container {
  display: flex;
  height: 100vh;
  background-color: #f9fafb;
}

/* Sidebar */
.sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid #f3f4f6;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease;
  z-index: 50;
}

.logo-area {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: rgba(255,255,255,0.2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.logo-text h1 {
  font-size: 18px;
  font-weight: bold;
  line-height: 1.2;
}

.logo-text p {
  font-size: 12px;
  opacity: 0.8;
}

.nav-menu {
  flex: 1;
  overflow-y: auto;
  padding: 16px 12px;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 12px;
  cursor: pointer;
  color: #4b5563;
  transition: all 0.2s;
  margin-bottom: 4px;
  border: 2px solid transparent;
}

.nav-item:hover {
  background-color: #f9fafb;
}

.nav-item.active {
  background-color: #eef2ff;
  color: #4f46e5;
  border-color: #e0e7ff;
}

.nav-item .el-icon {
  margin-right: 12px;
}

.arrow-icon {
  margin-left: auto;
  opacity: 0.5;
}

/* Admin Link */
.admin-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  margin: 8px 12px;
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  border: 1px solid #fcd34d;
  border-radius: 12px;
  cursor: pointer;
  color: #92400e;
  font-weight: 500;
  transition: all 0.2s;
}

.admin-link:hover {
  background: linear-gradient(135deg, #fde68a, #fcd34d);
  transform: translateX(4px);
}

/* Sidebar Footer */
.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid #f3f4f6;
  text-align: center;
  font-size: 11px;
  color: #9ca3af;
}

.sidebar-footer .version {
  color: #d1d5db;
  margin-top: 2px;
}

.user-info {
  padding: 16px;
  border-top: 1px solid #f3f4f6;
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #818cf8, #a855f7);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.username {
  font-weight: 500;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status {
  font-size: 12px;
  color: #6b7280;
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.header {
  height: 64px;
  background: white;
  border-bottom: 1px solid #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

/* User Dropdown in Header */
.user-dropdown-trigger {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #f3f4f6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  margin-right: 12px;
}

.user-dropdown-trigger:hover {
  background: #e5e7eb;
}

.user-name {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.dropdown-arrow {
  font-size: 12px;
  color: #6b7280;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h2 {
  font-size: 20px;
  font-weight: bold;
  color: #111827;
}

.menu-btn {
  display: none;
}

.content-wrapper {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
}

.content-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.player-id-card {
  margin-bottom: 24px;
  border-radius: 16px;
}

.player-id-row {
  display: flex;
  gap: 16px;
}

.input-group, .history-group {
  flex: 1;
}

.input-group label, .history-group label {
  display: block;
  font-size: 12px;
  font-weight: bold;
  color: #6b7280;
  text-transform: uppercase;
  margin-bottom: 8px;
}

/* Console Sidebar */
.console-sidebar {
  width: 400px;
  background: white;
  border-left: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  box-shadow: -4px 0 15px rgba(0,0,0,0.05);
  z-index: 40;
}

.console-header {
  height: 50px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  font-weight: bold;
  color: #374151;
}

.console-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #0f172a;
  color: #e2e8f0;
  font-family: monospace;
  font-size: 12px;
}

.log-item {
  margin-bottom: 12px;
  padding-left: 12px;
  border-left: 2px solid #3b82f6;
}

.log-item.error {
  border-left-color: #ef4444;
}

.log-item.success {
  border-left-color: #10b981;
}

.log-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
  color: #94a3b8;
}

.log-title {
  color: #60a5fa;
  margin-bottom: 4px;
  word-break: break-all;
}

.log-data {
  white-space: pre-wrap;
  word-break: break-all;
  color: #cbd5e1;
}

/* Mobile Responsive */
.mobile-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  z-index: 40;
  backdrop-filter: blur(4px);
}

.close-menu-btn {
  display: none;
  margin-left: auto;
  color: white;
}

@media (max-width: 1024px) {
  .sidebar {
    position: fixed;
    height: 100vh;
    transform: translateX(-100%);
  }
  
  .sidebar.mobile-open {
    transform: translateX(0);
  }
  
  .menu-btn {
    display: block;
  }
  
  .close-menu-btn {
    display: block;
  }
  
  .console-sidebar {
    width: 100%;
  }
  
  .player-id-row {
    flex-direction: column;
  }
  
  .hidden-xs {
    display: none !important;
  }
}

.fade-in {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform 0.3s ease;
}

.slide-right-enter-from,
.slide-right-leave-to {
  transform: translateX(100%);
}

.flex-center {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
