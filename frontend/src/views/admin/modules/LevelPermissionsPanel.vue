<template>
  <div class="panel-container" v-loading="loading">
    <!-- 等级选择器 -->
    <div class="level-selector">
      <div class="selector-left">
        <div class="selector-icon">
          <el-icon :size="24"><Lock /></el-icon>
        </div>
        <div class="selector-meta">
          <label>选择等级</label>
          <p>配置此等级的权限</p>
        </div>
      </div>
      <el-select v-model="selectedLevel" @change="loadLevelPermissions" class="level-select">
        <el-option v-for="config in levelConfigs" :key="config.level_value" :label="config.display_name" :value="config.level_value" />
      </el-select>
      <div class="selector-tip">
        <el-icon><InfoFilled /></el-icon>
        <span>修改此等级的权限配置，所有属于此等级的用户将自动继承。</span>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="quick-actions">
      <el-button @click="selectAll" type="primary" plain>
        <el-icon><Select /></el-icon> 全部选中
      </el-button>
      <el-button @click="deselectAll">
        <el-icon><CloseBold /></el-icon> 全部取消
      </el-button>
      <div class="selected-info">
        已选择 <span class="selected-count">{{ selectedCount }}</span> 项权限
      </div>
      <el-button type="primary" @click="savePermissions" :loading="saving" style="margin-left: auto">
        <el-icon><Check /></el-icon> 保存配置
      </el-button>
    </div>

    <!-- 权限分类网格 -->
    <div class="permissions-grid">
      <div v-for="(perms, category) in allPermissions" :key="category" class="permission-card">
        <div class="card-header">
          <div class="category-icon" :class="getCategoryClass(category)">
            <el-icon><component :is="getCategoryIcon(category)" /></el-icon>
          </div>
          <div class="category-info">
            <h3>{{ getCategoryName(category) }}</h3>
            <p>{{ perms.length }} 项权限</p>
          </div>
          <el-button size="small" :type="isCategoryAllSelected(category) ? 'primary' : 'default'" 
                     @click="toggleCategory(category)">
            {{ isCategoryAllSelected(category) ? '取消全选' : '全选' }}
          </el-button>
        </div>
        <div class="card-body">
          <el-checkbox-group v-model="selectedPermissions">
            <label v-for="perm in perms" :key="perm.code" class="permission-item">
              <el-checkbox :value="perm.code">
                <div class="perm-info">
                  <span class="perm-name">{{ perm.name }}</span>
                  <span class="perm-desc">{{ perm.description || '暂无描述' }}</span>
                </div>
              </el-checkbox>
            </label>
          </el-checkbox-group>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="Object.keys(allPermissions).length === 0 && !loading" class="empty-state">
      <el-icon :size="64"><Lock /></el-icon>
      <h3>暂无权限配置</h3>
      <p>请检查后端权限定义是否正确</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, markRaw } from 'vue'
import request from '@/api/request'
import { ElMessage } from 'element-plus'
import {
  Lock, InfoFilled, Select, CloseBold, Check,
  User, Money, Goods, Present, Setting, VideoPlay
} from '@element-plus/icons-vue'

const loading = ref(false)
const saving = ref(false)
const selectedLevel = ref(1)
const levelConfigs = ref([])
const allPermissions = ref({})
const selectedPermissions = ref([])
const originalPermissions = ref([])

const categoryConfig = {
  account: { name: '账号管理', icon: markRaw(User), class: 'bg-blue' },
  pet: { name: '宠物管理', icon: markRaw(Present), class: 'bg-pink' },
  equipment: { name: '装备管理', icon: markRaw(Goods), class: 'bg-orange' },
  gift: { name: '礼物道具', icon: markRaw(Present), class: 'bg-green' },
  character: { name: '角色管理', icon: markRaw(User), class: 'bg-purple' },
  game: { name: '游戏管理', icon: markRaw(VideoPlay), class: 'bg-indigo' },
  recharge: { name: '充值管理', icon: markRaw(Money), class: 'bg-yellow' }
}

const selectedCount = computed(() => selectedPermissions.value.length)

function getCategoryName(key) { return categoryConfig[key]?.name || key }
function getCategoryIcon(key) { return categoryConfig[key]?.icon || Setting }
function getCategoryClass(key) { return categoryConfig[key]?.class || 'bg-gray' }

function isCategoryAllSelected(category) {
  const perms = allPermissions.value[category] || []
  if (perms.length === 0) return false
  return perms.every(p => selectedPermissions.value.includes(p.code))
}

function toggleCategory(category) {
  const perms = allPermissions.value[category] || []
  const allSelected = isCategoryAllSelected(category)
  
  if (allSelected) {
    perms.forEach(p => {
      const idx = selectedPermissions.value.indexOf(p.code)
      if (idx > -1) selectedPermissions.value.splice(idx, 1)
    })
  } else {
    perms.forEach(p => {
      if (!selectedPermissions.value.includes(p.code)) {
        selectedPermissions.value.push(p.code)
      }
    })
  }
}

function selectAll() {
  selectedPermissions.value = []
  Object.values(allPermissions.value).forEach(perms => {
    perms.forEach(p => selectedPermissions.value.push(p.code))
  })
}

function deselectAll() {
  selectedPermissions.value = []
}

async function loadLevelConfigs() {
  try {
    const res = await request.get('/api/level-configs')
    levelConfigs.value = res.data || []
    // 如果当前选中的等级不在列表中，重置为第一个
    if (levelConfigs.value.length > 0 && !levelConfigs.value.find(c => c.level_value === selectedLevel.value)) {
      selectedLevel.value = levelConfigs.value[0].level_value
    }
  } catch (e) {
    // 回退
    levelConfigs.value = Array.from({ length: 10 }, (_, i) => ({
      level_value: i + 1,
      display_name: `Level ${i + 1}`
    }))
  }
}

async function loadAllPermissions() {
  loading.value = true
  try {
    const res = await request.get('/api/permissions')
    allPermissions.value = res.permissions || {}
  } catch (e) {} finally { loading.value = false }
}

async function loadLevelPermissions() {
  loading.value = true
  try {
    const res = await request.get(`/api/levels/${selectedLevel.value}/permissions`)
    const codes = res.permission_codes || []
    selectedPermissions.value = []
    
    if (codes.includes('*')) {
      Object.values(allPermissions.value).forEach(perms => {
        perms.forEach(p => {
          if (!selectedPermissions.value.includes(p.code)) {
            selectedPermissions.value.push(p.code)
          }
        })
      })
    } else {
      codes.forEach(code => {
        if (code.endsWith('.*')) {
          const prefix = code.split('.')[0]
          const categoryPerms = allPermissions.value[prefix] || []
          categoryPerms.forEach(p => {
            if (!selectedPermissions.value.includes(p.code)) {
              selectedPermissions.value.push(p.code)
            }
          })
        } else {
          if (!selectedPermissions.value.includes(code)) {
            selectedPermissions.value.push(code)
          }
        }
      })
    }
    
    originalPermissions.value = [...selectedPermissions.value]
  } catch (e) {} finally { loading.value = false }
}

async function savePermissions() {
  saving.value = true
  try {
    await request.put(`/api/levels/${selectedLevel.value}/permissions`, {
      permission_codes: selectedPermissions.value
    })
    originalPermissions.value = [...selectedPermissions.value]
    ElMessage.success(`Level ${selectedLevel.value} 权限保存成功`)
  } catch (e) {} finally { saving.value = false }
}

onMounted(async () => {
  await loadLevelConfigs()
  await loadAllPermissions()
  await loadLevelPermissions()
})
</script>

<style scoped>
.panel-container { width: 100%; }

.level-selector {
  background: white;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  margin-bottom: 24px;
}

.selector-left { display: flex; align-items: center; gap: 12px; }

.selector-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #818cf8, #a855f7);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.selector-meta label { font-weight: 700; color: #111827; display: block; }
.selector-meta p { font-size: 12px; color: #6b7280; margin: 0; }
.level-select { width: 160px; }

.selector-tip {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #eff6ff;
  border-radius: 12px;
  font-size: 14px;
  color: #1d4ed8;
}

.quick-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.selected-info { font-size: 14px; color: #6b7280; }
.selected-count {
  display: inline-block;
  padding: 2px 8px;
  background: #e0e7ff;
  color: #4338ca;
  border-radius: 6px;
  font-weight: 700;
}

.permissions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
}

.permission-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: linear-gradient(to right, #f9fafb, #f3f4f6);
  border-bottom: 1px solid #f3f4f6;
}

.category-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.bg-blue { background: #3b82f6; }
.bg-pink { background: #ec4899; }
.bg-orange { background: #f97316; }
.bg-green { background: #22c55e; }
.bg-purple { background: #a855f7; }
.bg-indigo { background: #6366f1; }
.bg-yellow { background: #eab308; }
.bg-gray { background: #6b7280; }

.category-info { flex: 1; }
.category-info h3 { font-size: 15px; font-weight: 700; color: #111827; margin: 0; }
.category-info p { font-size: 12px; color: #6b7280; margin: 0; }

.card-body { padding: 16px; max-height: 320px; overflow-y: auto; }

.permission-item {
  display: block;
  padding: 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s;
}
.permission-item:hover { background: #f9fafb; }

.perm-info { display: flex; flex-direction: column; margin-left: 8px; }
.perm-name { font-weight: 500; color: #111827; font-size: 14px; }
.perm-desc { font-size: 12px; color: #6b7280; margin-top: 2px; }

.empty-state { text-align: center; padding: 80px 24px; color: #9ca3af; }
.empty-state h3 { margin: 16px 0 8px; color: #374151; }

/* 响应式设计 */
@media (max-width: 1024px) {
  .level-selector { padding: 20px; gap: 16px; }
  .permissions-grid { gap: 16px; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }
}

@media (max-width: 768px) {
  .level-selector { 
    flex-direction: column; 
    align-items: stretch; 
    padding: 16px;
    gap: 12px;
    border-radius: 12px;
    margin-bottom: 16px;
  }
  .selector-left { width: 100%; }
  .selector-icon { width: 40px; height: 40px; }
  .level-select { width: 100%; }
  .selector-tip { width: 100%; order: 3; padding: 10px 12px; font-size: 13px; }
  
  .quick-actions { gap: 8px; margin-bottom: 16px; }
  .quick-actions .el-button { padding: 8px 12px; font-size: 13px; }
  .quick-actions .el-button:last-child { width: 100%; margin-left: 0 !important; margin-top: 8px; order: 4; }
  
  .permissions-grid { grid-template-columns: 1fr; gap: 16px; }
  .permission-card { border-radius: 12px; }
  .card-header { padding: 12px 16px; }
  .card-body { padding: 12px; max-height: 260px; }
  .permission-item { padding: 10px; }
}

@media (max-width: 480px) {
  .level-selector { padding: 12px; }
  .selector-icon { width: 36px; height: 36px; border-radius: 8px; }
  .selector-meta label { font-size: 14px; }
  .selector-meta p { font-size: 11px; }
  .selector-tip { font-size: 12px; padding: 8px 10px; }
  
  .selected-info { font-size: 12px; }
  .selected-count { padding: 1px 6px; font-size: 12px; }
  
  .category-icon { width: 32px; height: 32px; border-radius: 8px; }
  .category-info h3 { font-size: 14px; }
  .perm-name { font-size: 13px; }
  .perm-desc { font-size: 11px; }
  
  .empty-state { padding: 48px 16px; }
  .empty-state h3 { font-size: 16px; }
}
</style>
