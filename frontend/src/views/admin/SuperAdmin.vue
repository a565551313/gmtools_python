<template>
  <div class="admin-container" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <!-- 左侧菜单 -->
    <aside class="sidebar" :class="{ 'mobile-open': mobileMenuOpen }">
      <!-- Logo区域 -->
      <div class="logo-area">
        <div class="logo-icon">
          <el-icon :size="sidebarCollapsed ? 20 : 24" color="white"><Setting /></el-icon>
        </div>
        <Transition name="fade">
          <div v-if="!sidebarCollapsed" class="logo-text">
            <h1>超级后台</h1>
            <p>System Admin</p>
          </div>
        </Transition>
        <el-button class="close-menu-btn" link @click="mobileMenuOpen = false">
          <el-icon :size="20"><Close /></el-icon>
        </el-button>
      </div>

      <!-- 导航菜单 -->
      <nav class="nav-menu">
        <div class="nav-section">
          <span v-if="!sidebarCollapsed" class="nav-section-title">核心功能</span>
        </div>
        
        <el-tooltip 
          v-for="(module, key) in coreModules" 
          :key="key"
          :content="module.name"
          placement="right"
          :disabled="!sidebarCollapsed"
        >
          <div 
            class="nav-item"
            :class="{ active: currentModule === key }"
            @click="switchModule(key)"
          >
            <div class="nav-item-icon">
              <el-icon :size="20"><component :is="module.icon" /></el-icon>
            </div>
            <Transition name="fade">
              <span v-if="!sidebarCollapsed" class="nav-item-text">{{ module.name }}</span>
            </Transition>
            <div v-if="!sidebarCollapsed && module.badge" class="nav-badge">{{ module.badge }}</div>
            <div v-if="currentModule === key" class="nav-indicator"></div>
          </div>
        </el-tooltip>

        <div class="nav-section">
          <span v-if="!sidebarCollapsed" class="nav-section-title">扩展功能</span>
        </div>

        <el-tooltip 
          v-for="(module, key) in extendModules" 
          :key="key"
          :content="module.name + (module.coming ? ' (即将上线)' : '')"
          placement="right"
          :disabled="!sidebarCollapsed"
        >
          <div 
            class="nav-item"
            :class="{ active: currentModule === key, disabled: module.coming }"
            @click="!module.coming && switchModule(key)"
          >
            <div class="nav-item-icon">
              <el-icon :size="20"><component :is="module.icon" /></el-icon>
            </div>
            <Transition name="fade">
              <span v-if="!sidebarCollapsed" class="nav-item-text">{{ module.name }}</span>
            </Transition>
            <el-tag v-if="!sidebarCollapsed && module.coming" size="small" type="info" effect="plain" round>
              开发中
            </el-tag>
            <div v-if="currentModule === key && !module.coming" class="nav-indicator"></div>
          </div>
        </el-tooltip>
      </nav>

      <!-- 折叠按钮 -->
      <div class="collapse-btn-wrapper">
        <el-button class="collapse-btn" @click="toggleSidebar">
          <el-icon :size="18">
            <component :is="sidebarCollapsed ? 'DArrowRight' : 'DArrowLeft'" />
          </el-icon>
        </el-button>
      </div>

      <!-- 底部区域 -->
      <div class="sidebar-footer">
        <el-tooltip content="返回功能后台" placement="right" :disabled="!sidebarCollapsed">
          <el-button class="back-btn" @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            <span v-if="!sidebarCollapsed">返回功能后台</span>
          </el-button>
        </el-tooltip>
        <p v-if="!sidebarCollapsed" class="copyright">© 2024 GMTools</p>
      </div>
    </aside>

    <!-- 移动端遮罩 -->
    <Transition name="fade">
      <div v-if="mobileMenuOpen" class="mobile-overlay" @click="mobileMenuOpen = false"></div>
    </Transition>

    <!-- 右侧内容区 -->
    <main class="main-content">
      <!-- 顶部导航 -->
      <header class="header">
        <div class="header-left">
          <el-button class="menu-btn" text @click="mobileMenuOpen = true">
            <el-icon :size="22"><Menu /></el-icon>
          </el-button>
          
          <div class="breadcrumb">
            <el-icon class="breadcrumb-icon"><HomeFilled /></el-icon>
            <span class="breadcrumb-divider">/</span>
            <span class="breadcrumb-current">{{ modules[currentModule]?.name }}</span>
          </div>
        </div>

        <div class="header-right">
          <!-- 快捷操作 -->
          <div class="quick-actions">
            <el-tooltip content="刷新数据" placement="bottom">
              <el-button class="action-btn" circle @click="refreshData">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="全屏模式" placement="bottom">
              <el-button class="action-btn" circle @click="toggleFullscreen">
                <el-icon><FullScreen /></el-icon>
              </el-button>
            </el-tooltip>
          </div>

          <el-divider direction="vertical" />

          <!-- 用户信息 -->
          <el-dropdown trigger="click" @command="handleUserCommand">
            <div class="user-dropdown">
              <el-avatar :size="36" class="user-avatar">
                {{ authStore.user?.username?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <div class="user-info">
                <span class="user-name">{{ authStore.user?.username }}</span>
                <span class="user-role">超级管理员</span>
              </div>
              <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon> 个人资料
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon> 系统设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon> 退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 内容区域 -->
      <div class="content-wrapper">
        <!-- 模块标题 -->
        <div class="module-header">
          <div class="module-title">
            <div class="title-icon">
              <el-icon :size="24"><component :is="modules[currentModule]?.icon" /></el-icon>
            </div>
            <div class="title-text">
              <h1>{{ modules[currentModule]?.name }}</h1>
              <p>{{ modules[currentModule]?.description }}</p>
            </div>
          </div>
        </div>

        <!-- 模块内容 -->
        <Transition name="module-fade" mode="out-in">
          <div :key="currentModule" class="module-content">
            <!-- 用户管理 -->
            <UserManagementPanel v-if="currentModule === 'users'" ref="userPanelRef" />
            
            <!-- 激活码管理 -->
            <ActivationCodesPanel v-else-if="currentModule === 'activation'" ref="activationPanelRef" />
            
            <!-- 权限配置 -->
            <LevelPermissionsPanel v-else-if="currentModule === 'permissions'" />
            
            <!-- 等级管理 -->
            <LevelConfigPanel v-else-if="currentModule === 'levelConfig'" />
            
            <!-- 活动管理 -->
            <ActivityManagementPanel v-else-if="currentModule === 'events'" ref="activityPanelRef" />

            <!-- 道具限制管理 -->
            <ItemGiftManagementPanel v-else-if="currentModule === 'itemGift'" />

            <!-- 即将上线的模块 -->
            <div v-else class="coming-soon">
              <div class="coming-soon-content">
                <div class="coming-soon-icon">
                  <el-icon :size="64"><component :is="modules[currentModule]?.icon" /></el-icon>
                  <div class="icon-ring"></div>
                  <div class="icon-ring delay"></div>
                </div>
                <h2>{{ modules[currentModule]?.name }}</h2>
                <p class="main-text">该功能正在紧张开发中</p>
                <p class="sub-text">我们正在努力完善此功能，敬请期待！</p>
                
                <div class="progress-info">
                  <span>开发进度</span>
                  <el-progress :percentage="modules[currentModule]?.progress || 30" :stroke-width="8" />
                </div>

                <el-button type="primary" size="large" @click="switchModule('users')">
                  <el-icon><ArrowLeft /></el-icon> 返回用户管理
                </el-button>
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, markRaw, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Setting, Close, ArrowRight, ArrowLeft, Menu, User, 
  UserFilled, Key, Ticket, Bell, Message, Document, 
  Present, Star, HomeFilled, Refresh, FullScreen,
  ArrowDown, SwitchButton, Plus, DArrowLeft, DArrowRight, Goods
} from '@element-plus/icons-vue'

// 子模块组件
import UserManagementPanel from './modules/UserManagementPanel.vue'
import ActivationCodesPanel from './modules/ActivationCodesPanel.vue'
import LevelPermissionsPanel from './modules/LevelPermissionsPanel.vue'
import LevelConfigPanel from './modules/LevelConfigPanel.vue'

import ActivityManagementPanel from '@/views/admin/modules/ActivityManagementPanel.vue'
import ItemGiftManagementPanel from './modules/ItemGiftManagementPanel.vue'

const router = useRouter()
const authStore = useAuthStore()

// 响应式状态
const mobileMenuOpen = ref(false)
const sidebarCollapsed = ref(false)
const currentModule = ref('users')
const userPanelRef = ref(null)
const activationPanelRef = ref(null)
const activityPanelRef = ref(null)

// 核心模块
const coreModules = {
  users: {
    name: '用户管理',
    description: '管理系统用户账号、权限分配与状态控制',
    icon: markRaw(UserFilled),
    badge: null
  },
  activation: {
    name: '激活码管理',
    description: '生成、分发和管理用户激活码',
    icon: markRaw(Ticket),
    badge: null
  },
  permissions: {
    name: '权限配置',
    description: '配置不同等级用户的功能权限',
    icon: markRaw(Key),
    badge: null
  },
  levelConfig: {
    name: '等级管理',
    description: '管理等级配置，自定义等级名称',
    icon: markRaw(Star),
    badge: null
  },
  itemGift: {
    name: '道具限制',
    description: '管理道具白名单及等级发送限制',
    icon: markRaw(Goods),
    badge: null
  }
}

// 扩展模块
const extendModules = {
  announcements: {
    name: '公告管理',
    description: '发布和管理系统公告通知',
    icon: markRaw(Bell),
    coming: true,
    progress: 65
  },
  messages: {
    name: '消息管理',
    description: '管理用户消息和系统通知',
    icon: markRaw(Message),
    coming: true,
    progress: 40
  },
  tickets: {
    name: '工单管理',
    description: '处理用户反馈和工单请求',
    icon: markRaw(Document),
    coming: true,
    progress: 20
  },
  events: {
    name: '活动管理',
    description: '创建和管理游戏活动',
    icon: markRaw(Present),
    coming: false,
    progress: 100
  }
}

// 合并所有模块
const modules = { ...coreModules, ...extendModules }

// 切换模块
function switchModule(key) {
  if (modules[key]?.coming) return
  currentModule.value = key
  mobileMenuOpen.value = false
}

// 切换侧边栏
function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 返回功能后台
function goBack() {
  router.push('/')
}

// 刷新数据
function refreshData() {
  ElMessage.success('数据已刷新')
}

// 全屏模式
function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

// 用户下拉菜单命令
function handleUserCommand(command) {
  switch (command) {
    case 'profile':
      ElMessage.info('个人资料功能开发中')
      break
    case 'settings':
      ElMessage.info('系统设置功能开发中')
      break
    case 'logout':
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        authStore.logout()
        router.push('/login')
      }).catch(() => {})
      break
  }
}

// 快捷操作
function handleQuickAction() {
  if (currentModule.value === 'users') {
    userPanelRef.value?.showCreateDialog?.()
  } else if (currentModule.value === 'activation') {
    activationPanelRef.value?.showGenerateDialog?.()
  }
}

// 初始化
onMounted(() => {
  // 检查是否为移动端
  if (window.innerWidth <= 768) {
    sidebarCollapsed.value = false
  }
})
</script>

<style scoped>
/* ========== 变量定义 ========== */
.admin-container {
  --sidebar-width: 260px;
  --sidebar-collapsed-width: 72px;
  --header-height: 64px;
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --sidebar-bg: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  
  display: flex;
  min-height: 100vh;
  background: #f0f2f5;
}

/* ========== 侧边栏 ========== */
.sidebar {
  width: var(--sidebar-width);
  background: var(--sidebar-bg);
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 100;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.15);
}

.sidebar-collapsed .sidebar {
  width: var(--sidebar-collapsed-width);
}

/* Logo区域 */
.logo-area {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  min-height: 72px;
}

.logo-icon {
  width: 42px;
  height: 42px;
  background: var(--primary-gradient);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.logo-text {
  flex: 1;
  min-width: 0;
}

.logo-text h1 {
  color: white;
  font-size: 17px;
  font-weight: 700;
  margin: 0;
  letter-spacing: 0.5px;
}

.logo-text p {
  color: rgba(255, 255, 255, 0.5);
  font-size: 11px;
  margin: 2px 0 0;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.close-menu-btn {
  display: none;
  color: rgba(255, 255, 255, 0.7) !important;
}

/* 导航菜单 */
.nav-menu {
  flex: 1;
  padding: 16px 12px;
  overflow-y: auto;
  overflow-x: hidden;
}

.nav-menu::-webkit-scrollbar {
  width: 4px;
}

.nav-menu::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.nav-section {
  padding: 16px 8px 8px;
}

.nav-section-title {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.4);
  text-transform: uppercase;
  letter-spacing: 1.5px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.65);
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 4px;
  position: relative;
  overflow: hidden;
}

.nav-item::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
  opacity: 0;
  transition: opacity 0.2s;
}

.nav-item:hover {
  color: white;
}

.nav-item:hover::before {
  opacity: 1;
}

.nav-item.active {
  color: white;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3));
}

.nav-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nav-item-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  flex-shrink: 0;
  transition: all 0.2s;
}

.nav-item.active .nav-item-icon {
  background: var(--primary-gradient);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.nav-item-text {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
}

.nav-badge {
  background: #ef4444;
  color: white;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 600;
}

.nav-indicator {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 24px;
  background: var(--primary-gradient);
  border-radius: 3px 0 0 3px;
}

.nav-item .el-tag {
  font-size: 10px;
  margin-left: auto;
}

/* 折叠按钮 */
.collapse-btn-wrapper {
  padding: 0 12px 12px;
  display: flex;
  justify-content: center;
}

.collapse-btn {
  width: 100%;
  height: 36px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
  transition: all 0.2s;
}

.collapse-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.sidebar-collapsed .collapse-btn {
  width: 40px;
}

/* 底部区域 */
.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  text-align: center;
}

.back-btn {
  width: 100%;
  height: 40px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
  font-size: 13px;
  transition: all 0.2s;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border-color: rgba(255, 255, 255, 0.2);
}

.sidebar-collapsed .back-btn {
  width: 40px;
  padding: 0;
}

.copyright {
  color: rgba(255, 255, 255, 0.3);
  font-size: 11px;
  margin: 12px 0 0;
}

/* ========== 主内容区 ========== */
.main-content {
  flex: 1;
  margin-left: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-collapsed .main-content {
  margin-left: var(--sidebar-collapsed-width);
}

/* 头部 */
.header {
  height: var(--header-height);
  background: white;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 50;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.menu-btn {
  display: none;
  width: 40px;
  height: 40px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.breadcrumb-icon {
  color: #9ca3af;
}

.breadcrumb-divider {
  color: #d1d5db;
}

.breadcrumb-current {
  color: #374151;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.quick-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 36px;
  height: 36px;
  background: #f3f4f6;
  border: none;
  color: #6b7280;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #e5e7eb;
  color: #374151;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px 6px 6px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.user-dropdown:hover {
  background: #f3f4f6;
}

.user-avatar {
  background: var(--primary-gradient);
  color: white;
  font-weight: 600;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  line-height: 1.2;
}

.user-role {
  font-size: 11px;
  color: #9ca3af;
}

.dropdown-arrow {
  color: #9ca3af;
  font-size: 12px;
}

/* 内容区域 */
.content-wrapper {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.module-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.module-title {
  display: flex;
  align-items: center;
  gap: 16px;
}

.title-icon {
  width: 52px;
  height: 52px;
  background: var(--primary-gradient);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.title-text h1 {
  font-size: 22px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.title-text p {
  font-size: 13px;
  color: #6b7280;
  margin: 4px 0 0;
}

.module-actions {
  display: flex;
  gap: 12px;
}

.module-content {
  min-height: 400px;
}

/* ========== Coming Soon ========== */
.coming-soon {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 280px);
}

.coming-soon-content {
  text-align: center;
  padding: 48px;
  background: white;
  border-radius: 24px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  max-width: 420px;
  width: 100%;
}

.coming-soon-icon {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
  border-radius: 50%;
  color: #6366f1;
  margin-bottom: 24px;
}

.icon-ring {
  position: absolute;
  inset: -8px;
  border: 2px solid rgba(99, 102, 241, 0.3);
  border-radius: 50%;
  animation: ring-pulse 2s ease-out infinite;
}

.icon-ring.delay {
  animation-delay: 1s;
}

@keyframes ring-pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(1.3);
    opacity: 0;
  }
}

.coming-soon-content h2 {
  font-size: 24px;
  color: #1f2937;
  margin: 0 0 12px;
  font-weight: 700;
}

.coming-soon-content .main-text {
  font-size: 15px;
  color: #4b5563;
  margin: 0;
}

.coming-soon-content .sub-text {
  font-size: 13px;
  color: #9ca3af;
  margin: 8px 0 0;
}

.progress-info {
  margin: 32px 0;
  padding: 16px;
  background: #f9fafb;
  border-radius: 12px;
}

.progress-info span {
  display: block;
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 8px;
  text-align: left;
}

/* ========== 移动端适配 ========== */
.mobile-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 99;
  backdrop-filter: blur(4px);
}

@media (max-width: 768px) {
  .admin-container {
    --sidebar-width: 280px;
  }
  
  .sidebar {
    transform: translateX(-100%);
  }
  
  .sidebar.mobile-open {
    transform: translateX(0);
  }
  
  .close-menu-btn {
    display: flex;
    margin-left: auto;
  }
  
  .collapse-btn-wrapper {
    display: none;
  }
  
  .main-content {
    margin-left: 0 !important;
  }
  
  .menu-btn {
    display: flex;
  }
  
  .header {
    padding: 0 16px;
  }
  
  .quick-actions {
    display: none;
  }
  
  .user-info {
    display: none;
  }
  
  .content-wrapper {
    padding: 16px;
  }
  
  .module-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .title-icon {
    width: 44px;
    height: 44px;
  }
  
  .title-text h1 {
    font-size: 18px;
  }
}

/* ========== 动画 ========== */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.module-fade-enter-active {
  transition: all 0.3s ease-out;
}

.module-fade-leave-active {
  transition: all 0.2s ease-in;
}

.module-fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.module-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>