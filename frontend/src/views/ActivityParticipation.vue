<template>
  <div class="activity-participation" :class="{ 'mobile-mode': isMobile }">
    <!-- 活动标题区域 -->
    <div class="activity-header">
      <div class="activity-banner" v-if="activity.activity">
        <h1 class="activity-title">{{ activity.activity.name }}</h1>
        <p class="activity-description" v-if="activity.activity.description">
          {{ activity.activity.description }}
        </p>
        <div class="activity-status">
          <el-tag :type="activity.activity.is_active ? 'success' : 'danger'">
            {{ activity.activity.is_active ? '进行中' : '已结束' }}
          </el-tag>
          <el-tag v-if="timeRemaining > 0" type="warning">
            剩余时间: {{ formatTimeRemaining(timeRemaining) }}
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 游戏ID输入区域 -->
    <div class="game-id-section" v-if="activity.activity && activity.activity.game_id_required && !hasJoined">
      <div class="game-id-input">
        <h3>请输入您的游戏ID</h3>
        <el-input 
          v-model="userInfo.game_id" 
          placeholder="请输入游戏ID"
          @keyup.enter="startParticipate"
          size="large"
          style="width: 300px; margin-right: 10px;"
        />
        <el-button 
          type="primary" 
          size="large" 
          @click="startParticipate"
          :disabled="!userInfo.game_id.trim()"
        >
          开始参与
        </el-button>
      </div>
    </div>

    <!-- 参与信息显示 -->
    <div class="participation-info" v-if="hasJoined && activity.activity">
      <div class="info-card">
        <div class="user-info">
          <div class="user-icon">👤</div>
          <div class="user-details">
            <div class="game-id">游戏ID: {{ userInfo.game_id }}</div>
            <div class="participation-count" v-if="activity.activity.max_participations">
              剩余参与次数: {{ remainingParticipations }}
            </div>
            <div class="participation-count" v-else>
              无限次参与
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 转盘抽奖区域 -->
    <div class="roulette-section" v-if="canParticipate">
      <div class="roulette-container">
        <!-- 转盘 -->
        <div class="roulette-wheel" :style="wheelStyle">
          <div class="wheel-center">
            <div class="wheel-pointer" :style="pointerStyle"></div>
          </div>
        </div>
        
        <!-- 抽奖按钮 -->
        <div class="draw-button-container">
          <el-button 
            type="primary" 
            size="large" 
            @click="startDraw"
            :loading="isDrawing"
            :disabled="!canDraw || isDrawing"
            class="draw-button"
          >
            {{ isDrawing ? '抽奖中...' : '开始抽奖' }}
          </el-button>
        </div>
      </div>
    </div>

    <!-- 奖品展示 -->
    <div class="rewards-display" v-if="activity.rewards && activity.rewards.length > 0">
      <h3>奖品一览</h3>
      <div class="rewards-grid">
        <div 
          v-for="reward in activity.rewards" 
          :key="reward.id"
          class="reward-item"
          :class="{ 'available': reward.remaining_quantity > 0, 'empty': reward.remaining_quantity <= 0 }"
        >
          <div class="reward-icon">{{ reward.icon || '🎁' }}</div>
          <div class="reward-name">{{ reward.name }}</div>
          <div class="reward-info">
            <div class="probability">概率: {{ reward.probability }}%</div>
            <div class="quantity">剩余: {{ reward.remaining_quantity }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 抽奖结果弹窗 -->
    <el-dialog 
      v-model="showResultDialog" 
      :title="drawResult.isWin ? '恭喜中奖！' : '很遗憾'"
      width="400px"
      :show-close="false"
      :close-on-click-modal="false"
    >
      <div class="draw-result">
        <div class="result-icon">
          {{ drawResult.isWin ? '🎉' : '😔' }}
        </div>
        <div class="result-message">
          <p v-if="drawResult.isWin" class="win-message">
            恭喜您获得：{{ drawResult.reward?.name }}
          </p>
          <p v-else class="lose-message">
            很遗憾，这次没有中奖，再试试看吧！
          </p>
          <p v-if="drawResult.reward?.description" class="reward-desc">
            {{ drawResult.reward.description }}
          </p>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button 
            v-if="canDraw && remainingParticipations > 0" 
            type="primary" 
            @click="continueDraw"
          >
            继续抽奖
          </el-button>
          <el-button @click="closeResultDialog">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 抽奖记录 -->
    <div class="participation-history" v-if="participationHistory.length > 0">
      <h3>我的抽奖记录</h3>
      <div class="history-list">
        <div 
          v-for="record in participationHistory" 
          :key="record.id"
          class="history-item"
        >
          <div class="record-time">{{ formatTime(record.created_at) }}</div>
          <div class="record-result">
            <span v-if="record.reward_id" class="win-result">
              获得：{{ record.reward_name }}
            </span>
            <span v-else class="lose-result">未中奖</span>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'

const route = useRoute()

// 响应式数据
const activity = reactive({
  activity: null,
  rewards: [],
  statistics: null
})
const userInfo = reactive({
  game_id: ''
})
const participationHistory = ref([])
const isDrawing = ref(false)
const showResultDialog = ref(false)
const drawResult = reactive({
  isWin: false,
  reward: null
})
const hasJoined = ref(false)
const now = ref(new Date())

// 动画相关
const currentRotation = ref(0)
const targetRotation = ref(0)
const isAnimating = ref(false)

// 计算属性
const activityId = computed(() => route.params.id)

const canParticipate = computed(() => {
  if (!activity.activity) return false
  return activity.activity.is_active && isInTimeRange()
})

const isInTimeRange = () => {
  if (!activity.activity) return false
  if (!activity.activity.start_time && !activity.activity.end_time) return true
  
  // 使用响应式的 now.value
  const currentTime = now.value
  
  if (activity.activity.start_time) {
    const startTime = new Date(activity.activity.start_time)
    if (currentTime < startTime) return false
  }
  
  if (activity.activity.end_time) {
    const endTime = new Date(activity.activity.end_time)
    if (currentTime > endTime) return false
  }
  
  return true
}

const canDraw = computed(() => {
  if (!canParticipate.value) return false
  // 仅当需要游戏ID时才检查是否已加入
  if (activity.activity.game_id_required && !hasJoined.value) return false
  if (activity.activity.max_participations && remainingParticipations.value <= 0) return false
  
  return true
})

const remainingParticipations = computed(() => {
  if (!activity.activity) return 0
  if (!activity.activity.max_participations) return Infinity
  // 使用本地历史记录计算已参与次数
  return Math.max(0, activity.activity.max_participations - participationHistory.value.length)
})

const timeRemaining = computed(() => {
  if (!activity.activity) return 0
  if (!activity.activity.end_time) return 0
  const endTime = new Date(activity.activity.end_time)
  return Math.max(0, endTime - now.value)
})

const wheelStyle = computed(() => ({
  transform: `rotate(${currentRotation.value}deg)`,
  width: `${activity.activity?.config?.size || 400}px`,
  height: `${activity.activity?.config?.size || 400}px`
}))

const pointerStyle = computed(() => ({
  animation: isAnimating.value ? `pointer-bounce ${activity.activity?.config?.rotate_duration || 3}s ease-out` : 'none'
}))

const isMobile = computed(() => window.innerWidth <= 768)

// 加载活动信息
async function loadActivity() {
  try {
    const response = await fetch(`/api/activity/${activityId.value}/public-info`)
    const result = await response.json()
    
    if (result.success) {
      activity.activity = result.data.activity
      activity.rewards = result.data.rewards || []
      activity.statistics = result.data.statistics
      // 解析配置
      if (activity.activity.config) {
        try {
          activity.activity.config = JSON.parse(activity.activity.config)
        } catch (e) {
          activity.activity.config = {}
        }
      }
    } else {
      ElMessage.error(result.message || '加载活动失败')
    }
  } catch (error) {
    console.error('加载活动失败:', error)
    ElMessage.error('网络请求失败')
  }
}

// 加载用户抽奖记录
async function loadParticipationHistory() {
  if (!userInfo.game_id) return
  
  try {
    const response = await fetch(`/api/activity/${activityId.value}/history`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: userInfo.game_id })
    })
    const result = await response.json()
    
    if (result.success) {
      participationHistory.value = result.data
    }
  } catch (error) {
    console.error('加载记录失败:', error)
  }
}

// 开始参与
async function startParticipate() {
  if (!userInfo.game_id.trim()) {
    ElMessage.warning('请输入游戏ID')
    return
  }
  
  await loadParticipationHistory()
  hasJoined.value = true
}

// 开始抽奖
async function startDraw() {
  if (!canDraw.value) return
  
  isDrawing.value = true
  
  try {
    // 1. 先请求后端进行抽奖
    const drawResponse = await performDrawRequest()
    
    if (!drawResponse.success) {
      ElMessage.error(drawResponse.message || '抽奖失败')
      isDrawing.value = false
      return
    }
    
    const reward = drawResponse.data.reward
    
    // 2. 计算转盘停止角度
    // 如果没有中奖(reward为null)，则随机停在未中奖区域或默认位置
    // 这里假设如果没有中奖，后端返回null，我们需要找一个"谢谢参与"的区域或者默认角度
    // 如果所有区域都是奖项，那么应该有一个"谢谢参与"的虚拟奖项或者特定ID
    
    // 我们需要根据后端返回的 reward.id 找到对应的奖项配置
    let targetReward = null
    if (reward) {
      targetReward = activity.rewards.find(r => r.id === reward.id)
    }
    
    // 如果没找到对应奖项（可能是未中奖），我们需要处理
    // 假设未中奖停在第一个"谢谢参与"类型的奖项，或者随机停在缝隙？
    // 简单起见，如果未中奖，我们随机停在一个"谢谢参与"的奖项上，如果没有，就随机停
    
    if (!targetReward) {
        // 尝试寻找"谢谢参与"或类似奖项
        // 这里假设没有中奖就是 null
        // 如果前端配置了"谢谢参与"作为奖项之一，我们需要知道是哪一个
        // 暂时逻辑：如果没有中奖，随机选一个没有库存或者概率为0的项，或者直接报错？
        // 更好的逻辑是：后端应该返回"谢谢参与"也是一个奖项（如果配置了的话）
        // 如果后端返回 null，说明没中奖。前端应该有一个默认的"未中奖"角度。
        
        // 现有逻辑中 getRewardAngle 处理了 null 的情况吗？
        // getRewardAngle(null) 返回 0
    }

    targetRotation.value = currentRotation.value + 360 * 5 + getRewardAngle(targetReward)
    
    // 3. 开始转盘动画
    await animateWheel()
    
    // 4. 动画结束后显示结果
    drawResult.isWin = !!reward
    drawResult.reward = reward
    showResultDialog.value = true
    
    // 刷新活动信息
    await loadActivity()
    await loadParticipationHistory()
    
  } catch (error) {
    console.error('抽奖失败:', error)
    ElMessage.error('抽奖失败，请重试')
    isDrawing.value = false
  }
}

// 请求抽奖API
async function performDrawRequest() {
  const response = await fetch(`/api/activity/${activityId.value}/participate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      game_id: userInfo.game_id
    })
  })
  return await response.json()
}

// 获取奖项对应的转盘角度
function getRewardAngle(reward) {
  if (!reward || !activity.rewards) return 0
  
  const index = activity.rewards.findIndex(r => r.id === reward.id)
  const anglePerSection = 360 / activity.rewards.length
  
  // 奖项角度 + 随机偏移
  const baseAngle = index * anglePerSection
  const randomOffset = (Math.random() - 0.5) * anglePerSection * 0.8
  
  return baseAngle + anglePerSection / 2 + randomOffset
}

// 转盘动画
function animateWheel() {
  return new Promise((resolve) => {
    isAnimating.value = true
    const duration = (activity.activity.config?.rotate_duration || 3) * 1000
    const startTime = Date.now()
    const startRotation = currentRotation.value
    const rotationDistance = targetRotation.value - startRotation
    
    function animate() {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      
      // 缓动函数
      const easeProgress = 1 - Math.pow(1 - progress, 3)
      
      currentRotation.value = startRotation + rotationDistance * easeProgress
      
      if (progress < 1) {
        requestAnimationFrame(animate)
      } else {
        isAnimating.value = false
        isDrawing.value = false
        resolve()
      }
    }
    
    requestAnimationFrame(animate)
  })
}

// 继续抽奖
function continueDraw() {
  showResultDialog.value = false
}

// 关闭结果弹窗
function closeResultDialog() {
  showResultDialog.value = false
}

// 格式化时间
function formatTime(timeStr) {
  return new Date(timeStr).toLocaleString('zh-CN')
}

// 格式化剩余时间
function formatTimeRemaining(ms) {
  const hours = Math.floor(ms / (1000 * 60 * 60))
  const minutes = Math.floor((ms % (1000 * 60 * 60)) / (1000 * 60))
  const seconds = Math.floor((ms % (1000 * 60)) / 1000)
  
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
}

// 初始化
onMounted(async () => {
  await loadActivity()
  
  // 定时更新剩余时间
  setInterval(() => {
    now.value = new Date()
  }, 1000)
})
</script>

<style scoped>
.activity-participation {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.mobile-mode {
  padding: 10px;
}

.activity-header {
  text-align: center;
  margin-bottom: 30px;
  color: white;
}

.activity-banner {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 30px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.activity-title {
  font-size: 2.5rem;
  margin: 0 0 15px 0;
  font-weight: bold;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.activity-description {
  font-size: 1.2rem;
  margin: 0 0 20px 0;
  opacity: 0.9;
}

.activity-status {
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
}

.game-id-section {
  text-align: center;
  margin-bottom: 30px;
}

.game-id-input {
  background: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  display: inline-flex;
  align-items: center;
  gap: 15px;
}

.game-id-input h3 {
  margin: 0;
  color: #333;
  width: 100%;
  margin-bottom: 15px;
}

.participation-info {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.info-card {
  background: white;
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  min-width: 300px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-icon {
  font-size: 2rem;
}

.user-details {
  flex: 1;
}

.game-id {
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.participation-count {
  color: #666;
  font-size: 14px;
}

.roulette-section {
  display: flex;
  justify-content: center;
  margin-bottom: 50px;
}

.roulette-container {
  text-align: center;
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
}

.roulette-wheel {
  position: relative;
  margin: 0 auto 30px;
  border-radius: 50%;
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57);
  background-size: 400% 400%;
  animation: gradient-shift 3s ease infinite;
  border: 5px solid white;
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.3);
  transition: transform 3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.wheel-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 60px;
  background: white;
  border-radius: 50%;
  border: 3px solid #333;
  z-index: 10;
}

.wheel-pointer {
  position: absolute;
  top: -15px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 15px solid transparent;
  border-right: 15px solid transparent;
  border-top: 25px solid #333;
  border-bottom: 0;
}

.draw-button-container {
  margin-top: 20px;
}

.draw-button {
  padding: 15px 40px;
  font-size: 1.2rem;
  border-radius: 25px;
  box-shadow: 0 4px 15px rgba(64, 158, 255, 0.4);
}

.rewards-display {
  background: white;
  border-radius: 15px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.rewards-display h3 {
  margin: 0 0 20px 0;
  color: #333;
  text-align: center;
}

.rewards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
}

.reward-item {
  text-align: center;
  padding: 20px;
  border-radius: 10px;
  background: #f8f9fa;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.reward-item.available:hover {
  background: #e8f5e8;
  border-color: #28a745;
  transform: translateY(-2px);
}

.reward-item.empty {
  opacity: 0.5;
  background: #f5f5f5;
}

.reward-icon {
  font-size: 2rem;
  margin-bottom: 10px;
}

.reward-name {
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
}

.reward-info {
  font-size: 12px;
  color: #666;
}

.probability {
  margin-bottom: 5px;
}

.draw-result {
  text-align: center;
  padding: 20px;
}

.result-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  animation: bounce 0.5s ease infinite alternate;
}

.win-message {
  font-size: 1.2rem;
  color: #28a745;
  margin-bottom: 10px;
}

.lose-message {
  font-size: 1.1rem;
  color: #666;
  margin-bottom: 10px;
}

.reward-desc {
  color: #888;
  font-size: 14px;
}

.participation-history {
  background: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.participation-history h3 {
  margin: 0 0 20px 0;
  color: #333;
}

.history-list {
  max-height: 300px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.record-time {
  color: #666;
  font-size: 14px;
}

.record-result {
  font-weight: bold;
}

.win-result {
  color: #28a745;
}

.lose-result {
  color: #dc3545;
}

@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes bounce {
  0% { transform: translateY(0); }
  100% { transform: translateY(-10px); }
}

@keyframes pointer-bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateX(-50%) translateY(0); }
  40% { transform: translateX(-50%) translateY(-10px); }
  60% { transform: translateX(-50%) translateY(-5px); }
}

@media (max-width: 768px) {
  .activity-title {
    font-size: 1.8rem;
  }
  
  .activity-banner {
    padding: 20px;
  }
  
  .game-id-input {
    flex-direction: column;
    width: 100%;
    max-width: 300px;
  }
  
  .game-id-input .el-input {
    width: 100% !important;
  }
  
  .rewards-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
  
  .reward-item {
    padding: 15px;
  }
  
  .roulette-container {
    padding: 20px;
  }
  
  .history-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
}

@media (max-width: 480px) {
  .activity-title {
    font-size: 1.5rem;
  }
  
  .rewards-grid {
    grid-template-columns: 1fr;
  }
  
  .draw-button {
    padding: 12px 30px;
    font-size: 1rem;
  }
}
</style>