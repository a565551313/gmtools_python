<template>
  <div class="recharge-panel">
    <!-- Currency Recharge -->
    <div class="panel-card">
      <div class="card-header">
        <div class="header-icon yellow">
          <el-icon><Wallet /></el-icon>
        </div>
        <div class="header-text">
          <h3>货币充值</h3>
          <p>充值游戏内各类货币</p>
        </div>
      </div>
      <div class="card-body">
        <div class="form-grid cols-2">
          <div class="form-item">
            <label>货币类型</label>
            <el-select v-model="form.currencyType" placeholder="选择类型">
              <el-option label="仙玉" value="仙玉" />
              <el-option label="点卡" value="点卡" />
              <el-option label="银子" value="银子" />
              <el-option label="储备" value="储备" />
            </el-select>
          </div>
          <div class="form-item">
            <label>充值数量</label>
            <el-input v-model="form.currencyAmount" placeholder="输入数量">
              <template #prefix>
                <el-icon><Coin /></el-icon>
              </template>
            </el-input>
          </div>
        </div>
        <div class="action-bar">
          <el-button type="primary" @click="rechargeCurrency">
            <el-icon><Check /></el-icon>
            立即充值
          </el-button>
          <el-button @click="getRechargeRecord">
            <el-icon><Document /></el-icon>
            充值记录
          </el-button>
        </div>
      </div>
    </div>

    <!-- GM Level / Coin -->
    <div class="panel-card">
      <div class="card-header">
        <div class="header-icon purple">
          <el-icon><Trophy /></el-icon>
        </div>
        <div class="header-text">
          <h3>GM权限</h3>
          <p>设置GM等级与GM币</p>
        </div>
      </div>
      <div class="card-body">
        <div class="split-section">
          <div class="section-block">
            <div class="section-title">GM等级设置</div>
            <div class="form-grid cols-2">
              <div class="form-item">
                <label>选择等级</label>
                <el-select v-model="form.gmLevel" @change="updateGmLevelAmount">
                  <el-option v-for="i in 8" :key="i" :label="'GM'+(i-1)" :value="'GM'+(i-1)" />
                </el-select>
              </div>
              <div class="form-item">
                <label>对应数值</label>
                <el-input v-model="form.gmLevelAmount" readonly disabled />
              </div>
            </div>
            <el-button type="primary" class="section-btn purple" @click="rechargeGmLevel">
              设置GM等级
            </el-button>
          </div>
          <div class="section-divider"></div>
          <div class="section-block">
            <div class="section-title">GM币充值</div>
            <div class="form-item">
              <label>充值数额</label>
              <el-input v-model="form.gmCoinAmount" placeholder="输入GM币数量">
                <template #prefix>
                  <el-icon><Money /></el-icon>
                </template>
              </el-input>
            </div>
            <el-button type="primary" class="section-btn indigo" @click="rechargeGmCoin">
              充值GM币
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Exp / Skills -->
    <div class="panel-card">
      <div class="card-header">
        <div class="header-icon green">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="header-text">
          <h3>经验/熟练/积分</h3>
          <p>充值各类数值属性</p>
        </div>
      </div>
      <div class="card-body">
        <div class="form-grid cols-2">
          <div class="form-item">
            <label>充值类型</label>
            <el-select v-model="form.rechargeType" placeholder="选择类型">
              <el-option-group label="经验类">
                <el-option label="充值经验" value="充值经验" />
                <el-option label="充值累充" value="充值累充" />
              </el-option-group>
              <el-option-group label="熟练度">
                <el-option label="打造熟练" value="打造熟练" />
                <el-option label="裁缝熟练" value="裁缝熟练" />
                <el-option label="炼金熟练" value="炼金熟练" />
                <el-option label="淬灵熟练" value="淬灵熟练" />
              </el-option-group>
              <el-option-group label="贡献/积分">
                <el-option label="充值帮贡" value="充值帮贡" />
                <el-option label="充值门贡" value="充值门贡" />
                <el-option label="活跃积分" value="活跃积分" />
                <el-option label="比武积分" value="比武积分" />
              </el-option-group>
            </el-select>
          </div>
          <div class="form-item">
            <label>充值数额</label>
            <el-input v-model="form.genericAmount" placeholder="输入数额">
              <template #prefix>
                <el-icon><Plus /></el-icon>
              </template>
            </el-input>
          </div>
        </div>
        <div class="action-bar">
          <el-button type="success" @click="rechargeGeneric">
            <el-icon><Check /></el-icon>
            确认充值
          </el-button>
        </div>
      </div>
    </div>

    <!-- Bagua -->
    <div class="panel-card">
      <div class="card-header">
        <div class="header-icon slate">
          <el-icon><Compass /></el-icon>
        </div>
        <div class="header-text">
          <h3>八卦设置</h3>
          <p>配置角色八卦属性</p>
        </div>
      </div>
      <div class="card-body">
        <div class="bagua-grid">
          <div 
            v-for="name in baguaList" 
            :key="name.value"
            class="bagua-item"
            :class="{ active: form.baguaName === name.value }"
            @click="form.baguaName = name.value"
          >
            <span class="bagua-symbol">{{ name.symbol }}</span>
            <span class="bagua-name">{{ name.value }}</span>
          </div>
        </div>
        <div class="action-bar center">
          <el-button type="info" @click="setBagua">
            <el-icon><Setting /></el-icon>
            应用设置
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, inject } from 'vue'
import request from '@/api/request'
import { ElMessage } from 'element-plus'
import { 
  Wallet, Trophy, TrendCharts, Compass, 
  Coin, Check, Document, Money, Plus, Setting 
} from '@element-plus/icons-vue'

const playerId = inject('playerId')
const logToConsole = inject('logToConsole')

const baguaList = [
  { value: '乾', symbol: '☰' },
  { value: '兑', symbol: '☱' },
  { value: '离', symbol: '☲' },
  { value: '震', symbol: '☳' },
  { value: '巽', symbol: '☴' },
  { value: '坎', symbol: '☵' },
  { value: '艮', symbol: '☶' },
  { value: '坤', symbol: '☷' }
]

const form = reactive({
  currencyType: '仙玉',
  currencyAmount: '100',
  gmLevel: 'GM1',
  gmLevelAmount: '1',
  gmCoinAmount: '100',
  rechargeType: '充值经验',
  genericAmount: '100',
  baguaName: '乾'
})

function updateGmLevelAmount() {
  form.gmLevelAmount = form.gmLevel.replace('GM', '')
}

async function sendReq(func, args) {
  if (!playerId.value) {
    ElMessage.error('请输入角色ID')
    return
  }
  try {
    const res = await request.post('/api/account', { 
      function: func, 
      args: { player_id: playerId.value, ...args } 
    })
    logToConsole('POST', '/api/account', 200, res)
    ElMessage.success('执行成功')
  } catch (e) {
    logToConsole('POST', '/api/account', 0, { error: e.message })
  }
}

function rechargeCurrency() {
  sendReq('recharge_currency', { 
    currency_type: form.currencyType, 
    amount: parseInt(form.currencyAmount) || 0 
  })
}

function rechargeGmLevel() {
  sendReq('recharge_gm_level', { 
    amount: parseInt(form.gmLevelAmount) || 0, 
    gm_level: form.gmLevel 
  })
}

function rechargeGmCoin() {
  sendReq('recharge_gm_coin', { amount: parseInt(form.gmCoinAmount) || 0 })
}

function rechargeGeneric() {
  const type = form.rechargeType
  const amount = parseInt(form.genericAmount) || 0
  const skillTypes = ['充值经验', '充值累充', '打造熟练', '裁缝熟练', '炼金熟练', '淬灵熟练']
  const factionTypes = ['充值帮贡', '充值门贡', '活跃积分', '比武积分']
  
  if (skillTypes.includes(type)) {
    sendReq('recharge_skill', { amount, skill_type: type })
  } else if (factionTypes.includes(type)) {
    sendReq('recharge_faction', { amount, faction_type: type })
  }
}

function getRechargeRecord() {
  sendReq('recharge_record', {})
}

async function setBagua() {
  try {
    const res = await request.post('/api/account', { 
      function: 'set_bagua', 
      args: { bagua_name: form.baguaName } 
    })
    logToConsole('POST', '/api/account', 200, res)
    ElMessage.success('设置成功')
  } catch (e) {
    logToConsole('POST', '/api/account', 0, { error: e.message })
  }
}
</script>

<style scoped>
.recharge-panel {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 400px), 1fr));
  gap: 20px;
}

.panel-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 4px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
}

.panel-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px 24px;
  background: linear-gradient(135deg, #fafafa 0%, #fff 100%);
  border-bottom: 1px solid #f0f0f0;
}

.header-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.header-icon.yellow {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
}

.header-icon.purple {
  background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
  color: #7c3aed;
}

.header-icon.green {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
}

.header-icon.slate {
  background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
  color: #475569;
}

.header-text h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.header-text p {
  margin: 2px 0 0;
  font-size: 12px;
  color: #9ca3af;
}

.card-body {
  padding: 20px 24px 24px;
}

.form-grid {
  display: grid;
  gap: 16px;
}

.form-grid.cols-2 {
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-item label {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-item :deep(.el-select),
.form-item :deep(.el-input) {
  width: 100%;
}

.form-item :deep(.el-input__wrapper),
.form-item :deep(.el-select .el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #e5e7eb;
  transition: all 0.2s ease;
}

.form-item :deep(.el-input__wrapper:hover),
.form-item :deep(.el-select .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #d1d5db;
}

.form-item :deep(.el-input__wrapper.is-focus),
.form-item :deep(.el-select .el-input.is-focus .el-input__wrapper) {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
}

.action-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px dashed #e5e7eb;
}

.action-bar.center {
  justify-content: center;
}

.action-bar :deep(.el-button) {
  border-radius: 10px;
  padding: 10px 20px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.action-bar :deep(.el-button:hover) {
  transform: translateY(-1px);
}

/* Split Section for GM Card */
.split-section {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 20px;
  align-items: stretch;
}

@media (max-width: 600px) {
  .split-section {
    grid-template-columns: 1fr;
  }
  
  .section-divider {
    height: 1px !important;
    width: 100% !important;
    background: linear-gradient(90deg, transparent, #e5e7eb, transparent) !important;
  }
}

.section-block {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  padding-bottom: 8px;
  border-bottom: 2px solid #f3f4f6;
}

.section-divider {
  width: 1px;
  background: linear-gradient(180deg, transparent, #e5e7eb, transparent);
  margin: 0 4px;
}

.section-btn {
  margin-top: auto;
  border-radius: 10px !important;
  width: 100%;
}

.section-btn.purple {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%) !important;
  border: none !important;
}

.section-btn.indigo {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
  border: none !important;
}

/* Bagua Grid */
.bagua-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

@media (max-width: 400px) {
  .bagua-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.bagua-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 14px 8px;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}

.bagua-item:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
  transform: scale(1.02);
}

.bagua-item.active {
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.bagua-symbol {
  font-size: 24px;
  line-height: 1;
  color: #374151;
}

.bagua-item.active .bagua-symbol {
  color: #2563eb;
}

.bagua-name {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  margin-top: 4px;
}

.bagua-item.active .bagua-name {
  color: #3b82f6;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .panel-card {
    background: #1f2937;
    border-color: #374151;
  }
  
  .card-header {
    background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
    border-color: #374151;
  }
  
  .header-text h3 {
    color: #f9fafb;
  }
  
  .form-item label {
    color: #9ca3af;
  }
  
  .bagua-item {
    background: #374151;
    border-color: #4b5563;
  }
  
  .bagua-symbol,
  .bagua-name {
    color: #d1d5db;
  }
}
</style>