<template>
  <div class="activation-panel">
    <!-- 标题 -->
    <div class="header">
      <el-icon class="header-icon"><Ticket /></el-icon>
      <div class="header-text">
        <h1>激活码权限对比</h1>
        <p>选择适合您的等级，立即解锁更多高级功能</p>
      </div>
    </div>

    <!-- 当前等级提示 -->
    <div class="current-level-tip" v-if="currentUserLevel > 0">
      <el-icon><StarFilled /></el-icon>
      <span>您当前等级：<strong>Level {{ currentUserLevel }}</strong></span>
    </div>

    <!-- 权限对比卡片列表 -->
    <div class="levels-container">
      <!-- 骨架屏加载 -->
      <template v-if="loading">
        <div v-for="i in 10" :key="'skeleton-' + i" class="level-card skeleton-card">
          <div class="card-header skeleton-header">
            <el-skeleton :rows="0" animated>
              <template #template>
                <el-skeleton-item variant="circle" style="width: 80px; height: 80px; border-radius: 20px;" />
              </template>
            </el-skeleton>
          </div>
          <div class="skeleton-body">
            <el-skeleton :rows="4" animated />
          </div>
        </div>
      </template>

      <!-- 实际卡片 -->
      <template v-else>
        <div
          v-for="level in 10"
          :key="level"
          class="level-card"
          :class="{
            'current': level === currentUserLevel,
            'recommended': level === recommendedLevel,
            [`level-${level}`]: true
          }"
        >
          <!-- 推荐标签 -->
          <div v-if="level === recommendedLevel" class="recommend-ribbon">
            <span>推荐</span>
          </div>

          <!-- 卡片头部 -->
          <div class="card-header">
            <div class="level-badge">
              <span class="num">{{ level }}</span>
              <span class="text">Level</span>
            </div>
            <div v-if="level === currentUserLevel" class="current-tag">
              <el-icon><Star /></el-icon> 当前等级
            </div>
          </div>

          <!-- 价格区域 -->
          <div class="price-section">
            <span class="price-symbol">¥</span>
            <span class="price-value">{{ levelPrices[level] }}</span>
            <span class="price-unit">/月起</span>
          </div>

          <!-- 权限数量统计 -->
          <div class="perm-count">
            <el-icon><Check /></el-icon>
            <span>{{ getLevelPermissions(level).length }} 项专属权限</span>
          </div>

          <!-- 权限标签预览 -->
          <div class="perm-tags">
            <el-tag
              v-for="code in getLevelPermissions(level).slice(0, 6)"
              :key="code"
              size="small"
              effect="plain"
              round
            >
              {{ getPermissionName(code) }}
            </el-tag>
            <el-tag
              v-if="getLevelPermissions(level).length > 6"
              size="small"
              type="info"
              round
            >
              +{{ getLevelPermissions(level).length - 6 }}
            </el-tag>
          </div>

          <!-- 购买按钮区 -->
          <div class="card-footer">
            <el-button
              type="primary"
              size="large"
              round
              class="buy-btn"
              :class="{ 'btn-disabled': level <= currentUserLevel }"
              @click="openPurchaseDialog(level)"
              :disabled="level <= currentUserLevel"
            >
              <template v-if="level < currentUserLevel">
                <el-icon><CircleCheck /></el-icon>
                已拥有
              </template>
              <template v-else-if="level === currentUserLevel">
                <el-icon><Lock /></el-icon>
                当前等级
              </template>
              <template v-else>
                <el-icon><ShoppingCart /></el-icon>
                立即购买
              </template>
            </el-button>
          </div>

          <!-- 展开触发器 -->
          <div
            class="expand-trigger"
            @click="toggleExpand(level)"
            role="button"
            :aria-expanded="expandedLevel === level"
            tabindex="0"
            @keydown.enter="toggleExpand(level)"
          >
            <span>{{ expandedLevel === level ? '收起权限列表' : '查看全部权限' }}</span>
            <el-icon :class="{ rotate: expandedLevel === level }"><ArrowDown /></el-icon>
          </div>

          <!-- 展开的完整权限列表 -->
          <transition name="slide-fade">
            <div v-show="expandedLevel === level" class="expanded-permissions">
              <div class="expanded-header">
                <el-icon><List /></el-icon>
                <span>完整权限列表</span>
                <el-tag size="small" type="success">{{ getLevelPermissions(level).length }}项</el-tag>
              </div>
              <div class="expanded-tags">
                <el-tag
                  v-for="code in getLevelPermissions(level)"
                  :key="code"
                  size="small"
                  round
                  class="expanded-tag"
                >
                  <el-icon v-if="isNewPermission(level, code)" class="new-icon"><Promotion /></el-icon>
                  {{ getPermissionName(code) }}
                </el-tag>
              </div>
              <div v-if="level > 1" class="new-permissions-hint">
                <el-icon><Promotion /></el-icon>
                <span>带标记的为相比上一等级新增的权限</span>
              </div>
            </div>
          </transition>
        </div>
      </template>
    </div>

    <!-- 购买弹窗 -->
    <el-dialog
      v-model="purchaseDialogVisible"
      title=""
      width="92%"
      :style="{ maxWidth: '500px' }"
      class="purchase-dialog"
      destroy-on-close
      center
      :close-on-click-modal="!purchasing"
      :close-on-press-escape="!purchasing"
    >
      <div class="dialog-content">
        <!-- 弹窗头部 -->
        <div class="dialog-header" :class="`level-${selectedLevel}`">
          <div class="level-badge-large">
            <span>{{ selectedLevel }}</span>
          </div>
          <div class="dialog-header-text">
            <h3>升级到 Level {{ selectedLevel }}</h3>
            <p>解锁 {{ getLevelPermissions(selectedLevel).length }} 项高级功能权限</p>
          </div>
        </div>

        <!-- 表单区域 -->
        <el-form :model="purchaseForm" label-position="top" class="purchase-form">
          <el-form-item label="购买数量">
            <el-input-number
              v-model="purchaseForm.count"
              :min="1"
              :max="50"
              size="large"
              style="width: 100%"
              controls-position="right"
            />
            <div class="form-hint">批量购买可用于分发给团队成员</div>
          </el-form-item>

          <el-form-item label="有效期">
            <el-radio-group v-model="purchaseForm.expires_days" class="duration-group">
              <el-radio-button :label="30">
                <div class="duration-option">
                  <span class="duration-label">1个月</span>
                  <span class="duration-price">¥{{ calcPrice(30) }}</span>
                </div>
              </el-radio-button>
              <el-radio-button :label="90">
                <div class="duration-option">
                  <span class="duration-label">3个月</span>
                  <span class="duration-price">¥{{ calcPrice(90) }}</span>
                  <span class="duration-discount">省15%</span>
                </div>
              </el-radio-button>
              <el-radio-button :label="180">
                <div class="duration-option">
                  <span class="duration-label">半年</span>
                  <span class="duration-price">¥{{ calcPrice(180) }}</span>
                  <span class="duration-discount">省25%</span>
                </div>
              </el-radio-button>
              <el-radio-button :label="365">
                <div class="duration-option">
                  <span class="duration-label">1年</span>
                  <span class="duration-price">¥{{ calcPrice(365) }}</span>
                  <span class="duration-discount">省35%</span>
                </div>
              </el-radio-button>
              <el-radio-button :label="99999">
                <div class="duration-option">
                  <span class="duration-label">永久</span>
                  <span class="duration-price">¥{{ calcPrice(99999) }}</span>
                  <span class="duration-discount">最划算</span>
                </div>
              </el-radio-button>
            </el-radio-group>
          </el-form-item>
        </el-form>

        <!-- 价格汇总 -->
        <div class="price-summary">
          <div class="price-row">
            <span class="price-label">单价</span>
            <span class="price-value">¥{{ unitPrice }}</span>
          </div>
          <div class="price-row">
            <span class="price-label">数量</span>
            <span class="price-value">× {{ purchaseForm.count }}</span>
          </div>
          <div class="price-row total">
            <span class="price-label">总计</span>
            <span class="price-value">
              <span class="currency">¥</span>
              <span class="amount">{{ totalPrice }}</span>
            </span>
          </div>
        </div>

        <!-- 提示信息 -->
        <div class="price-hint">
          <div class="hint-item">
            <el-icon><CircleCheck /></el-icon>
            <span>购买后立即生效</span>
          </div>
          <div class="hint-item">
            <el-icon><CircleCheck /></el-icon>
            <span>激活码可重复使用</span>
          </div>
          <div class="hint-item">
            <el-icon><CircleCheck /></el-icon>
            <span>支持退款保障</span>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button size="large" @click="purchaseDialogVisible = false" :disabled="purchasing">
            取消
          </el-button>
          <el-button
            type="primary"
            size="large"
            :loading="purchasing"
            @click="purchaseCode"
            class="confirm-btn"
          >
            <el-icon v-if="!purchasing"><ShoppingCart /></el-icon>
            {{ purchasing ? '处理中...' : `确认支付 ¥${totalPrice}` }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 购买成功弹窗 -->
    <el-dialog
      v-model="successDialogVisible"
      title=""
      width="90%"
      :style="{ maxWidth: '400px' }"
      class="success-dialog"
      center
    >
      <div class="success-content">
        <div class="success-icon">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <h3>购买成功！</h3>
        <p>成功生成 {{ lastPurchase.count }} 个 Level {{ lastPurchase.level }} 激活码</p>
        <div class="success-codes" v-if="lastPurchase.codes?.length">
          <div class="codes-header">
            <span>激活码列表</span>
            <el-button type="primary" link @click="copyAllCodes">
              <el-icon><DocumentCopy /></el-icon>
              复制全部
            </el-button>
          </div>
          <div class="codes-list">
            <div v-for="code in lastPurchase.codes" :key="code" class="code-item">
              <span class="code-text">{{ code }}</span>
              <el-button type="primary" link size="small" @click="copyCode(code)">
                复制
              </el-button>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" size="large" @click="successDialogVisible = false" style="width: 100%">
          我知道了
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import request from '@/api/request'
import { ElMessage } from 'element-plus'
import {
  Ticket, StarFilled, Star, Check, ShoppingCart, Lock, List,
  ArrowDown, CircleCheck, Promotion, DocumentCopy
} from '@element-plus/icons-vue'

// Store
const authStore = useAuthStore()

// 状态
const loading = ref(false)
const purchasing = ref(false)
const purchaseDialogVisible = ref(false)
const successDialogVisible = ref(false)
const selectedLevel = ref(1)
const expandedLevel = ref(null)

// 数据
const allPermissions = ref({})
const levelPermissionsMap = ref({})

// 价格配置
const levelPrices = {
  1: 9.9,
  2: 19.9,
  3: 29.9,
  4: 49.9,
  5: 79.9,
  6: 99.9,
  7: 149.9,
  8: 199.9,
  9: 299.9,
  10: 499.9
}

// 有效期价格系数
const durationMultipliers = {
  30: 1,
  90: 2.55,    // 原价3倍，打85折
  180: 4.5,    // 原价6倍，打75折
  365: 7.8,    // 原价12倍，打65折
  99999: 12    // 永久，相当于12个月
}

// 购买表单
const purchaseForm = reactive({
  count: 1,
  expires_days: 30
})

// 上次购买记录
const lastPurchase = reactive({
  level: 0,
  count: 0,
  codes: []
})

// 计算属性
const currentUserLevel = computed(() => authStore.user?.level || 0)

const recommendedLevel = computed(() => {
  const current = currentUserLevel.value
  if (current >= 10) return null
  return Math.min(current + 2, 10) // 推荐比当前高2级
})

const unitPrice = computed(() => {
  const base = levelPrices[selectedLevel.value] || 0
  const multiplier = durationMultipliers[purchaseForm.expires_days] || 1
  return (base * multiplier).toFixed(2)
})

const totalPrice = computed(() => {
  return (parseFloat(unitPrice.value) * purchaseForm.count).toFixed(2)
})

// 方法
function getLevelPermissions(level) {
  return levelPermissionsMap.value[level] || []
}

function getPermissionName(code) {
  for (const perms of Object.values(allPermissions.value)) {
    const perm = perms.find(p => p.code === code)
    if (perm) return perm.name
  }
  if (code === '*') return '所有权限'
  if (code.endsWith('.*')) {
    const cat = code.split('.')[0]
    const names = {
      account: '账号管理',
      pet: '宠物管理',
      equipment: '装备管理',
      gift: '礼物道具',
      character: '角色管理',
      game: '游戏管理'
    }
    return `${names[cat] || cat} - 全部权限`
  }
  return code
}

function isNewPermission(level, code) {
  if (level <= 1) return false
  const prevPerms = getLevelPermissions(level - 1)
  return !prevPerms.includes(code)
}

function calcPrice(days) {
  const base = levelPrices[selectedLevel.value] || 0
  const multiplier = durationMultipliers[days] || 1
  return (base * multiplier).toFixed(0)
}

function toggleExpand(level) {
  expandedLevel.value = expandedLevel.value === level ? null : level
}

function openPurchaseDialog(level) {
  selectedLevel.value = level
  purchaseForm.count = 1
  purchaseForm.expires_days = 30
  purchaseDialogVisible.value = true
}

async function loadAllPermissions() {
  try {
    const res = await request.get('/api/permissions')
    allPermissions.value = res.permissions || {}
  } catch (e) {
    console.error('加载权限失败:', e)
    throw e
  }
}

async function loadLevelPermissions() {
  try {
    // 使用 Promise.all 并行请求所有等级的权限
    const promises = Array.from({ length: 10 }, (_, i) =>
      request.get(`/api/levels/${i + 1}/permissions`)
    )
    const results = await Promise.all(promises)
    results.forEach((res, index) => {
      levelPermissionsMap.value[index + 1] = res.permission_codes || []
    })
  } catch (e) {
    console.error('加载等级权限失败:', e)
    throw e
  }
}

async function purchaseCode() {
  purchasing.value = true
  try {
    const res = await request.post('/api/activation/generate', {
      level: selectedLevel.value,
      count: purchaseForm.count,
      expires_days: purchaseForm.expires_days
    })

    // 保存购买结果
    lastPurchase.level = selectedLevel.value
    lastPurchase.count = purchaseForm.count
    lastPurchase.codes = res.codes || []

    purchaseDialogVisible.value = false
    successDialogVisible.value = true

    // 重置表单
    purchaseForm.count = 1
    purchaseForm.expires_days = 30
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '购买失败，请稍后重试')
  } finally {
    purchasing.value = false
  }
}

function copyCode(code) {
  navigator.clipboard.writeText(code).then(() => {
    ElMessage.success('激活码已复制')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

function copyAllCodes() {
  const text = lastPurchase.codes.join('\n')
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('所有激活码已复制')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

// 初始化
onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      loadAllPermissions(),
      loadLevelPermissions()
    ])
  } catch (e) {
    ElMessage.error('加载数据失败，请刷新重试')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.activation-panel {
  padding: 24px 16px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f4f8 0%, #e0e7ff 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}

/* ==================== 标题区域 ==================== */
.header {
  text-align: center;
  margin-bottom: 32px;
}

.header-icon {
  font-size: 48px;
  color: #667eea;
  margin-bottom: 12px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.header-text h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.header-text p {
  color: #64748b;
  font-size: 15px;
  margin: 0;
}

/* ==================== 当前等级提示 ==================== */
.current-level-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 24px;
  padding: 12px 20px;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 12px;
  color: #92400e;
  font-size: 15px;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
  box-shadow: 0 4px 15px rgba(251, 191, 36, 0.2);
}

.current-level-tip strong {
  font-weight: 700;
  color: #d97706;
}

/* ==================== 等级卡片容器 ==================== */
.levels-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

/* ==================== 骨架屏样式 ==================== */
.skeleton-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
}

.skeleton-header {
  padding: 24px;
  background: linear-gradient(135deg, #e2e8f0, #cbd5e1);
  display: flex;
  justify-content: center;
}

.skeleton-body {
  padding: 20px;
}

/* ==================== 单个等级卡片 ==================== */
.level-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.level-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.level-card.current {
  border: 3px solid #fbbf24;
  box-shadow: 0 15px 40px rgba(251, 191, 36, 0.3);
}

.level-card.recommended {
  border: 3px solid #22c55e;
}

/* 推荐标签 */
.recommend-ribbon {
  position: absolute;
  top: 16px;
  right: -30px;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
  padding: 6px 40px;
  font-size: 12px;
  font-weight: 600;
  transform: rotate(45deg);
  z-index: 10;
  box-shadow: 0 2px 10px rgba(34, 197, 94, 0.4);
}

/* ==================== 卡片头部 ==================== */
.card-header {
  padding: 24px 20px 16px;
  text-align: center;
  background: linear-gradient(135deg, var(--header-from), var(--header-to));
  color: white;
  position: relative;
}

.level-badge {
  width: 80px;
  height: 80px;
  margin: 0 auto 12px;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  transition: transform 0.3s;
}

.level-card:hover .level-badge {
  transform: scale(1.05);
}

.level-badge .num {
  font-size: 32px;
  font-weight: 800;
  line-height: 1;
}

.level-badge .text {
  font-size: 11px;
  font-weight: 600;
  opacity: 0.9;
}

.current-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.25);
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  margin-top: 8px;
}

/* ==================== 价格区域 ==================== */
.price-section {
  text-align: center;
  padding: 16px 20px 8px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.price-symbol {
  font-size: 16px;
  font-weight: 600;
  color: #ef4444;
  vertical-align: top;
}

.price-value {
  font-size: 36px;
  font-weight: 800;
  color: #ef4444;
  line-height: 1;
}

.price-unit {
  font-size: 14px;
  color: #64748b;
  margin-left: 4px;
}

/* ==================== 权限数量 ==================== */
.perm-count {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 16px 20px 8px;
  color: #475569;
  font-size: 14px;
}

.perm-count .el-icon {
  color: #22c55e;
}

/* ==================== 权限标签预览 ==================== */
.perm-tags {
  padding: 0 20px 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  min-height: 70px;
}

/* ==================== 卡片底部 ==================== */
.card-footer {
  padding: 16px 20px;
  text-align: center;
  background: #f8fafc;
}

.buy-btn {
  min-width: 160px;
  font-weight: 600;
  transition: all 0.3s;
}

.buy-btn:not(.btn-disabled):hover {
  transform: scale(1.05);
}

.btn-disabled {
  background: #94a3b8 !important;
  border-color: #94a3b8 !important;
}

/* ==================== 展开触发器 ==================== */
.expand-trigger {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px;
  cursor: pointer;
  color: #64748b;
  font-size: 14px;
  transition: all 0.2s;
  border-top: 1px dashed #e2e8f0;
  user-select: none;
}

.expand-trigger:hover {
  color: #667eea;
  background: #f8fafc;
}

.expand-trigger:focus {
  outline: 2px solid #667eea;
  outline-offset: -2px;
}

.expand-trigger .el-icon {
  transition: transform 0.3s;
}

.expand-trigger .rotate {
  transform: rotate(180deg);
}

/* ==================== 展开权限列表 ==================== */
.expanded-permissions {
  background: #f1f5f9;
  padding: 20px;
  border-top: 1px dashed #cbd5e1;
}

.expanded-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  font-weight: 600;
  color: #334155;
}

.expanded-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.expanded-tag {
  background: white;
  border: 1px solid #e2e8f0;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.new-icon {
  color: #22c55e;
  font-size: 12px;
}

.new-permissions-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px dashed #cbd5e1;
  font-size: 12px;
  color: #64748b;
}

.new-permissions-hint .el-icon {
  color: #22c55e;
}

/* ==================== 等级专属渐变色 ==================== */
.level-1 .card-header { --header-from: #94a3b8; --header-to: #64748b; }
.level-2 .card-header { --header-from: #a78bfa; --header-to: #8b5cf6; }
.level-3 .card-header { --header-from: #60a5fa; --header-to: #3b82f6; }
.level-4 .card-header { --header-from: #4ade80; --header-to: #22c55e; }
.level-5 .card-header { --header-from: #fbbf24; --header-to: #f59e0b; }
.level-6 .card-header { --header-from: #fb923c; --header-to: #f97316; }
.level-7 .card-header { --header-from: #f87171; --header-to: #ef4444; }
.level-8 .card-header { --header-from: #e879f9; --header-to: #d946ef; }
.level-9 .card-header { --header-from: #818cf8; --header-to: #6366f1; }
.level-10 .card-header {
  --header-from: #fcd34d;
  --header-to: #f59e0b;
  background: linear-gradient(135deg, #fcd34d 0%, #f59e0b 50%, #fbbf24 100%);
}

/* ==================== 购买弹窗 ==================== */
.purchase-dialog :deep(.el-dialog) {
  border-radius: 24px;
  overflow: hidden;
}

.purchase-dialog :deep(.el-dialog__header) {
  display: none;
}

.purchase-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.dialog-content {
  padding: 0;
}

/* 弹窗头部 */
.dialog-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background: linear-gradient(135deg, var(--dialog-from, #667eea), var(--dialog-to, #764ba2));
  color: white;
}

.dialog-header.level-1 { --dialog-from: #94a3b8; --dialog-to: #64748b; }
.dialog-header.level-2 { --dialog-from: #a78bfa; --dialog-to: #8b5cf6; }
.dialog-header.level-3 { --dialog-from: #60a5fa; --dialog-to: #3b82f6; }
.dialog-header.level-4 { --dialog-from: #4ade80; --dialog-to: #22c55e; }
.dialog-header.level-5 { --dialog-from: #fbbf24; --dialog-to: #f59e0b; }
.dialog-header.level-6 { --dialog-from: #fb923c; --dialog-to: #f97316; }
.dialog-header.level-7 { --dialog-from: #f87171; --dialog-to: #ef4444; }
.dialog-header.level-8 { --dialog-from: #e879f9; --dialog-to: #d946ef; }
.dialog-header.level-9 { --dialog-from: #818cf8; --dialog-to: #6366f1; }
.dialog-header.level-10 { --dialog-from: #fcd34d; --dialog-to: #f59e0b; }

.level-badge-large {
  width: 72px;
  height: 72px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  font-weight: 800;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  flex-shrink: 0;
}

.dialog-header-text h3 {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
}

.dialog-header-text p {
  margin: 6px 0 0;
  opacity: 0.9;
  font-size: 14px;
}

/* 表单区域 */
.purchase-form {
  padding: 24px 24px 0;
}

.purchase-form :deep(.el-form-item__label) {
  font-weight: 600;
  color: #334155;
}

.form-hint {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 6px;
}

/* 有效期选择 */
.duration-group {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.duration-group :deep(.el-radio-button) {
  width: 100%;
  margin: 0;
}

.duration-group :deep(.el-radio-button__inner) {
  width: 100%;
  border-radius: 12px !important;
  border: 2px solid #e2e8f0 !important;
  padding: 12px 16px;
  text-align: left;
}

.duration-group :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  border-color: #667eea !important;
  background: #f0f4ff;
  color: #667eea;
}

.duration-option {
  display: flex;
  align-items: center;
  gap: 12px;
}

.duration-label {
  font-weight: 600;
  min-width: 60px;
}

.duration-price {
  font-weight: 700;
  color: #ef4444;
}

.duration-discount {
  margin-left: auto;
  padding: 2px 8px;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}

/* 价格汇总 */
.price-summary {
  margin: 20px 24px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  color: #64748b;
  font-size: 14px;
}

.price-row.total {
  border-top: 1px dashed #e2e8f0;
  margin-top: 8px;
  padding-top: 16px;
}

.price-row.total .price-label {
  font-weight: 700;
  color: #1e293b;
  font-size: 16px;
}

.price-row.total .price-value {
  color: #ef4444;
}

.price-row.total .currency {
  font-size: 18px;
  font-weight: 700;
}

.price-row.total .amount {
  font-size: 32px;
  font-weight: 800;
}

/* 提示信息 */
.price-hint {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 16px 24px;
  background: #f0fdf4;
  border-top: 1px solid #bbf7d0;
}

.hint-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #166534;
  font-size: 13px;
}

.hint-item .el-icon {
  color: #22c55e;
}

/* 弹窗底部 */
.dialog-footer {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  background: white;
  border-top: 1px solid #e2e8f0;
}

.dialog-footer .el-button {
  flex: 1;
}

.confirm-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important;
  font-weight: 600;
}

.confirm-btn:hover {
  opacity: 0.9;
}

/* ==================== 成功弹窗 ==================== */
.success-dialog :deep(.el-dialog) {
  border-radius: 24px;
}

.success-dialog :deep(.el-dialog__header) {
  display: none;
}

.success-content {
  text-align: center;
  padding: 24px;
}

.success-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  color: white;
  animation: success-pop 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes success-pop {
  0% { transform: scale(0); }
  100% { transform: scale(1); }
}

.success-content h3 {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px;
}

.success-content > p {
  color: #64748b;
  margin: 0 0 20px;
}

.success-codes {
  text-align: left;
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
  margin-top: 20px;
}

.codes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: 600;
  color: #334155;
}

.codes-list {
  max-height: 200px;
  overflow-y: auto;
}

.code-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: white;
  border-radius: 8px;
  margin-bottom: 8px;
  border: 1px solid #e2e8f0;
}

.code-item:last-child {
  margin-bottom: 0;
}

.code-text {
  font-family: 'Courier New', monospace;
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

/* ==================== 动画 ==================== */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.slide-fade-enter-to,
.slide-fade-leave-from {
  max-height: 500px;
}

/* ==================== 响应式 ==================== */
@media (max-width: 768px) {
  .activation-panel {
    padding: 16px 12px;
  }

  .levels-container {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .header-icon {
    font-size: 40px;
  }

  .header-text h1 {
    font-size: 22px;
  }

  .header-text p {
    font-size: 14px;
  }

  .level-badge {
    width: 70px;
    height: 70px;
  }

  .level-badge .num {
    font-size: 28px;
  }

  .price-value {
    font-size: 30px;
  }

  .dialog-header {
    flex-direction: column;
    text-align: center;
  }

  .duration-option {
    flex-wrap: wrap;
  }

  .duration-discount {
    margin-left: 0;
    margin-top: 4px;
  }

  .price-hint {
    flex-direction: column;
    gap: 10px;
  }

  .dialog-footer {
    flex-direction: column;
  }

  .dialog-footer .el-button {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .recommend-ribbon {
    font-size: 10px;
    padding: 4px 30px;
    right: -35px;
  }

  .perm-tags {
    min-height: auto;
  }
}

/* ==================== 深色模式适配（可选） ==================== */
@media (prefers-color-scheme: dark) {
  /* 如需支持深色模式，可在此添加样式 */
}
</style>