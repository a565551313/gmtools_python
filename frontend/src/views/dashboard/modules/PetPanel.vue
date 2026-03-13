<template>
  <div class="pet-manager">
    <!-- 顶部标签：宝宝 / 坐骑 -->
    <div class="tab-header">
      <button 
        :class="['tab-btn', { active: activeTab === 'pet' }]"
        @click="activeTab = 'pet'"
      >
        <span class="tab-icon">🐾</span>
        <span>宝宝管理</span>
      </button>
      <button 
        :class="['tab-btn', { active: activeTab === 'mount' }]"
        @click="activeTab = 'mount'"
      >
        <span class="tab-icon">🐎</span>
        <span>坐骑管理</span>
      </button>
    </div>

    <!-- 宝宝管理面板 -->
    <div v-show="activeTab === 'pet'" class="tab-content">
      <!-- 操作栏 -->
      <div class="action-bar">
        <div class="action-left">
          <el-button type="primary" @click="getPetInfo">
            <el-icon><Refresh /></el-icon>
            <span>获取信息</span>
          </el-button>
          <el-select
            v-model="selectedPetIndex"
            placeholder="选择宝宝"
            @change="onPetSelected"
            clearable
            class="pet-select"
          >
            <el-option
              v-for="(pet, index) in petData"
              :key="index"
              :label="pet['名称']"
              :value="index"
            />
          </el-select>
        </div>
        <el-button type="success" @click="modifyPet">
          <el-icon><Check /></el-icon>
          <span>保存修改</span>
        </el-button>
      </div>

      <!-- 子页签：基础属性 / 天生技能 / 功德录 / 技能设置 / 装备定制 -->
      <div class="sub-tab-header">
        <button
          :class="['sub-tab-btn', { active: activePetPage === 'basic' }]"
          @click="activePetPage = 'basic'"
        >
          基础属性
        </button>
        <button
          :class="['sub-tab-btn', { active: activePetPage === 'innate' }]"
          @click="activePetPage = 'innate'"
        >
          天生技能
        </button>
        <button
          :class="['sub-tab-btn', { active: activePetPage === 'merit' }]"
          @click="activePetPage = 'merit'"
        >
          功德录
        </button>
        <button
          :class="['sub-tab-btn', { active: activePetPage === 'skills' }]"
          @click="activePetPage = 'skills'"
        >
          技能设置
        </button>
        <button
          :class="['sub-tab-btn', { active: activePetPage === 'equip' }]"
          @click="activePetPage = 'equip'"
        >
          装备定制
        </button>
      </div>

      <!-- 基础属性页 -->
      <div v-show="activePetPage === 'basic'" class="pet-page">
        <section class="section-card">
          <header class="section-header">
            <span class="section-icon blue">📊</span>
            <div class="section-title">
              <h3>基础属性</h3>
              <p>等级、资质等核心数值</p>
            </div>
          </header>
          <div class="section-body">
            <div class="field-grid cols-3">
              <div v-for="field in fields.attrs" :key="field" class="field">
                <label>{{ field }}</label>
                <el-input v-model="petForm.attrs[field]" placeholder="--" />
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- 天生技能页 -->
      <div v-show="activePetPage === 'innate'" class="pet-page">
        <section class="section-card">
          <header class="section-header">
            <span class="section-icon purple">✨</span>
            <div class="section-title">
              <h3>天生技能</h3>
              <p>配置宝宝自带天生技能</p>
            </div>
          </header>
          <div class="section-body">
            <div class="field-grid cols-2">
              <div v-for="i in 4" :key="i" class="field">
                <label>天生{{ i }}</label>
                <el-input
                  v-model="petForm.innate['天生0' + i]"
                  placeholder="--"
                  size="small"
                />
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- 功德录页 -->
      <div v-show="activePetPage === 'merit'" class="pet-page">
        <section class="section-card">
          <header class="section-header">
            <span class="section-icon red">📜</span>
            <div class="section-title">
              <h3>功德录</h3>
              <p>自定义功德录属性加成</p>
            </div>
            <div class="section-actions">
              <el-button size="small" @click="activateMerit">激活</el-button>
              <el-button size="small" type="primary" @click="modifyMerit">修改</el-button>
            </div>
          </header>
          <div class="section-body">
            <div class="merit-list">
              <div v-for="(item, index) in meritForm.items" :key="index" class="merit-row">
                <el-select
                  v-model="item.type"
                  placeholder="属性"
                  size="small"
                  class="merit-type"
                >
                  <el-option
                    v-for="opt in meritTypesList"
                    :key="opt"
                    :label="opt"
                    :value="opt"
                  />
                </el-select>
                <el-input
                  v-model="item.value"
                  placeholder="数值"
                  size="small"
                  class="merit-value"
                />
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- 技能设置页 -->
      <div v-show="activePetPage === 'skills'" class="pet-page">
        <section class="section-card">
          <header class="section-header">
            <span class="section-icon amber">⚔️</span>
            <div class="section-title">
              <h3>技能设置</h3>
              <p>最多可配置20个技能</p>
            </div>
          </header>
          <div class="section-body">
            <div class="skills-container">
              <div v-for="i in 20" :key="i" class="skill-field">
                <span class="skill-num">{{ i }}</span>
                <el-input
                  v-model="petForm.skills['技能' + (i < 10 ? '0' + i : i)]"
                  placeholder="技能名称"
                  size="small"
                />
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- 装备定制页 -->
      <div v-show="activePetPage === 'equip'" class="pet-page">
        <section class="section-card">
          <header class="section-header">
            <span class="section-icon cyan">🛡️</span>
            <div class="section-title">
              <h3>定制装备</h3>
              <p>为宝宝打造专属装备</p>
            </div>
            <div class="section-actions">
              <el-button type="primary" @click="customPetEquip">发送装备</el-button>
            </div>
          </header>
          <div class="section-body">
            <div class="equip-form">
              <div class="equip-row">
                <div class="field">
                  <label>装备类型</label>
                  <el-select v-model="petEquipForm.type" placeholder="选择类型">
                    <el-option label="护腕" value="护腕" />
                    <el-option label="项圈" value="项圈" />
                    <el-option label="铠甲" value="铠甲" />
                  </el-select>
                </div>
                <div class="field">
                  <label>等级</label>
                  <el-input v-model="petEquipForm.level" placeholder="0" />
                </div>
                <div class="field">
                  <label>{{ getDynamicAttrLabel(petEquipForm.type) }}</label>
                  <el-input v-model="petEquipForm.mainAttrValue" placeholder="0" />
                </div>
                <div class="field">
                  <label>特效</label>
                  <el-select v-model="petEquipForm.effect" placeholder="选择特效" clearable>
                    <el-option label="无" value="" />
                    <el-option label="法术暴击" value="法术暴击" />
                    <el-option label="物理暴击" value="物理暴击" />
                    <el-option label="法术连击" value="法术连击" />
                    <el-option label="物理连击" value="物理连击" />
                    <el-option label="神佑复生" value="神佑复生" />
                  </el-select>
                </div>
              </div>
              <div class="equip-row">
                <div class="field">
                  <label>附加属性1</label>
                  <el-select v-model="petEquipForm.subAttr1" placeholder="选择属性" clearable>
                    <el-option
                      v-for="opt in commonAttrsList"
                      :key="opt"
                      :label="opt"
                      :value="opt"
                    />
                  </el-select>
                </div>
                <div class="field">
                  <label>数值</label>
                  <el-input v-model="petEquipForm.subAttr1Value" placeholder="0" />
                </div>
                <div class="field">
                  <label>附加属性2</label>
                  <el-select v-model="petEquipForm.subAttr2" placeholder="选择属性" clearable>
                    <el-option
                      v-for="opt in commonAttrsList"
                      :key="opt"
                      :label="opt"
                      :value="opt"
                    />
                  </el-select>
                </div>
                <div class="field">
                  <label>数值</label>
                  <el-input v-model="petEquipForm.subAttr2Value" placeholder="0" />
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>

    <!-- 坐骑管理面板 -->
    <div v-show="activeTab === 'mount'" class="tab-content">
      <!-- 操作栏 -->
      <div class="action-bar">
        <div class="action-left">
          <el-button type="primary" @click="getMountInfo">
            <el-icon><Refresh /></el-icon>
            <span>获取信息</span>
          </el-button>
          <el-select
            v-model="selectedMountIndex"
            placeholder="选择坐骑"
            @change="onMountSelected"
            clearable
            class="pet-select"
          >
            <el-option
              v-for="(mount, index) in mountData"
              :key="index"
              :label="mount['名称']"
              :value="index"
            />
          </el-select>
        </div>
        <el-button type="success" @click="modifyMount">
          <el-icon><Check /></el-icon>
          <span>保存修改</span>
        </el-button>
      </div>

      <!-- 内容区域 -->
      <div class="mount-grid">
        <!-- 坐骑属性 -->
        <section class="section-card">
          <header class="section-header">
            <span class="section-icon indigo">📈</span>
            <div class="section-title">
              <h3>坐骑属性</h3>
              <p>基础属性配置</p>
            </div>
          </header>
          <div class="section-body">
            <div class="field-grid cols-3">
              <div class="field">
                <label>等级</label>
                <el-input v-model="mountForm.modify['等级']" placeholder="--" />
              </div>
              <div class="field">
                <label>成长</label>
                <el-input v-model="mountForm.modify['成长']" placeholder="--" />
              </div>
              <div class="field">
                <label>技能点</label>
                <el-input v-model="mountForm.modify['技能点']" placeholder="--" />
              </div>
            </div>
          </div>
        </section>

        <!-- 坐骑技能 -->
        <section class="section-card">
          <header class="section-header">
            <span class="section-icon emerald">🌟</span>
            <div class="section-title">
              <h3>技能配置</h3>
              <p>最多5个技能</p>
            </div>
          </header>
          <div class="section-body">
            <div class="mount-skills">
              <div
                v-for="(skill, index) in mountForm.skills"
                :key="index"
                class="field"
              >
                <label>技能 {{ index + 1 }}</label>
                <el-select 
                  v-model="mountForm.skills[index]" 
                  placeholder="选择技能" 
                  clearable 
                  filterable
                >
                  <el-option
                    v-for="s in mountSkillsList"
                    :key="s"
                    :label="s"
                    :value="s"
                  />
                </el-select>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, inject } from 'vue'
import request from '@/api/request'
import { ElMessage } from 'element-plus'
import { Refresh, Check } from '@element-plus/icons-vue'
import { parseLuaTable } from '@/utils/luaParser'

const playerId = inject('playerId')
const logToConsole = inject('logToConsole')

const activeTab = ref('pet')
const activePetPage = ref('basic')

const fields = {
  attrs: [
    '等级', '模型', '种类', '潜力', '寿命', '成长',
    '攻击资质', '防御资质', '体力资质', '法力资质', '速度资质', '躲闪资质'
  ]
}

const mountSkillsList = [
  '反震', '吸血', '反击', '连击', '飞行', '感知', '再生', '冥思',
  '慧根', '必杀', '幸运', '神迹', '招架', '永恒', '偷袭', '毒',
  '驱鬼', '鬼魂术', '魔之心', '神佑复生', '精神集中', '法术连击',
  '法术暴击', '法术波动', '土属性吸收', '火属性吸收', '水属性吸收'
]

const meritTypesList = [
  '气血', '伤害', '防御', '速度', '穿刺等级', '治疗能力',
  '固定伤害', '法术伤害', '法术防御', '气血回复效果',
  '封印命中等级', '抵抗封印等级', '法术暴击等级',
  '物理暴击等级', '抗法术暴击等级', '抗物理暴击等级'
]

const commonAttrsList = [
  '伤害', '灵力', '敏捷', '耐力', '体质', '力量', '魔力', '气血', '魔法'
]

// 宝宝相关
const petData = ref([])
const selectedPetIndex = ref('')
const petForm = reactive({
  attrs: {},
  skills: {},
  innate: {}
})

const meritForm = reactive({
  items: Array(6).fill().map(() => ({ type: '', value: '' }))
})

const petEquipForm = reactive({
  type: '护腕',
  level: '0',
  mainAttrValue: '0',
  subAttr1: '',
  subAttr1Value: '0',
  subAttr2: '',
  subAttr2Value: '0',
  effect: ''
})

// 坐骑相关
const mountData = ref([])
const selectedMountIndex = ref('')
const mountForm = reactive({
  modify: { 等级: '', 成长: '', 技能点: '' },
  skills: ['', '', '', '', '']
})

// 初始化表单
fields.attrs.forEach(f => (petForm.attrs[f] = ''))
for (let i = 1; i <= 20; i++) {
  petForm.skills['技能' + (i < 10 ? '0' + i : i)] = ''
}
for (let i = 1; i <= 4; i++) {
  petForm.innate['天生0' + i] = ''
}

function getDynamicAttrLabel(type) {
  const map = { 护腕: '命中', 项圈: '速度', 铠甲: '防御' }
  return map[type] || '主属性'
}

async function getPetInfo() {
  if (!playerId.value) return ElMessage.error('请输入角色ID')
  try {
    const res = await request.post('/api/pet', {
      function: 'get_pet_info',
      args: { char_id: playerId.value }
    })
    logToConsole('POST', '/api/pet', 200, res)

    if (res.status === 'success' && res.data?.length > 0) {
      const petDataObj = res.data.find(item => item.seq_no === 11)
      if (petDataObj?.content) {
        const content = parseLuaTable(petDataObj.content)
        petData.value = Object.values(content).filter(
          item => typeof item === 'object' && item !== null && item['名称']
        )
        ElMessage.success(`获取成功，共 ${petData.value.length} 只宝宝`)
      } else {
        petData.value = []
        ElMessage.info('当前角色没有宝宝')
      }
    } else {
      petData.value = []
      ElMessage.info('当前角色没有宝宝')
    }
  } catch (e) {
    logToConsole('POST', '/api/pet', 0, { error: e.message })
  }
}

function onPetSelected(index) {
  const pet = petData.value[index]
  if (!pet) return

  fields.attrs.forEach(f => {
    petForm.attrs[f] = pet[f] !== undefined ? pet[f] : ''
  })

  const skills = pet['技能'] || {}
  for (let i = 1; i <= 20; i++) {
    const key = '技能' + (i < 10 ? '0' + i : i)
    petForm.skills[key] = skills[i] || ''
  }

  const innate = pet['天生技能'] || {}
  for (let i = 1; i <= 4; i++) {
    petForm.innate['天生0' + i] = innate[i] || ''
  }
}

async function modifyPet() {
  if (!playerId.value) return ElMessage.error('请输入角色ID')
  if (selectedPetIndex.value === '') return ElMessage.error('请选择宝宝')

  try {
    const res = await request.post('/api/pet', {
      function: 'modify_pet',
      args: {
        char_id: playerId.value,
        pet_index: parseInt(selectedPetIndex.value) + 1,
        modify_data: { ...petForm.attrs, ...petForm.innate }
      }
    })
    logToConsole('POST', '/api/pet', 200, res)
    ElMessage.success('修改成功')
  } catch (e) {
    logToConsole('POST', '/api/pet', 0, { error: e.message })
  }
}

async function activateMerit() {
  if (!playerId.value) return ElMessage.error('请输入角色ID')
  try {
    const res = await request.post('/api/pet', {
      function: 'activate_merit',
      args: { char_id: playerId.value }
    })
    logToConsole('POST', '/api/pet', 200, res)
    ElMessage.success('功德录激活成功')
  } catch (e) {
    logToConsole('POST', '/api/pet', 0, { error: e.message })
  }
}

async function modifyMerit() {
  if (!playerId.value) return ElMessage.error('请输入角色ID')

  const modifyData = {}
  meritForm.items.forEach((item, index) => {
    if (item.type && item.value) {
      modifyData[index + 1] = { 属性: item.type, 数值: parseInt(item.value) }
    }
  })

  try {
    const res = await request.post('/api/pet', {
      function: 'modify_merit',
      args: { char_id: playerId.value, modify_data: modifyData }
    })
    logToConsole('POST', '/api/pet', 200, res)
    ElMessage.success('功德录修改成功')
  } catch (e) {
    logToConsole('POST', '/api/pet', 0, { error: e.message })
  }
}

async function customPetEquip() {
  if (!playerId.value) return ElMessage.error('请输入角色ID')

  const equipData = {
    类型: petEquipForm.type,
    等级: parseInt(petEquipForm.level),
    属性值: parseInt(petEquipForm.mainAttrValue),
    属性1: petEquipForm.subAttr1,
    数值1: parseInt(petEquipForm.subAttr1Value),
    属性2: petEquipForm.subAttr2,
    数值2: parseInt(petEquipForm.subAttr2Value),
    特效: petEquipForm.effect
  }

  try {
    const res = await request.post('/api/pet', {
      function: 'custom_pet_equip',
      args: { char_id: playerId.value, equip_data: equipData }
    })
    logToConsole('POST', '/api/pet', 200, res)
    ElMessage.success('装备发送成功')
  } catch (e) {
    logToConsole('POST', '/api/pet', 0, { error: e.message })
  }
}

async function getMountInfo() {
  if (!playerId.value) return ElMessage.error('请输入角色ID')
  try {
    const res = await request.post('/api/pet', {
      function: 'get_mount',
      args: { char_id: playerId.value }
    })
    logToConsole('POST', '/api/pet', 200, res)

    if (res.status === 'success' && res.data?.length > 0) {
      const mountDataObj = res.data.find(item => item.seq_no === 14)
      if (mountDataObj?.content) {
        const parsedData = parseLuaTable(mountDataObj.content)
        mountData.value = Object.keys(parsedData)
          .map(key => parsedData[key])
          .filter(item => typeof item === 'object' && item !== null && item['名称'])
        ElMessage.success(`获取成功，共 ${mountData.value.length} 个坐骑`)
      } else {
        mountData.value = []
        ElMessage.info('当前角色没有坐骑')
      }
    } else {
      mountData.value = []
      ElMessage.info('当前角色没有坐骑')
    }
  } catch (e) {
    logToConsole('POST', '/api/pet', 0, { error: e.message })
  }
}

function onMountSelected(index) {
  const mount = mountData.value[index]
  if (!mount) return

  mountForm.modify['等级'] = mount['等级'] || ''
  mountForm.modify['成长'] = mount['成长'] || ''
  mountForm.modify['技能点'] = mount['技能点'] || ''

  const skills = mount['技能'] || {}
  mountForm.skills = ['', '', '', '', '']
  Object.keys(skills).forEach(key => {
    const i = parseInt(key) - 1
    if (i >= 0 && i < 5 && skills[key]) {
      mountForm.skills[i] = skills[key]
    }
  })
}

async function modifyMount() {
  if (!playerId.value) return ElMessage.error('请输入角色ID')
  if (selectedMountIndex.value === '') return ElMessage.error('请选择坐骑')

  const skillData = {}
  mountForm.skills.forEach((skill, i) => {
    if (skill?.trim()) skillData[i + 1] = skill
  })

  try {
    const res = await request.post('/api/pet', {
      function: 'modify_mount',
      args: {
        char_id: playerId.value,
        mount_data: {
          ...mountForm.modify,
          技能: skillData,
          编号: parseInt(selectedMountIndex.value) + 1
        }
      }
    })
    logToConsole('POST', '/api/pet', 200, res)
    ElMessage.success('修改成功')
  } catch (e) {
    logToConsole('POST', '/api/pet', 0, { error: e.message })
  }
}
</script>

<style scoped>
.pet-manager {
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-tertiary: #f1f5f9;
  --border-color: #e2e8f0;
  --border-light: #f1f5f9;
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #94a3b8;
  --accent-blue: #3b82f6;
  --accent-purple: #8b5cf6;
  --accent-amber: #f59e0b;
  --accent-red: #ef4444;
  --accent-cyan: #06b6d4;
  --accent-indigo: #6366f1;
  --accent-emerald: #10b981;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -4px rgba(0, 0, 0, 0.05);
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;

  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--border-color);
}

/* 顶部标签：宝宝 / 坐骑 */
.tab-header {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  background: transparent;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.tab-btn.active {
  background: var(--accent-blue);
  color: #fff;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.tab-icon {
  font-size: 18px;
}

/* 外层标签内容 */
.tab-content {
  padding: 20px;
}

/* 顶部操作栏 */
.action-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
  padding: 16px;
  background: var(--bg-primary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
}

.action-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.pet-select {
  width: 200px;
}

.action-bar :deep(.el-button) {
  border-radius: var(--radius-sm);
  font-weight: 500;
}

/* 子页签：基础属性 / 天生技能 / 功德录 / 技能设置 / 装备定制 */
.sub-tab-header {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.sub-tab-btn {
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.sub-tab-btn:hover {
  background: var(--bg-tertiary);
}

.sub-tab-btn.active {
  background: var(--accent-blue);
  border-color: var(--accent-blue);
  color: #fff;
  box-shadow: 0 2px 6px rgba(59, 130, 246, 0.35);
}

/* 每个宝宝子页面容器 */
.pet-page {
  margin-top: 4px;
}

/* 坐骑内容布局 */
.mount-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

/* 区块卡片 */
.section-card {
  background: var(--bg-primary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  transition: box-shadow 0.2s ease;
}

.section-card:hover {
  box-shadow: var(--shadow-lg);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-light);
}

.section-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  font-size: 18px;
  flex-shrink: 0;
}

.section-icon.blue { background: #dbeafe; }
.section-icon.purple { background: #ede9fe; }
.section-icon.amber { background: #fef3c7; }
.section-icon.red { background: #fee2e2; }
.section-icon.cyan { background: #cffafe; }
.section-icon.indigo { background: #e0e7ff; }
.section-icon.emerald { background: #d1fae5; }

.section-title {
  flex: 1;
  min-width: 0;
}

.section-title h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.section-title p {
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--text-muted);
}

.section-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.section-actions :deep(.el-button) {
  border-radius: var(--radius-sm);
}

.section-body {
  padding: 18px;
}

/* 表单字段 */
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
}

.field :deep(.el-input__wrapper),
.field :deep(.el-select .el-input__wrapper) {
  border-radius: var(--radius-sm);
  box-shadow: inset 0 0 0 1px var(--border-color);
  transition: all 0.15s ease;
}

.field :deep(.el-input__wrapper:hover),
.field :deep(.el-select .el-input__wrapper:hover) {
  box-shadow: inset 0 0 0 1px #cbd5e1;
}

.field :deep(.el-input__wrapper.is-focus),
.field :deep(.el-select .el-input__wrapper.is-focus) {
  box-shadow: inset 0 0 0 1px var(--accent-blue), 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* 字段网格 */
.field-grid {
  display: grid;
  gap: 14px;
}

.field-grid.cols-2 {
  grid-template-columns: repeat(2, 1fr);
}

.field-grid.cols-3 {
  grid-template-columns: repeat(3, 1fr);
}

/* 技能容器 */
.skills-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 10px;
}

.skill-field {
  display: flex;
  align-items: center;
  gap: 8px;
}

.skill-num {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  flex-shrink: 0;
}

.skill-field :deep(.el-input) {
  flex: 1;
}

/* 功德录 */
.merit-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.merit-row {
  display: flex;
  gap: 8px;
}

.merit-type {
  flex: 1;
}

.merit-value {
  width: 80px;
  flex-shrink: 0;
}

/* 装备表单 */
.equip-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.equip-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

/* 坐骑技能 */
.mount-skills {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 14px;
}

/* 响应式 */
@media (max-width: 1024px) {
  .mount-grid {
    grid-template-columns: 1fr;
  }

  .equip-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .field-grid.cols-3 {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .tab-content {
    padding: 16px;
  }

  .action-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .action-left {
    width: 100%;
  }

  .pet-select {
    flex: 1;
    width: auto;
  }

  .action-bar > .el-button {
    width: 100%;
  }

  .equip-row {
    grid-template-columns: 1fr;
  }

  .merit-list {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .tab-header {
    padding: 8px 12px;
  }

  .tab-btn {
    flex: 1;
    justify-content: center;
    padding: 10px 12px;
  }

  .tab-btn span:not(.tab-icon) {
    display: none;
  }

  .tab-content {
    padding: 12px;
  }

  .section-header {
    padding: 12px 14px;
  }

  .section-body {
    padding: 14px;
  }

  .field-grid.cols-2,
  .field-grid.cols-3 {
    grid-template-columns: 1fr;
  }

  .skills-container {
    grid-template-columns: 1fr;
  }

  .merit-row {
    flex-direction: column;
  }

  .merit-value {
    width: 100%;
  }

  .sub-tab-header {
    gap: 6px;
  }

  .sub-tab-btn {
    flex: 1 1 45%;
    padding: 7px 10px;
    font-size: 12px;
  }
}

/* 暗色模式 */
@media (prefers-color-scheme: dark) {
  .pet-manager {
    --bg-primary: #1e293b;
    --bg-secondary: #0f172a;
    --bg-tertiary: #334155;
    --border-color: #334155;
    --border-light: #1e293b;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.2);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
  }

  .tab-btn:hover {
    background: var(--bg-tertiary);
  }

  .section-icon.blue { background: #1e3a5f; }
  .section-icon.purple { background: #4c1d95; }
  .section-icon.amber { background: #78350f; }
  .section-icon.red { background: #7f1d1d; }
  .section-icon.cyan { background: #164e63; }
  .section-icon.indigo { background: #312e81; }
  .section-icon.emerald { background: #064e3b; }

  .skill-num {
    background: var(--bg-tertiary);
  }
}
</style>