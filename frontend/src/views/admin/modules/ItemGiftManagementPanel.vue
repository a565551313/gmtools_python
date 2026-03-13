<template>
  <div class="item-gift-management">
    <!-- 顶部统计卡片区 -->
    <div class="stats-container">
      <div class="stat-card" v-for="stat in statistics" :key="stat.label">
        <div class="stat-icon" :style="{ background: stat.color }">
          <component :is="stat.icon" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>
    </div>

    <!-- 主标题区域 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon class="title-icon"><Box /></el-icon>
          道具赠送限制管理
        </h1>
        <p class="page-description">配置可赠送的道具白名单及各等级的发送限制规则</p>
      </div>
      <div class="header-right">
        <el-tooltip content="刷新数据" placement="bottom">
          <el-button circle @click="refreshData" :loading="isRefreshing">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </el-tooltip>
      </div>
    </div>

    <!-- 标签页内容 -->
    <div class="content-wrapper">
      <el-tabs v-model="activeTab" class="modern-tabs" @tab-change="handleTabChange">
        <!-- 道具白名单 -->
        <el-tab-pane name="items">
          <template #label>
            <span class="tab-label">
              <el-icon><List /></el-icon>
              道具白名单
              <el-badge :value="items.length" class="tab-badge" v-if="items.length > 0" />
            </span>
          </template>

          <div class="tab-content">
            <!-- 工具栏 -->
            <div class="toolbar">
              <div class="toolbar-left">
                <el-input
                  v-model="itemSearchKeyword"
                  placeholder="搜索道具名称或描述..."
                  clearable
                  class="search-input"
                  @input="handleItemSearch"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                
                <el-select
                  v-model="itemStatusFilter"
                  placeholder="状态筛选"
                  clearable
                  style="width: 120px"
                  @change="handleItemSearch"
                >
                  <el-option label="全部" :value="null" />
                  <el-option label="启用" :value="true" />
                  <el-option label="禁用" :value="false" />
                </el-select>
              </div>

              <div class="toolbar-right">
                <el-button type="primary" @click="openAddItemDialog" class="add-btn">
                  <el-icon><Plus /></el-icon>
                  添加道具
                </el-button>
              </div>
            </div>

            <!-- 道具列表 -->
            <div class="items-grid" v-if="!loadingItems && filteredItems.length > 0">
              <TransitionGroup name="card-list">
                <div 
                  v-for="item in filteredItems" 
                  :key="item.item_name"
                  class="item-card"
                  @click="selectItem(item)"
                >
                  <div class="item-card-header">
                    <div class="item-icon-wrapper">
                      <el-image 
                        v-if="item.icon_url"
                        :src="item.icon_url" 
                        fit="cover"
                        class="item-icon"
                      >
                        <template #error>
                          <div class="icon-placeholder">
                            <el-icon><Picture /></el-icon>
                          </div>
                        </template>
                      </el-image>
                      <div v-else class="icon-placeholder">
                        <el-icon><Box /></el-icon>
                      </div>
                    </div>
                    <el-tag 
                      :type="item.is_active ? 'success' : 'info'" 
                      size="small"
                      effect="dark"
                      class="status-tag"
                    >
                      {{ item.is_active ? '启用' : '禁用' }}
                    </el-tag>
                  </div>

                  <div class="item-card-body">
                    <h3 class="item-name">{{ item.item_name }}</h3>
                    <p class="item-description">{{ item.description || '暂无描述' }}</p>
                  </div>

                  <div class="item-card-footer">
                    <el-button link type="primary" @click.stop="editItem(item)">
                      <el-icon><Edit /></el-icon>
                      编辑
                    </el-button>
                    <el-button link type="primary" @click.stop="viewLimits(item)">
                      <el-icon><View /></el-icon>
                      查看限制
                    </el-button>
                    <el-popconfirm 
                      title="确定要删除这个道具配置吗？" 
                      @confirm="deleteItem(item)"
                      width="200"
                    >
                      <template #reference>
                        <el-button link type="danger" @click.stop>
                          <el-icon><Delete /></el-icon>
                          删除
                        </el-button>
                      </template>
                    </el-popconfirm>
                  </div>
                </div>
              </TransitionGroup>
            </div>

            <!-- 加载状态 -->
            <div v-else-if="loadingItems" class="loading-container">
              <el-skeleton :rows="3" animated />
            </div>

            <!-- 空状态 -->
            <el-empty 
              v-else 
              description="暂无道具数据"
              :image-size="160"
            >
              <el-button type="primary" @click="openAddItemDialog">
                添加第一个道具
              </el-button>
            </el-empty>
          </div>
        </el-tab-pane>

        <!-- 等级限制配置 -->
        <el-tab-pane name="limits">
          <template #label>
            <span class="tab-label">
              <el-icon><Setting /></el-icon>
              等级限制配置
              <el-badge :value="limits.length" class="tab-badge" v-if="limits.length > 0" />
            </span>
          </template>

          <div class="tab-content">
            <!-- 筛选栏 -->
            <div class="filter-section">
              <div class="filter-grid">
                <el-select 
                  v-model="filterItemName" 
                  placeholder="筛选道具" 
                  clearable 
                  filterable
                  @change="loadLimits"
                  class="filter-select"
                >
                  <template #prefix>
                    <el-icon><Box /></el-icon>
                  </template>
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
                  class="filter-select"
                >
                  <template #prefix>
                    <el-icon><User /></el-icon>
                  </template>
                  <el-option
                    v-for="i in 10"
                    :key="i"
                    :label="`Level ${i}`"
                    :value="i"
                  />
                </el-select>

                <el-button 
                  type="primary" 
                  @click="openAddLimitDialog"
                  class="filter-add-btn"
                >
                  <el-icon><Plus /></el-icon>
                  添加限制规则
                </el-button>
              </div>
            </div>

            <!-- 限制规则表格 -->
            <div class="table-wrapper">
              <el-table 
                :data="limits" 
                v-loading="loadingLimits"
                class="modern-table"
                :header-cell-style="{ background: '#f8fafc', color: '#475569' }"
                stripe
                @sort-change="handleSortChange"
              >
                <el-table-column prop="item_name" label="道具" width="200" fixed>
                  <template #default="{ row }">
                    <div class="table-item-name">
                      <el-icon class="table-icon"><Box /></el-icon>
                      <strong>{{ row.item_name }}</strong>
                    </div>
                  </template>
                </el-table-column>

                <el-table-column prop="user_level" label="等级" width="120" sortable>
                  <template #default="{ row }">
                    <el-tag :type="getLevelTagType(row.user_level)" effect="plain">
                      Level {{ row.user_level }}
                    </el-tag>
                  </template>
                </el-table-column>

                <el-table-column label="单次数量限制" width="180">
                  <template #default="{ row }">
                    <div class="quantity-range">
                      <span class="range-value">{{ row.min_quantity }}</span>
                      <el-icon class="range-separator"><ArrowRight /></el-icon>
                      <span class="range-value">{{ row.max_quantity }}</span>
                      <span class="range-unit">个</span>
                    </div>
                  </template>
                </el-table-column>

                <el-table-column label="周期配额" min-width="220">
                  <template #default="{ row }">
                    <div class="period-info">
                      <el-icon class="period-icon"><Clock /></el-icon>
                      每 <strong>{{ row.reset_period_hours }}</strong> 小时
                      最多 <strong class="highlight-value">{{ row.period_total_limit }}</strong> 个
                    </div>
                  </template>
                </el-table-column>

                <el-table-column prop="is_active" label="状态" width="100" align="center">
                  <template #default="{ row }">
                    <el-switch
                      v-model="row.is_active"
                      size="default"
                      @change="toggleLimitStatus(row)"
                      :active-icon="Check"
                      :inactive-icon="Close"
                    />
                  </template>
                </el-table-column>

                <el-table-column label="操作" width="180" fixed="right" align="center">
                  <template #default="{ row }">
                    <div class="table-actions">
                      <el-tooltip content="编辑" placement="top">
                        <el-button 
                          link 
                          type="primary" 
                          @click="editLimit(row)"
                          circle
                        >
                          <el-icon><Edit /></el-icon>
                        </el-button>
                      </el-tooltip>

                      <el-popconfirm 
                        title="确定要删除这条限制规则吗？" 
                        @confirm="deleteLimit(row)"
                        width="220"
                      >
                        <template #reference>
                          <el-tooltip content="删除" placement="top">
                            <el-button link type="danger" circle>
                              <el-icon><Delete /></el-icon>
                            </el-button>
                          </el-tooltip>
                        </template>
                      </el-popconfirm>
                    </div>
                  </template>
                </el-table-column>
              </el-table>

              <!-- 空状态 -->
              <el-empty 
                v-if="!loadingLimits && limits.length === 0" 
                description="暂无限制规则"
                :image-size="160"
              >
                <el-button type="primary" @click="openAddLimitDialog">
                  创建第一条规则
                </el-button>
              </el-empty>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 添加/编辑道具弹窗 -->
    <el-dialog
      v-model="itemDialogVisible"
      :title="editingItem ? '编辑道具' : '添加道具'"
      width="600px"
      destroy-on-close
      class="modern-dialog"
      :close-on-click-modal="false"
    >
      <el-form 
        :model="itemForm" 
        label-width="100px" 
        :rules="itemRules" 
        ref="itemFormRef"
        class="modern-form"
      >
        <el-form-item label="道具名称" prop="item_name">
          <el-input 
            v-model="itemForm.item_name" 
            placeholder="游戏内的道具名称（唯一标识）"
            :disabled="!!editingItem"
          >
            <template #prefix>
              <el-icon><Box /></el-icon>
            </template>
          </el-input>
          <div class="form-tip" v-if="editingItem">
            <el-icon><InfoFilled /></el-icon>
            修改名称将同步更新所有关联的限制规则和日志
          </div>
        </el-form-item>

        <el-form-item label="图标URL" prop="icon_url">
          <el-input 
            v-model="itemForm.icon_url" 
            placeholder="https://example.com/icon.png"
          >
            <template #prefix>
              <el-icon><Picture /></el-icon>
            </template>
          </el-input>
          <div class="icon-preview" v-if="itemForm.icon_url">
            <el-image 
              :src="itemForm.icon_url" 
              style="width: 60px; height: 60px"
              fit="contain"
            >
              <template #error>
                <div class="icon-error">加载失败</div>
              </template>
            </el-image>
          </div>
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="itemForm.description" 
            type="textarea" 
            :rows="4"
            placeholder="请输入道具描述信息..."
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="状态" prop="is_active" v-if="editingItem">
          <el-switch 
            v-model="itemForm.is_active" 
            active-text="启用" 
            inactive-text="禁用"
            :active-icon="Check"
            :inactive-icon="Close"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="itemDialogVisible = false" size="large">
            取消
          </el-button>
          <el-button 
            type="primary" 
            @click="saveItem" 
            :loading="saving"
            size="large"
          >
            <el-icon v-if="!saving"><Check /></el-icon>
            {{ saving ? '保存中...' : '确定保存' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 添加/编辑限制弹窗 -->
    <el-dialog
      v-model="limitDialogVisible"
      :title="editingLimit ? '编辑限制规则' : '批量添加限制规则'"
      width="700px"
      destroy-on-close
      class="modern-dialog"
      :close-on-click-modal="false"
    >
      <el-form 
        :model="limitForm" 
        label-width="120px" 
        :rules="limitRules" 
        ref="limitFormRef"
        class="modern-form"
      >
        <!-- 道具选择 -->
        <el-form-item 
          :label="editingLimit ? '选择道具' : '批量选择道具'" 
          :prop="editingLimit ? 'item_name' : 'item_names'"
        >
          <el-select 
            v-if="!editingLimit"
            v-model="limitForm.item_names" 
            placeholder="可多选道具批量创建规则" 
            style="width: 100%"
            multiple
            filterable
            collapse-tags
            collapse-tags-tooltip
          >
            <template #prefix>
              <el-icon><Box /></el-icon>
            </template>
            <el-option
              v-for="item in items"
              :key="item.item_name"
              :label="item.item_name"
              :value="item.item_name"
            >
              <span class="option-label">{{ item.item_name }}</span>
              <span class="option-desc">{{ item.description }}</span>
            </el-option>
          </el-select>

          <el-select 
            v-else
            v-model="limitForm.item_name" 
            placeholder="请选择道具" 
            style="width: 100%"
            filterable
          >
            <template #prefix>
              <el-icon><Box /></el-icon>
            </template>
            <el-option
              v-for="item in items"
              :key="item.item_name"
              :label="item.item_name"
              :value="item.item_name"
            />
          </el-select>
        </el-form-item>

        <!-- 等级选择 -->
        <el-form-item 
          :label="editingLimit ? '适用等级' : '批量选择等级'" 
          :prop="editingLimit ? 'user_level' : 'user_levels'"
        >
          <el-select 
            v-if="!editingLimit"
            v-model="limitForm.user_levels" 
            placeholder="可多选等级批量创建规则" 
            style="width: 100%"
            multiple
            collapse-tags
            collapse-tags-tooltip
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
            <el-option
              v-for="i in 10"
              :key="i"
              :label="`Level ${i}`"
              :value="i"
            >
              <el-tag :type="getLevelTagType(i)" size="small">Level {{ i }}</el-tag>
            </el-option>
          </el-select>

          <el-select 
            v-else
            v-model="limitForm.user_level" 
            placeholder="请选择等级" 
            style="width: 100%"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
            <el-option
              v-for="i in 10"
              :key="i"
              :label="`Level ${i}`"
              :value="i"
            />
          </el-select>
        </el-form-item>
        
        <el-divider content-position="left">
          <el-icon><Money /></el-icon>
          单次发送限制
        </el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="最低数量" prop="min_quantity" label-width="100px">
              <el-input-number 
                v-model="limitForm.min_quantity" 
                :min="1" 
                :max="limitForm.max_quantity"
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最高数量" prop="max_quantity" label-width="100px">
              <el-input-number 
                v-model="limitForm.max_quantity" 
                :min="limitForm.min_quantity"
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">
          <el-icon><Clock /></el-icon>
          周期配额限制
        </el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="重置周期" prop="reset_period_hours" label-width="100px">
              <el-input-number 
                v-model="limitForm.reset_period_hours" 
                :min="1" 
                :step="1" 
                style="width: 100%" 
              />
              <span class="unit-text">小时</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="周期总量" prop="period_total_limit" label-width="100px">
              <el-input-number 
                v-model="limitForm.period_total_limit" 
                :min="1" 
                :step="10" 
                style="width: 100%" 
              />
              <span class="unit-text">个</span>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 批量创建提示 -->
        <el-alert
          v-if="!editingLimit && limitForm.item_names.length > 0 && limitForm.user_levels.length > 0"
          :title="`将创建 ${limitForm.item_names.length} × ${limitForm.user_levels.length} = ${limitForm.item_names.length * limitForm.user_levels.length} 条规则`"
          type="info"
          :closable="false"
          show-icon
        />
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="limitDialogVisible = false" size="large">
            取消
          </el-button>
          <el-button 
            type="primary" 
            @click="saveLimit" 
            :loading="saving"
            size="large"
          >
            <el-icon v-if="!saving"><Check /></el-icon>
            {{ saving ? '保存中...' : '确定保存' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Plus, Edit, Delete, Search, Picture, Box, List, Setting,
  Refresh, View, User, Clock, ArrowRight, Check, Close,
  InfoFilled, Money, DataAnalysis, TrendCharts, Collection
} from '@element-plus/icons-vue'
import request from '@/api/request'

// ==================== 状态管理 ====================
const activeTab = ref('items')
const loadingItems = ref(false)
const loadingLimits = ref(false)
const saving = ref(false)
const isRefreshing = ref(false)

// ==================== 数据 ====================
const items = ref([])
const limits = ref([])

// ==================== 搜索和筛选 ====================
const itemSearchKeyword = ref('')
const itemStatusFilter = ref(null)
const filterItemName = ref('')
const filterLevel = ref('')

// ==================== 弹窗控制 ====================
const itemDialogVisible = ref(false)
const limitDialogVisible = ref(false)
const editingItem = ref(null)
const editingLimit = ref(null)

// ==================== 表单引用 ====================
const itemFormRef = ref(null)
const limitFormRef = ref(null)

// ==================== 表单数据 ====================
const itemForm = reactive({
  item_name: '',
  description: '',
  icon_url: '',
  is_active: true
})

const limitForm = reactive({
  item_name: '',
  item_names: [],
  user_level: 1,
  user_levels: [],
  min_quantity: 1,
  max_quantity: 99,
  reset_period_hours: 24,
  period_total_limit: 200
})

// ==================== 验证规则 ====================
const itemRules = {
  item_name: [
    { required: true, message: '请输入道具名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 200, message: '描述不能超过 200 个字符', trigger: 'blur' }
  ]
}

const limitRules = {
  item_name: [{ required: true, message: '请选择道具', trigger: 'change' }],
  item_names: [
    { required: true, message: '请至少选择一个道具', trigger: 'change', type: 'array' },
    { type: 'array', min: 1, message: '请至少选择一个道具', trigger: 'change' }
  ],
  user_level: [{ required: true, message: '请选择等级', trigger: 'change' }],
  user_levels: [
    { required: true, message: '请至少选择一个等级', trigger: 'change', type: 'array' },
    { type: 'array', min: 1, message: '请至少选择一个等级', trigger: 'change' }
  ],
  min_quantity: [
    { required: true, message: '请输入最低数量', trigger: 'blur' },
    { type: 'number', min: 1, message: '最低数量不能小于 1', trigger: 'blur' }
  ],
  max_quantity: [
    { required: true, message: '请输入最高数量', trigger: 'blur' },
    { type: 'number', min: 1, message: '最高数量不能小于 1', trigger: 'blur' }
  ],
  reset_period_hours: [
    { required: true, message: '请输入重置周期', trigger: 'blur' },
    { type: 'number', min: 1, message: '重置周期不能小于 1 小时', trigger: 'blur' }
  ],
  period_total_limit: [
    { required: true, message: '请输入周期总量', trigger: 'blur' },
    { type: 'number', min: 1, message: '周期总量不能小于 1', trigger: 'blur' }
  ]
}

// ==================== 计算属性 ====================
// 统计数据
const statistics = computed(() => [
  {
    label: '道具总数',
    value: items.value.length,
    icon: Box,
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  },
  {
    label: '启用道具',
    value: items.value.filter(i => i.is_active).length,
    icon: Collection,
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
  },
  {
    label: '限制规则',
    value: limits.value.length,
    icon: DataAnalysis,
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
  },
  {
    label: '活跃规则',
    value: limits.value.filter(l => l.is_active).length,
    icon: TrendCharts,
    color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
  }
])

// 过滤后的道具列表
const filteredItems = computed(() => {
  let result = items.value

  // 关键词搜索
  if (itemSearchKeyword.value) {
    const keyword = itemSearchKeyword.value.toLowerCase()
    result = result.filter(item => 
      item.item_name.toLowerCase().includes(keyword) ||
      (item.description && item.description.toLowerCase().includes(keyword))
    )
  }

  // 状态筛选
  if (itemStatusFilter.value !== null) {
    result = result.filter(item => item.is_active === itemStatusFilter.value)
  }

  return result
})

// ==================== 辅助函数 ====================
function getLevelTagType(level) {
  if (level <= 3) return 'info'
  if (level <= 6) return 'success'
  if (level <= 9) return 'warning'
  return 'danger'
}

// ==================== 数据加载 ====================
async function loadItems() {
  loadingItems.value = true
  try {
    const res = await request.get('/api/item-configs')
    items.value = res.data || []
  } catch (e) {
    ElMessage.error('加载道具列表失败：' + (e.response?.data?.detail || e.message))
  } finally {
    loadingItems.value = false
  }
}

async function loadLimits() {
  loadingLimits.value = true
  try {
    let url = '/api/item-level-limits'
    
    if (filterItemName.value) {
      url = `/api/item-level-limits/item/${encodeURIComponent(filterItemName.value)}`
    } else if (filterLevel.value) {
      url = `/api/item-level-limits/level/${filterLevel.value}`
    }
    
    const res = await request.get(url)
    limits.value = res.data || []
    
    // 前端二次筛选
    if (filterItemName.value && filterLevel.value) {
      limits.value = limits.value.filter(l => l.user_level === filterLevel.value)
    }
  } catch (e) {
    ElMessage.error('加载限制规则失败：' + (e.response?.data?.detail || e.message))
  } finally {
    loadingLimits.value = false
  }
}

async function refreshData() {
  isRefreshing.value = true
  try {
    await Promise.all([loadItems(), loadLimits()])
    ElMessage.success('数据刷新成功')
  } finally {
    isRefreshing.value = false
  }
}

// ==================== 道具操作 ====================
function openAddItemDialog() {
  editingItem.value = null
  Object.assign(itemForm, {
    item_name: '',
    description: '',
    icon_url: '',
    is_active: true
  })
  itemDialogVisible.value = true
}

function editItem(row) {
  editingItem.value = row
  Object.assign(itemForm, {
    item_name: row.item_name,
    description: row.description,
    icon_url: row.icon_url,
    is_active: row.is_active
  })
  itemDialogVisible.value = true
}

function selectItem(item) {
  // 点击卡片可以执行的操作，这里暂时留空
}

async function saveItem() {
  if (!itemFormRef.value) return
  
  await itemFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    saving.value = true
    try {
      if (editingItem.value) {
        await request.put(
          `/api/item-configs/${encodeURIComponent(editingItem.value.item_name)}`, 
          itemForm
        )
        ElMessage.success('更新成功')
      } else {
        await request.post('/api/item-configs', itemForm)
        ElMessage.success('创建成功')
      }
      
      itemDialogVisible.value = false
      await loadItems()
      
      if (activeTab.value === 'limits') {
        await loadLimits()
      }
    } catch (e) {
      ElMessage.error(e.response?.data?.detail || '保存失败')
    } finally {
      saving.value = false
    }
  })
}

async function deleteItem(row) {
  try {
    await request.delete(`/api/item-configs/${encodeURIComponent(row.item_name)}`)
    ElMessage.success('删除成功')
    await loadItems()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '删除失败')
  }
}

function viewLimits(row) {
  activeTab.value = 'limits'
  filterItemName.value = row.item_name
  filterLevel.value = ''
  loadLimits()
}

function handleItemSearch() {
  // 触发计算属性更新
}

// ==================== 限制操作 ====================
function openAddLimitDialog() {
  editingLimit.value = null
  Object.assign(limitForm, {
    item_names: filterItemName.value ? [filterItemName.value] : [],
    item_name: '',
    user_level: filterLevel.value || 1,
    user_levels: filterLevel.value ? [filterLevel.value] : [],
    min_quantity: 1,
    max_quantity: 99,
    reset_period_hours: 24,
    period_total_limit: 200
  })
  limitDialogVisible.value = true
}

function editLimit(row) {
  editingLimit.value = row
  Object.assign(limitForm, {
    item_name: row.item_name,
    user_level: row.user_level,
    min_quantity: row.min_quantity,
    max_quantity: row.max_quantity,
    reset_period_hours: row.reset_period_hours,
    period_total_limit: row.period_total_limit
  })
  limitDialogVisible.value = true
}

async function saveLimit() {
  if (!limitFormRef.value) return
  
  await limitFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    // 验证数量范围
    if (limitForm.min_quantity > limitForm.max_quantity) {
      ElMessage.warning('最低数量不能大于最高数量')
      return
    }
    
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
        await request.post('/api/item-level-limits/batch', {
          items: limitForm.item_names,
          user_levels: limitForm.user_levels,
          min_quantity: limitForm.min_quantity,
          max_quantity: limitForm.max_quantity,
          reset_period_hours: limitForm.reset_period_hours,
          period_total_limit: limitForm.period_total_limit
        })
        const count = limitForm.item_names.length * limitForm.user_levels.length
        ElMessage.success(`成功创建 ${count} 条规则`)
      }
      
      limitDialogVisible.value = false
      await loadLimits()
    } catch (e) {
      ElMessage.error(e.response?.data?.detail || '保存失败')
    } finally {
      saving.value = false
    }
  })
}

async function deleteLimit(row) {
  try {
    await request.delete(`/api/item-level-limits/${row.id}`)
    ElMessage.success('删除成功')
    await loadLimits()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '删除失败')
  }
}

async function toggleLimitStatus(row) {
  try {
    await request.put(`/api/item-level-limits/${row.id}`, { 
      is_active: row.is_active 
    })
    ElMessage.success('状态更新成功')
  } catch (e) {
    row.is_active = !row.is_active // 回滚
    ElMessage.error('状态更新失败')
  }
}

function handleSortChange({ prop, order }) {
  // 可以实现排序逻辑
  console.log('排序:', prop, order)
}

function handleTabChange(tabName) {
  if (tabName === 'limits') {
    loadLimits()
  }
}

// ==================== 生命周期 ====================
onMounted(() => {
  loadItems()
  loadLimits()
})
</script>

<style scoped>
/* ==================== 基础布局 ==================== */
.item-gift-management {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8edf2 100%);
  min-height: 100vh;
}

/* ==================== 统计卡片 ==================== */
.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, transparent 0%, rgba(255, 255, 255, 0.1) 100%);
  opacity: 0;
  transition: opacity 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

/* ==================== 页面标题 ==================== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 0 4px;
}

.header-left {
  flex: 1;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  font-size: 32px;
  color: #667eea;
}

.page-description {
  margin: 0;
  color: #64748b;
  font-size: 15px;
  line-height: 1.6;
}

/* ==================== 主内容区 ==================== */
.content-wrapper {
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.modern-tabs {
  padding: 0;
}

.modern-tabs :deep(.el-tabs__header) {
  margin: 0;
  padding: 20px 24px 0;
  background: linear-gradient(to bottom, #ffffff 0%, #f8fafc 100%);
  border-bottom: 2px solid #e2e8f0;
}

.modern-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.modern-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 600;
  color: #64748b;
  padding: 0 24px;
  height: 48px;
  line-height: 48px;
  transition: all 0.3s;
}

.modern-tabs :deep(.el-tabs__item:hover) {
  color: #667eea;
}

.modern-tabs :deep(.el-tabs__item.is-active) {
  color: #667eea;
}

.modern-tabs :deep(.el-tabs__active-bar) {
  height: 3px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 3px 3px 0 0;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-badge {
  margin-left: 4px;
}

.tab-content {
  padding: 24px;
}

/* ==================== 工具栏 ==================== */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
  flex-wrap: wrap;
}

.toolbar-left {
  display: flex;
  gap: 12px;
  flex: 1;
  flex-wrap: wrap;
}

.toolbar-right {
  display: flex;
  gap: 12px;
}

.search-input {
  width: 300px;
  max-width: 100%;
}

.add-btn {
  font-weight: 600;
  padding: 12px 24px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* ==================== 道具网格卡片 ==================== */
.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.item-card {
  background: white;
  border-radius: 16px;
  border: 2px solid #e2e8f0;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.item-card:hover {
  border-color: #667eea;
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(102, 126, 234, 0.2);
}

.item-card-header {
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #e8edf2 100%);
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.item-icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  overflow: hidden;
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-icon {
  width: 100%;
  height: 100%;
}

.icon-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  color: #94a3b8;
  font-size: 28px;
}

.status-tag {
  border-radius: 6px;
  font-weight: 600;
}

.item-card-body {
  padding: 20px;
}

.item-name {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  word-break: break-word;
}

.item-description {
  margin: 0;
  font-size: 14px;
  color: #64748b;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 42px;
}

.item-card-footer {
  padding: 12px 20px;
  background: #f8fafc;
  display: flex;
  gap: 8px;
  border-top: 1px solid #e2e8f0;
}

.item-card-footer .el-button {
  flex: 1;
  font-weight: 600;
}

/* ==================== 筛选区域 ==================== */
.filter-section {
  margin-bottom: 24px;
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #e8edf2 100%);
  border-radius: 12px;
  border: 2px solid #e2e8f0;
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  align-items: center;
}

.filter-select {
  width: 100%;
}

.filter-add-btn {
  width: 100%;
  font-weight: 600;
  padding: 12px 20px;
  border-radius: 10px;
}

/* ==================== 表格 ==================== */
.table-wrapper {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.modern-table {
  border-radius: 12px;
  overflow: hidden;
}

.modern-table :deep(.el-table__header) {
  font-weight: 600;
}

.modern-table :deep(.el-table__row) {
  transition: all 0.3s;
}

.modern-table :deep(.el-table__row:hover) {
  background: #f8fafc !important;
}

.table-item-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
}

.table-icon {
  color: #667eea;
  font-size: 18px;
}

.quantity-range {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.range-value {
  font-weight: 600;
  color: #1e293b;
  background: #f1f5f9;
  padding: 4px 12px;
  border-radius: 6px;
}

.range-separator {
  color: #94a3b8;
}

.range-unit {
  color: #64748b;
  margin-left: 4px;
}

.period-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #475569;
}

.period-icon {
  color: #667eea;
  font-size: 16px;
}

.highlight-value {
  color: #667eea;
  font-weight: 700;
  font-size: 15px;
}

.table-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
}

/* ==================== 弹窗 ==================== */
.modern-dialog :deep(.el-dialog) {
  border-radius: 20px;
  overflow: hidden;
}

.modern-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px 28px;
  margin: 0;
}

.modern-dialog :deep(.el-dialog__title) {
  color: white;
  font-size: 20px;
  font-weight: 700;
}

.modern-dialog :deep(.el-dialog__close) {
  font-size: 20px;
}

.modern-dialog :deep(.el-dialog__body) {
  padding: 28px;
}

.modern-form {
  margin-top: 8px;
}

.modern-form :deep(.el-form-item__label) {
  font-weight: 600;
  color: #334155;
}

.modern-form :deep(.el-input__inner) {
  border-radius: 8px;
}

.modern-form :deep(.el-textarea__inner) {
  border-radius: 8px;
}

.form-tip {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin-top: 8px;
  padding: 8px 12px;
  background: #f1f5f9;
  border-radius: 6px;
  display: flex;
  align-items: flex-start;
  gap: 6px;
}

.form-tip .el-icon {
  color: #3b82f6;
  margin-top: 2px;
  flex-shrink: 0;
}

.icon-preview {
  margin-top: 12px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
  display: inline-block;
}

.icon-error {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fee2e2;
  color: #dc2626;
  font-size: 12px;
  border-radius: 4px;
}

.unit-text {
  margin-left: 12px;
  color: #64748b;
  font-weight: 600;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.dialog-footer .el-button {
  padding: 12px 28px;
  border-radius: 10px;
  font-weight: 600;
}

/* ==================== 下拉选项 ==================== */
.option-label {
  font-weight: 600;
  color: #1e293b;
}

.option-desc {
  font-size: 12px;
  color: #94a3b8;
  margin-left: 8px;
}

/* ==================== 加载和空状态 ==================== */
.loading-container {
  padding: 40px;
}

.el-empty {
  padding: 60px 20px;
}

/* ==================== 动画 ==================== */
.card-list-move,
.card-list-enter-active,
.card-list-leave-active {
  transition: all 0.5s cubic-bezier(0.55, 0, 0.1, 1);
}

.card-list-enter-from {
  opacity: 0;
  transform: translateY(30px) scale(0.9);
}

.card-list-leave-to {
  opacity: 0;
  transform: translateX(-30px) scale(0.9);
}

.card-list-leave-active {
  position: absolute;
}

/* ==================== 响应式设计 ==================== */
@media (max-width: 1400px) {
  .stats-container {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .items-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
}

@media (max-width: 992px) {
  .item-gift-management {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-left,
  .toolbar-right {
    width: 100%;
  }

  .search-input {
    width: 100%;
  }

  .filter-grid {
    grid-template-columns: 1fr;
  }

  .modern-dialog :deep(.el-dialog) {
    width: 95% !important;
    margin: 20px auto;
  }
}

@media (max-width: 768px) {
  .stats-container {
    grid-template-columns: 1fr;
  }

  .items-grid {
    grid-template-columns: 1fr;
  }

  .page-title {
    font-size: 24px;
  }

  .stat-value {
    font-size: 28px;
  }

  .tab-content {
    padding: 16px;
  }

  .modern-tabs :deep(.el-tabs__item) {
    padding: 0 16px;
    font-size: 14px;
  }

  .table-wrapper {
    overflow-x: auto;
  }

  .modern-table {
    min-width: 800px;
  }

  .item-card-footer {
    flex-direction: column;
  }

  .dialog-footer {
    flex-direction: column-reverse;
  }

  .dialog-footer .el-button {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .item-gift-management {
    padding: 12px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-icon {
    width: 48px;
    height: 48px;
    font-size: 20px;
  }

  .stat-value {
    font-size: 24px;
  }

  .page-title {
    font-size: 20px;
  }

  .title-icon {
    font-size: 24px;
  }

  .modern-form {
    margin-top: 0;
  }

  .modern-form :deep(.el-form-item__label) {
    font-size: 14px;
  }
}

/* ==================== 打印样式 ==================== */
@media print {
  .page-header,
  .toolbar,
  .filter-section,
  .item-card-footer,
  .table-actions,
  .modern-tabs :deep(.el-tabs__header) {
    display: none !important;
  }

  .item-gift-management {
    background: white;
  }

  .content-wrapper {
    box-shadow: none;
  }
}

/* ==================== 深色模式支持 ==================== */
@media (prefers-color-scheme: dark) {
  .item-gift-management {
    background: #0f172a;
  }

  .stat-card,
  .content-wrapper {
    background: #1e293b;
    border-color: #334155;
  }

  .page-title,
  .stat-value,
  .item-name {
    color: #f1f5f9;
  }

  .page-description,
  .stat-label,
  .item-description {
    color: #94a3b8;
  }

  .item-card {
    background: #1e293b;
    border-color: #334155;
  }

  .item-card-header,
  .item-card-footer,
  .filter-section {
    background: #0f172a;
  }
}

/* ==================== 无障碍支持 ==================== */
.item-card:focus,
.el-button:focus {
  outline: 2px solid #667eea;
  outline-offset: 2px;
}

/* ==================== 性能优化 ==================== */
.item-card,
.stat-card {
  will-change: transform;
  transform: translateZ(0);
  backface-visibility: hidden;
}
</style>