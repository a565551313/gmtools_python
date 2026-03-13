<template>
  <div class="gift-module">
    <!-- 顶部导航 -->
    <nav class="module-nav">
      <button 
        v-for="tab in tabs" 
        :key="tab.key"
        :class="['nav-item', { active: activeTab === tab.key }]"
        @click="activeTab = tab.key"
      >
        <span class="nav-icon">{{ tab.icon }}</span>
        <span class="nav-label">{{ tab.label }}</span>
      </button>
    </nav>

    <!-- 内容区域 -->
    <div class="module-body">
      <!-- ========== 物品赠送面板 ========== -->
      <template v-if="activeTab === 'item'">
        <div class="section-grid">
          <!-- 道具赠送 -->
          <div class="section-box">
            <div class="box-title">
              <i class="icon-dot blue"></i>
              道具赠送
            </div>
            <div class="box-content">
              <div class="input-group">
                <label>物品名称 <em>*</em></label>
                <el-select 
                  v-model="itemForm.name" 
                  placeholder="请选择物品" 
                  filterable 
                  style="width: 100%"
                  :loading="itemLoading"
                >
                  <el-option
                    v-for="item in availableItems"
                    :key="item.item_name"
                    :label="item.display_name"
                    :value="item.item_name"
                  >
                    <span style="float: left">{{ item.display_name }}</span>
                    <span style="float: right; color: #8492a6; font-size: 13px">{{ item.item_name }}</span>
                  </el-option>
                </el-select>
                <div class="limit-info" v-if="currentItemLimit" style="margin-top: 5px; font-size: 12px; color: #666;">
                  <span :style="{ color: currentItemLimit.remaining <= 0 ? '#f56c6c' : '#67c23a' }">
                    剩余配额: {{ currentItemLimit.remaining }}/{{ currentItemLimit.total_limit }} 
                  </span>
                  <span style="color: #909399; margin-left: 5px;">
                    (每{{ currentItemLimit.reset_period_hours }}小时重置)
                  </span>
                </div>
              </div>
              <div class="input-row">
                <div class="input-group">
                  <label>数量</label>
                  <el-input 
                    v-model="itemForm.amount" 
                    placeholder="1" 
                    type="number"
                    min="1"
                    :max="currentItemLimit?.remaining || 999"
                  />
                </div>
                <div class="input-group">
                  <label>参数</label>
                  <el-input v-model="itemForm.params" placeholder="可选" />
                </div>
              </div>
              <el-button 
                type="primary" 
                @click="giveItem" 
                class="submit-btn"
                :loading="submitLoading.item"
                :disabled="!canGiveItem"
              >
                {{ submitLoading.item ? '赠送中...' : '赠送道具' }}
              </el-button>
            </div>
          </div>

          <!-- 宝石赠送 -->
          <div class="section-box">
            <div class="box-title">
              <i class="icon-dot purple"></i>
              宝石赠送
            </div>
            <div class="box-content">
              <div class="input-group">
                <label>宝石类型 <em>*</em></label>
                <el-select v-model="gemForm.type" placeholder="选择宝石类型">
                  <el-option v-for="g in gemTypes" :key="g" :label="g" :value="g" />
                </el-select>
              </div>
              <div class="input-row">
                <div class="input-group">
                  <label>最低等级 <em>*</em></label>
                  <el-input 
                    v-model="gemForm.minLevel" 
                    placeholder="1" 
                    type="number"
                    min="1"
                    max="10"
                  />
                </div>
                <div class="input-group">
                  <label>最高等级</label>
                  <el-input 
                    v-model="gemForm.maxLevel" 
                    placeholder="可选" 
                    type="number"
                    min="1"
                    max="10"
                  />
                </div>
              </div>
              <el-button 
                type="success" 
                @click="giveGem" 
                class="submit-btn"
                :loading="submitLoading.gem"
                :disabled="!canGiveGem"
              >
                {{ submitLoading.gem ? '赠送中...' : '赠送宝石' }}
              </el-button>
            </div>
          </div>
        </div>

        <!-- 提示信息 -->
        <div class="tips-bar">
          <div class="tip-item">
            <span class="tip-icon">💡</span>
            <span>道具名称为必填项，数量默认为1</span>
          </div>
          <div class="tip-item">
            <span class="tip-icon">💎</span>
            <span>不填最高等级则只发放最低等级宝石</span>
          </div>
        </div>
      </template>

      <!-- ========== CDK管理面板 ========== -->
      <template v-if="activeTab === 'cdk'">
        <!-- 类型选择器 -->
        <div class="type-bar">
          <div class="type-selector">
            <label>充值类型</label>
            <el-select 
              v-model="cdkForm.selectedType" 
              placeholder="选择或输入类型"
              filterable
              allow-create
              class="type-select"
              :loading="typeLoading"
              @change="handleTypeChange"
            >
              <el-option v-for="t in rechargeTypes" :key="t" :label="t" :value="t" />
            </el-select>
          </div>
          <div class="type-actions">
            <el-button 
              @click="getRechargeTypes" 
              :icon="Refresh"
              :loading="typeLoading"
            >
              刷新
            </el-button>
            <el-button 
              type="primary" 
              @click="newRechargeType" 
              :icon="Plus"
              :loading="submitLoading.newType"
              :disabled="!cdkForm.selectedType"
            >
              新建
            </el-button>
            <el-button 
              type="danger" 
              @click="confirmDelRechargeType" 
              :icon="Delete"
              :loading="submitLoading.delType"
              :disabled="!cdkForm.selectedType || !rechargeTypes.includes(cdkForm.selectedType)"
            >
              删除
            </el-button>
          </div>
        </div>

        <!-- 生成控制 -->
        <div class="section-grid">
          <!-- 随机生成 -->
          <div class="section-box">
            <div class="box-title">
              <i class="icon-dot cyan"></i>
              随机生成
            </div>
            <div class="box-content">
              <div class="input-row">
                <div class="input-group">
                  <label>生成数量</label>
                  <el-input 
                    v-model="cdkForm.count" 
                    placeholder="10" 
                    type="number"
                    min="1"
                    max="100"
                  />
                </div>
                <div class="input-group">
                  <label>卡号位数</label>
                  <el-input 
                    v-model="cdkForm.digits" 
                    placeholder="12" 
                    type="number"
                    min="6"
                    max="32"
                  />
                </div>
              </div>
              <el-button 
                type="primary" 
                @click="generateCdk" 
                class="submit-btn"
                :loading="submitLoading.genCdk"
                :disabled="!cdkForm.selectedType"
              >
                {{ submitLoading.genCdk ? '生成中...' : '生成随机CDK' }}
              </el-button>
            </div>
          </div>

          <!-- 自定义生成 -->
          <div class="section-box">
            <div class="box-title">
              <i class="icon-dot amber"></i>
              自定义生成
            </div>
            <div class="box-content">
              <div class="input-group">
                <label>自定义内容 <em>*</em></label>
                <el-input 
                  v-model="cdkForm.custom" 
                  placeholder="输入自定义CDK内容"
                  maxlength="32"
                  show-word-limit
                />
              </div>
              <el-button 
                type="warning" 
                @click="generateCustomCdk" 
                class="submit-btn"
                :loading="submitLoading.genCustomCdk"
                :disabled="!cdkForm.selectedType || !cdkForm.custom"
              >
                {{ submitLoading.genCustomCdk ? '生成中...' : '生成自定义CDK' }}
              </el-button>
            </div>
          </div>
        </div>

        <!-- 卡号展示 -->
        <div class="card-display">
          <div class="display-header">
            <span class="display-title">卡号列表</span>
            <span v-if="cardList.length" class="display-count">{{ cardList.length }} 个</span>
            <div class="display-actions">
              <el-button 
                size="small" 
                @click="getRechargeCard" 
                :icon="Search"
                :loading="cardLoading"
                :disabled="!cdkForm.selectedType"
              >
                获取
              </el-button>
              <el-button 
                size="small" 
                @click="copyAllCards" 
                :icon="CopyDocument" 
                :disabled="!cardList.length"
              >
                复制全部
              </el-button>
              <el-button 
                size="small" 
                type="danger"
                @click="confirmClearCards" 
                :icon="Delete" 
                :disabled="!cardList.length"
              >
                清空
              </el-button>
            </div>
          </div>
          <div class="display-body" v-loading="cardLoading">
            <div v-if="cardList.length" class="card-list">
              <TransitionGroup name="card">
                <div 
                  v-for="(card, idx) in cardList" 
                  :key="card"
                  class="card-item"
                  :class="{ copied: copiedCard === card }"
                  @click="copyCard(card)"
                >
                  <span class="card-index">{{ idx + 1 }}</span>
                  <span class="card-code">{{ card }}</span>
                  <span class="card-copy">{{ copiedCard === card ? '已复制!' : '点击复制' }}</span>
                </div>
              </TransitionGroup>
            </div>
            <div v-else class="empty-state">
              <span class="empty-icon">📭</span>
              <span class="empty-text">暂无卡号，请先选择类型并点击获取</span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, inject, onMounted, computed, watch } from 'vue'
import request from '@/api/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Plus, Delete, Search, CopyDocument } from '@element-plus/icons-vue'

// ==================== 依赖注入 ====================
const playerId = inject('playerId')
const logToConsole = inject('logToConsole')

// ==================== 常量配置 ====================
const tabs = [
  { key: 'item', label: '物品赠送', icon: '🎁' },
  { key: 'cdk', label: 'CDK管理', icon: '🎫' }
]

const gemTypes = ['星辉石', '光芒石', '月亮石', '太阳石', '舍利子', '红玛瑙', '黑宝石', '神秘石']

// ==================== 响应式状态 ====================
const activeTab = ref('item')

// 表单数据
const itemForm = reactive({ 
  name: '', 
  amount: '1', 
  params: '' 
})

const gemForm = reactive({ 
  type: '', 
  minLevel: '', 
  maxLevel: '' 
})

const cdkForm = reactive({ 
  selectedType: '', 
  count: '10', 
  digits: '12', 
  custom: '' 
})

// 加载状态
const itemLoading = ref(false)
const typeLoading = ref(false)
const cardLoading = ref(false)

const submitLoading = reactive({
  item: false,
  gem: false,
  newType: false,
  delType: false,
  genCdk: false,
  genCustomCdk: false
})

// 数据状态
const availableItems = ref([])
const itemUsage = ref({})
const rechargeTypes = ref([])
const cardList = ref([])
const copiedCard = ref('')

// ==================== 计算属性 ====================
const currentItemLimit = computed(() => {
  if (!itemForm.name) return null
  return itemUsage.value[itemForm.name]
})

const canGiveItem = computed(() => {
  if (!playerId.value || !itemForm.name) return false
  if (currentItemLimit.value && currentItemLimit.value.remaining <= 0) return false
  return true
})

const canGiveGem = computed(() => {
  return !!(playerId.value && gemForm.type && gemForm.minLevel)
})

// ==================== 工具函数 ====================
function handleApiError(error, operation) {
  const msg = error.response?.data?.detail || error.message || `${operation}失败`
  const status = error.response?.status || 0
  logToConsole?.('ERROR', operation, status, { error: msg })
  ElMessage.error(msg)
  return msg
}

function handleApiSuccess(method, path, response, message) {
  logToConsole?.(method, path, 200, response)
  if (message) ElMessage.success(message)
}

function parseListFromContent(content) {
  const list = []
  const regex = /\[(\d+)\]="([^"]+)"/g
  let match
  while ((match = regex.exec(content)) !== null) {
    list.push(match[2])
  }
  return list
}

// ==================== 物品数据加载 ====================
async function loadItemData() {
  itemLoading.value = true
  try {
    const [itemsRes, usageRes] = await Promise.all([
      request.get('/api/items/available'),
      request.get('/api/items/my-usage')
    ])
    
    availableItems.value = itemsRes.data || []
    
    // 处理使用情况
    const usageMap = {}
    if (usageRes.data) {
      usageRes.data.forEach(u => {
        usageMap[u.item_name] = u
      })
    }
    itemUsage.value = usageMap
  } catch (e) {
    console.error('加载物品数据失败', e)
    handleApiError(e, '加载物品数据')
  } finally {
    itemLoading.value = false
  }
}

// ==================== 物品赠送 ====================
async function giveItem() {
  if (!playerId.value) return ElMessage.warning('请输入角色ID')
  if (!itemForm.name) return ElMessage.warning('请选择物品')
  
  const amount = parseInt(itemForm.amount) || 1
  if (amount <= 0) return ElMessage.warning('数量必须大于0')
  
  // 检查配额
  if (currentItemLimit.value && amount > currentItemLimit.value.remaining) {
    return ElMessage.warning(`赠送数量超过剩余配额 (${currentItemLimit.value.remaining})`)
  }

  submitLoading.item = true
  try {
    const res = await request.post('/api/items/send-gift', {
      recipient_username: playerId.value,
      item_name: itemForm.name,
      quantity: amount
    })
    
    handleApiSuccess('POST', '/api/items/send-gift', res, res.message || '道具赠送成功')
    
    // 重置表单并刷新数据
    itemForm.amount = '1'
    itemForm.params = ''
    await loadItemData()
  } catch (e) {
    handleApiError(e, '道具赠送')
  } finally {
    submitLoading.item = false
  }
}

// ==================== 宝石赠送 ====================
async function giveGem() {
  if (!playerId.value) return ElMessage.warning('请输入角色ID')
  if (!gemForm.type) return ElMessage.warning('请选择宝石类型')
  if (!gemForm.minLevel) return ElMessage.warning('请输入最低等级')

  const minLevel = parseInt(gemForm.minLevel)
  const maxLevel = gemForm.maxLevel ? parseInt(gemForm.maxLevel) : minLevel
  
  if (minLevel <= 0 || minLevel > 10) return ElMessage.warning('等级范围为1-10')
  if (maxLevel < minLevel) return ElMessage.warning('最高等级不能小于最低等级')

  submitLoading.gem = true
  try {
    const res = await request.post('/api/gift', {
      function: 'give_gem',
      args: {
        player_id: playerId.value,
        gem_name: gemForm.type,
        min_level: minLevel,
        max_level: maxLevel
      }
    })
    
    handleApiSuccess('POST', '/api/gift', res, '宝石赠送成功')
    
    // 重置表单
    gemForm.minLevel = ''
    gemForm.maxLevel = ''
  } catch (e) {
    handleApiError(e, '宝石赠送')
  } finally {
    submitLoading.gem = false
  }
}

// ==================== CDK类型管理 ====================
async function getRechargeTypes() {
  typeLoading.value = true
  try {
    const res = await request.post('/api/gift', {
      function: 'get_recharge_types',
      args: {}
    })
    
    handleApiSuccess('POST', '/api/gift', res)

    if (res.status === 'success' && res.data?.length > 0) {
      const obj = res.data.find(item => item.seq_no === 12)
      if (obj?.content) {
        const types = parseListFromContent(obj.content)
        rechargeTypes.value = types
        ElMessage.success(`获取到 ${types.length} 个类型`)
      } else {
        rechargeTypes.value = []
        ElMessage.info('暂无充值类型')
      }
    }
  } catch (e) {
    handleApiError(e, '获取充值类型')
  } finally {
    typeLoading.value = false
  }
}

async function newRechargeType() {
  if (!cdkForm.selectedType) return ElMessage.warning('请输入类型名称')
  
  // 检查是否已存在
  if (rechargeTypes.value.includes(cdkForm.selectedType)) {
    return ElMessage.warning('该类型已存在')
  }

  submitLoading.newType = true
  try {
    const res = await request.post('/api/gift', {
      function: 'new_recharge_type',
      args: { type_name: cdkForm.selectedType }
    })
    
    handleApiSuccess('POST', '/api/gift', res, '类型创建成功')
    await getRechargeTypes()
  } catch (e) {
    handleApiError(e, '创建类型')
  } finally {
    submitLoading.newType = false
  }
}

async function confirmDelRechargeType() {
  if (!cdkForm.selectedType) return ElMessage.warning('请选择要删除的类型')
  
  try {
    await ElMessageBox.confirm(
      `确定要删除充值类型 "${cdkForm.selectedType}" 吗？该操作不可恢复！`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    await delRechargeType()
  } catch {
    // 用户取消
  }
}

async function delRechargeType() {
  submitLoading.delType = true
  try {
    const res = await request.post('/api/gift', {
      function: 'del_recharge_type',
      args: { 
        selected_type: cdkForm.selectedType, 
        type_name: cdkForm.selectedType 
      }
    })
    
    handleApiSuccess('POST', '/api/gift', res, '类型删除成功')
    cdkForm.selectedType = ''
    cardList.value = []
    await getRechargeTypes()
  } catch (e) {
    handleApiError(e, '删除类型')
  } finally {
    submitLoading.delType = false
  }
}

// ==================== CDK卡号管理 ====================
function handleTypeChange() {
  cardList.value = []
}

async function getRechargeCard() {
  if (!cdkForm.selectedType) return ElMessage.warning('请选择充值类型')

  cardLoading.value = true
  try {
    const res = await request.post('/api/gift', {
      function: 'get_recharge_card',
      args: { selected_type: cdkForm.selectedType }
    })
    
    handleApiSuccess('POST', '/api/gift', res)

    if (res.status === 'success' && res.data?.length > 0) {
      const obj = res.data.find(item => item.seq_no === 12)
      if (obj?.content) {
        const cards = parseListFromContent(obj.content)
        cardList.value = cards
        ElMessage.success(`获取到 ${cards.length} 个卡号`)
      } else {
        cardList.value = []
        ElMessage.info('该类型暂无卡号')
      }
    }
  } catch (e) {
    handleApiError(e, '获取卡号')
  } finally {
    cardLoading.value = false
  }
}

async function generateCdk() {
  if (!cdkForm.selectedType) return ElMessage.warning('请选择充值类型')

  const count = parseInt(cdkForm.count) || 10
  const digits = parseInt(cdkForm.digits) || 12
  
  if (count <= 0 || count > 100) return ElMessage.warning('生成数量范围为1-100')
  if (digits < 6 || digits > 32) return ElMessage.warning('卡号位数范围为6-32')

  submitLoading.genCdk = true
  try {
    const res = await request.post('/api/gift', {
      function: 'generate_cdk',
      args: {
        selected_type: cdkForm.selectedType,
        gen_data: {
          数量: count,
          位数: digits
        }
      }
    })
    
    handleApiSuccess('POST', '/api/gift', res, `成功生成 ${count} 个CDK`)
    await getRechargeCard()
  } catch (e) {
    handleApiError(e, '生成CDK')
  } finally {
    submitLoading.genCdk = false
  }
}

async function generateCustomCdk() {
  if (!cdkForm.selectedType) return ElMessage.warning('请选择充值类型')
  if (!cdkForm.custom) return ElMessage.warning('请输入自定义内容')
  if (cdkForm.custom.length < 4) return ElMessage.warning('自定义内容至少4个字符')

  submitLoading.genCustomCdk = true
  try {
    const res = await request.post('/api/gift', {
      function: 'generate_custom_cdk',
      args: {
        selected_type: cdkForm.selectedType,
        gen_data: {
          数量: 1,
          位数: parseInt(cdkForm.digits) || 12,
          自定义内容: cdkForm.custom
        }
      }
    })
    
    handleApiSuccess('POST', '/api/gift', res, '自定义CDK生成成功')
    cdkForm.custom = ''
    await getRechargeCard()
  } catch (e) {
    handleApiError(e, '生成自定义CDK')
  } finally {
    submitLoading.genCustomCdk = false
  }
}

// ==================== 复制功能 ====================
async function copyCard(card) {
  try {
    await navigator.clipboard.writeText(card)
    copiedCard.value = card
    ElMessage.success('已复制: ' + card)
    
    // 2秒后重置复制状态
    setTimeout(() => {
      if (copiedCard.value === card) {
        copiedCard.value = ''
      }
    }, 2000)
  } catch {
    ElMessage.error('复制失败，请手动复制')
  }
}

async function copyAllCards() {
  if (!cardList.value.length) return
  
  try {
    await navigator.clipboard.writeText(cardList.value.join('\n'))
    ElMessage.success(`已复制全部 ${cardList.value.length} 个卡号`)
  } catch {
    ElMessage.error('复制失败，请手动复制')
  }
}

async function confirmClearCards() {
  try {
    await ElMessageBox.confirm(
      '确定要清空当前显示的卡号列表吗？（仅清空显示，不删除服务器数据）',
      '清空确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    cardList.value = []
    ElMessage.success('已清空卡号列表')
  } catch {
    // 用户取消
  }
}

// ==================== 生命周期 ====================
onMounted(() => {
  loadItemData()
})

// 切换到CDK标签时自动加载类型
watch(activeTab, (newTab) => {
  if (newTab === 'cdk' && rechargeTypes.value.length === 0) {
    getRechargeTypes()
  }
})
</script>

<style scoped>
/* ==================== 基础变量 ==================== */
.gift-module {
  --c-bg: #ffffff;
  --c-bg-soft: #f8fafc;
  --c-bg-mute: #f1f5f9;
  --c-border: #e2e8f0;
  --c-border-light: #f1f5f9;
  --c-text: #1e293b;
  --c-text-2: #475569;
  --c-text-3: #94a3b8;
  --c-primary: #3b82f6;
  --c-success: #10b981;
  --c-warning: #f59e0b;
  --c-danger: #ef4444;
  --radius: 12px;
  --radius-sm: 8px;
  --shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);

  background: var(--c-bg);
  border: 1px solid var(--c-border);
  border-radius: var(--radius);
  overflow: hidden;
}

/* ==================== 导航栏 ==================== */
.module-nav {
  display: flex;
  gap: 8px;
  padding: 16px 20px;
  background: var(--c-bg-soft);
  border-bottom: 1px solid var(--c-border);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 500;
  color: var(--c-text-2);
  cursor: pointer;
  transition: all 0.2s;
}

.nav-item:hover {
  background: var(--c-bg);
  border-color: var(--c-border);
}

.nav-item.active {
  background: var(--c-primary);
  border-color: var(--c-primary);
  color: #fff;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.nav-icon {
  font-size: 16px;
}

/* ==================== 内容区域 ==================== */
.module-body {
  padding: 20px;
}

/* ==================== 区块网格 ==================== */
.section-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

/* ==================== 区块盒子 ==================== */
.section-box {
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  border-radius: var(--radius);
  overflow: hidden;
  transition: box-shadow 0.2s;
}

.section-box:hover {
  box-shadow: var(--shadow);
}

.box-title {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  font-size: 14px;
  font-weight: 600;
  color: var(--c-text);
  background: var(--c-bg-soft);
  border-bottom: 1px solid var(--c-border-light);
}

.icon-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.icon-dot.blue { background: var(--c-primary); }
.icon-dot.purple { background: #8b5cf6; }
.icon-dot.cyan { background: #06b6d4; }
.icon-dot.amber { background: var(--c-warning); }

.box-content {
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* ==================== 输入组件 ==================== */
.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.input-group label {
  font-size: 13px;
  font-weight: 500;
  color: var(--c-text-2);
}

.input-group label em {
  color: var(--c-danger);
  font-style: normal;
}

.input-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.input-group :deep(.el-input__wrapper),
.input-group :deep(.el-select .el-input__wrapper) {
  border-radius: var(--radius-sm);
  box-shadow: 0 0 0 1px var(--c-border);
  transition: box-shadow 0.2s;
}

.input-group :deep(.el-input__wrapper:hover),
.input-group :deep(.el-select .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #cbd5e1;
}

.input-group :deep(.el-input__wrapper.is-focus),
.input-group :deep(.el-select .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--c-primary), 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input-group :deep(.el-select) {
  width: 100%;
}

/* ==================== 提交按钮 ==================== */
.submit-btn {
  width: 100%;
  height: 40px;
  border-radius: var(--radius-sm);
  font-weight: 500;
  transition: all 0.2s;
}

.submit-btn:not(:disabled):active {
  transform: scale(0.98);
}

/* ==================== 提示栏 ==================== */
.tips-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 14px 18px;
  background: var(--c-bg-mute);
  border-radius: var(--radius);
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--c-text-3);
}

.tip-icon {
  font-size: 14px;
}

/* ==================== 类型选择栏 ==================== */
.type-bar {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  padding: 18px;
  background: var(--c-bg-soft);
  border: 1px solid var(--c-border);
  border-radius: var(--radius);
  margin-bottom: 20px;
}

.type-selector {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.type-selector label {
  font-size: 13px;
  font-weight: 500;
  color: var(--c-text-2);
}

.type-select {
  width: 100%;
}

.type-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.type-actions :deep(.el-button) {
  border-radius: var(--radius-sm);
}

/* ==================== 卡号展示 ==================== */
.card-display {
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  border-radius: var(--radius);
  overflow: hidden;
}

.display-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  background: var(--c-bg-soft);
  border-bottom: 1px solid var(--c-border-light);
}

.display-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--c-text);
}

.display-count {
  font-size: 12px;
  color: var(--c-text-3);
  background: var(--c-bg-mute);
  padding: 2px 8px;
  border-radius: 10px;
}

.display-actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.display-actions :deep(.el-button) {
  border-radius: var(--radius-sm);
}

.display-body {
  padding: 16px;
  max-height: 320px;
  overflow-y: auto;
}

/* 卡号列表 */
.card-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.card-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background: var(--c-bg-soft);
  border: 1px solid var(--c-border-light);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.15s;
}

.card-item:hover {
  background: var(--c-bg-mute);
  border-color: var(--c-primary);
}

.card-item.copied {
  background: rgba(16, 185, 129, 0.1);
  border-color: var(--c-success);
}

.card-item:hover .card-copy,
.card-item.copied .card-copy {
  opacity: 1;
}

.card-item.copied .card-copy {
  color: var(--c-success);
}

.card-index {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--c-bg);
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--c-text-3);
  flex-shrink: 0;
}

.card-code {
  flex: 1;
  font-family: 'SF Mono', Monaco, Consolas, monospace;
  font-size: 13px;
  color: var(--c-text);
  letter-spacing: 0.5px;
  word-break: break-all;
}

.card-copy {
  font-size: 12px;
  color: var(--c-primary);
  opacity: 0;
  transition: opacity 0.15s;
  flex-shrink: 0;
}

/* 卡号动画 */
.card-enter-active,
.card-leave-active {
  transition: all 0.3s ease;
}

.card-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.card-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 48px 20px;
  color: var(--c-text-3);
}

.empty-icon {
  font-size: 40px;
  opacity: 0.6;
}

.empty-text {
  font-size: 14px;
}

/* ==================== 响应式 ==================== */
@media (max-width: 768px) {
  .module-nav {
    padding: 12px 16px;
  }

  .nav-item {
    flex: 1;
    justify-content: center;
    padding: 10px 12px;
  }

  .nav-label {
    display: none;
  }

  .module-body {
    padding: 16px;
  }

  .section-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .type-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .type-actions {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
  }

  .input-row {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .tips-bar {
    flex-direction: column;
    gap: 10px;
  }

  .display-header {
    flex-wrap: wrap;
  }

  .display-actions {
    width: 100%;
    margin-top: 8px;
    margin-left: 0;
  }
}

@media (max-width: 480px) {
  .module-nav {
    padding: 10px 12px;
    gap: 6px;
  }

  .nav-item {
    padding: 8px 10px;
  }

  .nav-icon {
    font-size: 18px;
  }

  .module-body {
    padding: 12px;
  }

  .box-title {
    padding: 12px 14px;
    font-size: 13px;
  }

  .box-content {
    padding: 14px;
  }

  .type-actions {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .card-item {
    padding: 8px 12px;
  }

  .card-code {
    font-size: 12px;
  }
  
  .display-actions {
    flex-wrap: wrap;
  }
}

/* ==================== 暗色模式 ==================== */
@media (prefers-color-scheme: dark) {
  .gift-module {
    --c-bg: #1e293b;
    --c-bg-soft: #0f172a;
    --c-bg-mute: #334155;
    --c-border: #334155;
    --c-border-light: #475569;
    --c-text: #f1f5f9;
    --c-text-2: #cbd5e1;
    --c-text-3: #64748b;
  }

  .nav-item:hover {
    background: var(--c-bg-mute);
  }

  .card-index {
    background: var(--c-bg-mute);
  }
  
  .card-item.copied {
    background: rgba(16, 185, 129, 0.15);
  }
}

/* ==================== 滚动条美化 ==================== */
.display-body::-webkit-scrollbar {
  width: 6px;
}

.display-body::-webkit-scrollbar-track {
  background: var(--c-bg-soft);
  border-radius: 3px;
}

.display-body::-webkit-scrollbar-thumb {
  background: var(--c-border);
  border-radius: 3px;
}

.display-body::-webkit-scrollbar-thumb:hover {
  background: var(--c-text-3);
}
</style>