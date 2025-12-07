<template>
  <div class="character-panel">
    <!-- 操作按钮区 -->
    <div class="action-bar">
      <div class="action-group">
        <el-button type="primary" color="#8b5cf6" @click="getCharacterInfo"><el-icon><Download /></el-icon>获取角色信息</el-button>
        <el-button type="warning" color="#8b5cf6" @click="recoverCharacterProps"><el-icon><RefreshLeft /></el-icon>恢复角色道具</el-button>
      </div>
      <el-button type="success" color="#8b5cf6" @click="modifyCharacter">确定修改</el-button>
    </div>

    <!-- 表单区域 -->
    <div class="form-section">
      <!-- 角色修炼 -->
      <div class="form-card">
        <div class="card-header">
          <div class="header-icon cultivation"></div>
          <span class="header-title">角色修炼</span>
          <span class="header-badge">{{ fields.cultivation.length }}项</span>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-4">
            <div v-for="field in fields.cultivation" :key="field" class="field-item">
              <label class="field-label">{{ field }}</label>
              <el-input v-model="form.cultivation[field]" placeholder="请输入" clearable />
            </div>
          </div>
        </div>
      </div>

      <!-- 召唤兽修炼 -->
      <div class="form-card">
        <div class="card-header">
          <div class="header-icon pet"></div>
          <span class="header-title">召唤兽修炼</span>
          <span class="header-badge">{{ fields.petCultivation.length }}项</span>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-5">
            <div v-for="field in fields.petCultivation" :key="field" class="field-item">
              <label class="field-label">{{ field }}</label>
              <el-input v-model="form.petCultivation[field]" placeholder="请输入" clearable />
            </div>
          </div>
        </div>
      </div>

      <!-- 生活技能 -->
      <div class="form-card">
        <div class="card-header">
          <div class="header-icon life"></div>
          <span class="header-title">生活技能</span>
          <span class="header-badge">{{ fields.life.length }}项</span>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-6">
            <div v-for="field in fields.life" :key="field" class="field-item">
              <label class="field-label">{{ field }}</label>
              <el-input v-model="form.life[field]" placeholder="请输入" clearable />
            </div>
          </div>
        </div>
      </div>

      <!-- 强化技能 -->
      <div class="form-card">
        <div class="card-header">
          <div class="header-icon enhancement"></div>
          <span class="header-title">强化技能</span>
          <span class="header-badge">{{ fields.enhancement.length }}项</span>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-6">
            <div v-for="field in fields.enhancement" :key="field" class="field-item">
              <label class="field-label">{{ field }}</label>
              <el-input v-model="form.enhancement[field]" placeholder="请输入" clearable />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, inject } from 'vue'
import request from '@/api/request'
import { ElMessage } from 'element-plus'
import { Download, RefreshLeft, Check } from '@element-plus/icons-vue'
import { parseLuaTable } from '@/utils/luaParser'

const playerId = inject('playerId')
const logToConsole = inject('logToConsole')

const fields = {
  cultivation: ["攻击修炼", "法术修炼", "防御修炼", "抗法修炼"],
  life: ["强身术", "冥想", "强壮", "暗器技巧", "中药医理", "烹饪技巧", "打造技巧", "裁缝技巧", "炼金术", "淬灵之术", "养生之道", "健身术"],
  enhancement: ["人物伤害", "人物防御", "人物气血", "人物法术", "人物速度", "人物固伤", "人物治疗", "宠物伤害", "宠物防御", "宠物气血", "宠物灵力", "宠物速度"],
  petCultivation: ["攻击控制力", "法术控制力", "防御控制力", "抗法控制力", "玩家等级"]
}

const form = reactive({
  cultivation: {},
  life: {},
  enhancement: {},
  petCultivation: {}
})

// 初始化表单数据
Object.keys(fields).forEach(key => {
  fields[key].forEach(field => {
    form[key][field] = ''
  })
})

async function getCharacterInfo() {
  if (!playerId.value) return ElMessage.error('请输入角色ID')
  try {
    const res = await request.post('/api/character', { 
      function: 'get_character_info', 
      args: { char_id: playerId.value } 
    })
    logToConsole('POST', '/api/character', 200, res)
    
    if (res.status === 'success' && res.data?.[0]?.content) {
      const data = parseLuaTable(res.data[0].content)
      
      if (data.修炼) {
        fields.cultivation.forEach(f => {
          form.cultivation[f] = data.修炼[f]?.[1] || ''
        })
      }
      if (data.生活技能) {
        Object.entries(data.生活技能).forEach(([k, v]) => {
          if (form.life.hasOwnProperty(k)) form.life[k] = v
        })
      }
      if (data.强化技能) {
        Object.entries(data.强化技能).forEach(([k, v]) => {
          if (form.enhancement.hasOwnProperty(k)) form.enhancement[k] = v
        })
      }
      if (data.bb修炼) {
        fields.petCultivation.forEach(f => {
          form.petCultivation[f] = data.bb修炼[f]?.[1] || ''
        })
      }
      ElMessage.success('角色信息获取成功')
    }
  } catch (e) {
    logToConsole('POST', '/api/character', 0, { error: e.message })
  }
}

async function recoverCharacterProps() {
  if (!playerId.value) return ElMessage.error('请输入角色ID')
  try {
    const res = await request.post('/api/character', { 
      function: 'recover_character_props', 
      args: { char_id: playerId.value } 
    })
    logToConsole('POST', '/api/character', 200, res)
    ElMessage.success('恢复成功')
  } catch (e) {
    logToConsole('POST', '/api/character', 0, { error: e.message })
  }
}

async function modifyCharacter() {
  if (!playerId.value) return ElMessage.error('请输入角色ID')
  
  const sections = [
    { name: '角色修炼', data: form.cultivation },
    { name: '角色生活', data: form.life },
    { name: '角色强化', data: form.enhancement },
    { name: '召唤兽修炼', data: form.petCultivation },
  ]
  
  const parts = []
  try {
    sections.forEach(sec => {
      const kvs = Object.entries(sec.data)
        .filter(([k, v]) => v !== undefined && v !== null && String(v).trim() !== '')
        .map(([k, v]) => {
          const s = String(v).trim()
          if (!/^\d+$/.test(s)) throw new Error(`${sec.name} - ${k} 必须为纯数字`)
          return `["${k}"]="${s}"`
        })
      if (kvs.length) parts.push(`["${sec.name}"]={${kvs.join(',')}}`)
    })
  } catch (e) {
    return ElMessage.error(e.message)
  }
  
  if (!parts.length) return ElMessage.warning('没有输入任何修改数据')
  
  try {
    const res = await request.post('/api/character', { 
      function: 'modify_character', 
      args: { 
        char_id: playerId.value, 
        modify_data_str: `{${parts.join(',')}}` 
      } 
    })
    logToConsole('POST', '/api/character', 200, res)
    ElMessage.success('修改成功')
  } catch (e) {
    logToConsole('POST', '/api/character', 0, { error: e.message })
  }
}
</script>

<style scoped>
.character-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 操作按钮区 */
.action-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.action-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.action-bar .el-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
  border-radius: 8px;
  padding: 10px 18px;
  transition: all 0.2s ease;
}

.action-bar .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 表单区域 */
.form-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 表单卡片 */
.form-card {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  transition: box-shadow 0.2s ease;
}

.form-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  background: linear-gradient(135deg, #fafbfc 0%, #f5f7fa 100%);
  border-bottom: 1px solid #eef1f5;
}

.header-icon {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.header-icon.cultivation { background: linear-gradient(135deg, #f59e0b, #f97316); }
.header-icon.pet { background: linear-gradient(135deg, #8b5cf6, #a855f7); }
.header-icon.life { background: linear-gradient(135deg, #10b981, #14b8a6); }
.header-icon.enhancement { background: linear-gradient(135deg, #3b82f6, #6366f1); }

.header-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  letter-spacing: 0.3px;
}

.header-badge {
  margin-left: auto;
  font-size: 11px;
  font-weight: 500;
  color: #9ca3af;
  background: #f3f4f6;
  padding: 3px 10px;
  border-radius: 12px;
}

/* 卡片内容 */
.card-body {
  padding: 20px;
}

/* Grid 布局 */
.grid {
  display: grid;
  gap: 16px;
}

.grid-cols-4 {
  grid-template-columns: repeat(4, 1fr);
}

.grid-cols-5 {
  grid-template-columns: repeat(5, 1fr);
}

.grid-cols-6 {
  grid-template-columns: repeat(6, 1fr);
}

/* 字段项 */
.field-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.field-item :deep(.el-input) {
  --el-input-border-radius: 8px;
}

.field-item :deep(.el-input__wrapper) {
  padding: 4px 12px;
  transition: all 0.2s ease;
}

.field-item :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #c0c4cc inset;
}

.field-item :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--el-color-primary) inset;
}

.field-item :deep(.el-input__inner) {
  font-size: 13px;
  height: 32px;
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .grid-cols-6 {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 992px) {
  .grid-cols-5 {
    grid-template-columns: repeat(4, 1fr);
  }
  .grid-cols-6 {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .character-panel {
    gap: 16px;
  }
  
  .action-bar {
    flex-direction: column;
    align-items: stretch;
    padding: 14px 16px;
  }
  
  .action-group {
    width: 100%;
  }
  
  .action-group .el-button {
    flex: 1;
  }
  
  .action-bar > .el-button {
    width: 100%;
    justify-content: center;
  }
  
  .card-header {
    padding: 12px 16px;
  }
  
  .card-body {
    padding: 16px;
  }
  
  .grid {
    gap: 12px;
  }
  
  .grid-cols-4,
  .grid-cols-5 {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .grid-cols-6 {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .action-bar {
    padding: 12px;
  }
  
  .action-group {
    flex-direction: column;
  }
  
  .action-group .el-button,
  .action-bar > .el-button {
    width: 100%;
    justify-content: center;
  }
  
  .card-body {
    padding: 12px;
  }
  
  .grid {
    gap: 10px;
  }
  
  .field-label {
    font-size: 11px;
  }
  
  .field-item :deep(.el-input__inner) {
    font-size: 12px;
    height: 36px;
  }
}
</style>