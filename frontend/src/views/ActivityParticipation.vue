<template>
  <div class="lucky-draw-page">
    <!-- 动态背景层 -->
    <div class="background-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
    </div>

    <div class="content-container">
      <!-- 头部区域 -->
      <header class="page-header">
        <div class="glass-card header-card">
          <h1 class="main-title">{{ activity.activity?.name || '幸运大转盘' }}</h1>
          <p class="sub-title" v-if="activity.activity?.description">
            {{ activity.activity.description }}
          </p>
          
          <div class="status-bar">
            <div class="status-item">
              <span class="dot" :class="activityStatus.type"></span>
              <span>{{ activityStatus.text }}</span>
            </div>
            <div class="status-item" v-if="timeRemaining > 0">
              <span>⏱️ {{ formatTimeRemaining(timeRemaining) }}</span>
            </div>
          </div>
        </div>
      </header>

      <!-- 登录/输入 ID 区域 -->
      <section class="login-section" v-if="requiresLogin && !hasJoined">
        <div class="glass-card login-card">
          <div class="login-icon">🎮</div>
          <h2>开启您的幸运之旅</h2>
          <div class="input-group">
            <el-input 
              v-model="userInfo.game_id" 
              placeholder="请输入您的游戏ID" 
              size="large"
              class="custom-input"
              @keyup.enter="startParticipate"
            />
            <el-button 
              type="primary" 
              size="large" 
              class="start-btn"
              :loading="isLoading"
              :disabled="!userInfo.game_id.trim()"
              @click="startParticipate"
            >
              立即参与
            </el-button>
          </div>
        </div>
      </section>

      <!-- 主游戏区域 -->
      <section class="game-section" v-if="!requiresLogin || hasJoined">
        
        <!-- 用户信息条 -->
        <div class="user-bar glass-card" v-if="hasJoined">
          <div class="user-profile">
            <div class="avatar">{{ userInfo.game_id.charAt(0).toUpperCase() }}</div>
            <div class="info">
              <div class="user-id">{{ userInfo.game_id }}</div>
              <div class="chances">
                剩余次数: <span class="highlight">{{ isUnlimited ? '无限' : remainingParticipations }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 转盘主体 -->
        <div class="wheel-wrapper">
          <!-- 外圈装饰 -->
          <div class="wheel-outer-ring">
            <!-- 装饰灯泡 -->
            <div class="lights-container">
              <span 
                v-for="n in 16" 
                :key="n" 
                class="light-bulb"
                :class="{ 'light-on': n % 2 === lightState }"
              ></span>
            </div>
            
            <!-- 转盘容器 -->
            <div class="wheel-inner">
              <!-- 旋转盘面 -->
              <div class="wheel-rotate-panel" :style="wheelRotateStyle">
                <!-- 扇区背景 -->
                <div class="wheel-bg" :style="wheelBgStyle"></div>

                <!-- 分割线 -->
                <div 
                  v-for="(_, index) in activity.rewards" 
                  :key="'line-'+index"
                  class="wheel-line"
                  :style="getLineStyle(index)"
                ></div>

                <!-- 奖品内容 -->
                <div 
                  v-for="(reward, index) in activity.rewards" 
                  :key="'item-'+(reward.id || index)"
                  class="wheel-item"
                  :style="getItemStyle(index)"
                >
                  <div class="item-content">
                    <span class="wheel-text">{{ reward.name }}</span>
                    <span class="wheel-icon">{{ reward.icon || '🎁' }}</span>
                  </div>
                </div>
              </div>

              <!-- 中心指针按钮 -->
              <div 
                class="wheel-pointer" 
                :class="{ 'disabled': !canDraw, 'drawing': isDrawing }"
                @click="handleDrawClick"
              >
                <div class="pointer-arrow"></div>
                <div class="pointer-center">
                  <span class="pointer-text">{{ isDrawing ? '...' : 'GO' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 奖品列表 -->
      <section class="info-section" v-if="displayRewards?.length">
        <div class="glass-card rewards-section">
          <div class="card-header"><h3>🎁 奖池一览</h3></div>
          
          <!-- 奖品滚动容器 -->
          <div class="rewards-scroll-container" :class="{ 'no-scroll': !shouldScroll }">
            <div 
              class="rewards-track" 
              :class="{ 'scrolling': shouldScroll }"
              :style="scrollStyle"
            >
              <!-- 原始奖品列表 -->
              <div 
                v-for="reward in displayRewards" 
                :key="'reward-' + reward.id"
                class="reward-card"
                :class="{ 'sold-out': reward.remaining_quantity === 0 }"
              >
                <span class="reward-icon">{{ reward.icon || '🎁' }}</span>
                <span class="reward-name">{{ reward.name }}</span>
                <span class="reward-stock" v-if="reward.remaining_quantity !== undefined && reward.remaining_quantity >= 0">
                  剩余 {{ reward.remaining_quantity }}
                </span>
              </div>
              
              <!-- 复制一份用于无缝滚动 -->
              <template v-if="shouldScroll">
                <div 
                  v-for="reward in displayRewards" 
                  :key="'reward-copy-' + reward.id"
                  class="reward-card"
                  :class="{ 'sold-out': reward.remaining_quantity === 0 }"
                >
                  <span class="reward-icon">{{ reward.icon || '🎁' }}</span>
                  <span class="reward-name">{{ reward.name }}</span>
                  <span class="reward-stock" v-if="reward.remaining_quantity !== undefined && reward.remaining_quantity >= 0">
                    剩余 {{ reward.remaining_quantity }}
                  </span>
                </div>
              </template>
            </div>
          </div>
        </div>

        <!-- 中奖记录 -->
        <div class="glass-card" v-if="hasJoined">
          <div class="card-header"><h3>📜 我的记录</h3></div>
          <div class="history-list" v-if="participationHistory.length > 0">
            <div v-for="record in participationHistory" :key="record.id" class="history-row">
              <span class="history-time">{{ formatTimeShort(record.created_at) }}</span>
              <span class="history-result" :class="{ 'is-win': record.reward_id }">
                {{ record.reward_id ? record.reward_name : '未中奖' }}
              </span>
            </div>
          </div>
          <div v-else class="empty-state">暂无抽奖记录</div>
        </div>
      </section>
    </div>

    <!-- 结果弹窗 -->
    <el-dialog
      v-model="showResultDialog"
      :show-close="false"
      width="90%"
      style="max-width: 360px;"
      align-center
      destroy-on-close
    >
      <div class="result-popup">
        <div class="result-icon-wrap">
          <span class="result-big-icon">{{ drawResult.isWin ? '🎉' : '😅' }}</span>
        </div>
        <h3 class="result-title">{{ drawResult.isWin ? '恭喜中奖！' : '没有中奖' }}</h3>
        
        <div class="prize-display" v-if="drawResult.isWin && drawResult.reward">
          <div class="prize-icon">{{ drawResult.reward.icon || '🎁' }}</div>
          <div class="prize-name">{{ drawResult.reward.name }}</div>
          <div class="prize-desc" v-if="drawResult.reward.description">
            {{ drawResult.reward.description }}
          </div>
        </div>
        
        <p class="result-tip" v-if="!drawResult.isWin">再接再厉，下次一定中！</p>

        <div class="result-actions">
          <el-button 
            v-if="canDraw && remainingParticipations > 0" 
            type="primary" 
            round 
            size="large"
            class="btn-continue"
            @click="continueDraw"
          >
            再抽一次
          </el-button>
          <el-button round size="large" class="btn-close" @click="closeResultDialog">
            关闭
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const route = useRoute()
const activityId = computed(() => route.params.id)

// 数据状态
const activity = reactive({ activity: null, rewards: [] })
const userInfo = reactive({ game_id: '' })
const participationHistory = ref([])
const hasJoined = ref(false)
const isLoading = ref(false)
const isDrawing = ref(false)
const showResultDialog = ref(false)
const drawResult = reactive({ isWin: false, reward: null })

// 转盘动画
const wheelRotation = ref(0)
const lightState = ref(0)

// 时间
const now = ref(new Date())
let timerInterval = null
let lightInterval = null

// --- 计算属性 ---

const requiresLogin = computed(() => activity.activity?.game_id_required)
const isUnlimited = computed(() => !activity.activity?.max_participations)

const remainingParticipations = computed(() => {
  if (!activity.activity || isUnlimited.value) return 999
  return Math.max(0, activity.activity.max_participations - participationHistory.value.length)
})

// 用于显示的奖品列表（过滤掉特殊的"谢谢参与"项）
const displayRewards = computed(() => {
  return activity.rewards.filter(r => r.id !== 'thanks' && r.name !== '谢谢参与')
})

// 是否需要滚动（超过3个奖品时滚动）
const shouldScroll = computed(() => {
  return displayRewards.value.length > 3
})

// 滚动动画样式
const scrollStyle = computed(() => {
  if (!shouldScroll.value) return {}
  
  const itemCount = displayRewards.value.length
  // 每个奖品卡片宽度约 100px + 间距 10px
  const itemWidth = 110
  const totalWidth = itemCount * itemWidth
  // 动画时长：根据奖品数量调整，每个奖品约 2 秒
  const duration = itemCount * 2
  
  return {
    '--scroll-distance': `-${totalWidth}px`,
    '--scroll-duration': `${duration}s`
  }
})

const activityStatus = computed(() => {
  if (!activity.activity) return { type: 'loading', text: '加载中...' }
  if (!activity.activity.is_active) return { type: 'ended', text: '已停止' }
  
  const startTime = activity.activity.start_time ? new Date(activity.activity.start_time) : null
  const endTime = activity.activity.end_time ? new Date(activity.activity.end_time) : null
  
  if (startTime && now.value < startTime) return { type: 'pending', text: '未开始' }
  if (endTime && now.value > endTime) return { type: 'ended', text: '已结束' }
  return { type: 'active', text: '进行中' }
})

const timeRemaining = computed(() => {
  if (!activity.activity?.end_time) return 0
  return Math.max(0, new Date(activity.activity.end_time) - now.value)
})

const canDraw = computed(() => {
  return activityStatus.value.type === 'active' && 
         (isUnlimited.value || remainingParticipations.value > 0) &&
         !isDrawing.value
})

const wheelRotateStyle = computed(() => ({
  transform: `rotate(${wheelRotation.value}deg)`,
  transition: isDrawing.value 
    ? `transform ${getRotateDuration()}s cubic-bezier(0.2, 0, 0.05, 1)` 
    : 'none'
}))

// 圆锥渐变背景
const wheelBgStyle = computed(() => {
  const count = activity.rewards.length
  if (count === 0) return {}
  
  const colors = ['#fef3c7', '#fde68a', '#fcd34d', '#fbbf24', '#f59e0b', '#d97706', '#b45309', '#92400e']
  const altColors = ['#fff7ed', '#ffedd5', '#fed7aa', '#fdba74', '#fb923c', '#f97316', '#ea580c', '#c2410c']
  
  let gradientParts = []
  const degreePerSegment = 360 / count
  
  for (let i = 0; i < count; i++) {
    const colorSet = i % 2 === 0 ? colors : altColors
    const color = colorSet[i % colorSet.length]
    const startDeg = i * degreePerSegment
    const endDeg = (i + 1) * degreePerSegment
    gradientParts.push(`${color} ${startDeg}deg ${endDeg}deg`)
  }
  
  return {
    background: `conic-gradient(from 0deg, ${gradientParts.join(', ')})`
  }
})

// --- 方法 ---

function getRotateDuration() {
  return activity.activity?.config?.rotate_duration || 4
}

function getLineStyle(index) {
  const count = activity.rewards.length
  const degree = 360 / count
  return {
    transform: `rotate(${index * degree}deg)`
  }
}

function getItemStyle(index) {
  const count = activity.rewards.length
  const degree = 360 / count
  const rotation = index * degree + degree / 2
  return {
    transform: `rotate(${rotation}deg)`
  }
}

async function loadActivity() {
  try {
    const response = await fetch(`/api/activity/${activityId.value}/public-info`)
    const result = await response.json()
    
    if (result.success) {
      activity.activity = result.data.activity
      activity.rewards = result.data.rewards || []
      
      // 解析配置
      if (activity.activity?.config && typeof activity.activity.config === 'string') {
        try {
          activity.activity.config = JSON.parse(activity.activity.config)
        } catch (e) {
          activity.activity.config = {}
        }
      }
      
      // 确保至少有一个扇区
      if (!activity.rewards || activity.rewards.length === 0) {
        activity.rewards = [{
          id: 'thanks',
          name: '谢谢参与',
          icon: '🙏',
          probability: 100,
          remaining_quantity: -1,
          total_quantity: -1,
          type: 'special',
          value: '{}'
        }]
      } else {
        // 检查是否已包含"谢谢参与"扇区
        const hasThanksReward = activity.rewards.some(reward => 
          reward.name === '谢谢参与' || reward.name === '未中奖'
        )
        if (!hasThanksReward) {
          activity.rewards.push({
            id: 'thanks',
            name: '谢谢参与',
            icon: '🙏',
            probability: 0,
            remaining_quantity: -1,
            total_quantity: -1,
            type: 'special',
            value: '{}'
          })
        }
      }
    } else {
      ElMessage.error(result.message || '加载活动失败')
    }
  } catch (error) {
    console.error('加载活动失败:', error)
    ElMessage.error('网络请求失败，请检查网络连接')
  }
}

async function startParticipate() {
  if (!userInfo.game_id.trim()) {
    ElMessage.warning('请输入游戏ID')
    return
  }
  
  isLoading.value = true
  try {
    await loadHistory()
    hasJoined.value = true
  } catch (error) {
    ElMessage.error('加载用户数据失败')
  } finally {
    isLoading.value = false
  }
}

async function loadHistory() {
  try {
    const response = await fetch(`/api/activity/${activityId.value}/history`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: userInfo.game_id })
    })
    const result = await response.json()
    
    if (result.success) {
      participationHistory.value = result.data || []
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
  }
}

async function handleDrawClick() {
  if (!canDraw.value) {
    if (isDrawing.value) {
      return
    }
    if (!isUnlimited.value && remainingParticipations.value <= 0) {
      ElMessage.warning('您的抽奖次数已用完')
      return
    }
    if (activityStatus.value.type !== 'active') {
      ElMessage.warning('活动' + activityStatus.value.text)
      return
    }
    return
  }

  isDrawing.value = true

  try {
    const response = await fetch(`/api/activity/${activityId.value}/participate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: userInfo.game_id })
    })
    
    if (!response.ok) {
      console.error('抽奖请求失败:', response)
      const errorMsg = `抽奖失败: ${response.status} ${response.statusText}`
      ElMessage.error(errorMsg)
      isDrawing.value = false
      return
    }
    
    const result = await response.json()
    
    if (!result.success) {
      const errorMsg = result.message || result.msg || result.error || '抽奖失败，请重试'
      console.error('抽奖结果失败:', result)
      ElMessage.error(errorMsg)
      isDrawing.value = false
      return
    }

    const reward = result.data?.reward || null
    const totalSegments = activity.rewards.length
    let targetIndex = 0

    if (reward && reward.id) {
      targetIndex = activity.rewards.findIndex(r => r.id === reward.id)
      if (targetIndex === -1) targetIndex = 0
    } else {
      const thanksIndex = activity.rewards.findIndex(r => 
        r.name === '谢谢参与' || r.name === '未中奖'
      )
      if (thanksIndex !== -1) {
        targetIndex = thanksIndex
      } else {
        targetIndex = Math.floor(Math.random() * totalSegments)
      }
    }

    const perAngle = 360 / totalSegments
    const targetAngle = targetIndex * perAngle + perAngle / 2
    const randomOffset = (Math.random() - 0.5) * (perAngle * 0.8)
    const spins = 360 * 5
    const finalAngle = spins + (360 - targetAngle) + randomOffset
    const baseRotation = Math.ceil(wheelRotation.value / 360) * 360
    wheelRotation.value = baseRotation + finalAngle

    const duration = getRotateDuration() * 1000
    
    setTimeout(() => {
      isDrawing.value = false
      drawResult.isWin = !!reward
      drawResult.reward = reward
      showResultDialog.value = true
      
      if (drawResult.isWin) {
        fireConfetti()
      }
      
      loadHistory()
      loadActivity()
    }, duration + 300)

  } catch (error) {
    console.error('抽奖请求失败:', error)
    ElMessage.error('网络请求失败，请检查网络连接后重试')
    isDrawing.value = false
  }
}

function continueDraw() {
  showResultDialog.value = false
}

function closeResultDialog() {
  showResultDialog.value = false
}

function formatTimeRemaining(ms) {
  const hours = Math.floor(ms / 3600000)
  const minutes = Math.floor((ms % 3600000) / 60000)
  const seconds = Math.floor((ms % 60000) / 1000)
  
  if (hours > 0) {
    return `${hours}时${minutes}分${seconds}秒`
  } else if (minutes > 0) {
    return `${minutes}分${seconds}秒`
  } else {
    return `${seconds}秒`
  }
}

function formatTimeShort(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const month = d.getMonth() + 1
  const day = d.getDate()
  const hour = d.getHours().toString().padStart(2, '0')
  const minute = d.getMinutes().toString().padStart(2, '0')
  return `${month}/${day} ${hour}:${minute}`
}

function fireConfetti() {
  const colors = ['#ff6b6b', '#feca57', '#48dbfb', '#ff9ff3', '#54a0ff', '#5f27cd', '#00d2d3', '#1dd1a1']
  const container = document.querySelector('.lucky-draw-page')
  if (!container) return
  
  for (let i = 0; i < 80; i++) {
    const confetti = document.createElement('div')
    confetti.className = 'confetti-piece'
    confetti.style.cssText = `
      position: fixed;
      left: 50%;
      top: 50%;
      width: ${6 + Math.random() * 6}px;
      height: ${6 + Math.random() * 6}px;
      background: ${colors[Math.floor(Math.random() * colors.length)]};
      z-index: 9999;
      pointer-events: none;
      border-radius: ${Math.random() > 0.5 ? '50%' : '0'};
    `
    container.appendChild(confetti)
    
    const angle = Math.random() * Math.PI * 2
    const velocity = 150 + Math.random() * 250
    const x = Math.cos(angle) * velocity
    const y = Math.sin(angle) * velocity - 100
    const rotation = Math.random() * 720
    
    confetti.animate([
      { transform: 'translate(-50%, -50%) rotate(0deg)', opacity: 1 },
      { transform: `translate(calc(-50% + ${x}px), calc(-50% + ${y}px)) rotate(${rotation}deg)`, opacity: 0 }
    ], {
      duration: 1200 + Math.random() * 800,
      easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
    }).onfinish = () => confetti.remove()
  }
}

onMounted(() => {
  loadActivity()
  
  timerInterval = setInterval(() => {
    now.value = new Date()
  }, 1000)
  
  lightInterval = setInterval(() => {
    lightState.value = lightState.value === 0 ? 1 : 0
  }, 500)
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
  if (lightInterval) clearInterval(lightInterval)
})
</script>

<style scoped>
/* ========== 基础样式 ========== */
.lucky-draw-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  color: #fff;
  position: relative;
  overflow-x: hidden;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
  padding-bottom: 40px;
}

/* 背景动画 */
.background-shapes {
  position: fixed;
  inset: 0;
  z-index: 0;
  overflow: hidden;
}

.shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.4;
}

.shape-1 {
  top: -20%;
  left: -10%;
  width: 60vw;
  height: 60vw;
  background: #e94560;
  animation: floatShape 15s ease-in-out infinite;
}

.shape-2 {
  bottom: -20%;
  right: -10%;
  width: 50vw;
  height: 50vw;
  background: #0f3460;
  animation: floatShape 12s ease-in-out infinite reverse;
}

@keyframes floatShape {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(30px, -30px) scale(1.1); }
}

/* 内容容器 */
.content-container {
  position: relative;
  z-index: 1;
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 玻璃卡片 */
.glass-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 20px;
}

/* ========== 头部 ========== */
.header-card {
  text-align: center;
  border-top: 3px solid #e94560;
}

.main-title {
  margin: 0 0 8px;
  font-size: 1.8rem;
  font-weight: 700;
  background: linear-gradient(90deg, #fff, #f8b739);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sub-title {
  margin: 0 0 16px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.status-bar {
  display: inline-flex;
  align-items: center;
  gap: 16px;
  background: rgba(0, 0, 0, 0.3);
  padding: 8px 16px;
  border-radius: 30px;
  font-size: 0.85rem;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot.active {
  background: #10b981;
  box-shadow: 0 0 8px #10b981;
  animation: pulse 1.5s infinite;
}

.dot.pending {
  background: #f59e0b;
}

.dot.ended {
  background: #ef4444;
}

.dot.loading {
  background: #6b7280;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* ========== 登录区域 ========== */
.login-card {
  text-align: center;
}

.login-icon {
  font-size: 3.5rem;
  margin-bottom: 12px;
}

.login-card h2 {
  margin: 0 0 20px;
  font-size: 1.3rem;
  font-weight: 600;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.custom-input :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  box-shadow: none;
}

.custom-input :deep(.el-input__inner) {
  color: #fff;
  height: 48px;
}

.custom-input :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.5);
}

.start-btn {
  height: 48px;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #e94560, #f8b739);
  border: none;
}

/* ========== 用户信息条 ========== */
.user-bar {
  padding: 12px 16px;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #e94560, #f8b739);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.2rem;
}

.info {
  flex: 1;
}

.user-id {
  font-weight: 600;
  font-size: 0.95rem;
}

.chances {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 2px;
}

.highlight {
  color: #f8b739;
  font-weight: 700;
}

/* ========== 转盘区域 ========== */
.wheel-wrapper {
  display: flex;
  justify-content: center;
  padding: 10px 0;
}

.wheel-outer-ring {
  position: relative;
  width: 320px;
  height: 320px;
  background: linear-gradient(145deg, #2d2d44, #1a1a2e);
  border-radius: 50%;
  padding: 15px;
  box-shadow: 
    0 10px 40px rgba(0, 0, 0, 0.5),
    inset 0 2px 4px rgba(255, 255, 255, 0.1);
}

/* 灯泡容器 */
.lights-container {
  position: absolute;
  inset: 0;
  border-radius: 50%;
}

.light-bulb {
  position: absolute;
  width: 10px;
  height: 10px;
  background: #666;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  box-shadow: 0 0 3px rgba(0, 0, 0, 0.5);
  transition: all 0.3s ease;
}

/* 使用 nth-child 精确定位每个灯泡 */
.light-bulb:nth-child(1)  { transform: translate(-50%, -50%) rotate(0deg)    translateY(-152px); }
.light-bulb:nth-child(2)  { transform: translate(-50%, -50%) rotate(22.5deg) translateY(-152px); }
.light-bulb:nth-child(3)  { transform: translate(-50%, -50%) rotate(45deg)   translateY(-152px); }
.light-bulb:nth-child(4)  { transform: translate(-50%, -50%) rotate(67.5deg) translateY(-152px); }
.light-bulb:nth-child(5)  { transform: translate(-50%, -50%) rotate(90deg)   translateY(-152px); }
.light-bulb:nth-child(6)  { transform: translate(-50%, -50%) rotate(112.5deg) translateY(-152px); }
.light-bulb:nth-child(7)  { transform: translate(-50%, -50%) rotate(135deg)  translateY(-152px); }
.light-bulb:nth-child(8)  { transform: translate(-50%, -50%) rotate(157.5deg) translateY(-152px); }
.light-bulb:nth-child(9)  { transform: translate(-50%, -50%) rotate(180deg)  translateY(-152px); }
.light-bulb:nth-child(10) { transform: translate(-50%, -50%) rotate(202.5deg) translateY(-152px); }
.light-bulb:nth-child(11) { transform: translate(-50%, -50%) rotate(225deg)  translateY(-152px); }
.light-bulb:nth-child(12) { transform: translate(-50%, -50%) rotate(247.5deg) translateY(-152px); }
.light-bulb:nth-child(13) { transform: translate(-50%, -50%) rotate(270deg)  translateY(-152px); }
.light-bulb:nth-child(14) { transform: translate(-50%, -50%) rotate(292.5deg) translateY(-152px); }
.light-bulb:nth-child(15) { transform: translate(-50%, -50%) rotate(315deg)  translateY(-152px); }
.light-bulb:nth-child(16) { transform: translate(-50%, -50%) rotate(337.5deg) translateY(-152px); }

/* 灯泡亮起状态 */
.light-bulb.light-on {
  background: #fff;
  box-shadow: 0 0 8px 2px #fff, 0 0 15px 4px #f8b739;
}

/* 交替颜色 */
.light-bulb:nth-child(odd).light-on {
  background: #f8b739;
  box-shadow: 0 0 8px 2px #f8b739, 0 0 15px 4px #f8b739;
}

.light-bulb:nth-child(even).light-on {
  background: #e94560;
  box-shadow: 0 0 8px 2px #e94560, 0 0 15px 4px #e94560;
}

/* 内部转盘 */
.wheel-inner {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.3);
}

/* 旋转层 */
.wheel-rotate-panel {
  position: absolute;
  inset: 0;
  border-radius: 50%;
}

.wheel-bg {
  position: absolute;
  inset: 0;
  border-radius: 50%;
}

/* 分割线 */
.wheel-line {
  position: absolute;
  top: 0;
  left: 50%;
  width: 2px;
  height: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform-origin: bottom center;
  margin-left: -1px;
}

/* 奖品项 */
.wheel-item {
  position: absolute;
  top: 0;
  left: 50%;
  width: 0;
  height: 50%;
  transform-origin: bottom center;
  display: flex;
  justify-content: center;
}

.item-content {
  margin-top: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 70px;
  text-align: center;
}

.wheel-icon {
  font-size: 1.8rem;
  margin-bottom: 4px;
  filter: drop-shadow(0 2px 3px rgba(0, 0, 0, 0.3));
}

.wheel-text {
  font-size: 0.7rem;
  font-weight: 700;
  color: #1a1a2e;
  line-height: 1.2;
  max-width: 45px; /* 大约8个中文字符宽度 */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap; /* 单行截断 */
  text-shadow: 0 1px 1px rgba(255, 255, 255, 0.5);
  margin-bottom: 5px; /* 调整与图标的间距 */
}

/* 指针 */
.wheel-pointer {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
  cursor: pointer;
}

.pointer-arrow {
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 12px solid transparent;
  border-right: 12px solid transparent;
  border-bottom: 30px solid #fff;
  filter: drop-shadow(0 -2px 4px rgba(0, 0, 0, 0.3));
}

.pointer-center {
  width: 70px;
  height: 70px;
  background: linear-gradient(145deg, #e94560, #c73e54);
  border-radius: 50%;
  border: 4px solid #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
  transition: transform 0.2s, box-shadow 0.2s;
}

.pointer-center:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(233, 69, 96, 0.5);
}

.pointer-center:active {
  transform: scale(0.95);
}

.pointer-text {
  font-size: 1.4rem;
  font-weight: 800;
  color: #fff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.wheel-pointer.disabled .pointer-center {
  background: linear-gradient(145deg, #6b7280, #4b5563);
  cursor: not-allowed;
}

.wheel-pointer.drawing .pointer-center {
  animation: drawingPulse 0.5s infinite alternate;
}

@keyframes drawingPulse {
  from { transform: scale(1); }
  to { transform: scale(0.95); }
}

/* ========== 信息区域 ========== */
.info-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-header {
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.card-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

/* ========== 奖品滚动区域 ========== */
.rewards-section {
  overflow: hidden;
}

.rewards-scroll-container {
  overflow: hidden;
  position: relative;
}

/* 不滚动时居中显示 */
.rewards-scroll-container.no-scroll {
  display: flex;
  justify-content: center;
}

.rewards-scroll-container.no-scroll .rewards-track {
  display: flex;
  justify-content: center;
  gap: 10px;
}

/* 滚动轨道 */
.rewards-track {
  display: flex;
  gap: 10px;
  width: max-content;
}

/* 滚动动画 */
.rewards-track.scrolling {
  animation: scrollLeft var(--scroll-duration, 10s) linear infinite;
}

@keyframes scrollLeft {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(var(--scroll-distance, -500px));
  }
}

/* 鼠标悬停暂停滚动 */
.rewards-scroll-container:hover .rewards-track.scrolling {
  animation-play-state: paused;
}

/* 奖品卡片 */
.reward-card {
  flex-shrink: 0;
  width: 100px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 12px 8px;
  text-align: center;
  transition: all 0.3s;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.reward-card:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
  border-color: rgba(248, 183, 57, 0.5);
}

.reward-card.sold-out {
  opacity: 0.4;
  filter: grayscale(1);
}

.reward-card .reward-icon {
  font-size: 1.8rem;
  display: block;
  margin-bottom: 6px;
}

.reward-card .reward-name {
  font-size: 0.75rem;
  font-weight: 600;
  display: block;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.reward-card .reward-stock {
  font-size: 0.65rem;
  color: rgba(255, 255, 255, 0.5);
  display: block;
}

/* 历史记录 */
.history-list {
  max-height: 180px;
  overflow-y: auto;
}

.history-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  font-size: 0.85rem;
}

.history-row:last-child {
  border-bottom: none;
}

.history-time {
  color: rgba(255, 255, 255, 0.5);
}

.history-result {
  color: rgba(255, 255, 255, 0.7);
}

.history-result.is-win {
  color: #f8b739;
  font-weight: 600;
}

.empty-state {
  text-align: center;
  color: rgba(255, 255, 255, 0.4);
  padding: 20px;
  font-size: 0.9rem;
}

/* ========== 结果弹窗 ========== */
:deep(.el-dialog) {
  background: linear-gradient(145deg, #2d2d44, #1a1a2e) !important;
  border-radius: 24px !important;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.el-dialog__header) {
  display: none;
}

:deep(.el-dialog__body) {
  padding: 30px 20px !important;
}

.result-popup {
  text-align: center;
  color: #fff;
}

.result-icon-wrap {
  margin-bottom: 16px;
}

.result-big-icon {
  font-size: 4rem;
  display: inline-block;
  animation: bounceIn 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes bounceIn {
  0% { transform: scale(0); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.result-title {
  margin: 0 0 20px;
  font-size: 1.5rem;
  font-weight: 700;
}

.prize-display {
  background: rgba(248, 183, 57, 0.15);
  border: 1px solid rgba(248, 183, 57, 0.3);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 16px;
}

.prize-icon {
  font-size: 3rem;
  margin-bottom: 10px;
}

.prize-name {
  font-size: 1.2rem;
  font-weight: 700;
  color: #f8b739;
  margin-bottom: 8px;
}

.prize-desc {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
}

.result-tip {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
  margin-bottom: 20px;
}

.result-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.btn-continue {
  height: 48px;
  font-size: 1rem;
  font-weight: 600;
  background: linear-gradient(135deg, #e94560, #f8b739);
  border: none;
}

.btn-close {
  height: 44px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
}

/* ========== 响应式 ========== */
@media (max-width: 380px) {
  .wheel-outer-ring {
    width: 280px;
    height: 280px;
  }
  
  .light-bulb:nth-child(1)  { transform: translate(-50%, -50%) rotate(0deg)    translateY(-132px); }
  .light-bulb:nth-child(2)  { transform: translate(-50%, -50%) rotate(22.5deg) translateY(-132px); }
  .light-bulb:nth-child(3)  { transform: translate(-50%, -50%) rotate(45deg)   translateY(-132px); }
  .light-bulb:nth-child(4)  { transform: translate(-50%, -50%) rotate(67.5deg) translateY(-132px); }
  .light-bulb:nth-child(5)  { transform: translate(-50%, -50%) rotate(90deg)   translateY(-132px); }
  .light-bulb:nth-child(6)  { transform: translate(-50%, -50%) rotate(112.5deg) translateY(-132px); }
  .light-bulb:nth-child(7)  { transform: translate(-50%, -50%) rotate(135deg)  translateY(-132px); }
  .light-bulb:nth-child(8)  { transform: translate(-50%, -50%) rotate(157.5deg) translateY(-132px); }
  .light-bulb:nth-child(9)  { transform: translate(-50%, -50%) rotate(180deg)  translateY(-132px); }
  .light-bulb:nth-child(10) { transform: translate(-50%, -50%) rotate(202.5deg) translateY(-132px); }
  .light-bulb:nth-child(11) { transform: translate(-50%, -50%) rotate(225deg)  translateY(-132px); }
  .light-bulb:nth-child(12) { transform: translate(-50%, -50%) rotate(247.5deg) translateY(-132px); }
  .light-bulb:nth-child(13) { transform: translate(-50%, -50%) rotate(270deg)  translateY(-132px); }
  .light-bulb:nth-child(14) { transform: translate(-50%, -50%) rotate(292.5deg) translateY(-132px); }
  .light-bulb:nth-child(15) { transform: translate(-50%, -50%) rotate(315deg)  translateY(-132px); }
  .light-bulb:nth-child(16) { transform: translate(-50%, -50%) rotate(337.5deg) translateY(-132px); }
  
  .main-title {
    font-size: 1.5rem;
  }
  
  .reward-card {
    width: 90px;
  }
}
</style>