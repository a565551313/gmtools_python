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
                <el-input v-model="itemForm.name" placeholder="请输入物品名称" />
              </div>
              <div class="input-row">
                <div class="input-group">
                  <label>数量</label>
                  <el-input v-model="itemForm.amount" placeholder="1" />
                </div>
                <div class="input-group">
                  <label>参数</label>
                  <el-input v-model="itemForm.params" placeholder="可选" />
                </div>
              </div>
              <el-button type="primary" @click="giveItem" class="submit-btn">
                赠送道具
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
                  <el-input v-model="gemForm.minLevel" placeholder="1" />
                </div>
                <div class="input-group">
                  <label>最高等级</label>
                  <el-input v-model="gemForm.maxLevel" placeholder="可选" />
                </div>
              </div>
              <el-button type="success" @click="giveGem" class="submit-btn">
                赠送宝石
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
            >
              <el-option v-for="t in rechargeTypes" :key="t" :label="t" :value="t" />
            </el-select>
          </div>
          <div class="type-actions">
            <el-button @click="getRechargeTypes" :icon="Refresh">刷新</el-button>
            <el-button type="primary" @click="newRechargeType" :icon="Plus">新建</el-button>
            <el-button type="danger" @click="delRechargeType" :icon="Delete">删除</el-button>
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
                  <el-input v-model="cdkForm.count" placeholder="10" />
                </div>
                <div class="input-group">
                  <label>卡号位数</label>
                  <el-input v-model="cdkForm.digits" placeholder="12" />
                </div>
              </div>
              <el-button type="primary" @click="generateCdk" class="submit-btn">
                生成随机CDK
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
                <label>自定义内容</label>
                <el-input v-model="cdkForm.custom" placeholder="输入自定义CDK内容" />
              </div>
              <el-button type="warning" @click="generateCustomCdk" class="submit-btn">
                生成自定义CDK
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
              <el-button size="small" @click="getRechargeCard" :icon="Search">获取</el-button>
              <el-button size="small" @click="copyAllCards" :icon="CopyDocument" :disabled="!cardList.length">复制全部</el-button>
            </div>
          </div>
          <div class="display-body">
            <div v-if="cardList.length" class="card-list">
              <div 
                v-for="(card, idx) in cardList" 
                :key="idx" 
                class="card-item"
                @click="copyCard(card)"
              >
                <span class="card-index">{{ idx + 1 }}</span>
                <span class="card-code">{{ card }}</span>
                <span class="card-copy">点击复制</span>
              </div>
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
import { ref, reactive, inject } from 'vue'
import request from '@/api/request'
import { ElMessage } from 'element-plus'
import { Refresh, Plus, Delete, Search, CopyDocument } from '@element-plus/icons-vue'

const playerId = inject('playerId')
const logToConsole = inject('logToConsole')

// 标签配置
const tabs = [
  { key: 'item', label: '物品赠送', icon: '🎁' },
  { key: 'cdk', label: 'CDK管理', icon: '🎫' }
]
const activeTab = ref('item')

// 宝石类型
const gemTypes = ['星辉石', '光芒石', '月亮石', '太阳石', '舍利子', '红玛瑙', '黑宝石', '神秘石']

// 表单数据
const itemForm = reactive({ name: '', amount: '1', params: '' })
const gemForm = reactive({ type: '', minLevel: '', maxLevel: '' })
const cdkForm = reactive({ selectedType: '', count: '10', digits: '12', custom: '' })

// CDK数据
const rechargeTypes = ref([])
const cardList = ref([])

// ========== 物品赠送 ==========
async function giveItem() {
  if (!playerId.value) return ElMessage.error('请输入角色ID')
  if (!itemForm.name) return ElMessage.error('请输入物品名称')

  try {
    const res = await request.post('/api/gift', {
      function: 'give_item',
      args: {
        player_id: playerId.value,
        item_name: itemForm.name,
        count: parseInt(itemForm.amount || '1'),
        item_category: itemForm.params || "default"
      }
    })
    logToConsole('POST', '/api/gift', 200, res)
    ElMessage.success('道具赠送成功')
  } catch (e) {
    logToConsole('POST', '/api/gift', 0, { error: e.message })
    ElMessage.error('赠送失败')
  }
}

// ========== 宝石赠送 ==========
async function giveGem() {
  if (!playerId.value) return ElMessage.error('请输入角色ID')
  if (!gemForm.type) return ElMessage.error('请选择宝石类型')
  if (!gemForm.minLevel) return ElMessage.error('请输入最低等级')

  try {
    const minLevel = parseInt(gemForm.minLevel)
    const maxLevel = gemForm.maxLevel ? parseInt(gemForm.maxLevel) : minLevel
    
    const res = await request.post('/api/gift', {
      function: 'give_gem',
      args: {
        player_id: playerId.value,
        gem_name: gemForm.type,
        min_level: minLevel,
        max_level: maxLevel
      }
    })
    logToConsole('POST', '/api/gift', 200, res)
    ElMessage.success('宝石赠送成功')
  } catch (e) {
    logToConsole('POST', '/api/gift', 0, { error: e.message })
    ElMessage.error('赠送失败')
  }
}

// ========== CDK管理 ==========
async function getRechargeTypes() {
  try {
    const res = await request.post('/api/gift', {
      function: 'get_recharge_types',
      args: {}
    })
    logToConsole('POST', '/api/gift', 200, res)

    if (res.status === 'success' && res.data?.length > 0) {
      const obj = res.data.find(item => item.seq_no === 12)
      if (obj?.content) {
        const types = []
        const regex = /\[(\d+)\]="([^"]+)"/g
        let match
        while ((match = regex.exec(obj.content)) !== null) {
          types.push(match[2])
        }
        rechargeTypes.value = types
        ElMessage.success(`获取到 ${types.length} 个类型`)
      }
    }
  } catch (e) {
    logToConsole('POST', '/api/gift', 0, { error: e.message })
  }
}

async function newRechargeType() {
  if (!cdkForm.selectedType) return ElMessage.error('请输入类型名称')

  try {
    const res = await request.post('/api/gift', {
      function: 'new_recharge_type',
      args: { type_name: cdkForm.selectedType }
    })
    logToConsole('POST', '/api/gift', 200, res)
    ElMessage.success('类型创建成功')
    getRechargeTypes()
  } catch (e) {
    logToConsole('POST', '/api/gift', 0, { error: e.message })
  }
}

async function delRechargeType() {
  if (!cdkForm.selectedType) return ElMessage.error('请选择要删除的类型')

  try {
    const res = await request.post('/api/gift', {
      function: 'del_recharge_type',
      args: { selected_type: cdkForm.selectedType, type_name: cdkForm.selectedType }
    })
    logToConsole('POST', '/api/gift', 200, res)
    ElMessage.success('类型删除成功')
    cdkForm.selectedType = ''
    cardList.value = []
    getRechargeTypes()
  } catch (e) {
    logToConsole('POST', '/api/gift', 0, { error: e.message })
  }
}

async function getRechargeCard() {
  if (!cdkForm.selectedType) return ElMessage.error('请选择充值类型')

  try {
    const res = await request.post('/api/gift', {
      function: 'get_recharge_card',
      args: { selected_type: cdkForm.selectedType }
    })
    logToConsole('POST', '/api/gift', 200, res)

    if (res.status === 'success' && res.data?.length > 0) {
      const obj = res.data.find(item => item.seq_no === 12)
      if (obj?.content) {
        const cards = []
        const regex = /\[(\d+)\]="([^"]+)"/g
        let match
        while ((match = regex.exec(obj.content)) !== null) {
          cards.push(match[2])
        }
        cardList.value = cards
        ElMessage.success(`获取到 ${cards.length} 个卡号`)
      } else {
        cardList.value = []
        ElMessage.info('该类型暂无卡号')
      }
    }
  } catch (e) {
    logToConsole('POST', '/api/gift', 0, { error: e.message })
  }
}

async function generateCdk() {
  if (!cdkForm.selectedType) return ElMessage.error('请选择充值类型')

  try {
    const res = await request.post('/api/gift', {
      function: 'generate_cdk',
      args: {
        selected_type: cdkForm.selectedType,
        gen_data: {
          数量: parseInt(cdkForm.count) || 10,
          位数: parseInt(cdkForm.digits) || 12
        }
      }
    })
    logToConsole('POST', '/api/gift', 200, res)
    ElMessage.success('CDK生成成功')
    getRechargeCard()
  } catch (e) {
    logToConsole('POST', '/api/gift', 0, { error: e.message })
  }
}

async function generateCustomCdk() {
  if (!cdkForm.selectedType) return ElMessage.error('请选择充值类型')
  if (!cdkForm.custom) return ElMessage.error('请输入自定义内容')

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
    logToConsole('POST', '/api/gift', 200, res)
    ElMessage.success('自定义CDK生成成功')
    getRechargeCard()
  } catch (e) {
    logToConsole('POST', '/api/gift', 0, { error: e.message })
  }
}

// ========== 复制功能 ==========
function copyCard(card) {
  navigator.clipboard.writeText(card)
    .then(() => ElMessage.success('已复制: ' + card))
    .catch(() => ElMessage.error('复制失败'))
}

function copyAllCards() {
  if (!cardList.value.length) return
  navigator.clipboard.writeText(cardList.value.join('\n'))
    .then(() => ElMessage.success('已复制全部卡号'))
    .catch(() => ElMessage.error('复制失败'))
}
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

.card-item:hover .card-copy {
  opacity: 1;
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
}

.card-code {
  flex: 1;
  font-family: 'SF Mono', Monaco, Consolas, monospace;
  font-size: 13px;
  color: var(--c-text);
  letter-spacing: 0.5px;
}

.card-copy {
  font-size: 12px;
  color: var(--c-primary);
  opacity: 0;
  transition: opacity 0.15s;
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
}
</style>