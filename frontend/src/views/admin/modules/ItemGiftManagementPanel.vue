<template>
  <div class="item-gift-management">
    <div class="panel-header">
      <div class="header-content">
        <h2>道具赠送限制管理</h2>
        <p class="subtitle">配置可赠送的道具白名单及各等级的发送限制规则</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddItemDialog" v-if="activeTab === 'items'">
          <el-icon><Plus /></el-icon> 添加道具
        </el-button>
        <el-button type="primary" @click="openAddLimitDialog" v-if="activeTab === 'limits'">
          <el-icon><Plus /></el-icon> 添加限制
        </el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="custom-tabs">
      <!-- 道具列表管理 -->
      <el-tab-pane label="道具白名单" name="items">
        <el-card class="table-card" shadow="hover">
          <el-table :data="items" v-loading="loadingItems" style="width: 100%">
            <el-table-column prop="item_name" label="道具名称 (ID)" width="200">
              <template #default="{ row }">
                <el-tag effect="plain" size="large">{{ row.item_name }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="图标" width="80">
              <template #default="{ row }">
                <el-image 
                  v-if="row.icon_url"
                  :src="row.icon_url" 
                  style="width: 40px; height: 40px" 
                  fit="contain"
                  :preview-src-list="[row.icon_url]"
                  preview-teleported
                >
                  <template #error>
                    <div class="image-slot">
                      <el-icon><Picture /></el-icon>
                    </div>
                  </template>
                </el-image>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
            <el-table-column prop="is_active" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                  {{ row.is_active ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="editItem(row)">编辑</el-button>
                <el-button link type="primary" @click="viewLimits(row)">查看限制</el-button>
                <el-popconfirm title="确定要删除这个道具配置吗？" @confirm="deleteItem(row)">
                  <template #reference>
                    <el-button link type="danger">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 等级限制管理 -->
      <el-tab-pane label="等级限制配置" name="limits">
        <div class="filter-bar">
          <el-select 
            v-model="filterItemName" 
            placeholder="筛选道具" 
            clearable 
            filterable
            @change="loadLimits"
            style="width: 200px"
          >
            <el-option
              v-for="item in items"
              :key="item.item_name"
              :label="item.item_name"
              :value="item.item_name"
            />
          </el-select>
          
          <el-select 
            v-model="filterLevel" 
            placeholder="筛选等级" 
            clearable 
            @change="loadLimits"
            style="width: 150px"
          >
            <el-option
              v-for="i in 10"
              :key="i"
              :label="`Level ${i}`"
              :value="i"
            />
          </el-select>
        </div>

        <el-card class="table-card" shadow="hover">
          <el-table :data="limits" v-loading="loadingLimits" style="width: 100%">
            <el-table-column prop="item_name" label="道具" width="180">
              <template #default="{ row }">
                <strong>{{ row.item_name }}</strong>
              </template>
            </el-table-column>
            <el-table-column prop="user_level" label="等级" width="100">
              <template #default="{ row }">
                <el-tag :type="getLevelTagType(row.user_level)">Level {{ row.user_level }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="单次数量限制" width="180">
              <template #default="{ row }">
                {{ row.min_quantity }} - {{ row.max_quantity }} 个
              </template>
            </el-table-column>
            <el-table-column label="周期配额" min-width="200">
              <template #default="{ row }">
                每 {{ row.reset_period_hours }} 小时最多 {{ row.period_total_limit }} 个
              </template>
            </el-table-column>
            <el-table-column prop="is_active" label="状态" width="100">
              <template #default="{ row }">
                <el-switch
                  v-model="row.is_active"
                  size="small"
                  @change="toggleLimitStatus(row)"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="editLimit(row)">编辑</el-button>
                <el-popconfirm title="确定要删除这条限制规则吗？" @confirm="deleteLimit(row)">
                  <template #reference>
                    <el-button link type="danger">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 添加/编辑道具弹窗 -->
    <el-dialog
      v-model="itemDialogVisible"
      :title="editingItem ? '编辑道具' : '添加道具'"
      width="500px"
      destroy-on-close
    >
      <el-form :model="itemForm" label-width="80px" :rules="itemRules" ref="itemFormRef">
        <el-form-item label="道具名称" prop="item_name">
          <el-input 
            v-model="itemForm.item_name" 
            placeholder="游戏内的道具名称（唯一标识）"
          />
          <div class="form-tip" v-if="editingItem">修改名称将同步更新所有关联的限制规则和日志</div>
        </el-form-item>
        <el-form-item label="图标URL" prop="icon_url">
          <el-input v-model="itemForm.icon_url" placeholder="可选" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="itemForm.description" type="textarea" rows="3" />
        </el-form-item>
        <el-form-item label="状态" prop="is_active" v-if="editingItem">
          <el-switch v-model="itemForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="itemDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveItem" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 添加/编辑限制弹窗 -->
    <el-dialog
      v-model="limitDialogVisible"
      :title="editingLimit ? '编辑限制规则' : '添加限制规则'"
      width="500px"
      destroy-on-close
    >
      <el-form :model="limitForm" label-width="100px" :rules="limitRules" ref="limitFormRef">
        <el-form-item label="选择道具" prop="item_names" v-if="!editingLimit">
          <el-select 
            v-model="limitForm.item_names" 
            placeholder="请选择道具（可多选）" 
            style="width: 100%"
            multiple
            filterable
            collapse-tags
            collapse-tags-tooltip
          >
            <el-option
              v-for="item in items"
              :key="item.item_name"
              :label="item.item_name"
              :value="item.item_name"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="选择道具" prop="item_name" v-else>
          <el-select 
            v-model="limitForm.item_name" 
            placeholder="请选择道具" 
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="item in items"
              :key="item.item_name"
              :label="item.item_name"
              :value="item.item_name"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="适用等级" prop="user_levels" v-if="!editingLimit">
          <el-select 
            v-model="limitForm.user_levels" 
            placeholder="请选择等级（可多选）" 
            style="width: 100%"
            multiple
            collapse-tags
            collapse-tags-tooltip
          >
            <el-option
              v-for="i in 10"
              :key="i"
              :label="`Level ${i}`"
              :value="i"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="适用等级" prop="user_level" v-else>
          <el-select 
            v-model="limitForm.user_level" 
            placeholder="请选择等级" 
            style="width: 100%"
          >
            <el-option
              v-for="i in 10"
              :key="i"
              :label="`Level ${i}`"
              :value="i"
            />
          </el-select>
        </el-form-item>
        
        <el-divider content-position="left">单次发送限制</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="最低数量" prop="min_quantity" label-width="80px">
              <el-input-number v-model="limitForm.min_quantity" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最高数量" prop="max_quantity" label-width="80px">
              <el-input-number v-model="limitForm.max_quantity" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">周期配额限制</el-divider>

        <el-form-item label="重置周期" prop="reset_period_hours">
          <el-input-number v-model="limitForm.reset_period_hours" :min="1" :step="1" style="width: 140px" />
          <span class="unit-text">小时</span>
        </el-form-item>
        <el-form-item label="周期总量" prop="period_total_limit">
          <el-input-number v-model="limitForm.period_total_limit" :min="1" :step="10" style="width: 140px" />
          <span class="unit-text">个</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="limitDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveLimit" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Search, Picture } from '@element-plus/icons-vue'
import request from '@/api/request'

// 状态
const activeTab = ref('items')
const loadingItems = ref(false)
const loadingLimits = ref(false)
const saving = ref(false)

// 数据
const items = ref([])
const limits = ref([])

// 筛选
const filterItemName = ref('')
const filterLevel = ref('')

// 弹窗控制
const itemDialogVisible = ref(false)
const limitDialogVisible = ref(false)
const editingItem = ref(null)
const editingLimit = ref(null)

// 表单引用
const itemFormRef = ref(null)
const limitFormRef = ref(null)

// 表单数据
const itemForm = reactive({
  item_name: '',
  description: '',
  icon_url: '',
  is_active: true
})

const limitForm = reactive({
  item_name: '',
  item_names: [], // 用于多选
  user_level: 1,
  user_levels: [], // 用于多选等级
  min_quantity: 1,
  max_quantity: 99,
  reset_period_hours: 24,
  period_total_limit: 200
})

// 验证规则
const itemRules = {
  item_name: [{ required: true, message: '请输入道具名称', trigger: 'blur' }]
}

const limitRules = {
  item_name: [{ required: true, message: '请选择道具', trigger: 'change' }],
  item_names: [{ required: true, message: '请至少选择一个道具', trigger: 'change', type: 'array' }],
  user_level: [{ required: true, message: '请选择等级', trigger: 'change' }],
  user_levels: [{ required: true, message: '请至少选择一个等级', trigger: 'change', type: 'array' }],
  min_quantity: [{ required: true, message: '请输入最低数量', trigger: 'blur' }],
  max_quantity: [{ required: true, message: '请输入最高数量', trigger: 'blur' }],
  reset_period_hours: [{ required: true, message: '请输入重置周期', trigger: 'blur' }],
  period_total_limit: [{ required: true, message: '请输入周期总量', trigger: 'blur' }]
}

// 辅助函数
function getLevelTagType(level) {
  if (level <= 3) return 'info'
  if (level <= 6) return 'success'
  if (level <= 9) return 'warning'
  return 'danger'
}

// 加载数据
async function loadItems() {
  loadingItems.value = true
  try {
    const res = await request.get('/api/item-configs')
    items.value = res.data || []
  } catch (e) {
    ElMessage.error('加载道具列表失败')
  } finally {
    loadingItems.value = false
  }
}

async function loadLimits() {
  loadingLimits.value = true
  try {
    let url = '/api/item-level-limits'
    
    // 如果有筛选，使用筛选API
    if (filterItemName.value) {
      url = `/api/item-level-limits/item/${encodeURIComponent(filterItemName.value)}`
    } else if (filterLevel.value) {
      url = `/api/item-level-limits/level/${filterLevel.value}`
    }
    
    const res = await request.get(url)
    limits.value = res.data || []
    
    // 前端二次筛选（如果API不支持组合筛选）
    if (filterItemName.value && filterLevel.value) {
      limits.value = limits.value.filter(l => l.user_level === filterLevel.value)
    }
  } catch (e) {
    ElMessage.error('加载限制规则失败')
  } finally {
    loadingLimits.value = false
  }
}

// 道具操作
function openAddItemDialog() {
  editingItem.value = null
  itemForm.item_name = ''
  itemForm.description = ''
  itemForm.icon_url = ''
  itemForm.is_active = true
  itemDialogVisible.value = true
}

function editItem(row) {
  editingItem.value = row
  itemForm.item_name = row.item_name
  itemForm.description = row.description
  itemForm.icon_url = row.icon_url
  itemForm.is_active = row.is_active
  itemDialogVisible.value = true
}

async function saveItem() {
  if (!itemFormRef.value) return
  await itemFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        if (editingItem.value) {
          // 如果修改了名称，需要传递新名称
          await request.put(`/api/item-configs/${encodeURIComponent(editingItem.value.item_name)}`, itemForm)
          ElMessage.success('更新成功')
        } else {
          await request.post('/api/item-configs', itemForm)
          ElMessage.success('创建成功')
        }
        itemDialogVisible.value = false
        loadItems()
        // 如果修改了道具名称，可能需要刷新限制列表
        if (activeTab.value === 'limits') {
          loadLimits()
        }
      } catch (e) {
        ElMessage.error(e.response?.data?.detail || '保存失败')
      } finally {
        saving.value = false
      }
    }
  })
}

async function deleteItem(row) {
  try {
    await request.delete(`/api/item-configs/${encodeURIComponent(row.item_name)}`)
    ElMessage.success('删除成功')
    loadItems()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

function viewLimits(row) {
  activeTab.value = 'limits'
  filterItemName.value = row.item_name
  loadLimits()
}

// 限制操作
function openAddLimitDialog() {
  editingLimit.value = null
  limitForm.item_names = filterItemName.value ? [filterItemName.value] : []
  limitForm.item_name = ''
  limitForm.user_level = filterLevel.value || 1
  limitForm.user_levels = filterLevel.value ? [filterLevel.value] : []
  limitForm.min_quantity = 1
  limitForm.max_quantity = 99
  limitForm.reset_period_hours = 24
  limitForm.period_total_limit = 200
  limitDialogVisible.value = true
}

function editLimit(row) {
  editingLimit.value = row
  limitForm.item_name = row.item_name
  limitForm.user_level = row.user_level
  limitForm.min_quantity = row.min_quantity
  limitForm.max_quantity = row.max_quantity
  limitForm.reset_period_hours = row.reset_period_hours
  limitForm.period_total_limit = row.period_total_limit
  limitDialogVisible.value = true
}

async function saveLimit() {
  if (!limitFormRef.value) return
  await limitFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        if (editingLimit.value) {
          await request.put(`/api/item-level-limits/${editingLimit.value.id}`, {
            item_name: limitForm.item_name,
            user_level: limitForm.user_level,
            min_quantity: limitForm.min_quantity,
            max_quantity: limitForm.max_quantity,
            reset_period_hours: limitForm.reset_period_hours,
            period_total_limit: limitForm.period_total_limit
          })
          ElMessage.success('更新成功')
        } else {
          // 批量创建
          await request.post('/api/item-level-limits/batch', {
            items: limitForm.item_names,
            user_levels: limitForm.user_levels,
            min_quantity: limitForm.min_quantity,
            max_quantity: limitForm.max_quantity,
            reset_period_hours: limitForm.reset_period_hours,
            period_total_limit: limitForm.period_total_limit
          })
          ElMessage.success('创建成功')
        }
        limitDialogVisible.value = false
        loadLimits()
      } catch (e) {
        ElMessage.error(e.response?.data?.detail || '保存失败')
      } finally {
        saving.value = false
      }
    }
  })
}

async function deleteLimit(row) {
  try {
    await request.delete(`/api/item-level-limits/${row.id}`)
    ElMessage.success('删除成功')
    loadLimits()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

async function toggleLimitStatus(row) {
  try {
    await request.put(`/api/item-level-limits/${row.id}`, { is_active: row.is_active })
    ElMessage.success('状态更新成功')
  } catch (e) {
    row.is_active = !row.is_active // 回滚
    ElMessage.error('状态更新失败')
  }
}

// 初始化
onMounted(() => {
  loadItems()
  loadLimits()
})
</script>

<style scoped>
.item-gift-management {
  padding: 20px;
  background: #f8fafc;
  min-height: 100%;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-content h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #1e293b;
}

.subtitle {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.custom-tabs {
  background: white;
  padding: 20px;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.table-card {
  border: none;
  box-shadow: none !important;
}

.item-display-name {
  font-weight: 600;
  color: #334155;
}

.filter-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  padding: 16px;
  background: #f1f5f9;
  border-radius: 8px;
}

.form-tip {
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.4;
  margin-top: 4px;
}

.unit-text {
  margin-left: 8px;
  color: #64748b;
}

.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
  font-size: 20px;
}
</style>
